"""Interfaz pública de búsqueda de productos de FerreteríaMS v0.

Proyecto: FerreteríaMS v0
Tarea: FERMS-V0-P04
Requisitos relacionados: RF-001, RF-002, RF-003, RF-004, RF-008, RF-009, RF-024, RF-025,
RF-028, RF-035, RF-036, RF-037, RF-038.
Criterios relacionados: CA-001, CA-002, CA-003, CA-004, CA-006, CA-007, CA-039, CA-040,
CA-041, CA-042, CA-043.

Adaptación de la plantilla académica a FerreteríaMS v0:
- Conserva la estructura de inicialización de Streamlit (`st.set_page_config`, `st.title`,
  `st.caption`), el uso estructurado de `st.session_state` y el manejo explícito de errores.
- Retira por completo las importaciones y llamadas al cliente de inteligencia artificial,
  la exigencia de clave de API para el asistente y la interfaz de chat operativa.
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
    MENSAJE_INICIAL_BUSQUEDA,
    MENSAJE_PRODUCTO_NO_ENCONTRADO,
    TAMANO_PAGINA_DEFECTO,
    EstadoBusqueda,
    ProductoCoincidente,
    ResultadoBusquedaPaginada,
    ejecutar_busqueda_productos,
    es_termino_busqueda_vacio,
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
    codigo_producto: str | None,
    estado: MutableMapping[str, Any] | None = None,
) -> None:
    """Punto de extensión preparado para integrar la selección y detalle en el Prompt 05 (Sección 7.4)."""
    destino: MutableMapping[str, Any] = estado if estado is not None else st.session_state
    destino[CLAVE_PRODUCTO_SELECCIONADO] = (
        str(codigo_producto).strip() if codigo_producto else None
    )


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
    """Presenta en la lista un producto coincidente con su Código, Nombre y Categoría (Sección 7.4)."""
    with st.container(border=True):
        col_principal, col_codigo = st.columns([3, 1])
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


def _renderizar_estado_inicial() -> None:
    """Presenta el estado inicial antes de realizar cualquier búsqueda (Sección 7.2 e imagen conceptual)."""
    with st.container(border=True):
        st.markdown("### 📦 Busca un producto")
        st.write(MENSAJE_INICIAL_BUSQUEDA)
        st.caption(TEXTO_AYUDA_EJEMPLOS)


def renderizar_aplicacion(
    descargador_remoto: DescargadorRemoto | None = None,
) -> None:
    """Construye y renderiza la interfaz pública principal de FerreteríaMS v0 en Streamlit."""
    st.set_page_config(
        page_title=TITULO,
        page_icon=ICONO_PAGINA,
        layout="wide",
    )
    inicializar_estado_sesion()

    # Encabezado principal conforme a la imagen conceptual de inicio v0 (Sección 7.1)
    st.title(f"{ICONO_PAGINA} {TITULO}")
    st.caption(DESCRIPCION)
    st.divider()

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


if __name__ == "__main__":
    renderizar_aplicacion()
