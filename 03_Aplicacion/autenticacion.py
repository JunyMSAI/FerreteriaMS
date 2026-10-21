"""Módulo de autenticación administrativa segura para FerreteríaMS v0.

Proyecto: FerreteríaMS v0
Tarea: FERMS-V0-P07 (Autenticación administrativa)
Requisitos relacionados: RF-011, RF-012, RF-013 (parcial), Sección 6.3.1 y 6.3.6.
Criterios relacionados: CA-009, CA-010, CA-011, CA-019 (parcial), CA-027 (parcial),
CA-028, CA-029, CA-030 (parcial), CA-058 (parcial), CA-059.

Responsabilidades en el Prompt 07:
- Gestionar la única cuenta administrativa de FerreteríaMS v0.
- Obtener y validar la configuración de credenciales desde un entorno seguro
  (variables de entorno o `st.secrets`), sin contraseñas reales por defecto.
- Verificar contraseñas mediante hash Argon2id (`argon2-cffi`), rechazando contraseñas
  en texto plano o hashes rápidos inseguros (MD5, SHA-1, SHA-256).
- Mantener un comportamiento uniforme ante credenciales incorrectas, sin revelar si el
  nombre de usuario administrativo existe.
- Crear, consultar y destruir el estado autenticado de sesión con firma HMAC del servidor
  y registro activo en memoria del proceso, impidiendo que la manipulación de claves
  públicas en `st.session_state` otorgue autorización administrativa sin verificación.
- Dejar preparados los contratos modulares para integrar en el Prompt 08:
  contadores de intentos fallidos, bloqueos progresivos (5, 10, 20 y 30 min),
  expiración por inactividad (15 min), advertencia previa (13 min), renovación
  y conservación temporal de borradores.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, MutableMapping

from argon2 import PasswordHasher, Type, extract_parameters
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

# Identificación del algoritmo de hashing aprobado (Sección 6.3 del Prompt 07)
ALGORITMO_HASH_CONTRASENA: str = "argon2id"
PREFIJO_HASH_ARGON2ID: str = "$argon2id$"

# Parámetros recomendados para Argon2id (equilibrio entre seguridad OWASP y fluidez en Streamlit)
ARGON2_TIME_COST_DEFECTO: int = 2
ARGON2_MEMORY_COST_KIB_DEFECTO: int = 19456  # 19 MiB (mínimo recomendado por OWASP para Argon2id)
ARGON2_PARALLELISM_DEFECTO: int = 1
ARGON2_HASH_LEN_DEFECTO: int = 32
ARGON2_SALT_LEN_DEFECTO: int = 16

_HASHER_ARGON2ID = PasswordHasher(
    time_cost=ARGON2_TIME_COST_DEFECTO,
    memory_cost=ARGON2_MEMORY_COST_KIB_DEFECTO,
    parallelism=ARGON2_PARALLELISM_DEFECTO,
    hash_len=ARGON2_HASH_LEN_DEFECTO,
    salt_len=ARGON2_SALT_LEN_DEFECTO,
    type=Type.ID,
)

# Hash fantasma generado aleatoriamente en tiempo de carga del módulo para mantener un costo de
# cómputo uniforme cuando el usuario o la configuración no permiten verificar un hash real.
_HASH_FANTASMA_TIEMPO_CONSTANTE: str = _HASHER_ARGON2ID.hash(secrets.token_urlsafe(24))

# Clave efímera del servidor por proceso para firmar tokens de sesión y evitar falsificación
# mediante modificación directa de marcadores públicos en `st.session_state`.
_CLAVE_FIRMA_SESION_PROCESO: bytes = secrets.token_bytes(32)

# Variables de entorno y claves en `st.secrets` soportadas para la única cuenta administrativa
VARIABLES_ENTORNO_ADMIN_USUARIO: tuple[str, ...] = (
    "FERRETERIAMS_ADMIN_USER",
    "FERRETERIAMS_ADMIN_USUARIO",
)
VARIABLES_ENTORNO_ADMIN_HASH: tuple[str, ...] = (
    "FERRETERIAMS_ADMIN_PASSWORD_HASH",
    "FERRETERIAMS_ADMIN_HASH",
)
SECCIONES_SECRETOS_ADMIN: tuple[str, ...] = ("admin", "autenticacion", "ferreteriams_admin")
CLAVES_SECRETO_USUARIO: tuple[str, ...] = (
    "FERRETERIAMS_ADMIN_USER",
    "FERRETERIAMS_ADMIN_USUARIO",
    "admin_user",
    "usuario",
    "username",
    "user",
)
CLAVES_SECRETO_HASH: tuple[str, ...] = (
    "FERRETERIAMS_ADMIN_PASSWORD_HASH",
    "FERRETERIAMS_ADMIN_HASH",
    "admin_password_hash",
    "password_hash",
    "hash_contrasena",
)

# Claves estructuradas de estado de sesión
CLAVE_SESION_ADMIN: str = "ferms_sesion_admin"
CLAVE_MENSAJE_AUTH_ADMIN: str = "ferms_mensaje_auth_admin"
CLAVE_CONTEXTO_DISPOSITIVO: str = "ferms_contexto_dispositivo"
CLAVE_MARCADORES_PUBLICOS_SOSPECHOSOS: tuple[str, ...] = (
    "admin",
    "is_admin",
    "es_admin",
    "autenticado",
    "admin_autenticado",
    "ferms_admin_autenticado",
    "login_exitoso",
)

# Indicador explícito del alcance del Prompt 07 frente al Prompt 08 (Secciones 3 y 10)
CONTROLES_AVANZADOS_P08_ACTIVOS: bool = False

# Mensajes seguros para el usuario (sin exponer secretos, hashes ni existencia de usuarios)
MARCA_SECRETO_OCULTO: str = "[SECRETO_PROTEGIDO]"

MENSAJE_ADMIN_NO_CONFIGURADO: str = (
    "El acceso administrativo se encuentra deshabilitado porque las credenciales "
    "administrativas aún no están configuradas en el entorno seguro del servidor."
)
MENSAJE_ADMIN_CONFIGURACION_INVALIDA: str = (
    "El acceso administrativo permanece deshabilitado porque la configuración de "
    "seguridad administrativa es incompleta o no utiliza un formato de hash válido."
)
MENSAJE_CREDENCIALES_INCOMPLETAS: str = (
    "Por favor, introduce tanto el usuario como la contraseña para iniciar sesión."
)
MENSAJE_CREDENCIALES_INVALIDAS: str = (
    "Usuario o contraseña incorrectos. No se autorizó el acceso administrativo."
)
MENSAJE_AUTENTICACION_EXITOSA: str = (
    "Sesión administrativa iniciada correctamente."
)
MENSAJE_SESION_CERRADA: str = (
    "La sesión administrativa se ha cerrado correctamente."
)
MENSAJE_ACCESO_NO_AUTORIZADO: str = (
    "Acceso administrativo denegado. Se requiere una sesión administrativa autenticada y válida."
)
MENSAJE_RESTRICCION_MOVIL_ADMIN: str = (
    "La administración del inventario está restringida exclusivamente a la interfaz web "
    "para computadora. Desde dispositivos móviles solo está habilitada la consulta pública."
)
MENSAJE_ERROR_INTERNO_AUTH: str = (
    "No fue posible procesar la solicitud de autenticación en este momento."
)

_PATRONES_SECRETOS_AUTH = (
    re.compile(r"\$argon2(?:id|i|d)\$[^\s,;\"']+"),
    re.compile(r"\$2[aby]\$[^\s,;\"']+"),
    re.compile(r"(?i)(password_hash\s*[=:]\s*)[^\s,;\"']+"),
    re.compile(r"(?i)(contrasena\s*[=:]\s*)[^\s,;\"']+"),
    re.compile(r"(?i)(password\s*[=:]\s*)[^\s,;\"']+"),
    re.compile(r"(?i)(bearer\s+)[^\s,;\"']+"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]+\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]+\b"),
)

_PATRON_USER_AGENT_MOVIL = re.compile(
    r"(?i)(android|iphone|ipod|iemobile|windows phone|blackberry|bb10|opera mini|mobile)"
)


class EstadoConfiguracionAdmin(str, Enum):
    """Estados posibles de la configuración de la cuenta administrativa única."""

    VALIDA = "VALIDA"
    NO_CONFIGURADA = "NO_CONFIGURADA"
    CONFIGURACION_INVALIDA = "CONFIGURACION_INVALIDA"


class CodigoResultadoAutenticacion(str, Enum):
    """Códigos estructurados para los resultados de verificación e inicio de sesión."""

    AUTENTICACION_EXITOSA = "AUTENTICACION_EXITOSA"
    CREDENCIALES_INVALIDAS = "CREDENCIALES_INVALIDAS"
    DATOS_INCOMPLETOS = "DATOS_INCOMPLETOS"
    CONFIGURACION_AUSENTE = "CONFIGURACION_AUSENTE"
    CONFIGURACION_INVALIDA = "CONFIGURACION_INVALIDA"
    DISPOSITIVO_NO_PERMITIDO = "DISPOSITIVO_NO_PERMITIDO"
    ERROR_INTERNO_AUTENTICACION = "ERROR_INTERNO_AUTENTICACION"


class ContextoDispositivo(str, Enum):
    """Clasificación del contexto de dispositivo para evaluar la restricción de escritorio (RF-013)."""

    ESCRITORIO = "ESCRITORIO"
    MOVIL = "MOVIL"
    DESCONOCIDO = "DESCONOCIDO"


class ErrorAutenticacionAdmin(Exception):
    """Excepción base segura para errores de autenticación y autorización administrativa."""

    def __init__(
        self,
        mensaje: str,
        *,
        codigo: CodigoResultadoAutenticacion = CodigoResultadoAutenticacion.ERROR_INTERNO_AUTENTICACION,
        secretos_para_sanitizar: tuple[str, ...] = (),
    ) -> None:
        mensaje_seguro = ocultar_secretos_autenticacion(mensaje, secretos_para_sanitizar)
        super().__init__(mensaje_seguro)
        self.mensaje: str = mensaje_seguro
        self.codigo: CodigoResultadoAutenticacion = codigo


class ErrorAutorizacionAdmin(ErrorAutenticacionAdmin):
    """Se lanza cuando se intenta ejecutar una acción administrativa sin sesión autenticada válida."""


@dataclass(frozen=True)
class ConfiguracionAdmin:
    """Representa la configuración validada de la única cuenta administrativa.

    El hash de contraseña se excluye de las representaciones textuales (`repr=False`)
    para impedir exposiciones accidentales en trazas o registros.
    """

    usuario: str
    password_hash: str = field(repr=False)

    def __repr__(self) -> str:
        return f"ConfiguracionAdmin(usuario={self.usuario!r}, password_hash='{MARCA_SECRETO_OCULTO}')"

    def __str__(self) -> str:
        return self.__repr__()


@dataclass(frozen=True)
class ResultadoVerificacionConfiguracion:
    """Resultado estructurado de la inspección de credenciales administrativas configuradas."""

    estado: EstadoConfiguracionAdmin
    es_valida: bool
    mensaje_usuario: str
    configuracion: ConfiguracionAdmin | None = field(default=None, repr=False)


@dataclass(frozen=True)
class ComprobanteVerificacionCredenciales:
    """Comprobante criptográfico de un solo uso emitido tras verificar credenciales con Argon2id.

    Garantiza que `registrar_autenticacion_en_sesion()` solamente pueda emitir una sesión
    administrativa válida como consecuencia directa de una verificación satisfactoria y
    reciente de usuario y contraseña en `verificar_credenciales_admin()`.
    """

    id_comprobante: str = field(repr=False)
    usuario: str
    emitido_en_epoch: float
    contexto_dispositivo: ContextoDispositivo
    huella_configuracion: str = field(repr=False)
    firma_hmac: str = field(repr=False)

    def __repr__(self) -> str:
        return (
            f"ComprobanteVerificacionCredenciales(usuario={self.usuario!r}, "
            f"contexto_dispositivo={self.contexto_dispositivo.value!r}, "
            f"id_comprobante='{MARCA_SECRETO_OCULTO}')"
        )


@dataclass(frozen=True)
class EstadoSesionAdmin:
    """Estado autenticado verificable asociado a una sesión administrativa individual.

    Incluye marcas de tiempo (`autenticado_en_epoch`, `ultima_actividad_epoch`) listas
    para conectarse con las reglas de inactividad y renovación del Prompt 08.
    """

    autenticado: bool
    usuario: str
    token_sesion: str = field(repr=False)
    firma_hmac: str = field(repr=False)
    autenticado_en_epoch: float
    ultima_actividad_epoch: float
    contexto_dispositivo: ContextoDispositivo = ContextoDispositivo.ESCRITORIO

    def __repr__(self) -> str:
        return (
            f"EstadoSesionAdmin(autenticado={self.autenticado!r}, "
            f"usuario={self.usuario!r}, "
            f"contexto_dispositivo={self.contexto_dispositivo.value!r})"
        )


@dataclass(frozen=True)
class ResultadoAutenticacion:
    """Contrato de retorno de las operaciones de verificación e inicio de sesión administrativa."""

    autenticado: bool
    codigo: CodigoResultadoAutenticacion
    mensaje_usuario: str
    usuario: str | None = None
    estado_sesion: EstadoSesionAdmin | None = field(default=None, repr=False)
    comprobante_verificacion: ComprobanteVerificacionCredenciales | None = field(
        default=None, repr=False
    )
    # Campos reservados para la integración del Prompt 08 (permanecen en None durante el Prompt 07)
    intentos_fallidos_acumulados: int | None = None
    bloqueado_hasta_epoch: float | None = None


@dataclass(frozen=True)
class ContratoExtensionPrompt08:
    """Especificación declarativa de los puntos de extensión reservados para el Prompt 08.

    Nota técnica (Sección 10 del Prompt 07):
    Los contadores de intentos fallidos y bloqueos progresivos del Prompt 08 deberán
    almacenarse en un registro compartido en el servidor (no únicamente en `st.session_state`),
    para evitar que abrir una pestaña o sesión nueva eluda un bloqueo temporal activo.
    """

    activo_en_etapa_actual: bool = CONTROLES_AVANZADOS_P08_ACTIVOS
    max_intentos_fallidos: int = 5
    bloqueos_progresivos_minutos: tuple[int, int, int, int] = (5, 10, 20, 30)
    advertencia_inactividad_segundos: int = 13 * 60
    expiracion_inactividad_segundos: int = 15 * 60
    retencion_borrador_segundos: int = 15 * 60
    requiere_almacenamiento_compartido_servidor: bool = True


CONTRATO_EXTENSION_PROMPT_08 = ContratoExtensionPrompt08()


@dataclass
class _RegistroComprobanteServidor:
    """Registro interno efímero de un solo uso para comprobar que una verificación fue genuina."""

    id_comprobante: str
    usuario: str
    emitido_en_epoch: float
    contexto_dispositivo: ContextoDispositivo
    huella_configuracion: str
    firma_hmac: str
    consumido: bool = False


@dataclass
class _RegistroSesionServidor:
    """Registro interno en memoria del servidor para validar sesiones activas y preparar el Prompt 08."""

    token_sesion: str
    usuario: str
    id_comprobante_origen: str
    huella_configuracion: str
    firma_hmac: str
    autenticado_en_epoch: float
    ultima_actividad_epoch: float
    contexto_dispositivo: ContextoDispositivo


# Ventana máxima de validez (en segundos) para canjear un comprobante de verificación por una sesión.
_TTL_COMPROBANTE_VERIFICACION_SEGUNDOS: float = 60.0

# Almacén en memoria del servidor de comprobantes de verificación pendientes de canje (un solo uso).
_COMPROBANTES_VERIFICACION_SERVIDOR: dict[str, _RegistroComprobanteServidor] = {}

# Almacén en memoria del servidor de sesiones autenticadas vigentes, indexado por `token_sesion`.
_SESIONES_ACTIVAS_SERVIDOR: dict[str, _RegistroSesionServidor] = {}


def ocultar_secretos_autenticacion(
    texto: str,
    secretos_adicionales: tuple[str, ...] = (),
) -> str:
    """Elimina cualquier rastro de contraseñas, hashes o tokens de un mensaje antes de mostrarlo."""
    if not texto:
        return ""
    resultado = str(texto)
    for secreto in secretos_adicionales:
        if isinstance(secreto, str) and secreto.strip():
            resultado = resultado.replace(secreto, MARCA_SECRETO_OCULTO)
            resultado = resultado.replace(secreto.strip(), MARCA_SECRETO_OCULTO)
    for patron in _PATRONES_SECRETOS_AUTH:
        if patron.groups >= 1:
            resultado = patron.sub(rf"\1{MARCA_SECRETO_OCULTO}", resultado)
        else:
            resultado = patron.sub(MARCA_SECRETO_OCULTO, resultado)
    return resultado


def generar_hash_contrasena(contrasena: str) -> str:
    """Genera un hash Argon2id seguro con sal criptográfica aleatoria (Sección 6.3).

    Esta función permite preparar el hash de la cuenta administrativa fuera de línea o
    en pruebas automatizadas sin almacenar contraseñas en texto plano.
    """
    if not isinstance(contrasena, str) or not contrasena or not contrasena.strip():
        raise ValueError("La contraseña para generar el hash debe ser un texto no vacío.")
    return _HASHER_ARGON2ID.hash(contrasena)


def es_hash_contrasena_valido(hash_almacenado: Any) -> bool:
    """Comprueba que el valor configurado sea un hash PHC Argon2id bien formado.

    Rechaza texto plano, MD5, SHA-1, SHA-256, cadenas vacías u otros formatos no autorizados.
    """
    if not isinstance(hash_almacenado, str):
        return False
    limpio = hash_almacenado.strip()
    if not limpio.startswith(PREFIJO_HASH_ARGON2ID):
        return False
    partes = limpio.split("$")
    # Estructura PHC estándar: ['', 'argon2id', 'v=19', 'm=...,t=...,p=...', '<salt>', '<hash>']
    if len(partes) != 6 or not partes[4] or not partes[5]:
        return False
    try:
        parametros = extract_parameters(limpio)
    except Exception:
        return False
    return parametros.type == Type.ID


def verificar_contrasena_hash(contrasena_plana: Any, hash_almacenado: Any) -> bool:
    """Verifica una contraseña frente a un hash Argon2id sin comparaciones en texto plano.

    Si los parámetros de entrada son inválidos, ejecuta una verificación fantasma con Argon2id
    para mantener un tiempo de respuesta razonablemente uniforme.
    """
    es_contrasena_valida = isinstance(contrasena_plana, str) and bool(contrasena_plana)
    es_hash_valido = es_hash_contrasena_valido(hash_almacenado)

    if not es_contrasena_valida or not es_hash_valido:
        try:
            _HASHER_ARGON2ID.verify(_HASH_FANTASMA_TIEMPO_CONSTANTE, "contrasena_fantasma_no_valida")
        except Exception:
            pass
        return False

    try:
        return bool(_HASHER_ARGON2ID.verify(hash_almacenado.strip(), contrasena_plana))
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
    except Exception:
        return False


def _extraer_desde_mapeo_secretos(
    secretos: Mapping[str, Any],
    claves_directas: tuple[str, ...],
) -> str | None:
    """Extrae un valor de configuración desde un diccionario o `st.secrets`."""
    for clave in claves_directas:
        if clave in secretos and secretos[clave] is not None:
            valor_str = str(secretos[clave]).strip()
            if valor_str:
                return valor_str

    for seccion in SECCIONES_SECRETOS_ADMIN:
        if seccion in secretos and isinstance(secretos[seccion], Mapping):
            sub_mapeo = secretos[seccion]
            for clave in claves_directas:
                if clave in sub_mapeo and sub_mapeo[clave] is not None:
                    valor_str = str(sub_mapeo[clave]).strip()
                    if valor_str:
                        return valor_str
    return None


def _hay_contexto_ejecucion_streamlit() -> bool:
    """Comprueba si existe un `ScriptRunContext` activo de Streamlit para evitar advertencias en modo bare."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx(suppress_warning=True) is not None
    except Exception:
        return False


def _es_estado_lectura_valido(estado: Any) -> bool:
    """Determina si el objeto de estado soporta lectura por clave (`dict`, `SessionStateProxy`, `SafeSessionState`)."""
    return (
        estado is not None
        and hasattr(estado, "__getitem__")
        and hasattr(estado, "__contains__")
    )


def _es_estado_escritura_valido(estado: Any) -> bool:
    """Determina si el objeto de estado soporta lectura y escritura por clave."""
    return _es_estado_lectura_valido(estado) and hasattr(estado, "__setitem__")


def _obtener_de_estado(estado: Any, clave: str, defecto: Any = None) -> Any:
    """Obtiene de forma segura un valor desde un diccionario o `st.session_state`."""
    if not _es_estado_lectura_valido(estado):
        return defecto
    try:
        return estado[clave] if clave in estado else defecto
    except Exception:
        return defecto


def _obtener_secretos_streamlit_seguro() -> Mapping[str, Any] | None:
    """Obtiene `st.secrets` si está disponible en tiempo de ejecución, sin lanzar errores si no existe."""
    if not _hay_contexto_ejecucion_streamlit():
        return None
    try:
        import streamlit as st

        secretos = getattr(st, "secrets", None)
        if secretos is not None and len(secretos) > 0:
            return secretos
    except Exception:
        pass
    return None


def _es_nombre_usuario_configurado_valido(usuario: Any) -> bool:
    """Verifica que el identificador del administrador sea un texto válido sin caracteres de control."""
    if not isinstance(usuario, str):
        return False
    limpio = usuario.strip()
    if not limpio or len(limpio) > 128:
        return False
    return not any(ord(c) < 32 or ord(c) == 127 for c in limpio)


def obtener_configuracion_admin(
    *,
    fuente_entorno: Mapping[str, Any] | None = None,
    fuente_secretos: Mapping[str, Any] | None = None,
) -> ResultadoVerificacionConfiguracion:
    """Obtiene y valida la configuración de la única cuenta administrativa (Secciones 6.1 a 6.4).

    Prioridad de lectura:
    1. `fuente_entorno` explícita (o `os.environ` cuando no se inyecta una fuente de prueba).
    2. `fuente_secretos` explícita (o `st.secrets` cuando está configurado).

    Nunca crea contraseñas por defecto ni acepta contraseñas en texto plano.
    """
    entorno_efectivo: Mapping[str, Any] = (
        fuente_entorno if fuente_entorno is not None else os.environ
    )
    secretos_efectivos: Mapping[str, Any] | None = (
        fuente_secretos
        if fuente_secretos is not None
        else (_obtener_secretos_streamlit_seguro() if fuente_entorno is None else None)
    )

    usuario_crudo: str | None = None
    hash_crudo: str | None = None

    for var_usr in VARIABLES_ENTORNO_ADMIN_USUARIO:
        val = entorno_efectivo.get(var_usr)
        if val is not None and str(val).strip():
            usuario_crudo = str(val).strip()
            break

    for var_hash in VARIABLES_ENTORNO_ADMIN_HASH:
        val = entorno_efectivo.get(var_hash)
        if val is not None and str(val).strip():
            hash_crudo = str(val).strip()
            break

    if secretos_efectivos is not None:
        if not usuario_crudo:
            usuario_crudo = _extraer_desde_mapeo_secretos(
                secretos_efectivos, CLAVES_SECRETO_USUARIO
            )
        if not hash_crudo:
            hash_crudo = _extraer_desde_mapeo_secretos(
                secretos_efectivos, CLAVES_SECRETO_HASH
            )

    # Caso 1: Ninguna credencial configurada -> acceso deshabilitado de forma segura
    if not usuario_crudo and not hash_crudo:
        return ResultadoVerificacionConfiguracion(
            estado=EstadoConfiguracionAdmin.NO_CONFIGURADA,
            es_valida=False,
            mensaje_usuario=MENSAJE_ADMIN_NO_CONFIGURADO,
            configuracion=None,
        )

    # Caso 2: Configuración parcial o con formato inválido (p. ej. contraseña en texto plano)
    if (
        not usuario_crudo
        or not hash_crudo
        or not _es_nombre_usuario_configurado_valido(usuario_crudo)
        or not es_hash_contrasena_valido(hash_crudo)
    ):
        return ResultadoVerificacionConfiguracion(
            estado=EstadoConfiguracionAdmin.CONFIGURACION_INVALIDA,
            es_valida=False,
            mensaje_usuario=MENSAJE_ADMIN_CONFIGURACION_INVALIDA,
            configuracion=None,
        )

    config = ConfiguracionAdmin(
        usuario=usuario_crudo.strip(),
        password_hash=hash_crudo.strip(),
    )
    return ResultadoVerificacionConfiguracion(
        estado=EstadoConfiguracionAdmin.VALIDA,
        es_valida=True,
        mensaje_usuario="Configuración administrativa válida.",
        configuracion=config,
    )


def verificar_configuracion_admin(
    *,
    fuente_entorno: Mapping[str, Any] | None = None,
    fuente_secretos: Mapping[str, Any] | None = None,
) -> bool:
    """Devuelve `True` únicamente si existe una configuración administrativa completa y con hash válido."""
    return obtener_configuracion_admin(
        fuente_entorno=fuente_entorno,
        fuente_secretos=fuente_secretos,
    ).es_valida


def detectar_contexto_dispositivo(
    *,
    encabezados_http: Mapping[str, Any] | None = None,
    estado: Any | None = None,
) -> ContextoDispositivo:
    """Evalúa los indicadores disponibles del contexto de dispositivo (Sección 9 del Prompt 07).

    Limitación técnica documentada:
    En aplicaciones web basadas en Streamlit sin servicios externos ni JavaScript invasivo,
    los encabezados HTTP (`Sec-CH-UA-Mobile`, `User-Agent`) y las media queries CSS ayudan a
    restringir el uso accidental desde teléfonos, pero un cliente podría falsificar encabezados.
    Por ello, toda operación administrativa exige siempre autenticación verificada en Python.
    """
    if _es_estado_lectura_valido(estado):
        contexto_en_estado = _obtener_de_estado(estado, CLAVE_CONTEXTO_DISPOSITIVO)
        if isinstance(contexto_en_estado, ContextoDispositivo):
            return contexto_en_estado
        if isinstance(contexto_en_estado, str):
            valor_up = contexto_en_estado.strip().upper()
            if valor_up == ContextoDispositivo.MOVIL.value:
                return ContextoDispositivo.MOVIL
            if valor_up == ContextoDispositivo.ESCRITORIO.value:
                return ContextoDispositivo.ESCRITORIO

    headers_efectivos: Mapping[str, Any] | None = encabezados_http
    if headers_efectivos is None and _hay_contexto_ejecucion_streamlit():
        try:
            import streamlit as st

            contexto_st = getattr(st, "context", None)
            if contexto_st is not None:
                headers_st = getattr(contexto_st, "headers", None)
                if headers_st is not None and hasattr(headers_st, "items"):
                    headers_efectivos = headers_st
        except Exception:
            headers_efectivos = None

    if headers_efectivos:
        mapa_min = {str(k).strip().lower(): str(v).strip() for k, v in headers_efectivos.items()}
        ch_mobile = mapa_min.get("sec-ch-ua-mobile", "")
        if ch_mobile == "?1" or ch_mobile.lower() == "true":
            return ContextoDispositivo.MOVIL

        user_agent = mapa_min.get("user-agent", "")
        if user_agent and _PATRON_USER_AGENT_MOVIL.search(user_agent):
            return ContextoDispositivo.MOVIL

        if user_agent or ch_mobile == "?0":
            return ContextoDispositivo.ESCRITORIO

    return ContextoDispositivo.ESCRITORIO


def _calcular_huella_configuracion(cfg: ConfiguracionAdmin) -> str:
    """Calcula una huella HMAC de la configuración administrativa verificada sin exponer el hash."""
    mensaje = f"{cfg.usuario}|{cfg.password_hash}".encode("utf-8")
    return hmac.new(_CLAVE_FIRMA_SESION_PROCESO, mensaje, hashlib.sha256).hexdigest()


def _calcular_firma_comprobante(
    id_comprobante: str,
    usuario: str,
    emitido_en_epoch: float,
    contexto_dispositivo: ContextoDispositivo,
    huella_configuracion: str,
) -> str:
    """Calcula la firma HMAC-SHA256 para un comprobante efímero de verificación de credenciales."""
    mensaje = (
        f"COMPROBANTE|{id_comprobante}|{usuario}|{emitido_en_epoch:.6f}|"
        f"{contexto_dispositivo.value}|{huella_configuracion}"
    ).encode("utf-8")
    return hmac.new(_CLAVE_FIRMA_SESION_PROCESO, mensaje, hashlib.sha256).hexdigest()


def _depurar_comprobantes_expirados(ahora_epoch: float | None = None) -> None:
    """Elimina comprobantes de verificación no canjeados cuya ventana de validez haya expirado."""
    referencia = float(ahora_epoch) if ahora_epoch is not None else time.time()
    ids_expirados = [
        id_comp
        for id_comp, reg in _COMPROBANTES_VERIFICACION_SERVIDOR.items()
        if reg.consumido or (referencia - reg.emitido_en_epoch) > _TTL_COMPROBANTE_VERIFICACION_SEGUNDOS
    ]
    for id_comp in ids_expirados:
        _COMPROBANTES_VERIFICACION_SERVIDOR.pop(id_comp, None)


def _calcular_firma_sesion(
    usuario: str,
    token_sesion: str,
    id_comprobante: str,
    autenticado_en_epoch: float,
    contexto_dispositivo: ContextoDispositivo,
) -> str:
    """Calcula la firma HMAC-SHA256 del servidor para un estado de sesión administrativo."""
    mensaje = (
        f"SESION|{usuario}|{token_sesion}|{id_comprobante}|"
        f"{autenticado_en_epoch:.6f}|{contexto_dispositivo.value}"
    ).encode("utf-8")
    return hmac.new(_CLAVE_FIRMA_SESION_PROCESO, mensaje, hashlib.sha256).hexdigest()


def verificar_credenciales_admin(
    usuario: Any,
    contrasena: Any,
    *,
    fuente_entorno: Mapping[str, Any] | None = None,
    fuente_secretos: Mapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo = ContextoDispositivo.ESCRITORIO,
) -> ResultadoAutenticacion:
    """Verifica el usuario y la contraseña frente a la configuración administrativa segura (Sección 7).

    Garantías de seguridad:
    - Rechaza solicitudes en contexto móvil (`DISPOSITIVO_NO_PERMITIDO`).
    - Rechaza configuraciones ausentes o inválidas sin habilitar accesos por defecto.
    - Rechaza usuario o contraseña vacíos (`DATOS_INCOMPLETOS`).
    - Ejecuta siempre la comparación en tiempo constante (`hmac.compare_digest`) y la
      verificación Argon2id antes de emitir el veredicto, devolviendo un mensaje uniforme
      que impide enumerar si el usuario ingresado coincide con el configurado.
    - Emite un `ComprobanteVerificacionCredenciales` de un solo uso firmado en servidor
      únicamente cuando la verificación Argon2id resulta satisfactoria.
    """
    try:
        if contexto_dispositivo == ContextoDispositivo.MOVIL:
            return ResultadoAutenticacion(
                autenticado=False,
                codigo=CodigoResultadoAutenticacion.DISPOSITIVO_NO_PERMITIDO,
                mensaje_usuario=MENSAJE_RESTRICCION_MOVIL_ADMIN,
            )

        verificacion_cfg = obtener_configuracion_admin(
            fuente_entorno=fuente_entorno,
            fuente_secretos=fuente_secretos,
        )
        if verificacion_cfg.estado == EstadoConfiguracionAdmin.NO_CONFIGURADA:
            return ResultadoAutenticacion(
                autenticado=False,
                codigo=CodigoResultadoAutenticacion.CONFIGURACION_AUSENTE,
                mensaje_usuario=MENSAJE_ADMIN_NO_CONFIGURADO,
            )
        if (
            verificacion_cfg.estado != EstadoConfiguracionAdmin.VALIDA
            or verificacion_cfg.configuracion is None
        ):
            return ResultadoAutenticacion(
                autenticado=False,
                codigo=CodigoResultadoAutenticacion.CONFIGURACION_INVALIDA,
                mensaje_usuario=MENSAJE_ADMIN_CONFIGURACION_INVALIDA,
            )

        usuario_str = usuario.strip() if isinstance(usuario, str) else ""
        contrasena_str = contrasena if isinstance(contrasena, str) else ""

        if not usuario_str or not contrasena_str or not contrasena_str.strip():
            return ResultadoAutenticacion(
                autenticado=False,
                codigo=CodigoResultadoAutenticacion.DATOS_INCOMPLETOS,
                mensaje_usuario=MENSAJE_CREDENCIALES_INCOMPLETAS,
            )

        cfg = verificacion_cfg.configuracion
        coincide_usuario = hmac.compare_digest(
            usuario_str.encode("utf-8"),
            cfg.usuario.encode("utf-8"),
        )
        coincide_contrasena = verificar_contrasena_hash(
            contrasena_str,
            cfg.password_hash,
        )

        if coincide_usuario and coincide_contrasena:
            ahora_verificacion = time.time()
            _depurar_comprobantes_expirados(ahora_verificacion)
            id_comprobante = secrets.token_urlsafe(32)
            huella_cfg = _calcular_huella_configuracion(cfg)
            firma_comprobante = _calcular_firma_comprobante(
                id_comprobante=id_comprobante,
                usuario=cfg.usuario,
                emitido_en_epoch=ahora_verificacion,
                contexto_dispositivo=contexto_dispositivo,
                huella_configuracion=huella_cfg,
            )
            comprobante = ComprobanteVerificacionCredenciales(
                id_comprobante=id_comprobante,
                usuario=cfg.usuario,
                emitido_en_epoch=ahora_verificacion,
                contexto_dispositivo=contexto_dispositivo,
                huella_configuracion=huella_cfg,
                firma_hmac=firma_comprobante,
            )
            _COMPROBANTES_VERIFICACION_SERVIDOR[id_comprobante] = _RegistroComprobanteServidor(
                id_comprobante=id_comprobante,
                usuario=cfg.usuario,
                emitido_en_epoch=ahora_verificacion,
                contexto_dispositivo=contexto_dispositivo,
                huella_configuracion=huella_cfg,
                firma_hmac=firma_comprobante,
                consumido=False,
            )
            return ResultadoAutenticacion(
                autenticado=True,
                codigo=CodigoResultadoAutenticacion.AUTENTICACION_EXITOSA,
                mensaje_usuario=MENSAJE_AUTENTICACION_EXITOSA,
                usuario=cfg.usuario,
                comprobante_verificacion=comprobante,
            )

        return ResultadoAutenticacion(
            autenticado=False,
            codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            mensaje_usuario=MENSAJE_CREDENCIALES_INVALIDAS,
        )
    except Exception as exc:
        secretos_conocidos: list[str] = []
        if isinstance(contrasena, str) and contrasena:
            secretos_conocidos.append(contrasena)
        _ = ocultar_secretos_autenticacion(str(exc), tuple(secretos_conocidos))
        return ResultadoAutenticacion(
            autenticado=False,
            codigo=CodigoResultadoAutenticacion.ERROR_INTERNO_AUTENTICACION,
            mensaje_usuario=MENSAJE_ERROR_INTERNO_AUTH,
        )


def _limpiar_marcadores_publicos_manipulables(estado: Any) -> None:
    """Elimina o desactiva claves booleanas simples que pudieran haberse inyectado en sesión."""
    if not _es_estado_escritura_valido(estado):
        return
    for clave_sospechosa in CLAVE_MARCADORES_PUBLICOS_SOSPECHOSOS:
        if clave_sospechosa in estado:
            try:
                del estado[clave_sospechosa]
            except Exception:
                estado[clave_sospechosa] = None


def registrar_autenticacion_en_sesion(
    estado: Any,
    verificacion_o_usuario: ResultadoAutenticacion | ComprobanteVerificacionCredenciales | str | None = None,
    *,
    usuario: str | None = None,
    resultado_verificacion: ResultadoAutenticacion | None = None,
    comprobante_verificacion: ComprobanteVerificacionCredenciales | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    marca_tiempo_epoch: float | None = None,
) -> EstadoSesionAdmin:
    """Registra una sesión administrativa verificada canjeando un comprobante de autenticación.

    Restricción de seguridad:
    - Esta función NO permite emitir sesiones a partir de un simple nombre de usuario (`str`)
      ni desde un `ResultadoAutenticacion` falsificado o fallido.
    - Exige y consume atómicamente un `ComprobanteVerificacionCredenciales` de un solo uso
      emitido previamente por `verificar_credenciales_admin()` tras comprobar Argon2id.
    """
    if not _es_estado_escritura_valido(estado):
        raise TypeError("El estado de sesión debe soportar lectura y escritura por clave.")

    if contexto_dispositivo == ContextoDispositivo.MOVIL:
        cerrar_sesion_admin(estado)
        raise ErrorAutorizacionAdmin(
            MENSAJE_RESTRICCION_MOVIL_ADMIN,
            codigo=CodigoResultadoAutenticacion.DISPOSITIVO_NO_PERMITIDO,
        )

    res_candidato: ResultadoAutenticacion | None = resultado_verificacion
    comp_candidato: ComprobanteVerificacionCredenciales | None = comprobante_verificacion
    usuario_explicito: str | None = usuario

    if isinstance(verificacion_o_usuario, ResultadoAutenticacion):
        if res_candidato is None:
            res_candidato = verificacion_o_usuario
    elif isinstance(verificacion_o_usuario, ComprobanteVerificacionCredenciales):
        if comp_candidato is None:
            comp_candidato = verificacion_o_usuario
    elif isinstance(verificacion_o_usuario, str):
        if usuario_explicito is None:
            usuario_explicito = verificacion_o_usuario
    elif verificacion_o_usuario is not None:
        cerrar_sesion_admin(estado)
        raise ErrorAutorizacionAdmin(
            MENSAJE_ACCESO_NO_AUTORIZADO,
            codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
        )

    if res_candidato is not None:
        if (
            not isinstance(res_candidato, ResultadoAutenticacion)
            or not res_candidato.autenticado
            or res_candidato.codigo != CodigoResultadoAutenticacion.AUTENTICACION_EXITOSA
            or not res_candidato.usuario
            or res_candidato.comprobante_verificacion is None
        ):
            cerrar_sesion_admin(estado)
            raise ErrorAutorizacionAdmin(
                MENSAJE_ACCESO_NO_AUTORIZADO,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            )
        if comp_candidato is None:
            comp_candidato = res_candidato.comprobante_verificacion

    if not isinstance(comp_candidato, ComprobanteVerificacionCredenciales):
        cerrar_sesion_admin(estado)
        raise ErrorAutorizacionAdmin(
            MENSAJE_ACCESO_NO_AUTORIZADO,
            codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
        )

    # Consumir atómicamente el comprobante del registro del servidor (estrictamente un solo uso)
    registro_comp = _COMPROBANTES_VERIFICACION_SERVIDOR.pop(comp_candidato.id_comprobante, None)
    if registro_comp is None or registro_comp.consumido:
        cerrar_sesion_admin(estado)
        raise ErrorAutorizacionAdmin(
            MENSAJE_ACCESO_NO_AUTORIZADO,
            codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
        )
    registro_comp.consumido = True

    ahora_sistema = time.time()
    if (ahora_sistema - registro_comp.emitido_en_epoch) > _TTL_COMPROBANTE_VERIFICACION_SEGUNDOS:
        cerrar_sesion_admin(estado)
        raise ErrorAutorizacionAdmin(
            MENSAJE_ACCESO_NO_AUTORIZADO,
            codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
        )

    firma_comp_esperada = _calcular_firma_comprobante(
        id_comprobante=registro_comp.id_comprobante,
        usuario=registro_comp.usuario,
        emitido_en_epoch=registro_comp.emitido_en_epoch,
        contexto_dispositivo=registro_comp.contexto_dispositivo,
        huella_configuracion=registro_comp.huella_configuracion,
    )
    if (
        not hmac.compare_digest(comp_candidato.firma_hmac, firma_comp_esperada)
        or not hmac.compare_digest(registro_comp.firma_hmac, firma_comp_esperada)
        or not hmac.compare_digest(comp_candidato.usuario, registro_comp.usuario)
        or not hmac.compare_digest(
            comp_candidato.huella_configuracion, registro_comp.huella_configuracion
        )
    ):
        cerrar_sesion_admin(estado)
        raise ErrorAutorizacionAdmin(
            MENSAJE_ACCESO_NO_AUTORIZADO,
            codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
        )

    if res_candidato is not None and not hmac.compare_digest(
        res_candidato.usuario or "", registro_comp.usuario
    ):
        cerrar_sesion_admin(estado)
        raise ErrorAutorizacionAdmin(
            MENSAJE_ACCESO_NO_AUTORIZADO,
            codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
        )

    if usuario_explicito is not None:
        if not isinstance(usuario_explicito, str) or not hmac.compare_digest(
            usuario_explicito.strip(), registro_comp.usuario
        ):
            cerrar_sesion_admin(estado)
            raise ErrorAutorizacionAdmin(
                MENSAJE_ACCESO_NO_AUTORIZADO,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            )

    contexto_efectivo = (
        contexto_dispositivo
        if contexto_dispositivo is not None
        else registro_comp.contexto_dispositivo
    )
    if (
        contexto_efectivo == ContextoDispositivo.MOVIL
        or registro_comp.contexto_dispositivo == ContextoDispositivo.MOVIL
    ):
        cerrar_sesion_admin(estado)
        raise ErrorAutorizacionAdmin(
            MENSAJE_RESTRICCION_MOVIL_ADMIN,
            codigo=CodigoResultadoAutenticacion.DISPOSITIVO_NO_PERMITIDO,
        )

    if not _es_nombre_usuario_configurado_valido(registro_comp.usuario):
        cerrar_sesion_admin(estado)
        raise ValueError("El nombre de usuario administrativo para la sesión no es válido.")

    # Si existía un token previo en esta sesión, revocarlo antes de emitir uno nuevo
    sesion_anterior = _obtener_de_estado(estado, CLAVE_SESION_ADMIN)
    if isinstance(sesion_anterior, EstadoSesionAdmin):
        _SESIONES_ACTIVAS_SERVIDOR.pop(sesion_anterior.token_sesion, None)

    _limpiar_marcadores_publicos_manipulables(estado)

    ahora = float(marca_tiempo_epoch) if marca_tiempo_epoch is not None else ahora_sistema
    usuario_limpio = registro_comp.usuario.strip()
    token_nuevo = secrets.token_urlsafe(32)
    firma = _calcular_firma_sesion(
        usuario=usuario_limpio,
        token_sesion=token_nuevo,
        id_comprobante=registro_comp.id_comprobante,
        autenticado_en_epoch=ahora,
        contexto_dispositivo=contexto_efectivo,
    )

    estado_sesion = EstadoSesionAdmin(
        autenticado=True,
        usuario=usuario_limpio,
        token_sesion=token_nuevo,
        firma_hmac=firma,
        autenticado_en_epoch=ahora,
        ultima_actividad_epoch=ahora,
        contexto_dispositivo=contexto_efectivo,
    )
    _SESIONES_ACTIVAS_SERVIDOR[token_nuevo] = _RegistroSesionServidor(
        token_sesion=token_nuevo,
        usuario=usuario_limpio,
        id_comprobante_origen=registro_comp.id_comprobante,
        huella_configuracion=registro_comp.huella_configuracion,
        firma_hmac=firma,
        autenticado_en_epoch=ahora,
        ultima_actividad_epoch=ahora,
        contexto_dispositivo=contexto_efectivo,
    )
    estado[CLAVE_SESION_ADMIN] = estado_sesion
    return estado_sesion


def cerrar_sesion_admin(estado: Any | None) -> None:
    """Cierra la sesión administrativa actual y revoca sus marcadores de autenticación (Sección 7)."""
    if not _es_estado_escritura_valido(estado):
        return

    actual = _obtener_de_estado(estado, CLAVE_SESION_ADMIN)
    if isinstance(actual, EstadoSesionAdmin):
        _SESIONES_ACTIVAS_SERVIDOR.pop(actual.token_sesion, None)
    elif isinstance(actual, Mapping):
        token_posible = actual.get("token_sesion")
        if isinstance(token_posible, str):
            _SESIONES_ACTIVAS_SERVIDOR.pop(token_posible, None)

    estado[CLAVE_SESION_ADMIN] = None
    _limpiar_marcadores_publicos_manipulables(estado)


def esta_autenticado_en_sesion(
    estado: Any | None,
    *,
    contexto_dispositivo: ContextoDispositivo | None = None,
) -> bool:
    """Consulta si la sesión actual posee una autorización administrativa auténtica y vigente.

    Protección efectiva (Secciones 8.3 y 11.1):
    - Ignora por completo cualquier clave booleana pública (`estado['admin'] = True`, etc.).
    - Exige un objeto `EstadoSesionAdmin` cuya firma HMAC coincida con la clave secreta del
      proceso y cuyo `token_sesion` figure como activo en `_SESIONES_ACTIVAS_SERVIDOR`
      vinculado a un comprobante de verificación de credenciales genuino.
    - Deniega la autorización si el contexto de dispositivo es móvil.
    """
    if not _es_estado_lectura_valido(estado):
        return False

    contexto_efectivo = (
        contexto_dispositivo
        if contexto_dispositivo is not None
        else detectar_contexto_dispositivo(estado=estado)
    )
    if contexto_efectivo == ContextoDispositivo.MOVIL:
        return False

    objeto_sesion = _obtener_de_estado(estado, CLAVE_SESION_ADMIN)
    if not isinstance(objeto_sesion, EstadoSesionAdmin):
        return False

    if not objeto_sesion.autenticado:
        return False

    if objeto_sesion.contexto_dispositivo == ContextoDispositivo.MOVIL:
        return False

    if not objeto_sesion.token_sesion or not objeto_sesion.firma_hmac:
        return False

    registro_servidor = _SESIONES_ACTIVAS_SERVIDOR.get(objeto_sesion.token_sesion)
    if registro_servidor is None:
        return False

    if not registro_servidor.id_comprobante_origen or not registro_servidor.huella_configuracion:
        return False

    firma_esperada = _calcular_firma_sesion(
        usuario=objeto_sesion.usuario,
        token_sesion=objeto_sesion.token_sesion,
        id_comprobante=registro_servidor.id_comprobante_origen,
        autenticado_en_epoch=objeto_sesion.autenticado_en_epoch,
        contexto_dispositivo=objeto_sesion.contexto_dispositivo,
    )
    if not hmac.compare_digest(objeto_sesion.firma_hmac, firma_esperada):
        return False
    if not hmac.compare_digest(registro_servidor.firma_hmac, firma_esperada):
        return False
    if not hmac.compare_digest(registro_servidor.usuario, objeto_sesion.usuario):
        return False

    return True


def obtener_usuario_autenticado(
    estado: Any | None,
    *,
    contexto_dispositivo: ContextoDispositivo | None = None,
) -> str | None:
    """Devuelve el nombre del administrador si la sesión está autenticada válidamente, o `None`."""
    if not esta_autenticado_en_sesion(estado, contexto_dispositivo=contexto_dispositivo):
        return None
    sesion: EstadoSesionAdmin = estado[CLAVE_SESION_ADMIN]
    return sesion.usuario


def iniciar_sesion_admin(
    usuario: Any,
    contrasena: Any,
    estado: Any,
    *,
    fuente_entorno: Mapping[str, Any] | None = None,
    fuente_secretos: Mapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
) -> ResultadoAutenticacion:
    """Ejecuta el flujo completo de verificación de credenciales y registro de estado en sesión."""
    if not _es_estado_escritura_valido(estado):
        raise TypeError("Se requiere un diccionario o `st.session_state` mutable para iniciar sesión.")

    contexto_efectivo = (
        contexto_dispositivo
        if contexto_dispositivo is not None
        else detectar_contexto_dispositivo(estado=estado)
    )

    resultado_verificacion = verificar_credenciales_admin(
        usuario=usuario,
        contrasena=contrasena,
        fuente_entorno=fuente_entorno,
        fuente_secretos=fuente_secretos,
        contexto_dispositivo=contexto_efectivo,
    )

    if (
        not resultado_verificacion.autenticado
        or resultado_verificacion.usuario is None
        or resultado_verificacion.comprobante_verificacion is None
    ):
        # Asegurar que un intento fallido no deje ningún estado autenticado previo activo
        cerrar_sesion_admin(estado)
        return resultado_verificacion

    estado_sesion = registrar_autenticacion_en_sesion(
        estado=estado,
        resultado_verificacion=resultado_verificacion,
        contexto_dispositivo=contexto_efectivo,
    )
    return ResultadoAutenticacion(
        autenticado=True,
        codigo=CodigoResultadoAutenticacion.AUTENTICACION_EXITOSA,
        mensaje_usuario=MENSAJE_AUTENTICACION_EXITOSA,
        usuario=estado_sesion.usuario,
        estado_sesion=estado_sesion,
    )


def requerir_autorizacion_admin(
    estado: Mapping[str, Any] | None,
    *,
    contexto_dispositivo: ContextoDispositivo | None = None,
) -> EstadoSesionAdmin:
    """Valida en Python que la sesión actual tenga autorización administrativa vigente (Sección 8.3).

    Lanza `ErrorAutorizacionAdmin` si la sesión no está autenticada o si proviene de un
    contexto móvil. Todas las operaciones administrativas futuras deberán invocar esta guarda.
    """
    contexto_efectivo = (
        contexto_dispositivo
        if contexto_dispositivo is not None
        else detectar_contexto_dispositivo(estado=estado)
    )
    if contexto_efectivo == ContextoDispositivo.MOVIL:
        raise ErrorAutorizacionAdmin(
            MENSAJE_RESTRICCION_MOVIL_ADMIN,
            codigo=CodigoResultadoAutenticacion.DISPOSITIVO_NO_PERMITIDO,
        )

    if not esta_autenticado_en_sesion(estado, contexto_dispositivo=contexto_efectivo):
        raise ErrorAutorizacionAdmin(
            MENSAJE_ACCESO_NO_AUTORIZADO,
            codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
        )

    assert estado is not None
    return estado[CLAVE_SESION_ADMIN]
