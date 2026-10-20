"""Motor de búsqueda pública de productos por nombre y paginación de resultados.

Proyecto: FerreteríaMS v0
Tarea: FERMS-V0-P04
Requisitos relacionados: RF-001, RF-002, RF-003, RF-004, RF-008, RF-009, RF-024, RF-035, RF-036, RF-037.
Criterios relacionados: CA-001, CA-002, CA-003, CA-004, CA-006, CA-007, CA-039, CA-040, CA-041, CA-043.

Este módulo recibe información estructurada del inventario y devuelve coincidencias
calculadas exclusivamente sobre el campo `Nombre` de la hoja `Productos`, ordenadas
por relevancia y paginadas de diez en diez.
No realiza conexiones directas con GitHub API ni duplica las validaciones de `inventario.py`.
"""

from __future__ import annotations

import math
import sys
import unicodedata
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import pandas as pd

_DIRECTORIO_ACTUAL = Path(__file__).resolve().parent
if str(_DIRECTORIO_ACTUAL) not in sys.path:
    sys.path.insert(0, str(_DIRECTORIO_ACTUAL))

from inventario import (  # noqa: E402
    HOJA_CATEGORIAS,
    HOJA_PRODUCTOS,
    InventarioDatos,
    obtener_productos_estructurados,
)

# Constantes aprobadas en 02_Especificaciones_v0.md y 02_Prompts/04_Busqueda_Publica.md
TAMANO_PAGINA_DEFECTO: int = 10

MENSAJE_INICIAL_BUSQUEDA: str = "Escribe el nombre del producto que deseas encontrar"
MENSAJE_BUSCANDO_PRODUCTOS: str = "Buscando productos…"
MENSAJE_PRODUCTO_NO_ENCONTRADO: str = "No encontramos este producto en nuestro inventario"
MENSAJE_BUSQUEDA_VACIA: str = (
    "Por favor, escribe el nombre de un producto antes de presionar Buscar."
)

# Campos de búsqueda expresamente prohibidos como filtros independientes en v0 (RF-001, CA-043)
CAMPOS_BUSQUEDA_HABILITADOS: tuple[str, ...] = ("Nombre",)
CAMPOS_FILTRO_INDEPENDIENTE_PROHIBIDOS: tuple[str, ...] = (
    "Marca",
    "Categoria_ID",
    "Nombre_Categoria",
    "Codigo_Producto",
    "Descripcion",
    "Ubicacion_ID",
    "Rack",
    "Columna",
    "Nivel",
    "Posicion",
)


class PrioridadRelevancia(int, Enum):
    """Prioridad de relevancia aprobada en RF-035 y CA-039."""

    COINCIDENCIA_INICIO = 0
    COINCIDENCIA_INTERIOR = 1


class EstadoBusqueda(str, Enum):
    """Estados posibles del motor de búsqueda sobre un inventario válido."""

    INICIAL = "INICIAL"
    BUSQUEDA_VACIA = "BUSQUEDA_VACIA"
    CON_RESULTADOS = "CON_RESULTADOS"
    SIN_RESULTADOS = "SIN_RESULTADOS"


@dataclass(frozen=True)
class ProductoCoincidente:
    """Representa un producto coincidente conservando sus textos originales e información para detalle."""

    codigo_producto: str
    nombre: str
    categoria_id: str
    nombre_categoria: str
    prioridad: PrioridadRelevancia
    descripcion: str = ""
    ubicacion_principal: Mapping[str, Any] | None = None
    ubicaciones_secundarias: tuple[Mapping[str, Any], ...] = ()
    todas_las_ubicaciones: tuple[Mapping[str, Any], ...] = ()

    @property
    def coincide_al_inicio(self) -> bool:
        """Indica si el nombre del producto comienza con el término buscado (CA-039)."""
        return self.prioridad == PrioridadRelevancia.COINCIDENCIA_INICIO

    def a_diccionario_resumen(self) -> dict[str, str]:
        """Devuelve los campos públicos de lista autorizados para el Prompt 04 (Sección 7.4)."""
        return {
            "codigo_producto": self.codigo_producto,
            "nombre": self.nombre,
            "categoria_id": self.categoria_id,
            "nombre_categoria": self.nombre_categoria,
        }

    def a_diccionario_completo(self) -> dict[str, Any]:
        """Devuelve la estructura completa preparada para la futura vista de detalle del Prompt 05."""
        return {
            "codigo_producto": self.codigo_producto,
            "nombre": self.nombre,
            "categoria_id": self.categoria_id,
            "nombre_categoria": self.nombre_categoria,
            "prioridad": self.prioridad.value,
            "descripcion": self.descripcion,
            "ubicacion_principal": (
                dict(self.ubicacion_principal)
                if self.ubicacion_principal is not None
                else None
            ),
            "ubicaciones_secundarias": [dict(u) for u in self.ubicaciones_secundarias],
            "todas_las_ubicaciones": [dict(u) for u in self.todas_las_ubicaciones],
        }


@dataclass(frozen=True)
class ResultadoBusquedaPaginada:
    """Resultado inmutable de una consulta al motor de búsqueda con soporte de paginación."""

    estado: EstadoBusqueda
    termino_original: str
    termino_normalizado: str
    resultados_pagina: tuple[ProductoCoincidente, ...]
    todos_los_resultados: tuple[ProductoCoincidente, ...]
    total_resultados: int
    pagina_actual: int
    tamano_pagina: int
    total_paginas: int
    mensaje_usuario: str

    @property
    def tiene_resultados(self) -> bool:
        return self.estado == EstadoBusqueda.CON_RESULTADOS and self.total_resultados > 0

    @property
    def requiere_paginacion(self) -> bool:
        """Indica si deben mostrarse controles de paginación (solo cuando hay más de una página)."""
        return self.total_paginas > 1

    @property
    def tiene_pagina_anterior(self) -> bool:
        return self.requiere_paginacion and self.pagina_actual > 1

    @property
    def tiene_pagina_siguiente(self) -> bool:
        return self.requiere_paginacion and self.pagina_actual < self.total_paginas

    @property
    def indice_inicio_mostrado(self) -> int:
        """Índice 1-based del primer producto mostrado en la página actual (0 si no hay resultados)."""
        if not self.resultados_pagina:
            return 0
        return (self.pagina_actual - 1) * self.tamano_pagina + 1

    @property
    def indice_fin_mostrado(self) -> int:
        """Índice 1-based del último producto mostrado en la página actual (0 si no hay resultados)."""
        if not self.resultados_pagina:
            return 0
        return self.indice_inicio_mostrado + len(self.resultados_pagina) - 1


def normalizar_texto_busqueda(texto: Any) -> str:
    """Normaliza una cadena para búsqueda ignorando mayúsculas/minúsculas, acentos y espacios extra.

    Cumple RF-003, CA-003 y CA-004:
    - Convierte a texto sin alterar el objeto original.
    - Colapsa espacios múltiples y recorta extremos.
    - Descompone caracteres en NFD y elimina marcas diacríticas (categoría Unicode 'Mn').
    - Aplica `casefold()` para comparación insensible a mayúsculas/minúsculas.
    """
    if texto is None:
        return ""
    try:
        if pd.isna(texto):
            return ""
    except (TypeError, ValueError):
        pass

    limpio = " ".join(str(texto).strip().split())
    if not limpio:
        return ""

    descompuesto = unicodedata.normalize("NFD", limpio)
    sin_acentos = "".join(
        caracter
        for caracter in descompuesto
        if unicodedata.category(caracter) != "Mn"
    )
    return unicodedata.normalize("NFC", sin_acentos).casefold()


def es_termino_busqueda_vacio(termino: Any) -> bool:
    """Determina si el término de búsqueda está vacío o solo contiene espacios/marcas sin texto."""
    return normalizar_texto_busqueda(termino) == ""


def resolver_pagina_busqueda(
    termino_anterior: str | None,
    termino_nuevo: str,
    pagina_solicitada: int = 1,
) -> int:
    """Resuelve el número de página reiniciando a 1 cuando cambia el término buscado (Sección 6.6)."""
    if termino_anterior is None:
        return 1
    if normalizar_texto_busqueda(termino_anterior) != normalizar_texto_busqueda(termino_nuevo):
        return 1
    try:
        pagina_int = int(pagina_solicitada)
    except (TypeError, ValueError):
        return 1
    return max(1, pagina_int)


def extraer_catalogo_productos(
    origen_datos: InventarioDatos | Iterable[Mapping[str, Any]] | pd.DataFrame | Mapping[str, pd.DataFrame],
) -> list[dict[str, Any]]:
    """Obtiene una lista uniforme de registros de productos reutilizando las estructuras de `inventario.py`."""
    if isinstance(origen_datos, InventarioDatos):
        return obtener_productos_estructurados(origen_datos)

    if isinstance(origen_datos, Mapping):
        if HOJA_PRODUCTOS in origen_datos and isinstance(origen_datos[HOJA_PRODUCTOS], pd.DataFrame):
            df_prod = origen_datos[HOJA_PRODUCTOS]
            mapa_cat: dict[str, str] = {}
            if HOJA_CATEGORIAS in origen_datos and isinstance(origen_datos[HOJA_CATEGORIAS], pd.DataFrame):
                df_cat = origen_datos[HOJA_CATEGORIAS]
                if "Categoria_ID" in df_cat.columns and "Nombre_Categoria" in df_cat.columns:
                    mapa_cat = dict(
                        zip(
                            df_cat["Categoria_ID"].astype(str).str.strip(),
                            df_cat["Nombre_Categoria"].astype(str).str.strip(),
                        )
                    )
            registros_map: list[dict[str, Any]] = []
            for _, fila in df_prod.iterrows():
                cat_id = str(fila.get("Categoria_ID", "")).strip()
                registros_map.append(
                    {
                        "codigo_producto": str(fila.get("Codigo_Producto", "")).strip(),
                        "nombre": str(fila.get("Nombre", "")).strip(),
                        "categoria_id": cat_id,
                        "nombre_categoria": mapa_cat.get(cat_id, ""),
                        "descripcion": str(fila.get("Descripcion", "")).strip(),
                        "ubicacion_principal": None,
                        "ubicaciones_secundarias": [],
                        "todas_las_ubicaciones": [],
                    }
                )
            return registros_map

    if isinstance(origen_datos, pd.DataFrame):
        registros_df: list[dict[str, Any]] = []
        for _, fila in origen_datos.iterrows():
            cod = str(fila.get("Codigo_Producto", fila.get("codigo_producto", ""))).strip()
            nom = str(fila.get("Nombre", fila.get("nombre", ""))).strip()
            cat_id = str(fila.get("Categoria_ID", fila.get("categoria_id", ""))).strip()
            nom_cat = str(fila.get("Nombre_Categoria", fila.get("nombre_categoria", ""))).strip()
            desc = str(fila.get("Descripcion", fila.get("descripcion", ""))).strip()
            registros_df.append(
                {
                    "codigo_producto": cod,
                    "nombre": nom,
                    "categoria_id": cat_id,
                    "nombre_categoria": nom_cat,
                    "descripcion": desc,
                    "ubicacion_principal": None,
                    "ubicaciones_secundarias": [],
                    "todas_las_ubicaciones": [],
                }
            )
        return registros_df

    if isinstance(origen_datos, Iterable):
        registros_iter: list[dict[str, Any]] = []
        for item in origen_datos:
            if not isinstance(item, Mapping):
                raise TypeError(
                    f"Cada elemento del catálogo debe ser un mapeo o diccionario; se recibió {type(item).__name__}."
                )
            cod = str(item.get("codigo_producto", item.get("Codigo_Producto", ""))).strip()
            nom = str(item.get("nombre", item.get("Nombre", ""))).strip()
            cat_id = str(item.get("categoria_id", item.get("Categoria_ID", ""))).strip()
            nom_cat = str(item.get("nombre_categoria", item.get("Nombre_Categoria", ""))).strip()
            desc = str(item.get("descripcion", item.get("Descripcion", ""))).strip()
            ubic_prin = item.get("ubicacion_principal")
            ubic_sec = item.get("ubicaciones_secundarias") or ()
            todas_ubic = item.get("todas_las_ubicaciones") or ()
            registros_iter.append(
                {
                    "codigo_producto": cod,
                    "nombre": nom,
                    "categoria_id": cat_id,
                    "nombre_categoria": nom_cat,
                    "descripcion": desc,
                    "ubicacion_principal": dict(ubic_prin) if isinstance(ubic_prin, Mapping) else None,
                    "ubicaciones_secundarias": [
                        dict(u) for u in ubic_sec if isinstance(u, Mapping)
                    ],
                    "todas_las_ubicaciones": [
                        dict(u) for u in todas_ubic if isinstance(u, Mapping)
                    ],
                }
            )
        return registros_iter

    raise TypeError(
        f"Origen de datos no soportado para la búsqueda: {type(origen_datos).__name__}."
    )


def buscar_productos_por_nombre(
    origen_datos: InventarioDatos | Iterable[Mapping[str, Any]] | pd.DataFrame | Mapping[str, pd.DataFrame],
    termino_busqueda: str,
) -> list[ProductoCoincidente]:
    """Busca productos exclusivamente por su campo `Nombre`, aplicando normalización y orden por relevancia.

    Reglas aplicadas:
    - RF-001 / CA-001 / CA-043: Evalúa únicamente el campo `Nombre` de la hoja `Productos`.
      Ignora coincidencias que existan solo en código, categoría, marca, descripción o ubicación.
    - RF-002 / CA-002: Admite coincidencias parciales en cualquier posición del nombre.
    - RF-003 / CA-003 / CA-004: Ignora diferencias de mayúsculas/minúsculas y acentuación,
      conservando intactos los textos originales del inventario.
    - RF-035 / CA-039: Ordena primero los productos cuyo nombre normalizado comienza con el término
      normalizado (`COINCIDENCIA_INICIO = 0`) y después los que lo contienen en otra posición
      (`COINCIDENCIA_INTERIOR = 1`), desempatando de forma estable por `(nombre_normalizado, codigo_producto)`.
    """
    termino_norm = normalizar_texto_busqueda(termino_busqueda)
    if not termino_norm:
        return []

    catalogo = extraer_catalogo_productos(origen_datos)
    coincidencias_con_clave: list[tuple[tuple[int, str, str], ProductoCoincidente]] = []

    for item in catalogo:
        nombre_original = str(item.get("nombre", "")).strip()
        if not nombre_original:
            continue

        nombre_norm = normalizar_texto_busqueda(nombre_original)
        if termino_norm not in nombre_norm:
            continue

        if nombre_norm.startswith(termino_norm):
            prioridad = PrioridadRelevancia.COINCIDENCIA_INICIO
        else:
            prioridad = PrioridadRelevancia.COINCIDENCIA_INTERIOR

        codigo_original = str(item.get("codigo_producto", "")).strip()
        categoria_id = str(item.get("categoria_id", "")).strip()
        nombre_categoria = str(item.get("nombre_categoria", "")).strip()
        descripcion = str(item.get("descripcion", "")).strip()

        ubic_prin_raw = item.get("ubicacion_principal")
        ubic_sec_raw = item.get("ubicaciones_secundarias") or ()
        todas_ubic_raw = item.get("todas_las_ubicaciones") or ()

        producto = ProductoCoincidente(
            codigo_producto=codigo_original,
            nombre=nombre_original,
            categoria_id=categoria_id,
            nombre_categoria=nombre_categoria,
            prioridad=prioridad,
            descripcion=descripcion,
            ubicacion_principal=(
                dict(ubic_prin_raw) if isinstance(ubic_prin_raw, Mapping) else None
            ),
            ubicaciones_secundarias=tuple(
                dict(u) for u in ubic_sec_raw if isinstance(u, Mapping)
            ),
            todas_las_ubicaciones=tuple(
                dict(u) for u in todas_ubic_raw if isinstance(u, Mapping)
            ),
        )

        clave_orden = (prioridad.value, nombre_norm, codigo_original)
        coincidencias_con_clave.append((clave_orden, producto))

    coincidencias_con_clave.sort(key=lambda par: par[0])
    return [par[1] for par in coincidencias_con_clave]


def paginar_resultados(
    resultados: Sequence[ProductoCoincidente],
    pagina: int = 1,
    tamano_pagina: int = TAMANO_PAGINA_DEFECTO,
) -> tuple[tuple[ProductoCoincidente, ...], int, int]:
    """Divide la lista ordenada de coincidencias en páginas de hasta `tamano_pagina` elementos (RF-036, CA-040).

    Devuelve `(resultados_pagina, pagina_ajustada, total_paginas)`.
    """
    if tamano_pagina < 1:
        raise ValueError("El tamaño de página debe ser al menos 1.")

    total_items = len(resultados)
    if total_items == 0:
        return (), 1, 0

    total_paginas = math.ceil(total_items / tamano_pagina)
    try:
        pagina_solicitada = int(pagina)
    except (TypeError, ValueError):
        pagina_solicitada = 1

    pagina_ajustada = max(1, min(pagina_solicitada, total_paginas))
    inicio = (pagina_ajustada - 1) * tamano_pagina
    fin = inicio + tamano_pagina
    rebanada = tuple(resultados[inicio:fin])
    return rebanada, pagina_ajustada, total_paginas


def ejecutar_busqueda_productos(
    origen_datos: InventarioDatos | Iterable[Mapping[str, Any]] | pd.DataFrame | Mapping[str, pd.DataFrame] | None,
    termino_busqueda: str,
    pagina: int = 1,
    tamano_pagina: int = TAMANO_PAGINA_DEFECTO,
) -> ResultadoBusquedaPaginada:
    """Ejecuta una búsqueda completa validando término vacío, ordenando por relevancia y paginando resultados."""
    if tamano_pagina < 1:
        raise ValueError("El tamaño de página debe ser al menos 1.")

    termino_original = "" if termino_busqueda is None else str(termino_busqueda)
    termino_norm = normalizar_texto_busqueda(termino_original)

    # RF-037 / CA-041 / Sección 7.6: No consultar productos cuando el término está vacío
    if not termino_norm:
        return ResultadoBusquedaPaginada(
            estado=EstadoBusqueda.BUSQUEDA_VACIA,
            termino_original=termino_original,
            termino_normalizado="",
            resultados_pagina=(),
            todos_los_resultados=(),
            total_resultados=0,
            pagina_actual=1,
            tamano_pagina=tamano_pagina,
            total_paginas=0,
            mensaje_usuario=MENSAJE_BUSQUEDA_VACIA,
        )

    if origen_datos is None:
        raise ValueError(
            "Se requiere un origen de datos válido del inventario para ejecutar la búsqueda."
        )

    coincidencias = buscar_productos_por_nombre(origen_datos, termino_original)
    total_resultados = len(coincidencias)

    # RF-008 / CA-006 / Sección 7.5: Mensaje exacto cuando no existen coincidencias
    if total_resultados == 0:
        return ResultadoBusquedaPaginada(
            estado=EstadoBusqueda.SIN_RESULTADOS,
            termino_original=termino_original,
            termino_normalizado=termino_norm,
            resultados_pagina=(),
            todos_los_resultados=(),
            total_resultados=0,
            pagina_actual=1,
            tamano_pagina=tamano_pagina,
            total_paginas=0,
            mensaje_usuario=MENSAJE_PRODUCTO_NO_ENCONTRADO,
        )

    resultados_pagina, pagina_actual, total_paginas = paginar_resultados(
        coincidencias,
        pagina=pagina,
        tamano_pagina=tamano_pagina,
    )

    mensaje_exito = (
        f"Se encontraron {total_resultados} producto(s) para «{termino_original.strip()}»."
    )
    return ResultadoBusquedaPaginada(
        estado=EstadoBusqueda.CON_RESULTADOS,
        termino_original=termino_original,
        termino_normalizado=termino_norm,
        resultados_pagina=resultados_pagina,
        todos_los_resultados=tuple(coincidencias),
        total_resultados=total_resultados,
        pagina_actual=pagina_actual,
        tamano_pagina=tamano_pagina,
        total_paginas=total_paginas,
        mensaje_usuario=mensaje_exito,
    )

