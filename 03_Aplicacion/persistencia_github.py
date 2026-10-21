"""Persistencia administrativa del inventario Excel en GitHub mediante Contents API.

Proyecto: FerreteríaMS v0
Tarea: FERMS-V0-P10
Módulo: 03_Aplicacion/persistencia_github.py
Requisitos relacionados: RF-012, RF-013, RF-014, RF-015, RF-016, RF-017, RF-018,
RF-019, RF-020, RF-021, RF-022, RF-023, RF-024, RF-025, RF-026, RF-027, RF-028,
RF-029, RF-030, RF-031, RF-035, RF-036, RF-037, RF-038 y Sección 6.3.
Criterios de aceptación relacionados: CA-012, CA-013, CA-014, CA-015, CA-016, CA-017,
CA-018, CA-019, CA-020, CA-021, CA-022, CA-023, CA-024, CA-025, CA-026, CA-042,
CA-044, CA-045, CA-046, CA-047, CA-048, CA-049, CA-050, CA-051, CA-054, CA-055,
CA-056, CA-057 y CA-058.

Este módulo implementa:
- Serialización íntegra de `InventarioDatos` a bytes `.xlsx` en memoria (`BytesIO`) con las
  cuatro hojas oficiales (`Productos`, `Categorías`, `Ubicaciones`, `Asignaciones`), orden
  exacto de columnas y preservación de códigos como texto con ceros a la izquierda.
- Verificación obligatoria de ida y vuelta (round-trip) releyendo los bytes `.xlsx` generados
  con `cargar_inventario_excel()` antes de autorizar cualquier publicación remota.
- Construcción y validación de solicitudes `PUT /repos/{owner}/{repo}/contents/{path}` hacia
  GitHub Contents API sobre el destino oficial (`JunyMSAI/FerreteriaMS`, rama `main`,
  ruta `03_Aplicacion/inventario.xlsx`).
- Creación inicial controlada exclusivamente cuando GitHub confirma de forma inequívoca la
  inexistencia del archivo maestro (`EstadoExistenciaRemota.NO_EXISTE`) y existe confirmación
  administrativa explícita.
- Actualización controlada con verificación previa de concurrencia por SHA (`sha_base_remoto`
  frente al SHA remoto actual) y detección de conflictos `409 Conflict` / `422`.
- Conservación intacta de los cambios locales pendientes y del borrador temporal ante
  cualquier conflicto de versión o fallo de red, autenticación, permisos o servidor.
- Sanitización estricta de tokens, contraseñas y hashes en mensajes, logs y excepciones.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Mapping, MutableMapping

from administracion_productos import (
    CLAVE_ESPACIO_TRABAJO_ADMIN,
    CLAVE_FORMULARIO_BORRADOR_ADMIN,
    CLAVE_RESULTADO_CARGA_ADMIN,
    MENSAJE_INVENTARIO_DISPONIBLE_EDICION_LOCAL,
    CodigoErrorAdministrativo,
    ErrorAdministracionInventario,
    ErrorValidacionAdministrativa,
    EspacioTrabajoAdminInventario,
    EstadoInventarioAdmin,
    ResultadoCargaInventarioAdmin,
    _obtener_espacio_trabajo_autorizado,
    cargar_inventario_administrativo_en_sesion,
    clonar_inventario_datos,
    contiene_datos_demostrativos,
    inventarios_son_identicos,
)
from autenticacion import (
    CodigoResultadoAutenticacion,
    ContextoDispositivo,
    ErrorAutorizacionAdmin,
    EstadoSesionAdmin,
    ProveedorReloj,
    consultar_estado_bloqueo_admin,
    descartar_borrador_admin,
    ocultar_secretos_autenticacion,
    renovar_sesion_admin,
)
from github_inventario import (
    CONFIGURACION_POR_DEFECTO,
    GITHUB_API_BASE_URL as URL_BASE_API_GITHUB,
    GITHUB_API_VERSION as VERSION_API_GITHUB,
    GITHUB_PROPIETARIO_DEFECTO as PROPIETARIO_POR_DEFECTO,
    GITHUB_RAMA_DEFECTO as RAMA_POR_DEFECTO,
    GITHUB_REPOSITORIO_DEFECTO as REPOSITORIO_POR_DEFECTO,
    GITHUB_RUTA_INVENTARIO_DEFECTO as RUTA_ARCHIVO_POR_DEFECTO,
    MARCA_SECRETO_OCULTO,
    CodigoErrorGitHub,
    ConfiguracionRepositorioGitHub,
    EjecutorHTTP,
    ErrorLecturaGitHub,
    RespuestaHTTPGitHub,
    ResultadoExistenciaRemota,
    ResultadoLecturaInventarioRemoto,
    _ManejadorRedireccionSeguraGitHub,
    consultar_existencia_inventario_remoto,
    descargar_inventario_remoto,
    obtener_token_configurado,
    ocultar_secretos_en_texto,
    validar_url_solicitud_github,
)
from inventario import (
    ESQUEMA_HOJAS as ESQUEMA_COLUMNAS,
    ORDEN_HOJAS,
    ErrorInventario,
    EstadoExistenciaRemota,
    InventarioDatos,
    cargar_inventario_excel,
    construir_inventario_datos,
    serializar_inventario_a_bytes,
    validar_inventario,
)

# Compuerta de seguridad para escrituras de red reales.
# Durante la ejecución de pruebas y mientras no se active en despliegue autorizado,
# permanece en False para impedir cualquier solicitud HTTP PUT real hacia GitHub.
ESCRITURA_REAL_GITHUB_HABILITADA: bool = False

TIMEOUT_ESCRITURA_POR_DEFECTO: float = 15.0

MENSAJE_COMMIT_ACTUALIZACION_DEFECTO: str = (
    "Actualización administrativa de inventario.xlsx (FerreteríaMS v0)"
)
MENSAJE_COMMIT_INICIALIZACION_DEFECTO: str = (
    "Inicialización administrativa de inventario.xlsx (FerreteríaMS v0)"
)

# Claves de estado de sesión para persistencia GitHub (Prompt 10)
CLAVE_CONFIRMACION_GUARDADO_GITHUB: str = "ferms_admin_confirmacion_guardado_github"
CLAVE_CONFLICTO_SHA_ADMIN: str = "ferms_admin_conflicto_sha"
CLAVE_ULTIMA_PUBLICACION_GITHUB_ADMIN: str = "ferms_admin_ultima_publicacion_github"
CLAVE_HUELLA_ULTIMA_PUBLICACION_ADMIN: str = "ferms_admin_huella_ultima_publicacion"

# Mensajes comprensibles en español para el administrador (Secciones 12 y 13)
MENSAJE_PUBLICACION_ACTUALIZACION_EXITOSA: str = (
    "Los cambios del inventario fueron guardados y confirmados exitosamente en GitHub."
)
MENSAJE_PUBLICACION_INICIALIZACION_EXITOSA: str = (
    "El archivo maestro 'inventario.xlsx' fue inicializado y confirmado exitosamente en GitHub."
)
MENSAJE_CONFLICTO_SHA_DETECTADO: str = (
    "No fue posible guardar porque el archivo 'inventario.xlsx' en GitHub fue modificado "
    "por otra operación (conflicto de versión SHA). Tus cambios locales y el borrador "
    "temporal se conservan intactos."
)
MENSAJE_ARCHIVO_REMOTO_YA_EXISTE: str = (
    "No es posible realizar la creación inicial porque '03_Aplicacion/inventario.xlsx' "
    "ya existe en GitHub. Tus datos locales se conservan sin sobrescribir el archivo remoto."
)
MENSAJE_CONFIRMACION_EXPLICITA_REQUERIDA: str = (
    "Debes confirmar explícitamente la operación antes de publicar cambios en GitHub."
)
MENSAJE_SIN_CAMBIOS_PENDIENTES: str = (
    "No existen cambios locales pendientes para publicar en GitHub."
)
MENSAJE_PUBLICACION_DUPLICADA_BLOQUEADA: str = (
    "Esta operación ya fue publicada y confirmada previamente en GitHub. "
    "No se enviará una publicación duplicada."
)
MENSAJE_RECARGA_REMOTA_TRAS_CONFLICTO_EXITOSA: str = (
    "Se recargó la versión vigente del inventario desde GitHub y se actualizó el SHA base de trabajo."
)
MENSAJE_CONFIRMACION_RECARGA_CONFLICTO_REQUERIDA: str = (
    "Debes confirmar explícitamente la recarga de la versión remota para reemplazar "
    "los cambios locales en conflicto."
)
MENSAJE_ERROR_TOKEN_ESCRITURA: str = (
    "No se encontró un token de GitHub configurado para realizar operaciones de escritura "
    "en el repositorio oficial."
)
MENSAJE_ERROR_CREDENCIAL_ESCRITURA: str = (
    "GitHub rechazó la autenticación o el token configurado no posee permisos de escritura "
    "sobre el repositorio oficial. Tus cambios locales permanecen protegidos."
)
MENSAJE_ERROR_DESTINO_ESCRITURA: str = (
    "El destino de escritura solicitado no coincide con el repositorio, rama o ruta oficial "
    "autorizada para FerreteríaMS v0."
)
MENSAJE_ERROR_REPOSITORIO_O_RAMA_ESCRITURA: str = (
    "No fue posible acceder al repositorio oficial o a la rama 'main' en GitHub. "
    "Tus cambios locales permanecen protegidos."
)
MENSAJE_ERROR_LIMITE_SOLICITUDES_ESCRITURA: str = (
    "Se alcanzó temporalmente el límite de solicitudes de GitHub API (rate limit). "
    "Tus cambios locales se conservan intactos para reintentar más tarde."
)
MENSAJE_ERROR_SERVIDOR_ESCRITURA: str = (
    "El servidor de GitHub presentó un error temporal (5xx) al procesar la escritura. "
    "Tus cambios locales se conservan intactos para reintentar."
)
MENSAJE_ERROR_RED_ESCRITURA: str = (
    "No fue posible completar el guardado en GitHub debido a un error de conexión o "
    "tiempo de espera agotado. Tus cambios locales siguen protegidos en la sesión."
)
MENSAJE_ERROR_RESPUESTA_INESPERADA_ESCRITURA: str = (
    "GitHub devolvió una respuesta inesperada o incompleta sin confirmar el nuevo SHA "
    "del archivo. No se declaró el guardado como exitoso y tus cambios locales se conservan."
)
MENSAJE_DATOS_DEMOSTRATIVOS_NO_PUBLICABLES: str = (
    "No se permite publicar ni inicializar en GitHub un inventario con datos demostrativos "
    "([DEMOSTRATIVO]). Los datos de demostración son exclusivos para edición temporal en memoria."
)
MENSAJE_INICIALIZACION_OFICIAL_NO_AUTORIZADA: str = (
    "La inicialización del archivo maestro 'inventario.xlsx' en GitHub requiere un inventario "
    "oficial autorizado y no puede ejecutarse desde una copia no autorizada o demostrativa."
)

_PATRON_ENCABEZADO_AUTH_TEXTO = re.compile(
    r"(?i)(['\"]?authorization['\"]?\s*[:=]\s*['\"]?(?:bearer\s+|token\s+)?)([^'\"\s,}]+)"
)


class ModoPublicacionGitHub(str, Enum):
    """Modalidad de escritura remota sobre `03_Aplicacion/inventario.xlsx` en GitHub."""

    ACTUALIZACION_ARCHIVO_EXISTENTE = "ACTUALIZACION_ARCHIVO_EXISTENTE"
    CREACION_INICIAL_ARCHIVO_NUEVO = "CREACION_INICIAL_ARCHIVO_NUEVO"


class EstadoResultadoPublicacionGitHub(str, Enum):
    """Estados posibles del intento de persistencia remota en GitHub."""

    PUBLICACION_CONFIRMADA = "PUBLICACION_CONFIRMADA"
    CREACION_INICIAL_CONFIRMADA = "CREACION_INICIAL_CONFIRMADA"
    CONFLICTO_SHA_REMOTO = "CONFLICTO_SHA_REMOTO"
    CONFLICTO_ARCHIVO_REMOTO_EXISTENTE = "CONFLICTO_ARCHIVO_REMOTO_EXISTENTE"
    ERROR_SERIALIZACION_O_VALIDACION = "ERROR_SERIALIZACION_O_VALIDACION"
    ERROR_AUTORIZACION_ADMIN = "ERROR_AUTORIZACION_ADMIN"
    BLOQUEADO_DATOS_DEMOSTRATIVOS = "BLOQUEADO_DATOS_DEMOSTRATIVOS"
    CONFIRMACION_REQUERIDA = "CONFIRMACION_REQUERIDA"
    SIN_CAMBIOS_PENDIENTES = "SIN_CAMBIOS_PENDIENTES"
    OPERACION_DUPLICADA = "OPERACION_DUPLICADA"
    ERROR_CREDENCIALES_O_PERMISOS = "ERROR_CREDENCIALES_O_PERMISOS"
    ERROR_DESTINO_O_RAMA = "ERROR_DESTINO_O_RAMA"
    ERROR_LIMITE_SOLICITUDES = "ERROR_LIMITE_SOLICITUDES"
    ERROR_SERVIDOR_GITHUB = "ERROR_SERVIDOR_GITHUB"
    ERROR_RED_O_TIMEOUT = "ERROR_RED_O_TIMEOUT"
    ERROR_RESPUESTA_INESPERADA = "ERROR_RESPUESTA_INESPERADA"


class CodigoErrorPersistenciaGitHub(str, Enum):
    """Códigos tipados de error durante la serialización, verificación y escritura en GitHub."""

    SERIALIZACION_INVALIDA = "SERIALIZACION_INVALIDA"
    VERIFICACION_ROUNDTRIP_FALLIDA = "VERIFICACION_ROUNDTRIP_FALLIDA"
    DESTINO_NO_AUTORIZADO = "DESTINO_NO_AUTORIZADO"
    TOKEN_ESCRITURA_FALTANTE = "TOKEN_ESCRITURA_FALTANTE"
    CONFIRMACION_EXPLICITA_REQUERIDA = "CONFIRMACION_EXPLICITA_REQUERIDA"
    SIN_CAMBIOS_PENDIENTES = "SIN_CAMBIOS_PENDIENTES"
    OPERACION_DUPLICADA = "OPERACION_DUPLICADA"
    SHA_BASE_FALTANTE = "SHA_BASE_FALTANTE"
    CONFLICTO_SHA_REMOTO = "CONFLICTO_SHA_REMOTO"
    ARCHIVO_REMOTO_YA_EXISTE = "ARCHIVO_REMOTO_YA_EXISTE"
    ESTADO_REMOTO_NO_VERIFICADO = "ESTADO_REMOTO_NO_VERIFICADO"
    CREDENCIAL_INVALIDA_O_SIN_PERMISO = "CREDENCIAL_INVALIDA_O_SIN_PERMISO"
    ACCESO_DENEGADO_ESCRITURA = "ACCESO_DENEGADO_ESCRITURA"
    REPOSITORIO_O_RAMA_INEXISTENTE = "REPOSITORIO_O_RAMA_INEXISTENTE"
    LIMITE_SOLICITUDES_AGOTADO = "LIMITE_SOLICITUDES_AGOTADO"
    ERROR_SERVIDOR_GITHUB = "ERROR_SERVIDOR_GITHUB"
    TIEMPO_ESPERA_AGOTADO = "TIEMPO_ESPERA_AGOTADO"
    CONEXION_RED_FALLIDA = "CONEXION_RED_FALLIDA"
    RESPUESTA_INESPERADA_ESCRITURA = "RESPUESTA_INESPERADA_ESCRITURA"
    ESCRITURA_REAL_NO_AUTORIZADA = "ESCRITURA_REAL_NO_AUTORIZADA"
    DATOS_DEMOSTRATIVOS_NO_PUBLICABLES = "DATOS_DEMOSTRATIVOS_NO_PUBLICABLES"
    INICIALIZACION_OFICIAL_NO_AUTORIZADA = "INICIALIZACION_OFICIAL_NO_AUTORIZADA"
    AUTORIZACION_ADMIN_INVALIDA = "AUTORIZACION_ADMIN_INVALIDA"


def sanitizar_texto_persistencia(
    texto: Any,
    *,
    token: str | None = None,
) -> str:
    """Sanitiza cualquier texto eliminando tokens de GitHub, encabezados Authorization, hashes Argon2 y credenciales."""
    if texto is None:
        return ""
    secretos_extra: tuple[str, ...] = (token.strip(),) if isinstance(token, str) and token.strip() else ()
    base = ocultar_secretos_autenticacion(str(texto), secretos_extra)
    base = _PATRON_ENCABEZADO_AUTH_TEXTO.sub(rf"\1{MARCA_SECRETO_OCULTO}", base)
    return ocultar_secretos_en_texto(base, token=token)


class ErrorPersistenciaGitHub(Exception):
    """Excepción base para errores de persistencia del inventario en GitHub (Prompt 10)."""

    def __init__(
        self,
        mensaje: str,
        *,
        codigo: CodigoErrorPersistenciaGitHub = CodigoErrorPersistenciaGitHub.RESPUESTA_INESPERADA_ESCRITURA,
        estado_publicacion: EstadoResultadoPublicacionGitHub = EstadoResultadoPublicacionGitHub.ERROR_RESPUESTA_INESPERADA,
        status_code: int | None = None,
        es_reintentable: bool = False,
        sha_base_local: str | None = None,
        sha_remoto_actual: str | None = None,
        detalle_tecnico: str = "",
        token: str | None = None,
    ) -> None:
        mensaje_seguro = sanitizar_texto_persistencia(mensaje, token=token)
        detalle_seguro = sanitizar_texto_persistencia(detalle_tecnico, token=token)
        super().__init__(mensaje_seguro)
        self.mensaje = mensaje_seguro
        self.codigo = codigo
        self.estado_publicacion = estado_publicacion
        self.status_code = status_code
        self.es_reintentable = es_reintentable
        self.sha_base_local = sha_base_local
        self.sha_remoto_actual = sha_remoto_actual
        self.detalle_tecnico = detalle_seguro
        self.conserva_cambios_locales = True

    def __str__(self) -> str:
        return self.mensaje

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"codigo={self.codigo.value!r}, "
            f"estado_publicacion={self.estado_publicacion.value!r}, "
            f"status_code={self.status_code!r}, "
            f"mensaje={sanitizar_texto_persistencia(self.mensaje)!r})"
        )


class ErrorSerializacionInventarioPersistente(ErrorPersistenciaGitHub):
    """Fallo al serializar `InventarioDatos` a `.xlsx` o en la verificación round-trip."""

    def __init__(
        self,
        mensaje: str,
        *,
        codigo: CodigoErrorPersistenciaGitHub = CodigoErrorPersistenciaGitHub.SERIALIZACION_INVALIDA,
        detalle_tecnico: str = "",
    ) -> None:
        super().__init__(
            mensaje,
            codigo=codigo,
            estado_publicacion=EstadoResultadoPublicacionGitHub.ERROR_SERIALIZACION_O_VALIDACION,
            es_reintentable=False,
            detalle_tecnico=detalle_tecnico,
        )


class ErrorDestinoEscrituraNoAutorizadoGitHub(ErrorPersistenciaGitHub):
    """Intento de escribir en un propietario, repositorio, rama, ruta o dominio no oficial."""

    def __init__(self, mensaje: str, *, detalle_tecnico: str = "") -> None:
        super().__init__(
            mensaje,
            codigo=CodigoErrorPersistenciaGitHub.DESTINO_NO_AUTORIZADO,
            estado_publicacion=EstadoResultadoPublicacionGitHub.ERROR_DESTINO_O_RAMA,
            es_reintentable=False,
            detalle_tecnico=detalle_tecnico,
        )


class ErrorTokenEscrituraFaltanteGitHub(ErrorPersistenciaGitHub):
    """Ausencia de token de GitHub configurado al intentar escribir en el repositorio."""

    def __init__(
        self,
        mensaje: str = MENSAJE_ERROR_TOKEN_ESCRITURA,
        *,
        detalle_tecnico: str = "",
    ) -> None:
        super().__init__(
            mensaje,
            codigo=CodigoErrorPersistenciaGitHub.TOKEN_ESCRITURA_FALTANTE,
            estado_publicacion=EstadoResultadoPublicacionGitHub.ERROR_CREDENCIALES_O_PERMISOS,
            es_reintentable=False,
            detalle_tecnico=detalle_tecnico,
        )


class ErrorConfirmacionPublicacionRequerida(ErrorPersistenciaGitHub):
    """Intento de publicar o inicializar en GitHub sin confirmación explícita del administrador."""

    def __init__(
        self,
        mensaje: str = MENSAJE_CONFIRMACION_EXPLICITA_REQUERIDA,
    ) -> None:
        super().__init__(
            mensaje,
            codigo=CodigoErrorPersistenciaGitHub.CONFIRMACION_EXPLICITA_REQUERIDA,
            estado_publicacion=EstadoResultadoPublicacionGitHub.CONFIRMACION_REQUERIDA,
            es_reintentable=True,
        )


class ErrorSinCambiosPendientesPublicacion(ErrorPersistenciaGitHub):
    """Intento de actualizar el inventario remoto cuando no existen cambios locales pendientes."""

    def __init__(
        self,
        mensaje: str = MENSAJE_SIN_CAMBIOS_PENDIENTES,
    ) -> None:
        super().__init__(
            mensaje,
            codigo=CodigoErrorPersistenciaGitHub.SIN_CAMBIOS_PENDIENTES,
            estado_publicacion=EstadoResultadoPublicacionGitHub.SIN_CAMBIOS_PENDIENTES,
            es_reintentable=False,
        )


class ErrorPublicacionDuplicadaGitHub(ErrorPersistenciaGitHub):
    """Bloqueo de doble envío para una operación administrativa ya confirmada en GitHub."""

    def __init__(
        self,
        mensaje: str = MENSAJE_PUBLICACION_DUPLICADA_BLOQUEADA,
    ) -> None:
        super().__init__(
            mensaje,
            codigo=CodigoErrorPersistenciaGitHub.OPERACION_DUPLICADA,
            estado_publicacion=EstadoResultadoPublicacionGitHub.OPERACION_DUPLICADA,
            es_reintentable=False,
        )


class ErrorShaBaseFaltanteGitHub(ErrorPersistenciaGitHub):
    """Intento de actualizar un archivo remoto sin disponer del SHA base de la versión cargada."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(
            mensaje,
            codigo=CodigoErrorPersistenciaGitHub.SHA_BASE_FALTANTE,
            estado_publicacion=EstadoResultadoPublicacionGitHub.CONFLICTO_SHA_REMOTO,
            es_reintentable=False,
        )


class ErrorConflictoVersionShaGitHub(ErrorPersistenciaGitHub):
    """Conflicto de concurrencia detectado porque el SHA remoto cambió respecto al SHA base local."""

    def __init__(
        self,
        mensaje: str = MENSAJE_CONFLICTO_SHA_DETECTADO,
        *,
        sha_base_local: str | None = None,
        sha_remoto_actual: str | None = None,
        status_code: int | None = None,
        detalle_tecnico: str = "",
        token: str | None = None,
    ) -> None:
        super().__init__(
            mensaje,
            codigo=CodigoErrorPersistenciaGitHub.CONFLICTO_SHA_REMOTO,
            estado_publicacion=EstadoResultadoPublicacionGitHub.CONFLICTO_SHA_REMOTO,
            status_code=status_code,
            es_reintentable=False,
            sha_base_local=sha_base_local,
            sha_remoto_actual=sha_remoto_actual,
            detalle_tecnico=detalle_tecnico,
            token=token,
        )


class ErrorInventarioRemotoYaExiste(ErrorPersistenciaGitHub):
    """Bloqueo de creación inicial cuando el archivo remoto `inventario.xlsx` ya existe en GitHub."""

    def __init__(
        self,
        mensaje: str = MENSAJE_ARCHIVO_REMOTO_YA_EXISTE,
        *,
        sha_remoto_actual: str | None = None,
        status_code: int | None = None,
        detalle_tecnico: str = "",
        token: str | None = None,
    ) -> None:
        super().__init__(
            mensaje,
            codigo=CodigoErrorPersistenciaGitHub.ARCHIVO_REMOTO_YA_EXISTE,
            estado_publicacion=EstadoResultadoPublicacionGitHub.CONFLICTO_ARCHIVO_REMOTO_EXISTENTE,
            status_code=status_code,
            es_reintentable=False,
            sha_remoto_actual=sha_remoto_actual,
            detalle_tecnico=detalle_tecnico,
            token=token,
        )


class ErrorCredencialesEscrituraGitHub(ErrorPersistenciaGitHub):
    """Fallo HTTP 401 o 403 por token inválido, expirado o sin permisos de escritura."""

    def __init__(
        self,
        mensaje: str = MENSAJE_ERROR_CREDENCIAL_ESCRITURA,
        *,
        codigo: CodigoErrorPersistenciaGitHub = CodigoErrorPersistenciaGitHub.CREDENCIAL_INVALIDA_O_SIN_PERMISO,
        status_code: int | None = None,
        detalle_tecnico: str = "",
        token: str | None = None,
    ) -> None:
        super().__init__(
            mensaje,
            codigo=codigo,
            estado_publicacion=EstadoResultadoPublicacionGitHub.ERROR_CREDENCIALES_O_PERMISOS,
            status_code=status_code,
            es_reintentable=False,
            detalle_tecnico=detalle_tecnico,
            token=token,
        )


class ErrorRepositorioORamaEscrituraGitHub(ErrorPersistenciaGitHub):
    """Fallo HTTP 404 por repositorio inaccesible o rama `main` inexistente durante la escritura."""

    def __init__(
        self,
        mensaje: str = MENSAJE_ERROR_REPOSITORIO_O_RAMA_ESCRITURA,
        *,
        status_code: int | None = 404,
        detalle_tecnico: str = "",
        token: str | None = None,
    ) -> None:
        super().__init__(
            mensaje,
            codigo=CodigoErrorPersistenciaGitHub.REPOSITORIO_O_RAMA_INEXISTENTE,
            estado_publicacion=EstadoResultadoPublicacionGitHub.ERROR_DESTINO_O_RAMA,
            status_code=status_code,
            es_reintentable=False,
            detalle_tecnico=detalle_tecnico,
            token=token,
        )


class ErrorLimiteSolicitudesEscrituraGitHub(ErrorPersistenciaGitHub):
    """Fallo HTTP 429 o 403 por agotamiento de cuota (rate limit) en GitHub API."""

    def __init__(
        self,
        mensaje: str = MENSAJE_ERROR_LIMITE_SOLICITUDES_ESCRITURA,
        *,
        status_code: int | None = 429,
        detalle_tecnico: str = "",
        token: str | None = None,
    ) -> None:
        super().__init__(
            mensaje,
            codigo=CodigoErrorPersistenciaGitHub.LIMITE_SOLICITUDES_AGOTADO,
            estado_publicacion=EstadoResultadoPublicacionGitHub.ERROR_LIMITE_SOLICITUDES,
            status_code=status_code,
            es_reintentable=True,
            detalle_tecnico=detalle_tecnico,
            token=token,
        )


class ErrorServidorEscrituraGitHub(ErrorPersistenciaGitHub):
    """Error temporal HTTP 5xx (500, 502, 503, 504) en los servidores de GitHub."""

    def __init__(
        self,
        mensaje: str = MENSAJE_ERROR_SERVIDOR_ESCRITURA,
        *,
        status_code: int | None = 500,
        detalle_tecnico: str = "",
        token: str | None = None,
    ) -> None:
        super().__init__(
            mensaje,
            codigo=CodigoErrorPersistenciaGitHub.ERROR_SERVIDOR_GITHUB,
            estado_publicacion=EstadoResultadoPublicacionGitHub.ERROR_SERVIDOR_GITHUB,
            status_code=status_code,
            es_reintentable=True,
            detalle_tecnico=detalle_tecnico,
            token=token,
        )


class ErrorRedOTimeoutEscrituraGitHub(ErrorPersistenciaGitHub):
    """Error de conexión de red o tiempo de espera agotado durante la persistencia en GitHub."""

    def __init__(
        self,
        mensaje: str = MENSAJE_ERROR_RED_ESCRITURA,
        *,
        codigo: CodigoErrorPersistenciaGitHub = CodigoErrorPersistenciaGitHub.CONEXION_RED_FALLIDA,
        detalle_tecnico: str = "",
        token: str | None = None,
    ) -> None:
        super().__init__(
            mensaje,
            codigo=codigo,
            estado_publicacion=EstadoResultadoPublicacionGitHub.ERROR_RED_O_TIMEOUT,
            status_code=None,
            es_reintentable=True,
            detalle_tecnico=detalle_tecnico,
            token=token,
        )


class ErrorRespuestaInesperadaEscrituraGitHub(ErrorPersistenciaGitHub):
    """Respuesta HTTP o JSON malformada o sin confirmación de nuevo `sha` tras `PUT`."""

    def __init__(
        self,
        mensaje: str = MENSAJE_ERROR_RESPUESTA_INESPERADA_ESCRITURA,
        *,
        status_code: int | None = None,
        detalle_tecnico: str = "",
        token: str | None = None,
    ) -> None:
        super().__init__(
            mensaje,
            codigo=CodigoErrorPersistenciaGitHub.RESPUESTA_INESPERADA_ESCRITURA,
            estado_publicacion=EstadoResultadoPublicacionGitHub.ERROR_RESPUESTA_INESPERADA,
            status_code=status_code,
            es_reintentable=False,
            detalle_tecnico=detalle_tecnico,
            token=token,
        )


class ErrorEscrituraRealNoAutorizadaGitHub(ErrorPersistenciaGitHub):
    """Bloqueo preventivo cuando se intenta ejecutar una solicitud HTTP PUT real no autorizada."""

    def __init__(
        self,
        mensaje: str = (
            "Las escrituras HTTP PUT reales hacia GitHub están deshabilitadas en este "
            "entorno mientras no se autorice expresamente su activación."
        ),
    ) -> None:
        super().__init__(
            mensaje,
            codigo=CodigoErrorPersistenciaGitHub.ESCRITURA_REAL_NO_AUTORIZADA,
            estado_publicacion=EstadoResultadoPublicacionGitHub.ERROR_AUTORIZACION_ADMIN,
            es_reintentable=False,
        )


class ErrorPublicacionDatosDemostrativosNoAutorizada(ErrorPersistenciaGitHub):
    """Bloqueo de seguridad cuando se intenta publicar datos demostrativos o una inicialización no autorizada."""

    def __init__(
        self,
        mensaje: str = MENSAJE_DATOS_DEMOSTRATIVOS_NO_PUBLICABLES,
        *,
        codigo: CodigoErrorPersistenciaGitHub = CodigoErrorPersistenciaGitHub.DATOS_DEMOSTRATIVOS_NO_PUBLICABLES,
        detalle_tecnico: str = "",
    ) -> None:
        super().__init__(
            mensaje,
            codigo=codigo,
            estado_publicacion=EstadoResultadoPublicacionGitHub.BLOQUEADO_DATOS_DEMOSTRATIVOS,
            es_reintentable=False,
            detalle_tecnico=detalle_tecnico,
        )


def _redactar_encabezados_representacion(encabezados: Mapping[str, str] | None) -> dict[str, str]:
    """Devuelve una copia segura de los encabezados HTTP redactando cualquier credencial o Authorization."""
    if not isinstance(encabezados, Mapping):
        return {}
    seguros: dict[str, str] = {}
    for k, v in encabezados.items():
        clave_str = str(k)
        if clave_str.strip().lower() in ("authorization", "proxy-authorization", "x-github-token", "cookie", "set-cookie"):
            seguros[clave_str] = f"Bearer {MARCA_SECRETO_OCULTO}"
        else:
            seguros[clave_str] = sanitizar_texto_persistencia(v)
    return seguros


@dataclass(frozen=True)
class PaqueteExcelVerificado:
    """Resultado inmutable de la serialización `.xlsx` en memoria y su verificación round-trip."""

    bytes_xlsx: bytes
    sha256_bytes: str
    tamano_bytes: int
    contenido_base64: str
    inventario_verificado: InventarioDatos
    hojas_verificadas: tuple[str, ...] = ORDEN_HOJAS

    def __repr__(self) -> str:
        return (
            f"PaqueteExcelVerificado(sha256_bytes={self.sha256_bytes!r}, "
            f"tamano_bytes={self.tamano_bytes}, "
            f"hojas_verificadas={self.hojas_verificadas!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()


@dataclass(frozen=True)
class SolicitudPutContentsGitHub:
    """Representación verificada de una solicitud `PUT` hacia GitHub Contents API."""

    url: str
    metodo: str
    encabezados: Mapping[str, str]
    payload: Mapping[str, Any]
    cuerpo_json_bytes: bytes
    modo_publicacion: ModoPublicacionGitHub
    sha_base_enviado: str | None
    sha256_excel: str
    tamano_excel_bytes: int

    def __repr__(self) -> str:
        encabezados_seguros = _redactar_encabezados_representacion(self.encabezados)
        payload_seguro = {
            k: ("<BASE64_EXCEL>" if k == "content" else sanitizar_texto_persistencia(v))
            for k, v in (self.payload.items() if isinstance(self.payload, Mapping) else ())
        }
        return (
            f"SolicitudPutContentsGitHub("
            f"url={sanitizar_texto_persistencia(self.url)!r}, "
            f"metodo={self.metodo!r}, "
            f"encabezados={encabezados_seguros!r}, "
            f"payload={payload_seguro!r}, "
            f"modo_publicacion={self.modo_publicacion.value!r}, "
            f"sha_base_enviado={self.sha_base_enviado!r}, "
            f"sha256_excel={self.sha256_excel!r}, "
            f"tamano_excel_bytes={self.tamano_excel_bytes})"
        )

    def __str__(self) -> str:
        return self.__repr__()


@dataclass(frozen=True)
class EstadoConflictoShaAdmin:
    """Detalle estructurado de un conflicto de versión SHA detectado antes o durante el guardado."""

    sha_base_local: str | None
    sha_remoto_detectado: str | None
    modo_publicacion: ModoPublicacionGitHub
    detectado_en: str
    mensaje_usuario: str
    detalle_tecnico: str = ""
    detectado_en_epoch: float = 0.0
    cambios_locales_preservados: bool = True

    def __repr__(self) -> str:
        return (
            f"EstadoConflictoShaAdmin("
            f"sha_base_local={self.sha_base_local!r}, "
            f"sha_remoto_detectado={self.sha_remoto_detectado!r}, "
            f"modo_publicacion={self.modo_publicacion.value!r}, "
            f"detectado_en={self.detectado_en!r}, "
            f"mensaje_usuario={sanitizar_texto_persistencia(self.mensaje_usuario)!r}, "
            f"detalle_tecnico={sanitizar_texto_persistencia(self.detalle_tecnico)!r}, "
            f"cambios_locales_preservados={self.cambios_locales_preservados})"
        )

    def __str__(self) -> str:
        return self.__repr__()


@dataclass(frozen=True)
class ResultadoPublicacionGitHub:
    """Resultado estructurado de una operación de persistencia del inventario en GitHub."""

    exito: bool
    confirmado_en_github: bool
    estado: EstadoResultadoPublicacionGitHub
    modo_publicacion: ModoPublicacionGitHub
    mensaje_usuario: str
    detalle_tecnico: str = ""
    codigo_error: CodigoErrorPersistenciaGitHub | None = None
    sha_anterior: str | None = None
    nuevo_sha_archivo: str | None = None
    sha_commit: str | None = None
    sha256_bytes: str | None = None
    tamano_bytes: int = 0
    codigos_productos_creados: tuple[str, ...] = ()
    codigos_productos_editados: tuple[str, ...] = ()
    total_operaciones_publicadas: int = 0
    conflicto_sha: EstadoConflictoShaAdmin | None = None
    permite_reintentar: bool = False
    permite_recargar_remoto: bool = False
    cambios_locales_preservados: bool = True
    huella_operacion: str | None = None

    def __repr__(self) -> str:
        return (
            f"ResultadoPublicacionGitHub("
            f"exito={self.exito}, "
            f"confirmado_en_github={self.confirmado_en_github}, "
            f"estado={self.estado.value!r}, "
            f"modo_publicacion={self.modo_publicacion.value!r}, "
            f"mensaje_usuario={sanitizar_texto_persistencia(self.mensaje_usuario)!r}, "
            f"detalle_tecnico={sanitizar_texto_persistencia(self.detalle_tecnico)!r}, "
            f"codigo_error={self.codigo_error.value if self.codigo_error else None!r}, "
            f"nuevo_sha_archivo={self.nuevo_sha_archivo!r}, "
            f"sha_commit={self.sha_commit!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()


EjecutorHTTPPut = Callable[[str, Mapping[str, str], bytes, float], RespuestaHTTPGitHub]
ConsultorExistenciaRemota = Callable[..., ResultadoExistenciaRemota]


def verificar_inventario_autorizado_para_publicacion(
    inventario: InventarioDatos,
    *,
    modo_publicacion: ModoPublicacionGitHub | None = None,
    espacio_trabajo: EspacioTrabajoAdminInventario | None = None,
    requerir_autorizacion_inicializacion_oficial: bool = False,
) -> None:
    """Verifica que el inventario no contenga datos demostrativos y que toda creación inicial esté autorizada.

    Cumple la Corrección 2 de auditoría P10:
    1. Rechaza cualquier `InventarioDatos` marcado con `es_demostrativo=True` o que contenga marcas
       `[DEMOSTRATIVO]` o `(Demostrativo)` en sus productos o categorías.
    2. Rechaza cualquier `EspacioTrabajoAdminInventario` con `es_copia_demostrativa=True` o cuyo
       `inventario_original` o `inventario_trabajo` provenga de datos de demostración.
    3. En `ModoPublicacionGitHub.CREACION_INICIAL_ARCHIVO_NUEVO`, exige que el espacio de trabajo
       cuente explícitamente con `inicializacion_oficial_autorizada=True` y `es_copia_demostrativa=False`.
    """
    if not isinstance(inventario, InventarioDatos):
        raise ErrorSerializacionInventarioPersistente(
            "El objeto proporcionado no es una instancia válida de InventarioDatos.",
            codigo=CodigoErrorPersistenciaGitHub.SERIALIZACION_INVALIDA,
        )

    es_demo_inv = contiene_datos_demostrativos(inventario)
    es_demo_espacio = False
    if espacio_trabajo is not None:
        es_demo_espacio = (
            bool(getattr(espacio_trabajo, "es_copia_demostrativa", False))
            or contiene_datos_demostrativos(espacio_trabajo.inventario_original)
            or contiene_datos_demostrativos(espacio_trabajo.inventario_trabajo)
        )

    if es_demo_inv or es_demo_espacio:
        raise ErrorPublicacionDatosDemostrativosNoAutorizada(
            MENSAJE_DATOS_DEMOSTRATIVOS_NO_PUBLICABLES,
            codigo=CodigoErrorPersistenciaGitHub.DATOS_DEMOSTRATIVOS_NO_PUBLICABLES,
            detalle_tecnico=(
                "Se rechazó la publicación porque el inventario o el espacio de trabajo contiene "
                "datos demostrativos ([DEMOSTRATIVO]) reservados exclusivamente para uso local en memoria."
            ),
        )

    if modo_publicacion == ModoPublicacionGitHub.CREACION_INICIAL_ARCHIVO_NUEVO and (
        requerir_autorizacion_inicializacion_oficial or espacio_trabajo is not None
    ):
        autorizado_init = (
            espacio_trabajo is not None
            and getattr(espacio_trabajo, "inicializacion_oficial_autorizada", False) is True
            and getattr(espacio_trabajo, "es_copia_demostrativa", False) is False
        )
        if not autorizado_init:
            raise ErrorPublicacionDatosDemostrativosNoAutorizada(
                MENSAJE_INICIALIZACION_OFICIAL_NO_AUTORIZADA,
                codigo=CodigoErrorPersistenciaGitHub.INICIALIZACION_OFICIAL_NO_AUTORIZADA,
                detalle_tecnico=(
                    "Se rechazó la creación inicial porque el espacio de trabajo no posee "
                    "autorización explícita de inicialización oficial ('inicializacion_oficial_autorizada=True')."
                ),
            )


def serializar_y_verificar_inventario_xlsx(
    inventario: InventarioDatos,
    *,
    lector_roundtrip: Callable[[bytes], InventarioDatos] | None = None,
) -> PaqueteExcelVerificado:
    """Serializa `InventarioDatos` a `.xlsx` en memoria y verifica su lectura round-trip íntegra.

    Cumple la Sección 6 del Prompt 10 (RF-023, RF-024, RF-025, CA-017, CA-018, CA-022):
    1. Verifica que la entrada sea un `InventarioDatos` válido sin mutar los DataFrames originales.
    2. Valida las cuatro hojas (`Productos`, `Categorías`, `Ubicaciones`, `Asignaciones`), el
       orden exacto de columnas, la unicidad de códigos, la integridad referencial y la regla
       de exactamente una ubicación principal por producto.
    3. Genera los bytes `.xlsx` en memoria (`BytesIO`) preservando los textos y ceros iniciales.
    4. Relee los bytes producidos mediante `cargar_inventario_excel()` (verificación round-trip)
       y comprueba que el inventario reconstruido sea idéntico al inventario de entrada.
    5. Verifica la codificación Base64 sin corrupción binaria.
    """
    if not isinstance(inventario, InventarioDatos):
        raise ErrorSerializacionInventarioPersistente(
            "El objeto proporcionado para serialización no es una instancia válida de InventarioDatos.",
            codigo=CodigoErrorPersistenciaGitHub.SERIALIZACION_INVALIDA,
        )

    try:
        copia_aislada = clonar_inventario_datos(inventario)
        hojas_copia = copia_aislada.obtener_hojas()
        validar_inventario(hojas_copia, lanzar_excepcion=True)
        inventario_validado = construir_inventario_datos(hojas_copia)
    except (ErrorInventario, ErrorAdministracionInventario, Exception) as exc_val:
        raise ErrorSerializacionInventarioPersistente(
            f"El inventario contiene errores de esquema o integridad y no puede serializarse: {exc_val}",
            codigo=CodigoErrorPersistenciaGitHub.SERIALIZACION_INVALIDA,
            detalle_tecnico=str(exc_val),
        ) from exc_val

    try:
        bytes_xlsx = serializar_inventario_a_bytes(inventario_validado)
    except Exception as exc_ser:
        raise ErrorSerializacionInventarioPersistente(
            f"Error al generar los bytes del archivo Excel en memoria: {exc_ser}",
            codigo=CodigoErrorPersistenciaGitHub.SERIALIZACION_INVALIDA,
            detalle_tecnico=str(exc_ser),
        ) from exc_ser

    if not isinstance(bytes_xlsx, bytes) or len(bytes_xlsx) == 0:
        raise ErrorSerializacionInventarioPersistente(
            "La serialización del inventario produjo un contenido binario vacío o inválido.",
            codigo=CodigoErrorPersistenciaGitHub.SERIALIZACION_INVALIDA,
        )

    # Verificación obligatoria de ida y vuelta (round-trip) en memoria
    funcion_lectura = lector_roundtrip or cargar_inventario_excel
    try:
        inventario_releido = funcion_lectura(bytes_xlsx)
    except Exception as exc_rt:
        raise ErrorSerializacionInventarioPersistente(
            f"Fallo en la verificación round-trip al releer los bytes Excel generados: {exc_rt}",
            codigo=CodigoErrorPersistenciaGitHub.VERIFICACION_ROUNDTRIP_FALLIDA,
            detalle_tecnico=str(exc_rt),
        ) from exc_rt

    if not isinstance(inventario_releido, InventarioDatos):
        raise ErrorSerializacionInventarioPersistente(
            "La verificación round-trip no devolvió un objeto InventarioDatos válido.",
            codigo=CodigoErrorPersistenciaGitHub.VERIFICACION_ROUNDTRIP_FALLIDA,
        )

    hojas_releidas = inventario_releido.obtener_hojas()
    if tuple(hojas_releidas.keys()) != ORDEN_HOJAS:
        raise ErrorSerializacionInventarioPersistente(
            "Las hojas del archivo Excel releído no coinciden con las cuatro hojas oficiales.",
            codigo=CodigoErrorPersistenciaGitHub.VERIFICACION_ROUNDTRIP_FALLIDA,
        )

    for nombre_hoja in ORDEN_HOJAS:
        columnas_esperadas = tuple(ESQUEMA_COLUMNAS[nombre_hoja])
        columnas_actuales = tuple(hojas_releidas[nombre_hoja].columns)
        if columnas_actuales != columnas_esperadas:
            raise ErrorSerializacionInventarioPersistente(
                f"El orden de columnas en la hoja '{nombre_hoja}' ({columnas_actuales}) "
                f"no coincide con el esquema oficial ({columnas_esperadas}).",
                codigo=CodigoErrorPersistenciaGitHub.VERIFICACION_ROUNDTRIP_FALLIDA,
            )

    if not inventarios_son_identicos(inventario_validado, inventario_releido):
        raise ErrorSerializacionInventarioPersistente(
            "La verificación round-trip detectó diferencias entre el inventario a persistir "
            "y el inventario reconstruido desde los bytes Excel.",
            codigo=CodigoErrorPersistenciaGitHub.VERIFICACION_ROUNDTRIP_FALLIDA,
        )

    contenido_b64 = base64.b64encode(bytes_xlsx).decode("ascii")
    try:
        decodificado = base64.b64decode(contenido_b64, validate=True)
    except (binascii.Error, ValueError) as exc_b64:
        raise ErrorSerializacionInventarioPersistente(
            "Error al verificar la codificación Base64 del archivo Excel.",
            codigo=CodigoErrorPersistenciaGitHub.SERIALIZACION_INVALIDA,
            detalle_tecnico=str(exc_b64),
        ) from exc_b64

    if decodificado != bytes_xlsx:
        raise ErrorSerializacionInventarioPersistente(
            "Los bytes decodificados desde Base64 no coinciden exactamente con los bytes Excel generados.",
            codigo=CodigoErrorPersistenciaGitHub.SERIALIZACION_INVALIDA,
        )

    sha256_hex = hashlib.sha256(bytes_xlsx).hexdigest()
    return PaqueteExcelVerificado(
        bytes_xlsx=bytes_xlsx,
        sha256_bytes=sha256_hex,
        tamano_bytes=len(bytes_xlsx),
        contenido_base64=contenido_b64,
        inventario_verificado=inventario_releido,
        hojas_verificadas=ORDEN_HOJAS,
    )


def validar_destino_escritura_github(
    config: ConfiguracionRepositorioGitHub = CONFIGURACION_POR_DEFECTO,
) -> str:
    """Verifica que el destino de escritura coincida exactamente con el repositorio, rama y ruta oficiales.

    Bloquea cualquier intento de escribir en otro propietario, repositorio, rama distinta de `main`,
    ruta distinta de `03_Aplicacion/inventario.xlsx` o URL fuera de `https://api.github.com`.
    """
    if not isinstance(config, ConfiguracionRepositorioGitHub):
        raise ErrorDestinoEscrituraNoAutorizadoGitHub(
            MENSAJE_ERROR_DESTINO_ESCRITURA,
            detalle_tecnico="Configuración de repositorio inválida.",
        )

    propietario = (config.propietario or "").strip()
    repositorio = (config.repositorio or "").strip()
    rama = (config.rama or "").strip()
    ruta_archivo = (config.ruta_archivo or "").strip().lstrip("/")
    url_base = (config.url_base_api or "").strip().rstrip("/")

    if (
        propietario != PROPIETARIO_POR_DEFECTO
        or repositorio != REPOSITORIO_POR_DEFECTO
        or rama != RAMA_POR_DEFECTO
        or ruta_archivo != RUTA_ARCHIVO_POR_DEFECTO
        or url_base != URL_BASE_API_GITHUB
    ):
        raise ErrorDestinoEscrituraNoAutorizadoGitHub(
            MENSAJE_ERROR_DESTINO_ESCRITURA,
            detalle_tecnico=(
                f"Destino rechazado: repo='{propietario}/{repositorio}', "
                f"rama='{rama}', ruta='{ruta_archivo}', base='{url_base}'."
            ),
        )

    url_escritura = (
        f"{URL_BASE_API_GITHUB}/repos/{PROPIETARIO_POR_DEFECTO}/"
        f"{REPOSITORIO_POR_DEFECTO}/contents/{RUTA_ARCHIVO_POR_DEFECTO}"
    )
    try:
        validar_url_solicitud_github(
            url_escritura,
            config=config,
            contexto="escritura en GitHub Contents API",
        )
    except ErrorLecturaGitHub as exc_url:
        raise ErrorDestinoEscrituraNoAutorizadoGitHub(
            MENSAJE_ERROR_DESTINO_ESCRITURA,
            detalle_tecnico=exc_url.mensaje,
        ) from exc_url

    return url_escritura


def _resolver_token_escritura_github(
    *,
    token: str | None = None,
    fuente_secretos: Mapping[str, Any] | None = None,
    fuente_entorno: Mapping[str, str] | None = None,
) -> str | None:
    """Resuelve el token de escritura desde argumento explícito, secretos, entorno o `github_inventario`."""
    if token is not None:
        return obtener_token_configurado(token_explicito=token)

    if isinstance(fuente_secretos, Mapping):
        for clave in ("FERRETERIAMS_GITHUB_TOKEN", "GITHUB_TOKEN", "github_token"):
            val = fuente_secretos.get(clave)
            if isinstance(val, str) and val.strip():
                return obtener_token_configurado(token_explicito=val.strip())
        bloque_gh = fuente_secretos.get("github")
        if isinstance(bloque_gh, Mapping):
            val_tok = bloque_gh.get("token")
            if isinstance(val_tok, str) and val_tok.strip():
                return obtener_token_configurado(token_explicito=val_tok.strip())

    if isinstance(fuente_entorno, Mapping):
        for clave in ("FERRETERIAMS_GITHUB_TOKEN", "GITHUB_TOKEN"):
            val_env = fuente_entorno.get(clave)
            if isinstance(val_env, str) and val_env.strip():
                return obtener_token_configurado(token_explicito=val_env.strip())

    return obtener_token_configurado()


def construir_encabezados_escritura_github(token: str) -> dict[str, str]:
    """Construye los encabezados HTTP obligatorios para escritura autenticada en GitHub Contents API."""
    token_limpio = (token or "").strip()
    if not token_limpio:
        raise ErrorTokenEscrituraFaltanteGitHub()

    return {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": VERSION_API_GITHUB,
        "User-Agent": "FerreteriaMS-v0",
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Authorization": f"Bearer {token_limpio}",
    }


def construir_solicitud_put_contents_github(
    inventario: InventarioDatos,
    *,
    modo_publicacion: ModoPublicacionGitHub,
    sha_base_remoto: str | None = None,
    mensaje_commit: str | None = None,
    token: str | None = None,
    fuente_secretos: Mapping[str, Any] | None = None,
    fuente_entorno: Mapping[str, str] | None = None,
    config: ConfiguracionRepositorioGitHub = CONFIGURACION_POR_DEFECTO,
    lector_roundtrip: Callable[[bytes], InventarioDatos] | None = None,
) -> tuple[SolicitudPutContentsGitHub, PaqueteExcelVerificado]:
    """Construye y valida la solicitud `PUT` completa para GitHub Contents API."""
    url_destino = validar_destino_escritura_github(config)

    try:
        token_resuelto = _resolver_token_escritura_github(
            token=token,
            fuente_secretos=fuente_secretos,
            fuente_entorno=fuente_entorno,
        )
    except ErrorLecturaGitHub as exc_tok:
        raise ErrorCredencialesEscrituraGitHub(
            MENSAJE_ERROR_CREDENCIAL_ESCRITURA,
            detalle_tecnico=exc_tok.mensaje,
        ) from exc_tok

    if not token_resuelto:
        raise ErrorTokenEscrituraFaltanteGitHub()

    if not isinstance(modo_publicacion, ModoPublicacionGitHub):
        raise ErrorPersistenciaGitHub(
            "El modo de publicación especificado no es válido.",
            codigo=CodigoErrorPersistenciaGitHub.RESPUESTA_INESPERADA_ESCRITURA,
        )

    sha_limpio: str | None = None
    if modo_publicacion == ModoPublicacionGitHub.ACTUALIZACION_ARCHIVO_EXISTENTE:
        if not isinstance(sha_base_remoto, str) or not sha_base_remoto.strip():
            raise ErrorShaBaseFaltanteGitHub(
                "Se requiere el SHA vigente del archivo remoto ('sha_base_remoto') "
                "para actualizar '03_Aplicacion/inventario.xlsx' en GitHub."
            )
        sha_limpio = sha_base_remoto.strip()
    elif modo_publicacion == ModoPublicacionGitHub.CREACION_INICIAL_ARCHIVO_NUEVO:
        if isinstance(sha_base_remoto, str) and sha_base_remoto.strip():
            raise ErrorInventarioRemotoYaExiste(
                MENSAJE_ARCHIVO_REMOTO_YA_EXISTE,
                sha_remoto_actual=sha_base_remoto.strip(),
            )

    verificar_inventario_autorizado_para_publicacion(
        inventario,
        modo_publicacion=modo_publicacion,
    )

    paquete_excel = serializar_y_verificar_inventario_xlsx(
        inventario,
        lector_roundtrip=lector_roundtrip,
    )

    mensaje_limpio = (mensaje_commit or "").strip()
    if not mensaje_limpio:
        mensaje_limpio = (
            MENSAJE_COMMIT_ACTUALIZACION_DEFECTO
            if modo_publicacion == ModoPublicacionGitHub.ACTUALIZACION_ARCHIVO_EXISTENTE
            else MENSAJE_COMMIT_INICIALIZACION_DEFECTO
        )

    payload: dict[str, Any] = {
        "message": mensaje_limpio,
        "content": paquete_excel.contenido_base64,
        "branch": config.rama.strip(),
    }
    if (
        modo_publicacion == ModoPublicacionGitHub.ACTUALIZACION_ARCHIVO_EXISTENTE
        and sha_limpio is not None
    ):
        payload["sha"] = sha_limpio

    cuerpo_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    encabezados = construir_encabezados_escritura_github(token_resuelto)

    solicitud = SolicitudPutContentsGitHub(
        url=url_destino,
        metodo="PUT",
        encabezados=encabezados,
        payload=payload,
        cuerpo_json_bytes=cuerpo_bytes,
        modo_publicacion=modo_publicacion,
        sha_base_enviado=sha_limpio,
        sha256_excel=paquete_excel.sha256_bytes,
        tamano_excel_bytes=paquete_excel.tamano_bytes,
    )
    return solicitud, paquete_excel


def _ExtraerMensajeJsonSeguro(
    cuerpo: bytes,
    *,
    token: str | None = None,
) -> str:
    """Extrae el campo `message` de una respuesta JSON de GitHub sanitizando cualquier secreto."""
    if not cuerpo:
        return "Sin detalle adicional en el cuerpo HTTP."
    try:
        datos = json.loads(cuerpo.decode("utf-8", errors="replace"))
        if isinstance(datos, dict) and isinstance(datos.get("message"), str):
            return sanitizar_texto_persistencia(datos["message"], token=token)
    except Exception:
        pass
    texto = cuerpo.decode("utf-8", errors="replace").strip()[:280]
    return sanitizar_texto_persistencia(texto, token=token)


def ejecutar_solicitud_put_github(
    url: str,
    encabezados: Mapping[str, str],
    cuerpo_json_bytes: bytes,
    timeout: float = TIMEOUT_ESCRITURA_POR_DEFECTO,
) -> RespuestaHTTPGitHub:
    """Ejecuta una solicitud HTTP `PUT` real hacia GitHub Contents API con protección de transporte y credenciales.

    Compuerta incondicional (Corrección 1 de auditoría P10):
    Mientras `ESCRITURA_REAL_GITHUB_HABILITADA` no sea `True`, esta función rechaza de manera
    absoluta cualquier ejecución y lanza `ErrorEscrituraRealNoAutorizadaGitHub` antes de construir
    o abrir ninguna conexión de red. Ningún parámetro público permite anular esta prohibición.
    """
    token_en_encabezado: str | None = None
    for k, v in encabezados.items():
        if k.lower() == "authorization" and isinstance(v, str):
            partes = v.strip().split(" ", 1)
            token_en_encabezado = partes[1].strip() if len(partes) == 2 else v.strip()
            break

    if not token_en_encabezado:
        raise ErrorTokenEscrituraFaltanteGitHub()

    try:
        validar_url_solicitud_github(
            url,
            encabezados=encabezados,
            token=token_en_encabezado,
            contexto="escritura en GitHub Contents API",
        )
    except ErrorLecturaGitHub as exc_url:
        raise ErrorDestinoEscrituraNoAutorizadoGitHub(
            MENSAJE_ERROR_DESTINO_ESCRITURA,
            detalle_tecnico=exc_url.mensaje,
        ) from exc_url

    if not isinstance(cuerpo_json_bytes, bytes) or len(cuerpo_json_bytes) == 0:
        raise ErrorSerializacionInventarioPersistente(
            "El cuerpo JSON de la solicitud PUT no puede estar vacío.",
            codigo=CodigoErrorPersistenciaGitHub.SERIALIZACION_INVALIDA,
        )

    if ESCRITURA_REAL_GITHUB_HABILITADA is not True:
        raise ErrorEscrituraRealNoAutorizadaGitHub()

    solicitud = urllib.request.Request(
        url=url,
        data=cuerpo_json_bytes,
        headers=dict(encabezados),
        method="PUT",
    )

    try:
        opener = urllib.request.build_opener(
            _ManejadorRedireccionSeguraGitHub(token=token_en_encabezado)
        )
        contexto_respuesta = opener.open(solicitud, timeout=timeout)

        with contexto_respuesta as respuesta:
            status_code = int(
                getattr(respuesta, "status", None) or respuesta.getcode() or 200
            )
            cuerpo = respuesta.read()
            headers_resp = (
                {k: v for k, v in respuesta.headers.items()}
                if getattr(respuesta, "headers", None)
                else {}
            )
            url_final = str(getattr(respuesta, "url", None) or url)
            validar_url_solicitud_github(
                url_final,
                encabezados=encabezados,
                token=token_en_encabezado,
                contexto="respuesta de escritura en GitHub Contents API",
            )
            return RespuestaHTTPGitHub(
                status_code=status_code,
                cuerpo=cuerpo,
                encabezados=headers_resp,
                url=url_final,
            )
    except urllib.error.HTTPError as exc_http:
        cuerpo_error = b""
        try:
            cuerpo_error = exc_http.read()
        except Exception:
            pass
        headers_err = (
            {k: v for k, v in exc_http.headers.items()}
            if getattr(exc_http, "headers", None)
            else {}
        )
        return RespuestaHTTPGitHub(
            status_code=int(exc_http.code),
            cuerpo=cuerpo_error,
            encabezados=headers_err,
            url=url,
        )
    except (TimeoutError, socket.timeout) as exc_timeout:
        raise ErrorRedOTimeoutEscrituraGitHub(
            MENSAJE_ERROR_RED_ESCRITURA,
            codigo=CodigoErrorPersistenciaGitHub.TIEMPO_ESPERA_AGOTADO,
            detalle_tecnico="Tiempo de espera agotado durante la solicitud PUT a GitHub.",
            token=token_en_encabezado,
        ) from exc_timeout
    except urllib.error.URLError as exc_url_err:
        razon = getattr(exc_url_err, "reason", exc_url_err)
        if isinstance(razon, (TimeoutError, socket.timeout)):
            raise ErrorRedOTimeoutEscrituraGitHub(
                MENSAJE_ERROR_RED_ESCRITURA,
                codigo=CodigoErrorPersistenciaGitHub.TIEMPO_ESPERA_AGOTADO,
                detalle_tecnico="Tiempo de espera agotado al conectar con GitHub API.",
                token=token_en_encabezado,
            ) from exc_url_err
        raise ErrorRedOTimeoutEscrituraGitHub(
            MENSAJE_ERROR_RED_ESCRITURA,
            codigo=CodigoErrorPersistenciaGitHub.CONEXION_RED_FALLIDA,
            detalle_tecnico=sanitizar_texto_persistencia(
                str(razon), token=token_en_encabezado
            ),
            token=token_en_encabezado,
        ) from exc_url_err
    except ErrorPersistenciaGitHub:
        raise
    except ErrorLecturaGitHub as exc_lectura:
        raise ErrorRespuestaInesperadaEscrituraGitHub(
            MENSAJE_ERROR_RESPUESTA_INESPERADA_ESCRITURA,
            detalle_tecnico=exc_lectura.mensaje,
            token=token_en_encabezado,
        ) from exc_lectura
    except OSError as exc_os:
        raise ErrorRedOTimeoutEscrituraGitHub(
            MENSAJE_ERROR_RED_ESCRITURA,
            codigo=CodigoErrorPersistenciaGitHub.CONEXION_RED_FALLIDA,
            detalle_tecnico=sanitizar_texto_persistencia(
                str(exc_os), token=token_en_encabezado
            ),
            token=token_en_encabezado,
        ) from exc_os


def interpretar_respuesta_put_github(
    respuesta: RespuestaHTTPGitHub,
    *,
    modo_publicacion: ModoPublicacionGitHub,
    sha_base_enviado: str | None = None,
    token: str | None = None,
) -> tuple[str, str]:
    """Valida la respuesta HTTP de `PUT /repos/{owner}/{repo}/contents/{path}` y extrae `(nuevo_sha_archivo, sha_commit)`.

    Nunca declara éxito si el código HTTP no es `200`/`201` o si el JSON devuelto carece de
    `content.sha` y `commit.sha` válidos.
    """
    if not isinstance(respuesta, RespuestaHTTPGitHub):
        raise ErrorRespuestaInesperadaEscrituraGitHub(
            MENSAJE_ERROR_RESPUESTA_INESPERADA_ESCRITURA,
            detalle_tecnico="Respuesta HTTP inválida.",
            token=token,
        )

    status = int(respuesta.status_code)
    detalle_api = _ExtraerMensajeJsonSeguro(respuesta.cuerpo, token=token)
    detalle_lower = detalle_api.lower()

    if status in (200, 201):
        try:
            datos = json.loads(respuesta.cuerpo.decode("utf-8"))
        except Exception as exc_json:
            raise ErrorRespuestaInesperadaEscrituraGitHub(
                MENSAJE_ERROR_RESPUESTA_INESPERADA_ESCRITURA,
                status_code=status,
                detalle_tecnico="El cuerpo de la respuesta 200/201 no es JSON válido.",
                token=token,
            ) from exc_json

        if not isinstance(datos, dict):
            raise ErrorRespuestaInesperadaEscrituraGitHub(
                MENSAJE_ERROR_RESPUESTA_INESPERADA_ESCRITURA,
                status_code=status,
                detalle_tecnico="La respuesta JSON de escritura no es un objeto.",
                token=token,
            )

        bloque_content = datos.get("content")
        bloque_commit = datos.get("commit")
        if not isinstance(bloque_content, dict) or not isinstance(bloque_commit, dict):
            raise ErrorRespuestaInesperadaEscrituraGitHub(
                MENSAJE_ERROR_RESPUESTA_INESPERADA_ESCRITURA,
                status_code=status,
                detalle_tecnico="La respuesta JSON carece de los objetos 'content' o 'commit'.",
                token=token,
            )

        nuevo_sha_archivo = str(bloque_content.get("sha") or "").strip()
        sha_commit = str(bloque_commit.get("sha") or "").strip()
        if not nuevo_sha_archivo or not sha_commit:
            raise ErrorRespuestaInesperadaEscrituraGitHub(
                MENSAJE_ERROR_RESPUESTA_INESPERADA_ESCRITURA,
                status_code=status,
                detalle_tecnico="La respuesta de GitHub no incluyó un SHA válido para el archivo o el commit.",
                token=token,
            )

        ruta_confirmada = str(bloque_content.get("path") or "").strip().lstrip("/")
        if ruta_confirmada and ruta_confirmada != RUTA_ARCHIVO_POR_DEFECTO:
            raise ErrorRespuestaInesperadaEscrituraGitHub(
                MENSAJE_ERROR_RESPUESTA_INESPERADA_ESCRITURA,
                status_code=status,
                detalle_tecnico=(
                    f"La ruta devuelta en content.path ('{ruta_confirmada}') no coincide "
                    f"con '{RUTA_ARCHIVO_POR_DEFECTO}'."
                ),
                token=token,
            )

        return nuevo_sha_archivo, sha_commit

    if status == 409:
        raise ErrorConflictoVersionShaGitHub(
            MENSAJE_CONFLICTO_SHA_DETECTADO,
            sha_base_local=sha_base_enviado,
            status_code=409,
            detalle_tecnico=f"HTTP 409 Conflict en GitHub API: {detalle_api}",
            token=token,
        )

    if status == 422:
        if (
            modo_publicacion == ModoPublicacionGitHub.CREACION_INICIAL_ARCHIVO_NUEVO
            and ("sha" in detalle_lower or "already exists" in detalle_lower)
        ):
            raise ErrorInventarioRemotoYaExiste(
                MENSAJE_ARCHIVO_REMOTO_YA_EXISTE,
                status_code=422,
                detalle_tecnico=f"HTTP 422 al intentar crear archivo ya existente: {detalle_api}",
                token=token,
            )
        raise ErrorConflictoVersionShaGitHub(
            MENSAJE_CONFLICTO_SHA_DETECTADO,
            sha_base_local=sha_base_enviado,
            status_code=422,
            detalle_tecnico=f"HTTP 422 por conflicto o desajuste de SHA en GitHub API: {detalle_api}",
            token=token,
        )

    if status == 401:
        raise ErrorCredencialesEscrituraGitHub(
            MENSAJE_ERROR_CREDENCIAL_ESCRITURA,
            codigo=CodigoErrorPersistenciaGitHub.CREDENCIAL_INVALIDA_O_SIN_PERMISO,
            status_code=401,
            detalle_tecnico=f"HTTP 401 Unauthorized: {detalle_api}",
            token=token,
        )

    if status == 403:
        restante = respuesta.obtener_encabezado("x-ratelimit-remaining")
        if (
            restante == "0"
            or "rate limit" in detalle_lower
            or "secondary rate limit" in detalle_lower
        ):
            raise ErrorLimiteSolicitudesEscrituraGitHub(
                MENSAJE_ERROR_LIMITE_SOLICITUDES_ESCRITURA,
                status_code=403,
                detalle_tecnico=f"HTTP 403 Rate Limit: {detalle_api}",
                token=token,
            )
        if any(
            ind in detalle_lower
            for ind in (
                "personal access token",
                "bad credentials",
                "resource not accessible",
                "permission",
                "write",
                "scope",
            )
        ):
            raise ErrorCredencialesEscrituraGitHub(
                MENSAJE_ERROR_CREDENCIAL_ESCRITURA,
                codigo=CodigoErrorPersistenciaGitHub.CREDENCIAL_INVALIDA_O_SIN_PERMISO,
                status_code=403,
                detalle_tecnico=f"HTTP 403 Permisos insuficientes del token: {detalle_api}",
                token=token,
            )
        raise ErrorCredencialesEscrituraGitHub(
            MENSAJE_ERROR_CREDENCIAL_ESCRITURA,
            codigo=CodigoErrorPersistenciaGitHub.ACCESO_DENEGADO_ESCRITURA,
            status_code=403,
            detalle_tecnico=f"HTTP 403 Forbidden: {detalle_api}",
            token=token,
        )

    if status == 404:
        raise ErrorRepositorioORamaEscrituraGitHub(
            MENSAJE_ERROR_REPOSITORIO_O_RAMA_ESCRITURA,
            status_code=404,
            detalle_tecnico=f"HTTP 404 en escritura (repositorio, rama o permisos): {detalle_api}",
            token=token,
        )

    if status == 429:
        raise ErrorLimiteSolicitudesEscrituraGitHub(
            MENSAJE_ERROR_LIMITE_SOLICITUDES_ESCRITURA,
            status_code=429,
            detalle_tecnico=f"HTTP 429 Too Many Requests: {detalle_api}",
            token=token,
        )

    if status >= 500:
        raise ErrorServidorEscrituraGitHub(
            MENSAJE_ERROR_SERVIDOR_ESCRITURA,
            status_code=status,
            detalle_tecnico=f"HTTP {status} Server Error: {detalle_api}",
            token=token,
        )

    raise ErrorRespuestaInesperadaEscrituraGitHub(
        MENSAJE_ERROR_RESPUESTA_INESPERADA_ESCRITURA,
        status_code=status,
        detalle_tecnico=f"HTTP {status}: {detalle_api}",
        token=token,
    )


def _mapear_error_existencia_remota(
    existencia: ResultadoExistenciaRemota,
    *,
    token: str | None = None,
) -> ErrorPersistenciaGitHub:
    """Traduce un fallo en la consulta previa de existencia (`DESCONOCIDO_ERROR`) a una excepción tipada."""
    cod = existencia.codigo_error
    detalle = sanitizar_texto_persistencia(existencia.mensaje, token=token)

    if cod == CodigoErrorGitHub.CREDENCIAL_INVALIDA:
        return ErrorCredencialesEscrituraGitHub(
            MENSAJE_ERROR_CREDENCIAL_ESCRITURA,
            codigo=CodigoErrorPersistenciaGitHub.CREDENCIAL_INVALIDA_O_SIN_PERMISO,
            status_code=401,
            detalle_tecnico=detalle,
            token=token,
        )
    if cod == CodigoErrorGitHub.ACCESO_DENEGADO:
        return ErrorCredencialesEscrituraGitHub(
            MENSAJE_ERROR_CREDENCIAL_ESCRITURA,
            codigo=CodigoErrorPersistenciaGitHub.ACCESO_DENEGADO_ESCRITURA,
            status_code=403,
            detalle_tecnico=detalle,
            token=token,
        )
    if cod in (
        CodigoErrorGitHub.REPOSITORIO_INACCESIBLE,
        CodigoErrorGitHub.RAMA_INEXISTENTE,
    ):
        return ErrorRepositorioORamaEscrituraGitHub(
            MENSAJE_ERROR_REPOSITORIO_O_RAMA_ESCRITURA,
            status_code=404,
            detalle_tecnico=detalle,
            token=token,
        )
    if cod == CodigoErrorGitHub.LIMITE_SOLICITUDES:
        return ErrorLimiteSolicitudesEscrituraGitHub(
            MENSAJE_ERROR_LIMITE_SOLICITUDES_ESCRITURA,
            status_code=429,
            detalle_tecnico=detalle,
            token=token,
        )
    if cod == CodigoErrorGitHub.ERROR_SERVIDOR:
        return ErrorServidorEscrituraGitHub(
            MENSAJE_ERROR_SERVIDOR_ESCRITURA,
            status_code=503,
            detalle_tecnico=detalle,
            token=token,
        )
    if cod == CodigoErrorGitHub.TIEMPO_ESPERA_AGOTADO:
        return ErrorRedOTimeoutEscrituraGitHub(
            MENSAJE_ERROR_RED_ESCRITURA,
            codigo=CodigoErrorPersistenciaGitHub.TIEMPO_ESPERA_AGOTADO,
            detalle_tecnico=detalle,
            token=token,
        )
    if cod == CodigoErrorGitHub.CONEXION_RED_FALLIDA:
        return ErrorRedOTimeoutEscrituraGitHub(
            MENSAJE_ERROR_RED_ESCRITURA,
            codigo=CodigoErrorPersistenciaGitHub.CONEXION_RED_FALLIDA,
            detalle_tecnico=detalle,
            token=token,
        )
    return ErrorRespuestaInesperadaEscrituraGitHub(
        MENSAJE_ERROR_RESPUESTA_INESPERADA_ESCRITURA,
        detalle_tecnico=detalle,
        token=token,
    )


def calcular_huella_publicacion(
    espacio: EspacioTrabajoAdminInventario,
    modo_publicacion: ModoPublicacionGitHub,
    *,
    sha256_excel: str | None = None,
) -> str:
    """Calcula una huella determinista de la operación para impedir envíos duplicados."""
    resumen_ops = "|".join(
        f"{op.tipo_operacion}:{op.codigo_producto}:{getattr(op, 'nombre', '')}"
        for op in espacio.historial_operaciones_locales
    )
    if sha256_excel is None:
        bytes_inv = serializar_inventario_a_bytes(espacio.inventario_trabajo)
        sha256_excel = hashlib.sha256(bytes_inv).hexdigest()

    cadena_base = (
        f"sesion={espacio.id_sesion_propietaria}|"
        f"modo={modo_publicacion.value}|"
        f"sha_base={espacio.sha_base_remoto or 'NONE'}|"
        f"sha256={sha256_excel}|"
        f"ops={resumen_ops}"
    )
    return hashlib.sha256(cadena_base.encode("utf-8")).hexdigest()


def _verificar_transporte_escritura_autorizado(
    ejecutor_http_put: EjecutorHTTPPut | None,
) -> None:
    """Verifica la separación estricta entre transporte simulado de pruebas y escritura real en red.

    Mientras `ESCRITURA_REAL_GITHUB_HABILITADA` no sea `True`:
    - Si no se inyecta `ejecutor_http_put`, la ejecución delega en `ejecutar_solicitud_put_github`,
      cuya compuerta incondicional rechaza cualquier escritura real con `ErrorEscrituraRealNoAutorizadaGitHub`.
    - Si se intenta inyectar como `ejecutor_http_put` la propia función `ejecutar_solicitud_put_github`
      o primitivas de red reales (`urllib.request`, `http.client`, `socket`, `ssl`, `OpenerDirector`),
      rechaza la operación inmediatamente con `ErrorEscrituraRealNoAutorizadaGitHub`.
    """
    if ejecutor_http_put is None:
        return

    if not callable(ejecutor_http_put):
        raise ErrorEscrituraRealNoAutorizadaGitHub(
            "El ejecutor de transporte HTTP PUT proporcionado no es válido."
        )

    if ESCRITURA_REAL_GITHUB_HABILITADA is not True:
        modulo_ejecutor = str(getattr(ejecutor_http_put, "__module__", "") or "").strip()
        dueno_metodo = getattr(ejecutor_http_put, "__self__", None)
        if (
            ejecutor_http_put is ejecutar_solicitud_put_github
            or ejecutor_http_put is urllib.request.urlopen
            or modulo_ejecutor in ("urllib.request", "http.client", "socket", "ssl")
            or isinstance(dueno_metodo, urllib.request.OpenerDirector)
        ):
            raise ErrorEscrituraRealNoAutorizadaGitHub(
                "No se permite utilizar un ejecutor de red real mientras ESCRITURA_REAL_GITHUB_HABILITADA sea False."
            )


def publicar_cambios_administrativos_github(
    estado: MutableMapping[str, Any],
    *,
    confirmacion_explicita: bool = False,
    modo_publicacion: ModoPublicacionGitHub | None = None,
    mensaje_commit: str | None = None,
    token: str | None = None,
    fuente_secretos: Mapping[str, Any] | None = None,
    fuente_entorno: Mapping[str, str] | None = None,
    config: ConfiguracionRepositorioGitHub = CONFIGURACION_POR_DEFECTO,
    ejecutor_http_get: EjecutorHTTP | None = None,
    ejecutor_http_put: EjecutorHTTPPut | None = None,
    consultor_existencia: ConsultorExistenciaRemota | None = None,
    lector_roundtrip: Callable[[bytes], InventarioDatos] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> ResultadoPublicacionGitHub:
    """Ejecuta de forma transaccional y controlada la publicación del inventario en GitHub.

    Cumple las Secciones 6, 7, 8, 9, 10, 11, 12 y 13 del Prompt 10:
    1. Exige contexto de escritorio, sesión administrativa autenticada y vigente, ausencia de
       bloqueo administrativo activo y propiedad de la sesión sobre el espacio de trabajo.
    2. Exige confirmación explícita (`confirmacion_explicita=True`).
    3. Rechaza cualquier intento de publicar datos demostrativos (`[DEMOSTRATIVO]`,
       `es_copia_demostrativa=True`) o inicializaciones sin `inicializacion_oficial_autorizada=True`.
    4. Impide envíos duplicados o publicaciones sin cambios pendientes.
    5. Serializa el inventario a `.xlsx` en memoria y verifica su lectura round-trip antes de
       realizar cualquier escritura.
    6. Consulta el estado remoto inmediatamente antes de escribir:
       - En `CREACION_INICIAL_ARCHIVO_NUEVO`: exige `EstadoExistenciaRemota.NO_EXISTE` confirmado.
         Si el archivo ya existe, aborta sin sobrescribir y registra el conflicto.
       - En `ACTUALIZACION_ARCHIVO_EXISTENTE`: exige `EstadoExistenciaRemota.EXISTE` y coincidencia
         exacta entre `sha_base_remoto` y el `sha_github` remoto actual. Si difieren, aborta antes
         del `PUT`, registra `EstadoConflictoShaAdmin` y preserva los cambios locales y el borrador.
    7. Ejecuta `PUT /repos/JunyMSAI/FerreteriaMS/contents/03_Aplicacion/inventario.xlsx` y valida
       que la respuesta confirme un nuevo `content.sha` y `commit.sha`.
    8. Solo tras confirmación exitosa actualiza `inventario_original`, `inventario_trabajo`,
       `sha_base_remoto`, limpia los cambios pendientes y descarta el borrador temporal.
    """
    if not isinstance(estado, MutableMapping):
        raise ErrorValidacionAdministrativa(
            "Se requiere un diccionario de estado de sesión válido para publicar cambios.",
            codigo=CodigoErrorAdministrativo.ESPACIO_TRABAJO_NO_INICIALIZADO,
        )

    # 1. Verificar que no exista un bloqueo administrativo activo (Sección 8, prueba 31)
    estado_bloqueo = consultar_estado_bloqueo_admin(
        reloj=reloj,
        ahora_epoch=ahora_epoch,
    )
    if estado_bloqueo.esta_bloqueado:
        raise ErrorAutorizacionAdmin(
            estado_bloqueo.mensaje_usuario,
            codigo=CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE,
        )

    # 2. Verificar sesión administrativa autenticada, no expirada, en escritorio y propietaria del espacio
    sesion, espacio = _obtener_espacio_trabajo_autorizado(
        estado,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=False,
    )

    # 3. Exigir confirmación explícita del administrador antes de cualquier llamada remota (Sección 8 y 12)
    if confirmacion_explicita is not True:
        raise ErrorConfirmacionPublicacionRequerida()

    # 4. Resolver el modo de publicación (creación inicial vs actualización de archivo existente)
    if modo_publicacion is not None:
        modo_efectivo = modo_publicacion
    elif espacio.origen_remoto_confirmado or (
        isinstance(espacio.sha_base_remoto, str) and bool(espacio.sha_base_remoto.strip())
    ):
        modo_efectivo = ModoPublicacionGitHub.ACTUALIZACION_ARCHIVO_EXISTENTE
    else:
        modo_efectivo = ModoPublicacionGitHub.CREACION_INICIAL_ARCHIVO_NUEVO

    # 5. Validar reglas previas del espacio de trabajo, bloqueo de datos demostrativos y duplicados
    if modo_efectivo == ModoPublicacionGitHub.ACTUALIZACION_ARCHIVO_EXISTENTE:
        if not isinstance(espacio.sha_base_remoto, str) or not espacio.sha_base_remoto.strip():
            raise ErrorShaBaseFaltanteGitHub(
                "El espacio de trabajo no posee un SHA base remoto válido para actualizar el inventario."
            )
    elif modo_efectivo == ModoPublicacionGitHub.CREACION_INICIAL_ARCHIVO_NUEVO:
        if espacio.origen_remoto_confirmado or (
            isinstance(espacio.sha_base_remoto, str) and bool(espacio.sha_base_remoto.strip())
        ):
            raise ErrorInventarioRemotoYaExiste(
                MENSAJE_ARCHIVO_REMOTO_YA_EXISTE,
                sha_remoto_actual=espacio.sha_base_remoto,
            )

    verificar_inventario_autorizado_para_publicacion(
        espacio.inventario_trabajo,
        modo_publicacion=modo_efectivo,
        espacio_trabajo=espacio,
        requerir_autorizacion_inicializacion_oficial=True,
    )

    huellas_previas = estado.get(CLAVE_HUELLA_ULTIMA_PUBLICACION_ADMIN)
    huella_candidata = calcular_huella_publicacion(espacio, modo_efectivo)
    if (
        (isinstance(huellas_previas, str) and huellas_previas == huella_candidata)
        or (
            isinstance(huellas_previas, (tuple, list, set, frozenset))
            and huella_candidata in huellas_previas
        )
    ):
        raise ErrorPublicacionDuplicadaGitHub()

    if modo_efectivo == ModoPublicacionGitHub.ACTUALIZACION_ARCHIVO_EXISTENTE:
        if not espacio.tiene_cambios_locales_pendientes:
            raise ErrorSinCambiosPendientesPublicacion()

    # 6. Validar destino, token, serialización a .xlsx en memoria y round-trip antes de tocar la red
    try:
        token_resuelto = _resolver_token_escritura_github(
            token=token,
            fuente_secretos=fuente_secretos,
            fuente_entorno=fuente_entorno,
        )
    except ErrorLecturaGitHub as exc_tok:
        raise ErrorCredencialesEscrituraGitHub(
            MENSAJE_ERROR_CREDENCIAL_ESCRITURA,
            detalle_tecnico=exc_tok.mensaje,
        ) from exc_tok

    solicitud_put, paquete_verificado = construir_solicitud_put_contents_github(
        espacio.inventario_trabajo,
        modo_publicacion=modo_efectivo,
        sha_base_remoto=espacio.sha_base_remoto
        if modo_efectivo == ModoPublicacionGitHub.ACTUALIZACION_ARCHIVO_EXISTENTE
        else None,
        mensaje_commit=mensaje_commit,
        token=token_resuelto,
        fuente_secretos=fuente_secretos,
        fuente_entorno=fuente_entorno,
        config=config,
        lector_roundtrip=lector_roundtrip,
    )

    instante_actual = (
        float(ahora_epoch)
        if ahora_epoch is not None
        else (float(reloj()) if reloj is not None else time.time())
    )

    # 7. Consulta previa obligatoria de existencia y versión SHA en GitHub antes de ejecutar PUT
    funcion_existencia = consultor_existencia or consultar_existencia_inventario_remoto
    try:
        existencia_actual = funcion_existencia(
            config=config,
            token=token_resuelto,
            ejecutor_http=ejecutor_http_get,
            lanzar_excepcion=False,
        )
    except ErrorLecturaGitHub as exc_lectura_previa:
        raise ErrorRedOTimeoutEscrituraGitHub(
            MENSAJE_ERROR_RED_ESCRITURA,
            detalle_tecnico=exc_lectura_previa.mensaje,
            token=token_resuelto,
        ) from exc_lectura_previa

    if existencia_actual.estado == EstadoExistenciaRemota.DESCONOCIDO_ERROR:
        raise _mapear_error_existencia_remota(existencia_actual, token=token_resuelto)

    if modo_efectivo == ModoPublicacionGitHub.CREACION_INICIAL_ARCHIVO_NUEVO:
        if (
            existencia_actual.estado == EstadoExistenciaRemota.EXISTE
            or not existencia_actual.inexistencia_confirmada
        ):
            sha_detectado = (existencia_actual.sha_github or "").strip() or None
            conflicto_creacion = EstadoConflictoShaAdmin(
                sha_base_local=None,
                sha_remoto_detectado=sha_detectado,
                modo_publicacion=modo_efectivo,
                detectado_en="verificacion_previa",
                mensaje_usuario=MENSAJE_ARCHIVO_REMOTO_YA_EXISTE,
                detalle_tecnico=(
                    f"El archivo remoto ya existe en GitHub (SHA='{sha_detectado}'). "
                    f"Se abortó la creación inicial sin enviar PUT."
                ),
                detectado_en_epoch=instante_actual,
                cambios_locales_preservados=True,
            )
            estado[CLAVE_CONFLICTO_SHA_ADMIN] = conflicto_creacion
            raise ErrorInventarioRemotoYaExiste(
                MENSAJE_ARCHIVO_REMOTO_YA_EXISTE,
                sha_remoto_actual=sha_detectado,
                detalle_tecnico=conflicto_creacion.detalle_tecnico,
                token=token_resuelto,
            )

    elif modo_efectivo == ModoPublicacionGitHub.ACTUALIZACION_ARCHIVO_EXISTENTE:
        sha_base_esperado = (espacio.sha_base_remoto or "").strip()
        if existencia_actual.estado == EstadoExistenciaRemota.NO_EXISTE:
            conflicto_inexistente = EstadoConflictoShaAdmin(
                sha_base_local=sha_base_esperado,
                sha_remoto_detectado=None,
                modo_publicacion=modo_efectivo,
                detectado_en="verificacion_previa",
                mensaje_usuario=MENSAJE_CONFLICTO_SHA_DETECTADO,
                detalle_tecnico=(
                    f"El archivo remoto con SHA base '{sha_base_esperado}' ya no existe "
                    f"en GitHub al verificar antes de guardar."
                ),
                detectado_en_epoch=instante_actual,
                cambios_locales_preservados=True,
            )
            estado[CLAVE_CONFLICTO_SHA_ADMIN] = conflicto_inexistente
            raise ErrorConflictoVersionShaGitHub(
                MENSAJE_CONFLICTO_SHA_DETECTADO,
                sha_base_local=sha_base_esperado,
                sha_remoto_actual=None,
                detalle_tecnico=conflicto_inexistente.detalle_tecnico,
                token=token_resuelto,
            )

        sha_remoto_actual = (existencia_actual.sha_github or "").strip()
        if not sha_remoto_actual or sha_remoto_actual != sha_base_esperado:
            conflicto_previo = EstadoConflictoShaAdmin(
                sha_base_local=sha_base_esperado,
                sha_remoto_detectado=sha_remoto_actual or None,
                modo_publicacion=modo_efectivo,
                detectado_en="verificacion_previa",
                mensaje_usuario=MENSAJE_CONFLICTO_SHA_DETECTADO,
                detalle_tecnico=(
                    f"El SHA base local ('{sha_base_esperado}') difiere del SHA remoto "
                    f"vigente en GitHub ('{sha_remoto_actual}')."
                ),
                detectado_en_epoch=instante_actual,
                cambios_locales_preservados=True,
            )
            estado[CLAVE_CONFLICTO_SHA_ADMIN] = conflicto_previo
            raise ErrorConflictoVersionShaGitHub(
                MENSAJE_CONFLICTO_SHA_DETECTADO,
                sha_base_local=sha_base_esperado,
                sha_remoto_actual=sha_remoto_actual or None,
                detalle_tecnico=conflicto_previo.detalle_tecnico,
                token=token_resuelto,
            )

    # 8. Verificar compuerta de transporte y ejecutar solicitud PUT hacia GitHub Contents API
    _verificar_transporte_escritura_autorizado(ejecutor_http_put)
    if ejecutor_http_put is not None:
        try:
            respuesta_put = ejecutor_http_put(
                solicitud_put.url,
                solicitud_put.encabezados,
                solicitud_put.cuerpo_json_bytes,
                TIMEOUT_ESCRITURA_POR_DEFECTO,
            )
        except ErrorPersistenciaGitHub:
            raise
        except (TimeoutError, socket.timeout) as exc_to:
            raise ErrorRedOTimeoutEscrituraGitHub(
                MENSAJE_ERROR_RED_ESCRITURA,
                codigo=CodigoErrorPersistenciaGitHub.TIEMPO_ESPERA_AGOTADO,
                detalle_tecnico=str(exc_to),
                token=token_resuelto,
            ) from exc_to
        except (urllib.error.URLError, OSError) as exc_red:
            raise ErrorRedOTimeoutEscrituraGitHub(
                MENSAJE_ERROR_RED_ESCRITURA,
                codigo=CodigoErrorPersistenciaGitHub.CONEXION_RED_FALLIDA,
                detalle_tecnico=str(exc_red),
                token=token_resuelto,
            ) from exc_red
    else:
        respuesta_put = ejecutar_solicitud_put_github(
            solicitud_put.url,
            solicitud_put.encabezados,
            solicitud_put.cuerpo_json_bytes,
            TIMEOUT_ESCRITURA_POR_DEFECTO,
        )

    try:
        nuevo_sha_archivo, sha_commit = interpretar_respuesta_put_github(
            respuesta_put,
            modo_publicacion=modo_efectivo,
            sha_base_enviado=solicitud_put.sha_base_enviado,
            token=token_resuelto,
        )
    except ErrorConflictoVersionShaGitHub as exc_conflicto_put:
        conflicto_put = EstadoConflictoShaAdmin(
            sha_base_local=solicitud_put.sha_base_enviado,
            sha_remoto_detectado=exc_conflicto_put.sha_remoto_actual,
            modo_publicacion=modo_efectivo,
            detectado_en="respuesta_put",
            mensaje_usuario=MENSAJE_CONFLICTO_SHA_DETECTADO,
            detalle_tecnico=exc_conflicto_put.detalle_tecnico,
            detectado_en_epoch=instante_actual,
            cambios_locales_preservados=True,
        )
        estado[CLAVE_CONFLICTO_SHA_ADMIN] = conflicto_put
        raise
    except ErrorInventarioRemotoYaExiste as exc_ya_existe_put:
        conflicto_ya_existe = EstadoConflictoShaAdmin(
            sha_base_local=None,
            sha_remoto_detectado=exc_ya_existe_put.sha_remoto_actual,
            modo_publicacion=modo_efectivo,
            detectado_en="respuesta_put",
            mensaje_usuario=MENSAJE_ARCHIVO_REMOTO_YA_EXISTE,
            detalle_tecnico=exc_ya_existe_put.detalle_tecnico,
            detectado_en_epoch=instante_actual,
            cambios_locales_preservados=True,
        )
        estado[CLAVE_CONFLICTO_SHA_ADMIN] = conflicto_ya_existe
        raise

    # 9. Confirmación exitosa: actualizar atómicamente el estado local, el SHA base y limpiar borradores
    sha_anterior = espacio.sha_base_remoto
    creados_publicados = tuple(espacio.codigos_productos_creados)
    editados_publicados = tuple(espacio.codigos_productos_editados)
    total_ops_publicadas = len(espacio.historial_operaciones_locales)

    sesion_renovada = renovar_sesion_admin(
        estado,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
    )

    espacio_confirmado = EspacioTrabajoAdminInventario(
        inventario_original=clonar_inventario_datos(paquete_verificado.inventario_verificado),
        inventario_trabajo=clonar_inventario_datos(paquete_verificado.inventario_verificado),
        usuario_propietario=sesion.usuario,
        id_sesion_propietaria=sesion.token_sesion,
        sha_base_remoto=nuevo_sha_archivo,
        origen_remoto_confirmado=True,
        codigos_productos_creados=(),
        codigos_productos_editados=(),
        historial_operaciones_locales=(),
        creado_en_epoch=espacio.creado_en_epoch,
        actualizado_en_epoch=sesion_renovada.ultima_actividad_epoch,
        confirmado_en_github=True,
        es_copia_local_temporal=False,
        es_copia_demostrativa=False,
        inicializacion_oficial_autorizada=False,
    )
    estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = espacio_confirmado
    estado[CLAVE_RESULTADO_CARGA_ADMIN] = ResultadoCargaInventarioAdmin(
        estado=EstadoInventarioAdmin.INVENTARIO_DISPONIBLE_EDICION_LOCAL,
        mensaje_usuario=MENSAJE_INVENTARIO_DISPONIBLE_EDICION_LOCAL,
        espacio_trabajo=espacio_confirmado,
        sha_base_remoto=nuevo_sha_archivo,
        permite_reintentar=False,
        permite_inicializar_demo_local=False,
        confirmado_en_github=True,
    )

    # Limpiar conflictos previos, confirmación puntual y borradores temporales (CA-055, Sección 11)
    estado[CLAVE_CONFLICTO_SHA_ADMIN] = None
    estado[CLAVE_CONFIRMACION_GUARDADO_GITHUB] = False
    estado[CLAVE_FORMULARIO_BORRADOR_ADMIN] = None
    descartar_borrador_admin(estado, reloj=reloj, ahora_epoch=ahora_epoch)

    # Registrar huella previa y posterior para impedir reenvío duplicado de la misma operación
    huella_post_confirmacion = calcular_huella_publicacion(
        espacio_confirmado,
        ModoPublicacionGitHub.ACTUALIZACION_ARCHIVO_EXISTENTE,
        sha256_excel=paquete_verificado.sha256_bytes,
    )
    estado[CLAVE_HUELLA_ULTIMA_PUBLICACION_ADMIN] = (
        huella_candidata,
        huella_post_confirmacion,
    )

    estado_res = (
        EstadoResultadoPublicacionGitHub.ACTUALIZACION_CONFIRMADA
        if hasattr(EstadoResultadoPublicacionGitHub, "ACTUALIZACION_CONFIRMADA")
        else (
            EstadoResultadoPublicacionGitHub.PUBLICACION_CONFIRMADA
            if modo_efectivo == ModoPublicacionGitHub.ACTUALIZACION_ARCHIVO_EXISTENTE
            else EstadoResultadoPublicacionGitHub.CREACION_INICIAL_CONFIRMADA
        )
    )
    mensaje_exito = (
        MENSAJE_PUBLICACION_ACTUALIZACION_EXITOSA
        if modo_efectivo == ModoPublicacionGitHub.ACTUALIZACION_ARCHIVO_EXISTENTE
        else MENSAJE_PUBLICACION_INICIALIZACION_EXITOSA
    )

    resultado_confirmado = ResultadoPublicacionGitHub(
        exito=True,
        confirmado_en_github=True,
        estado=estado_res,
        modo_publicacion=modo_efectivo,
        mensaje_usuario=mensaje_exito,
        detalle_tecnico=(
            f"Confirmado en GitHub ({config.repositorio_completo}@{config.rama}): "
            f"nuevo SHA='{nuevo_sha_archivo}', commit='{sha_commit}'."
        ),
        codigo_error=None,
        sha_anterior=sha_anterior,
        nuevo_sha_archivo=nuevo_sha_archivo,
        sha_commit=sha_commit,
        sha256_bytes=paquete_verificado.sha256_bytes,
        tamano_bytes=paquete_verificado.tamano_bytes,
        codigos_productos_creados=creados_publicados,
        codigos_productos_editados=editados_publicados,
        total_operaciones_publicadas=total_ops_publicadas,
        conflicto_sha=None,
        permite_reintentar=False,
        permite_recargar_remoto=False,
        cambios_locales_preservados=False,
        huella_operacion=huella_candidata,
    )
    estado[CLAVE_ULTIMA_PUBLICACION_GITHUB_ADMIN] = resultado_confirmado
    return resultado_confirmado


def recargar_inventario_remoto_tras_conflicto(
    estado: MutableMapping[str, Any],
    *,
    confirmar_descarte_locales: bool = False,
    descargador_remoto: Callable[..., ResultadoLecturaInventarioRemoto] | None = None,
    config: ConfiguracionRepositorioGitHub = CONFIGURACION_POR_DEFECTO,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> ResultadoCargaInventarioAdmin:
    """Recarga de forma segura la versión remota vigente tras un conflicto SHA, exigiendo confirmación explícita.

    Cumple la Sección 10.2 y el escenario de prueba 21:
    - Nunca sobrescribe ni descarta silenciosamente los cambios locales pendientes sin que el
      administrador confirme explícitamente (`confirmar_descarte_locales=True`).
    - Si la descarga remota falla, conserva intactos los cambios locales, el borrador y el
      estado de conflicto para que no se pierda información.
    """
    if not isinstance(estado, MutableMapping):
        raise ErrorValidacionAdministrativa(
            "Se requiere un diccionario de estado de sesión válido.",
            codigo=CodigoErrorAdministrativo.ESPACIO_TRABAJO_NO_INICIALIZADO,
        )

    estado_bloqueo = consultar_estado_bloqueo_admin(
        reloj=reloj,
        ahora_epoch=ahora_epoch,
    )
    if estado_bloqueo.esta_bloqueado:
        raise ErrorAutorizacionAdmin(
            estado_bloqueo.mensaje_usuario,
            codigo=CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE,
        )

    _, espacio_actual = _obtener_espacio_trabajo_autorizado(
        estado,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=False,
    )

    if (
        espacio_actual.tiene_cambios_locales_pendientes
        or not espacio_actual.origen_remoto_confirmado
    ) and confirmar_descarte_locales is not True:
        raise ErrorConfirmacionPublicacionRequerida(
            MENSAJE_CONFIRMACION_RECARGA_CONFLICTO_REQUERIDA
        )

    lector = descargador_remoto or descargar_inventario_remoto
    try:
        lectura_remota = lector(config=config)
    except ErrorLecturaGitHub as exc_red:
        raise ErrorRedOTimeoutEscrituraGitHub(
            MENSAJE_ERROR_RED_ESCRITURA,
            detalle_tecnico=exc_red.mensaje,
        ) from exc_red

    # Solo tras descargar y validar con éxito la versión remota vigente reemplazamos el espacio local
    resultado_carga = cargar_inventario_administrativo_en_sesion(
        estado,
        config_github=config,
        descargador_remoto=lambda **_: lectura_remota,
        inicializar_demo_si_no_existe=False,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
    )

    if resultado_carga.espacio_trabajo is not None:
        estado[CLAVE_CONFLICTO_SHA_ADMIN] = None
        estado[CLAVE_CONFIRMACION_GUARDADO_GITHUB] = False
        estado[CLAVE_FORMULARIO_BORRADOR_ADMIN] = None
        descartar_borrador_admin(estado, reloj=reloj, ahora_epoch=ahora_epoch)

    return resultado_carga
