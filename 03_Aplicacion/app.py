"""Interfaz pública responsive, sección visual Gemini («Próximamente»), seguridad administrativa y gestión local de productos y ubicaciones de FerreteríaMS v0.

Proyecto: FerreteríaMS v0
Tareas: FERMS-V0-P04, FERMS-V0-P05, FERMS-V0-P06, FERMS-V0-P07, FERMS-V0-P08, FERMS-V0-P09
Requisitos relacionados: RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007, RF-008,
RF-009, RF-010, RF-011, RF-012, RF-013, RF-014, RF-015, RF-016, RF-017, RF-018, RF-019,
RF-020, RF-021, RF-022, RF-023, RF-024, RF-025, RF-027 (preparación SHA), RF-028, RF-032,
RF-033, RF-034, RF-035, RF-036, RF-037, RF-038, Sección 5.3 y Sección 6.3.
Criterios relacionados: CA-001, CA-002, CA-003, CA-004, CA-005, CA-006, CA-007, CA-008,
CA-009, CA-010, CA-011, CA-012 (local), CA-013 (local), CA-014, CA-015, CA-016, CA-017,
CA-018, CA-019, CA-022, CA-027, CA-028, CA-029, CA-030, CA-031, CA-032, CA-033, CA-034,
CA-039, CA-040, CA-041, CA-042, CA-043, CA-044, CA-045, CA-046, CA-047, CA-048, CA-049,
CA-050, CA-051 (local), CA-052, CA-053, CA-054, CA-055, CA-056, CA-057, CA-058, CA-059,
CA-060, CA-061.
"""

from __future__ import annotations

import html
import math
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping, MutableMapping, Sequence

import streamlit as st

_DIRECTORIO_ACTUAL = Path(__file__).resolve().parent
if str(_DIRECTORIO_ACTUAL) not in sys.path:
    sys.path.insert(0, str(_DIRECTORIO_ACTUAL))

import administracion_productos  # noqa: E402
import autenticacion  # noqa: E402
import github_inventario  # noqa: E402
from administracion_productos import (  # noqa: E402
    CLAVE_CATEGORIA_ADMIN_SELECCIONADA,
    CLAVE_ESPACIO_TRABAJO_ADMIN,
    CLAVE_FORMULARIO_BORRADOR_ADMIN,
    CLAVE_MENSAJE_OPERACION_ADMIN,
    CLAVE_MODO_VISTA_ADMIN,
    CLAVE_PRODUCTO_ADMIN_SELECCIONADO,
    CLAVE_RESULTADO_CARGA_ADMIN,
    CLAVE_TERMINO_FILTRO_ADMIN,
    CLAVE_UBICACION_ADMIN_SELECCIONADA,
    MENSAJE_CAMBIO_PRINCIPAL_LOCAL_EXITOSO,
    MENSAJE_CAMBIOS_LOCALES_DESCARTADOS,
    MENSAJE_CATALOGO_PREDEFINIDO_NO_EDITABLE,
    MENSAJE_CREACION_CATEGORIA_LOCAL_EXITOSA,
    MENSAJE_CREACION_LOCAL_EXITOSA,
    MENSAJE_CREACION_UBICACION_LOCAL_EXITOSA,
    MENSAJE_DATOS_REMOTOS_INVALIDOS_ADMIN,
    MENSAJE_DESACTIVACION_PRODUCTO_LOCAL_EXITOSA,
    MENSAJE_DESACTIVACION_UBICACION_LOCAL_EXITOSA,
    MENSAJE_EDICION_CATEGORIA_LOCAL_EXITOSA,
    MENSAJE_EDICION_LOCAL_EXITOSA,
    MENSAJE_EDICION_UBICACION_LOCAL_EXITOSA,
    MENSAJE_ELIMINACION_SECUNDARIA_LOCAL_EXITOSA,
    MENSAJE_ERROR_CONEXION_ADMIN,
    MENSAJE_INVENTARIO_DISPONIBLE_EDICION_LOCAL,
    MENSAJE_INVENTARIO_REMOTO_INEXISTENTE_ADMIN,
    MENSAJE_REACTIVACION_PRODUCTO_LOCAL_EXITOSA,
    AsignacionUbicacionEntrada,
    CodigoErrorAdministrativo,
    ErrorAdministracionInventario,
    ErrorValidacionAdministrativa,
    EspacioTrabajoAdminInventario,
    EstadoInventarioAdmin,
    ModoVistaAdmin,
    PaquetePublicacionPendienteP10,
    ResultadoCargaInventarioAdmin,
    ResultadoOperacionCategoriaAdmin,
    ResultadoOperacionProductoAdmin,
    ResultadoOperacionUbicacionAdmin,
    cambiar_estado_producto_local,
    cambiar_ubicacion_principal_local,
    cargar_inventario_administrativo_en_sesion,
    consultar_categoria_administrativa_por_id,
    consultar_categorias_administrativas,
    consultar_producto_administrativo_por_codigo,
    consultar_productos_administrativos,
    consultar_ubicacion_administrativa_por_id,
    consultar_ubicaciones_administrativas,
    contiene_datos_demostrativos,
    crear_categoria_local,
    crear_producto_local,
    crear_ubicacion_local,
    desactivar_producto_local,
    desactivar_ubicacion_local,
    descartar_cambios_locales_en_sesion,
    editar_categoria_local,
    editar_producto_local,
    editar_ubicacion_local,
    eliminar_asignacion_ubicacion_local,
    escapar_texto_presentacion_segura,
    guardar_borrador_formulario_admin,
    inicializar_espacio_trabajo_desde_inventario,
    limpiar_espacio_trabajo_admin_en_sesion,
    obtener_catalogo_categorias_admin,
    obtener_catalogo_ubicaciones_admin,
    preparar_paquete_publicacion_futura_p10,
    reactivar_producto_local,
    rechazar_modificacion_catalogo_predefinido,
    renombrar_categoria_local,
    restaurar_borrador_en_espacio_trabajo_admin,
)
from autenticacion import (  # noqa: E402
    CLAVE_BORRADOR_RESTAURADO_ADMIN,
    CLAVE_CONTEXTO_DISPOSITIVO,
    CLAVE_MENSAJE_AUTH_ADMIN,
    CLAVE_MOTIVO_FIN_SESION_ADMIN,
    CLAVE_SESION_ADMIN,
    CLAVE_VINCULO_BORRADOR_SESION,
    MENSAJE_ACCESO_NO_AUTORIZADO,
    MENSAJE_ADMIN_CONFIGURACION_INVALIDA,
    MENSAJE_ADMIN_NO_CONFIGURADO,
    MENSAJE_AUTENTICACION_EXITOSA,
    MENSAJE_BORRADOR_DESCARTADO,
    MENSAJE_BORRADOR_RESTAURADO,
    MENSAJE_BORRADOR_RETENIDO_REAUTENTICACION,
    MENSAJE_CREDENCIALES_INCOMPLETAS,
    MENSAJE_CREDENCIALES_INVALIDAS,
    MENSAJE_RESTRICCION_MOVIL_ADMIN,
    MENSAJE_SESION_CERRADA,
    MENSAJE_SESION_EXPIRADA_INACTIVIDAD,
    MENSAJE_SESION_RENOVADA,
    TEXTO_BOTON_CONTINUAR_SESION,
    BorradorTemporalAdmin,
    CodigoResultadoAutenticacion,
    ContextoDispositivo,
    ErrorAutorizacionAdmin,
    EstadoBloqueoAdmin,
    EstadoConfiguracionAdmin,
    EstadoSesionAdmin,
    EstadoTiempoSesionAdmin,
    ProveedorReloj,
    ResultadoAutenticacion,
    cerrar_sesion_admin,
    consultar_estado_bloqueo_admin,
    consultar_estado_sesion_admin,
    descartar_borrador_admin,
    detectar_contexto_dispositivo,
    esta_autenticado_en_sesion,
    guardar_borrador_admin,
    iniciar_sesion_admin,
    obtener_borrador_admin,
    obtener_configuracion_admin,
    obtener_usuario_autenticado,
    ocultar_secretos_autenticacion,
    renovar_sesion_admin,
    requerir_autorizacion_admin,
    restaurar_borrador_admin,
    tiene_borrador_pendiente_en_sesion,
    verificar_configuracion_admin,
)
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
    EjecutorHTTP,
    ErrorArchivoExcelRemotoCorrupto,
    ErrorArchivoRemotoInexistente,
    ErrorEsquemaInventarioRemoto,
    ErrorLecturaGitHub,
    ResultadoLecturaInventarioRemoto,
    ocultar_secretos_en_texto,
)
from inventario import InventarioDatos  # noqa: E402
import asistente_gemini  # noqa: E402
from asistente_gemini import (  # noqa: E402
    AVISO_PERMANENTE_IA_GEMINI,
    CLAVE_CAMBIO_PRODUCTO_PENDIENTE_GEMINI,
    CLAVE_CONTADOR_USO_GEMINI,
    CLAVE_HISTORIAL_CHAT_GEMINI,
    CLAVE_IDIOMA_PREFERIDO_GEMINI,
    CLAVE_PRODUCTO_ANTERIOR_GEMINI,
    CLAVE_PRODUCTO_CONTEXTO_GEMINI,
    CLAVE_ULTIMA_PREGUNTA_FALLIDA_GEMINI,
    CLAVE_ULTIMO_ERROR_GEMINI,
    CLAVE_ULTIMO_RESULTADO_GEMINI,
    CONFIGURACION_LIMITES_DEFECTO,
    LONGITUD_MAXIMA_PREGUNTA_CARACTERES_DEFECTO,
    MAX_CONSULTAS_POR_VENTANA_DEFECTO,
    MAX_MENSAJES_HISTORIAL_CONTEXTO_DEFECTO,
    MENSAJE_NUEVA_CONVERSACION_GEMINI,
    MODELO_GEMINI_DEFECTO,
    PLACEHOLDER_PREGUNTA_GEMINI,
    TEXTO_BOTON_ENVIAR_PREGUNTA_GEMINI,
    TEXTO_BOTON_NUEVA_CONVERSACION_GEMINI,
    TEXTO_BOTON_REINTENTAR_GEMINI,
    ClienteGeneradorGemini,
    CodigoErrorGemini,
    ConfiguracionLimitesGemini,
    ErrorAsistenteGemini,
    EstadoRespuestaGemini,
    EstadoUsoSesionGemini,
    IdiomaAsistente,
    MensajeChatGemini,
    ProductoContextoGemini,
    ResultadoConsultaGemini,
    SolicitudModeloGemini,
    inicializar_estado_gemini_en_sesion,
    iniciar_nueva_conversacion_gemini,
    obtener_categoria_tecnica_error_gemini,
    obtener_clave_api_gemini,
    obtener_estado_uso_gemini_en_sesion,
    obtener_historial_chat_gemini,
    obtener_producto_activo_seleccionado_contexto,
    obtener_productos_relevantes_para_consulta,
    ocultar_secretos_gemini,
    procesar_consulta_gemini_en_sesion,
    reintentar_ultima_consulta_gemini_en_sesion,
    sincronizar_producto_seleccionado_gemini,
    verificar_condiciones_capa_gratuita,
)
import persistencia_github  # noqa: E402
from persistencia_github import (  # noqa: E402
    CLAVE_CONFIRMACION_GUARDADO_GITHUB,
    CLAVE_CONFLICTO_SHA_ADMIN,
    CLAVE_HUELLA_ULTIMA_PUBLICACION_ADMIN,
    CLAVE_ULTIMA_PUBLICACION_GITHUB_ADMIN,
    MENSAJE_ARCHIVO_REMOTO_YA_EXISTE,
    MENSAJE_CONFIRMACION_EXPLICITA_REQUERIDA,
    MENSAJE_CONFIRMACION_RECARGA_CONFLICTO_REQUERIDA,
    MENSAJE_CONFLICTO_SHA_DETECTADO,
    MENSAJE_DATOS_DEMOSTRATIVOS_NO_PUBLICABLES,
    MENSAJE_INICIALIZACION_OFICIAL_NO_AUTORIZADA,
    MENSAJE_PUBLICACION_ACTUALIZACION_EXITOSA,
    MENSAJE_PUBLICACION_DUPLICADA_BLOQUEADA,
    MENSAJE_PUBLICACION_INICIALIZACION_EXITOSA,
    MENSAJE_RECARGA_REMOTA_TRAS_CONFLICTO_EXITOSA,
    MENSAJE_SIN_CAMBIOS_PENDIENTES,
    CodigoErrorPersistenciaGitHub,
    ConsultorExistenciaRemota,
    EjecutorHTTPPut,
    ErrorConflictoVersionShaGitHub,
    ErrorPersistenciaGitHub,
    ErrorPublicacionDatosDemostrativosNoAutorizada,
    EstadoConflictoShaAdmin,
    EstadoResultadoPublicacionGitHub,
    ModoPublicacionGitHub,
    PaqueteExcelVerificado,
    ResultadoPublicacionGitHub,
    SolicitudPutContentsGitHub,
    construir_solicitud_put_contents_github,
    publicar_cambios_administrativos_github,
    recargar_inventario_remoto_tras_conflicto,
    serializar_y_verificar_inventario_xlsx,
)

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

# Constantes de navegación y sección administrativa (Prompts 07, 08 y 09)
TEXTO_BOTON_NAV_INICIO: str = "🏠 Inicio"
TEXTO_BOTON_NAV_PRODUCTOS: str = "📦 Productos"
TITULO_SECCION_ADMIN_LOGIN: str = "Acceso de administración"
SUBTITULO_SECCION_ADMIN_LOGIN: str = (
    "Ingresa con tu usuario y contraseña para acceder al panel administrativo de Productos."
)
TITULO_SECCION_PRODUCTOS_ADMIN: str = "Productos — Panel administrativo"
TEXTO_BOTON_LOGIN_ADMIN: str = "🔐 Iniciar sesión"
TEXTO_BOTON_LOGOUT_ADMIN: str = "🚪 Cerrar sesión (Logout)"
TEXTO_BOTON_VOLVER_SITIO: str = "🏠 Volver al buscador público"
TEXTO_BOTON_RESTAURAR_BORRADOR: str = "📥 Restaurar borrador temporal"
TEXTO_BOTON_DESCARTAR_BORRADOR: str = "🗑️ Descartar borrador temporal"
TEXTO_BOTON_ADMIN_CARGAR_INVENTARIO: str = "📥 Cargar / recargar inventario"
TEXTO_BOTON_ADMIN_ABRIR_CONSULTA: str = "📋 Consultar inventario"
TEXTO_BOTON_ADMIN_ABRIR_CREAR: str = "➕ Crear producto"
TEXTO_BOTON_ADMIN_ABRIR_EDITAR: str = "✏️ Editar producto y ubicaciones"
TEXTO_BOTON_ADMIN_ABRIR_CATEGORIAS: str = "🗂️ Administrar categorías"
TEXTO_BOTON_ADMIN_ABRIR_UBICACIONES: str = "📍 Administrar ubicaciones"
TEXTO_BOTON_ADMIN_DESCARTAR_CAMBIOS: str = "↩️ Descartar cambios locales"
TEXTO_BOTON_ADMIN_CONFIRMAR_CREAR: str = "✅ Validar y registrar en copia local"
TEXTO_BOTON_ADMIN_CONFIRMAR_EDITAR: str = "💾 Validar y aplicar cambios en copia local"
TEXTO_BOTON_ADMIN_CONFIRMAR_CREAR_CATEGORIA: str = "✅ Crear categoría en copia local"
TEXTO_BOTON_ADMIN_CONFIRMAR_RENOMBRAR_CATEGORIA: str = "💾 Renombrar categoría en copia local"
TEXTO_BOTON_ADMIN_CONFIRMAR_CREAR_UBICACION: str = "✅ Crear ubicación física en copia local"
TEXTO_BOTON_ADMIN_CONFIRMAR_EDITAR_UBICACION: str = "💾 Guardar cambios de ubicación física"
TEXTO_BOTON_ADMIN_DESACTIVAR_UBICACION: str = "🚫 Desactivar ubicación física"
TEXTO_BOTON_ADMIN_GUARDAR_BORRADOR_FORM: str = "📝 Guardar borrador de formulario"
TEXTO_BOTON_ADMIN_PUBLICAR_GITHUB: str = "☁️ Guardar y publicar cambios en GitHub"
TEXTO_BOTON_ADMIN_INICIALIZAR_GITHUB: str = "☁️ Inicializar inventario maestro en GitHub"
TEXTO_CHECKBOX_ADMIN_CONFIRMAR_PUBLICACION: str = (
    "Confirmo explícitamente publicar y versionar estos cambios en GitHub (rama main)"
)
TEXTO_BOTON_ADMIN_RECARGAR_TRAS_CONFLICTO: str = (
    "🔄 Recargar versión remota vigente desde GitHub"
)
TEXTO_CHECKBOX_ADMIN_CONFIRMAR_RECARGA_CONFLICTO: str = (
    "Confirmo recargar la versión remota vigente reemplazando los cambios locales en conflicto"
)
MENSAJE_MANTENIMIENTO_PENDIENTE_P09: str = (
    "Las funciones operativas de mantenimiento del inventario (registro, edición de productos "
    "y asignación de ubicaciones físicas) se implementarán en etapas posteriores autorizadas."
)
NOTA_CONTROLES_SESION_PENDIENTES_P08: str = (
    "Nota de seguridad activa (Prompts 07 y 08): verificación por hash Argon2id, límite de "
    "5 intentos fallidos con bloqueos progresivos (5, 10, 20 y 30 min), expiración tras "
    "15 minutos de inactividad, aviso previo 2 minutos antes (minuto 13), renovación mediante "
    "«Continuar sesión» y retención temporal de borradores por 15 minutos adicionales."
)
AVISO_PERSISTENCIA_REMOTA_PENDIENTE_P10: str = (
    "Edición local temporal activa (Prompt 09): las altas y modificaciones validadas se mantienen "
    "en la copia de trabajo de esta sesión. La escritura remota en GitHub se habilitará en el Prompt 10."
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
CLAVE_SECCION_ACTIVA = "ferms_seccion_activa"


class SeccionInterfaz(str, Enum):
    """Secciones principales de navegación de FerreteríaMS v0 (Inicio público y Productos administrativo)."""

    INICIO = "INICIO"
    PRODUCTOS = "PRODUCTOS"


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
        CLAVE_SECCION_ACTIVA: SeccionInterfaz.INICIO.value,
        CLAVE_SESION_ADMIN: None,
        CLAVE_MENSAJE_AUTH_ADMIN: None,
        CLAVE_VINCULO_BORRADOR_SESION: None,
        CLAVE_BORRADOR_RESTAURADO_ADMIN: None,
        CLAVE_MOTIVO_FIN_SESION_ADMIN: None,
        CLAVE_ESPACIO_TRABAJO_ADMIN: None,
        CLAVE_RESULTADO_CARGA_ADMIN: None,
        CLAVE_MODO_VISTA_ADMIN: ModoVistaAdmin.INICIAL.value,
        CLAVE_PRODUCTO_ADMIN_SELECCIONADO: None,
        CLAVE_CATEGORIA_ADMIN_SELECCIONADA: None,
        CLAVE_UBICACION_ADMIN_SELECCIONADA: None,
        CLAVE_TERMINO_FILTRO_ADMIN: "",
        CLAVE_MENSAJE_OPERACION_ADMIN: None,
        CLAVE_FORMULARIO_BORRADOR_ADMIN: None,
        CLAVE_CONFIRMACION_GUARDADO_GITHUB: False,
        CLAVE_CONFLICTO_SHA_ADMIN: None,
        CLAVE_ULTIMA_PUBLICACION_GITHUB_ADMIN: None,
        CLAVE_HUELLA_ULTIMA_PUBLICACION_ADMIN: None,
    }
    for clave, valor_defecto in valores_por_defecto.items():
        if clave not in destino:
            destino[clave] = valor_defecto
    inicializar_estado_gemini_en_sesion(destino)
    return destino


def seleccionar_seccion_interfaz(
    seccion: SeccionInterfaz | str,
    estado: MutableMapping[str, Any] | None = None,
) -> SeccionInterfaz:
    """Cambia la sección activa de la interfaz entre `INICIO` (público) y `PRODUCTOS` (administración)."""
    destino = inicializar_estado_sesion(estado)
    if isinstance(seccion, SeccionInterfaz):
        seccion_enum = seccion
    elif isinstance(seccion, str) and seccion.strip().upper() == SeccionInterfaz.PRODUCTOS.value:
        seccion_enum = SeccionInterfaz.PRODUCTOS
    else:
        seccion_enum = SeccionInterfaz.INICIO

    destino[CLAVE_SECCION_ACTIVA] = seccion_enum.value
    return seccion_enum


def obtener_seccion_activa(
    estado: Mapping[str, Any] | None = None,
) -> SeccionInterfaz:
    """Devuelve la sección activa actual en el estado de sesión (`INICIO` por defecto)."""
    origen: Mapping[str, Any] = estado if estado is not None else st.session_state
    valor = origen.get(CLAVE_SECCION_ACTIVA, SeccionInterfaz.INICIO.value)
    if isinstance(valor, SeccionInterfaz):
        return valor
    if isinstance(valor, str) and valor.strip().upper() == SeccionInterfaz.PRODUCTOS.value:
        return SeccionInterfaz.PRODUCTOS
    return SeccionInterfaz.INICIO


def ejecutar_login_administrativo_en_sesion(
    usuario: Any,
    contrasena: Any,
    *,
    estado: MutableMapping[str, Any] | None = None,
    fuente_entorno: Mapping[str, Any] | None = None,
    fuente_secretos: Mapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoAutenticacion:
    """Ejecuta el inicio de sesión administrativo delegando en `autenticacion.py` y actualiza el estado."""
    destino = inicializar_estado_sesion(estado)
    resultado = iniciar_sesion_admin(
        usuario=usuario,
        contrasena=contrasena,
        estado=destino,
        fuente_entorno=fuente_entorno,
        fuente_secretos=fuente_secretos,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
    )
    destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
        "tipo": "success" if resultado.autenticado else "error",
        "codigo": resultado.codigo.value,
        "mensaje": resultado.mensaje_usuario,
    }
    return resultado


def ejecutar_renovacion_sesion_en_sesion(
    estado: MutableMapping[str, Any] | None = None,
    *,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> EstadoSesionAdmin | None:
    """Renueva explícitamente una sesión administrativa activa mediante «Continuar sesión» (Sección 8)."""
    destino = inicializar_estado_sesion(estado)
    try:
        sesion_renovada = renovar_sesion_admin(
            destino,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "success",
            "codigo": "SESION_RENOVADA",
            "mensaje": MENSAJE_SESION_RENOVADA,
        }
        return sesion_renovada
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "warning"
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return None


def ejecutar_restauracion_borrador_en_sesion(
    estado: MutableMapping[str, Any] | None = None,
    *,
    inventario_base: InventarioDatos | None = None,
    sha_base_remoto: str | None = None,
    eliminar_tras_restaurar: bool = False,
    config_github: ConfiguracionRepositorioGitHub | None = CONFIGURACION_POR_DEFECTO,
    descargador_remoto: DescargadorRemoto | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> BorradorTemporalAdmin | None:
    """Restaura un borrador temporal en la sesión autenticada actual y reaplica sus cambios validados."""
    destino = inicializar_estado_sesion(estado)
    config_efectiva = (
        config_github if config_github is not None else CONFIGURACION_POR_DEFECTO
    )
    try:
        borrador = restaurar_borrador_en_espacio_trabajo_admin(
            destino,
            inventario_base=inventario_base,
            sha_base_remoto=sha_base_remoto,
            eliminar_tras_restaurar=eliminar_tras_restaurar,
            config_github=config_efectiva,
            descargador_remoto=descargador_remoto,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        if borrador is not None:
            if destino.get(CLAVE_ESPACIO_TRABAJO_ADMIN) is not None:
                destino[CLAVE_RESULTADO_CARGA_ADMIN] = None
                modo_restaurado: str | None = None
                if isinstance(borrador.datos, Mapping):
                    form_activo = borrador.datos.get("formulario_activo")
                    if isinstance(form_activo, Mapping):
                        modo_candidato = (
                            str(form_activo.get("modo_formulario", "")).strip().upper()
                        )
                        if modo_candidato in {
                            ModoVistaAdmin.CONSULTA.value,
                            ModoVistaAdmin.CREAR_PRODUCTO.value,
                            ModoVistaAdmin.EDITAR_PRODUCTO.value,
                            ModoVistaAdmin.CATEGORIAS.value,
                            ModoVistaAdmin.UBICACIONES.value,
                        }:
                            modo_restaurado = modo_candidato
                        campos_form = form_activo.get("campos")
                        if isinstance(campos_form, Mapping):
                            cod_form = str(
                                campos_form.get("codigo_producto", "")
                            ).strip()
                            if cod_form:
                                destino[CLAVE_PRODUCTO_ADMIN_SELECCIONADO] = cod_form
                            cat_form = str(
                                campos_form.get("categoria_id", "")
                            ).strip()
                            if cat_form:
                                destino[CLAVE_CATEGORIA_ADMIN_SELECCIONADA] = cat_form
                            ubic_form = str(
                                campos_form.get("ubicacion_id", "")
                            ).strip()
                            if ubic_form:
                                destino[CLAVE_UBICACION_ADMIN_SELECCIONADA] = ubic_form
                if modo_restaurado is not None:
                    destino[CLAVE_MODO_VISTA_ADMIN] = modo_restaurado
                else:
                    destino[CLAVE_MODO_VISTA_ADMIN] = ModoVistaAdmin.CONSULTA.value
            destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
                "tipo": "success",
                "codigo": "BORRADOR_RESTAURADO",
                "mensaje": MENSAJE_BORRADOR_RESTAURADO,
            }
        return borrador
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return None
    except ErrorAdministracionInventario as exc_admin:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": exc_admin.codigo.value,
            "mensaje": exc_admin.mensaje,
        }
        return None


def ejecutar_descarte_borrador_en_sesion(
    estado: MutableMapping[str, Any] | None = None,
    *,
    reloj: ProveedorReloj | None = None,
) -> bool:
    """Descarta y elimina de forma segura el borrador temporal asociado a la sesión."""
    destino = inicializar_estado_sesion(estado)
    eliminado = descartar_borrador_admin(destino, reloj=reloj)
    destino[CLAVE_FORMULARIO_BORRADOR_ADMIN] = None
    if eliminado:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "info",
            "codigo": "BORRADOR_DESCARTADO",
            "mensaje": MENSAJE_BORRADOR_DESCARTADO,
        }
    return eliminado


def ejecutar_logout_administrativo_en_sesion(
    estado: MutableMapping[str, Any] | None = None,
    *,
    reloj: ProveedorReloj | None = None,
) -> None:
    """Cierra la sesión administrativa actual, revoca el acceso y elimina borradores y espacios temporales."""
    destino = inicializar_estado_sesion(estado)
    cerrar_sesion_admin(destino, conservar_borrador_temporal=False, reloj=reloj)
    limpiar_espacio_trabajo_admin_en_sesion(destino)
    destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
        "tipo": "info",
        "codigo": "SESION_CERRADA",
        "mensaje": MENSAJE_SESION_CERRADA,
    }


def seleccionar_modo_vista_admin_en_sesion(
    modo: ModoVistaAdmin | str,
    estado: MutableMapping[str, Any] | None = None,
    *,
    codigo_producto_editar: str | None = None,
    categoria_id_editar: str | None = None,
    ubicacion_id_editar: str | None = None,
) -> ModoVistaAdmin:
    """Cambia la subvista activa dentro del panel administrativo de Productos."""
    destino = inicializar_estado_sesion(estado)
    if isinstance(modo, ModoVistaAdmin):
        modo_enum = modo
    elif isinstance(modo, str):
        valor_limpio = modo.strip().upper()
        try:
            modo_enum = ModoVistaAdmin(valor_limpio)
        except ValueError:
            modo_enum = ModoVistaAdmin.CONSULTA
    else:
        modo_enum = ModoVistaAdmin.CONSULTA

    destino[CLAVE_MODO_VISTA_ADMIN] = modo_enum.value
    if codigo_producto_editar is not None and isinstance(codigo_producto_editar, str):
        destino[CLAVE_PRODUCTO_ADMIN_SELECCIONADO] = codigo_producto_editar.strip() or None
    if categoria_id_editar is not None and isinstance(categoria_id_editar, str):
        destino[CLAVE_CATEGORIA_ADMIN_SELECCIONADA] = categoria_id_editar.strip() or None
    if ubicacion_id_editar is not None and isinstance(ubicacion_id_editar, str):
        destino[CLAVE_UBICACION_ADMIN_SELECCIONADA] = ubicacion_id_editar.strip() or None
    return modo_enum


def ejecutar_carga_inventario_admin_en_sesion(
    estado: MutableMapping[str, Any] | None = None,
    *,
    inicializar_demo_si_no_existe: bool = False,
    descargador_remoto: DescargadorRemoto | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoCargaInventarioAdmin | None:
    """Carga el inventario remoto para edición administrativa local o prepara copia demostrativa en memoria."""
    destino = inicializar_estado_sesion(estado)
    try:
        resultado = cargar_inventario_administrativo_en_sesion(
            destino,
            descargador_remoto=descargador_remoto,
            inicializar_demo_si_no_existe=inicializar_demo_si_no_existe,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        if resultado.espacio_trabajo is not None and (
            destino.get(CLAVE_MODO_VISTA_ADMIN) == ModoVistaAdmin.INICIAL.value
        ):
            destino[CLAVE_MODO_VISTA_ADMIN] = ModoVistaAdmin.CONSULTA.value
        return resultado
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return None


def ejecutar_creacion_producto_en_sesion(
    *,
    codigo_producto: Any,
    nombre: Any,
    categoria_id: Any,
    descripcion: Any = "",
    ubicaciones_ids: Sequence[Any] | None = None,
    ubicacion_principal_id: Any = None,
    asignaciones: Sequence[Mapping[str, Any] | AsignacionUbicacionEntrada] | None = None,
    estado: MutableMapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoOperacionProductoAdmin:
    """Ejecuta y valida el alta local de un producto actualizando el aviso administrativo en sesión."""
    destino = inicializar_estado_sesion(estado)
    try:
        res = crear_producto_local(
            destino,
            codigo_producto=codigo_producto,
            nombre=nombre,
            categoria_id=categoria_id,
            descripcion=descripcion,
            ubicaciones_ids=ubicaciones_ids,
            ubicacion_principal_id=ubicacion_principal_id,
            asignaciones=asignaciones,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "success",
            "codigo": res.estado.value,
            "mensaje": res.mensaje_usuario,
        }
        destino[CLAVE_PRODUCTO_ADMIN_SELECCIONADO] = res.codigo_producto
        return res
    except ErrorAdministracionInventario as exc_admin:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": exc_admin.codigo.value,
            "mensaje": exc_admin.mensaje,
        }
        return ResultadoOperacionProductoAdmin(
            exito=False,
            estado=exc_admin.estado,
            mensaje_usuario=exc_admin.mensaje,
            codigo_error=exc_admin.codigo,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return ResultadoOperacionProductoAdmin(
            exito=False,
            estado=EstadoInventarioAdmin.SESION_ADMINISTRATIVA_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else EstadoInventarioAdmin.ERROR_VALIDACION_ADMINISTRATIVA,
            mensaje_usuario=exc_auth.mensaje,
            codigo_error=CodigoErrorAdministrativo.SESION_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else CodigoErrorAdministrativo.AUTORIZACION_INVALIDA,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )


def ejecutar_edicion_producto_en_sesion(
    *,
    codigo_producto: Any,
    nuevo_codigo_producto: Any = None,
    nombre: Any = None,
    categoria_id: Any = None,
    descripcion: Any = None,
    ubicaciones_ids: Sequence[Any] | None = None,
    ubicacion_principal_id: Any = None,
    asignaciones: Sequence[Mapping[str, Any] | AsignacionUbicacionEntrada] | None = None,
    estado: MutableMapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoOperacionProductoAdmin:
    """Ejecuta y valida la edición local de un producto existente actualizando el aviso administrativo."""
    destino = inicializar_estado_sesion(estado)
    try:
        res = editar_producto_local(
            destino,
            codigo_producto=codigo_producto,
            nuevo_codigo_producto=nuevo_codigo_producto,
            nombre=nombre,
            categoria_id=categoria_id,
            descripcion=descripcion,
            ubicaciones_ids=ubicaciones_ids,
            ubicacion_principal_id=ubicacion_principal_id,
            asignaciones=asignaciones,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "success",
            "codigo": res.estado.value,
            "mensaje": res.mensaje_usuario,
        }
        return res
    except ErrorAdministracionInventario as exc_admin:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": exc_admin.codigo.value,
            "mensaje": exc_admin.mensaje,
        }
        return ResultadoOperacionProductoAdmin(
            exito=False,
            estado=exc_admin.estado,
            mensaje_usuario=exc_admin.mensaje,
            codigo_error=exc_admin.codigo,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return ResultadoOperacionProductoAdmin(
            exito=False,
            estado=EstadoInventarioAdmin.SESION_ADMINISTRATIVA_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else EstadoInventarioAdmin.ERROR_VALIDACION_ADMINISTRATIVA,
            mensaje_usuario=exc_auth.mensaje,
            codigo_error=CodigoErrorAdministrativo.SESION_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else CodigoErrorAdministrativo.AUTORIZACION_INVALIDA,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )


def ejecutar_cambio_ubicacion_principal_en_sesion(
    *,
    codigo_producto: Any,
    nueva_ubicacion_principal_id: Any,
    incluir_si_no_estaba_asignada: bool = False,
    estado: MutableMapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoOperacionProductoAdmin:
    """Cambia localmente la ubicación principal de un producto asegurando exactamente una principal."""
    destino = inicializar_estado_sesion(estado)
    try:
        res = cambiar_ubicacion_principal_local(
            destino,
            codigo_producto=codigo_producto,
            nueva_ubicacion_principal_id=nueva_ubicacion_principal_id,
            incluir_si_no_estaba_asignada=incluir_si_no_estaba_asignada,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "success",
            "codigo": res.estado.value,
            "mensaje": res.mensaje_usuario,
        }
        return res
    except ErrorAdministracionInventario as exc_admin:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": exc_admin.codigo.value,
            "mensaje": exc_admin.mensaje,
        }
        return ResultadoOperacionProductoAdmin(
            exito=False,
            estado=exc_admin.estado,
            mensaje_usuario=exc_admin.mensaje,
            codigo_error=exc_admin.codigo,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return ResultadoOperacionProductoAdmin(
            exito=False,
            estado=EstadoInventarioAdmin.SESION_ADMINISTRATIVA_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else EstadoInventarioAdmin.ERROR_VALIDACION_ADMINISTRATIVA,
            mensaje_usuario=exc_auth.mensaje,
            codigo_error=CodigoErrorAdministrativo.SESION_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else CodigoErrorAdministrativo.AUTORIZACION_INVALIDA,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )


def ejecutar_eliminacion_ubicacion_secundaria_en_sesion(
    *,
    codigo_producto: Any,
    ubicacion_id: Any,
    estado: MutableMapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoOperacionProductoAdmin:
    """Retira localmente una ubicación secundaria asignada a un producto validando la integridad."""
    destino = inicializar_estado_sesion(estado)
    try:
        res = eliminar_asignacion_ubicacion_local(
            destino,
            codigo_producto=codigo_producto,
            ubicacion_id=ubicacion_id,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "success",
            "codigo": res.estado.value,
            "mensaje": res.mensaje_usuario,
        }
        return res
    except ErrorAdministracionInventario as exc_admin:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": exc_admin.codigo.value,
            "mensaje": exc_admin.mensaje,
        }
        return ResultadoOperacionProductoAdmin(
            exito=False,
            estado=exc_admin.estado,
            mensaje_usuario=exc_admin.mensaje,
            codigo_error=exc_admin.codigo,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return ResultadoOperacionProductoAdmin(
            exito=False,
            estado=EstadoInventarioAdmin.SESION_ADMINISTRATIVA_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else EstadoInventarioAdmin.ERROR_VALIDACION_ADMINISTRATIVA,
            mensaje_usuario=exc_auth.mensaje,
            codigo_error=CodigoErrorAdministrativo.SESION_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else CodigoErrorAdministrativo.AUTORIZACION_INVALIDA,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )


def ejecutar_creacion_categoria_en_sesion(
    *,
    categoria_id: Any,
    nombre_categoria: Any,
    estado: MutableMapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoOperacionCategoriaAdmin:
    """Ejecuta y valida el alta local de una categoría actualizando el aviso administrativo en sesión."""
    destino = inicializar_estado_sesion(estado)
    try:
        res = crear_categoria_local(
            destino,
            categoria_id=categoria_id,
            nombre_categoria=nombre_categoria,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "success",
            "codigo": res.estado.value,
            "mensaje": res.mensaje_usuario,
        }
        destino[CLAVE_CATEGORIA_ADMIN_SELECCIONADA] = res.categoria_id
        return res
    except ErrorAdministracionInventario as exc_admin:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": exc_admin.codigo.value,
            "mensaje": exc_admin.mensaje,
        }
        return ResultadoOperacionCategoriaAdmin(
            exito=False,
            estado=exc_admin.estado,
            mensaje_usuario=exc_admin.mensaje,
            codigo_error=exc_admin.codigo,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return ResultadoOperacionCategoriaAdmin(
            exito=False,
            estado=EstadoInventarioAdmin.SESION_ADMINISTRATIVA_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else EstadoInventarioAdmin.ERROR_VALIDACION_ADMINISTRATIVA,
            mensaje_usuario=exc_auth.mensaje,
            codigo_error=CodigoErrorAdministrativo.SESION_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else CodigoErrorAdministrativo.AUTORIZACION_INVALIDA,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )


def ejecutar_renombrado_categoria_en_sesion(
    *,
    categoria_id: Any,
    nuevo_nombre_categoria: Any = None,
    nombre_categoria: Any = None,
    nuevo_categoria_id: Any = None,
    estado: MutableMapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoOperacionCategoriaAdmin:
    """Ejecuta y valida el renombrado local de una categoría manteniendo `Categoria_ID` inmutable."""
    destino = inicializar_estado_sesion(estado)
    try:
        res = renombrar_categoria_local(
            destino,
            categoria_id=categoria_id,
            nuevo_nombre_categoria=nuevo_nombre_categoria,
            nombre_categoria=nombre_categoria,
            nuevo_categoria_id=nuevo_categoria_id,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "success",
            "codigo": res.estado.value,
            "mensaje": res.mensaje_usuario,
        }
        destino[CLAVE_CATEGORIA_ADMIN_SELECCIONADA] = res.categoria_id
        return res
    except ErrorAdministracionInventario as exc_admin:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": exc_admin.codigo.value,
            "mensaje": exc_admin.mensaje,
        }
        return ResultadoOperacionCategoriaAdmin(
            exito=False,
            estado=exc_admin.estado,
            mensaje_usuario=exc_admin.mensaje,
            codigo_error=exc_admin.codigo,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return ResultadoOperacionCategoriaAdmin(
            exito=False,
            estado=EstadoInventarioAdmin.SESION_ADMINISTRATIVA_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else EstadoInventarioAdmin.ERROR_VALIDACION_ADMINISTRATIVA,
            mensaje_usuario=exc_auth.mensaje,
            codigo_error=CodigoErrorAdministrativo.SESION_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else CodigoErrorAdministrativo.AUTORIZACION_INVALIDA,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )


ejecutar_edicion_categoria_en_sesion = ejecutar_renombrado_categoria_en_sesion


def ejecutar_creacion_ubicacion_en_sesion(
    *,
    ubicacion_id: Any,
    rack: Any,
    columna: Any,
    nivel: Any,
    posicion: Any,
    estado: MutableMapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoOperacionUbicacionAdmin:
    """Ejecuta y valida el alta local de una ubicación física actualizando el aviso administrativo."""
    destino = inicializar_estado_sesion(estado)
    try:
        res = crear_ubicacion_local(
            destino,
            ubicacion_id=ubicacion_id,
            rack=rack,
            columna=columna,
            nivel=nivel,
            posicion=posicion,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "success",
            "codigo": res.estado.value,
            "mensaje": res.mensaje_usuario,
        }
        destino[CLAVE_UBICACION_ADMIN_SELECCIONADA] = res.ubicacion_id
        return res
    except ErrorAdministracionInventario as exc_admin:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": exc_admin.codigo.value,
            "mensaje": exc_admin.mensaje,
        }
        return ResultadoOperacionUbicacionAdmin(
            exito=False,
            estado=exc_admin.estado,
            mensaje_usuario=exc_admin.mensaje,
            codigo_error=exc_admin.codigo,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return ResultadoOperacionUbicacionAdmin(
            exito=False,
            estado=EstadoInventarioAdmin.SESION_ADMINISTRATIVA_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else EstadoInventarioAdmin.ERROR_VALIDACION_ADMINISTRATIVA,
            mensaje_usuario=exc_auth.mensaje,
            codigo_error=CodigoErrorAdministrativo.SESION_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else CodigoErrorAdministrativo.AUTORIZACION_INVALIDA,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )


def ejecutar_edicion_ubicacion_en_sesion(
    *,
    ubicacion_id: Any,
    rack: Any = None,
    columna: Any = None,
    nivel: Any = None,
    posicion: Any = None,
    nuevo_ubicacion_id: Any = None,
    estado: MutableMapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoOperacionUbicacionAdmin:
    """Ejecuta y valida la edición local de coordenadas físicas cuando la ubicación no tiene productos."""
    destino = inicializar_estado_sesion(estado)
    try:
        res = editar_ubicacion_local(
            destino,
            ubicacion_id=ubicacion_id,
            rack=rack,
            columna=columna,
            nivel=nivel,
            posicion=posicion,
            nuevo_ubicacion_id=nuevo_ubicacion_id,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "success",
            "codigo": res.estado.value,
            "mensaje": res.mensaje_usuario,
        }
        destino[CLAVE_UBICACION_ADMIN_SELECCIONADA] = res.ubicacion_id
        return res
    except ErrorAdministracionInventario as exc_admin:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": exc_admin.codigo.value,
            "mensaje": exc_admin.mensaje,
        }
        return ResultadoOperacionUbicacionAdmin(
            exito=False,
            estado=exc_admin.estado,
            mensaje_usuario=exc_admin.mensaje,
            codigo_error=exc_admin.codigo,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return ResultadoOperacionUbicacionAdmin(
            exito=False,
            estado=EstadoInventarioAdmin.SESION_ADMINISTRATIVA_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else EstadoInventarioAdmin.ERROR_VALIDACION_ADMINISTRATIVA,
            mensaje_usuario=exc_auth.mensaje,
            codigo_error=CodigoErrorAdministrativo.SESION_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else CodigoErrorAdministrativo.AUTORIZACION_INVALIDA,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )


def ejecutar_desactivacion_ubicacion_en_sesion(
    *,
    ubicacion_id: Any,
    estado: MutableMapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoOperacionUbicacionAdmin:
    """Desactiva localmente una ubicación física sin productos asociados (`Activo = 'No'`)."""
    destino = inicializar_estado_sesion(estado)
    try:
        res = desactivar_ubicacion_local(
            destino,
            ubicacion_id=ubicacion_id,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "success",
            "codigo": res.estado.value,
            "mensaje": res.mensaje_usuario,
        }
        destino[CLAVE_UBICACION_ADMIN_SELECCIONADA] = res.ubicacion_id
        return res
    except ErrorAdministracionInventario as exc_admin:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": exc_admin.codigo.value,
            "mensaje": exc_admin.mensaje,
        }
        return ResultadoOperacionUbicacionAdmin(
            exito=False,
            estado=exc_admin.estado,
            mensaje_usuario=exc_admin.mensaje,
            codigo_error=exc_admin.codigo,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return ResultadoOperacionUbicacionAdmin(
            exito=False,
            estado=EstadoInventarioAdmin.SESION_ADMINISTRATIVA_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else EstadoInventarioAdmin.ERROR_VALIDACION_ADMINISTRATIVA,
            mensaje_usuario=exc_auth.mensaje,
            codigo_error=CodigoErrorAdministrativo.SESION_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else CodigoErrorAdministrativo.AUTORIZACION_INVALIDA,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )


def ejecutar_desactivacion_producto_en_sesion(
    *,
    codigo_producto: Any,
    confirmado: bool = True,
    estado: MutableMapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoOperacionProductoAdmin:
    """Desactiva localmente un producto (`Activo = 'No'`) conservando sus datos y asignaciones."""
    destino = inicializar_estado_sesion(estado)
    try:
        res = desactivar_producto_local(
            destino,
            codigo_producto=codigo_producto,
            confirmado=confirmado,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "success",
            "codigo": res.estado.value,
            "mensaje": res.mensaje_usuario,
        }
        destino[CLAVE_PRODUCTO_ADMIN_SELECCIONADO] = res.codigo_producto
        return res
    except ErrorAdministracionInventario as exc_admin:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": exc_admin.codigo.value,
            "mensaje": exc_admin.mensaje,
        }
        return ResultadoOperacionProductoAdmin(
            exito=False,
            estado=exc_admin.estado,
            mensaje_usuario=exc_admin.mensaje,
            codigo_error=exc_admin.codigo,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return ResultadoOperacionProductoAdmin(
            exito=False,
            estado=EstadoInventarioAdmin.SESION_ADMINISTRATIVA_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else EstadoInventarioAdmin.ERROR_VALIDACION_ADMINISTRATIVA,
            mensaje_usuario=exc_auth.mensaje,
            codigo_error=CodigoErrorAdministrativo.SESION_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else CodigoErrorAdministrativo.AUTORIZACION_INVALIDA,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )


def ejecutar_reactivacion_producto_en_sesion(
    *,
    codigo_producto: Any,
    confirmado: bool = True,
    estado: MutableMapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoOperacionProductoAdmin:
    """Reactiva localmente un producto (`Activo = 'Sí'`) validando su integridad."""
    destino = inicializar_estado_sesion(estado)
    try:
        res = reactivar_producto_local(
            destino,
            codigo_producto=codigo_producto,
            confirmado=confirmado,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "success",
            "codigo": res.estado.value,
            "mensaje": res.mensaje_usuario,
        }
        destino[CLAVE_PRODUCTO_ADMIN_SELECCIONADO] = res.codigo_producto
        return res
    except ErrorAdministracionInventario as exc_admin:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": exc_admin.codigo.value,
            "mensaje": exc_admin.mensaje,
        }
        return ResultadoOperacionProductoAdmin(
            exito=False,
            estado=exc_admin.estado,
            mensaje_usuario=exc_admin.mensaje,
            codigo_error=exc_admin.codigo,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return ResultadoOperacionProductoAdmin(
            exito=False,
            estado=EstadoInventarioAdmin.SESION_ADMINISTRATIVA_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else EstadoInventarioAdmin.ERROR_VALIDACION_ADMINISTRATIVA,
            mensaje_usuario=exc_auth.mensaje,
            codigo_error=CodigoErrorAdministrativo.SESION_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else CodigoErrorAdministrativo.AUTORIZACION_INVALIDA,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )


def ejecutar_cambio_estado_producto_en_sesion(
    *,
    codigo_producto: Any,
    activo: Any,
    confirmado: bool = True,
    estado: MutableMapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoOperacionProductoAdmin:
    """Cambia el estado lógico ('Sí'/'No') de un producto en la sesión administrativa."""
    destino = inicializar_estado_sesion(estado)
    try:
        res = cambiar_estado_producto_local(
            destino,
            codigo_producto=codigo_producto,
            activo=activo,
            confirmado=confirmado,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "success",
            "codigo": res.estado.value,
            "mensaje": res.mensaje_usuario,
        }
        destino[CLAVE_PRODUCTO_ADMIN_SELECCIONADO] = res.codigo_producto
        return res
    except ErrorAdministracionInventario as exc_admin:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": exc_admin.codigo.value,
            "mensaje": exc_admin.mensaje,
        }
        return ResultadoOperacionProductoAdmin(
            exito=False,
            estado=exc_admin.estado,
            mensaje_usuario=exc_admin.mensaje,
            codigo_error=exc_admin.codigo,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )
    except ErrorAutorizacionAdmin as exc_auth:
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return ResultadoOperacionProductoAdmin(
            exito=False,
            estado=EstadoInventarioAdmin.SESION_ADMINISTRATIVA_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else EstadoInventarioAdmin.ERROR_VALIDACION_ADMINISTRATIVA,
            mensaje_usuario=exc_auth.mensaje,
            codigo_error=CodigoErrorAdministrativo.SESION_EXPIRADA
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else CodigoErrorAdministrativo.AUTORIZACION_INVALIDA,
            confirmado_en_github=False,
            es_cambio_local_temporal=True,
        )


def ejecutar_descarte_cambios_locales_en_sesion(
    estado: MutableMapping[str, Any] | None = None,
    *,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> EspacioTrabajoAdminInventario | None:
    """Descarta todas las modificaciones locales no guardadas restaurando la copia original en memoria."""
    destino = inicializar_estado_sesion(estado)
    try:
        espacio = descartar_cambios_locales_en_sesion(
            destino,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "info",
            "codigo": "CAMBIOS_LOCALES_DESCARTADOS",
            "mensaje": MENSAJE_CAMBIOS_LOCALES_DESCARTADOS,
        }
        return espacio
    except (ErrorAdministracionInventario, ErrorAutorizacionAdmin) as exc:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": "ERROR_DESCARTE",
            "mensaje": str(exc),
        }
        return None


def ejecutar_publicacion_github_en_sesion(
    estado: MutableMapping[str, Any] | None = None,
    *,
    confirmacion_explicita: bool = False,
    modo_publicacion: ModoPublicacionGitHub | None = None,
    mensaje_commit: str | None = None,
    token: str | None = None,
    fuente_secretos: Mapping[str, Any] | None = None,
    fuente_entorno: Mapping[str, str] | None = None,
    config_github: ConfiguracionRepositorioGitHub = CONFIGURACION_POR_DEFECTO,
    ejecutor_http_get: EjecutorHTTP | None = None,
    ejecutor_http_put: EjecutorHTTPPut | None = None,
    consultor_existencia: ConsultorExistenciaRemota | None = None,
    lector_roundtrip: Callable[[bytes], InventarioDatos] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoPublicacionGitHub:
    """Orquesta el guardado administrativo y su confirmación en GitHub actualizando los avisos en sesión."""
    destino = inicializar_estado_sesion(estado)
    espacio_previo = destino.get(CLAVE_ESPACIO_TRABAJO_ADMIN)
    modo_inferido = (
        modo_publicacion
        if modo_publicacion is not None
        else (
            ModoPublicacionGitHub.ACTUALIZACION_ARCHIVO_EXISTENTE
            if isinstance(espacio_previo, EspacioTrabajoAdminInventario)
            and (
                espacio_previo.origen_remoto_confirmado
                or bool((espacio_previo.sha_base_remoto or "").strip())
            )
            else ModoPublicacionGitHub.CREACION_INICIAL_ARCHIVO_NUEVO
        )
    )
    try:
        resultado = publicar_cambios_administrativos_github(
            destino,
            confirmacion_explicita=confirmacion_explicita,
            modo_publicacion=modo_publicacion,
            mensaje_commit=mensaje_commit,
            token=token,
            fuente_secretos=fuente_secretos,
            fuente_entorno=fuente_entorno,
            config=config_github,
            ejecutor_http_get=ejecutor_http_get,
            ejecutor_http_put=ejecutor_http_put,
            consultor_existencia=consultor_existencia,
            lector_roundtrip=lector_roundtrip,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "success",
            "codigo": resultado.estado.value,
            "mensaje": resultado.mensaje_usuario,
        }
        return resultado
    except ErrorPersistenciaGitHub as exc_pers:
        tipo_aviso = (
            "warning"
            if exc_pers.codigo
            in (
                CodigoErrorPersistenciaGitHub.CONFIRMACION_EXPLICITA_REQUERIDA,
                CodigoErrorPersistenciaGitHub.SIN_CAMBIOS_PENDIENTES,
                CodigoErrorPersistenciaGitHub.OPERACION_DUPLICADA,
            )
            else "error"
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": tipo_aviso,
            "codigo": exc_pers.codigo.value,
            "mensaje": exc_pers.mensaje,
        }
        conflicto_actual = destino.get(CLAVE_CONFLICTO_SHA_ADMIN)
        return ResultadoPublicacionGitHub(
            exito=False,
            confirmado_en_github=False,
            estado=exc_pers.estado_publicacion,
            modo_publicacion=modo_inferido,
            mensaje_usuario=exc_pers.mensaje,
            detalle_tecnico=exc_pers.detalle_tecnico,
            codigo_error=exc_pers.codigo,
            sha_anterior=exc_pers.sha_base_local,
            conflicto_sha=conflicto_actual
            if isinstance(conflicto_actual, EstadoConflictoShaAdmin)
            else None,
            permite_reintentar=exc_pers.es_reintentable,
            permite_recargar_remoto=exc_pers.codigo
            in (
                CodigoErrorPersistenciaGitHub.CONFLICTO_SHA_REMOTO,
                CodigoErrorPersistenciaGitHub.ARCHIVO_REMOTO_YA_EXISTE,
            ),
            cambios_locales_preservados=True,
        )
    except ErrorAdministracionInventario as exc_admin:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": exc_admin.codigo.value,
            "mensaje": exc_admin.mensaje,
        }
        return ResultadoPublicacionGitHub(
            exito=False,
            confirmado_en_github=False,
            estado=EstadoResultadoPublicacionGitHub.ERROR_SERIALIZACION_O_VALIDACION,
            modo_publicacion=modo_inferido,
            mensaje_usuario=exc_admin.mensaje,
            codigo_error=CodigoErrorPersistenciaGitHub.SERIALIZACION_INVALIDA,
            cambios_locales_preservados=True,
        )
    except ErrorAutorizacionAdmin as exc_auth:
        if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA:
            destino[CLAVE_ESPACIO_TRABAJO_ADMIN] = None
            destino[CLAVE_RESULTADO_CARGA_ADMIN] = None
            destino[CLAVE_MODO_VISTA_ADMIN] = ModoVistaAdmin.INICIAL.value
        destino[CLAVE_MENSAJE_AUTH_ADMIN] = {
            "tipo": "warning"
            if exc_auth.codigo == CodigoResultadoAutenticacion.SESION_EXPIRADA
            else "error",
            "codigo": exc_auth.codigo.value,
            "mensaje": exc_auth.mensaje,
        }
        return ResultadoPublicacionGitHub(
            exito=False,
            confirmado_en_github=False,
            estado=EstadoResultadoPublicacionGitHub.ERROR_AUTORIZACION_ADMIN,
            modo_publicacion=modo_inferido,
            mensaje_usuario=exc_auth.mensaje,
            codigo_error=CodigoErrorPersistenciaGitHub.AUTORIZACION_ADMIN_INVALIDA,
            cambios_locales_preservados=True,
        )


def ejecutar_recarga_remota_tras_conflicto_en_sesion(
    estado: MutableMapping[str, Any] | None = None,
    *,
    confirmar_descarte_locales: bool = False,
    descargador_remoto: DescargadorRemoto | None = None,
    config_github: ConfiguracionRepositorioGitHub = CONFIGURACION_POR_DEFECTO,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
) -> ResultadoCargaInventarioAdmin | None:
    """Recarga la versión remota vigente tras un conflicto SHA, exigiendo confirmación explícita."""
    destino = inicializar_estado_sesion(estado)
    try:
        resultado = recargar_inventario_remoto_tras_conflicto(
            destino,
            confirmar_descarte_locales=confirmar_descarte_locales,
            descargador_remoto=descargador_remoto,
            config=config_github,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
        )
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "success",
            "codigo": "RECARGA_REMOTA_TRAS_CONFLICTO_EXITOSA",
            "mensaje": MENSAJE_RECARGA_REMOTA_TRAS_CONFLICTO_EXITOSA,
        }
        return resultado
    except ErrorPersistenciaGitHub as exc_pers:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "warning"
            if exc_pers.codigo
            == CodigoErrorPersistenciaGitHub.CONFIRMACION_EXPLICITA_REQUERIDA
            else "error",
            "codigo": exc_pers.codigo.value,
            "mensaje": exc_pers.mensaje,
        }
        return None
    except (ErrorAdministracionInventario, ErrorAutorizacionAdmin) as exc:
        destino[CLAVE_MENSAJE_OPERACION_ADMIN] = {
            "tipo": "error",
            "codigo": "ERROR_RECARGA_CONFLICTO",
            "mensaje": str(exc),
        }
        return None


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
    sincronizar_producto_seleccionado_gemini(
        destino,
        codigo_seleccionado_actual=destino.get(CLAVE_PRODUCTO_SELECCIONADO),
    )
    return obtener_detalle_producto_en_sesion(estado=destino)


def volver_a_resultados_en_sesion(
    estado: MutableMapping[str, Any] | None = None,
) -> None:
    """Cierra la vista de detalle y regresa a la lista de resultados conservando página y búsqueda activa."""
    destino = inicializar_estado_sesion(estado)
    destino[CLAVE_PRODUCTO_SELECCIONADO] = None
    sincronizar_producto_seleccionado_gemini(
        destino,
        codigo_seleccionado_actual=None,
    )


def _obtener_inventario_lectura_para_gemini(
    estado: MutableMapping[str, Any],
    *,
    inventario_explicito: InventarioDatos | None = None,
    descargador_remoto: DescargadorRemoto | None = None,
) -> InventarioDatos | None:
    """Obtiene en modo solo lectura el inventario vigente para consulta contextual de Gemini."""
    if inventario_explicito is not None:
        return inventario_explicito

    inv_sesion = estado.get(CLAVE_INVENTARIO_SESION)
    if isinstance(inv_sesion, InventarioDatos):
        return inv_sesion

    lector = descargador_remoto or github_inventario.descargar_inventario_remoto
    try:
        lectura = lector(config=CONFIGURACION_POR_DEFECTO)
        if isinstance(lectura.inventario, InventarioDatos):
            estado[CLAVE_INVENTARIO_SESION] = lectura.inventario
            estado[CLAVE_SHA_SESION] = lectura.sha_github
            return lectura.inventario
    except Exception:
        return None
    return None


def ejecutar_consulta_gemini_en_sesion(
    pregunta: Any,
    *,
    estado: MutableMapping[str, Any] | None = None,
    inventario: InventarioDatos | None = None,
    descargador_remoto: DescargadorRemoto | None = None,
    cliente_generador: ClienteGeneradorGemini | None = None,
    fuente_secretos: Mapping[str, Any] | None = None,
    fuente_entorno: Mapping[str, str] | None = None,
    config_limites: ConfiguracionLimitesGemini = CONFIGURACION_LIMITES_DEFECTO,
    reloj: ProveedorReloj | None = None,
) -> ResultadoConsultaGemini:
    """Ejecuta una consulta de cliente en el chat Gemini en modo lectura sin afectar el buscador."""
    destino = inicializar_estado_sesion(estado)
    inv_efectivo = _obtener_inventario_lectura_para_gemini(
        destino,
        inventario_explicito=inventario,
        descargador_remoto=descargador_remoto,
    )
    codigo_sel = destino.get(CLAVE_PRODUCTO_SELECCIONADO)
    return procesar_consulta_gemini_en_sesion(
        pregunta,
        estado=destino,
        inventario=inv_efectivo,
        codigo_producto_seleccionado=codigo_sel,
        cliente_generador=cliente_generador,
        fuente_secretos=fuente_secretos,
        fuente_entorno=fuente_entorno,
        config_limites=config_limites,
        reloj=reloj,
    )


def ejecutar_nueva_conversacion_gemini_en_sesion(
    estado: MutableMapping[str, Any] | None = None,
    *,
    config_limites: ConfiguracionLimitesGemini = CONFIGURACION_LIMITES_DEFECTO,
    reloj: ProveedorReloj | None = None,
) -> EstadoUsoSesionGemini:
    """Limpia el historial y contexto temporal de Gemini conservando el contador de uso de la ventana."""
    destino = inicializar_estado_sesion(estado)
    return iniciar_nueva_conversacion_gemini(
        destino,
        config_limites=config_limites,
        reloj=reloj,
    )


def ejecutar_reintento_gemini_en_sesion(
    estado: MutableMapping[str, Any] | None = None,
    *,
    inventario: InventarioDatos | None = None,
    descargador_remoto: DescargadorRemoto | None = None,
    cliente_generador: ClienteGeneradorGemini | None = None,
    fuente_secretos: Mapping[str, Any] | None = None,
    fuente_entorno: Mapping[str, str] | None = None,
    config_limites: ConfiguracionLimitesGemini = CONFIGURACION_LIMITES_DEFECTO,
    reloj: ProveedorReloj | None = None,
) -> ResultadoConsultaGemini | None:
    """Reintenta manualmente la última consulta fallida en el chat Gemini."""
    destino = inicializar_estado_sesion(estado)
    inv_efectivo = _obtener_inventario_lectura_para_gemini(
        destino,
        inventario_explicito=inventario,
        descargador_remoto=descargador_remoto,
    )
    codigo_sel = destino.get(CLAVE_PRODUCTO_SELECCIONADO)
    return reintentar_ultima_consulta_gemini_en_sesion(
        estado=destino,
        inventario=inv_efectivo,
        codigo_producto_seleccionado=codigo_sel,
        cliente_generador=cliente_generador,
        fuente_secretos=fuente_secretos,
        fuente_entorno=fuente_entorno,
        config_limites=config_limites,
        reloj=reloj,
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
    """Orquesta la validación de entrada, lectura vigente desde GitHub y búsqueda por nombre."""
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
    """Presenta la identidad visual y la barra de navegación superior de FerreteríaMS (Inicio / Productos)."""
    col_marca, col_nav = st.columns([2.35, 1], vertical_alignment="center")
    with col_marca:
        st.title(f"{ICONO_PAGINA} {TITULO}")
        st.caption(DESCRIPCION)

    seccion_actual = obtener_seccion_activa()
    with col_nav:
        col_nav_inicio, col_nav_productos = st.columns(2, gap="small")
        with col_nav_inicio:
            if st.button(
                TEXTO_BOTON_NAV_INICIO,
                key="btn_nav_inicio",
                type="primary" if seccion_actual == SeccionInterfaz.INICIO else "secondary",
                use_container_width=True,
            ):
                seleccionar_seccion_interfaz(SeccionInterfaz.INICIO)
                st.rerun()
        with col_nav_productos:
            if st.button(
                TEXTO_BOTON_NAV_PRODUCTOS,
                key="btn_nav_productos",
                type="primary" if seccion_actual == SeccionInterfaz.PRODUCTOS else "secondary",
                use_container_width=True,
            ):
                seleccionar_seccion_interfaz(SeccionInterfaz.PRODUCTOS)
                st.rerun()

    if seccion_actual == SeccionInterfaz.INICIO:
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
    """Presenta el área visual reservada para el Asistente Gemini en v0 (compatibilidad legado)."""
    _renderizar_seccion_gemini()


def _renderizar_seccion_gemini(
    *,
    descargador_remoto: DescargadorRemoto | None = None,
    cliente_generador: ClienteGeneradorGemini | None = None,
) -> None:
    """Renderiza el chat operativo de texto del Asistente Gemini (Bloque 2 — P16, RF-F-012..RF-F-025)."""
    with st.container(border=True):
        st.subheader(f"✨ {TITULO_SECCION_GEMINI}")

        # 1. Aviso permanente de inteligencia artificial y seguridad técnica (RF-F-019, CA-F-015)
        st.markdown(
            f"""
            <div class="ferms-gemini-aviso-permanente" role="note" aria-label="Aviso de inteligencia artificial y seguridad técnica">
                <strong>ℹ️ Aviso importante:</strong> {AVISO_PERMANENTE_IA_GEMINI}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 2. Contexto actual del producto seleccionado (RF-F-016, CA-F-012)
        codigo_sel = st.session_state.get(CLAVE_PRODUCTO_SELECCIONADO)
        sincronizar_producto_seleccionado_gemini(
            st.session_state,
            codigo_seleccionado_actual=codigo_sel,
        )
        inv_en_sesion = st.session_state.get(CLAVE_INVENTARIO_SESION)
        prod_ctx = obtener_producto_activo_seleccionado_contexto(
            inv_en_sesion if isinstance(inv_en_sesion, InventarioDatos) else None,
            codigo_sel,
        )
        if prod_ctx is not None:
            cod_seg = escapar_texto_presentacion_segura(prod_ctx.codigo_producto)
            nom_seg = escapar_texto_presentacion_segura(prod_ctx.nombre)
            ubic_seg = escapar_texto_presentacion_segura(
                prod_ctx.ubicacion_principal_etiqueta
            )
            st.markdown(
                f"""
                <div class="ferms-gemini-contexto-producto" role="status" aria-label="Producto activo en contexto">
                    <strong>📌 Producto seleccionado en contexto:</strong> {nom_seg}
                    (<code>{cod_seg}</code>)<br/>
                    <span>📍 {ubic_seg}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.caption(
                "Asesoría técnica bilingüe (ES/EN) sobre herramientas, materiales, reparaciones y proyectos. "
                "Puedes seleccionar un producto de la búsqueda para incluirlo como referencia."
            )

        # 3. Contador de uso de la ventana actual y botón «Nueva conversación» (RF-F-022, RF-F-023)
        estado_uso = obtener_estado_uso_gemini_en_sesion(st.session_state)
        col_uso, col_nueva = st.columns([1.4, 1.2], vertical_alignment="center")
        with col_uso:
            st.caption(
                f"📊 Consultas en ventana actual: "
                f"{estado_uso.consultas_realizadas}/{estado_uso.limite_consultas}"
            )
        with col_nueva:
            if st.button(
                TEXTO_BOTON_NUEVA_CONVERSACION_GEMINI,
                key="btn_nueva_conversacion_gemini",
                use_container_width=True,
            ):
                ejecutar_nueva_conversacion_gemini_en_sesion(st.session_state)
                st.session_state["_ferms_limpiar_campo_pregunta_gemini"] = True
                st.rerun()

        # 4. Historial temporal de mensajes de la sesión (RF-F-012, RF-F-021)
        historial = obtener_historial_chat_gemini(st.session_state)
        if not historial:
            st.caption(
                "Escribe tu consulta técnica abajo. Los productos activos confirmados en nuestro "
                "catálogo se distinguirán explícitamente de las recomendaciones generales."
            )
        else:
            for msg in historial:
                texto_msg_seguro = escapar_texto_presentacion_segura(
                    ocultar_secretos_gemini(msg.contenido)
                ).replace("\n", "<br/>")
                if msg.rol == "user":
                    st.markdown(
                        f"""
                        <div class="ferms-gemini-mensaje-usuario">
                            <strong>👤 Tú:</strong><br/>{texto_msg_seguro}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="ferms-gemini-mensaje-asistente">
                            <strong>🤖 Asistente Gemini:</strong><br/>{texto_msg_seguro}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        # 5. Retroalimentación de errores y opción de reintento manual (RF-F-024, CA-F-017)
        error_gemini = st.session_state.get(CLAVE_ULTIMO_ERROR_GEMINI)
        if isinstance(error_gemini, Mapping):
            msg_err_seg = ocultar_secretos_gemini(str(error_gemini.get("mensaje", "")))
            cod_err_str = ocultar_secretos_gemini(
                str(error_gemini.get("codigo", ""))
            ).strip()
            es_reintentable = bool(error_gemini.get("reintentable", False))
            if msg_err_seg:
                if cod_err_str in {
                    CodigoErrorGemini.PREGUNTA_VACIA.value,
                    CodigoErrorGemini.PREGUNTA_DEMASIADO_LARGA.value,
                    CodigoErrorGemini.LIMITE_USO_SESION_ALCANZADO.value,
                }:
                    st.warning(msg_err_seg)
                else:
                    st.error(msg_err_seg)
                    if cod_err_str:
                        cat_err_seg = ocultar_secretos_gemini(
                            str(
                                error_gemini.get("categoria_tecnica")
                                or obtener_categoria_tecnica_error_gemini(cod_err_str)
                            )
                        ).strip()
                        subcat_err_seg = ocultar_secretos_gemini(
                            str(error_gemini.get("subcategoria_tecnica", "") or "")
                        ).strip()
                        sufijo_subcat = (
                            f" · Detalle: `{subcat_err_seg}`" if subcat_err_seg else ""
                        )
                        st.caption(
                            f"Diagnóstico técnico: `{cod_err_str}` ({cat_err_seg}){sufijo_subcat}"
                        )
            if es_reintentable and st.session_state.get(CLAVE_ULTIMA_PREGUNTA_FALLIDA_GEMINI):
                if st.button(
                    TEXTO_BOTON_REINTENTAR_GEMINI,
                    key="btn_reintentar_consulta_gemini",
                    use_container_width=True,
                ):
                    ejecutar_reintento_gemini_en_sesion(
                        estado=st.session_state,
                        descargador_remoto=descargador_remoto,
                        cliente_generador=cliente_generador,
                    )
                    st.rerun()

        # 6. Campo para escribir preguntas y botón de envío (RF-F-012, RF-F-023)
        if st.session_state.pop("_ferms_limpiar_campo_pregunta_gemini", False):
            st.session_state["campo_pregunta_gemini"] = ""

        pregunta_input = st.text_area(
            label="Consulta técnica para el Asistente Gemini",
            placeholder=PLACEHOLDER_PREGUNTA_GEMINI,
            key="campo_pregunta_gemini",
            height=92,
            disabled=estado_uso.limite_alcanzado,
        )
        enviar_presionado = st.button(
            TEXTO_BOTON_ENVIAR_PREGUNTA_GEMINI,
            key="btn_enviar_pregunta_gemini",
            type="primary",
            disabled=estado_uso.limite_alcanzado,
            use_container_width=True,
        )
        if enviar_presionado:
            res_consulta = ejecutar_consulta_gemini_en_sesion(
                pregunta_input,
                estado=st.session_state,
                descargador_remoto=descargador_remoto,
                cliente_generador=cliente_generador,
            )
            if res_consulta.exito:
                st.session_state["_ferms_limpiar_campo_pregunta_gemini"] = True
            st.rerun()


def formatear_nombre_usuario_admin_seguro(usuario: Any) -> str:
    """Escapa caracteres especiales HTML del nombre administrativo para presentación segura."""
    if not isinstance(usuario, str):
        return ""
    return html.escape(usuario.strip(), quote=True)


def _mostrar_retroalimentacion_auth_pendiente() -> None:
    """Muestra y limpia el último mensaje de estado de autenticación almacenado en sesión."""
    aviso = st.session_state.get(CLAVE_MENSAJE_AUTH_ADMIN)
    if not isinstance(aviso, Mapping):
        return
    mensaje_seguro = ocultar_secretos_autenticacion(str(aviso.get("mensaje", "")))
    if not mensaje_seguro:
        return
    tipo = str(aviso.get("tipo", "info"))
    if tipo == "success":
        st.success(mensaje_seguro)
    elif tipo == "error":
        st.error(mensaje_seguro)
    elif tipo == "warning":
        st.warning(mensaje_seguro)
    else:
        st.info(mensaje_seguro)


def _mostrar_retroalimentacion_operacion_admin() -> None:
    """Muestra el último mensaje de validación u operación local del inventario administrativo."""
    aviso = st.session_state.get(CLAVE_MENSAJE_OPERACION_ADMIN)
    if not isinstance(aviso, Mapping):
        return
    mensaje_seguro = ocultar_secretos_en_texto(
        ocultar_secretos_autenticacion(str(aviso.get("mensaje", "")))
    )
    if not mensaje_seguro:
        return
    tipo = str(aviso.get("tipo", "info"))
    if tipo == "success":
        st.success(mensaje_seguro)
    elif tipo == "error":
        st.error(mensaje_seguro)
    elif tipo == "warning":
        st.warning(mensaje_seguro)
    else:
        st.info(mensaje_seguro)


def _renderizar_vista_consulta_admin(
    contexto_dispositivo: ContextoDispositivo,
) -> None:
    """Renderiza el listado y buscador interno de productos para consulta administrativa (Sección 5.1)."""
    st.markdown("#### 📋 Consulta administrativa de productos y ubicaciones")
    termino_filtro = st.text_input(
        label="Filtrar por código o nombre de producto",
        value=str(st.session_state.get(CLAVE_TERMINO_FILTRO_ADMIN, "")),
        placeholder="Escribe un código (p. ej. 001) o nombre...",
        key="campo_admin_filtro_productos",
    )
    st.session_state[CLAVE_TERMINO_FILTRO_ADMIN] = termino_filtro

    try:
        productos = consultar_productos_administrativos(
            st.session_state,
            termino_filtro=termino_filtro,
            contexto_dispositivo=contexto_dispositivo,
            registrar_actividad=False,
        )
    except (ErrorAdministracionInventario, ErrorAutorizacionAdmin) as exc:
        st.error(str(exc))
        return

    st.caption(
        f"Total de productos en vista administrativa: {len(productos)} · "
        f"{MENSAJE_CATALOGO_PREDEFINIDO_NO_EDITABLE}"
    )

    if not productos:
        st.info("No se encontraron productos que coincidan con el filtro administrativo.")
        return

    for prod in productos:
        cod_raw = str(prod["codigo_producto"])
        cod_seguro = escapar_texto_presentacion_segura(cod_raw)
        nom_seguro = escapar_texto_presentacion_segura(prod["nombre"])
        cat_id_seguro = escapar_texto_presentacion_segura(prod["categoria_id"])
        cat_nom_seguro = escapar_texto_presentacion_segura(prod["nombre_categoria"])
        desc_segura = escapar_texto_presentacion_segura(
            prod["descripcion"] or "Sin descripción registrada."
        )
        estado_reg_seguro = escapar_texto_presentacion_segura(
            prod.get("estado_registro_texto", "")
        )
        es_activo_prod = bool(prod.get("es_activo", True))
        etiqueta_estado_prod = (
            "🟢 Activo (visible en búsqueda pública)"
            if es_activo_prod
            else "🔴 Inactivo (excluido de búsqueda pública)"
        )

        with st.container(border=True):
            col_info, col_ubic, col_acc = st.columns([2.2, 2.0, 1.2])
            with col_info:
                st.markdown(f"**{nom_seguro}**")
                st.markdown(f"`Código: {cod_seguro}` · **{etiqueta_estado_prod}**")
                st.caption(f"Categoría: {cat_id_seguro} — {cat_nom_seguro}")
                st.caption(f"Descripción: {desc_segura}")
                st.caption(f"Estado del registro: {estado_reg_seguro}")
            with col_ubic:
                ubic_prin = prod.get("ubicacion_principal")
                if isinstance(ubic_prin, Mapping):
                    etiqueta_prin = escapar_texto_presentacion_segura(
                        f"{ubic_prin.get('ubicacion_id', '')}: "
                        f"{ubic_prin.get('etiqueta', '')}"
                    )
                    st.markdown(f"📍 **Principal:** {etiqueta_prin}")
                secundarias = prod.get("ubicaciones_secundarias", [])
                if secundarias:
                    etiquetas_sec = ", ".join(
                        escapar_texto_presentacion_segura(
                            f"{u.get('ubicacion_id', '')} ({u.get('etiqueta', '')})"
                        )
                        for u in secundarias
                        if isinstance(u, Mapping)
                    )
                    st.caption(f"🗂️ Secundarias ({len(secundarias)}): {etiquetas_sec}")
                else:
                    st.caption("🗂️ Sin ubicaciones secundarias.")
            with col_acc:
                if st.button(
                    "✏️ Editar",
                    key=f"btn_admin_editar_{cod_raw}",
                    use_container_width=True,
                ):
                    seleccionar_modo_vista_admin_en_sesion(
                        ModoVistaAdmin.EDITAR_PRODUCTO,
                        st.session_state,
                        codigo_producto_editar=cod_raw,
                    )
                    st.rerun()
                confirmar_estado_lista = st.checkbox(
                    "Confirmar cambio de estado",
                    key=f"chk_admin_estado_prod_{cod_raw}",
                )
                if es_activo_prod:
                    if st.button(
                        "🔴 Desactivar",
                        key=f"btn_admin_desactivar_prod_{cod_raw}",
                        disabled=not confirmar_estado_lista,
                        use_container_width=True,
                    ):
                        ejecutar_desactivacion_producto_en_sesion(
                            codigo_producto=cod_raw,
                            confirmado=confirmar_estado_lista,
                            estado=st.session_state,
                            contexto_dispositivo=contexto_dispositivo,
                        )
                        st.rerun()
                else:
                    if st.button(
                        "🟢 Reactivar",
                        key=f"btn_admin_reactivar_prod_{cod_raw}",
                        disabled=not confirmar_estado_lista,
                        use_container_width=True,
                    ):
                        ejecutar_reactivacion_producto_en_sesion(
                            codigo_producto=cod_raw,
                            confirmado=confirmar_estado_lista,
                            estado=st.session_state,
                            contexto_dispositivo=contexto_dispositivo,
                        )
                        st.rerun()


def _renderizar_formulario_crear_producto_admin(
    contexto_dispositivo: ContextoDispositivo,
) -> None:
    """Renderiza el formulario administrativo de alta local de producto (Sección 5.2)."""
    st.markdown("#### ➕ Crear producto nuevo (en copia temporal de trabajo)")
    st.caption(AVISO_PERSISTENCIA_REMOTA_PENDIENTE_P10)

    try:
        categorias = obtener_catalogo_categorias_admin(
            st.session_state, contexto_dispositivo=contexto_dispositivo
        )
        ubicaciones = obtener_catalogo_ubicaciones_admin(
            st.session_state, contexto_dispositivo=contexto_dispositivo
        )
    except (ErrorAdministracionInventario, ErrorAutorizacionAdmin) as exc:
        st.error(str(exc))
        return

    opciones_cat = [c["categoria_id"] for c in categorias]
    etiquetas_cat = {c["categoria_id"]: c["etiqueta"] for c in categorias}
    opciones_ubic = [u["ubicacion_id"] for u in ubicaciones]
    etiquetas_ubic = {u["ubicacion_id"]: u["etiqueta"] for u in ubicaciones}

    borrador_form = st.session_state.get(CLAVE_FORMULARIO_BORRADOR_ADMIN)
    campos_borrador: Mapping[str, Any] = {}
    if isinstance(borrador_form, Mapping):
        if "campos" in borrador_form and isinstance(borrador_form["campos"], Mapping):
            campos_borrador = borrador_form["campos"]
        else:
            campos_borrador = borrador_form

    valor_cod_inicial = str(campos_borrador.get("codigo_producto", campos_borrador.get("codigo", "")))
    valor_nom_inicial = str(campos_borrador.get("nombre", ""))
    valor_desc_inicial = str(campos_borrador.get("descripcion", ""))

    with st.container(border=True):
        codigo_nuevo = st.text_input(
            label="Código único del producto (texto obligatorio, conserva ceros iniciales)",
            value=valor_cod_inicial,
            placeholder="Ejemplo: 00099 o P-099",
            key="campo_admin_crear_codigo",
        )
        nombre_nuevo = st.text_input(
            label="Nombre del producto (obligatorio)",
            value=valor_nom_inicial,
            placeholder="Ejemplo: Sierra circular profesional 7-1/4",
            key="campo_admin_crear_nombre",
        )
        categoria_nueva = st.selectbox(
            label="Categoría predefinida (obligatoria)",
            options=opciones_cat,
            format_func=lambda cid: etiquetas_cat.get(cid, cid),
            key="campo_admin_crear_categoria",
        )
        descripcion_nueva = st.text_area(
            label="Descripción técnica o comercial (opcional)",
            value=valor_desc_inicial,
            placeholder="Describe características y uso del producto...",
            key="campo_admin_crear_descripcion",
        )
        ubicaciones_seleccionadas = st.multiselect(
            label="Ubicaciones físicas asignadas (mínimo una ubicación predefinida)",
            options=opciones_ubic,
            default=opciones_ubic[:1] if opciones_ubic else [],
            format_func=lambda uid: etiquetas_ubic.get(uid, uid),
            key="campo_admin_crear_ubicaciones",
        )
        ubicacion_principal_sel = st.selectbox(
            label="Ubicación física principal (exactamente una de las ubicaciones asignadas)",
            options=opciones_ubic,
            format_func=lambda uid: etiquetas_ubic.get(uid, uid),
            key="campo_admin_crear_ubicacion_principal",
        )

        col_crear, col_borr = st.columns(2)
        with col_crear:
            if st.button(
                TEXTO_BOTON_ADMIN_CONFIRMAR_CREAR,
                key="btn_admin_confirmar_crear_producto",
                type="primary",
                use_container_width=True,
            ):
                ejecutar_creacion_producto_en_sesion(
                    codigo_producto=codigo_nuevo,
                    nombre=nombre_nuevo,
                    categoria_id=categoria_nueva,
                    descripcion=descripcion_nueva,
                    ubicaciones_ids=ubicaciones_seleccionadas,
                    ubicacion_principal_id=ubicacion_principal_sel,
                    estado=st.session_state,
                    contexto_dispositivo=contexto_dispositivo,
                )
                st.rerun()
        with col_borr:
            if st.button(
                TEXTO_BOTON_ADMIN_GUARDAR_BORRADOR_FORM,
                key="btn_admin_guardar_borrador_crear",
                use_container_width=True,
            ):
                try:
                    guardar_borrador_formulario_admin(
                        st.session_state,
                        {
                            "codigo_producto": codigo_nuevo,
                            "nombre": nombre_nuevo,
                            "categoria_id": categoria_nueva,
                            "descripcion": descripcion_nueva,
                            "ubicaciones_ids": list(ubicaciones_seleccionadas),
                            "ubicacion_principal_id": ubicacion_principal_sel,
                        },
                        modo_formulario=ModoVistaAdmin.CREAR_PRODUCTO.value,
                        contexto_dispositivo=contexto_dispositivo,
                    )
                    st.session_state[CLAVE_MENSAJE_OPERACION_ADMIN] = {
                        "tipo": "info",
                        "codigo": "BORRADOR_FORMULARIO_GUARDADO",
                        "mensaje": "Borrador del formulario de creación guardado temporalmente en la sesión.",
                    }
                except Exception as exc_b:
                    st.session_state[CLAVE_MENSAJE_OPERACION_ADMIN] = {
                        "tipo": "error",
                        "codigo": "ERROR_BORRADOR",
                        "mensaje": str(exc_b),
                    }
                st.rerun()


def _renderizar_formulario_editar_producto_admin(
    contexto_dispositivo: ContextoDispositivo,
) -> None:
    """Renderiza el formulario administrativo de edición local de producto y ubicaciones (Sección 5.3)."""
    st.markdown("#### ✏️ Editar producto existente y sus ubicaciones físicas")
    st.caption(AVISO_PERSISTENCIA_REMOTA_PENDIENTE_P10)

    try:
        productos = consultar_productos_administrativos(
            st.session_state,
            contexto_dispositivo=contexto_dispositivo,
            registrar_actividad=False,
        )
        categorias = obtener_catalogo_categorias_admin(
            st.session_state, contexto_dispositivo=contexto_dispositivo
        )
        ubicaciones = obtener_catalogo_ubicaciones_admin(
            st.session_state, contexto_dispositivo=contexto_dispositivo
        )
    except (ErrorAdministracionInventario, ErrorAutorizacionAdmin) as exc:
        st.error(str(exc))
        return

    if not productos:
        st.warning("No existen productos en el inventario de trabajo para editar.")
        return

    codigos_disponibles = [str(p["codigo_producto"]) for p in productos]
    mapa_productos = {str(p["codigo_producto"]): p for p in productos}

    codigo_preseleccionado = st.session_state.get(CLAVE_PRODUCTO_ADMIN_SELECCIONADO)
    indice_sel = (
        codigos_disponibles.index(codigo_preseleccionado)
        if isinstance(codigo_preseleccionado, str)
        and codigo_preseleccionado in codigos_disponibles
        else 0
    )

    codigo_elegido = st.selectbox(
        label="Selecciona el producto a editar",
        options=codigos_disponibles,
        index=indice_sel,
        format_func=lambda c: (
            f"{c} — {mapa_productos[c]['nombre']} "
            f"[{'Activo' if mapa_productos[c].get('es_activo', True) else 'Inactivo'}]"
        ),
        key="campo_admin_editar_selector_codigo",
    )
    st.session_state[CLAVE_PRODUCTO_ADMIN_SELECCIONADO] = codigo_elegido
    prod_actual = mapa_productos[codigo_elegido]
    es_activo_actual = bool(prod_actual.get("es_activo", True))

    opciones_cat = [c["categoria_id"] for c in categorias]
    etiquetas_cat = {c["categoria_id"]: c["etiqueta"] for c in categorias}
    cat_actual_id = str(prod_actual["categoria_id"])
    indice_cat = opciones_cat.index(cat_actual_id) if cat_actual_id in opciones_cat else 0

    opciones_ubic = [u["ubicacion_id"] for u in ubicaciones]
    etiquetas_ubic = {u["ubicacion_id"]: u["etiqueta"] for u in ubicaciones}

    ubic_prin_actual = prod_actual.get("ubicacion_principal") or {}
    id_prin_actual = str(ubic_prin_actual.get("ubicacion_id", ""))
    ids_sec_actuales = [
        str(u.get("ubicacion_id", ""))
        for u in prod_actual.get("ubicaciones_secundarias", [])
        if isinstance(u, Mapping)
    ]
    ids_todas_actuales = [
        uid for uid in ([id_prin_actual] + ids_sec_actuales) if uid in opciones_ubic
    ]
    indice_prin = (
        opciones_ubic.index(id_prin_actual) if id_prin_actual in opciones_ubic else 0
    )

    valor_nombre_actual = str(prod_actual["nombre"])
    valor_categoria_actual = opciones_cat[indice_cat] if opciones_cat else None
    valor_descripcion_actual = str(prod_actual.get("descripcion", ""))
    valor_ubicaciones_actuales = list(ids_todas_actuales)
    valor_principal_actual = opciones_ubic[indice_prin] if opciones_ubic else None

    clave_contexto_edicion = "_ferms_admin_editar_contexto_producto"
    contexto_producto_actual = (
        codigo_elegido,
        valor_nombre_actual,
        valor_categoria_actual,
        valor_descripcion_actual,
        tuple(valor_ubicaciones_actuales),
        valor_principal_actual,
    )
    claves_campos_edicion = (
        "campo_admin_editar_nombre",
        "campo_admin_editar_categoria",
        "campo_admin_editar_descripcion",
        "campo_admin_editar_ubicaciones",
        "campo_admin_editar_ubicacion_principal",
    )
    if (
        st.session_state.get(clave_contexto_edicion) != contexto_producto_actual
        or not all(clave in st.session_state for clave in claves_campos_edicion)
    ):
        st.session_state["campo_admin_editar_nombre"] = valor_nombre_actual
        st.session_state["campo_admin_editar_categoria"] = valor_categoria_actual
        st.session_state["campo_admin_editar_descripcion"] = valor_descripcion_actual
        st.session_state["campo_admin_editar_ubicaciones"] = list(
            valor_ubicaciones_actuales
        )
        st.session_state["campo_admin_editar_ubicacion_principal"] = (
            valor_principal_actual
        )
        st.session_state[clave_contexto_edicion] = contexto_producto_actual

    with st.container(border=True):
        etiqueta_estado_actual = (
            "🟢 Activo (visible en búsqueda pública)"
            if es_activo_actual
            else "🔴 Inactivo (excluido de búsqueda pública)"
        )
        st.markdown(
            f"**Código único del producto (inmutable — RF-015 / CA-044):** "
            f"`{escapar_texto_presentacion_segura(codigo_elegido)}` · "
            f"**Estado actual:** {etiqueta_estado_actual}"
        )
        nombre_editado = st.text_input(
            label="Nombre del producto (obligatorio)",
            key="campo_admin_editar_nombre",
        )
        categoria_editada = st.selectbox(
            label="Categoría predefinida",
            options=opciones_cat,
            format_func=lambda cid: etiquetas_cat.get(cid, cid),
            key="campo_admin_editar_categoria",
        )
        descripcion_editada = st.text_area(
            label="Descripción del producto",
            key="campo_admin_editar_descripcion",
        )
        ubicaciones_editadas = st.multiselect(
            label="Ubicaciones físicas asignadas al producto (mínimo una)",
            options=opciones_ubic,
            format_func=lambda uid: etiquetas_ubic.get(uid, uid),
            key="campo_admin_editar_ubicaciones",
        )
        ubicacion_principal_editada = st.selectbox(
            label="Ubicación física principal (exactamente una)",
            options=opciones_ubic,
            format_func=lambda uid: etiquetas_ubic.get(uid, uid),
            key="campo_admin_editar_ubicacion_principal",
        )

        col_guardar_ed, col_borr_ed = st.columns(2)
        with col_guardar_ed:
            if st.button(
                TEXTO_BOTON_ADMIN_CONFIRMAR_EDITAR,
                key="btn_admin_confirmar_editar_producto",
                type="primary",
                use_container_width=True,
            ):
                ejecutar_edicion_producto_en_sesion(
                    codigo_producto=codigo_elegido,
                    nombre=nombre_editado,
                    categoria_id=categoria_editada,
                    descripcion=descripcion_editada,
                    ubicaciones_ids=ubicaciones_editadas,
                    ubicacion_principal_id=ubicacion_principal_editada,
                    estado=st.session_state,
                    contexto_dispositivo=contexto_dispositivo,
                )
                st.rerun()
        with col_borr_ed:
            if st.button(
                TEXTO_BOTON_ADMIN_GUARDAR_BORRADOR_FORM,
                key="btn_admin_guardar_borrador_editar",
                use_container_width=True,
            ):
                try:
                    guardar_borrador_formulario_admin(
                        st.session_state,
                        {
                            "codigo_producto": codigo_elegido,
                            "nombre": nombre_editado,
                            "categoria_id": categoria_editada,
                            "descripcion": descripcion_editada,
                            "ubicaciones_ids": list(ubicaciones_editadas),
                            "ubicacion_principal_id": ubicacion_principal_editada,
                        },
                        modo_formulario=ModoVistaAdmin.EDITAR_PRODUCTO.value,
                        contexto_dispositivo=contexto_dispositivo,
                    )
                    st.session_state[CLAVE_MENSAJE_OPERACION_ADMIN] = {
                        "tipo": "info",
                        "codigo": "BORRADOR_FORMULARIO_GUARDADO",
                        "mensaje": "Borrador del formulario de edición guardado temporalmente en la sesión.",
                    }
                except Exception as exc_b:
                    st.session_state[CLAVE_MENSAJE_OPERACION_ADMIN] = {
                        "tipo": "error",
                        "codigo": "ERROR_BORRADOR",
                        "mensaje": str(exc_b),
                    }
                st.rerun()

        if ids_sec_actuales:
            st.markdown("**Retiro rápido de ubicaciones secundarias asignadas:**")
            for uid_sec in ids_sec_actuales:
                if st.button(
                    f"🗑️ Retirar ubicación secundaria {uid_sec}",
                    key=f"btn_admin_retirar_secundaria_{codigo_elegido}_{uid_sec}",
                ):
                    ejecutar_eliminacion_ubicacion_secundaria_en_sesion(
                        codigo_producto=codigo_elegido,
                        ubicacion_id=uid_sec,
                        estado=st.session_state,
                        contexto_dispositivo=contexto_dispositivo,
                    )
                    st.rerun()

        st.divider()
        st.markdown("**Estado de visibilidad pública del producto (RF-F-008 / CA-F-007):**")
        st.caption(
            "Los productos inactivos conservan intactos sus datos y ubicaciones asignadas, "
            "pero quedan excluidos del buscador y del detalle público."
        )
        confirmar_cambio_ed = st.checkbox(
            "Confirmo el cambio de estado de este producto",
            key=f"chk_admin_editar_estado_{codigo_elegido}",
        )
        if es_activo_actual:
            if st.button(
                "🔴 Desactivar producto",
                key=f"btn_admin_editar_desactivar_{codigo_elegido}",
                disabled=not confirmar_cambio_ed,
            ):
                ejecutar_desactivacion_producto_en_sesion(
                    codigo_producto=codigo_elegido,
                    confirmado=confirmar_cambio_ed,
                    estado=st.session_state,
                    contexto_dispositivo=contexto_dispositivo,
                )
                st.rerun()
        else:
            if st.button(
                "🟢 Reactivar producto",
                key=f"btn_admin_editar_reactivar_{codigo_elegido}",
                disabled=not confirmar_cambio_ed,
            ):
                ejecutar_reactivacion_producto_en_sesion(
                    codigo_producto=codigo_elegido,
                    confirmado=confirmar_cambio_ed,
                    estado=st.session_state,
                    contexto_dispositivo=contexto_dispositivo,
                )
                st.rerun()


def _renderizar_vista_categorias_admin(
    contexto_dispositivo: ContextoDispositivo,
) -> None:
    """Renderiza el panel administrativo de consulta, creación y renombrado de categorías (P14)."""
    st.markdown("#### 🗂️ Administración del catálogo de categorías")
    st.caption(
        "Crea nuevas categorías o renombra las existentes conservando su `Categoria_ID` inmutable. "
        "La desactivación o eliminación de categorías no forma parte de esta etapa."
    )

    try:
        categorias = consultar_categorias_administrativas(
            st.session_state,
            contexto_dispositivo=contexto_dispositivo,
            registrar_actividad=False,
        )
    except (ErrorAdministracionInventario, ErrorAutorizacionAdmin) as exc:
        st.error(str(exc))
        return

    col_crear_cat, col_renombrar_cat = st.columns(2)
    with col_crear_cat:
        with st.container(border=True):
            st.markdown("##### ➕ Crear nueva categoría")
            nueva_cat_id = st.text_input(
                label="Identificador único `Categoria_ID` (obligatorio)",
                placeholder="Ejemplo: CAT-099",
                key="campo_admin_crear_categoria_id",
            )
            nuevo_nom_cat = st.text_input(
                label="Nombre de la categoría (`Nombre_Categoria`, obligatorio)",
                placeholder="Ejemplo: Iluminación LED industrial",
                key="campo_admin_crear_nombre_categoria",
            )
            if st.button(
                TEXTO_BOTON_ADMIN_CONFIRMAR_CREAR_CATEGORIA,
                key="btn_admin_confirmar_crear_categoria",
                type="primary",
                use_container_width=True,
            ):
                ejecutar_creacion_categoria_en_sesion(
                    categoria_id=nueva_cat_id,
                    nombre_categoria=nuevo_nom_cat,
                    estado=st.session_state,
                    contexto_dispositivo=contexto_dispositivo,
                )
                st.rerun()

    with col_renombrar_cat:
        with st.container(border=True):
            st.markdown("##### ✏️ Renombrar categoría existente")
            if not categorias:
                st.info("No existen categorías registradas para renombrar.")
            else:
                ids_cat = [str(c["categoria_id"]) for c in categorias]
                mapa_cat = {str(c["categoria_id"]): c for c in categorias}
                cat_pre = st.session_state.get(CLAVE_CATEGORIA_ADMIN_SELECCIONADA)
                idx_cat = (
                    ids_cat.index(cat_pre)
                    if isinstance(cat_pre, str) and cat_pre in ids_cat
                    else 0
                )
                cat_sel_id = st.selectbox(
                    label="Selecciona la categoría a renombrar",
                    options=ids_cat,
                    index=idx_cat,
                    format_func=lambda cid: f"{cid} — {mapa_cat[cid]['nombre_categoria']}",
                    key="campo_admin_selector_categoria_renombrar",
                )
                st.session_state[CLAVE_CATEGORIA_ADMIN_SELECCIONADA] = cat_sel_id
                cat_actual = mapa_cat[cat_sel_id]

                clave_ctx_cat = "_ferms_admin_editar_contexto_categoria"
                ctx_cat_actual = (cat_sel_id, str(cat_actual["nombre_categoria"]))
                if (
                    st.session_state.get(clave_ctx_cat) != ctx_cat_actual
                    or "campo_admin_renombrar_nombre_categoria" not in st.session_state
                ):
                    st.session_state["campo_admin_renombrar_nombre_categoria"] = str(
                        cat_actual["nombre_categoria"]
                    )
                    st.session_state[clave_ctx_cat] = ctx_cat_actual

                st.markdown(
                    f"**`Categoria_ID` (inmutable — RF-F-002):** "
                    f"`{escapar_texto_presentacion_segura(cat_sel_id)}`"
                )
                st.caption(
                    f"Productos asociados: {cat_actual['total_productos_asociados']} "
                    f"(el nuevo nombre se reflejará automáticamente en todos ellos)."
                )
                nombre_cat_editado = st.text_input(
                    label="Nuevo nombre de la categoría (`Nombre_Categoria`)",
                    key="campo_admin_renombrar_nombre_categoria",
                )
                if st.button(
                    TEXTO_BOTON_ADMIN_CONFIRMAR_RENOMBRAR_CATEGORIA,
                    key="btn_admin_confirmar_renombrar_categoria",
                    type="primary",
                    use_container_width=True,
                ):
                    ejecutar_renombrado_categoria_en_sesion(
                        categoria_id=cat_sel_id,
                        nuevo_nombre_categoria=nombre_cat_editado,
                        estado=st.session_state,
                        contexto_dispositivo=contexto_dispositivo,
                    )
                    st.rerun()

    st.markdown(f"##### 📋 Categorías registradas ({len(categorias)})")
    for cat in categorias:
        cid_seg = escapar_texto_presentacion_segura(cat["categoria_id"])
        nom_seg = escapar_texto_presentacion_segura(cat["nombre_categoria"])
        est_seg = escapar_texto_presentacion_segura(cat["estado_registro_texto"])
        total_asoc = int(cat["total_productos_asociados"])
        with st.container(border=True):
            col_c1, col_c2 = st.columns([3, 1.5])
            with col_c1:
                st.markdown(f"**{nom_seg}** (`{cid_seg}`)")
                st.caption(f"Estado del registro: {est_seg}")
            with col_c2:
                st.markdown(f"📦 **{total_asoc} producto(s) asociado(s)**")


def _renderizar_vista_ubicaciones_admin(
    contexto_dispositivo: ContextoDispositivo,
) -> None:
    """Renderiza el panel administrativo de consulta, alta, edición y desactivación de ubicaciones (P14)."""
    st.markdown("#### 📍 Administración del catálogo de ubicaciones físicas")
    st.caption(
        "Crea nuevas ubicaciones físicas, o edita y desactiva aquellas que no tengan productos asociados "
        "en la hoja `Asignaciones`. El identificador `Ubicacion_ID` permanece inmutable."
    )

    try:
        ubicaciones = consultar_ubicaciones_administrativas(
            st.session_state,
            incluir_inactivas=True,
            contexto_dispositivo=contexto_dispositivo,
            registrar_actividad=False,
        )
    except (ErrorAdministracionInventario, ErrorAutorizacionAdmin) as exc:
        st.error(str(exc))
        return

    col_crear_ub, col_editar_ub = st.columns(2)
    with col_crear_ub:
        with st.container(border=True):
            st.markdown("##### ➕ Crear nueva ubicación física")
            nuevo_ubic_id = st.text_input(
                label="Identificador único `Ubicacion_ID` (obligatorio)",
                placeholder="Ejemplo: U-099",
                key="campo_admin_crear_ubicacion_id",
            )
            col_r, col_c = st.columns(2)
            with col_r:
                nuevo_rack = st.text_input(
                    label="Rack (obligatorio)",
                    placeholder="Ej.: R9",
                    key="campo_admin_crear_ubicacion_rack",
                )
            with col_c:
                nueva_columna = st.text_input(
                    label="Columna (obligatorio)",
                    placeholder="Ej.: C1",
                    key="campo_admin_crear_ubicacion_columna",
                )
            col_n, col_p = st.columns(2)
            with col_n:
                nuevo_nivel = st.text_input(
                    label="Nivel (obligatorio)",
                    placeholder="Ej.: N1",
                    key="campo_admin_crear_ubicacion_nivel",
                )
            with col_p:
                nueva_posicion = st.text_input(
                    label="Posición (obligatorio)",
                    placeholder="Ej.: P1",
                    key="campo_admin_crear_ubicacion_posicion",
                )
            if st.button(
                TEXTO_BOTON_ADMIN_CONFIRMAR_CREAR_UBICACION,
                key="btn_admin_confirmar_crear_ubicacion",
                type="primary",
                use_container_width=True,
            ):
                ejecutar_creacion_ubicacion_en_sesion(
                    ubicacion_id=nuevo_ubic_id,
                    rack=nuevo_rack,
                    columna=nueva_columna,
                    nivel=nuevo_nivel,
                    posicion=nueva_posicion,
                    estado=st.session_state,
                    contexto_dispositivo=contexto_dispositivo,
                )
                st.rerun()

    with col_editar_ub:
        with st.container(border=True):
            st.markdown("##### ✏️ Editar o desactivar ubicación existente")
            if not ubicaciones:
                st.info("No existen ubicaciones físicas registradas.")
            else:
                ids_ubic = [str(u["ubicacion_id"]) for u in ubicaciones]
                mapa_ubic = {str(u["ubicacion_id"]): u for u in ubicaciones}
                ubic_pre = st.session_state.get(CLAVE_UBICACION_ADMIN_SELECCIONADA)
                idx_ubic = (
                    ids_ubic.index(ubic_pre)
                    if isinstance(ubic_pre, str) and ubic_pre in ids_ubic
                    else 0
                )
                ubic_sel_id = st.selectbox(
                    label="Selecciona la ubicación física",
                    options=ids_ubic,
                    index=idx_ubic,
                    format_func=lambda uid: (
                        f"{uid} — {mapa_ubic[uid]['etiqueta']} "
                        f"({'Activa' if mapa_ubic[uid]['es_activa'] else 'Inactiva'})"
                    ),
                    key="campo_admin_selector_ubicacion_editar",
                )
                st.session_state[CLAVE_UBICACION_ADMIN_SELECCIONADA] = ubic_sel_id
                ubic_actual = mapa_ubic[ubic_sel_id]

                clave_ctx_ubic = "_ferms_admin_editar_contexto_ubicacion"
                ctx_ubic_actual = (
                    ubic_sel_id,
                    str(ubic_actual["rack"]),
                    str(ubic_actual["columna"]),
                    str(ubic_actual["nivel"]),
                    str(ubic_actual["posicion"]),
                    str(ubic_actual["activo"]),
                )
                claves_ed_ubic = (
                    "campo_admin_editar_ubicacion_rack",
                    "campo_admin_editar_ubicacion_columna",
                    "campo_admin_editar_ubicacion_nivel",
                    "campo_admin_editar_ubicacion_posicion",
                )
                if (
                    st.session_state.get(clave_ctx_ubic) != ctx_ubic_actual
                    or not all(k in st.session_state for k in claves_ed_ubic)
                ):
                    st.session_state["campo_admin_editar_ubicacion_rack"] = str(
                        ubic_actual["rack"]
                    )
                    st.session_state["campo_admin_editar_ubicacion_columna"] = str(
                        ubic_actual["columna"]
                    )
                    st.session_state["campo_admin_editar_ubicacion_nivel"] = str(
                        ubic_actual["nivel"]
                    )
                    st.session_state["campo_admin_editar_ubicacion_posicion"] = str(
                        ubic_actual["posicion"]
                    )
                    st.session_state[clave_ctx_ubic] = ctx_ubic_actual

                st.markdown(
                    f"**`Ubicacion_ID` (inmutable — RF-F-005):** "
                    f"`{escapar_texto_presentacion_segura(ubic_sel_id)}` · "
                    f"**Estado `Activo`:** `{escapar_texto_presentacion_segura(ubic_actual['activo'])}`"
                )
                if int(ubic_actual["total_productos_asociados"]) > 0:
                    st.warning(ubic_actual["motivo_bloqueo"])

                col_er, col_ec = st.columns(2)
                with col_er:
                    rack_ed = st.text_input(
                        label="Rack",
                        key="campo_admin_editar_ubicacion_rack",
                    )
                with col_ec:
                    col_ed = st.text_input(
                        label="Columna",
                        key="campo_admin_editar_ubicacion_columna",
                    )
                col_en, col_ep = st.columns(2)
                with col_en:
                    niv_ed = st.text_input(
                        label="Nivel",
                        key="campo_admin_editar_ubicacion_nivel",
                    )
                with col_ep:
                    pos_ed = st.text_input(
                        label="Posición",
                        key="campo_admin_editar_ubicacion_posicion",
                    )

                col_btn_ed_u, col_btn_des_u = st.columns(2)
                with col_btn_ed_u:
                    if st.button(
                        TEXTO_BOTON_ADMIN_CONFIRMAR_EDITAR_UBICACION,
                        key="btn_admin_confirmar_editar_ubicacion",
                        type="primary",
                        use_container_width=True,
                    ):
                        ejecutar_edicion_ubicacion_en_sesion(
                            ubicacion_id=ubic_sel_id,
                            rack=rack_ed,
                            columna=col_ed,
                            nivel=niv_ed,
                            posicion=pos_ed,
                            estado=st.session_state,
                            contexto_dispositivo=contexto_dispositivo,
                        )
                        st.rerun()
                with col_btn_des_u:
                    if st.button(
                        TEXTO_BOTON_ADMIN_DESACTIVAR_UBICACION,
                        key="btn_admin_desactivar_ubicacion",
                        use_container_width=True,
                    ):
                        ejecutar_desactivacion_ubicacion_en_sesion(
                            ubicacion_id=ubic_sel_id,
                            estado=st.session_state,
                            contexto_dispositivo=contexto_dispositivo,
                        )
                        st.rerun()

    st.markdown(f"##### 📋 Ubicaciones físicas registradas ({len(ubicaciones)})")
    for ubic in ubicaciones:
        uid_seg = escapar_texto_presentacion_segura(ubic["ubicacion_id"])
        etiq_seg = escapar_texto_presentacion_segura(ubic["etiqueta"])
        est_seg = escapar_texto_presentacion_segura(ubic["estado_registro_texto"])
        total_asoc = int(ubic["total_productos_asociados"])
        es_act = bool(ubic["es_activa"])
        with st.container(border=True):
            col_u1, col_u2 = st.columns([3, 1.5])
            with col_u1:
                insignia_estado = "🟢 Activa" if es_act else "⚪ Inactiva (No asignable)"
                st.markdown(f"**`{uid_seg}` — {etiq_seg}** · {insignia_estado}")
                st.caption(f"Estado del registro: {est_seg}")
            with col_u2:
                st.markdown(f"📦 **{total_asoc} producto(s) asociado(s)**")
                if total_asoc > 0:
                    st.caption("🔒 Reasigna sus productos antes de editar o desactivar.")


def _renderizar_seccion_administrativa_productos(
    descargador_remoto: DescargadorRemoto | None = None,
) -> None:
    """Renderiza la sección administrativa `Productos` con protección en Python (Prompts 07, 08 y 09).

    Cumple:
    - RF-011, RF-012 / CA-009: Presenta el formulario Login/Logout al acceder a Productos.
    - RF-013 / CA-019, CA-058: Rechaza el acceso y cualquier operación administrativa cuando se
      detecta un contexto móvil y muestra la advertencia de exclusividad para computadora.
    - CA-010, CA-011: Verifica credenciales con Argon2id y habilita la vista administrativa inicial
      conservando compatibilidad con las regresiones de Prompts 07 y 08.
    - CA-030, CA-052..CA-057: Integra bloqueos progresivos, expiración a los 15 min de inactividad,
      advertencia previa 2 min antes, botón «Continuar sesión» y recuperación de borradores.
    - RF-014..RF-024 / CA-012..CA-018, CA-044..CA-051 (local): Permite consultar inventario, crear
      productos nuevos, editar productos existentes (con `Codigo_Producto` inmutable) y gestionar
      ubicaciones principales y secundarias sobre una copia temporal validada en memoria.
    """
    st.markdown(
        f"""
        <div class="ferms-aviso-solo-escritorio" role="note">
            <strong>💻 Acceso administrativo exclusivo para computadora:</strong>
            {MENSAJE_RESTRICCION_MOVIL_ADMIN}
        </div>
        """,
        unsafe_allow_html=True,
    )

    contexto_dispositivo = detectar_contexto_dispositivo(estado=st.session_state)
    if contexto_dispositivo == ContextoDispositivo.MOVIL:
        st.subheader(f"🔒 {TITULO_SECCION_ADMIN_LOGIN}")
        st.warning(MENSAJE_RESTRICCION_MOVIL_ADMIN)
        if st.button(
            TEXTO_BOTON_VOLVER_SITIO,
            key="btn_volver_inicio_desde_admin",
            use_container_width=True,
        ):
            seleccionar_seccion_interfaz(SeccionInterfaz.INICIO)
            st.rerun()
        return

    # Evaluación pasiva en servidor del estado temporal de la sesión (no actualiza actividad)
    estado_tiempo = consultar_estado_sesion_admin(
        st.session_state, contexto_dispositivo=contexto_dispositivo
    )
    if estado_tiempo.expirada:
        st.session_state[CLAVE_ESPACIO_TRABAJO_ADMIN] = None
        st.session_state[CLAVE_RESULTADO_CARGA_ADMIN] = None
        st.session_state[CLAVE_MODO_VISTA_ADMIN] = ModoVistaAdmin.INICIAL.value
        aviso_actual = st.session_state.get(CLAVE_MENSAJE_AUTH_ADMIN)
        codigo_aviso = (
            str(aviso_actual.get("codigo", ""))
            if isinstance(aviso_actual, Mapping)
            else ""
        )
        if codigo_aviso != CodigoResultadoAutenticacion.SESION_EXPIRADA.value:
            st.session_state[CLAVE_MENSAJE_AUTH_ADMIN] = {
                "tipo": "warning",
                "codigo": CodigoResultadoAutenticacion.SESION_EXPIRADA.value,
                "mensaje": MENSAJE_SESION_EXPIRADA_INACTIVIDAD,
            }

    # Validación efectiva en Python del estado autenticado de la sesión (Sección 8.3)
    if not estado_tiempo.autenticado or not esta_autenticado_en_sesion(
        st.session_state, contexto_dispositivo=contexto_dispositivo
    ):
        st.subheader(f"🔒 {TITULO_SECCION_ADMIN_LOGIN}")
        st.markdown(
            f"""
            <div class="ferms-admin-login-panel" role="region" aria-label="Acceso restringido de administración">
                <div class="ferms-admin-candado-icono" aria-hidden="true">🔒</div>
                <p class="ferms-admin-login-titulo">FerreteríaMS — {TITULO_SECCION_ADMIN_LOGIN}</p>
                <p class="ferms-admin-login-subtitulo">{SUBTITULO_SECCION_ADMIN_LOGIN}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        verificacion_cfg = obtener_configuracion_admin()
        if not verificacion_cfg.es_valida:
            st.warning(verificacion_cfg.mensaje_usuario)

        estado_bloqueo = consultar_estado_bloqueo_admin()
        aviso_pendiente = st.session_state.get(CLAVE_MENSAJE_AUTH_ADMIN)
        codigo_pendiente = (
            str(aviso_pendiente.get("codigo", ""))
            if isinstance(aviso_pendiente, Mapping)
            else ""
        )
        if (
            estado_bloqueo.esta_bloqueado
            and codigo_pendiente
            != CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE.value
        ):
            st.error(estado_bloqueo.mensaje_usuario)

        _mostrar_retroalimentacion_auth_pendiente()

        if estado_tiempo.tiene_borrador_retenido:
            st.info(f"📝 {MENSAJE_BORRADOR_RETENIDO_REAUTENTICACION}")

        with st.container(border=True):
            usuario_input = st.text_input(
                label="Usuario administrativo",
                placeholder="Usuario",
                key="campo_admin_usuario",
            )
            contrasena_input = st.text_input(
                label="Contraseña administrativa",
                placeholder="Contraseña",
                type="password",
                key="campo_admin_contrasena",
            )

            col_login, col_volver = st.columns(2)
            with col_login:
                login_presionado = st.button(
                    TEXTO_BOTON_LOGIN_ADMIN,
                    key="btn_admin_iniciar_sesion",
                    type="primary",
                    use_container_width=True,
                )
            with col_volver:
                volver_presionado = st.button(
                    TEXTO_BOTON_VOLVER_SITIO,
                    key="btn_volver_inicio_desde_admin",
                    use_container_width=True,
                )

            if volver_presionado:
                st.session_state[CLAVE_MENSAJE_AUTH_ADMIN] = None
                seleccionar_seccion_interfaz(SeccionInterfaz.INICIO)
                st.rerun()

            if login_presionado:
                ejecutar_login_administrativo_en_sesion(
                    usuario_input,
                    contrasena_input,
                    estado=st.session_state,
                    contexto_dispositivo=contexto_dispositivo,
                )
                st.rerun()

        st.caption(
            "🛡️ Área restringida para administración · Exclusivo para personal autorizado desde computadora."
        )
        return

    # Verificación obligatoria de autorización en Python antes de renderizar contenido administrativo
    try:
        sesion_admin = requerir_autorizacion_admin(
            st.session_state, contexto_dispositivo=contexto_dispositivo
        )
    except ErrorAutorizacionAdmin as exc_auth:
        st.error(exc_auth.mensaje)
        return

    st.subheader(f"📦 {TITULO_SECCION_PRODUCTOS_ADMIN}")
    _mostrar_retroalimentacion_auth_pendiente()
    _mostrar_retroalimentacion_operacion_admin()

    # Advertencia previa a los 13 minutos de inactividad (2 minutos antes de expirar — CA-054)
    if estado_tiempo.en_ventana_advertencia and estado_tiempo.mensaje_advertencia:
        st.warning(f"⏳ {estado_tiempo.mensaje_advertencia}")

    usuario_presentacion_segura = formatear_nombre_usuario_admin_seguro(
        sesion_admin.usuario
    )
    st.markdown(
        """
        <div class="ferms-admin-panel-autorizado" role="region" aria-label="Panel administrativo de Productos">
            <span class="ferms-admin-etiqueta-gestion">GESTIÓN DE PRODUCTOS · ACCESO AUTORIZADO</span>
            <p class="ferms-marca-subtitulo">
                Sesión administrativa verificada para la cuenta única en la interfaz web de escritorio.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        f"👤 Cuenta administrativa autenticada: {usuario_presentacion_segura}"
    )
    minutos_rest_aprox = max(1, int(math.ceil(estado_tiempo.segundos_restantes / 60.0)))
    st.caption(
        f"⏱️ Estado de sesión: Activa · Tiempo restante antes de expirar por inactividad: "
        f"~{minutos_rest_aprox} min ({int(math.ceil(estado_tiempo.segundos_restantes))} s)."
    )

    col_continuar, col_logout, col_volver_pub = st.columns(3)
    with col_continuar:
        if st.button(
            TEXTO_BOTON_CONTINUAR_SESION,
            key="btn_admin_continuar_sesion",
            type="primary" if estado_tiempo.en_ventana_advertencia else "secondary",
            use_container_width=True,
        ):
            ejecutar_renovacion_sesion_en_sesion(
                st.session_state,
                contexto_dispositivo=contexto_dispositivo,
            )
            st.rerun()
    with col_logout:
        if st.button(
            TEXTO_BOTON_LOGOUT_ADMIN,
            key="btn_admin_cerrar_sesion",
            use_container_width=True,
        ):
            ejecutar_logout_administrativo_en_sesion(st.session_state)
            st.rerun()
    with col_volver_pub:
        if st.button(
            TEXTO_BOTON_VOLVER_SITIO,
            key="btn_volver_inicio_desde_admin",
            use_container_width=True,
        ):
            seleccionar_seccion_interfaz(SeccionInterfaz.INICIO)
            st.rerun()

    # Si existe un borrador temporal disponible tras reautenticación, permitir restaurarlo o descartarlo
    if estado_tiempo.tiene_borrador_retenido:
        with st.container(border=True):
            st.info(
                "📝 Existe un borrador administrativo temporal asociado a tu sesión "
                "(no confirmado todavía en GitHub)."
            )
            col_rest, col_desc = st.columns(2)
            with col_rest:
                if st.button(
                    TEXTO_BOTON_RESTAURAR_BORRADOR,
                    key="btn_admin_restaurar_borrador",
                    use_container_width=True,
                ):
                    ejecutar_restauracion_borrador_en_sesion(
                        st.session_state,
                        descargador_remoto=descargador_remoto,
                        contexto_dispositivo=contexto_dispositivo,
                    )
                    st.rerun()
            with col_desc:
                if st.button(
                    TEXTO_BOTON_DESCARTAR_BORRADOR,
                    key="btn_admin_descartar_borrador",
                    use_container_width=True,
                ):
                    ejecutar_descarte_borrador_en_sesion(st.session_state)
                    st.rerun()

    # Barra de herramientas de gestión administrativa local (Prompts 09 y 14)
    col_cargar, col_consulta, col_crear, col_editar, col_categorias, col_ubicaciones = st.columns(6)
    with col_cargar:
        if st.button(
            TEXTO_BOTON_ADMIN_CARGAR_INVENTARIO,
            key="btn_admin_cargar_inventario",
            use_container_width=True,
        ):
            ejecutar_carga_inventario_admin_en_sesion(
                st.session_state,
                descargador_remoto=descargador_remoto,
                contexto_dispositivo=contexto_dispositivo,
            )
            st.rerun()
    with col_consulta:
        if st.button(
            TEXTO_BOTON_ADMIN_ABRIR_CONSULTA,
            key="btn_admin_abrir_consulta",
            use_container_width=True,
        ):
            seleccionar_modo_vista_admin_en_sesion(
                ModoVistaAdmin.CONSULTA, st.session_state
            )
            if st.session_state.get(CLAVE_ESPACIO_TRABAJO_ADMIN) is None:
                ejecutar_carga_inventario_admin_en_sesion(
                    st.session_state,
                    descargador_remoto=descargador_remoto,
                    contexto_dispositivo=contexto_dispositivo,
                )
            st.rerun()
    with col_crear:
        if st.button(
            TEXTO_BOTON_ADMIN_ABRIR_CREAR,
            key="btn_admin_abrir_crear",
            use_container_width=True,
        ):
            seleccionar_modo_vista_admin_en_sesion(
                ModoVistaAdmin.CREAR_PRODUCTO, st.session_state
            )
            if st.session_state.get(CLAVE_ESPACIO_TRABAJO_ADMIN) is None:
                ejecutar_carga_inventario_admin_en_sesion(
                    st.session_state,
                    descargador_remoto=descargador_remoto,
                    contexto_dispositivo=contexto_dispositivo,
                )
            st.rerun()
    with col_editar:
        if st.button(
            TEXTO_BOTON_ADMIN_ABRIR_EDITAR,
            key="btn_admin_abrir_editar",
            use_container_width=True,
        ):
            seleccionar_modo_vista_admin_en_sesion(
                ModoVistaAdmin.EDITAR_PRODUCTO, st.session_state
            )
            if st.session_state.get(CLAVE_ESPACIO_TRABAJO_ADMIN) is None:
                ejecutar_carga_inventario_admin_en_sesion(
                    st.session_state,
                    descargador_remoto=descargador_remoto,
                    contexto_dispositivo=contexto_dispositivo,
                )
            st.rerun()
    with col_categorias:
        if st.button(
            TEXTO_BOTON_ADMIN_ABRIR_CATEGORIAS,
            key="btn_admin_abrir_categorias",
            use_container_width=True,
        ):
            seleccionar_modo_vista_admin_en_sesion(
                ModoVistaAdmin.CATEGORIAS, st.session_state
            )
            if st.session_state.get(CLAVE_ESPACIO_TRABAJO_ADMIN) is None:
                ejecutar_carga_inventario_admin_en_sesion(
                    st.session_state,
                    descargador_remoto=descargador_remoto,
                    contexto_dispositivo=contexto_dispositivo,
                )
            st.rerun()
    with col_ubicaciones:
        if st.button(
            TEXTO_BOTON_ADMIN_ABRIR_UBICACIONES,
            key="btn_admin_abrir_ubicaciones",
            use_container_width=True,
        ):
            seleccionar_modo_vista_admin_en_sesion(
                ModoVistaAdmin.UBICACIONES, st.session_state
            )
            if st.session_state.get(CLAVE_ESPACIO_TRABAJO_ADMIN) is None:
                ejecutar_carga_inventario_admin_en_sesion(
                    st.session_state,
                    descargador_remoto=descargador_remoto,
                    contexto_dispositivo=contexto_dispositivo,
                )
            st.rerun()

    espacio_actual: EspacioTrabajoAdminInventario | None = st.session_state.get(
        CLAVE_ESPACIO_TRABAJO_ADMIN
    )
    resultado_carga: ResultadoCargaInventarioAdmin | None = st.session_state.get(
        CLAVE_RESULTADO_CARGA_ADMIN
    )
    modo_vista_str = str(
        st.session_state.get(CLAVE_MODO_VISTA_ADMIN, ModoVistaAdmin.INICIAL.value)
    )

    # Vista inicial tras login antes de activar un modo o espacio de trabajo
    if (
        modo_vista_str == ModoVistaAdmin.INICIAL.value
        and espacio_actual is None
        and resultado_carga is None
    ):
        with st.container(border=True):
            st.info(f"ℹ️ {MENSAJE_MANTENIMIENTO_PENDIENTE_P09}")
            st.caption(NOTA_CONTROLES_SESION_PENDIENTES_P08)
        return

    # Estados diferenciados cuando no fue posible cargar desde GitHub (Sección 10)
    if espacio_actual is None and resultado_carga is not None:
        with st.container(border=True):
            if resultado_carga.estado == EstadoInventarioAdmin.INVENTARIO_REMOTO_INEXISTENTE:
                st.warning(resultado_carga.mensaje_usuario)
                if resultado_carga.detalle_tecnico:
                    st.caption(resultado_carga.detalle_tecnico)
                col_reint, col_demo = st.columns(2)
                with col_reint:
                    if st.button(
                        "🔄 Reintentar lectura desde GitHub",
                        key="btn_admin_reintentar_carga",
                        use_container_width=True,
                    ):
                        ejecutar_carga_inventario_admin_en_sesion(
                            st.session_state,
                            descargador_remoto=descargador_remoto,
                            contexto_dispositivo=contexto_dispositivo,
                        )
                        st.rerun()
                with col_demo:
                    if st.button(
                        "🧪 Preparar copia demostrativa en memoria",
                        key="btn_admin_inicializar_demo_local",
                        use_container_width=True,
                    ):
                        ejecutar_carga_inventario_admin_en_sesion(
                            st.session_state,
                            inicializar_demo_si_no_existe=True,
                            descargador_remoto=descargador_remoto,
                            contexto_dispositivo=contexto_dispositivo,
                        )
                        st.rerun()
            else:
                st.error(resultado_carga.mensaje_usuario)
                if resultado_carga.detalle_tecnico:
                    st.caption(resultado_carga.detalle_tecnico)
                if st.button(
                    "🔄 Reintentar lectura desde GitHub",
                    key="btn_admin_reintentar_carga",
                ):
                    ejecutar_carga_inventario_admin_en_sesion(
                        st.session_state,
                        descargador_remoto=descargador_remoto,
                        contexto_dispositivo=contexto_dispositivo,
                    )
                    st.rerun()
        return

    if espacio_actual is None:
        return

    # Panel de estado del espacio de trabajo administrativo en memoria y persistencia GitHub (Prompts 09 y 10)
    with st.container(border=True):
        sha_presentacion = escapar_texto_presentacion_segura(
            espacio_actual.sha_base_remoto or "sin-sha-remoto (base local en memoria)"
        )
        conflicto_sha_activo = st.session_state.get(CLAVE_CONFLICTO_SHA_ADMIN)
        ultima_publicacion = st.session_state.get(CLAVE_ULTIMA_PUBLICACION_GITHUB_ADMIN)
        es_espacio_demostrativo = bool(
            espacio_actual.es_copia_demostrativa
            or contiene_datos_demostrativos(espacio_actual.inventario_trabajo)
            or contiene_datos_demostrativos(espacio_actual.inventario_original)
        )

        if es_espacio_demostrativo:
            st.session_state[CLAVE_CONFIRMACION_GUARDADO_GITHUB] = False
            if espacio_actual.tiene_cambios_locales_pendientes:
                st.warning(
                    f"🟡 **Cambios locales pendientes de guardar (no confirmados en GitHub):** "
                    f"{espacio_actual.total_productos_modificados_localmente} producto(s) modificado(s) "
                    f"en esta sesión · SHA base remoto: `{sha_presentacion}`."
                )
            st.info(
                f"🧪 **Copia demostrativa en memoria (`[DEMOSTRATIVO]`):** "
                f"{MENSAJE_DATOS_DEMOSTRATIVOS_NO_PUBLICABLES}"
            )
            if espacio_actual.tiene_cambios_locales_pendientes:
                if st.button(
                    TEXTO_BOTON_ADMIN_DESCARTAR_CAMBIOS,
                    key="btn_admin_descartar_cambios_locales",
                    use_container_width=True,
                ):
                    ejecutar_descarte_cambios_locales_en_sesion(
                        st.session_state,
                        contexto_dispositivo=contexto_dispositivo,
                    )
                    st.rerun()
        elif not espacio_actual.origen_remoto_confirmado and not espacio_actual.inicializacion_oficial_autorizada:
            st.session_state[CLAVE_CONFIRMACION_GUARDADO_GITHUB] = False
            st.warning(f"🔒 {MENSAJE_INICIALIZACION_OFICIAL_NO_AUTORIZADA}")
        elif espacio_actual.tiene_cambios_locales_pendientes or not espacio_actual.origen_remoto_confirmado:
            if espacio_actual.origen_remoto_confirmado:
                st.warning(
                    f"🟡 **Cambios locales pendientes de guardar (no confirmados en GitHub):** "
                    f"{espacio_actual.total_productos_modificados_localmente} producto(s) modificado(s) "
                    f"en esta sesión · SHA base remoto: `{sha_presentacion}`."
                )
            else:
                st.warning(
                    "🟡 **Inventario oficial autorizado pendiente de inicialización en GitHub:** "
                    "el archivo maestro aún no existe en remoto. Puedes revisarlo y confirmar "
                    "su publicación inicial controlada."
                )

            confirmacion_marcada = st.checkbox(
                TEXTO_CHECKBOX_ADMIN_CONFIRMAR_PUBLICACION,
                value=bool(st.session_state.get(CLAVE_CONFIRMACION_GUARDADO_GITHUB, False)),
                key="chk_admin_confirmar_publicacion_github",
            )
            st.session_state[CLAVE_CONFIRMACION_GUARDADO_GITHUB] = confirmacion_marcada

            etiqueta_boton_publicar = (
                TEXTO_BOTON_ADMIN_PUBLICAR_GITHUB
                if espacio_actual.origen_remoto_confirmado
                else TEXTO_BOTON_ADMIN_INICIALIZAR_GITHUB
            )
            col_pub, col_desc_loc = st.columns(2)
            with col_pub:
                if st.button(
                    etiqueta_boton_publicar,
                    key="btn_admin_publicar_github",
                    type="primary",
                    use_container_width=True,
                ):
                    ejecutar_publicacion_github_en_sesion(
                        st.session_state,
                        confirmacion_explicita=bool(confirmacion_marcada),
                        contexto_dispositivo=contexto_dispositivo,
                    )
                    st.rerun()
            with col_desc_loc:
                if st.button(
                    TEXTO_BOTON_ADMIN_DESCARTAR_CAMBIOS,
                    key="btn_admin_descartar_cambios_locales",
                    use_container_width=True,
                ):
                    ejecutar_descarte_cambios_locales_en_sesion(
                        st.session_state,
                        contexto_dispositivo=contexto_dispositivo,
                    )
                    st.rerun()
        else:
            st.info(
                f"🟢 **{MENSAJE_INVENTARIO_DISPONIBLE_EDICION_LOCAL}** "
                f"(SHA base remoto: `{sha_presentacion}`)."
            )
            if (
                isinstance(ultima_publicacion, ResultadoPublicacionGitHub)
                and ultima_publicacion.confirmado_en_github
            ):
                sha_conf = escapar_texto_presentacion_segura(
                    ultima_publicacion.nuevo_sha_archivo or ""
                )
                commit_conf = escapar_texto_presentacion_segura(
                    ultima_publicacion.sha_commit or ""
                )
                st.caption(
                    f"☁️ Última publicación confirmada en GitHub · SHA archivo: `{sha_conf}` "
                    f"· Commit: `{commit_conf}`."
                )

        if isinstance(conflicto_sha_activo, EstadoConflictoShaAdmin):
            sha_local_seg = escapar_texto_presentacion_segura(
                conflicto_sha_activo.sha_base_local or "ninguno"
            )
            sha_rem_seg = escapar_texto_presentacion_segura(
                conflicto_sha_activo.sha_remoto_detectado or "desconocido"
            )
            st.error(
                f"⚠️ **Conflicto de versión (SHA) detectado:** "
                f"{escapar_texto_presentacion_segura(conflicto_sha_activo.mensaje_usuario)} "
                f"(SHA base local: `{sha_local_seg}` · SHA remoto detectado: `{sha_rem_seg}`)."
            )
            confirmar_recarga_conflicto = st.checkbox(
                TEXTO_CHECKBOX_ADMIN_CONFIRMAR_RECARGA_CONFLICTO,
                key="chk_admin_confirmar_recarga_conflicto",
            )
            if st.button(
                TEXTO_BOTON_ADMIN_RECARGAR_TRAS_CONFLICTO,
                key="btn_admin_recargar_remoto_conflicto",
            ):
                ejecutar_recarga_remota_tras_conflicto_en_sesion(
                    st.session_state,
                    confirmar_descarte_locales=bool(confirmar_recarga_conflicto),
                    descargador_remoto=descargador_remoto,
                    contexto_dispositivo=contexto_dispositivo,
                )
                st.rerun()

    if modo_vista_str == ModoVistaAdmin.CREAR_PRODUCTO.value:
        _renderizar_formulario_crear_producto_admin(contexto_dispositivo)
    elif modo_vista_str == ModoVistaAdmin.EDITAR_PRODUCTO.value:
        _renderizar_formulario_editar_producto_admin(contexto_dispositivo)
    elif modo_vista_str == ModoVistaAdmin.CATEGORIAS.value:
        _renderizar_vista_categorias_admin(contexto_dispositivo)
    elif modo_vista_str == ModoVistaAdmin.UBICACIONES.value:
        _renderizar_vista_ubicaciones_admin(contexto_dispositivo)
    else:
        _renderizar_vista_consulta_admin(contexto_dispositivo)


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
    cliente_generador_gemini: ClienteGeneradorGemini | None = None,
) -> None:
    """Construye y renderiza la interfaz pública responsive, el chat Gemini y la administración."""

    st.set_page_config(
    page_title=TITULO,
    page_icon=ICONO_PAGINA,
    layout="wide",
    menu_items={
        "Get Help": None,
        "Report a Bug": None,
        "About": None,
    },
    )

    _aplicar_estilos_locales()
    inicializar_estado_sesion()

    # 1. Encabezado, identidad visual y navegación (Inicio / Productos)
    _renderizar_banner_encabezado()

    # 2. Composición principal a la izquierda (Inicio público o Productos protegido) y Gemini a la derecha
    col_principal, col_gemini = st.columns([2.35, 1], gap="large")
    with col_principal:
        if obtener_seccion_activa() == SeccionInterfaz.PRODUCTOS:
            _renderizar_seccion_administrativa_productos(
                descargador_remoto=descargador_remoto
            )
        else:
            _renderizar_area_inventario(descargador_remoto=descargador_remoto)
    with col_gemini:
        _renderizar_seccion_gemini(
            descargador_remoto=descargador_remoto,
            cliente_generador=cliente_generador_gemini,
        )


if __name__ == "__main__":
    renderizar_aplicacion()
