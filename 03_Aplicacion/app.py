"""Interfaz pública responsive de búsqueda, detalles, localización física y área visual Gemini («Próximamente») de FerreteríaMS v0.

Proyecto: FerreteríaMS v0
Tareas: FERMS-V0-P04, FERMS-V0-P05, FERMS-V0-P06
Requisitos relacionados: RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007, RF-008,
RF-009, RF-010, RF-024, RF-025, RF-028, RF-032, RF-033, RF-034, RF-035, RF-036, RF-037, RF-038.
Criterios relacionados: CA-001, CA-002, CA-003, CA-004, CA-005, CA-006, CA-007, CA-008,
CA-031, CA-032, CA-033, CA-034, CA-039, CA-040, CA-041, CA-042, CA-043, CA-060, CA-061.

Adaptación de la plantilla académica a FerreteríaMS v0:
- Conserva la estructura de inicialización de Streamlit (`st.set_page_config`, `st.title`,
  `st.caption`), el uso estructurado de `st.session_state` y el manejo explícito de errores.
- Retira por completo las importaciones y llamadas al cliente de inteligencia artificial,
  la exigencia de clave de API para el asistente y la interfaz de chat operativa.
- Incorpora la presentación visual responsive (escritorio, tableta y teléfono) y el área
  visual reservada de «Asistente Gemini — Próximamente» sin capacidades operativas de IA en v0.
- Reutiliza `03_Aplicacion/inventario.py`, `03_Aplicacion/github_inventario.py` y
  `03_Aplicacion/busqueda.py` sin duplicar sus responsabilidades ni realizar escrituras remotas.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, MutableMapping

import streamlit as st

_DIRECTORIO_ACTUAL = Path(__file__).resolve().parent
if str(_DIRECTORIO_ACTUAL) not in sys.path:
    sys.path.insert(0, str(_DIRECTORIO_ACTUAL))

import github_inventario  # noqa: E402
from busqueda import (  # noqa: E402
    MENSAJE_BUSCANDO_PRODUCTOS,
    MENSAJE_BUSQUEDA_VACIA,
    MENSAJE_ERROR_INTEGRIDAD_DETALLE,
    MENSAJE_INICIAL_BUSQUEDA,
    MENSAJE_PRODUCTO_NO_ENCONTRADO,
    MENSAJE_PRODUCTO_SELECCIONADO_NO_DISPONIBLE,
    MENSAJE_SIN_UBICACIONES_SECUNDARIAS,
    TAMANO_PAGINA_DEFECTO,
    TEXTO_SIN_DESCRIPCION,
    DetalleProductoLocalizado,
    EstadoBusqueda,
    EstadoDetalleProducto,
    ProductoCoincidente,
    ResultadoBusquedaPaginada,
    ResultadoConsultaDetalle,
    UbicacionFisicaDetalle,
    consultar_detalle_producto,
    ejecutar_busqueda_productos,
    es_termino_busqueda_vacio,
    formatear_cadena_ubicacion,
    normalizar_texto_busqueda,
    resolver_pagina_busqueda,
)
from github_inventario import (  # noqa: E402
    CONFIGURACION_POR_DEFECTO,
    CategoriaResultadoConsulta,
    CodigoErrorGitHub,
    ConfiguracionRepositorioGitHub,
    ErrorArchivoExcelRemotoCorrupto,
    ErrorArchivoRemotoInexistente,
    ErrorEsquemaInventarioRemoto,
    ErrorLecturaGitHub,
    ResultadoLecturaInventarioRemoto,
    ocultar_secretos_en_texto,
)
from inventario import InventarioDatos  # noqa: E402

# Constantes de identificación y textos públicos aprobados para FerreteríaMS v0
TITULO: str = "FerreteríaMS"
ICONO_PAGINA: str = "🛠️"
DESCRIPCION: str = (
    "Encuentra rápidamente lo que necesitas para tus proyectos. "
    "Busca productos por su nombre para consultar su registro en el inventario de la tienda."
)
TITULO_SECCION_BUSQUEDA: str = "Buscar productos"
PLACEHOLDER_CAMPO_BUSQUEDA: str = "Escribe el nombre del producto..."
TEXTO_AYUDA_EJEMPLOS: str = (
    'Escribe el nombre de un producto en el buscador para ver los resultados aquí. '
    'Por ejemplo: "martillo", "tornillo" o "cinta".'
)
AVISO_ACCESO_PUBLICO: str = (
    "Puedes buscar productos sin iniciar sesión. "
    "El acceso público te permite consultar nuestro catálogo. No necesitas una cuenta."
)
MENSAJE_CAMBIO_TERMINO_PENDIENTE: str = (
    "Has modificado el término en el buscador. Presiona «Buscar» para consultar los resultados."
)

# Constantes de selección y vista de detalle de producto (Secciones 4, 5, 6, 7 y 9 del Prompt 05)
TEXTO_BOTON_VER_DETALLE: str = "Ver detalles y ubicación"
TEXTO_BOTON_VOLVER_RESULTADOS: str = "⬅️ Volver a los resultados"
TITULO_SECCION_DETALLE_PRODUCTO: str = "Detalles del producto"
TITULO_SECCION_UBICACION_PRINCIPAL: str = "Ubicación principal"
TITULO_SECCION_UBICACIONES_SECUNDARIAS: str = "Ubicaciones secundarias"

# Constantes del área visual de Gemini «Próximamente» y diseño responsive (Secciones 5, 6 y 7 del Prompt 06)
RUTA_ARCHIVO_ESTILOS_CSS: Path = _DIRECTORIO_ACTUAL / "estilos.css"
ETIQUETA_BANNER_SUPERIOR: str = "TU FERRETERÍA · LOCALIZACIÓN DE PRODUCTOS EN TIENDA"
TITULO_SECCION_GEMINI: str = "Asistente Gemini"
ESTADO_GEMINI_PROXIMAMENTE: str = "Próximamente"
SUBTITULO_GEMINI_V0: str = "Asistencia con IA disponible en la entrega final"
DESCRIPCION_GEMINI_V0: str = (
    "En la versión final, podrás consultar orientación técnica sobre productos, "
    "recomendaciones de herramientas y asesoría para tus proyectos de hogar, obra y taller."
)
NOTA_ESTADO_GEMINI_V0: str = (
    "Funcionalidad informativa reservada en FerreteríaMS v0: actualmente no está habilitado "
    "el asistente conversacional ni se realizan consultas a modelos de inteligencia artificial."
)

# Mensajes diferenciados para los estados del inventario remoto (Sección 8.2 del Prompt 04)
MENSAJE_INVENTARIO_NO_INICIALIZADO: str = (
    "El inventario maestro todavía no ha sido inicializado en el repositorio oficial. "
    "La búsqueda estará disponible una vez que se inicialice el archivo maestro."
)
MENSAJE_ERROR_TECNICO_CONSULTA: str = (
    "No fue posible consultar el inventario en este momento debido a un problema técnico "
    "de conexión o acceso. Por favor, verifica la conexión e intenta nuevamente."
)
MENSAJE_INVENTARIO_REMOTO_INVALIDO: str = (
    "El archivo de inventario remoto presenta un formato inválido o inconsistencias de "
    "estructura y no puede procesarse correctamente."
)

# Claves de estado de sesión en Streamlit
CLAVE_TERMINO_BUSCADO = "ferms_termino_buscado"
CLAVE_PAGINA_ACTUAL = "ferms_pagina_actual"
CLAVE_RESPUESTA_BUSQUEDA = "ferms_respuesta_busqueda"
CLAVE_INVENTARIO_SESION = "ferms_inventario_vigente"
CLAVE_SHA_SESION = "ferms_sha_github_vigente"
CLAVE_PRODUCTO_SELECCIONADO = "ferms_producto_seleccionado_codigo"


class EstadoOperativoInterfaz(str, Enum):
    """Estados operativos diferenciables de la interfaz pública (Secciones 7 y 8.2 del Prompt 04)."""

    INICIAL = "INICIAL"
    BUSQUEDA_VACIA = "BUSQUEDA_VACIA"
    RESULTADOS_ENCONTRADOS = "RESULTADOS_ENCONTRADOS"
    SIN_COINCIDENCIAS = "SIN_COINCIDENCIAS"
    INVENTARIO_NO_INICIALIZADO = "INVENTARIO_NO_INICIALIZADO"
    ERROR_CONEXION_O_AUTORIZACION = "ERROR_CONEXION_O_AUTORIZACION"
    INVENTARIO_REMOTO_INVALIDO = "INVENTARIO_REMOTO_INVALIDO"


@dataclass(frozen=True)
class RespuestaInterfazBusqueda:
    """Resultado estructurado de la orquestación entre GitHub API y el motor de búsqueda."""

    estado_operativo: EstadoOperativoInterfaz
    categoria_consulta: CategoriaResultadoConsulta | None
    termino_busqueda: str
    mensaje_principal: str
    detalle_estado: str = ""
    resultado_busqueda: ResultadoBusquedaPaginada | None = None
    permite_reintentar: bool = False
    codigo_error_github: CodigoErrorGitHub | None = None
    sha_github: str | None = None
    inventario_vigente: InventarioDatos | None = None


DescargadorRemoto = Callable[..., ResultadoLecturaInventarioRemoto]


def inicializar_estado_sesion(
    estado: MutableMapping[str, Any] | None = None,
) -> MutableMapping[str, Any]:
    """Inicializa las claves necesarias en `st.session_state` (o un diccionario de prueba)."""
    destino: MutableMapping[str, Any] = estado if estado is not None else st.session_state
    valores_por_defecto: dict[str, Any] = {
        CLAVE_TERMINO_BUSCADO: "",
        CLAVE_PAGINA_ACTUAL: 1,
        CLAVE_RESPUESTA_BUSQUEDA: None,
        CLAVE_INVENTARIO_SESION: None,
        CLAVE_SHA_SESION: None,
        CLAVE_PRODUCTO_SELECCIONADO: None,
    }
    for clave, valor_defecto in valores_por_defecto.items():
        if clave not in destino:
            destino[clave] = valor_defecto
    return destino


def limpiar_resultados_previos_en_sesion(
    estado: MutableMapping[str, Any] | None = None,
) -> None:
    """Limpia resultados, término activo, paginación, selección e inventario previo en sesión (Sección 7.3)."""
    destino: MutableMapping[str, Any] = estado if estado is not None else st.session_state
    destino[CLAVE_TERMINO_BUSCADO] = ""
    destino[CLAVE_PAGINA_ACTUAL] = 1
    destino[CLAVE_RESPUESTA_BUSQUEDA] = None
    destino[CLAVE_INVENTARIO_SESION] = None
    destino[CLAVE_SHA_SESION] = None
    destino[CLAVE_PRODUCTO_SELECCIONADO] = None


def _es_misma_busqueda_activa(
    termino_anterior: str | None,
    termino_nuevo: str | None,
) -> bool:
    """Determina si dos términos corresponden a la misma búsqueda activa no vacía."""
    if es_termino_busqueda_vacio(termino_anterior) or es_termino_busqueda_vacio(
        termino_nuevo
    ):
        return False
    return normalizar_texto_busqueda(termino_anterior) == normalizar_texto_busqueda(
        termino_nuevo
    )


def preparar_seleccion_producto_para_detalle(
    codigo_producto: Any,
    estado: MutableMapping[str, Any] | None = None,
) -> None:
    """Registra en el estado de sesión el código del producto seleccionado (Sección 4 del Prompt 05)."""
    destino = inicializar_estado_sesion(estado)
    if codigo_producto is None:
        destino[CLAVE_PRODUCTO_SELECCIONADO] = None
    elif isinstance(codigo_producto, str):
        limpio = codigo_producto.strip()
        destino[CLAVE_PRODUCTO_SELECCIONADO] = limpio if limpio else None
    else:
        # Si se recibe un tipo no textual (p. ej. int), se conserva para que la validación lo rechace
        destino[CLAVE_PRODUCTO_SELECCIONADO] = codigo_producto


def obtener_detalle_producto_en_sesion(
    estado: MutableMapping[str, Any] | None = None,
) -> ResultadoConsultaDetalle:
    """Recupera el detalle y las ubicaciones del producto seleccionado usando el inventario validado en sesión.

    Cumple las Secciones 4.2, 4.4 y 8.4 del Prompt 05:
    - No realiza descargas nuevas desde GitHub al abrir o consultar el detalle.
    - Utiliza exclusivamente el inventario validado (`CLAVE_INVENTARIO_SESION`) de la búsqueda activa.
    - Verifica que el código seleccionado pertenezca a la consulta activa.
    """
    destino = inicializar_estado_sesion(estado)
    codigo_seleccionado = destino.get(CLAVE_PRODUCTO_SELECCIONADO)

    if codigo_seleccionado is None or (
        isinstance(codigo_seleccionado, str) and not codigo_seleccionado.strip()
    ):
        return ResultadoConsultaDetalle(
            estado=EstadoDetalleProducto.SIN_SELECCION,
            codigo_solicitado="",
            mensaje_usuario="",
        )

    inventario_sesion: InventarioDatos | None = destino.get(CLAVE_INVENTARIO_SESION)
    respuesta_busqueda: RespuestaInterfazBusqueda | None = destino.get(
        CLAVE_RESPUESTA_BUSQUEDA
    )

    resultados_activos = None
    if respuesta_busqueda is not None:
        if (
            respuesta_busqueda.estado_operativo
            != EstadoOperativoInterfaz.RESULTADOS_ENCONTRADOS
            or respuesta_busqueda.resultado_busqueda is None
        ):
            return ResultadoConsultaDetalle(
                estado=EstadoDetalleProducto.PRODUCTO_NO_DISPONIBLE,
                codigo_solicitado=str(codigo_seleccionado),
                mensaje_usuario=MENSAJE_PRODUCTO_SELECCIONADO_NO_DISPONIBLE,
            )
        resultados_activos = respuesta_busqueda.resultado_busqueda.todos_los_resultados

    return consultar_detalle_producto(
        inventario_sesion,
        codigo_seleccionado,
        resultados_activos=resultados_activos,
    )


def seleccionar_producto_en_sesion(
    codigo_producto: Any,
    estado: MutableMapping[str, Any] | None = None,
) -> ResultadoConsultaDetalle:
    """Selecciona un producto por su código exacto y devuelve su detalle desde el inventario en sesión."""
    destino = inicializar_estado_sesion(estado)
    preparar_seleccion_producto_para_detalle(codigo_producto, estado=destino)
    return obtener_detalle_producto_en_sesion(estado=destino)


def volver_a_resultados_en_sesion(
    estado: MutableMapping[str, Any] | None = None,
) -> None:
    """Cierra la vista de detalle y regresa a la lista de resultados conservando página y búsqueda activa."""
    destino = inicializar_estado_sesion(estado)
    destino[CLAVE_PRODUCTO_SELECCIONADO] = None


def procesar_consulta_busqueda_publica(
    termino_busqueda: str,
    *,
    pagina: int = 1,
    tamano_pagina: int = TAMANO_PAGINA_DEFECTO,
    termino_anterior: str | None = None,
    inventario_en_sesion: InventarioDatos | None = None,
    sha_en_sesion: str | None = None,
    forzar_recarga_remota: bool = True,
    config_github: ConfiguracionRepositorioGitHub = CONFIGURACION_POR_DEFECTO,
    descargador_remoto: DescargadorRemoto | None = None,
) -> RespuestaInterfazBusqueda:
    """Orquesta la validación de entrada, lectura vigente desde GitHub y búsqueda por nombre.

    Garantiza:
    - RF-037 / CA-041: Si el término está vacío, solicita introducir un nombre sin consultar GitHub.
    - RF-025 / RF-028: Cuando se ejecuta una búsqueda (`forzar_recarga_remota=True`), descarga la
      versión vigente confirmada en GitHub sin requerir reinicio manual de Streamlit.
    - Cuando el usuario navega entre páginas de una búsqueda activa (`forzar_recarga_remota=False`),
      reutiliza el inventario validado de esa consulta activa evitando llamadas HTTP innecesarias.
    - RF-038 / CA-042 y Sección 8.2: Distingue estrictamente entre inventario disponible,
      inventario no inicializado, error técnico de conexión/autorización e inventario remoto inválido.
    """
    lector_efectivo = descargador_remoto or github_inventario.descargar_inventario_remoto
    termino_str = "" if termino_busqueda is None else str(termino_busqueda)

    # 1. Manejo de búsqueda vacía sin realizar consultas de productos ni llamadas remotas
    if es_termino_busqueda_vacio(termino_str):
        resultado_vacio = ejecutar_busqueda_productos(
            None,
            termino_str,
            pagina=1,
            tamano_pagina=tamano_pagina,
        )
        return RespuestaInterfazBusqueda(
            estado_operativo=EstadoOperativoInterfaz.BUSQUEDA_VACIA,
            categoria_consulta=None,
            termino_busqueda=termino_str,
            mensaje_principal=MENSAJE_BUSQUEDA_VACIA,
            resultado_busqueda=resultado_vacio,
            permite_reintentar=False,
        )

    # 2. Resolver página (reinicia a 1 si el término cambió respecto a la búsqueda anterior)
    pagina_efectiva = resolver_pagina_busqueda(
        termino_anterior=termino_anterior,
        termino_nuevo=termino_str,
        pagina_solicitada=pagina,
    )

    # 3. Obtener inventario vigente desde GitHub (reutiliza solo al paginar la misma búsqueda válida)
    puede_reutilizar_inventario_sesion = (
        not forzar_recarga_remota
        and inventario_en_sesion is not None
        and _es_misma_busqueda_activa(termino_anterior, termino_str)
    )
    inventario_actual: InventarioDatos | None = (
        inventario_en_sesion if puede_reutilizar_inventario_sesion else None
    )
    sha_actual: str | None = (
        sha_en_sesion if puede_reutilizar_inventario_sesion else None
    )

    if inventario_actual is None:
        try:
            lectura_remota = lector_efectivo(config=config_github)
            inventario_actual = lectura_remota.inventario
            sha_actual = lectura_remota.sha_github
        except ErrorArchivoRemotoInexistente as exc_no_existe:
            return RespuestaInterfazBusqueda(
                estado_operativo=EstadoOperativoInterfaz.INVENTARIO_NO_INICIALIZADO,
                categoria_consulta=CategoriaResultadoConsulta.INVENTARIO_NO_INICIALIZADO,
                termino_busqueda=termino_str,
                mensaje_principal=MENSAJE_INVENTARIO_NO_INICIALIZADO,
                detalle_estado=ocultar_secretos_en_texto(exc_no_existe.mensaje),
                permite_reintentar=True,
                codigo_error_github=exc_no_existe.codigo,
            )
        except (ErrorArchivoExcelRemotoCorrupto, ErrorEsquemaInventarioRemoto) as exc_invalido:
            return RespuestaInterfazBusqueda(
                estado_operativo=EstadoOperativoInterfaz.INVENTARIO_REMOTO_INVALIDO,
                categoria_consulta=CategoriaResultadoConsulta.DATOS_REMOTOS_INVALIDOS,
                termino_busqueda=termino_str,
                mensaje_principal=MENSAJE_INVENTARIO_REMOTO_INVALIDO,
                detalle_estado=ocultar_secretos_en_texto(exc_invalido.mensaje),
                permite_reintentar=True,
                codigo_error_github=exc_invalido.codigo,
            )
        except ErrorLecturaGitHub as exc_github:
            return RespuestaInterfazBusqueda(
                estado_operativo=EstadoOperativoInterfaz.ERROR_CONEXION_O_AUTORIZACION,
                categoria_consulta=CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO,
                termino_busqueda=termino_str,
                mensaje_principal=MENSAJE_ERROR_TECNICO_CONSULTA,
                detalle_estado=ocultar_secretos_en_texto(exc_github.mensaje),
                permite_reintentar=True,
                codigo_error_github=exc_github.codigo,
            )
        except Exception as exc_general:
            return RespuestaInterfazBusqueda(
                estado_operativo=EstadoOperativoInterfaz.ERROR_CONEXION_O_AUTORIZACION,
                categoria_consulta=CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO,
                termino_busqueda=termino_str,
                mensaje_principal=MENSAJE_ERROR_TECNICO_CONSULTA,
                detalle_estado=ocultar_secretos_en_texto(str(exc_general)),
                permite_reintentar=True,
                codigo_error_github=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            )

    # 4. Ejecutar motor de búsqueda sobre el inventario validado
    resultado_paginado = ejecutar_busqueda_productos(
        inventario_actual,
        termino_str,
        pagina=pagina_efectiva,
        tamano_pagina=tamano_pagina,
    )

    if resultado_paginado.estado == EstadoBusqueda.SIN_RESULTADOS:
        return RespuestaInterfazBusqueda(
            estado_operativo=EstadoOperativoInterfaz.SIN_COINCIDENCIAS,
            categoria_consulta=CategoriaResultadoConsulta.PRODUCTO_NO_ENCONTRADO,
            termino_busqueda=termino_str,
            mensaje_principal=MENSAJE_PRODUCTO_NO_ENCONTRADO,
            resultado_busqueda=resultado_paginado,
            permite_reintentar=False,
            sha_github=sha_actual,
            inventario_vigente=inventario_actual,
        )

    return RespuestaInterfazBusqueda(
        estado_operativo=EstadoOperativoInterfaz.RESULTADOS_ENCONTRADOS,
        categoria_consulta=CategoriaResultadoConsulta.INVENTARIO_DISPONIBLE,
        termino_busqueda=termino_str,
        mensaje_principal=resultado_paginado.mensaje_usuario,
        resultado_busqueda=resultado_paginado,
        permite_reintentar=False,
        sha_github=sha_actual,
        inventario_vigente=inventario_actual,
    )


def ejecutar_flujo_busqueda_en_sesion(
    termino_busqueda: str,
    *,
    pagina: int = 1,
    forzar_recarga_remota: bool = True,
    estado: MutableMapping[str, Any] | None = None,
    descargador_remoto: DescargadorRemoto | None = None,
) -> RespuestaInterfazBusqueda:
    """Actualiza el estado de sesión ejecutando una búsqueda nueva o un cambio de página."""
    destino = inicializar_estado_sesion(estado)
    termino_anterior = destino.get(CLAVE_TERMINO_BUSCADO) or None
    inventario_previo = destino.get(CLAVE_INVENTARIO_SESION)
    sha_previo = destino.get(CLAVE_SHA_SESION)

    es_paginacion_busqueda_valida = (
        not forzar_recarga_remota
        and inventario_previo is not None
        and _es_misma_busqueda_activa(termino_anterior, termino_busqueda)
    )

    # Limpiar datos previos antes de iniciar una consulta nueva, vacía o con cambio de término (Sección 7.3)
    if not es_paginacion_busqueda_valida:
        limpiar_resultados_previos_en_sesion(destino)
        inventario_en_sesion = None
        sha_en_sesion = None
    else:
        destino[CLAVE_PRODUCTO_SELECCIONADO] = None
        inventario_en_sesion = inventario_previo
        sha_en_sesion = sha_previo

    respuesta = procesar_consulta_busqueda_publica(
        termino_busqueda,
        pagina=pagina,
        termino_anterior=termino_anterior,
        inventario_en_sesion=inventario_en_sesion,
        sha_en_sesion=sha_en_sesion,
        forzar_recarga_remota=not es_paginacion_busqueda_valida,
        descargador_remoto=descargador_remoto,
    )

    if (
        respuesta.estado_operativo
        in (
            EstadoOperativoInterfaz.RESULTADOS_ENCONTRADOS,
            EstadoOperativoInterfaz.SIN_COINCIDENCIAS,
        )
        and respuesta.inventario_vigente is not None
    ):
        destino[CLAVE_RESPUESTA_BUSQUEDA] = respuesta
        destino[CLAVE_TERMINO_BUSCADO] = termino_busqueda
        destino[CLAVE_PAGINA_ACTUAL] = (
            respuesta.resultado_busqueda.pagina_actual
            if respuesta.resultado_busqueda is not None
            else 1
        )
        destino[CLAVE_INVENTARIO_SESION] = respuesta.inventario_vigente
        destino[CLAVE_SHA_SESION] = respuesta.sha_github
    else:
        limpiar_resultados_previos_en_sesion(destino)
        destino[CLAVE_RESPUESTA_BUSQUEDA] = respuesta

    return respuesta


def _renderizar_tarjeta_producto(producto: ProductoCoincidente) -> None:
    """Presenta en la lista un producto coincidente con su Código, Nombre, Categoría y botón de detalle."""
    with st.container(border=True):
        col_principal, col_codigo, col_accion = st.columns([3, 1.2, 1.4])
        with col_principal:
            st.markdown(f"**{producto.nombre}**")
            etiqueta_categoria = (
                producto.nombre_categoria
                if producto.nombre_categoria
                else producto.categoria_id
            )
            st.caption(f"Categoría: {etiqueta_categoria}")
        with col_codigo:
            st.markdown(f"`Código: {producto.codigo_producto}`")
        with col_accion:
            if st.button(
                TEXTO_BOTON_VER_DETALLE,
                key=f"btn_ver_detalle_{producto.codigo_producto}",
                use_container_width=True,
            ):
                seleccionar_producto_en_sesion(producto.codigo_producto)
                st.rerun()


def _renderizar_bloque_ubicacion(
    ubicacion: UbicacionFisicaDetalle,
    *,
    etiqueta_encabezado: str | None = None,
    destacar_principal: bool = False,
) -> None:
    """Presenta Rack, Columna, Nivel y Posición de una ubicación física (Secciones 6 y 7 del Prompt 05)."""
    with st.container(border=True):
        if etiqueta_encabezado:
            st.markdown(f"**{etiqueta_encabezado}**")

        cadena_ubicacion = formatear_cadena_ubicacion(ubicacion)
        if destacar_principal:
            st.success(f"📍 **{cadena_ubicacion}**")
        else:
            st.markdown(f"🔹 **{cadena_ubicacion}**")

        col_rack, col_columna, col_nivel, col_posicion = st.columns(4)
        with col_rack:
            st.caption("Rack")
            st.markdown(f"**{ubicacion.rack}**")
        with col_columna:
            st.caption("Columna")
            st.markdown(f"**{ubicacion.columna}**")
        with col_nivel:
            st.caption("Nivel")
            st.markdown(f"**{ubicacion.nivel}**")
        with col_posicion:
            st.caption("Posición")
            st.markdown(f"**{ubicacion.posicion}**")


def _renderizar_vista_detalle_producto(
    resultado_detalle: ResultadoConsultaDetalle,
    respuesta_busqueda: RespuestaInterfazBusqueda | None = None,
) -> None:
    """Presenta la vista detallada de un producto seleccionado y sus ubicaciones físicas (Secciones 5, 6, 7 y 9)."""
    col_volver, col_contexto = st.columns([1.5, 3.5])
    with col_volver:
        if st.button(
            TEXTO_BOTON_VOLVER_RESULTADOS,
            key="btn_volver_resultados",
            use_container_width=True,
        ):
            volver_a_resultados_en_sesion()
            st.rerun()
    with col_contexto:
        if (
            respuesta_busqueda is not None
            and respuesta_busqueda.resultado_busqueda is not None
        ):
            res_pag = respuesta_busqueda.resultado_busqueda
            st.caption(
                f"Búsqueda activa: «{respuesta_busqueda.termino_busqueda.strip()}» · "
                f"Página {res_pag.pagina_actual} de {res_pag.total_paginas}"
            )

    if resultado_detalle.estado == EstadoDetalleProducto.PRODUCTO_NO_DISPONIBLE:
        st.warning(resultado_detalle.mensaje_usuario)
        return

    if resultado_detalle.estado == EstadoDetalleProducto.ERROR_INTEGRIDAD_UBICACION:
        st.error(resultado_detalle.mensaje_usuario)
        if resultado_detalle.detalle_error:
            st.caption(resultado_detalle.detalle_error)
        return

    if not resultado_detalle.tiene_detalle or resultado_detalle.detalle is None:
        st.warning(MENSAJE_PRODUCTO_SELECCIONADO_NO_DISPONIBLE)
        return

    detalle: DetalleProductoLocalizado = resultado_detalle.detalle

    # 1. Datos generales del producto (Sección 5 — RF-005)
    with st.container(border=True):
        st.subheader(f"📋 {TITULO_SECCION_DETALLE_PRODUCTO}")
        st.markdown(f"### {detalle.nombre}")
        col_cod, col_cat = st.columns(2)
        with col_cod:
            st.markdown(f"**Código del producto:** `{detalle.codigo_producto}`")
        with col_cat:
            st.markdown(f"**Categoría:** {detalle.nombre_categoria}")
        st.markdown(f"**Descripción:** {detalle.descripcion_presentacion}")

    # 2. Ubicación principal destacada (Sección 6 — RF-006)
    with st.container(border=True):
        st.subheader(f"📍 {TITULO_SECCION_UBICACION_PRINCIPAL}")
        _renderizar_bloque_ubicacion(
            detalle.ubicacion_principal,
            destacar_principal=True,
        )

    # 3. Ubicaciones secundarias diferenciadas (Sección 7 — RF-007 / CA-005)
    with st.container(border=True):
        st.subheader(f"🗂️ {TITULO_SECCION_UBICACIONES_SECUNDARIAS}")
        if detalle.tiene_ubicaciones_secundarias:
            st.caption(
                f"Se registran {len(detalle.ubicaciones_secundarias)} ubicación(es) "
                f"secundaria(s) adicional(es) para este producto:"
            )
            for indice, ubic_sec in enumerate(detalle.ubicaciones_secundarias, start=1):
                _renderizar_bloque_ubicacion(
                    ubic_sec,
                    etiqueta_encabezado=f"Ubicación secundaria {indice}",
                    destacar_principal=False,
                )
        else:
            st.caption(MENSAJE_SIN_UBICACIONES_SECUNDARIAS)


def _renderizar_controles_paginacion(
    resultado: ResultadoBusquedaPaginada,
    termino_activo: str,
    descargador_remoto: DescargadorRemoto | None = None,
) -> None:
    """Muestra los controles de paginación únicamente cuando existen más de diez resultados (Sección 6.6)."""
    if not resultado.requiere_paginacion:
        return

    col_ant, col_info, col_sig = st.columns([1, 2, 1])
    with col_ant:
        if st.button(
            "⬅️ Anterior",
            key="btn_pagina_anterior",
            disabled=not resultado.tiene_pagina_anterior,
            use_container_width=True,
        ):
            ejecutar_flujo_busqueda_en_sesion(
                termino_activo,
                pagina=resultado.pagina_actual - 1,
                forzar_recarga_remota=False,
                descargador_remoto=descargador_remoto,
            )
            st.rerun()

    with col_info:
        st.markdown(
            f"<div style='text-align: center; padding-top: 0.4rem;'>"
            f"<strong>Página {resultado.pagina_actual} de {resultado.total_paginas}</strong> "
            f"(mostrando {resultado.indice_inicio_mostrado}–{resultado.indice_fin_mostrado} "
            f"de {resultado.total_resultados})"
            f"</div>",
            unsafe_allow_html=True,
        )

    with col_sig:
        if st.button(
            "Siguiente ➡️",
            key="btn_pagina_siguiente",
            disabled=not resultado.tiene_pagina_siguiente,
            use_container_width=True,
        ):
            ejecutar_flujo_busqueda_en_sesion(
                termino_activo,
                pagina=resultado.pagina_actual + 1,
                forzar_recarga_remota=False,
                descargador_remoto=descargador_remoto,
            )
            st.rerun()


def cargar_estilos_locales(ruta_css: Path = RUTA_ARCHIVO_ESTILOS_CSS) -> str:
    """Lee el archivo CSS local justificado para el diseño responsive y accesible (Sección 7.4)."""
    if not ruta_css.is_file():
        return ""
    return ruta_css.read_text(encoding="utf-8")


def _aplicar_estilos_locales() -> None:
    """Inyecta las reglas CSS locales de adaptación responsive en la página Streamlit."""
    contenido_css = cargar_estilos_locales()
    if contenido_css:
        st.markdown(f"<style>\n{contenido_css}\n</style>", unsafe_allow_html=True)


def _renderizar_banner_encabezado() -> None:
    """Presenta la identidad visual de FerreteríaMS conforme al boceto conceptual de v0 (Sección 5.2)."""
    st.title(f"{ICONO_PAGINA} {TITULO}")
    st.caption(DESCRIPCION)
    st.markdown(
        f"""
        <div class="ferms-banner-encabezado" role="region" aria-label="Presentación de FerreteríaMS">
            <div class="ferms-banner-principal">
                <span class="ferms-etiqueta-superior">{ETIQUETA_BANNER_SUPERIOR}</span>
                <p class="ferms-marca-subtitulo">
                    Localiza productos por su nombre y consulta su ubicación física exacta
                    (<strong>Rack</strong>, <strong>Columna</strong>, <strong>Nivel</strong> y <strong>Posición</strong>)
                    dentro de la ferretería desde tu computadora, tableta o teléfono.
                </p>
            </div>
            <div class="ferms-banner-pilares" aria-label="Características del servicio de consulta">
                <span class="ferms-pilar-item">🛠️ Todo para tus proyectos</span>
                <span class="ferms-pilar-item">📍 Ubicación física en tienda</span>
                <span class="ferms-pilar-item">🏠 Hogar, obra y taller</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _renderizar_estado_inicial() -> None:
    """Presenta el estado inicial antes de realizar cualquier búsqueda (Sección 7.2 e imagen conceptual)."""
    with st.container(border=True):
        st.markdown("### 📦 Busca un producto")
        st.write(MENSAJE_INICIAL_BUSQUEDA)
        st.caption(TEXTO_AYUDA_EJEMPLOS)


def _renderizar_seccion_gemini_proximamente() -> None:
    """Presenta el área visual reservada para el Asistente Gemini en v0 (Sección 6, RF-032..RF-034, CA-031..CA-033).

    Garantiza:
    - Identificación clara como «Asistente Gemini» y estado «Próximamente».
    - Información descriptiva estática sobre su futuro propósito en la entrega final.
    - Ausencia total de cuadros de chat, botones engañosos, clientes de IA o llamadas a Gemini API.
    """
    with st.container(border=True):
        st.subheader(f"✨ {TITULO_SECCION_GEMINI}")
        st.markdown(f"**Estado:** `{ESTADO_GEMINI_PROXIMAMENTE}`")
        st.markdown(
            f"""
            <div class="ferms-gemini-panel" role="region" aria-label="{TITULO_SECCION_GEMINI} — {ESTADO_GEMINI_PROXIMAMENTE}">
                <div class="ferms-gemini-cabecera">
                    <span class="ferms-gemini-titulo">✨ {TITULO_SECCION_GEMINI}</span>
                    <span class="ferms-gemini-badge">{ESTADO_GEMINI_PROXIMAMENTE}</span>
                </div>
                <div class="ferms-gemini-icono" aria-hidden="true">🤖</div>
                <p class="ferms-gemini-subtitulo">{SUBTITULO_GEMINI_V0}</p>
                <p class="ferms-gemini-descripcion">{DESCRIPCION_GEMINI_V0}</p>
                <div class="ferms-gemini-nota-estado">{NOTA_ESTADO_GEMINI_V0}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            "Próximamente en la entrega final · Sin chat activo en FerreteríaMS v0."
        )


def _renderizar_area_inventario(
    descargador_remoto: DescargadorRemoto | None = None,
) -> None:
    """Renderiza el área principal de búsqueda pública, resultados paginados, detalles y ubicaciones."""
    # Sección pública de búsqueda exclusivamente por nombre de producto (RF-001, CA-043)
    st.subheader(f"🔍 {TITULO_SECCION_BUSQUEDA}")
    st.write(f"{MENSAJE_INICIAL_BUSQUEDA}.")

    col_input, col_boton = st.columns([4, 1])
    with col_input:
        termino_input = st.text_input(
            label=MENSAJE_INICIAL_BUSQUEDA,
            placeholder=PLACEHOLDER_CAMPO_BUSQUEDA,
            key="campo_nombre_producto",
            label_visibility="collapsed",
        )
    with col_boton:
        buscar_presionado = st.button(
            "🔍 Buscar",
            key="btn_ejecutar_busqueda",
            type="primary",
            use_container_width=True,
        )

    if buscar_presionado:
        limpiar_resultados_previos_en_sesion()
        with st.spinner(MENSAJE_BUSCANDO_PRODUCTOS):
            ejecutar_flujo_busqueda_en_sesion(
                termino_input,
                pagina=1,
                forzar_recarga_remota=True,
                descargador_remoto=descargador_remoto,
            )

    respuesta_actual: RespuestaInterfazBusqueda | None = st.session_state.get(
        CLAVE_RESPUESTA_BUSQUEDA
    )
    termino_buscado_activo: str = st.session_state.get(CLAVE_TERMINO_BUSCADO, "")
    termino_referencia_consulta: str = (
        termino_buscado_activo
        if termino_buscado_activo
        else (
            respuesta_actual.termino_busqueda if respuesta_actual is not None else ""
        )
    )

    # Sección 7.3: No mostrar resultados anteriores si el usuario cambió el texto y aún no presionó Buscar
    termino_modificado_pendiente = (
        not buscar_presionado
        and respuesta_actual is not None
        and respuesta_actual.estado_operativo != EstadoOperativoInterfaz.BUSQUEDA_VACIA
        and normalizar_texto_busqueda(termino_input)
        != normalizar_texto_busqueda(termino_referencia_consulta)
    )

    if respuesta_actual is None:
        _renderizar_estado_inicial()
    elif termino_modificado_pendiente:
        st.info(MENSAJE_CAMBIO_TERMINO_PENDIENTE)
    elif respuesta_actual.estado_operativo == EstadoOperativoInterfaz.BUSQUEDA_VACIA:
        st.warning(respuesta_actual.mensaje_principal)
    elif respuesta_actual.estado_operativo == EstadoOperativoInterfaz.SIN_COINCIDENCIAS:
        st.info(MENSAJE_PRODUCTO_NO_ENCONTRADO)
    elif respuesta_actual.estado_operativo == EstadoOperativoInterfaz.INVENTARIO_NO_INICIALIZADO:
        st.warning(respuesta_actual.mensaje_principal)
        if respuesta_actual.detalle_estado:
            st.caption(respuesta_actual.detalle_estado)
        if st.button("🔄 Reintentar consulta", key="btn_reintentar_no_inicializado"):
            termino_reintento = termino_input or termino_referencia_consulta
            limpiar_resultados_previos_en_sesion()
            with st.spinner(MENSAJE_BUSCANDO_PRODUCTOS):
                ejecutar_flujo_busqueda_en_sesion(
                    termino_reintento,
                    pagina=1,
                    forzar_recarga_remota=True,
                    descargador_remoto=descargador_remoto,
                )
            st.rerun()
    elif respuesta_actual.estado_operativo == EstadoOperativoInterfaz.INVENTARIO_REMOTO_INVALIDO:
        st.error(respuesta_actual.mensaje_principal)
        if respuesta_actual.detalle_estado:
            st.caption(respuesta_actual.detalle_estado)
        if st.button("🔄 Reintentar consulta", key="btn_reintentar_invalido"):
            termino_reintento = termino_input or termino_referencia_consulta
            limpiar_resultados_previos_en_sesion()
            with st.spinner(MENSAJE_BUSCANDO_PRODUCTOS):
                ejecutar_flujo_busqueda_en_sesion(
                    termino_reintento,
                    pagina=1,
                    forzar_recarga_remota=True,
                    descargador_remoto=descargador_remoto,
                )
            st.rerun()
    elif respuesta_actual.estado_operativo == EstadoOperativoInterfaz.ERROR_CONEXION_O_AUTORIZACION:
        st.error(respuesta_actual.mensaje_principal)
        if respuesta_actual.detalle_estado:
            st.caption(respuesta_actual.detalle_estado)
        if st.button("🔄 Reintentar consulta", key="btn_reintentar_error_tecnico"):
            termino_reintento = termino_input or termino_referencia_consulta
            limpiar_resultados_previos_en_sesion()
            with st.spinner(MENSAJE_BUSCANDO_PRODUCTOS):
                ejecutar_flujo_busqueda_en_sesion(
                    termino_reintento,
                    pagina=1,
                    forzar_recarga_remota=True,
                    descargador_remoto=descargador_remoto,
                )
            st.rerun()
    elif (
        respuesta_actual.estado_operativo == EstadoOperativoInterfaz.RESULTADOS_ENCONTRADOS
        and respuesta_actual.resultado_busqueda is not None
    ):
        codigo_seleccionado = st.session_state.get(CLAVE_PRODUCTO_SELECCIONADO)
        if codigo_seleccionado is not None and (
            not isinstance(codigo_seleccionado, str) or codigo_seleccionado.strip()
        ):
            resultado_detalle = obtener_detalle_producto_en_sesion()
            _renderizar_vista_detalle_producto(
                resultado_detalle,
                respuesta_busqueda=respuesta_actual,
            )
        else:
            resultado = respuesta_actual.resultado_busqueda
            st.success(
                f"Mostrando {resultado.indice_inicio_mostrado}–{resultado.indice_fin_mostrado} "
                f"de {resultado.total_resultados} producto(s) coincidente(s) para "
                f"«{respuesta_actual.termino_busqueda.strip()}»."
            )
            for producto in resultado.resultados_pagina:
                _renderizar_tarjeta_producto(producto)

            _renderizar_controles_paginacion(
                resultado=resultado,
                termino_activo=respuesta_actual.termino_busqueda,
                descargador_remoto=descargador_remoto,
            )

    st.divider()
    st.info(f"ℹ️ {AVISO_ACCESO_PUBLICO}")


def renderizar_aplicacion(
    descargador_remoto: DescargadorRemoto | None = None,
) -> None:
    """Construye y renderiza la interfaz pública responsive de FerreteríaMS v0 en Streamlit.

    Distribución responsive (Sección 7 del Prompt 06):
    - Escritorio: Dos áreas diferenciadas en paralelo (`col_inventario` a la izquierda y `col_gemini` a la derecha).
    - Tableta y teléfono: Apilamiento vertical automático (1. Encabezado FerreteríaMS, 2. Buscador,
      3. Resultados o detalles, 4. Área Gemini «Próximamente») sin desplazamiento horizontal.
    """
    st.set_page_config(
        page_title=TITULO,
        page_icon=ICONO_PAGINA,
        layout="wide",
    )
    _aplicar_estilos_locales()
    inicializar_estado_sesion()

    # 1. Encabezado e identidad visual de FerreteríaMS (Secciones 5.1 y 5.2)
    _renderizar_banner_encabezado()

    # 2. Composición responsive: Inventario a la izquierda y Gemini «Próximamente» a la derecha (Sección 7)
    col_inventario, col_gemini = st.columns([2.35, 1], gap="large")
    with col_inventario:
        _renderizar_area_inventario(descargador_remoto=descargador_remoto)
    with col_gemini:
        _renderizar_seccion_gemini_proximamente()


if __name__ == "__main__":
    renderizar_aplicacion()
