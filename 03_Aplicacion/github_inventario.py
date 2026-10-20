"""Módulo de lectura segura del inventario maestro desde GitHub API.

Proyecto: FerreteríaMS v0
Tarea: FERMS-V0-P03
Requisitos relacionados: RF-022, RF-023, RF-024, RF-025, RF-027, RF-028, RF-029, RF-030, RF-038.
Criterios relacionados: CA-020 (parcial), CA-021 (parcial), CA-022, CA-024 (parcial),
CA-025 (parcial), CA-036 (pendiente de despliegue), CA-042.

Este módulo implementa exclusivamente operaciones de SOLO LECTURA (HTTP GET) contra GitHub API.
No crea, modifica, reemplaza ni elimina archivos locales ni remotos.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping

import sys

_DIRECTORIO_ACTUAL = Path(__file__).resolve().parent
if str(_DIRECTORIO_ACTUAL) not in sys.path:
    sys.path.insert(0, str(_DIRECTORIO_ACTUAL))

import inventario as motor_inventario  # noqa: E402
from inventario import (  # noqa: E402
    DetalleErrorInventario,
    ErrorArchivoCorrupto,
    ErrorEstructuraInventario,
    ErrorInventario,
    ErrorProteccionInventario,
    ErrorValidacionInventario,
    EstadoExistenciaRemota,
    InventarioDatos,
    cargar_inventario_excel,
    preparar_inicializacion_segura,
)

# Parámetros oficiales del repositorio aprobados en 02_Prompts/03_Lectura_GitHub.md (Sección 4)
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_PROPIETARIO_DEFECTO = "JunyMSAI"
GITHUB_REPOSITORIO_DEFECTO = "FerreteriaMS"
GITHUB_RAMA_DEFECTO = "main"
GITHUB_RUTA_INVENTARIO_DEFECTO = "03_Aplicacion/inventario.xlsx"
GITHUB_API_VERSION = "2022-11-28"
GITHUB_TIMEOUT_SEGUNDOS_DEFECTO = 15.0

DOMINIOS_API_GITHUB_PERMITIDOS: tuple[str, ...] = ("api.github.com",)
DOMINIOS_DESCARGA_GITHUB_PERMITIDOS: tuple[str, ...] = (
    "raw.githubusercontent.com",
    "api.github.com",
)
DOMINIOS_REDIRECCION_GITHUB_PERMITIDOS: tuple[str, ...] = (
    "api.github.com",
    "raw.githubusercontent.com",
    "objects.githubusercontent.com",
)
MAX_REDIRECCIONES_GITHUB = 3
_URLOPEN_ORIGINAL = urllib.request.urlopen

MARCA_SECRETO_OCULTO = "[SECRETO_PROTEGIDO]"

_PATRONES_SECRETOS = (
    re.compile(r"(?i)(bearer\s+)[^\s,;\"']+"),
    re.compile(r"(?i)(token\s+)[^\s,;\"']+"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]+\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]+\b"),
)


class CodigoErrorGitHub(str, Enum):
    """Códigos identificables para los 13 escenarios de error definidos en la Sección 7 del Prompt 03."""

    ARCHIVO_REMOTO_INEXISTENTE = "ARCHIVO_REMOTO_INEXISTENTE"
    REPOSITORIO_INACCESIBLE = "REPOSITORIO_INACCESIBLE"
    RAMA_INEXISTENTE = "RAMA_INEXISTENTE"
    ACCESO_DENEGADO = "ACCESO_DENEGADO"
    CREDENCIAL_INVALIDA = "CREDENCIAL_INVALIDA"
    LIMITE_SOLICITUDES = "LIMITE_SOLICITUDES"
    ERROR_SERVIDOR = "ERROR_SERVIDOR"
    TIEMPO_ESPERA_AGOTADO = "TIEMPO_ESPERA_AGOTADO"
    CONEXION_RED_FALLIDA = "CONEXION_RED_FALLIDA"
    RESPUESTA_INESPERADA = "RESPUESTA_INESPERADA"
    CONTENIDO_BINARIO_INVALIDO = "CONTENIDO_BINARIO_INVALIDO"
    ARCHIVO_EXCEL_CORRUPTO = "ARCHIVO_EXCEL_CORRUPTO"
    ESQUEMA_INVENTARIO_INVALIDO = "ESQUEMA_INVENTARIO_INVALIDO"


class CategoriaResultadoConsulta(str, Enum):
    """Categorías de alto nivel para que la futura interfaz distinga el estado del inventario (Sección 7)."""

    INVENTARIO_DISPONIBLE = "INVENTARIO_DISPONIBLE"
    PRODUCTO_NO_ENCONTRADO = "PRODUCTO_NO_ENCONTRADO"
    INVENTARIO_NO_INICIALIZADO = "INVENTARIO_NO_INICIALIZADO"
    ERROR_CONSULTA_INVENTARIO = "ERROR_CONSULTA_INVENTARIO"
    DATOS_REMOTOS_INVALIDOS = "DATOS_REMOTOS_INVALIDOS"


@dataclass(frozen=True)
class ConfiguracionRepositorioGitHub:
    """Configuración centralizada del repositorio remoto de GitHub."""

    propietario: str = GITHUB_PROPIETARIO_DEFECTO
    repositorio: str = GITHUB_REPOSITORIO_DEFECTO
    rama: str = GITHUB_RAMA_DEFECTO
    ruta_archivo: str = GITHUB_RUTA_INVENTARIO_DEFECTO
    url_base_api: str = GITHUB_API_BASE_URL
    timeout_segundos: float = GITHUB_TIMEOUT_SEGUNDOS_DEFECTO

    def __post_init__(self) -> None:
        if not self.propietario or not self.propietario.strip():
            raise ValueError("El propietario del repositorio GitHub no puede estar vacío.")
        if not self.repositorio or not self.repositorio.strip():
            raise ValueError("El nombre del repositorio GitHub no puede estar vacío.")
        if not self.rama or not self.rama.strip():
            raise ValueError("La rama de GitHub no puede estar vacía.")
        if not self.ruta_archivo or not self.ruta_archivo.strip():
            raise ValueError("La ruta del archivo de inventario no puede estar vacía.")
        if not self.url_base_api or not self.url_base_api.strip():
            raise ValueError("La URL base de GitHub API no puede estar vacía.")
        if self.timeout_segundos <= 0:
            raise ValueError("El tiempo de espera (timeout) debe ser mayor que cero.")

    @property
    def repositorio_completo(self) -> str:
        """Identificador 'propietario/repositorio'."""
        return f"{self.propietario.strip()}/{self.repositorio.strip()}"

    @property
    def ruta_archivo_normalizada(self) -> str:
        """Ruta relativa normalizada con barras '/' sin barra inicial."""
        return self.ruta_archivo.strip().replace("\\", "/").lstrip("/")

    def _base_limpia(self) -> str:
        return self.url_base_api.strip().rstrip("/")

    def url_repositorio(self) -> str:
        """Construye la URL de consulta de metadatos del repositorio."""
        prop = urllib.parse.quote(self.propietario.strip(), safe="")
        repo = urllib.parse.quote(self.repositorio.strip(), safe="")
        return f"{self._base_limpia()}/repos/{prop}/{repo}"

    def url_rama(self) -> str:
        """Construye la URL de consulta de la rama configurada."""
        rama_cod = urllib.parse.quote(self.rama.strip(), safe="")
        return f"{self.url_repositorio()}/branches/{rama_cod}"

    def url_contenido_archivo(self) -> str:
        """Construye la URL de GitHub Contents API para el archivo maestro en la rama configurada."""
        segmentos = [
            urllib.parse.quote(seg, safe="")
            for seg in self.ruta_archivo_normalizada.split("/")
            if seg
        ]
        ruta_codificada = "/".join(segmentos)
        query = urllib.parse.urlencode({"ref": self.rama.strip()})
        return f"{self.url_repositorio()}/contents/{ruta_codificada}?{query}"


CONFIGURACION_POR_DEFECTO = ConfiguracionRepositorioGitHub()


@dataclass(frozen=True)
class RespuestaHTTPGitHub:
    """Representación inmutable de una respuesta HTTP recibida desde GitHub API."""

    status_code: int
    cuerpo: bytes
    encabezados: Mapping[str, str] = field(default_factory=dict)
    url: str = ""

    def obtener_encabezado(self, nombre: str, valor_por_defecto: str = "") -> str:
        """Busca un encabezado HTTP sin distinción entre mayúsculas y minúsculas."""
        objetivo = nombre.lower()
        for clave, valor in self.encabezados.items():
            if clave.lower() == objetivo:
                return str(valor)
        return valor_por_defecto


EjecutorHTTP = Callable[[str, Mapping[str, str], float], RespuestaHTTPGitHub]


def ocultar_secretos_en_texto(texto: str, token: str | None = None) -> str:
    """Elimina cualquier rastro de tokens o credenciales antes de exponer mensajes o errores."""
    if not texto:
        return ""
    resultado = str(texto)
    if token and token.strip():
        resultado = resultado.replace(token.strip(), MARCA_SECRETO_OCULTO)
    for patron in _PATRONES_SECRETOS:
        if patron.groups >= 1:
            resultado = patron.sub(rf"\1{MARCA_SECRETO_OCULTO}", resultado)
        else:
            resultado = patron.sub(MARCA_SECRETO_OCULTO, resultado)
    return resultado


class ErrorLecturaGitHub(Exception):
    """Excepción base estructurada para todos los errores de lectura desde GitHub API."""

    codigo_por_defecto: CodigoErrorGitHub = CodigoErrorGitHub.RESPUESTA_INESPERADA
    categoria_por_defecto: CategoriaResultadoConsulta = (
        CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO
    )

    def __init__(
        self,
        mensaje: str,
        *,
        codigo: CodigoErrorGitHub | None = None,
        categoria: CategoriaResultadoConsulta | None = None,
        status_code: int | None = None,
        es_reintentable: bool = False,
        errores_inventario: list[DetalleErrorInventario] | None = None,
        token_para_sanitizar: str | None = None,
    ) -> None:
        mensaje_seguro = ocultar_secretos_en_texto(mensaje, token=token_para_sanitizar)
        super().__init__(mensaje_seguro)
        self.mensaje: str = mensaje_seguro
        self.codigo: CodigoErrorGitHub = codigo or self.codigo_por_defecto
        self.categoria: CategoriaResultadoConsulta = categoria or self.categoria_por_defecto
        self.status_code: int | None = status_code
        self.es_reintentable: bool = es_reintentable
        self.errores_inventario: list[DetalleErrorInventario] = (
            list(errores_inventario) if errores_inventario else []
        )


class ErrorArchivoRemotoInexistente(ErrorLecturaGitHub):
    """Escenario 1: Se confirmó con seguridad que el archivo maestro no existe en el repositorio y rama."""

    codigo_por_defecto = CodigoErrorGitHub.ARCHIVO_REMOTO_INEXISTENTE
    categoria_por_defecto = CategoriaResultadoConsulta.INVENTARIO_NO_INICIALIZADO


class ErrorRepositorioInaccesible(ErrorLecturaGitHub):
    """Escenario 2: El repositorio no existe o no es accesible."""

    codigo_por_defecto = CodigoErrorGitHub.REPOSITORIO_INACCESIBLE
    categoria_por_defecto = CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO


class ErrorRamaInexistente(ErrorLecturaGitHub):
    """Escenario 3: La rama configurada no existe o no es accesible en el repositorio."""

    codigo_por_defecto = CodigoErrorGitHub.RAMA_INEXISTENTE
    categoria_por_defecto = CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO


class ErrorAccesoDenegadoGitHub(ErrorLecturaGitHub):
    """Escenario 4: GitHub deniega el acceso al recurso solicitado (403 Forbidden por permisos)."""

    codigo_por_defecto = CodigoErrorGitHub.ACCESO_DENEGADO
    categoria_por_defecto = CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO


class ErrorCredencialInvalidaGitHub(ErrorLecturaGitHub):
    """Escenario 5: La credencial proporcionada es inválida, expiró o tiene permisos insuficientes."""

    codigo_por_defecto = CodigoErrorGitHub.CREDENCIAL_INVALIDA
    categoria_por_defecto = CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO


class ErrorLimiteSolicitudesGitHub(ErrorLecturaGitHub):
    """Escenario 6: Se alcanzó el límite de solicitudes (rate limit) de GitHub API."""

    codigo_por_defecto = CodigoErrorGitHub.LIMITE_SOLICITUDES
    categoria_por_defecto = CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO


class ErrorServidorGitHub(ErrorLecturaGitHub):
    """Escenario 7: Error temporal del servidor de GitHub (HTTP 5xx)."""

    codigo_por_defecto = CodigoErrorGitHub.ERROR_SERVIDOR
    categoria_por_defecto = CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO


class ErrorTiempoEsperaGitHub(ErrorLecturaGitHub):
    """Escenario 8: Se agotó el tiempo de espera (timeout) al consultar GitHub API."""

    codigo_por_defecto = CodigoErrorGitHub.TIEMPO_ESPERA_AGOTADO
    categoria_por_defecto = CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO


class ErrorConexionRedGitHub(ErrorLecturaGitHub):
    """Escenario 9: Fallo de conexión de red al intentar comunicarse con GitHub API."""

    codigo_por_defecto = CodigoErrorGitHub.CONEXION_RED_FALLIDA
    categoria_por_defecto = CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO


class ErrorRespuestaInesperadaGitHub(ErrorLecturaGitHub):
    """Escenario 10: La respuesta de GitHub API tiene un formato o estructura inesperada."""

    codigo_por_defecto = CodigoErrorGitHub.RESPUESTA_INESPERADA
    categoria_por_defecto = CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO


class ErrorContenidoBinarioInvalido(ErrorLecturaGitHub):
    """Escenario 11: El contenido binario descargado o su codificación base64 es inválido o vacío."""

    codigo_por_defecto = CodigoErrorGitHub.CONTENIDO_BINARIO_INVALIDO
    categoria_por_defecto = CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO


class ErrorArchivoExcelRemotoCorrupto(ErrorLecturaGitHub):
    """Escenario 12: Los bytes descargados desde GitHub corresponden a un archivo Excel corrupto."""

    codigo_por_defecto = CodigoErrorGitHub.ARCHIVO_EXCEL_CORRUPTO
    categoria_por_defecto = CategoriaResultadoConsulta.DATOS_REMOTOS_INVALIDOS


class ErrorEsquemaInventarioRemoto(ErrorLecturaGitHub):
    """Escenario 13: El archivo Excel remoto incumple la estructura de 4 hojas o reglas de integridad."""

    codigo_por_defecto = CodigoErrorGitHub.ESQUEMA_INVENTARIO_INVALIDO
    categoria_por_defecto = CategoriaResultadoConsulta.DATOS_REMOTOS_INVALIDOS


@dataclass(frozen=True)
class ResultadoExistenciaRemota:
    """Resultado estructurado de la verificación de existencia del archivo maestro remoto."""

    estado: EstadoExistenciaRemota
    propietario: str
    repositorio: str
    rama: str
    ruta_archivo: str
    categoria_consulta: CategoriaResultadoConsulta
    sha_github: str | None = None
    tamano_bytes: int | None = None
    codigo_error: CodigoErrorGitHub | None = None
    mensaje: str = ""

    @property
    def repositorio_completo(self) -> str:
        return f"{self.propietario}/{self.repositorio}"

    @property
    def existe(self) -> bool:
        return self.estado == EstadoExistenciaRemota.EXISTE

    @property
    def inexistencia_confirmada(self) -> bool:
        return self.estado == EstadoExistenciaRemota.NO_EXISTE


@dataclass(frozen=True)
class ResultadoLecturaInventarioRemoto:
    """Resultado de una descarga y validación exitosa del inventario maestro desde GitHub."""

    propietario: str
    repositorio: str
    rama: str
    ruta_archivo: str
    sha_github: str
    sha256_local: str
    tamano_bytes: int
    inventario: InventarioDatos
    categoria_consulta: CategoriaResultadoConsulta = (
        CategoriaResultadoConsulta.INVENTARIO_DISPONIBLE
    )

    @property
    def repositorio_completo(self) -> str:
        return f"{self.propietario}/{self.repositorio}"


def obtener_token_configurado(token_explicito: str | None = None) -> str | None:
    """Obtiene de forma segura un token opcional sin exponerlo ni exigir su presencia.

    Prioridad:
    1. `token_explicito`, si fue proporcionado.
    2. Variables de entorno `FERRETERIAMS_GITHUB_TOKEN` o `GITHUB_TOKEN`.
    3. `streamlit.secrets` (si estuviera disponible y configurado en tiempo de ejecución).
    """
    if token_explicito is not None:
        limpio = token_explicito.strip()
        if not limpio or any(ord(c) < 32 or ord(c) == 127 for c in limpio):
            raise ErrorCredencialInvalidaGitHub(
                "La credencial de GitHub proporcionada tiene un formato inválido o está vacía.",
                codigo=CodigoErrorGitHub.CREDENCIAL_INVALIDA,
            )
        return limpio

    for var_entorno in ("FERRETERIAMS_GITHUB_TOKEN", "GITHUB_TOKEN"):
        valor_env = os.environ.get(var_entorno)
        if valor_env and valor_env.strip():
            return valor_env.strip()

    try:
        import streamlit as st

        secretos = getattr(st, "secrets", None)
        if secretos is not None:
            for clave in ("GITHUB_TOKEN", "github_token"):
                if clave in secretos and str(secretos[clave]).strip():
                    return str(secretos[clave]).strip()
            if "github" in secretos and isinstance(secretos["github"], Mapping):
                token_sec = secretos["github"].get("token")
                if token_sec and str(token_sec).strip():
                    return str(token_sec).strip()
    except Exception:
        # En ejecuciones fuera de Streamlit o sin secrets.toml configurado, se continúa sin token
        pass

    return None


def construir_encabezados_github(
    token: str | None = None,
    accept: str = "application/vnd.github+json",
) -> dict[str, str]:
    """Construye los encabezados HTTP de solo lectura evitando depender de caché obsoleta."""
    encabezados: dict[str, str] = {
        "Accept": accept,
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
        "User-Agent": "FerreteriaMS-v0-GitHubReader",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
    }
    if token:
        encabezados["Authorization"] = f"Bearer {token}"
    return encabezados


def _tiene_encabezado_autorizacion(encabezados: Mapping[str, str] | None) -> bool:
    """Indica si el diccionario de encabezados contiene una cabecera Authorization no vacía."""
    if not encabezados:
        return False
    return any(
        str(clave).strip().lower() == "authorization" and bool(str(valor).strip())
        for clave, valor in encabezados.items()
    )


def validar_url_solicitud_github(
    url: str,
    *,
    dominios_permitidos: tuple[str, ...] = DOMINIOS_API_GITHUB_PERMITIDOS,
    encabezados: Mapping[str, str] | None = None,
    config: ConfiguracionRepositorioGitHub | None = None,
    es_descarga: bool = False,
    es_redireccion: bool = False,
    token: str | None = None,
    contexto: str = "consulta a GitHub API",
) -> urllib.parse.SplitResult:
    """Valida que la URL utilice HTTPS, apunte a un dominio y destino autorizados y proteja el token."""
    if not isinstance(url, str) or not url.strip():
        raise ErrorRespuestaInesperadaGitHub(
            f"URL vacía o inválida para {contexto}.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            token_para_sanitizar=token,
        )

    url_limpia = url.strip()
    if any(ord(c) < 32 or ord(c) == 127 for c in url_limpia):
        raise ErrorRespuestaInesperadaGitHub(
            f"La URL contiene caracteres de control no permitidos para {contexto}.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            token_para_sanitizar=token,
        )

    partes = urllib.parse.urlsplit(url_limpia)
    esquema = partes.scheme.lower()
    if esquema != "https":
        raise ErrorRespuestaInesperadaGitHub(
            f"Esquema de URL no permitido para {contexto}: '{esquema}'. "
            "Se exige HTTPS cifrado para todas las solicitudes.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            token_para_sanitizar=token,
        )

    if partes.username is not None or partes.password is not None:
        raise ErrorRespuestaInesperadaGitHub(
            f"No se permiten credenciales incrustadas en la URL para {contexto}.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            token_para_sanitizar=token,
        )

    try:
        puerto = partes.port
    except ValueError as exc_puerto:
        raise ErrorRespuestaInesperadaGitHub(
            f"Puerto inválido en la URL para {contexto}.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            token_para_sanitizar=token,
        ) from exc_puerto

    if puerto not in (None, 443):
        raise ErrorRespuestaInesperadaGitHub(
            f"Puerto no permitido ({puerto}) en la URL para {contexto}.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            token_para_sanitizar=token,
        )

    hostname = (partes.hostname or "").strip().lower()
    dominios_norm = tuple(d.lower() for d in dominios_permitidos)
    if not hostname or hostname not in dominios_norm:
        raise ErrorRespuestaInesperadaGitHub(
            f"Dominio no autorizado para {contexto}: '{hostname or '<vacío>'}'.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            token_para_sanitizar=token,
        )

    # Protección estricta del token: jamás enviar Authorization fuera de api.github.com
    if _tiene_encabezado_autorizacion(encabezados) and hostname not in DOMINIOS_API_GITHUB_PERMITIDOS:
        raise ErrorRespuestaInesperadaGitHub(
            f"Protección de credenciales: se bloqueó el envío del encabezado Authorization "
            f"hacia el dominio '{hostname}'.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            token_para_sanitizar=token,
        )

    ruta_cruda = partes.path or ""
    ruta_decodificada = urllib.parse.unquote(ruta_cruda)
    segmentos_crudos = [seg for seg in ruta_cruda.split("/") if seg]
    segmentos_decodificados = [seg for seg in ruta_decodificada.split("/") if seg]

    if (
        "\\" in ruta_cruda
        or "\\" in ruta_decodificada
        or any(seg in (".", "..") for seg in segmentos_crudos)
        or any(seg in (".", "..") for seg in segmentos_decodificados)
    ):
        raise ErrorRespuestaInesperadaGitHub(
            f"Ruta de destino inválida o con segmentos de navegación no permitidos en {contexto}.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            token_para_sanitizar=token,
        )

    if es_redireccion:
        if not segmentos_decodificados:
            raise ErrorRespuestaInesperadaGitHub(
                "La URL de redirección no contiene una ruta de recurso válida.",
                codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
                token_para_sanitizar=token,
            )
        return partes

    if not es_descarga and hostname in DOMINIOS_API_GITHUB_PERMITIDOS:
        if len(segmentos_decodificados) < 3 or segmentos_decodificados[0] != "repos":
            raise ErrorRespuestaInesperadaGitHub(
                f"La URL de consulta a GitHub API no apunta a un endpoint '/repos/...' válido: '{ruta_cruda}'.",
                codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
                token_para_sanitizar=token,
            )
        if config is not None:
            prop_esperado = config.propietario.strip()
            repo_esperado = config.repositorio.strip()
            if (
                segmentos_decodificados[1] != prop_esperado
                or segmentos_decodificados[2] != repo_esperado
            ):
                raise ErrorRespuestaInesperadaGitHub(
                    f"El destino de la URL ('{segmentos_decodificados[1]}/{segmentos_decodificados[2]}') "
                    f"no coincide con el repositorio configurado ('{config.repositorio_completo}').",
                    codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
                    token_para_sanitizar=token,
                )

    if es_descarga:
        if config is None:
            raise ErrorRespuestaInesperadaGitHub(
                "Se requiere la configuración del repositorio para validar la URL de descarga.",
                codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
                token_para_sanitizar=token,
            )
        prop_esperado = config.propietario.strip()
        repo_esperado = config.repositorio.strip()
        segmentos_archivo = [seg for seg in config.ruta_archivo_normalizada.split("/") if seg]

        if hostname == "raw.githubusercontent.com":
            # Formato esperado: /{propietario}/{repositorio}/{rama_o_sha}/{ruta_archivo}
            min_segmentos = 3 + len(segmentos_archivo)
            if (
                len(segmentos_decodificados) < min_segmentos
                or segmentos_decodificados[0] != prop_esperado
                or segmentos_decodificados[1] != repo_esperado
                or segmentos_decodificados[-len(segmentos_archivo) :] != segmentos_archivo
            ):
                raise ErrorRespuestaInesperadaGitHub(
                    f"La URL de descarga en '{hostname}' no corresponde al repositorio "
                    f"'{config.repositorio_completo}' o al archivo '{config.ruta_archivo_normalizada}'.",
                    codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
                    token_para_sanitizar=token,
                )
        elif hostname == "api.github.com":
            # Formato esperado: /repos/{propietario}/{repositorio}/contents/{ruta_archivo}
            prefijo_esperado = ["repos", prop_esperado, repo_esperado, "contents", *segmentos_archivo]
            if segmentos_decodificados != prefijo_esperado:
                raise ErrorRespuestaInesperadaGitHub(
                    f"La URL de descarga en '{hostname}' no corresponde a la ruta autorizada "
                    f"del archivo '{config.ruta_archivo_normalizada}'.",
                    codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
                    token_para_sanitizar=token,
                )
        else:
            raise ErrorRespuestaInesperadaGitHub(
                f"Dominio de descarga no confiable: '{hostname}'.",
                codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
                token_para_sanitizar=token,
            )

    return partes


def validar_url_descarga_github(
    url_descarga: str,
    config: ConfiguracionRepositorioGitHub,
    token: str | None = None,
) -> str:
    """Valida que `download_url` utilice HTTPS y apunte al repositorio y archivo esperados en GitHub."""
    validar_url_solicitud_github(
        url_descarga,
        dominios_permitidos=DOMINIOS_DESCARGA_GITHUB_PERMITIDOS,
        config=config,
        es_descarga=True,
        token=token,
        contexto="descarga de contenido (download_url)",
    )
    return url_descarga.strip()


class _ManejadorRedireccionSeguraGitHub(urllib.request.HTTPRedirectHandler):
    """Controla las redirecciones HTTP impidiendo esquemas no cifrados, dominios externos y fuga de tokens."""

    def __init__(self, token: str | None = None) -> None:
        super().__init__()
        self._token = token
        self._conteo_redirecciones = 0

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> urllib.request.Request | None:
        self._conteo_redirecciones += 1
        if self._conteo_redirecciones > MAX_REDIRECCIONES_GITHUB:
            raise ErrorRespuestaInesperadaGitHub(
                "Se excedió el número máximo de redirecciones permitidas al consultar GitHub.",
                codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
                status_code=code,
                token_para_sanitizar=self._token,
            )

        url_origen = req.full_url
        url_destino = urllib.parse.urljoin(url_origen, newurl)

        validar_url_solicitud_github(
            url_destino,
            dominios_permitidos=DOMINIOS_REDIRECCION_GITHUB_PERMITIDOS,
            es_redireccion=True,
            token=self._token,
            contexto="redirección HTTP",
        )

        encabezados_actuales = {
            **dict(req.headers.items()),
            **dict(req.unredirected_hdrs.items()),
        }
        if _tiene_encabezado_autorizacion(encabezados_actuales):
            raise ErrorRespuestaInesperadaGitHub(
                "Redirección bloqueada por seguridad para impedir la filtración de credenciales "
                "de autorización.",
                codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
                status_code=code,
                token_para_sanitizar=self._token,
            )

        encabezados_limpios = {
            k: v
            for k, v in req.headers.items()
            if k.lower() not in ("authorization", "cookie", "host")
        }
        return urllib.request.Request(
            url=url_destino,
            headers=encabezados_limpios,
            method="GET",
        )


def ejecutar_solicitud_get_github(
    url: str,
    encabezados: Mapping[str, str],
    timeout_segundos: float = GITHUB_TIMEOUT_SEGUNDOS_DEFECTO,
) -> RespuestaHTTPGitHub:
    """Ejecuta exclusivamente una solicitud HTTPS GET hacia dominios oficiales de GitHub."""
    validar_url_solicitud_github(
        url,
        dominios_permitidos=DOMINIOS_DESCARGA_GITHUB_PERMITIDOS,
        encabezados=encabezados,
        es_redireccion=(
            (urllib.parse.urlsplit(url.strip()).hostname or "").strip().lower()
            == "raw.githubusercontent.com"
        ),
        contexto="solicitud GET a GitHub",
    )

    solicitud = urllib.request.Request(
        url=url.strip(),
        headers=dict(encabezados),
        method="GET",
    )
    if solicitud.get_method() != "GET":
        raise PermissionError("Solo se autorizan solicitudes HTTP GET en este módulo.")

    try:
        if urllib.request.urlopen is _URLOPEN_ORIGINAL:
            opener = urllib.request.build_opener(_ManejadorRedireccionSeguraGitHub())
            contexto_respuesta = opener.open(solicitud, timeout=timeout_segundos)
        else:
            contexto_respuesta = urllib.request.urlopen(solicitud, timeout=timeout_segundos)

        with contexto_respuesta as respuesta:
            cuerpo = respuesta.read()
            status = int(getattr(respuesta, "status", None) or respuesta.getcode())
            headers_dict = (
                {k: v for k, v in respuesta.headers.items()}
                if getattr(respuesta, "headers", None) is not None
                else {}
            )
            url_final = (
                getattr(respuesta, "url", None)
                or (respuesta.geturl() if hasattr(respuesta, "geturl") else None)
                or url.strip()
            )

            if 300 <= status < 400:
                ubicacion = ""
                for k, v in headers_dict.items():
                    if k.lower() == "location":
                        ubicacion = str(v).strip()
                        break
                if ubicacion:
                    url_redir = urllib.parse.urljoin(url.strip(), ubicacion)
                    validar_url_solicitud_github(
                        url_redir,
                        dominios_permitidos=DOMINIOS_REDIRECCION_GITHUB_PERMITIDOS,
                        es_redireccion=True,
                        contexto="redirección HTTP",
                    )
                raise ErrorRespuestaInesperadaGitHub(
                    f"Redirección HTTP ({status}) no permitida o no completada de forma segura.",
                    codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
                    status_code=status,
                )

            if str(url_final).strip() != url.strip():
                validar_url_solicitud_github(
                    str(url_final),
                    dominios_permitidos=DOMINIOS_REDIRECCION_GITHUB_PERMITIDOS,
                    es_redireccion=True,
                    contexto="URL final tras redirección",
                )
                if _tiene_encabezado_autorizacion(encabezados):
                    raise ErrorRespuestaInesperadaGitHub(
                        "Redirección bloqueada por seguridad en una solicitud autenticada.",
                        codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
                        status_code=status,
                    )

            return RespuestaHTTPGitHub(
                status_code=status,
                cuerpo=cuerpo,
                encabezados=headers_dict,
                url=str(url_final),
            )
    except ErrorLecturaGitHub:
        raise
    except urllib.error.HTTPError as exc_http:
        if 300 <= int(exc_http.code) < 400:
            raise ErrorRespuestaInesperadaGitHub(
                f"Redirección HTTP ({exc_http.code}) rechazada por política de seguridad.",
                codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
                status_code=int(exc_http.code),
            ) from exc_http
        try:
            cuerpo_err = exc_http.read() if exc_http.fp is not None else b""
        except Exception:
            cuerpo_err = b""
        headers_err = {k: v for k, v in exc_http.headers.items()} if exc_http.headers else {}
        return RespuestaHTTPGitHub(
            status_code=int(exc_http.code),
            cuerpo=cuerpo_err,
            encabezados=headers_err,
            url=url.strip(),
        )
    except (TimeoutError, socket.timeout) as exc_timeout:
        raise ErrorTiempoEsperaGitHub(
            "Se agotó el tiempo de espera al intentar conectar con GitHub API. "
            "Verifique su conexión e intente nuevamente.",
            codigo=CodigoErrorGitHub.TIEMPO_ESPERA_AGOTADO,
            es_reintentable=True,
        ) from exc_timeout
    except urllib.error.URLError as exc_url:
        razon = getattr(exc_url, "reason", None)
        if isinstance(razon, ErrorLecturaGitHub):
            raise razon from exc_url
        if isinstance(razon, (TimeoutError, socket.timeout)):
            raise ErrorTiempoEsperaGitHub(
                "Se agotó el tiempo de espera al consultar GitHub API. "
                "Verifique su conexión e intente nuevamente.",
                codigo=CodigoErrorGitHub.TIEMPO_ESPERA_AGOTADO,
                es_reintentable=True,
            ) from exc_url
        raise ErrorConexionRedGitHub(
            "No fue posible establecer conexión de red con GitHub API. "
            "Verifique su conexión a internet e intente nuevamente.",
            codigo=CodigoErrorGitHub.CONEXION_RED_FALLIDA,
            es_reintentable=True,
        ) from exc_url
    except OSError as exc_os:
        raise ErrorConexionRedGitHub(
            "Error de comunicación de red al consultar GitHub API.",
            codigo=CodigoErrorGitHub.CONEXION_RED_FALLIDA,
            es_reintentable=True,
        ) from exc_os


def _extraer_mensaje_api(respuesta: RespuestaHTTPGitHub, token: str | None = None) -> str:
    """Extrae de forma segura el campo 'message' de una respuesta JSON de error de GitHub."""
    if not respuesta.cuerpo:
        return ""
    try:
        datos = json.loads(respuesta.cuerpo.decode("utf-8", errors="replace"))
        if isinstance(datos, Mapping) and "message" in datos:
            return ocultar_secretos_en_texto(str(datos["message"]).strip(), token=token)
    except Exception:
        pass
    return ""


def _decodificar_json_objeto(
    respuesta: RespuestaHTTPGitHub,
    contexto: str,
    token: str | None = None,
) -> Mapping[str, Any]:
    """Valida que el cuerpo de una respuesta HTTP 200 sea un objeto JSON (dict)."""
    if not respuesta.cuerpo:
        raise ErrorRespuestaInesperadaGitHub(
            f"GitHub API devolvió una respuesta vacía al consultar {contexto}.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            status_code=respuesta.status_code,
            token_para_sanitizar=token,
        )
    try:
        datos = json.loads(respuesta.cuerpo.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ErrorRespuestaInesperadaGitHub(
            f"GitHub API devolvió un formato JSON inválido al consultar {contexto}.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            status_code=respuesta.status_code,
            token_para_sanitizar=token,
        ) from exc

    if not isinstance(datos, Mapping):
        raise ErrorRespuestaInesperadaGitHub(
            f"GitHub API devolvió una estructura JSON inesperada ({type(datos).__name__}) "
            f"al consultar {contexto}; se esperaba un objeto.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            status_code=respuesta.status_code,
            token_para_sanitizar=token,
        )
    return datos


def _clasificar_error_http_comun(
    respuesta: RespuestaHTTPGitHub,
    config: ConfiguracionRepositorioGitHub,
    token: str | None = None,
) -> ErrorLecturaGitHub:
    """Traduce códigos de estado HTTP de error (distintos de 200 y 404 contextual) a excepciones tipadas."""
    status = respuesta.status_code
    detalle_api = _extraer_mensaje_api(respuesta, token=token)
    detalle_min = detalle_api.lower()
    restante_ratelimit = respuesta.obtener_encabezado("X-RateLimit-Remaining", "").strip()
    retry_after = respuesta.obtener_encabezado("Retry-After", "").strip()

    # Escenario 5: Credencial inválida o expirada (401)
    if status == 401:
        return ErrorCredencialInvalidaGitHub(
            f"Autenticación rechazada por GitHub API (HTTP 401) para '{config.repositorio_completo}': "
            f"credencial inválida o expirada. {detalle_api}".strip(),
            codigo=CodigoErrorGitHub.CREDENCIAL_INVALIDA,
            status_code=status,
            es_reintentable=False,
            token_para_sanitizar=token,
        )

    # Escenario 6: Límite de solicitudes (429 o 403 por rate limit)
    es_rate_limit = (
        status == 429
        or restante_ratelimit == "0"
        or "rate limit" in detalle_min
        or "abuse detection" in detalle_min
        or (status == 403 and bool(retry_after))
    )
    if es_rate_limit:
        return ErrorLimiteSolicitudesGitHub(
            "Se alcanzó el límite de solicitudes de GitHub API. "
            "Espere unos minutos antes de volver a consultar el inventario.",
            codigo=CodigoErrorGitHub.LIMITE_SOLICITUDES,
            status_code=status,
            es_reintentable=True,
            token_para_sanitizar=token,
        )

    # Escenarios 4 y 5 en HTTP 403: Credencial con permisos insuficientes vs Acceso denegado
    if status == 403:
        indicadores_credencial_insuficiente = (
            "personal access token",
            "resource not accessible by integration",
            "insufficient",
            "bad credentials",
            "token",
            "scope",
        )
        if token and any(ind in detalle_min for ind in indicadores_credencial_insuficiente):
            return ErrorCredencialInvalidaGitHub(
                f"La credencial configurada no posee permisos suficientes para leer "
                f"'{config.repositorio_completo}' (HTTP 403). {detalle_api}".strip(),
                codigo=CodigoErrorGitHub.CREDENCIAL_INVALIDA,
                status_code=status,
                es_reintentable=False,
                token_para_sanitizar=token,
            )
        return ErrorAccesoDenegadoGitHub(
            f"Acceso denegado por GitHub API (HTTP 403) al consultar "
            f"'{config.repositorio_completo}'. {detalle_api}".strip(),
            codigo=CodigoErrorGitHub.ACCESO_DENEGADO,
            status_code=status,
            es_reintentable=False,
            token_para_sanitizar=token,
        )

    # Escenario 7: Error temporal del servidor de GitHub (5xx)
    if 500 <= status < 600:
        return ErrorServidorGitHub(
            f"Error temporal del servidor de GitHub API (HTTP {status}). "
            "Por favor, reintente la consulta en unos instantes.",
            codigo=CodigoErrorGitHub.ERROR_SERVIDOR,
            status_code=status,
            es_reintentable=True,
            token_para_sanitizar=token,
        )

    # Escenario 10: Cualquier otro código inesperado
    return ErrorRespuestaInesperadaGitHub(
        f"GitHub API devolvió un código HTTP inesperado ({status}) al consultar "
        f"'{config.repositorio_completo}'. {detalle_api}".strip(),
        codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
        status_code=status,
        es_reintentable=False,
        token_para_sanitizar=token,
    )


def _diagnosticar_404_contenido(
    respuesta_404: RespuestaHTTPGitHub,
    config: ConfiguracionRepositorioGitHub,
    encabezados: Mapping[str, str],
    ejecutor: EjecutorHTTP,
    token: str | None = None,
) -> None:
    """Determina con seguridad la causa de un HTTP 404 al consultar el archivo maestro.

    Regla de seguridad (Sección 5.2):
    Un 404 solo puede interpretarse como inexistencia del archivo cuando se comprueba que
    tanto el repositorio como la rama son accesibles (HTTP 200 con estructura JSON válida).
    Si el archivo realmente no existe, lanza `ErrorArchivoRemotoInexistente`.
    Si el repositorio o la rama no son accesibles, lanza `ErrorRepositorioInaccesible`
    o `ErrorRamaInexistente`.
    """
    detalle_404 = _extraer_mensaje_api(respuesta_404, token=token)
    detalle_404_min = detalle_404.lower()

    if "no commit found for the ref" in detalle_404_min or "no branch found" in detalle_404_min:
        raise ErrorRamaInexistente(
            f"La rama '{config.rama}' no existe o no es accesible en el repositorio "
            f"'{config.repositorio_completo}'.",
            codigo=CodigoErrorGitHub.RAMA_INEXISTENTE,
            status_code=404,
            es_reintentable=False,
            token_para_sanitizar=token,
        )

    # Paso 1: Verificar que el repositorio exista y sea accesible
    url_repo = config.url_repositorio()
    validar_url_solicitud_github(
        url_repo,
        dominios_permitidos=DOMINIOS_API_GITHUB_PERMITIDOS,
        encabezados=encabezados,
        config=config,
        token=token,
        contexto="consulta de metadatos del repositorio",
    )
    resp_repo = ejecutor(url_repo, encabezados, config.timeout_segundos)
    if resp_repo.status_code == 404:
        raise ErrorRepositorioInaccesible(
            f"El repositorio '{config.repositorio_completo}' no existe, es privado o "
            "no se cuenta con permisos para acceder a él.",
            codigo=CodigoErrorGitHub.REPOSITORIO_INACCESIBLE,
            status_code=404,
            es_reintentable=False,
            token_para_sanitizar=token,
        )
    if resp_repo.status_code != 200:
        raise _clasificar_error_http_comun(resp_repo, config, token=token)

    datos_repo = _decodificar_json_objeto(
        resp_repo,
        contexto=f"el repositorio '{config.repositorio_completo}'",
        token=token,
    )
    if "full_name" not in datos_repo and "name" not in datos_repo and "id" not in datos_repo:
        raise ErrorRespuestaInesperadaGitHub(
            f"La respuesta de metadatos del repositorio '{config.repositorio_completo}' "
            "no contiene los campos identificadores esperados.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            status_code=resp_repo.status_code,
            token_para_sanitizar=token,
        )

    # Paso 2: Verificar que la rama exista y sea accesible
    url_rama = config.url_rama()
    validar_url_solicitud_github(
        url_rama,
        dominios_permitidos=DOMINIOS_API_GITHUB_PERMITIDOS,
        encabezados=encabezados,
        config=config,
        token=token,
        contexto="consulta de la rama del repositorio",
    )
    resp_rama = ejecutor(url_rama, encabezados, config.timeout_segundos)
    if resp_rama.status_code == 404:
        raise ErrorRamaInexistente(
            f"La rama '{config.rama}' no existe o no es accesible en el repositorio "
            f"'{config.repositorio_completo}'.",
            codigo=CodigoErrorGitHub.RAMA_INEXISTENTE,
            status_code=404,
            es_reintentable=False,
            token_para_sanitizar=token,
        )
    if resp_rama.status_code != 200:
        raise _clasificar_error_http_comun(resp_rama, config, token=token)

    datos_rama = _decodificar_json_objeto(
        resp_rama,
        contexto=f"la rama '{config.rama}' en '{config.repositorio_completo}'",
        token=token,
    )
    if "name" not in datos_rama and "commit" not in datos_rama:
        raise ErrorRespuestaInesperadaGitHub(
            f"La respuesta de la rama '{config.rama}' en '{config.repositorio_completo}' "
            "no contiene información válida de referencia.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            status_code=resp_rama.status_code,
            token_para_sanitizar=token,
        )

    # Repositorio y rama confirmados como accesibles -> el archivo solicitado realmente no existe
    raise ErrorArchivoRemotoInexistente(
        f"Se confirmó que el archivo maestro '{config.ruta_archivo_normalizada}' todavía no existe "
        f"en '{config.repositorio_completo}' (rama '{config.rama}').",
        codigo=CodigoErrorGitHub.ARCHIVO_REMOTO_INEXISTENTE,
        categoria=CategoriaResultadoConsulta.INVENTARIO_NO_INICIALIZADO,
        status_code=404,
        es_reintentable=False,
        token_para_sanitizar=token,
    )


def _validar_metadatos_archivo_github(
    datos: Mapping[str, Any],
    config: ConfiguracionRepositorioGitHub,
    token: str | None = None,
) -> tuple[str, int | None]:
    """Verifica que el objeto JSON de GitHub Contents API corresponda al archivo esperado y extrae su SHA."""
    tipo = datos.get("type")
    if tipo != "file":
        raise ErrorRespuestaInesperadaGitHub(
            f"La ruta '{config.ruta_archivo_normalizada}' en GitHub no corresponde a un archivo "
            f"(tipo devuelto: {tipo!r}).",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            token_para_sanitizar=token,
        )

    ruta_remota = str(datos.get("path", "")).strip().replace("\\", "/").lstrip("/")
    if ruta_remota and ruta_remota != config.ruta_archivo_normalizada:
        raise ErrorRespuestaInesperadaGitHub(
            f"La ruta devuelta por GitHub API ('{ruta_remota}') no coincide con el archivo "
            f"esperado ('{config.ruta_archivo_normalizada}').",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            token_para_sanitizar=token,
        )

    sha = datos.get("sha")
    if not isinstance(sha, str) or not sha.strip():
        raise ErrorRespuestaInesperadaGitHub(
            "La respuesta de GitHub API no incluye un identificador 'sha' válido para el archivo.",
            codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
            token_para_sanitizar=token,
        )

    tamano_raw = datos.get("size")
    tamano: int | None = None
    if tamano_raw is not None:
        if not isinstance(tamano_raw, int) or isinstance(tamano_raw, bool) or tamano_raw < 0:
            raise ErrorRespuestaInesperadaGitHub(
                f"El tamaño del archivo reportado por GitHub API es inválido: {tamano_raw!r}.",
                codigo=CodigoErrorGitHub.RESPUESTA_INESPERADA,
                token_para_sanitizar=token,
            )
        tamano = tamano_raw

    return sha.strip(), tamano


def _extraer_bytes_archivo_github(
    datos: Mapping[str, Any],
    config: ConfiguracionRepositorioGitHub,
    encabezados: Mapping[str, str],
    ejecutor: EjecutorHTTP,
    tamano_esperado: int | None,
    token: str | None = None,
) -> bytes:
    """Obtiene y verifica los bytes completos del archivo desde la respuesta de GitHub API."""
    if tamano_esperado == 0:
        raise ErrorContenidoBinarioInvalido(
            f"El archivo remoto '{config.ruta_archivo_normalizada}' está vacío (0 bytes).",
            codigo=CodigoErrorGitHub.CONTENIDO_BINARIO_INVALIDO,
            token_para_sanitizar=token,
        )

    codificacion = str(datos.get("encoding", "")).strip().lower()
    contenido_b64 = datos.get("content")

    contenido_bytes: bytes | None = None

    if codificacion == "base64" and isinstance(contenido_b64, str) and contenido_b64.strip():
        try:
            contenido_bytes = base64.b64decode(contenido_b64, validate=True)
        except (binascii.Error, ValueError) as exc_b64:
            # Intentar limpieza de saltos de línea estándar en MIME base64 de GitHub
            try:
                compacto = "".join(contenido_b64.split())
                contenido_bytes = base64.b64decode(compacto, validate=True)
            except (binascii.Error, ValueError) as exc_b64_2:
                raise ErrorContenidoBinarioInvalido(
                    "El contenido base64 devuelto por GitHub API es inválido o está truncado.",
                    codigo=CodigoErrorGitHub.CONTENIDO_BINARIO_INVALIDO,
                    token_para_sanitizar=token,
                ) from exc_b64_2
    elif datos.get("download_url") and isinstance(datos.get("download_url"), str):
        url_descarga = validar_url_descarga_github(
            str(datos["download_url"]).strip(),
            config=config,
            token=token,
        )
        host_descarga = (urllib.parse.urlsplit(url_descarga).hostname or "").strip().lower()
        token_descarga = token if host_descarga in DOMINIOS_API_GITHUB_PERMITIDOS else None
        encabezados_raw = construir_encabezados_github(
            token=token_descarga, accept="application/octet-stream"
        )
        validar_url_solicitud_github(
            url_descarga,
            dominios_permitidos=DOMINIOS_DESCARGA_GITHUB_PERMITIDOS,
            encabezados=encabezados_raw,
            config=config,
            es_descarga=True,
            token=token,
            contexto="descarga de contenido (download_url)",
        )
        resp_raw = ejecutor(url_descarga, encabezados_raw, config.timeout_segundos)
        if resp_raw.status_code != 200:
            raise _clasificar_error_http_comun(resp_raw, config, token=token)
        contenido_bytes = resp_raw.cuerpo
    else:
        raise ErrorContenidoBinarioInvalido(
            "La respuesta de GitHub API no contiene contenido binario codificado en base64 "
            "ni una URL de descarga válida.",
            codigo=CodigoErrorGitHub.CONTENIDO_BINARIO_INVALIDO,
            token_para_sanitizar=token,
        )

    if not isinstance(contenido_bytes, bytes) or len(contenido_bytes) == 0:
        raise ErrorContenidoBinarioInvalido(
            "Los datos binarios descargados desde GitHub API están vacíos.",
            codigo=CodigoErrorGitHub.CONTENIDO_BINARIO_INVALIDO,
            token_para_sanitizar=token,
        )

    if tamano_esperado is not None and len(contenido_bytes) != tamano_esperado:
        raise ErrorContenidoBinarioInvalido(
            f"Descarga incompleta o inconsistente: GitHub reportó {tamano_esperado} bytes, "
            f"pero se recibieron {len(contenido_bytes)} bytes.",
            codigo=CodigoErrorGitHub.CONTENIDO_BINARIO_INVALIDO,
            token_para_sanitizar=token,
        )

    return contenido_bytes


def consultar_existencia_inventario_remoto(
    config: ConfiguracionRepositorioGitHub = CONFIGURACION_POR_DEFECTO,
    *,
    token: str | None = None,
    ejecutor_http: EjecutorHTTP | None = None,
    lanzar_excepcion: bool = False,
) -> ResultadoExistenciaRemota:
    """Consulta si el archivo maestro existe en la rama configurada de GitHub.

    Devuelve un `ResultadoExistenciaRemota` cuyo campo `estado` es compatible con
    `EstadoExistenciaRemota` (`EXISTE`, `NO_EXISTE`, `DESCONOCIDO_ERROR`).

    Si `lanzar_excepcion=False` (por defecto), los errores de red, autenticación,
    permisos, repositorio/rama inaccesible o formato inesperado se traducen en el estado
    seguro `EstadoExistenciaRemota.DESCONOCIDO_ERROR`, nunca en `NO_EXISTE`.
    """
    ejecutor = ejecutor_http or ejecutar_solicitud_get_github
    try:
        token_efectivo = obtener_token_configurado(token)
        encabezados = construir_encabezados_github(token=token_efectivo)
        url_contenido = config.url_contenido_archivo()
        validar_url_solicitud_github(
            url_contenido,
            dominios_permitidos=DOMINIOS_API_GITHUB_PERMITIDOS,
            encabezados=encabezados,
            config=config,
            token=token_efectivo,
            contexto="consulta de existencia en GitHub API",
        )
        respuesta = ejecutor(
            url_contenido,
            encabezados,
            config.timeout_segundos,
        )

        if respuesta.status_code == 200:
            datos = _decodificar_json_objeto(
                respuesta,
                contexto=f"el archivo '{config.ruta_archivo_normalizada}'",
                token=token_efectivo,
            )
            sha, tamano = _validar_metadatos_archivo_github(
                datos, config, token=token_efectivo
            )
            return ResultadoExistenciaRemota(
                estado=EstadoExistenciaRemota.EXISTE,
                propietario=config.propietario,
                repositorio=config.repositorio,
                rama=config.rama,
                ruta_archivo=config.ruta_archivo_normalizada,
                categoria_consulta=CategoriaResultadoConsulta.INVENTARIO_DISPONIBLE,
                sha_github=sha,
                tamano_bytes=tamano,
                codigo_error=None,
                mensaje=(
                    f"El archivo maestro '{config.ruta_archivo_normalizada}' existe en "
                    f"'{config.repositorio_completo}' (rama '{config.rama}', SHA '{sha}')."
                ),
            )

        if respuesta.status_code == 404:
            try:
                _diagnosticar_404_contenido(
                    respuesta,
                    config,
                    encabezados,
                    ejecutor,
                    token=token_efectivo,
                )
            except ErrorArchivoRemotoInexistente as exc_inexistente:
                if lanzar_excepcion:
                    raise
                return ResultadoExistenciaRemota(
                    estado=EstadoExistenciaRemota.NO_EXISTE,
                    propietario=config.propietario,
                    repositorio=config.repositorio,
                    rama=config.rama,
                    ruta_archivo=config.ruta_archivo_normalizada,
                    categoria_consulta=CategoriaResultadoConsulta.INVENTARIO_NO_INICIALIZADO,
                    sha_github=None,
                    tamano_bytes=None,
                    codigo_error=exc_inexistente.codigo,
                    mensaje=exc_inexistente.mensaje,
                )

        raise _clasificar_error_http_comun(respuesta, config, token=token_efectivo)

    except ErrorLecturaGitHub as exc:
        if lanzar_excepcion:
            raise
        return ResultadoExistenciaRemota(
            estado=EstadoExistenciaRemota.DESCONOCIDO_ERROR,
            propietario=config.propietario,
            repositorio=config.repositorio,
            rama=config.rama,
            ruta_archivo=config.ruta_archivo_normalizada,
            categoria_consulta=exc.categoria,
            sha_github=None,
            tamano_bytes=None,
            codigo_error=exc.codigo,
            mensaje=exc.mensaje,
        )


def descargar_inventario_remoto(
    config: ConfiguracionRepositorioGitHub = CONFIGURACION_POR_DEFECTO,
    *,
    token: str | None = None,
    ejecutor_http: EjecutorHTTP | None = None,
) -> ResultadoLecturaInventarioRemoto:
    """Descarga el archivo maestro desde GitHub API, obtiene su SHA y valida sus 4 hojas con `inventario.py`.

    No guarda ninguna copia del archivo en el disco local y no sustituye un archivo ausente o
    inválido por el inventario demostrativo.
    """
    ejecutor = ejecutor_http or ejecutar_solicitud_get_github
    token_efectivo = obtener_token_configurado(token)
    encabezados = construir_encabezados_github(token=token_efectivo)
    url_contenido = config.url_contenido_archivo()
    validar_url_solicitud_github(
        url_contenido,
        dominios_permitidos=DOMINIOS_API_GITHUB_PERMITIDOS,
        encabezados=encabezados,
        config=config,
        token=token_efectivo,
        contexto="descarga de inventario desde GitHub API",
    )

    respuesta = ejecutor(
        url_contenido,
        encabezados,
        config.timeout_segundos,
    )

    if respuesta.status_code == 404:
        _diagnosticar_404_contenido(
            respuesta,
            config,
            encabezados,
            ejecutor,
            token=token_efectivo,
        )

    if respuesta.status_code != 200:
        raise _clasificar_error_http_comun(respuesta, config, token=token_efectivo)

    datos = _decodificar_json_objeto(
        respuesta,
        contexto=f"el archivo '{config.ruta_archivo_normalizada}'",
        token=token_efectivo,
    )
    sha_github, tamano = _validar_metadatos_archivo_github(
        datos, config, token=token_efectivo
    )
    contenido_bytes = _extraer_bytes_archivo_github(
        datos,
        config,
        encabezados,
        ejecutor,
        tamano_esperado=tamano,
        token=token_efectivo,
    )

    # Validación mediante el motor existente en 03_Aplicacion/inventario.py (Sección 5.5)
    try:
        inventario_validado = cargar_inventario_excel(contenido_bytes)
    except ErrorArchivoCorrupto as exc_corrupto:
        raise ErrorArchivoExcelRemotoCorrupto(
            f"El archivo '{config.ruta_archivo_normalizada}' descargado desde GitHub está corrupto "
            f"o no es un libro Excel (.xlsx) válido: {exc_corrupto.mensaje}",
            codigo=CodigoErrorGitHub.ARCHIVO_EXCEL_CORRUPTO,
            categoria=CategoriaResultadoConsulta.DATOS_REMOTOS_INVALIDOS,
            errores_inventario=exc_corrupto.errores,
            token_para_sanitizar=token_efectivo,
        ) from exc_corrupto
    except (ErrorEstructuraInventario, ErrorValidacionInventario, ErrorInventario) as exc_esquema:
        raise ErrorEsquemaInventarioRemoto(
            f"El inventario remoto '{config.ruta_archivo_normalizada}' incumple el esquema o las "
            f"reglas de integridad aprobadas: {exc_esquema.mensaje}",
            codigo=CodigoErrorGitHub.ESQUEMA_INVENTARIO_INVALIDO,
            categoria=CategoriaResultadoConsulta.DATOS_REMOTOS_INVALIDOS,
            errores_inventario=exc_esquema.errores,
            token_para_sanitizar=token_efectivo,
        ) from exc_esquema

    sha256_local = hashlib.sha256(contenido_bytes).hexdigest()

    return ResultadoLecturaInventarioRemoto(
        propietario=config.propietario,
        repositorio=config.repositorio,
        rama=config.rama,
        ruta_archivo=config.ruta_archivo_normalizada,
        sha_github=sha_github,
        sha256_local=sha256_local,
        tamano_bytes=len(contenido_bytes),
        inventario=inventario_validado,
        categoria_consulta=CategoriaResultadoConsulta.INVENTARIO_DISPONIBLE,
    )


def preparar_inicializacion_desde_consulta_remota(
    config: ConfiguracionRepositorioGitHub = CONFIGURACION_POR_DEFECTO,
    *,
    token: str | None = None,
    ejecutor_http: EjecutorHTTP | None = None,
    ruta_local_control: str | Path | None = None,
) -> tuple[ResultadoExistenciaRemota, bytes]:
    """Integra la consulta de existencia de GitHub con `preparar_inicializacion_segura(...)` del motor Excel.

    - Si el estado remoto es `EXISTE`, `preparar_inicializacion_segura` lanza `ErrorProteccionInventario`.
    - Si el estado remoto es `DESCONOCIDO_ERROR` (por fallo de red, permisos, rama/repo inaccesible, etc.),
      `preparar_inicializacion_segura` lanza `ErrorProteccionInventario`.
    - Solo cuando se confirma `NO_EXISTE` devuelve `(resultado_existencia, bytes_demostrativos)` en memoria,
      sin escribir en disco ni en GitHub.
    """
    resultado_existencia = consultar_existencia_inventario_remoto(
        config=config,
        token=token,
        ejecutor_http=ejecutor_http,
        lanzar_excepcion=False,
    )
    bytes_iniciales = preparar_inicializacion_segura(
        estado_remoto=resultado_existencia.estado,
        ruta_local_control=ruta_local_control,
    )
    return resultado_existencia, bytes_iniciales
