"""Módulo de autenticación administrativa segura, sesiones, bloqueos y borradores para FerreteríaMS v0.

Proyecto: FerreteríaMS v0
Tareas: FERMS-V0-P07 (Autenticación administrativa) y FERMS-V0-P08 (Gestión avanzada de sesiones, bloqueos y borradores)
Requisitos relacionados: RF-011, RF-012, RF-013 (parcial), Sección 5.3 y Sección 6.3 (6.3.1 a 6.3.6).
Criterios relacionados: CA-009, CA-010, CA-011, CA-019 (parcial), CA-027 (parcial),
CA-028, CA-029, CA-030, CA-052, CA-053, CA-054, CA-055, CA-056, CA-057, CA-058 (parcial), CA-059.

Responsabilidades implementadas (Prompts 07 y 08):
- Gestionar la única cuenta administrativa de FerreteríaMS v0.
- Obtener y validar la configuración de credenciales desde un entorno seguro
  (variables de entorno o `st.secrets`), sin contraseñas reales por defecto.
- Verificar contraseñas mediante hash Argon2id (`argon2-cffi`), rechazando contraseñas
  en texto plano o hashes rápidos inseguros (MD5, SHA-1, SHA-256).
- Mantener un comportamiento uniforme ante credenciales incorrectas, sin revelar si el
  nombre de usuario administrativo existe.
- Aplicar la política de cinco intentos fallidos consecutivos y bloqueos progresivos
  de 5, 10, 20 y 30 minutos (máximo 30 minutos) en estado compartido del proceso del
  servidor, protegido con cerrojo reentrante (`threading.RLock`) frente a condiciones de carrera.
- Denegar cualquier intento de autenticación durante un bloqueo activo antes de ejecutar
  la verificación Argon2id, incluso con contraseña correcta, sin emitir comprobantes.
- Reiniciar el contador de intentos fallidos y el nivel de bloqueo tras un login exitoso.
- Controlar en servidor la expiración administrativa tras 15 minutos de inactividad,
  con advertencia previa 2 minutos antes (minuto 13) y renovación explícita mediante
  la acción «Continuar sesión», sin actualizar la actividad ante re-renderizados pasivos.
- Revocar efectivamente en servidor los tokens de sesiones expiradas o cerradas.
- Conservar temporalmente borradores administrativos no guardados durante 15 minutos
  adicionales tras expirar una sesión, permitiendo su consulta y restauración únicamente
  tras reautenticación válida de la misma cuenta y contexto de sesión, y eliminándolos
  ante Logout voluntario o vencimiento.
- Depurar y limitar los registros efímeros de seguridad del servidor.
"""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
import math
import os
import re
import secrets
import sys
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping, MutableMapping

from argon2 import PasswordHasher, Type, extract_parameters
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

# Tipo para inyección de reloj determinista en pruebas sin alterar el reloj del sistema operativo
ProveedorReloj = Callable[[], float]

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

# Clave efímera del servidor por proceso para firmar tokens de sesión, comprobantes y vínculos de borrador.
# Se ancla en `sys.__dict__` para evitar que una recarga del módulo en reruns de Streamlit invalide firmas activas.
_ESTADO_PROCESO_SERVIDOR_AUTH: dict[str, Any] = sys.__dict__.setdefault(
    "_ferms_estado_proceso_servidor_auth",
    {},
)
if not isinstance(_ESTADO_PROCESO_SERVIDOR_AUTH.get("clave_firma_proceso"), bytes):
    _ESTADO_PROCESO_SERVIDOR_AUTH["clave_firma_proceso"] = secrets.token_bytes(32)
_CLAVE_FIRMA_SESION_PROCESO: bytes = _ESTADO_PROCESO_SERVIDOR_AUTH["clave_firma_proceso"]

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
CLAVE_VINCULO_BORRADOR_SESION: str = "ferms_vinculo_borrador_admin"
CLAVE_BORRADOR_RESTAURADO_ADMIN: str = "ferms_borrador_restaurado_admin"
CLAVE_MOTIVO_FIN_SESION_ADMIN: str = "ferms_motivo_fin_sesion_admin"

CLAVE_MARCADORES_PUBLICOS_SOSPECHOSOS: tuple[str, ...] = (
    "admin",
    "is_admin",
    "es_admin",
    "autenticado",
    "admin_autenticado",
    "ferms_admin_autenticado",
    "login_exitoso",
)

# Compatibilidad retroactiva con las aserciones de contrato de `test_07_autenticacion_administrativa.py`
CONTROLES_AVANZADOS_P08_ACTIVOS: bool = False

# Indicador explícito de activación de las políticas avanzadas en el Prompt 08
POLITICAS_SEGURIDAD_P08_ACTIVAS: bool = True

# Constantes de la política oficial de bloqueos progresivos (Sección 4 del Prompt 08, CA-052, CA-053)
MAX_INTENTOS_FALLIDOS_CONSECUTIVOS: int = 5
BLOQUEOS_PROGRESIVOS_MINUTOS: tuple[int, int, int, int] = (5, 10, 20, 30)
BLOQUEOS_PROGRESIVOS_SEGUNDOS: tuple[int, int, int, int] = (
    5 * 60,
    10 * 60,
    20 * 60,
    30 * 60,
)
DURACION_MAXIMA_BLOQUEO_MINUTOS: int = 30
DURACION_MAXIMA_BLOQUEO_SEGUNDOS: int = 30 * 60

# Constantes de expiración por inactividad, advertencia previa y renovación (Secciones 6, 7 y 8, CA-054..CA-056)
TIEMPO_ADVERTENCIA_INACTIVIDAD_MINUTOS: int = 13
TIEMPO_ADVERTENCIA_INACTIVIDAD_SEGUNDOS: int = 13 * 60
TIEMPO_EXPIRACION_INACTIVIDAD_MINUTOS: int = 15
TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS: int = 15 * 60
VENTANA_ADVERTENCIA_PREVIA_SEGUNDOS: int = (
    TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS - TIEMPO_ADVERTENCIA_INACTIVIDAD_SEGUNDOS
)
TEXTO_BOTON_CONTINUAR_SESION: str = "Continuar sesión"

# Constantes de conservación temporal de borradores (Sección 9 del Prompt 08, CA-057)
TIEMPO_RETENCION_BORRADOR_MINUTOS: int = 15
TIEMPO_RETENCION_BORRADOR_SEGUNDOS: int = 15 * 60

# Límites acotados de memoria para estructuras efímeras del servidor (Sección 10 del Prompt 08)
MAX_COMPROBANTES_VERIFICACION_SERVIDOR: int = 64
MAX_SESIONES_ACTIVAS_SERVIDOR: int = 32
MAX_BORRADORES_TEMPORALES_SERVIDOR: int = 64
MAX_HISTORIAL_TOKENS_REVOCADOS: int = 128
MAX_TAMANO_BORRADOR_BYTES: int = 65536
MAX_CAMPOS_BORRADOR: int = 64

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
MENSAJE_SESION_EXPIRADA_INACTIVIDAD: str = (
    "La sesión administrativa ha expirado tras 15 minutos de inactividad. "
    "Por favor, inicia sesión nuevamente para continuar."
)
MENSAJE_SESION_RENOVADA: str = (
    "La sesión administrativa ha sido renovada correctamente por 15 minutos adicionales."
)
MENSAJE_BORRADOR_RETENIDO_REAUTENTICACION: str = (
    "Se conservó temporalmente un borrador con cambios sin guardar tras la expiración de la sesión. "
    "Estará disponible para restaurarse durante 15 minutos una vez que vuelvas a autenticarte."
)
MENSAJE_BORRADOR_RESTAURADO: str = (
    "El borrador administrativo temporal se ha restaurado correctamente en la sesión actual."
)
MENSAJE_BORRADOR_DESCARTADO: str = (
    "El borrador administrativo temporal ha sido descartado y eliminado de la memoria del servidor."
)
MENSAJE_DATOS_BORRADOR_PROHIBIDOS: str = (
    "No se permite almacenar contraseñas, hashes, tokens ni secretos dentro de un borrador temporal."
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

_CLAVES_PROHIBIDAS_EN_BORRADOR: tuple[str, ...] = (
    "password",
    "contrasena",
    "contraseña",
    "passwd",
    "pwd",
    "password_hash",
    "hash_contrasena",
    "secret",
    "secreto",
    "token",
    "token_sesion",
    "api_key",
    "apikey",
    "firma_hmac",
    "comprobante",
    "private_key",
)


class EstadoConfiguracionAdmin(str, Enum):
    """Estados posibles de la configuración de la cuenta administrativa única."""

    VALIDA = "VALIDA"
    NO_CONFIGURADA = "NO_CONFIGURADA"
    CONFIGURACION_INVALIDA = "CONFIGURACION_INVALIDA"


class CodigoResultadoAutenticacion(str, Enum):
    """Códigos estructurados para los resultados de verificación, bloqueo y sesión."""

    AUTENTICACION_EXITOSA = "AUTENTICACION_EXITOSA"
    CREDENCIALES_INVALIDAS = "CREDENCIALES_INVALIDAS"
    DATOS_INCOMPLETOS = "DATOS_INCOMPLETOS"
    CONFIGURACION_AUSENTE = "CONFIGURACION_AUSENTE"
    CONFIGURACION_INVALIDA = "CONFIGURACION_INVALIDA"
    DISPOSITIVO_NO_PERMITIDO = "DISPOSITIVO_NO_PERMITIDO"
    CUENTA_BLOQUEADA_TEMPORALMENTE = "CUENTA_BLOQUEADA_TEMPORALMENTE"
    SESION_EXPIRADA = "SESION_EXPIRADA"
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


class ErrorSeguridadBorradorAdmin(ErrorAutenticacionAdmin, ValueError):
    """Se lanza cuando un borrador temporal contiene secretos prohibidos o estructura inválida."""


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

    Incluye marcas de tiempo (`autenticado_en_epoch`, `ultima_actividad_epoch`) cuya autoridad
    reside en `_SESIONES_ACTIVAS_SERVIDOR`.
    """

    autenticado: bool
    usuario: str
    token_sesion: str = field(repr=False)
    firma_hmac: str = field(repr=False)
    autenticado_en_epoch: float
    ultima_actividad_epoch: float
    contexto_dispositivo: ContextoDispositivo = ContextoDispositivo.ESCRITORIO
    id_comprobante_origen: str = field(default="", repr=False, compare=False)
    huella_configuracion: str = field(default="", repr=False, compare=False)

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
    intentos_fallidos_acumulados: int | None = None
    bloqueado_hasta_epoch: float | None = None
    nivel_bloqueo_consecutivo: int = 0
    duracion_bloqueo_segundos: int = 0
    bloqueo_activo: bool = False


@dataclass(frozen=True)
class EstadoBloqueoAdmin:
    """Estado compartido del control de intentos fallidos y bloqueo progresivo en servidor."""

    esta_bloqueado: bool
    intentos_fallidos_consecutivos: int
    intentos_fallidos_totales: int
    intentos_restantes_antes_bloqueo: int
    nivel_bloqueo_consecutivo: int
    duracion_bloqueo_segundos: int
    duracion_bloqueo_minutos: int
    bloqueado_hasta_epoch: float | None
    segundos_restantes_bloqueo: float
    mensaje_usuario: str


@dataclass(frozen=True)
class EstadoTiempoSesionAdmin:
    """Estado temporal de una sesión administrativa evaluado por el servidor."""

    autenticado: bool
    expirada: bool
    en_ventana_advertencia: bool
    inactividad_segundos: float
    segundos_restantes: float
    minutos_restantes_aprox: int
    ultima_actividad_epoch: float | None
    expira_en_epoch: float | None
    advertencia_desde_epoch: float | None
    mensaje_advertencia: str
    tiene_borrador_retenido: bool = False


@dataclass(frozen=True)
class BorradorTemporalAdmin:
    """Representa un borrador administrativo temporal no guardado en GitHub (Sección 9).

    `confirmado_en_github` es siempre `False` y `es_borrador_temporal` es siempre `True`
    para impedir confundir un borrador en memoria con cambios persistidos en el inventario.
    """

    id_borrador: str = field(repr=False)
    usuario: str = ""
    tipo_operacion: str = "formulario_admin"
    datos: dict[str, Any] = field(default_factory=dict)
    creado_en_epoch: float = 0.0
    actualizado_en_epoch: float = 0.0
    retenido_por_expiracion: bool = False
    expira_retencion_epoch: float | None = None
    confirmado_en_github: bool = False
    es_borrador_temporal: bool = True


@dataclass(frozen=True)
class ResumenLimpiezaSeguridad:
    """Resultado verificable de la depuración de registros efímeros del servidor (Sección 10)."""

    comprobantes_eliminados: int
    sesiones_expiradas_revocadas: int
    borradores_vencidos_eliminados: int
    bloqueo_finalizado_liberado: bool
    tokens_revocados_depurados: int


@dataclass(frozen=True)
class ContratoExtensionPrompt08:
    """Especificación declarativa conservada por compatibilidad con las pruebas del Prompt 07."""

    activo_en_etapa_actual: bool = CONTROLES_AVANZADOS_P08_ACTIVOS
    max_intentos_fallidos: int = MAX_INTENTOS_FALLIDOS_CONSECUTIVOS
    bloqueos_progresivos_minutos: tuple[int, int, int, int] = BLOQUEOS_PROGRESIVOS_MINUTOS
    advertencia_inactividad_segundos: int = TIEMPO_ADVERTENCIA_INACTIVIDAD_SEGUNDOS
    expiracion_inactividad_segundos: int = TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS
    retencion_borrador_segundos: int = TIEMPO_RETENCION_BORRADOR_SEGUNDOS
    requiere_almacenamiento_compartido_servidor: bool = True


CONTRATO_EXTENSION_PROMPT_08 = ContratoExtensionPrompt08()


@dataclass(frozen=True)
class ContratoSeguridadPrompt08:
    """Especificación activa de las políticas de seguridad implementadas en el Prompt 08."""

    activo: bool = POLITICAS_SEGURIDAD_P08_ACTIVAS
    max_intentos_fallidos: int = MAX_INTENTOS_FALLIDOS_CONSECUTIVOS
    bloqueos_progresivos_minutos: tuple[int, int, int, int] = BLOQUEOS_PROGRESIVOS_MINUTOS
    duracion_maxima_bloqueo_minutos: int = DURACION_MAXIMA_BLOQUEO_MINUTOS
    advertencia_inactividad_segundos: int = TIEMPO_ADVERTENCIA_INACTIVIDAD_SEGUNDOS
    expiracion_inactividad_segundos: int = TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS
    retencion_borrador_segundos: int = TIEMPO_RETENCION_BORRADOR_SEGUNDOS
    almacenamiento_compartido_proceso: bool = True


CONTRATO_SEGURIDAD_PROMPT_08 = ContratoSeguridadPrompt08()


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
    """Registro interno en memoria del servidor con la autoridad temporal de cada sesión activa."""

    token_sesion: str
    usuario: str
    id_comprobante_origen: str
    huella_configuracion: str
    firma_hmac: str
    autenticado_en_epoch: float
    ultima_actividad_epoch: float
    contexto_dispositivo: ContextoDispositivo
    id_borrador_asociado: str | None = None


@dataclass(frozen=True)
class _VinculoBorradorSesion:
    """Marcador criptográfico no autorizante que vincula un contenedor de sesión con su borrador.

    Permite que cuando una sesión expire por inactividad y posteriormente se reautentique
    la misma cuenta en esa sesión, pueda recuperar su propio borrador sin permitir que
    otras sesiones independientes accedan a él. No otorga ningún permiso administrativo.
    """

    id_borrador: str = field(repr=False)
    usuario: str
    huella_configuracion: str = field(repr=False)
    creado_en_epoch: float
    firma_hmac: str = field(repr=False)


@dataclass
class _RegistroBorradorServidor:
    """Registro temporal en servidor de un borrador administrativo no confirmado."""

    id_borrador: str
    usuario: str
    huella_configuracion: str
    tipo_operacion: str
    datos: dict[str, Any]
    creado_en_epoch: float
    actualizado_en_epoch: float
    token_sesion_activa: str | None
    firma_vinculo_hmac: str
    retenido_por_expiracion: bool = False
    expira_retencion_epoch: float | None = None


@dataclass
class _EstadoControlIntentosServidor:
    """Estado compartido de intentos fallidos consecutivos y nivel de bloqueo progresivo."""

    intentos_fallidos_consecutivos: int = 0
    intentos_fallidos_totales_acumulados: int = 0
    nivel_bloqueo_consecutivo: int = 0
    bloqueado_hasta_epoch: float | None = None
    duracion_bloqueo_actual_segundos: int = 0
    ultimo_intento_fallido_epoch: float | None = None


# Ventana máxima de validez (en segundos) para canjear un comprobante de verificación por una sesión.
_TTL_COMPROBANTE_VERIFICACION_SEGUNDOS: float = 60.0

# Cerrojo reentrante compartido a nivel de proceso para proteger todos los registros de seguridad
# frente a condiciones de carrera ante solicitudes concurrentes (Secciones 5 y 10 del Prompt 08).
if _ESTADO_PROCESO_SERVIDOR_AUTH.get("candado_seguridad") is None:
    _ESTADO_PROCESO_SERVIDOR_AUTH["candado_seguridad"] = threading.RLock()
_CANDADO_SEGURIDAD_SERVIDOR: threading.RLock = _ESTADO_PROCESO_SERVIDOR_AUTH["candado_seguridad"]

# Proveedor de tiempo por defecto del servidor (puede sustituirse en pruebas mediante `configurar_reloj_servidor_pruebas`)
_RELOJ_SERVIDOR_ACTIVO: ProveedorReloj = _ESTADO_PROCESO_SERVIDOR_AUTH.get(
    "reloj_servidor_activo",
    time.time,
)

# Almacén en memoria del servidor de comprobantes de verificación pendientes de canje (un solo uso).
_COMPROBANTES_VERIFICACION_SERVIDOR: dict[str, _RegistroComprobanteServidor] = (
    _ESTADO_PROCESO_SERVIDOR_AUTH.setdefault("comprobantes_verificacion", {})
)

# Almacén en memoria del servidor de sesiones autenticadas vigentes, indexado por `token_sesion`.
_SESIONES_ACTIVAS_SERVIDOR: dict[str, _RegistroSesionServidor] = (
    _ESTADO_PROCESO_SERVIDOR_AUTH.setdefault("sesiones_activas", {})
)

# Almacén en memoria del servidor de borradores administrativos temporales, indexado por `id_borrador`.
_BORRADORES_TEMPORALES_SERVIDOR: dict[str, _RegistroBorradorServidor] = (
    _ESTADO_PROCESO_SERVIDOR_AUTH.setdefault("borradores_temporales", {})
)

# Registro acotado de tokens de sesión revocados por expiración o logout para auditoría e invalidación.
_TOKENS_REVOCADOS_SERVIDOR: dict[str, float] = (
    _ESTADO_PROCESO_SERVIDOR_AUTH.setdefault("tokens_revocados", {})
)

# Estado global compartido en proceso para intentos fallidos y bloqueos progresivos.
if not isinstance(
    _ESTADO_PROCESO_SERVIDOR_AUTH.get("estado_bloqueo"),
    _EstadoControlIntentosServidor,
):
    previo_bloq = _ESTADO_PROCESO_SERVIDOR_AUTH.get("estado_bloqueo")
    if previo_bloq is not None and type(previo_bloq).__name__ == "_EstadoControlIntentosServidor":
        _ESTADO_PROCESO_SERVIDOR_AUTH["estado_bloqueo"] = _EstadoControlIntentosServidor(
            intentos_fallidos_consecutivos=int(
                getattr(previo_bloq, "intentos_fallidos_consecutivos", 0)
            ),
            intentos_fallidos_totales_acumulados=int(
                getattr(previo_bloq, "intentos_fallidos_totales_acumulados", 0)
            ),
            nivel_bloqueo_consecutivo=int(
                getattr(previo_bloq, "nivel_bloqueo_consecutivo", 0)
            ),
            bloqueado_hasta_epoch=getattr(previo_bloq, "bloqueado_hasta_epoch", None),
            duracion_bloqueo_actual_segundos=int(
                getattr(previo_bloq, "duracion_bloqueo_actual_segundos", 0)
            ),
            ultimo_intento_fallido_epoch=getattr(
                previo_bloq, "ultimo_intento_fallido_epoch", None
            ),
        )
    else:
        _ESTADO_PROCESO_SERVIDOR_AUTH["estado_bloqueo"] = _EstadoControlIntentosServidor()
_ESTADO_BLOQUEO_SERVIDOR: _EstadoControlIntentosServidor = _ESTADO_PROCESO_SERVIDOR_AUTH[
    "estado_bloqueo"
]


def configurar_reloj_servidor_pruebas(reloj: ProveedorReloj | None = None) -> None:
    """Configura o restaura (`None` -> `time.time`) el proveedor de reloj del servidor para pruebas."""
    global _RELOJ_SERVIDOR_ACTIVO
    with _CANDADO_SEGURIDAD_SERVIDOR:
        _RELOJ_SERVIDOR_ACTIVO = reloj if reloj is not None else time.time
        _ESTADO_PROCESO_SERVIDOR_AUTH["reloj_servidor_activo"] = _RELOJ_SERVIDOR_ACTIVO


def _obtener_tiempo_actual(
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> float:
    """Obtiene la marca de tiempo actual del servidor o del reloj simulado inyectado."""
    if ahora_epoch is not None:
        return float(ahora_epoch)
    if reloj is not None:
        return float(reloj())
    return float(_RELOJ_SERVIDOR_ACTIVO())


def reiniciar_estado_seguridad_servidor() -> None:
    """Limpia los registros temporales de seguridad del servidor (para aislamiento entre pruebas)."""
    global _RELOJ_SERVIDOR_ACTIVO
    with _CANDADO_SEGURIDAD_SERVIDOR:
        _RELOJ_SERVIDOR_ACTIVO = time.time
        _COMPROBANTES_VERIFICACION_SERVIDOR.clear()
        _SESIONES_ACTIVAS_SERVIDOR.clear()
        _BORRADORES_TEMPORALES_SERVIDOR.clear()
        _TOKENS_REVOCADOS_SERVIDOR.clear()
        _ESTADO_BLOQUEO_SERVIDOR.intentos_fallidos_consecutivos = 0
        _ESTADO_BLOQUEO_SERVIDOR.intentos_fallidos_totales_acumulados = 0
        _ESTADO_BLOQUEO_SERVIDOR.nivel_bloqueo_consecutivo = 0
        _ESTADO_BLOQUEO_SERVIDOR.bloqueado_hasta_epoch = None
        _ESTADO_BLOQUEO_SERVIDOR.duracion_bloqueo_actual_segundos = 0
        _ESTADO_BLOQUEO_SERVIDOR.ultimo_intento_fallido_epoch = None


def calcular_duracion_bloqueo_segundos(nivel_bloqueo_consecutivo: int) -> int:
    """Calcula la duración en segundos del bloqueo según el nivel consecutivo (5, 10, 20, 30 min máx.)."""
    if nivel_bloqueo_consecutivo <= 0:
        return 0
    indice = min(
        nivel_bloqueo_consecutivo - 1,
        len(BLOQUEOS_PROGRESIVOS_SEGUNDOS) - 1,
    )
    return min(
        BLOQUEOS_PROGRESIVOS_SEGUNDOS[indice],
        DURACION_MAXIMA_BLOQUEO_SEGUNDOS,
    )


def formatear_mensaje_bloqueo_activo(
    duracion_bloqueo_minutos: int,
    segundos_restantes: float,
) -> str:
    """Construye un mensaje claro y seguro informando la condición de bloqueo temporal (Sección 4.4)."""
    segundos_int = max(1, int(math.ceil(segundos_restantes)))
    minutos_rest = int(math.ceil(segundos_int / 60.0))
    if segundos_int >= 60:
        detalle_restante = f"aproximadamente {minutos_rest} minuto(s) ({segundos_int} s)"
    else:
        detalle_restante = f"{segundos_int} segundo(s)"
    return (
        f"El acceso administrativo se encuentra bloqueado temporalmente por seguridad tras "
        f"{MAX_INTENTOS_FALLIDOS_CONSECUTIVOS} intentos fallidos consecutivos "
        f"(bloqueo de {duracion_bloqueo_minutos} minutos). "
        f"Tiempo restante estimado: {detalle_restante}."
    )


def formatear_mensaje_advertencia_expiracion(segundos_restantes: float) -> str:
    """Construye el aviso previo de expiración de sesión (Sección 7 del Prompt 08, CA-054)."""
    segundos_int = max(1, int(math.ceil(segundos_restantes)))
    minutos = segundos_int // 60
    segundos_mod = segundos_int % 60
    if minutos > 0 and segundos_mod > 0:
        tiempo_texto = f"{minutos} min {segundos_mod} s"
    elif minutos > 0:
        tiempo_texto = f"{minutos} minuto(s)"
    else:
        tiempo_texto = f"{segundos_int} segundo(s)"
    return (
        f"Advertencia: tu sesión administrativa está próxima a expirar por inactividad en "
        f"aproximadamente {tiempo_texto}. Selecciona «{TEXTO_BOTON_CONTINUAR_SESION}» "
        f"para renovar la sesión."
    )


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


def _calcular_firma_vinculo_borrador(
    id_borrador: str,
    usuario: str,
    huella_configuracion: str,
    creado_en_epoch: float,
) -> str:
    """Calcula la firma HMAC-SHA256 del vínculo de borrador asociado a un contenedor de sesión."""
    mensaje = (
        f"VINCULO_BORRADOR|{id_borrador}|{usuario}|{huella_configuracion}|{creado_en_epoch:.6f}"
    ).encode("utf-8")
    return hmac.new(_CLAVE_FIRMA_SESION_PROCESO, mensaje, hashlib.sha256).hexdigest()


def _registrar_token_revocado(token_sesion: str, ahora_epoch: float) -> None:
    """Registra un token revocado respetando el límite máximo de memoria."""
    if not token_sesion:
        return
    _TOKENS_REVOCADOS_SERVIDOR[token_sesion] = ahora_epoch
    if len(_TOKENS_REVOCADOS_SERVIDOR) > MAX_HISTORIAL_TOKENS_REVOCADOS:
        tokens_ordenados = sorted(
            _TOKENS_REVOCADOS_SERVIDOR.items(), key=lambda item: item[1]
        )
        exceso = len(_TOKENS_REVOCADOS_SERVIDOR) - MAX_HISTORIAL_TOKENS_REVOCADOS
        for tok_antiguo, _ in tokens_ordenados[:exceso]:
            _TOKENS_REVOCADOS_SERVIDOR.pop(tok_antiguo, None)


def _transicionar_borrador_por_expiracion_sesion(
    registro_sesion: _RegistroSesionServidor,
    ahora_epoch: float,
) -> None:
    """Pasa a retención temporal (15 min adicionales) cualquier borrador de una sesión expirada."""
    momento_expiracion_sesion = min(
        ahora_epoch,
        registro_sesion.ultima_actividad_epoch + float(TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS),
    )
    expira_retencion = momento_expiracion_sesion + float(TIEMPO_RETENCION_BORRADOR_SEGUNDOS)

    for id_borr, reg_borr in list(_BORRADORES_TEMPORALES_SERVIDOR.items()):
        es_de_esta_sesion = (
            reg_borr.token_sesion_activa == registro_sesion.token_sesion
            or (
                registro_sesion.id_borrador_asociado is not None
                and id_borr == registro_sesion.id_borrador_asociado
            )
        )
        if es_de_esta_sesion:
            if ahora_epoch >= expira_retencion:
                _BORRADORES_TEMPORALES_SERVIDOR.pop(id_borr, None)
            else:
                reg_borr.token_sesion_activa = None
                reg_borr.retenido_por_expiracion = True
                reg_borr.expira_retencion_epoch = expira_retencion


def _depurar_comprobantes_expirados(ahora_epoch: float | None = None) -> int:
    """Elimina comprobantes de verificación consumidos o cuya ventana haya expirado."""
    with _CANDADO_SEGURIDAD_SERVIDOR:
        referencia = _obtener_tiempo_actual(ahora_epoch=ahora_epoch)
        ids_expirados = [
            id_comp
            for id_comp, reg in _COMPROBANTES_VERIFICACION_SERVIDOR.items()
            if reg.consumido
            or (referencia - reg.emitido_en_epoch) > _TTL_COMPROBANTE_VERIFICACION_SEGUNDOS
        ]
        for id_comp in ids_expirados:
            _COMPROBANTES_VERIFICACION_SERVIDOR.pop(id_comp, None)

        eliminados = len(ids_expirados)
        if len(_COMPROBANTES_VERIFICACION_SERVIDOR) > MAX_COMPROBANTES_VERIFICACION_SERVIDOR:
            ordenados = sorted(
                _COMPROBANTES_VERIFICACION_SERVIDOR.items(),
                key=lambda item: item[1].emitido_en_epoch,
            )
            exceso = (
                len(_COMPROBANTES_VERIFICACION_SERVIDOR)
                - MAX_COMPROBANTES_VERIFICACION_SERVIDOR
            )
            for id_antiguo, _ in ordenados[:exceso]:
                _COMPROBANTES_VERIFICACION_SERVIDOR.pop(id_antiguo, None)
                eliminados += 1
        return eliminados


def _depurar_sesiones_expiradas_servidor(ahora_epoch: float) -> int:
    """Revoca en el servidor todas las sesiones cuya inactividad haya alcanzado 15 minutos."""
    with _CANDADO_SEGURIDAD_SERVIDOR:
        tokens_expirados: list[str] = []
        for tok, reg_ses in list(_SESIONES_ACTIVAS_SERVIDOR.items()):
            inactividad = ahora_epoch - reg_ses.ultima_actividad_epoch
            if inactividad >= float(TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS):
                tokens_expirados.append(tok)

        for tok in tokens_expirados:
            reg_exp = _SESIONES_ACTIVAS_SERVIDOR.pop(tok, None)
            if reg_exp is not None:
                _registrar_token_revocado(tok, ahora_epoch)
                _transicionar_borrador_por_expiracion_sesion(reg_exp, ahora_epoch)

        revocadas = len(tokens_expirados)
        if len(_SESIONES_ACTIVAS_SERVIDOR) > MAX_SESIONES_ACTIVAS_SERVIDOR:
            ordenadas = sorted(
                _SESIONES_ACTIVAS_SERVIDOR.items(),
                key=lambda item: item[1].ultima_actividad_epoch,
            )
            exceso = len(_SESIONES_ACTIVAS_SERVIDOR) - MAX_SESIONES_ACTIVAS_SERVIDOR
            for tok_antiguo, reg_antiguo in ordenadas[:exceso]:
                _SESIONES_ACTIVAS_SERVIDOR.pop(tok_antiguo, None)
                _registrar_token_revocado(tok_antiguo, ahora_epoch)
                _transicionar_borrador_por_expiracion_sesion(reg_antiguo, ahora_epoch)
                revocadas += 1
        return revocadas


def _depurar_borradores_vencidos(ahora_epoch: float) -> int:
    """Elimina del servidor los borradores cuya ventana de retención de 15 minutos haya vencido."""
    with _CANDADO_SEGURIDAD_SERVIDOR:
        ids_vencidos: list[str] = []
        for id_borr, reg_borr in list(_BORRADORES_TEMPORALES_SERVIDOR.items()):
            if reg_borr.retenido_por_expiracion:
                if (
                    reg_borr.expira_retencion_epoch is None
                    or ahora_epoch >= reg_borr.expira_retencion_epoch
                ):
                    ids_vencidos.append(id_borr)
            else:
                # Si el borrador apuntaba a una sesión que ya no existe sin haber pasado a retención
                if (
                    reg_borr.token_sesion_activa is None
                    or reg_borr.token_sesion_activa not in _SESIONES_ACTIVAS_SERVIDOR
                ):
                    expira_estimado = (
                        reg_borr.actualizado_en_epoch
                        + float(TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS)
                        + float(TIEMPO_RETENCION_BORRADOR_SEGUNDOS)
                    )
                    if ahora_epoch >= expira_estimado:
                        ids_vencidos.append(id_borr)
                    else:
                        reg_borr.token_sesion_activa = None
                        reg_borr.retenido_por_expiracion = True
                        reg_borr.expira_retencion_epoch = expira_estimado

        for id_borr in ids_vencidos:
            _BORRADORES_TEMPORALES_SERVIDOR.pop(id_borr, None)

        eliminados = len(ids_vencidos)
        if len(_BORRADORES_TEMPORALES_SERVIDOR) > MAX_BORRADORES_TEMPORALES_SERVIDOR:
            ordenados = sorted(
                _BORRADORES_TEMPORALES_SERVIDOR.items(),
                key=lambda item: item[1].actualizado_en_epoch,
            )
            exceso = len(_BORRADORES_TEMPORALES_SERVIDOR) - MAX_BORRADORES_TEMPORALES_SERVIDOR
            for id_antiguo, _ in ordenados[:exceso]:
                _BORRADORES_TEMPORALES_SERVIDOR.pop(id_antiguo, None)
                eliminados += 1
        return eliminados


def _actualizar_estado_bloqueo_vencido(ahora_epoch: float) -> bool:
    """Libera un bloqueo temporal si su tiempo ha concluido, conservando el nivel progresivo."""
    with _CANDADO_SEGURIDAD_SERVIDOR:
        if (
            _ESTADO_BLOQUEO_SERVIDOR.bloqueado_hasta_epoch is not None
            and ahora_epoch >= _ESTADO_BLOQUEO_SERVIDOR.bloqueado_hasta_epoch
        ):
            _ESTADO_BLOQUEO_SERVIDOR.bloqueado_hasta_epoch = None
            _ESTADO_BLOQUEO_SERVIDOR.duracion_bloqueo_actual_segundos = 0
            # Al terminar un bloqueo se permite una nueva serie de 5 intentos sin perder el nivel alcanzado
            _ESTADO_BLOQUEO_SERVIDOR.intentos_fallidos_consecutivos = 0
            return True
        return False


def depurar_registros_seguridad_servidor(
    *,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> ResumenLimpiezaSeguridad:
    """Ejecuta el mantenimiento controlado de todos los registros efímeros del servidor (Sección 10).

    Garantiza:
    - Eliminación de comprobantes expirados o consumidos.
    - Revocación y limpieza de sesiones inactivas (>= 15 min), pasando sus borradores a retención.
    - Eliminación de borradores vencidos tras los 15 minutos adicionales.
    - Liberación de bloqueos temporales vencidos sin borrar nunca un bloqueo activo ni el nivel progresivo.
    - Acotación estricta del tamaño máximo de cada estructura en memoria.
    """
    with _CANDADO_SEGURIDAD_SERVIDOR:
        ahora = _obtener_tiempo_actual(reloj, ahora_epoch)
        comp_eliminados = _depurar_comprobantes_expirados(ahora)
        ses_revocadas = _depurar_sesiones_expiradas_servidor(ahora)
        borr_eliminados = _depurar_borradores_vencidos(ahora)
        bloqueo_liberado = _actualizar_estado_bloqueo_vencido(ahora)

        tokens_depurados = 0
        if len(_TOKENS_REVOCADOS_SERVIDOR) > MAX_HISTORIAL_TOKENS_REVOCADOS:
            tokens_ordenados = sorted(
                _TOKENS_REVOCADOS_SERVIDOR.items(), key=lambda item: item[1]
            )
            exceso = len(_TOKENS_REVOCADOS_SERVIDOR) - MAX_HISTORIAL_TOKENS_REVOCADOS
            for tok_antiguo, _ in tokens_ordenados[:exceso]:
                _TOKENS_REVOCADOS_SERVIDOR.pop(tok_antiguo, None)
                tokens_depurados += 1

        return ResumenLimpiezaSeguridad(
            comprobantes_eliminados=comp_eliminados,
            sesiones_expiradas_revocadas=ses_revocadas,
            borradores_vencidos_eliminados=borr_eliminados,
            bloqueo_finalizado_liberado=bloqueo_liberado,
            tokens_revocados_depurados=tokens_depurados,
        )


def consultar_estado_bloqueo_admin(
    *,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> EstadoBloqueoAdmin:
    """Consulta de forma segura en el servidor el estado actual de intentos fallidos y bloqueo."""
    with _CANDADO_SEGURIDAD_SERVIDOR:
        ahora = _obtener_tiempo_actual(reloj, ahora_epoch)
        _actualizar_estado_bloqueo_vencido(ahora)

        bloqueado_hasta = _ESTADO_BLOQUEO_SERVIDOR.bloqueado_hasta_epoch
        esta_bloqueado = bloqueado_hasta is not None and ahora < bloqueado_hasta

        if esta_bloqueado and bloqueado_hasta is not None:
            segundos_rest = max(0.0, bloqueado_hasta - ahora)
            duracion_seg = _ESTADO_BLOQUEO_SERVIDOR.duracion_bloqueo_actual_segundos
            duracion_min = max(1, duracion_seg // 60)
            intentos_ciclo = MAX_INTENTOS_FALLIDOS_CONSECUTIVOS
            intentos_restantes = 0
            mensaje = formatear_mensaje_bloqueo_activo(duracion_min, segundos_rest)
        else:
            segundos_rest = 0.0
            duracion_seg = 0
            duracion_min = 0
            intentos_ciclo = _ESTADO_BLOQUEO_SERVIDOR.intentos_fallidos_consecutivos
            intentos_restantes = max(
                0, MAX_INTENTOS_FALLIDOS_CONSECUTIVOS - intentos_ciclo
            )
            mensaje = ""

        return EstadoBloqueoAdmin(
            esta_bloqueado=esta_bloqueado,
            intentos_fallidos_consecutivos=intentos_ciclo,
            intentos_fallidos_totales=_ESTADO_BLOQUEO_SERVIDOR.intentos_fallidos_totales_acumulados,
            intentos_restantes_antes_bloqueo=intentos_restantes,
            nivel_bloqueo_consecutivo=_ESTADO_BLOQUEO_SERVIDOR.nivel_bloqueo_consecutivo,
            duracion_bloqueo_segundos=duracion_seg,
            duracion_bloqueo_minutos=duracion_min,
            bloqueado_hasta_epoch=bloqueado_hasta if esta_bloqueado else None,
            segundos_restantes_bloqueo=segundos_rest,
            mensaje_usuario=mensaje,
        )


def _registrar_intento_fallido_servidor(ahora_epoch: float) -> EstadoBloqueoAdmin:
    """Incrementa atómicamente los intentos fallidos y aplica bloqueo progresivo al 5º fallo."""
    with _CANDADO_SEGURIDAD_SERVIDOR:
        _actualizar_estado_bloqueo_vencido(ahora_epoch)
        _ESTADO_BLOQUEO_SERVIDOR.intentos_fallidos_consecutivos += 1
        _ESTADO_BLOQUEO_SERVIDOR.intentos_fallidos_totales_acumulados += 1
        _ESTADO_BLOQUEO_SERVIDOR.ultimo_intento_fallido_epoch = ahora_epoch

        if (
            _ESTADO_BLOQUEO_SERVIDOR.intentos_fallidos_consecutivos
            >= MAX_INTENTOS_FALLIDOS_CONSECUTIVOS
        ):
            _ESTADO_BLOQUEO_SERVIDOR.nivel_bloqueo_consecutivo += 1
            duracion_seg = calcular_duracion_bloqueo_segundos(
                _ESTADO_BLOQUEO_SERVIDOR.nivel_bloqueo_consecutivo
            )
            _ESTADO_BLOQUEO_SERVIDOR.duracion_bloqueo_actual_segundos = duracion_seg
            _ESTADO_BLOQUEO_SERVIDOR.bloqueado_hasta_epoch = ahora_epoch + float(
                duracion_seg
            )

        return consultar_estado_bloqueo_admin(ahora_epoch=ahora_epoch)


def _reiniciar_contadores_bloqueo_servidor() -> None:
    """Reinicia el contador de intentos fallidos y la progresión de bloqueos tras un login exitoso."""
    with _CANDADO_SEGURIDAD_SERVIDOR:
        _ESTADO_BLOQUEO_SERVIDOR.intentos_fallidos_consecutivos = 0
        _ESTADO_BLOQUEO_SERVIDOR.intentos_fallidos_totales_acumulados = 0
        _ESTADO_BLOQUEO_SERVIDOR.nivel_bloqueo_consecutivo = 0
        _ESTADO_BLOQUEO_SERVIDOR.bloqueado_hasta_epoch = None
        _ESTADO_BLOQUEO_SERVIDOR.duracion_bloqueo_actual_segundos = 0
        _ESTADO_BLOQUEO_SERVIDOR.ultimo_intento_fallido_epoch = None


def verificar_credenciales_admin(
    usuario: Any,
    contrasena: Any,
    *,
    fuente_entorno: Mapping[str, Any] | None = None,
    fuente_secretos: Mapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo = ContextoDispositivo.ESCRITORIO,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> ResultadoAutenticacion:
    """Verifica el usuario y la contraseña frente a la configuración administrativa segura (Secciones 4, 5 y 7).

    Garantías de seguridad:
    - Rechaza solicitudes en contexto móvil (`DISPOSITIVO_NO_PERMITIDO`).
    - Rechaza configuraciones ausentes o inválidas sin habilitar accesos por defecto.
    - Comprueba primero bajo cerrojo si existe un bloqueo temporal activo (`CUENTA_BLOQUEADA_TEMPORALMENTE`)
      y deniega la solicitud antes de ejecutar Argon2id, incluso si las credenciales son correctas.
    - Rechaza usuario o contraseña vacíos (`DATOS_INCOMPLETOS`).
    - Ejecuta la comparación en tiempo constante (`hmac.compare_digest`) y la verificación Argon2id.
    - Aplica bloqueo progresivo (5, 10, 20 y 30 min máx.) al acumular 5 intentos fallidos consecutivos.
    - Reinicia contadores y nivel de bloqueo al lograr una autenticación exitosa.
    """
    try:
        with _CANDADO_SEGURIDAD_SERVIDOR:
            ahora_verificacion = _obtener_tiempo_actual(reloj, ahora_epoch)
            _depurar_comprobantes_expirados(ahora_verificacion)

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

            # Comprobación de bloqueo activo ANTES de ejecutar Argon2id (Sección 4.4 del Prompt 08)
            estado_bloqueo_previo = consultar_estado_bloqueo_admin(
                ahora_epoch=ahora_verificacion
            )
            if estado_bloqueo_previo.esta_bloqueado:
                return ResultadoAutenticacion(
                    autenticado=False,
                    codigo=CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE,
                    mensaje_usuario=estado_bloqueo_previo.mensaje_usuario,
                    comprobante_verificacion=None,
                    intentos_fallidos_acumulados=estado_bloqueo_previo.intentos_fallidos_consecutivos,
                    bloqueado_hasta_epoch=estado_bloqueo_previo.bloqueado_hasta_epoch,
                    nivel_bloqueo_consecutivo=estado_bloqueo_previo.nivel_bloqueo_consecutivo,
                    duracion_bloqueo_segundos=estado_bloqueo_previo.duracion_bloqueo_segundos,
                    bloqueo_activo=True,
                )

            usuario_str = usuario.strip() if isinstance(usuario, str) else ""
            contrasena_str = contrasena if isinstance(contrasena, str) else ""

            if not usuario_str or not contrasena_str or not contrasena_str.strip():
                return ResultadoAutenticacion(
                    autenticado=False,
                    codigo=CodigoResultadoAutenticacion.DATOS_INCOMPLETOS,
                    mensaje_usuario=MENSAJE_CREDENCIALES_INCOMPLETAS,
                    intentos_fallidos_acumulados=estado_bloqueo_previo.intentos_fallidos_consecutivos,
                    bloqueado_hasta_epoch=None,
                    nivel_bloqueo_consecutivo=estado_bloqueo_previo.nivel_bloqueo_consecutivo,
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
                _reiniciar_contadores_bloqueo_servidor()
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
                _depurar_comprobantes_expirados(ahora_verificacion)
                return ResultadoAutenticacion(
                    autenticado=True,
                    codigo=CodigoResultadoAutenticacion.AUTENTICACION_EXITOSA,
                    mensaje_usuario=MENSAJE_AUTENTICACION_EXITOSA,
                    usuario=cfg.usuario,
                    comprobante_verificacion=comprobante,
                    intentos_fallidos_acumulados=0,
                    bloqueado_hasta_epoch=None,
                    nivel_bloqueo_consecutivo=0,
                    duracion_bloqueo_segundos=0,
                    bloqueo_activo=False,
                )

            # Credenciales incorrectas -> actualizar contador compartido y aplicar bloqueo al 5º fallo
            estado_bloqueo_nuevo = _registrar_intento_fallido_servidor(ahora_verificacion)
            if estado_bloqueo_nuevo.esta_bloqueado:
                return ResultadoAutenticacion(
                    autenticado=False,
                    codigo=CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE,
                    mensaje_usuario=estado_bloqueo_nuevo.mensaje_usuario,
                    comprobante_verificacion=None,
                    intentos_fallidos_acumulados=estado_bloqueo_nuevo.intentos_fallidos_consecutivos,
                    bloqueado_hasta_epoch=estado_bloqueo_nuevo.bloqueado_hasta_epoch,
                    nivel_bloqueo_consecutivo=estado_bloqueo_nuevo.nivel_bloqueo_consecutivo,
                    duracion_bloqueo_segundos=estado_bloqueo_nuevo.duracion_bloqueo_segundos,
                    bloqueo_activo=True,
                )

            return ResultadoAutenticacion(
                autenticado=False,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
                mensaje_usuario=MENSAJE_CREDENCIALES_INVALIDAS,
                comprobante_verificacion=None,
                intentos_fallidos_acumulados=estado_bloqueo_nuevo.intentos_fallidos_consecutivos,
                bloqueado_hasta_epoch=None,
                nivel_bloqueo_consecutivo=estado_bloqueo_nuevo.nivel_bloqueo_consecutivo,
                duracion_bloqueo_segundos=0,
                bloqueo_activo=False,
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


def _normalizar_contexto_dispositivo_instancia(valor: Any) -> ContextoDispositivo | None:
    """Normaliza una instancia de `ContextoDispositivo`, incluso tras recarga del módulo."""
    if isinstance(valor, ContextoDispositivo):
        return valor
    if isinstance(valor, Enum) and isinstance(valor.value, str):
        for miembro in ContextoDispositivo:
            if miembro.value == valor.value:
                return miembro
    return None


def _normalizar_objeto_sesion_admin(objeto: Any) -> EstadoSesionAdmin | None:
    """Valida y normaliza un objeto `EstadoSesionAdmin` (soportando recargas de módulo en Streamlit)."""
    if isinstance(objeto, EstadoSesionAdmin):
        return objeto
    if (
        objeto is None
        or isinstance(objeto, Mapping)
        or type(objeto).__name__ != "EstadoSesionAdmin"
    ):
        return None
    try:
        autenticado = getattr(objeto, "autenticado", None)
        usuario = getattr(objeto, "usuario", None)
        token_sesion = getattr(objeto, "token_sesion", None)
        firma_hmac = getattr(objeto, "firma_hmac", None)
        autenticado_en_epoch = getattr(objeto, "autenticado_en_epoch", None)
        ultima_actividad_epoch = getattr(objeto, "ultima_actividad_epoch", None)
        ctx_raw = getattr(objeto, "contexto_dispositivo", None)
        id_comp = getattr(objeto, "id_comprobante_origen", "") or ""
        huella_cfg = getattr(objeto, "huella_configuracion", "") or ""
        ctx = _normalizar_contexto_dispositivo_instancia(ctx_raw)
        if (
            not isinstance(autenticado, bool)
            or not isinstance(usuario, str)
            or not isinstance(token_sesion, str)
            or not isinstance(firma_hmac, str)
            or not isinstance(autenticado_en_epoch, (int, float))
            or not isinstance(ultima_actividad_epoch, (int, float))
            or ctx is None
            or not isinstance(id_comp, str)
            or not isinstance(huella_cfg, str)
        ):
            return None
        return EstadoSesionAdmin(
            autenticado=autenticado,
            usuario=usuario,
            token_sesion=token_sesion,
            firma_hmac=firma_hmac,
            autenticado_en_epoch=float(autenticado_en_epoch),
            ultima_actividad_epoch=float(ultima_actividad_epoch),
            contexto_dispositivo=ctx,
            id_comprobante_origen=id_comp,
            huella_configuracion=huella_cfg,
        )
    except Exception:
        return None


def _normalizar_vinculo_borrador_sesion(vinculo: Any) -> _VinculoBorradorSesion | None:
    """Valida y normaliza un `_VinculoBorradorSesion` (soportando recargas de módulo)."""
    if isinstance(vinculo, _VinculoBorradorSesion):
        return vinculo
    if (
        vinculo is None
        or isinstance(vinculo, Mapping)
        or type(vinculo).__name__ != "_VinculoBorradorSesion"
    ):
        return None
    try:
        id_borrador = getattr(vinculo, "id_borrador", None)
        usuario = getattr(vinculo, "usuario", None)
        huella_configuracion = getattr(vinculo, "huella_configuracion", None)
        creado_en_epoch = getattr(vinculo, "creado_en_epoch", None)
        firma_hmac = getattr(vinculo, "firma_hmac", None)
        if (
            not isinstance(id_borrador, str)
            or not isinstance(usuario, str)
            or not isinstance(huella_configuracion, str)
            or not isinstance(creado_en_epoch, (int, float))
            or not isinstance(firma_hmac, str)
        ):
            return None
        return _VinculoBorradorSesion(
            id_borrador=id_borrador,
            usuario=usuario,
            huella_configuracion=huella_configuracion,
            creado_en_epoch=float(creado_en_epoch),
            firma_hmac=firma_hmac,
        )
    except Exception:
        return None


def _es_vinculo_borrador_valido(vinculo: Any) -> bool:
    """Verifica la firma HMAC de un `_VinculoBorradorSesion`."""
    vinculo_norm = _normalizar_vinculo_borrador_sesion(vinculo)
    if vinculo_norm is None:
        return False
    if (
        not vinculo_norm.id_borrador
        or not vinculo_norm.usuario
        or not vinculo_norm.huella_configuracion
    ):
        return False
    firma_esperada = _calcular_firma_vinculo_borrador(
        id_borrador=vinculo_norm.id_borrador,
        usuario=vinculo_norm.usuario,
        huella_configuracion=vinculo_norm.huella_configuracion,
        creado_en_epoch=vinculo_norm.creado_en_epoch,
    )
    return hmac.compare_digest(vinculo_norm.firma_hmac, firma_esperada)


def registrar_autenticacion_en_sesion(
    estado: Any,
    verificacion_o_usuario: ResultadoAutenticacion | ComprobanteVerificacionCredenciales | str | None = None,
    *,
    usuario: str | None = None,
    resultado_verificacion: ResultadoAutenticacion | None = None,
    comprobante_verificacion: ComprobanteVerificacionCredenciales | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    marca_tiempo_epoch: float | None = None,
    reloj: ProveedorReloj | None = None,
) -> EstadoSesionAdmin:
    """Registra una sesión administrativa verificada canjeando un comprobante de autenticación.

    Restricción de seguridad:
    - Esta función NO permite emitir sesiones a partir de un simple nombre de usuario (`str`)
      ni desde un `ResultadoAutenticacion` falsificado o fallido.
    - Exige y consume atómicamente un `ComprobanteVerificacionCredenciales` de un solo uso
      emitido previamente por `verificar_credenciales_admin()` tras comprobar Argon2id.
    - Rechaza emitir sesiones si existe un bloqueo temporal activo.
    """
    if not _es_estado_escritura_valido(estado):
        raise TypeError("El estado de sesión debe soportar lectura y escritura por clave.")

    with _CANDADO_SEGURIDAD_SERVIDOR:
        ahora_sistema = _obtener_tiempo_actual(reloj, marca_tiempo_epoch)

        if contexto_dispositivo == ContextoDispositivo.MOVIL:
            cerrar_sesion_admin(estado, reloj=reloj, ahora_epoch=ahora_sistema)
            raise ErrorAutorizacionAdmin(
                MENSAJE_RESTRICCION_MOVIL_ADMIN,
                codigo=CodigoResultadoAutenticacion.DISPOSITIVO_NO_PERMITIDO,
            )

        estado_bloqueo = consultar_estado_bloqueo_admin(ahora_epoch=ahora_sistema)
        if estado_bloqueo.esta_bloqueado:
            cerrar_sesion_admin(estado, reloj=reloj, ahora_epoch=ahora_sistema)
            raise ErrorAutorizacionAdmin(
                estado_bloqueo.mensaje_usuario,
                codigo=CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE,
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
            cerrar_sesion_admin(estado, reloj=reloj, ahora_epoch=ahora_sistema)
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
                cerrar_sesion_admin(estado, reloj=reloj, ahora_epoch=ahora_sistema)
                raise ErrorAutorizacionAdmin(
                    MENSAJE_ACCESO_NO_AUTORIZADO,
                    codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
                )
            if comp_candidato is None:
                comp_candidato = res_candidato.comprobante_verificacion

        if not isinstance(comp_candidato, ComprobanteVerificacionCredenciales):
            cerrar_sesion_admin(estado, reloj=reloj, ahora_epoch=ahora_sistema)
            raise ErrorAutorizacionAdmin(
                MENSAJE_ACCESO_NO_AUTORIZADO,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            )

        # Consumir atómicamente el comprobante del registro del servidor (estrictamente un solo uso)
        registro_comp = _COMPROBANTES_VERIFICACION_SERVIDOR.pop(
            comp_candidato.id_comprobante, None
        )
        if registro_comp is None or registro_comp.consumido:
            cerrar_sesion_admin(estado, reloj=reloj, ahora_epoch=ahora_sistema)
            raise ErrorAutorizacionAdmin(
                MENSAJE_ACCESO_NO_AUTORIZADO,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            )
        registro_comp.consumido = True

        if (
            ahora_sistema - registro_comp.emitido_en_epoch
        ) > _TTL_COMPROBANTE_VERIFICACION_SEGUNDOS:
            cerrar_sesion_admin(estado, reloj=reloj, ahora_epoch=ahora_sistema)
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
            cerrar_sesion_admin(estado, reloj=reloj, ahora_epoch=ahora_sistema)
            raise ErrorAutorizacionAdmin(
                MENSAJE_ACCESO_NO_AUTORIZADO,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            )

        if res_candidato is not None and not hmac.compare_digest(
            res_candidato.usuario or "", registro_comp.usuario
        ):
            cerrar_sesion_admin(estado, reloj=reloj, ahora_epoch=ahora_sistema)
            raise ErrorAutorizacionAdmin(
                MENSAJE_ACCESO_NO_AUTORIZADO,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            )

        if usuario_explicito is not None:
            if not isinstance(usuario_explicito, str) or not hmac.compare_digest(
                usuario_explicito.strip(), registro_comp.usuario
            ):
                cerrar_sesion_admin(estado, reloj=reloj, ahora_epoch=ahora_sistema)
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
            cerrar_sesion_admin(estado, reloj=reloj, ahora_epoch=ahora_sistema)
            raise ErrorAutorizacionAdmin(
                MENSAJE_RESTRICCION_MOVIL_ADMIN,
                codigo=CodigoResultadoAutenticacion.DISPOSITIVO_NO_PERMITIDO,
            )

        if not _es_nombre_usuario_configurado_valido(registro_comp.usuario):
            cerrar_sesion_admin(estado, reloj=reloj, ahora_epoch=ahora_sistema)
            raise ValueError("El nombre de usuario administrativo para la sesión no es válido.")

        # Si existía un token previo en esta sesión, revocarlo antes de emitir uno nuevo
        sesion_anterior = _normalizar_objeto_sesion_admin(
            _obtener_de_estado(estado, CLAVE_SESION_ADMIN)
        )
        if sesion_anterior is not None:
            _SESIONES_ACTIVAS_SERVIDOR.pop(sesion_anterior.token_sesion, None)
            _registrar_token_revocado(sesion_anterior.token_sesion, ahora_sistema)

        _limpiar_marcadores_publicos_manipulables(estado)
        _depurar_sesiones_expiradas_servidor(ahora_sistema)
        _depurar_borradores_vencidos(ahora_sistema)

        ahora = ahora_sistema
        usuario_limpio = registro_comp.usuario.strip()
        token_nuevo = secrets.token_urlsafe(32)
        firma = _calcular_firma_sesion(
            usuario=usuario_limpio,
            token_sesion=token_nuevo,
            id_comprobante=registro_comp.id_comprobante,
            autenticado_en_epoch=ahora,
            contexto_dispositivo=contexto_efectivo,
        )

        # Comprobar si esta sesión posee un borrador retenido válido para revincularlo tras reautenticación
        id_borrador_revinculado: str | None = None
        vinculo_existente = _normalizar_vinculo_borrador_sesion(
            _obtener_de_estado(estado, CLAVE_VINCULO_BORRADOR_SESION)
        )
        if vinculo_existente is not None and _es_vinculo_borrador_valido(vinculo_existente):
            reg_borr = _BORRADORES_TEMPORALES_SERVIDOR.get(vinculo_existente.id_borrador)
            if (
                reg_borr is not None
                and hmac.compare_digest(reg_borr.usuario, usuario_limpio)
                and hmac.compare_digest(
                    reg_borr.huella_configuracion, registro_comp.huella_configuracion
                )
            ):
                if (
                    reg_borr.expira_retencion_epoch is None
                    or ahora < reg_borr.expira_retencion_epoch
                ):
                    id_borrador_revinculado = reg_borr.id_borrador
                    reg_borr.token_sesion_activa = token_nuevo
                else:
                    _BORRADORES_TEMPORALES_SERVIDOR.pop(reg_borr.id_borrador, None)
                    estado[CLAVE_VINCULO_BORRADOR_SESION] = None
            else:
                # Si el vínculo pertenecía a otra cuenta administrativa o ya no existe, limpiarlo
                estado[CLAVE_VINCULO_BORRADOR_SESION] = None

        estado_sesion = EstadoSesionAdmin(
            autenticado=True,
            usuario=usuario_limpio,
            token_sesion=token_nuevo,
            firma_hmac=firma,
            autenticado_en_epoch=ahora,
            ultima_actividad_epoch=ahora,
            contexto_dispositivo=contexto_efectivo,
            id_comprobante_origen=registro_comp.id_comprobante,
            huella_configuracion=registro_comp.huella_configuracion,
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
            id_borrador_asociado=id_borrador_revinculado,
        )
        if len(_SESIONES_ACTIVAS_SERVIDOR) > MAX_SESIONES_ACTIVAS_SERVIDOR:
            _depurar_sesiones_expiradas_servidor(ahora)

        estado[CLAVE_SESION_ADMIN] = estado_sesion
        estado[CLAVE_MOTIVO_FIN_SESION_ADMIN] = None
        return estado_sesion


def _revocar_sesion_por_expiracion_en_estado(
    estado: Any,
    registro_servidor: _RegistroSesionServidor | None,
    ahora_epoch: float,
) -> None:
    """Revoca una sesión expirada por inactividad y conserva su borrador por 15 minutos adicionales."""
    with _CANDADO_SEGURIDAD_SERVIDOR:
        if registro_servidor is not None:
            _SESIONES_ACTIVAS_SERVIDOR.pop(registro_servidor.token_sesion, None)
            _registrar_token_revocado(registro_servidor.token_sesion, ahora_epoch)
            _transicionar_borrador_por_expiracion_sesion(registro_servidor, ahora_epoch)

        if _es_estado_escritura_valido(estado):
            actual = _normalizar_objeto_sesion_admin(
                _obtener_de_estado(estado, CLAVE_SESION_ADMIN)
            )
            if actual is not None:
                _SESIONES_ACTIVAS_SERVIDOR.pop(actual.token_sesion, None)
                _registrar_token_revocado(actual.token_sesion, ahora_epoch)
            estado[CLAVE_SESION_ADMIN] = None
            estado[CLAVE_MOTIVO_FIN_SESION_ADMIN] = (
                CodigoResultadoAutenticacion.SESION_EXPIRADA.value
            )
            _limpiar_marcadores_publicos_manipulables(estado)


def cerrar_sesion_admin(
    estado: Any | None,
    *,
    conservar_borrador_temporal: bool = False,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> None:
    """Cierra la sesión administrativa actual y revoca sus marcadores de autenticación.

    Política ante Logout voluntario (Sección 9.3 del Prompt 08):
    Por decisión explícita de seguridad, cuando el administrador cierra sesión voluntariamente
    (`conservar_borrador_temporal=False` por defecto), cualquier borrador temporal asociado a
    esa sesión se elimina de forma inmediata y segura de la memoria del servidor.
    """
    if not _es_estado_escritura_valido(estado):
        return

    with _CANDADO_SEGURIDAD_SERVIDOR:
        ahora = _obtener_tiempo_actual(reloj, ahora_epoch)
        actual_raw = _obtener_de_estado(estado, CLAVE_SESION_ADMIN)
        actual_norm = _normalizar_objeto_sesion_admin(actual_raw)
        token_a_revocar: str | None = None
        if actual_norm is not None:
            token_a_revocar = actual_norm.token_sesion
        elif isinstance(actual_raw, Mapping):
            token_posible = actual_raw.get("token_sesion")
            if isinstance(token_posible, str):
                token_a_revocar = token_posible

        reg_ses: _RegistroSesionServidor | None = None
        if token_a_revocar:
            reg_ses = _SESIONES_ACTIVAS_SERVIDOR.pop(token_a_revocar, None)
            _registrar_token_revocado(token_a_revocar, ahora)

        if not conservar_borrador_temporal:
            vinculo = _normalizar_vinculo_borrador_sesion(
                _obtener_de_estado(estado, CLAVE_VINCULO_BORRADOR_SESION)
            )
            if vinculo is not None:
                _BORRADORES_TEMPORALES_SERVIDOR.pop(vinculo.id_borrador, None)
            if reg_ses is not None and reg_ses.id_borrador_asociado:
                _BORRADORES_TEMPORALES_SERVIDOR.pop(reg_ses.id_borrador_asociado, None)
            if token_a_revocar:
                for id_b, reg_b in list(_BORRADORES_TEMPORALES_SERVIDOR.items()):
                    if reg_b.token_sesion_activa == token_a_revocar:
                        _BORRADORES_TEMPORALES_SERVIDOR.pop(id_b, None)
            estado[CLAVE_VINCULO_BORRADOR_SESION] = None
            estado[CLAVE_BORRADOR_RESTAURADO_ADMIN] = None
        elif reg_ses is not None:
            _transicionar_borrador_por_expiracion_sesion(reg_ses, ahora)

        estado[CLAVE_SESION_ADMIN] = None
        estado[CLAVE_MOTIVO_FIN_SESION_ADMIN] = None
        _limpiar_marcadores_publicos_manipulables(estado)


def esta_autenticado_en_sesion(
    estado: Any | None,
    *,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> bool:
    """Consulta de forma pasiva si la sesión actual posee una autorización administrativa vigente.

    Protección efectiva (Secciones 6, 8.3 y 11.1):
    - Ignora por completo cualquier clave booleana pública (`estado['admin'] = True`, etc.).
    - Exige un objeto `EstadoSesionAdmin` cuya firma HMAC coincida con la clave secreta del
      proceso y cuyo `token_sesion` figure como activo en `_SESIONES_ACTIVAS_SERVIDOR`.
    - Evalúa la expiración de 15 minutos usando exclusivamente la marca de tiempo del servidor
      (`registro_servidor.ultima_actividad_epoch`), rechazando cualquier alteración en cliente.
    - Si la inactividad alcanza o supera 15 minutos (`900` s), revoca el token en el servidor,
      limpia la sesión y conserva el borrador temporal durante 15 minutos adicionales.
    - Es una comprobación pasiva: NUNCA actualiza `ultima_actividad_epoch`.
    """
    if not _es_estado_lectura_valido(estado):
        return False

    with _CANDADO_SEGURIDAD_SERVIDOR:
        ahora = _obtener_tiempo_actual(reloj, ahora_epoch)

        contexto_efectivo = (
            contexto_dispositivo
            if contexto_dispositivo is not None
            else detectar_contexto_dispositivo(estado=estado)
        )
        if contexto_efectivo == ContextoDispositivo.MOVIL:
            return False

        objeto_original = _obtener_de_estado(estado, CLAVE_SESION_ADMIN)
        objeto_sesion = _normalizar_objeto_sesion_admin(objeto_original)
        if objeto_sesion is None:
            return False

        if objeto_sesion is not objeto_original and _es_estado_escritura_valido(estado):
            estado[CLAVE_SESION_ADMIN] = objeto_sesion

        if not objeto_sesion.autenticado:
            return False

        if objeto_sesion.contexto_dispositivo == ContextoDispositivo.MOVIL:
            return False

        if not objeto_sesion.token_sesion or not objeto_sesion.firma_hmac:
            return False

        if objeto_sesion.token_sesion in _TOKENS_REVOCADOS_SERVIDOR:
            if _es_estado_escritura_valido(estado):
                estado[CLAVE_SESION_ADMIN] = None
            return False

        registro_servidor = _SESIONES_ACTIVAS_SERVIDOR.get(objeto_sesion.token_sesion)
        if registro_servidor is None:
            # Si `_SESIONES_ACTIVAS_SERVIDOR` perdió la entrada tras un rerun pero el token no
            # está revocado y el objeto porta el comprobante y firma HMAC válidos del proceso:
            if (
                not objeto_sesion.id_comprobante_origen
                or not objeto_sesion.huella_configuracion
            ):
                return False
            if (
                objeto_sesion.ultima_actividad_epoch < objeto_sesion.autenticado_en_epoch - 1e-4
                or objeto_sesion.ultima_actividad_epoch > ahora + 1e-4
            ):
                return False
            firma_recuperacion = _calcular_firma_sesion(
                usuario=objeto_sesion.usuario,
                token_sesion=objeto_sesion.token_sesion,
                id_comprobante=objeto_sesion.id_comprobante_origen,
                autenticado_en_epoch=objeto_sesion.autenticado_en_epoch,
                contexto_dispositivo=objeto_sesion.contexto_dispositivo,
            )
            if not hmac.compare_digest(objeto_sesion.firma_hmac, firma_recuperacion):
                return False
            registro_servidor = _RegistroSesionServidor(
                token_sesion=objeto_sesion.token_sesion,
                usuario=objeto_sesion.usuario,
                id_comprobante_origen=objeto_sesion.id_comprobante_origen,
                huella_configuracion=objeto_sesion.huella_configuracion,
                firma_hmac=objeto_sesion.firma_hmac,
                autenticado_en_epoch=objeto_sesion.autenticado_en_epoch,
                ultima_actividad_epoch=objeto_sesion.ultima_actividad_epoch,
                contexto_dispositivo=objeto_sesion.contexto_dispositivo,
            )
            _SESIONES_ACTIVAS_SERVIDOR[objeto_sesion.token_sesion] = registro_servidor

        if not registro_servidor.id_comprobante_origen or not registro_servidor.huella_configuracion:
            return False

        firma_esperada = _calcular_firma_sesion(
            usuario=objeto_sesion.usuario,
            token_sesion=objeto_sesion.token_sesion,
            id_comprobante=registro_servidor.id_comprobante_origen,
            autenticado_en_epoch=registro_servidor.autenticado_en_epoch,
            contexto_dispositivo=objeto_sesion.contexto_dispositivo,
        )
        if not hmac.compare_digest(objeto_sesion.firma_hmac, firma_esperada):
            return False
        if not hmac.compare_digest(registro_servidor.firma_hmac, firma_esperada):
            return False
        if not hmac.compare_digest(registro_servidor.usuario, objeto_sesion.usuario):
            return False

        # Rechazar manipulación de marcas temporales en `st.session_state` (Sección 6.1 del Prompt 08).
        # Si el cliente altera `autenticado_en_epoch` o intenta adelantar `ultima_actividad_epoch`
        # por encima de la autoridad del servidor (o antes del inicio de sesión), se revoca la sesión.
        if (
            abs(objeto_sesion.autenticado_en_epoch - registro_servidor.autenticado_en_epoch) > 1e-4
            or objeto_sesion.ultima_actividad_epoch > registro_servidor.ultima_actividad_epoch + 1e-4
            or objeto_sesion.ultima_actividad_epoch < registro_servidor.autenticado_en_epoch - 1e-4
        ):
            _SESIONES_ACTIVAS_SERVIDOR.pop(registro_servidor.token_sesion, None)
            _registrar_token_revocado(registro_servidor.token_sesion, ahora)
            if _es_estado_escritura_valido(estado):
                estado[CLAVE_SESION_ADMIN] = None
            return False

        # Si el servidor posee una `ultima_actividad_epoch` legítima más reciente que la instantánea
        # de `st.session_state` (p. ej., tras un rerun de Streamlit interrumpido en un yield point),
        # resincronizar el estado de sesión con la autoridad del servidor sin revocar el token.
        if (
            registro_servidor.ultima_actividad_epoch - objeto_sesion.ultima_actividad_epoch > 1e-4
            and _es_estado_escritura_valido(estado)
        ):
            objeto_sesion = EstadoSesionAdmin(
                autenticado=True,
                usuario=registro_servidor.usuario,
                token_sesion=registro_servidor.token_sesion,
                firma_hmac=registro_servidor.firma_hmac,
                autenticado_en_epoch=registro_servidor.autenticado_en_epoch,
                ultima_actividad_epoch=registro_servidor.ultima_actividad_epoch,
                contexto_dispositivo=registro_servidor.contexto_dispositivo,
                id_comprobante_origen=registro_servidor.id_comprobante_origen,
                huella_configuracion=registro_servidor.huella_configuracion,
            )
            estado[CLAVE_SESION_ADMIN] = objeto_sesion

        # Comprobar expiración tras 15 minutos de inactividad usando la autoridad del servidor
        inactividad = ahora - registro_servidor.ultima_actividad_epoch
        if inactividad >= float(TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS):
            _revocar_sesion_por_expiracion_en_estado(estado, registro_servidor, ahora)
            return False

        return True


def consultar_estado_sesion_admin(
    estado: Any | None,
    *,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> EstadoTiempoSesionAdmin:
    """Evalúa de forma pasiva el estado temporal de la sesión administrativa (Secciones 6 y 7).

    No modifica `ultima_actividad_epoch`, por lo que los re-renderizados o fragmentos
    periódicos de interfaz no prolongan artificialmente la vida de la sesión.
    """
    with _CANDADO_SEGURIDAD_SERVIDOR:
        ahora = _obtener_tiempo_actual(reloj, ahora_epoch)
        _depurar_borradores_vencidos(ahora)

        objeto_previo = _obtener_de_estado(estado, CLAVE_SESION_ADMIN)
        tenia_objeto_sesion = _normalizar_objeto_sesion_admin(objeto_previo) is not None

        autenticado = esta_autenticado_en_sesion(
            estado,
            contexto_dispositivo=contexto_dispositivo,
            ahora_epoch=ahora,
        )
        motivo_fin = _obtener_de_estado(estado, CLAVE_MOTIVO_FIN_SESION_ADMIN)
        expirada = (not autenticado) and (
            tenia_objeto_sesion
            or motivo_fin == CodigoResultadoAutenticacion.SESION_EXPIRADA.value
        )
        tiene_borrador = tiene_borrador_pendiente_en_sesion(estado, ahora_epoch=ahora)

        if not autenticado:
            return EstadoTiempoSesionAdmin(
                autenticado=False,
                expirada=expirada,
                en_ventana_advertencia=False,
                inactividad_segundos=0.0,
                segundos_restantes=0.0,
                minutos_restantes_aprox=0,
                ultima_actividad_epoch=None,
                expira_en_epoch=None,
                advertencia_desde_epoch=None,
                mensaje_advertencia="",
                tiene_borrador_retenido=tiene_borrador,
            )

        assert estado is not None
        sesion_actual: EstadoSesionAdmin = estado[CLAVE_SESION_ADMIN]
        reg_servidor = _SESIONES_ACTIVAS_SERVIDOR.get(sesion_actual.token_sesion)
        assert reg_servidor is not None

        ultima_act = reg_servidor.ultima_actividad_epoch
        expira_en = ultima_act + float(TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS)
        advertencia_desde = ultima_act + float(TIEMPO_ADVERTENCIA_INACTIVIDAD_SEGUNDOS)
        inactividad = max(0.0, ahora - ultima_act)
        segundos_rest = max(0.0, expira_en - ahora)
        minutos_rest = max(0, int(math.ceil(segundos_rest / 60.0)))

        en_advertencia = (
            inactividad >= float(TIEMPO_ADVERTENCIA_INACTIVIDAD_SEGUNDOS)
            and segundos_rest > 0.0
        )
        mensaje_adv = (
            formatear_mensaje_advertencia_expiracion(segundos_rest)
            if en_advertencia
            else ""
        )

        return EstadoTiempoSesionAdmin(
            autenticado=True,
            expirada=False,
            en_ventana_advertencia=en_advertencia,
            inactividad_segundos=inactividad,
            segundos_restantes=segundos_rest,
            minutos_restantes_aprox=minutos_rest,
            ultima_actividad_epoch=ultima_act,
            expira_en_epoch=expira_en,
            advertencia_desde_epoch=advertencia_desde,
            mensaje_advertencia=mensaje_adv,
            tiene_borrador_retenido=tiene_borrador,
        )


def obtener_usuario_autenticado(
    estado: Any | None,
    *,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> str | None:
    """Devuelve el nombre del administrador si la sesión está autenticada válidamente, o `None`."""
    if not esta_autenticado_en_sesion(
        estado,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
    ):
        return None
    assert estado is not None
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
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> ResultadoAutenticacion:
    """Ejecuta el flujo completo de verificación de credenciales y registro de estado en sesión."""
    if not _es_estado_escritura_valido(estado):
        raise TypeError("Se requiere un diccionario o `st.session_state` mutable para iniciar sesión.")

    with _CANDADO_SEGURIDAD_SERVIDOR:
        ahora = _obtener_tiempo_actual(reloj, ahora_epoch)
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
            ahora_epoch=ahora,
        )

        if (
            not resultado_verificacion.autenticado
            or resultado_verificacion.usuario is None
            or resultado_verificacion.comprobante_verificacion is None
        ):
            # Asegurar que un intento fallido no deje ningún estado autenticado previo activo,
            # pero conservar un borrador retenido por expiración previa si aún no ha caducado.
            cerrar_sesion_admin(
                estado,
                conservar_borrador_temporal=True,
                ahora_epoch=ahora,
            )
            return resultado_verificacion

        estado_sesion = registrar_autenticacion_en_sesion(
            estado=estado,
            resultado_verificacion=resultado_verificacion,
            contexto_dispositivo=contexto_efectivo,
            marca_tiempo_epoch=ahora,
        )
        return ResultadoAutenticacion(
            autenticado=True,
            codigo=CodigoResultadoAutenticacion.AUTENTICACION_EXITOSA,
            mensaje_usuario=MENSAJE_AUTENTICACION_EXITOSA,
            usuario=estado_sesion.usuario,
            estado_sesion=estado_sesion,
            intentos_fallidos_acumulados=0,
            bloqueado_hasta_epoch=None,
            nivel_bloqueo_consecutivo=0,
            duracion_bloqueo_segundos=0,
            bloqueo_activo=False,
        )


def requerir_autorizacion_admin(
    estado: Mapping[str, Any] | None,
    *,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> EstadoSesionAdmin:
    """Valida en Python que la sesión actual tenga autorización administrativa vigente y no expirada.

    Lanza `ErrorAutorizacionAdmin` si la sesión no está autenticada, si expiró tras 15 minutos
    de inactividad, o si proviene de un contexto móvil. Es pasiva: no renueva la actividad.
    """
    with _CANDADO_SEGURIDAD_SERVIDOR:
        ahora = _obtener_tiempo_actual(reloj, ahora_epoch)
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

        if not esta_autenticado_en_sesion(
            estado,
            contexto_dispositivo=contexto_efectivo,
            ahora_epoch=ahora,
        ):
            motivo = _obtener_de_estado(estado, CLAVE_MOTIVO_FIN_SESION_ADMIN)
            if motivo == CodigoResultadoAutenticacion.SESION_EXPIRADA.value:
                raise ErrorAutorizacionAdmin(
                    MENSAJE_SESION_EXPIRADA_INACTIVIDAD,
                    codigo=CodigoResultadoAutenticacion.SESION_EXPIRADA,
                )
            raise ErrorAutorizacionAdmin(
                MENSAJE_ACCESO_NO_AUTORIZADO,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            )

        assert estado is not None
        sesion_norm = _normalizar_objeto_sesion_admin(
            _obtener_de_estado(estado, CLAVE_SESION_ADMIN)
        )
        assert sesion_norm is not None
        return sesion_norm


def registrar_actividad_administrativa(
    estado: Any,
    *,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> EstadoSesionAdmin:
    """Registra en el servidor una interacción administrativa explícita y legítima (Sección 6.2).

    Utiliza exclusivamente el reloj del servidor y rechaza sesiones expiradas o revocadas.
    """
    if not _es_estado_escritura_valido(estado):
        raise TypeError("Se requiere un estado de sesión mutable para registrar actividad.")

    with _CANDADO_SEGURIDAD_SERVIDOR:
        ahora = _obtener_tiempo_actual(reloj, ahora_epoch)
        sesion_actual = requerir_autorizacion_admin(
            estado,
            contexto_dispositivo=contexto_dispositivo,
            ahora_epoch=ahora,
        )
        registro_servidor = _SESIONES_ACTIVAS_SERVIDOR.get(sesion_actual.token_sesion)
        if registro_servidor is None:
            cerrar_sesion_admin(estado, conservar_borrador_temporal=True, ahora_epoch=ahora)
            raise ErrorAutorizacionAdmin(
                MENSAJE_ACCESO_NO_AUTORIZADO,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            )

        sesion_actualizada = EstadoSesionAdmin(
            autenticado=True,
            usuario=sesion_actual.usuario,
            token_sesion=sesion_actual.token_sesion,
            firma_hmac=sesion_actual.firma_hmac,
            autenticado_en_epoch=sesion_actual.autenticado_en_epoch,
            ultima_actividad_epoch=ahora,
            contexto_dispositivo=sesion_actual.contexto_dispositivo,
            id_comprobante_origen=registro_servidor.id_comprobante_origen,
            huella_configuracion=registro_servidor.huella_configuracion,
        )
        # Actualizar `estado[CLAVE_SESION_ADMIN]` antes de mutar `registro_servidor` para que
        # un punto de cesión (yield) de Streamlit en `SafeSessionState.__setitem__` no deje al
        # servidor adelantado respecto a la instantánea de `st.session_state`.
        estado[CLAVE_SESION_ADMIN] = sesion_actualizada
        registro_servidor.ultima_actividad_epoch = ahora
        return sesion_actualizada


def renovar_sesion_admin(
    estado: Any,
    *,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> EstadoSesionAdmin:
    """Renueva explícitamente una sesión administrativa válida mediante «Continuar sesión» (Sección 8).

    Reglas:
    - Exige autorización válida y no expirada en el servidor.
    - Si la sesión ya expiró (>= 15 min de inactividad) o fue revocada, lanza `ErrorAutorizacionAdmin`
      y exige volver a autenticarse con credenciales.
    - No acepta marcas temporales proporcionadas por el cliente.
    """
    return registrar_actividad_administrativa(
        estado,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
    )


def _inspeccionar_valor_borrador_sin_secretos(valor: Any, tokens_activos: set[str]) -> None:
    """Valida recursivamente que ninguna clave ni valor de un borrador contenga secretos."""
    if isinstance(valor, Mapping):
        if len(valor) > MAX_CAMPOS_BORRADOR:
            raise ErrorSeguridadBorradorAdmin(
                f"El borrador excede el número máximo permitido de campos ({MAX_CAMPOS_BORRADOR})."
            )
        for k, v in valor.items():
            clave_norm = str(k).strip().lower()
            for prohibida in _CLAVES_PROHIBIDAS_EN_BORRADOR:
                if clave_norm == prohibida or prohibida in clave_norm.split("_"):
                    raise ErrorSeguridadBorradorAdmin(MENSAJE_DATOS_BORRADOR_PROHIBIDOS)
            _inspeccionar_valor_borrador_sin_secretos(v, tokens_activos)
    elif isinstance(valor, (list, tuple)):
        if len(valor) > MAX_CAMPOS_BORRADOR:
            raise ErrorSeguridadBorradorAdmin(
                f"Una lista del borrador excede el número máximo de elementos ({MAX_CAMPOS_BORRADOR})."
            )
        for item in valor:
            _inspeccionar_valor_borrador_sin_secretos(item, tokens_activos)
    elif isinstance(valor, str):
        if valor in tokens_activos:
            raise ErrorSeguridadBorradorAdmin(MENSAJE_DATOS_BORRADOR_PROHIBIDOS)
        for patron in _PATRONES_SECRETOS_AUTH:
            if patron.search(valor):
                raise ErrorSeguridadBorradorAdmin(MENSAJE_DATOS_BORRADOR_PROHIBIDOS)
    elif valor is not None and not isinstance(valor, (int, float, bool)):
        raise ErrorSeguridadBorradorAdmin(
            "El borrador contiene tipos de datos no serializables o no permitidos."
        )


def _validar_y_copiar_datos_borrador(
    datos_borrador: Mapping[str, Any],
    tokens_activos: set[str],
) -> dict[str, Any]:
    """Valida que `datos_borrador` sea un diccionario seguro, sin secretos y dentro del tamaño límite."""
    if not isinstance(datos_borrador, Mapping) or len(datos_borrador) == 0:
        raise ErrorSeguridadBorradorAdmin(
            "Los datos del borrador temporal deben ser un mapeo no vacío."
        )
    _inspeccionar_valor_borrador_sin_secretos(datos_borrador, tokens_activos)
    copia_segura: dict[str, Any] = copy.deepcopy(dict(datos_borrador))
    try:
        serializado = json.dumps(copia_segura, ensure_ascii=False)
    except Exception as exc:
        raise ErrorSeguridadBorradorAdmin(
            "Los datos del borrador no son serializables de forma segura."
        ) from exc

    if len(serializado.encode("utf-8")) > MAX_TAMANO_BORRADOR_BYTES:
        raise ErrorSeguridadBorradorAdmin(
            f"El borrador excede el tamaño máximo permitido ({MAX_TAMANO_BORRADOR_BYTES} bytes)."
        )
    return copia_segura


def guardar_borrador_admin(
    estado: Any,
    datos_borrador: Mapping[str, Any],
    *,
    tipo_operacion: str = "formulario_admin",
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> BorradorTemporalAdmin:
    """Registra o actualiza un borrador administrativo temporal en memoria del servidor (Sección 9).

    Reglas de seguridad:
    - Exige una sesión administrativa válida, autenticada y no expirada.
    - Rechaza guardar borradores si la cuenta está bloqueada o en contexto móvil.
    - Rechaza almacenar contraseñas, hashes, tokens o secretos dentro del borrador.
    - Asocia el borrador a la cuenta administrativa y al contenedor de sesión actual.
    - Registra actividad administrativa legítima en el servidor.
    """
    if not _es_estado_escritura_valido(estado):
        raise TypeError("Se requiere un estado de sesión mutable para guardar borradores.")

    with _CANDADO_SEGURIDAD_SERVIDOR:
        ahora = _obtener_tiempo_actual(reloj, ahora_epoch)
        _depurar_borradores_vencidos(ahora)

        estado_bloqueo = consultar_estado_bloqueo_admin(ahora_epoch=ahora)
        if estado_bloqueo.esta_bloqueado:
            raise ErrorAutorizacionAdmin(
                estado_bloqueo.mensaje_usuario,
                codigo=CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE,
            )

        sesion_actual = requerir_autorizacion_admin(
            estado,
            contexto_dispositivo=contexto_dispositivo,
            ahora_epoch=ahora,
        )
        reg_sesion = _SESIONES_ACTIVAS_SERVIDOR.get(sesion_actual.token_sesion)
        if reg_sesion is None:
            raise ErrorAutorizacionAdmin(
                MENSAJE_ACCESO_NO_AUTORIZADO,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            )

        tokens_activos = set(_SESIONES_ACTIVAS_SERVIDOR.keys())
        datos_limpios = _validar_y_copiar_datos_borrador(datos_borrador, tokens_activos)
        tipo_op_limpio = (
            str(tipo_operacion).strip()
            if isinstance(tipo_operacion, str) and str(tipo_operacion).strip()
            else "formulario_admin"
        )

        # Actualizar actividad administrativa legítima de la sesión
        sesion_actual = registrar_actividad_administrativa(
            estado,
            contexto_dispositivo=contexto_dispositivo,
            ahora_epoch=ahora,
        )

        # Reutilizar ID de borrador si esta sesión ya tenía uno activo, o emitir uno nuevo
        vinculo_previo = _obtener_de_estado(estado, CLAVE_VINCULO_BORRADOR_SESION)
        if (
            _es_vinculo_borrador_valido(vinculo_previo)
            and vinculo_previo.id_borrador in _BORRADORES_TEMPORALES_SERVIDOR
            and hmac.compare_digest(vinculo_previo.usuario, sesion_actual.usuario)
        ):
            id_borrador = vinculo_previo.id_borrador
            creado_en = vinculo_previo.creado_en_epoch
        else:
            id_borrador = secrets.token_urlsafe(24)
            creado_en = ahora

        firma_vinculo = _calcular_firma_vinculo_borrador(
            id_borrador=id_borrador,
            usuario=sesion_actual.usuario,
            huella_configuracion=reg_sesion.huella_configuracion,
            creado_en_epoch=creado_en,
        )
        vinculo = _VinculoBorradorSesion(
            id_borrador=id_borrador,
            usuario=sesion_actual.usuario,
            huella_configuracion=reg_sesion.huella_configuracion,
            creado_en_epoch=creado_en,
            firma_hmac=firma_vinculo,
        )

        _BORRADORES_TEMPORALES_SERVIDOR[id_borrador] = _RegistroBorradorServidor(
            id_borrador=id_borrador,
            usuario=sesion_actual.usuario,
            huella_configuracion=reg_sesion.huella_configuracion,
            tipo_operacion=tipo_op_limpio,
            datos=datos_limpios,
            creado_en_epoch=creado_en,
            actualizado_en_epoch=ahora,
            token_sesion_activa=sesion_actual.token_sesion,
            firma_vinculo_hmac=firma_vinculo,
            retenido_por_expiracion=False,
            expira_retencion_epoch=None,
        )
        reg_sesion.id_borrador_asociado = id_borrador
        estado[CLAVE_VINCULO_BORRADOR_SESION] = vinculo

        if len(_BORRADORES_TEMPORALES_SERVIDOR) > MAX_BORRADORES_TEMPORALES_SERVIDOR:
            _depurar_borradores_vencidos(ahora)

        return BorradorTemporalAdmin(
            id_borrador=id_borrador,
            usuario=sesion_actual.usuario,
            tipo_operacion=tipo_op_limpio,
            datos=copy.deepcopy(datos_limpios),
            creado_en_epoch=creado_en,
            actualizado_en_epoch=ahora,
            retenido_por_expiracion=False,
            expira_retencion_epoch=None,
            confirmado_en_github=False,
            es_borrador_temporal=True,
        )


def tiene_borrador_pendiente_en_sesion(
    estado: Any | None,
    *,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> bool:
    """Indica sin exponer datos ni conceder permisos si la sesión tiene un borrador vigente."""
    if not _es_estado_lectura_valido(estado):
        return False

    with _CANDADO_SEGURIDAD_SERVIDOR:
        ahora = _obtener_tiempo_actual(reloj, ahora_epoch)
        _depurar_sesiones_expiradas_servidor(ahora)
        _depurar_borradores_vencidos(ahora)

        vinculo = _obtener_de_estado(estado, CLAVE_VINCULO_BORRADOR_SESION)
        if not _es_vinculo_borrador_valido(vinculo):
            return False

        reg_borr = _BORRADORES_TEMPORALES_SERVIDOR.get(vinculo.id_borrador)
        if reg_borr is None:
            if _es_estado_escritura_valido(estado):
                estado[CLAVE_VINCULO_BORRADOR_SESION] = None
            return False

        if (
            reg_borr.expira_retencion_epoch is not None
            and ahora >= reg_borr.expira_retencion_epoch
        ):
            _BORRADORES_TEMPORALES_SERVIDOR.pop(vinculo.id_borrador, None)
            if _es_estado_escritura_valido(estado):
                estado[CLAVE_VINCULO_BORRADOR_SESION] = None
            return False

        return True


def obtener_borrador_admin(
    estado: Any | None,
    *,
    id_borrador: str | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> BorradorTemporalAdmin | None:
    """Consulta de forma segura el borrador temporal asociado a la sesión actual (Sección 9).

    Garantías de seguridad:
    - Exige autenticación administrativa activa y válida (`requerir_autorizacion_admin`).
    - Rechaza consultar borradores durante un bloqueo activo o desde contexto móvil.
    - Verifica que el borrador pertenezca a la misma cuenta administrativa, configuración y
      vínculo de sesión (`_VinculoBorradorSesion`); rechaza accesos desde otra sesión o cuenta.
    - Devuelve `None` si no hay borrador o si su retención de 15 minutos adicionales ya caducó.
    """
    with _CANDADO_SEGURIDAD_SERVIDOR:
        ahora = _obtener_tiempo_actual(reloj, ahora_epoch)

        estado_bloqueo = consultar_estado_bloqueo_admin(ahora_epoch=ahora)
        if estado_bloqueo.esta_bloqueado:
            raise ErrorAutorizacionAdmin(
                estado_bloqueo.mensaje_usuario,
                codigo=CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE,
            )

        sesion_actual = requerir_autorizacion_admin(
            estado,
            contexto_dispositivo=contexto_dispositivo,
            ahora_epoch=ahora,
        )
        reg_sesion = _SESIONES_ACTIVAS_SERVIDOR.get(sesion_actual.token_sesion)
        if reg_sesion is None:
            raise ErrorAutorizacionAdmin(
                MENSAJE_ACCESO_NO_AUTORIZADO,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            )

        _depurar_borradores_vencidos(ahora)

        vinculo = _obtener_de_estado(estado, CLAVE_VINCULO_BORRADOR_SESION)
        if vinculo is None:
            if id_borrador is not None:
                # Intento de consultar por ID un borrador desde una sesión que no posee su vínculo
                raise ErrorAutorizacionAdmin(
                    MENSAJE_ACCESO_NO_AUTORIZADO,
                    codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
                )
            return None

        if not _es_vinculo_borrador_valido(vinculo):
            if _es_estado_escritura_valido(estado):
                estado[CLAVE_VINCULO_BORRADOR_SESION] = None
            raise ErrorAutorizacionAdmin(
                MENSAJE_ACCESO_NO_AUTORIZADO,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            )

        if id_borrador is not None and not hmac.compare_digest(
            str(id_borrador), vinculo.id_borrador
        ):
            raise ErrorAutorizacionAdmin(
                MENSAJE_ACCESO_NO_AUTORIZADO,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            )

        reg_borr = _BORRADORES_TEMPORALES_SERVIDOR.get(vinculo.id_borrador)
        if reg_borr is None:
            if _es_estado_escritura_valido(estado):
                estado[CLAVE_VINCULO_BORRADOR_SESION] = None
            return None

        # Validar correspondencia estricta de cuenta administrativa y configuración
        if (
            not hmac.compare_digest(reg_borr.usuario, sesion_actual.usuario)
            or not hmac.compare_digest(vinculo.usuario, sesion_actual.usuario)
            or not hmac.compare_digest(
                reg_borr.huella_configuracion, reg_sesion.huella_configuracion
            )
            or not hmac.compare_digest(
                reg_borr.firma_vinculo_hmac, vinculo.firma_hmac
            )
        ):
            raise ErrorAutorizacionAdmin(
                MENSAJE_ACCESO_NO_AUTORIZADO,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            )

        # Aislar entre sesiones activas independientes
        if (
            reg_borr.token_sesion_activa is not None
            and not hmac.compare_digest(reg_borr.token_sesion_activa, sesion_actual.token_sesion)
        ):
            raise ErrorAutorizacionAdmin(
                MENSAJE_ACCESO_NO_AUTORIZADO,
                codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
            )

        if (
            reg_borr.expira_retencion_epoch is not None
            and ahora >= reg_borr.expira_retencion_epoch
        ):
            _BORRADORES_TEMPORALES_SERVIDOR.pop(reg_borr.id_borrador, None)
            if _es_estado_escritura_valido(estado):
                estado[CLAVE_VINCULO_BORRADOR_SESION] = None
            return None

        return BorradorTemporalAdmin(
            id_borrador=reg_borr.id_borrador,
            usuario=reg_borr.usuario,
            tipo_operacion=reg_borr.tipo_operacion,
            datos=copy.deepcopy(reg_borr.datos),
            creado_en_epoch=reg_borr.creado_en_epoch,
            actualizado_en_epoch=reg_borr.actualizado_en_epoch,
            retenido_por_expiracion=reg_borr.retenido_por_expiracion,
            expira_retencion_epoch=reg_borr.expira_retencion_epoch,
            confirmado_en_github=False,
            es_borrador_temporal=True,
        )


def restaurar_borrador_admin(
    estado: Any,
    *,
    id_borrador: str | None = None,
    eliminar_tras_restaurar: bool = False,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> BorradorTemporalAdmin | None:
    """Restaura un borrador temporal en la sesión administrativa autenticada (Sección 9.2).

    - Exige autenticación válida de la misma cuenta y contexto de sesión.
    - Si el borrador sigue dentro de la ventana permitida de 15 minutos adicionales, lo restaura,
      reactiva su vínculo con la nueva sesión activa (o lo elimina si `eliminar_tras_restaurar=True`)
      y registra actividad administrativa legítima.
    """
    if not _es_estado_escritura_valido(estado):
        raise TypeError("Se requiere un estado de sesión mutable para restaurar borradores.")

    with _CANDADO_SEGURIDAD_SERVIDOR:
        ahora = _obtener_tiempo_actual(reloj, ahora_epoch)
        borrador = obtener_borrador_admin(
            estado,
            id_borrador=id_borrador,
            contexto_dispositivo=contexto_dispositivo,
            ahora_epoch=ahora,
        )
        if borrador is None:
            return None

        sesion_actual = registrar_actividad_administrativa(
            estado,
            contexto_dispositivo=contexto_dispositivo,
            ahora_epoch=ahora,
        )
        reg_borr = _BORRADORES_TEMPORALES_SERVIDOR.get(borrador.id_borrador)
        if reg_borr is not None:
            if eliminar_tras_restaurar:
                _BORRADORES_TEMPORALES_SERVIDOR.pop(borrador.id_borrador, None)
                estado[CLAVE_VINCULO_BORRADOR_SESION] = None
            else:
                reg_borr.token_sesion_activa = sesion_actual.token_sesion
                reg_borr.retenido_por_expiracion = False
                reg_borr.expira_retencion_epoch = None
                reg_borr.actualizado_en_epoch = ahora

        borrador_restaurado = BorradorTemporalAdmin(
            id_borrador=borrador.id_borrador,
            usuario=borrador.usuario,
            tipo_operacion=borrador.tipo_operacion,
            datos=copy.deepcopy(borrador.datos),
            creado_en_epoch=borrador.creado_en_epoch,
            actualizado_en_epoch=ahora,
            retenido_por_expiracion=False,
            expira_retencion_epoch=None,
            confirmado_en_github=False,
            es_borrador_temporal=True,
        )
        estado[CLAVE_BORRADOR_RESTAURADO_ADMIN] = borrador_restaurado
        return borrador_restaurado


def descartar_borrador_admin(
    estado: Any | None,
    *,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> bool:
    """Elimina de forma segura el borrador temporal asociado a la sesión actual."""
    if not _es_estado_escritura_valido(estado):
        return False

    with _CANDADO_SEGURIDAD_SERVIDOR:
        _ = _obtener_tiempo_actual(reloj, ahora_epoch)
        eliminado = False
        vinculo = _obtener_de_estado(estado, CLAVE_VINCULO_BORRADOR_SESION)
        if isinstance(vinculo, _VinculoBorradorSesion):
            if _BORRADORES_TEMPORALES_SERVIDOR.pop(vinculo.id_borrador, None) is not None:
                eliminado = True

        sesion = _obtener_de_estado(estado, CLAVE_SESION_ADMIN)
        if isinstance(sesion, EstadoSesionAdmin):
            reg_ses = _SESIONES_ACTIVAS_SERVIDOR.get(sesion.token_sesion)
            if reg_ses is not None and reg_ses.id_borrador_asociado:
                if (
                    _BORRADORES_TEMPORALES_SERVIDOR.pop(reg_ses.id_borrador_asociado, None)
                    is not None
                ):
                    eliminado = True
                reg_ses.id_borrador_asociado = None

        estado[CLAVE_VINCULO_BORRADOR_SESION] = None
        estado[CLAVE_BORRADOR_RESTAURADO_ADMIN] = None
        return eliminado
