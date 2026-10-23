"""Motor de búsqueda pública de productos por nombre, paginación y consulta de detalles/ubicaciones.

Proyecto: FerreteríaMS v0
Tareas: FERMS-V0-P04, FERMS-V0-P05
Requisitos relacionados: RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007, RF-008,
RF-009, RF-024, RF-035, RF-036, RF-037.
Criterios relacionados: CA-001, CA-002, CA-003, CA-004, CA-005, CA-006, CA-007, CA-039,
CA-040, CA-041, CA-043.

Este módulo recibe información estructurada del inventario y devuelve coincidencias
calculadas exclusivamente sobre el campo `Nombre` de la hoja `Productos`, ordenadas
por relevancia y paginadas de diez en diez, así como el detalle estructurado y las
ubicaciones físicas (principal y secundarias) de un producto seleccionado.
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
    ErrorValorActivoInvalido,
    InventarioDatos,
    normalizar_valor_activo,
    obtener_producto_por_codigo,
    obtener_productos_estructurados,
    validar_inventario,
)

# Constantes aprobadas en 02_Especificaciones_v0.md, 02_Prompts/04_Busqueda_Publica.md y 05_Detalles_Ubicaciones.md
TAMANO_PAGINA_DEFECTO: int = 10

MENSAJE_INICIAL_BUSQUEDA: str = "Escribe el nombre del producto que deseas encontrar"
MENSAJE_BUSCANDO_PRODUCTOS: str = "Buscando productos…"
MENSAJE_PRODUCTO_NO_ENCONTRADO: str = "No encontramos este producto en nuestro inventario"
MENSAJE_BUSQUEDA_VACIA: str = (
    "Por favor, escribe el nombre de un producto antes de presionar Buscar."
)

TEXTO_SIN_DESCRIPCION: str = "Sin descripción registrada."
MENSAJE_SIN_UBICACIONES_SECUNDARIAS: str = (
    "Este producto solamente tiene una ubicación física registrada (sin ubicaciones secundarias)."
)
MENSAJE_PRODUCTO_SELECCIONADO_NO_DISPONIBLE: str = (
    "El producto seleccionado no está disponible en la consulta actual."
)
MENSAJE_ERROR_INTEGRIDAD_DETALLE: str = (
    "Se detectó una inconsistencia de integridad en los datos de ubicación o registro del producto."
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


def _resolver_estado_activo_registro(item: Mapping[str, Any] | pd.Series) -> tuple[str, bool]:
    """Determina el estado ('Sí'/'No', es_activo) de un registro o fila de producto con retrocompatibilidad."""
    if "es_activo" in item and isinstance(item["es_activo"], bool):
        es_activo = bool(item["es_activo"])
        return ("Sí" if es_activo else "No"), es_activo

    val_bruto: Any = "Sí"
    if "Activo" in item:
        val_bruto = item["Activo"]
    elif "activo" in item:
        val_bruto = item["activo"]

    if val_bruto is None:
        return "Sí", True
    try:
        if pd.isna(val_bruto):
            return "Sí", True
    except (TypeError, ValueError):
        pass

    texto_limpio = str(val_bruto).strip()
    if not texto_limpio:
        return "Sí", True
    try:
        activo_norm = normalizar_valor_activo(texto_limpio)
    except ErrorValorActivoInvalido:
        return "No", False
    return activo_norm, (activo_norm == "Sí")


def extraer_catalogo_productos(
    origen_datos: InventarioDatos | Iterable[Mapping[str, Any]] | pd.DataFrame | Mapping[str, pd.DataFrame],
    *,
    solo_activos: bool = True,
) -> list[dict[str, Any]]:
    """Obtiene una lista uniforme de registros de productos reutilizando las estructuras de `inventario.py`.

    Por defecto (`solo_activos=True`) excluye los productos inactivos (`Activo = "No"`),
    cumpliendo RF-F-008 y CA-F-007 para la búsqueda pública y el catálogo activo.
    """
    if isinstance(origen_datos, InventarioDatos):
        return obtener_productos_estructurados(
            origen_datos, incluir_inactivos=not solo_activos
        )

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
                activo_texto, es_activo = _resolver_estado_activo_registro(fila)
                if solo_activos and not es_activo:
                    continue
                cat_id = str(fila.get("Categoria_ID", "")).strip()
                registros_map.append(
                    {
                        "codigo_producto": str(fila.get("Codigo_Producto", "")).strip(),
                        "nombre": str(fila.get("Nombre", "")).strip(),
                        "categoria_id": cat_id,
                        "nombre_categoria": mapa_cat.get(cat_id, ""),
                        "descripcion": str(fila.get("Descripcion", "")).strip(),
                        "activo": activo_texto,
                        "es_activo": es_activo,
                        "ubicacion_principal": None,
                        "ubicaciones_secundarias": [],
                        "todas_las_ubicaciones": [],
                    }
                )
            return registros_map

    if isinstance(origen_datos, pd.DataFrame):
        registros_df: list[dict[str, Any]] = []
        for _, fila in origen_datos.iterrows():
            activo_texto, es_activo = _resolver_estado_activo_registro(fila)
            if solo_activos and not es_activo:
                continue
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
                    "activo": activo_texto,
                    "es_activo": es_activo,
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
            activo_texto, es_activo = _resolver_estado_activo_registro(item)
            if solo_activos and not es_activo:
                continue
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
                    "activo": activo_texto,
                    "es_activo": es_activo,
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


def obtener_catalogo_productos_activos(
    origen_datos: InventarioDatos | Iterable[Mapping[str, Any]] | pd.DataFrame | Mapping[str, pd.DataFrame],
) -> list[dict[str, Any]]:
    """Devuelve exclusivamente el catálogo de productos activos (`Activo = 'Sí'`) para consultas públicas y contexto activo."""
    return extraer_catalogo_productos(origen_datos, solo_activos=True)


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
        ubic_prin_dict = (
            dict(ubic_prin_raw) if isinstance(ubic_prin_raw, Mapping) else None
        )
        ubic_sec_raw = item.get("ubicaciones_secundarias") or ()
        ubic_sec_ordenadas = _ordenar_ubicaciones_secundarias_dict(
            ubic_sec_raw,
            ubicacion_principal=ubic_prin_dict,
        )
        todas_ubic_ordenadas = (
            ([ubic_prin_dict] if ubic_prin_dict is not None else [])
            + ubic_sec_ordenadas
        )

        producto = ProductoCoincidente(
            codigo_producto=codigo_original,
            nombre=nombre_original,
            categoria_id=categoria_id,
            nombre_categoria=nombre_categoria,
            prioridad=prioridad,
            descripcion=descripcion,
            ubicacion_principal=ubic_prin_dict,
            ubicaciones_secundarias=tuple(ubic_sec_ordenadas),
            todas_las_ubicaciones=tuple(todas_ubic_ordenadas),
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


class EstadoDetalleProducto(str, Enum):
    """Estados posibles al consultar el detalle y las ubicaciones de un producto seleccionado (Prompt 05)."""

    SIN_SELECCION = "SIN_SELECCION"
    DETALLE_DISPONIBLE = "DETALLE_DISPONIBLE"
    PRODUCTO_NO_DISPONIBLE = "PRODUCTO_NO_DISPONIBLE"
    ERROR_INTEGRIDAD_UBICACION = "ERROR_INTEGRIDAD_UBICACION"


def formatear_cadena_ubicacion(ubicacion: Mapping[str, Any] | UbicacionFisicaDetalle) -> str:
    """Devuelve la disposición visual clara de una ubicación física (Sección 6 del Prompt 05).

    Formato: `Rack {rack} → Columna {columna} → Nivel {nivel} → Posición {posicion}`
    Conserva intactos los valores originales del inventario sin reinterpretarlos.
    """
    if isinstance(ubicacion, UbicacionFisicaDetalle):
        rack = ubicacion.rack
        columna = ubicacion.columna
        nivel = ubicacion.nivel
        posicion = ubicacion.posicion
    elif isinstance(ubicacion, Mapping):
        rack = str(ubicacion.get("rack", ubicacion.get("Rack", ""))).strip()
        columna = str(ubicacion.get("columna", ubicacion.get("Columna", ""))).strip()
        nivel = str(ubicacion.get("nivel", ubicacion.get("Nivel", ""))).strip()
        posicion = str(ubicacion.get("posicion", ubicacion.get("Posicion", ""))).strip()
    else:
        raise TypeError(f"Tipo de ubicación no soportado: {type(ubicacion).__name__}.")

    return f"Rack {rack} → Columna {columna} → Nivel {nivel} → Posición {posicion}"


def _clave_orden_ubicacion_dict(ubic: Mapping[str, Any]) -> tuple[str, str, str, str, str]:
    """Clave determinista y estable para ordenar ubicaciones físicas."""
    rack = str(ubic.get("rack", ubic.get("Rack", ""))).strip()
    columna = str(ubic.get("columna", ubic.get("Columna", ""))).strip()
    nivel = str(ubic.get("nivel", ubic.get("Nivel", ""))).strip()
    posicion = str(ubic.get("posicion", ubic.get("Posicion", ""))).strip()
    ubic_id = str(ubic.get("ubicacion_id", ubic.get("Ubicacion_ID", ""))).strip()
    return (rack, columna, nivel, posicion, ubic_id)


def _ordenar_ubicaciones_secundarias_dict(
    ubicaciones_secundarias: Iterable[Mapping[str, Any]],
    *,
    ubicacion_principal: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Ordena de forma estable las ubicaciones secundarias y evita duplicar la ubicación principal (Sección 7)."""
    id_principal = ""
    coord_principal: tuple[str, str, str, str] | None = None
    if isinstance(ubicacion_principal, Mapping):
        id_principal = str(
            ubicacion_principal.get(
                "ubicacion_id", ubicacion_principal.get("Ubicacion_ID", "")
            )
        ).strip()
        coord_principal = (
            str(ubicacion_principal.get("rack", ubicacion_principal.get("Rack", ""))).strip(),
            str(ubicacion_principal.get("columna", ubicacion_principal.get("Columna", ""))).strip(),
            str(ubicacion_principal.get("nivel", ubicacion_principal.get("Nivel", ""))).strip(),
            str(ubicacion_principal.get("posicion", ubicacion_principal.get("Posicion", ""))).strip(),
        )

    ids_vistos: set[str] = set()
    coords_vistas: set[tuple[str, str, str, str]] = set()
    filtradas: list[dict[str, Any]] = []

    for item in ubicaciones_secundarias:
        if not isinstance(item, Mapping):
            continue
        copia = dict(item)
        ubic_id = str(copia.get("ubicacion_id", copia.get("Ubicacion_ID", ""))).strip()
        coord = (
            str(copia.get("rack", copia.get("Rack", ""))).strip(),
            str(copia.get("columna", copia.get("Columna", ""))).strip(),
            str(copia.get("nivel", copia.get("Nivel", ""))).strip(),
            str(copia.get("posicion", copia.get("Posicion", ""))).strip(),
        )

        if id_principal and ubic_id == id_principal:
            continue
        if coord_principal is not None and any(coord_principal) and coord == coord_principal:
            continue
        if ubic_id and ubic_id in ids_vistos:
            continue
        if any(coord) and coord in coords_vistas:
            continue

        if ubic_id:
            ids_vistos.add(ubic_id)
        if any(coord):
            coords_vistas.add(coord)
        filtradas.append(copia)

    filtradas.sort(key=_clave_orden_ubicacion_dict)
    return filtradas


@dataclass(frozen=True)
class UbicacionFisicaDetalle:
    """Representación inmutable de una ubicación física validada (RF-006, RF-007)."""

    ubicacion_id: str
    rack: str
    columna: str
    nivel: str
    posicion: str
    es_principal: bool

    @property
    def etiqueta_flechas(self) -> str:
        """Devuelve la cadena `Rack X → Columna Y → Nivel Z → Posición W`."""
        return formatear_cadena_ubicacion(self)

    def a_diccionario(self) -> dict[str, Any]:
        return {
            "ubicacion_id": self.ubicacion_id,
            "rack": self.rack,
            "columna": self.columna,
            "nivel": self.nivel,
            "posicion": self.posicion,
            "es_principal": self.es_principal,
            "principal": "Sí" if self.es_principal else "No",
            "etiqueta": self.etiqueta_flechas,
        }


@dataclass(frozen=True)
class DetalleProductoLocalizado:
    """Información descriptiva y localización física completa de un producto seleccionado (RF-005, RF-006, RF-007)."""

    codigo_producto: str
    nombre: str
    categoria_id: str
    nombre_categoria: str
    descripcion: str
    ubicacion_principal: UbicacionFisicaDetalle
    ubicaciones_secundarias: tuple[UbicacionFisicaDetalle, ...] = ()

    @property
    def tiene_descripcion(self) -> bool:
        return bool(self.descripcion.strip())

    @property
    def descripcion_presentacion(self) -> str:
        """Devuelve la descripción original o un texto neutro cuando está vacía (Sección 5)."""
        return self.descripcion if self.tiene_descripcion else TEXTO_SIN_DESCRIPCION

    @property
    def tiene_ubicaciones_secundarias(self) -> bool:
        return len(self.ubicaciones_secundarias) > 0

    @property
    def total_ubicaciones(self) -> int:
        return 1 + len(self.ubicaciones_secundarias)

    @property
    def todas_las_ubicaciones(self) -> tuple[UbicacionFisicaDetalle, ...]:
        return (self.ubicacion_principal, *self.ubicaciones_secundarias)


@dataclass(frozen=True)
class ResultadoConsultaDetalle:
    """Resultado estructurado al consultar los detalles y ubicaciones de un producto seleccionado."""

    estado: EstadoDetalleProducto
    codigo_solicitado: str
    mensaje_usuario: str
    detalle: DetalleProductoLocalizado | None = None
    detalle_error: str = ""

    @property
    def tiene_detalle(self) -> bool:
        return (
            self.estado == EstadoDetalleProducto.DETALLE_DISPONIBLE
            and self.detalle is not None
        )


def _construir_ubicacion_detalle_desde_mapping(
    datos_ubic: Mapping[str, Any],
    *,
    es_principal: bool,
) -> UbicacionFisicaDetalle | None:
    """Construye y verifica que una ubicación física posea todos sus campos requeridos."""
    ubic_id = str(
        datos_ubic.get("ubicacion_id", datos_ubic.get("Ubicacion_ID", ""))
    ).strip()
    rack = str(datos_ubic.get("rack", datos_ubic.get("Rack", ""))).strip()
    columna = str(datos_ubic.get("columna", datos_ubic.get("Columna", ""))).strip()
    nivel = str(datos_ubic.get("nivel", datos_ubic.get("Nivel", ""))).strip()
    posicion = str(datos_ubic.get("posicion", datos_ubic.get("Posicion", ""))).strip()

    if not ubic_id or not rack or not columna or not nivel or not posicion:
        return None

    return UbicacionFisicaDetalle(
        ubicacion_id=ubic_id,
        rack=rack,
        columna=columna,
        nivel=nivel,
        posicion=posicion,
        es_principal=es_principal,
    )


def consultar_detalle_producto(
    inventario: InventarioDatos | None,
    codigo_producto: Any,
    *,
    resultados_activos: Sequence[ProductoCoincidente] | None = None,
) -> ResultadoConsultaDetalle:
    """Recupera los detalles y ubicaciones físicas de un producto desde el inventario validado.

    Cumple las Secciones 4, 5, 6, 7 y 8 del Prompt 05:
    - Exige que `codigo_producto` se conserve como texto (`str`), incluidos los ceros iniciales,
      rechazando conversiones numéricas automáticas (`int`, `float`, `bool`).
    - Reutiliza `validar_inventario` y `obtener_producto_por_codigo` de `inventario.py` sin
      volver a implementar por separado las relaciones entre las cuatro hojas.
    - Si detecta alguna inconsistencia de integridad en los datos del inventario (p. ej. producto
      sin ubicación principal, con múltiples ubicaciones principales o con referencias rotas),
      la comunica como `ERROR_INTEGRIDAD_UBICACION` sin corregirla silenciosamente.
    - Si el código no pertenece al inventario validado de la búsqueda activa, devuelve
      `PRODUCTO_NO_DISPONIBLE` sin exponer datos de otro producto ni inventar ubicaciones.
    - Ordena las ubicaciones secundarias de forma estable y reproducible sin duplicar la principal.
    """
    if codigo_producto is None:
        return ResultadoConsultaDetalle(
            estado=EstadoDetalleProducto.SIN_SELECCION,
            codigo_solicitado="",
            mensaje_usuario="",
        )

    # Prohibición de convertir automáticamente códigos a números (Secciones 4.1 y 5)
    if not isinstance(codigo_producto, str):
        return ResultadoConsultaDetalle(
            estado=EstadoDetalleProducto.PRODUCTO_NO_DISPONIBLE,
            codigo_solicitado=str(codigo_producto),
            mensaje_usuario=MENSAJE_PRODUCTO_SELECCIONADO_NO_DISPONIBLE,
        )

    codigo_limpio = codigo_producto.strip()
    if not codigo_limpio:
        return ResultadoConsultaDetalle(
            estado=EstadoDetalleProducto.SIN_SELECCION,
            codigo_solicitado="",
            mensaje_usuario="",
        )

    if inventario is None or not isinstance(inventario, InventarioDatos):
        return ResultadoConsultaDetalle(
            estado=EstadoDetalleProducto.PRODUCTO_NO_DISPONIBLE,
            codigo_solicitado=codigo_limpio,
            mensaje_usuario=MENSAJE_PRODUCTO_SELECCIONADO_NO_DISPONIBLE,
        )

    # Comprobar integridad estructural y relacional mediante `inventario.py` (Sección 6)
    try:
        hojas = inventario.obtener_hojas()
        resultado_val = validar_inventario(hojas, lanzar_excepcion=False)
    except Exception as exc_val:
        return ResultadoConsultaDetalle(
            estado=EstadoDetalleProducto.ERROR_INTEGRIDAD_UBICACION,
            codigo_solicitado=codigo_limpio,
            mensaje_usuario=MENSAJE_ERROR_INTEGRIDAD_DETALLE,
            detalle_error=str(exc_val),
        )

    if not resultado_val.es_valido:
        resumen_errores = "; ".join(err.mensaje for err in resultado_val.errores)
        return ResultadoConsultaDetalle(
            estado=EstadoDetalleProducto.ERROR_INTEGRIDAD_UBICACION,
            codigo_solicitado=codigo_limpio,
            mensaje_usuario=MENSAJE_ERROR_INTEGRIDAD_DETALLE,
            detalle_error=resumen_errores,
        )

    # Si existe una lista de resultados activos en la consulta, el código debe pertenecer a ella (Sección 4.4)
    if resultados_activos is not None:
        codigos_en_consulta = {
            prod.codigo_producto
            for prod in resultados_activos
            if isinstance(prod, ProductoCoincidente)
        }
        if codigo_limpio not in codigos_en_consulta:
            return ResultadoConsultaDetalle(
                estado=EstadoDetalleProducto.PRODUCTO_NO_DISPONIBLE,
                codigo_solicitado=codigo_limpio,
                mensaje_usuario=MENSAJE_PRODUCTO_SELECCIONADO_NO_DISPONIBLE,
            )

    # Reutilizar `obtener_producto_por_codigo` de `inventario.py` excluyendo inactivos (Sección 8.1, RF-F-008)
    datos_producto = obtener_producto_por_codigo(
        inventario, codigo_limpio, incluir_inactivos=False
    )
    if datos_producto is None:
        return ResultadoConsultaDetalle(
            estado=EstadoDetalleProducto.PRODUCTO_NO_DISPONIBLE,
            codigo_solicitado=codigo_limpio,
            mensaje_usuario=MENSAJE_PRODUCTO_SELECCIONADO_NO_DISPONIBLE,
        )

    ubic_prin_raw = datos_producto.get("ubicacion_principal")
    if not isinstance(ubic_prin_raw, Mapping):
        return ResultadoConsultaDetalle(
            estado=EstadoDetalleProducto.ERROR_INTEGRIDAD_UBICACION,
            codigo_solicitado=codigo_limpio,
            mensaje_usuario=MENSAJE_ERROR_INTEGRIDAD_DETALLE,
            detalle_error=f"El producto '{codigo_limpio}' no posee una ubicación principal válida.",
        )

    ubicacion_principal = _construir_ubicacion_detalle_desde_mapping(
        ubic_prin_raw,
        es_principal=True,
    )
    if ubicacion_principal is None:
        return ResultadoConsultaDetalle(
            estado=EstadoDetalleProducto.ERROR_INTEGRIDAD_UBICACION,
            codigo_solicitado=codigo_limpio,
            mensaje_usuario=MENSAJE_ERROR_INTEGRIDAD_DETALLE,
            detalle_error=(
                f"La ubicación principal del producto '{codigo_limpio}' tiene campos físicos incompletos."
            ),
        )

    ubic_sec_raw = datos_producto.get("ubicaciones_secundarias") or ()
    ubic_sec_ordenadas_dict = _ordenar_ubicaciones_secundarias_dict(
        ubic_sec_raw,
        ubicacion_principal=ubic_prin_raw,
    )

    ubicaciones_secundarias: list[UbicacionFisicaDetalle] = []
    for item_sec in ubic_sec_ordenadas_dict:
        ubic_sec_obj = _construir_ubicacion_detalle_desde_mapping(
            item_sec,
            es_principal=False,
        )
        if ubic_sec_obj is None:
            return ResultadoConsultaDetalle(
                estado=EstadoDetalleProducto.ERROR_INTEGRIDAD_UBICACION,
                codigo_solicitado=codigo_limpio,
                mensaje_usuario=MENSAJE_ERROR_INTEGRIDAD_DETALLE,
                detalle_error=(
                    f"Una ubicación secundaria del producto '{codigo_limpio}' tiene campos físicos incompletos."
                ),
            )
        ubicaciones_secundarias.append(ubic_sec_obj)

    nombre_prod = str(datos_producto.get("nombre", "")).strip()
    categoria_id = str(datos_producto.get("categoria_id", "")).strip()
    nombre_categoria = str(datos_producto.get("nombre_categoria", "")).strip()
    descripcion = str(datos_producto.get("descripcion", "")).strip()

    if not nombre_prod or not categoria_id or not nombre_categoria:
        return ResultadoConsultaDetalle(
            estado=EstadoDetalleProducto.ERROR_INTEGRIDAD_UBICACION,
            codigo_solicitado=codigo_limpio,
            mensaje_usuario=MENSAJE_ERROR_INTEGRIDAD_DETALLE,
            detalle_error=(
                f"Los datos generales o la categoría del producto '{codigo_limpio}' están incompletos."
            ),
        )

    detalle = DetalleProductoLocalizado(
        codigo_producto= str(datos_producto.get("codigo_producto", codigo_limpio)).strip(),
        nombre=nombre_prod,
        categoria_id=categoria_id,
        nombre_categoria=nombre_categoria,
        descripcion=descripcion,
        ubicacion_principal=ubicacion_principal,
        ubicaciones_secundarias=tuple(ubicaciones_secundarias),
    )

    return ResultadoConsultaDetalle(
        estado=EstadoDetalleProducto.DETALLE_DISPONIBLE,
        codigo_solicitado=detalle.codigo_producto,
        mensaje_usuario=f"Detalles y ubicación de «{detalle.nombre}».",
        detalle=detalle,
    )


