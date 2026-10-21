"""Motor administrativo de consulta, creación y edición local de productos y ubicaciones.

Proyecto: FerreteríaMS v0
Tarea: FERMS-V0-P09 (Gestión administrativa de productos y ubicaciones)
Requisitos relacionados: RF-011, RF-012, RF-013, RF-014, RF-015, RF-016, RF-017,
RF-018, RF-019, RF-020, RF-021, RF-022, RF-023, RF-024, RF-027 (preparación SHA).
Criterios relacionados: CA-009, CA-010, CA-011, CA-012 (local), CA-013 (local),
CA-014, CA-015, CA-016, CA-017, CA-018, CA-019, CA-022, CA-027, CA-028, CA-029,
CA-030, CA-044, CA-045, CA-046, CA-047, CA-048, CA-049, CA-050, CA-051 (local),
CA-055, CA-057, CA-058.

Límite esencial del Prompt 09:
Este módulo opera exclusivamente sobre copias de trabajo validadas en memoria.
NO escribe en GitHub mediante API, NO ejecuta solicitudes HTTP de escritura remota
y NO crea ni modifica el archivo maestro definitivo `03_Aplicacion/inventario.xlsx`.
La persistencia remota y la resolución de conflictos SHA en GitHub Contents API
corresponden exclusivamente al Prompt 10.
"""

from __future__ import annotations

import copy
import html
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Sequence

import pandas as pd

_DIRECTORIO_ACTUAL = Path(__file__).resolve().parent
if str(_DIRECTORIO_ACTUAL) not in sys.path:
    sys.path.insert(0, str(_DIRECTORIO_ACTUAL))

import autenticacion  # noqa: E402
import github_inventario  # noqa: E402
import inventario as motor_inventario  # noqa: E402
from autenticacion import (  # noqa: E402
    BorradorTemporalAdmin,
    CodigoResultadoAutenticacion,
    ContextoDispositivo,
    ErrorAutenticacionAdmin,
    ErrorAutorizacionAdmin,
    ErrorSeguridadBorradorAdmin,
    EstadoSesionAdmin,
    ProveedorReloj,
    consultar_estado_bloqueo_admin,
    descartar_borrador_admin,
    detectar_contexto_dispositivo,
    esta_autenticado_en_sesion,
    guardar_borrador_admin,
    obtener_borrador_admin,
    ocultar_secretos_autenticacion,
    registrar_actividad_administrativa,
    requerir_autorizacion_admin,
    restaurar_borrador_admin,
    tiene_borrador_pendiente_en_sesion,
)
from busqueda import normalizar_texto_busqueda  # noqa: E402
from github_inventario import (  # noqa: E402
    CONFIGURACION_POR_DEFECTO,
    ConfiguracionRepositorioGitHub,
    ErrorArchivoExcelRemotoCorrupto,
    ErrorArchivoRemotoInexistente,
    ErrorEsquemaInventarioRemoto,
    ErrorLecturaGitHub,
    ResultadoLecturaInventarioRemoto,
    ocultar_secretos_en_texto,
)
from inventario import (  # noqa: E402
    ESQUEMA_HOJAS,
    HOJA_ASIGNACIONES,
    HOJA_CATEGORIAS,
    HOJA_PRODUCTOS,
    HOJA_UBICACIONES,
    ORDEN_HOJAS,
    CodigoErrorInventario,
    DetalleErrorInventario,
    ErrorInventario,
    ErrorValidacionInventario,
    InventarioDatos,
    construir_inventario_datos,
    crear_inventario_demostrativo,
    formatear_ubicacion_fisica,
    normalizar_valor_principal,
    obtener_producto_por_codigo,
    obtener_productos_estructurados,
    validar_inventario,
)

# Claves de estado de sesión para la capa de edición administrativa temporal
CLAVE_ESPACIO_TRABAJO_ADMIN: str = "ferms_espacio_trabajo_admin"
CLAVE_RESULTADO_CARGA_ADMIN: str = "ferms_resultado_carga_admin"
CLAVE_MODO_VISTA_ADMIN: str = "ferms_modo_vista_admin"
CLAVE_PRODUCTO_ADMIN_SELECCIONADO: str = "ferms_producto_admin_seleccionado"
CLAVE_TERMINO_FILTRO_ADMIN: str = "ferms_termino_filtro_admin"
CLAVE_MENSAJE_OPERACION_ADMIN: str = "ferms_mensaje_operacion_admin"
CLAVE_FORMULARIO_BORRADOR_ADMIN: str = "ferms_formulario_borrador_admin"

# Límites de validación para los campos de texto de productos
LONGITUD_MAXIMA_CODIGO_PRODUCTO: int = 64
LONGITUD_MAXIMA_NOMBRE_PRODUCTO: int = 200
LONGITUD_MAXIMA_DESCRIPCION_PRODUCTO: int = 2000

# Textos y avisos claros diferenciados (Sección 10 del Prompt 09)
MENSAJE_INVENTARIO_DISPONIBLE_EDICION_LOCAL: str = (
    "Inventario cargado en memoria de trabajo. Las creaciones y ediciones se validan "
    "localmente y permanecen pendientes de guardar en GitHub (Prompt 10)."
)
MENSAJE_INVENTARIO_REMOTO_INEXISTENTE_ADMIN: str = (
    "GitHub confirmó que el archivo maestro 'inventario.xlsx' todavía no existe en el "
    "repositorio remoto. Durante esta etapa no se crea automáticamente en disco ni en GitHub; "
    "puedes preparar una copia de trabajo demostrativa en memoria para edición local."
)
MENSAJE_ERROR_CONEXION_ADMIN: str = (
    "No fue posible descargar el inventario para administración debido a un error de "
    "conexión o acceso con GitHub API. Verifica la conexión e intenta nuevamente."
)
MENSAJE_DATOS_REMOTOS_INVALIDOS_ADMIN: str = (
    "El inventario remoto descargado presenta inconsistencias de estructura o integridad "
    "y fue rechazado para evitar trabajar sobre datos corruptos."
)
MENSAJE_CREACION_LOCAL_EXITOSA: str = (
    "Producto validado y registrado en la copia temporal de trabajo (cambio local "
    "pendiente de guardar; aún no persistido en GitHub)."
)
MENSAJE_EDICION_LOCAL_EXITOSA: str = (
    "Modificación validada y aplicada en la copia temporal de trabajo (cambio local "
    "pendiente de guardar; aún no persistido en GitHub)."
)
MENSAJE_CAMBIO_PRINCIPAL_LOCAL_EXITOSO: str = (
    "Ubicación principal actualizada en la copia temporal de trabajo (cambio local "
    "pendiente de guardar; aún no persistido en GitHub)."
)
MENSAJE_ELIMINACION_SECUNDARIA_LOCAL_EXITOSA: str = (
    "Ubicación secundaria retirada en la copia temporal de trabajo (cambio local "
    "pendiente de guardar; aún no persistido en GitHub)."
)
MENSAJE_CAMBIOS_LOCALES_DESCARTADOS: str = (
    "Se descartaron las modificaciones locales no guardadas y se restauró la copia "
    "base original del inventario en memoria."
)
MENSAJE_CATALOGO_PREDEFINIDO_NO_EDITABLE: str = (
    "En FerreteríaMS v0 los catálogos de Categorías y Ubicaciones físicas están "
    "predefinidos en el archivo Excel (RF-021). Su creación, edición o eliminación "
    "directa no está permitida en esta etapa."
)


class ModoVistaAdmin(str, Enum):
    """Subvistas del panel administrativo de Productos."""

    INICIAL = "INICIAL"
    CONSULTA = "CONSULTA"
    CREAR_PRODUCTO = "CREAR_PRODUCTO"
    EDITAR_PRODUCTO = "EDITAR_PRODUCTO"


class EstadoInventarioAdmin(str, Enum):
    """Estados diferenciables del inventario y la edición administrativa (Sección 10)."""

    NO_CARGADO = "NO_CARGADO"
    INVENTARIO_DISPONIBLE_EDICION_LOCAL = "INVENTARIO_DISPONIBLE_EDICION_LOCAL"
    INVENTARIO_REMOTO_INEXISTENTE = "INVENTARIO_REMOTO_INEXISTENTE"
    ERROR_CONEXION = "ERROR_CONEXION"
    DATOS_REMOTOS_INVALIDOS = "DATOS_REMOTOS_INVALIDOS"
    ERROR_VALIDACION_ADMINISTRATIVA = "ERROR_VALIDACION_ADMINISTRATIVA"
    MODIFICACION_LOCAL_VALIDA = "MODIFICACION_LOCAL_VALIDA"
    CAMBIOS_LOCALES_PENDIENTES = "CAMBIOS_LOCALES_PENDIENTES"
    SESION_ADMINISTRATIVA_EXPIRADA = "SESION_ADMINISTRATIVA_EXPIRADA"
    BORRADOR_TEMPORAL_RECUPERABLE = "BORRADOR_TEMPORAL_RECUPERABLE"


class CodigoErrorAdministrativo(str, Enum):
    """Códigos estructurados para los rechazos de validación y seguridad del Prompt 09."""

    AUTORIZACION_INVALIDA = "AUTORIZACION_INVALIDA"
    SESION_EXPIRADA = "SESION_EXPIRADA"
    DISPOSITIVO_NO_PERMITIDO = "DISPOSITIVO_NO_PERMITIDO"
    ESPACIO_TRABAJO_NO_INICIALIZADO = "ESPACIO_TRABAJO_NO_INICIALIZADO"
    SESION_PROPIETARIA_DISTINTA = "SESION_PROPIETARIA_DISTINTA"
    CODIGO_PRODUCTO_OBLIGATORIO = "CODIGO_PRODUCTO_OBLIGATORIO"
    CODIGO_PRODUCTO_INVALIDO = "CODIGO_PRODUCTO_INVALIDO"
    CODIGO_PRODUCTO_DUPLICADO = "CODIGO_PRODUCTO_DUPLICADO"
    CODIGO_PRODUCTO_INMUTABLE = "CODIGO_PRODUCTO_INMUTABLE"
    PRODUCTO_NO_EXISTE = "PRODUCTO_NO_EXISTE"
    NOMBRE_PRODUCTO_OBLIGATORIO = "NOMBRE_PRODUCTO_OBLIGATORIO"
    NOMBRE_PRODUCTO_INVALIDO = "NOMBRE_PRODUCTO_INVALIDO"
    DESCRIPCION_PRODUCTO_INVALIDA = "DESCRIPCION_PRODUCTO_INVALIDA"
    CATEGORIA_OBLIGATORIA = "CATEGORIA_OBLIGATORIA"
    CATEGORIA_INEXISTENTE = "CATEGORIA_INEXISTENTE"
    UBICACION_INEXISTENTE = "UBICACION_INEXISTENTE"
    PRODUCTO_SIN_UBICACION = "PRODUCTO_SIN_UBICACION"
    SIN_UBICACION_PRINCIPAL = "SIN_UBICACION_PRINCIPAL"
    UBICACION_PRINCIPAL_MULTIPLE = "UBICACION_PRINCIPAL_MULTIPLE"
    ASIGNACION_DUPLICADA = "ASIGNACION_DUPLICADA"
    ELIMINACION_UNICA_UBICACION = "ELIMINACION_UNICA_UBICACION"
    OPERACION_CATALOGO_NO_PERMITIDA = "OPERACION_CATALOGO_NO_PERMITIDA"
    INTEGRIDAD_INVENTARIO_INVALIDA = "INTEGRIDAD_INVENTARIO_INVALIDA"
    BORRADOR_INVALIDO_O_VENCIDO = "BORRADOR_INVALIDO_O_VENCIDO"


class ErrorAdministracionInventario(Exception):
    """Excepción base de la capa administrativa de productos y ubicaciones."""

    def __init__(
        self,
        mensaje: str,
        *,
        codigo: CodigoErrorAdministrativo = CodigoErrorAdministrativo.INTEGRIDAD_INVENTARIO_INVALIDA,
        estado: EstadoInventarioAdmin = EstadoInventarioAdmin.ERROR_VALIDACION_ADMINISTRATIVA,
        errores_inventario: Sequence[DetalleErrorInventario] | None = None,
    ) -> None:
        mensaje_limpio = ocultar_secretos_en_texto(
            ocultar_secretos_autenticacion(str(mensaje))
        )
        super().__init__(mensaje_limpio)
        self.mensaje: str = mensaje_limpio
        self.codigo: CodigoErrorAdministrativo = codigo
        self.estado: EstadoInventarioAdmin = estado
        self.errores_inventario: list[DetalleErrorInventario] = (
            list(errores_inventario) if errores_inventario else []
        )


class ErrorValidacionAdministrativa(ErrorAdministracionInventario):
    """Se lanza cuando una creación, edición o asignación incumple las reglas de integridad."""


class ErrorSincronizacionBorradorAdmin(
    ErrorValidacionAdministrativa, ErrorSeguridadBorradorAdmin
):
    """Se lanza cuando falla la sincronización del borrador temporal y se revierte la operación local."""

    def __init__(
        self,
        mensaje: str,
        *,
        codigo: CodigoErrorAdministrativo = CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
        estado: EstadoInventarioAdmin = EstadoInventarioAdmin.ERROR_VALIDACION_ADMINISTRATIVA,
        errores_inventario: Sequence[DetalleErrorInventario] | None = None,
    ) -> None:
        ErrorValidacionAdministrativa.__init__(
            self,
            mensaje,
            codigo=codigo,
            estado=estado,
            errores_inventario=errores_inventario,
        )


@dataclass(frozen=True)
class AsignacionUbicacionEntrada:
    """Representa una asignación candidata de ubicación física para un producto."""

    ubicacion_id: str
    principal: str = "No"

    @property
    def es_principal(self) -> bool:
        return normalizar_valor_principal(self.principal) == "Sí"


@dataclass(frozen=True)
class OperacionLocalInventario:
    """Registro inmutable de una operación administrativa validada en memoria."""

    tipo_operacion: str
    codigo_producto: str
    nombre: str
    categoria_id: str
    descripcion: str
    asignaciones: tuple[dict[str, str], ...]
    realizada_en_epoch: float

    def a_diccionario_serializable(self) -> dict[str, Any]:
        """Convierte la operación a un diccionario seguro apto para borradores temporales."""
        return {
            "tipo_operacion": self.tipo_operacion,
            "codigo_producto": self.codigo_producto,
            "nombre": self.nombre,
            "categoria_id": self.categoria_id,
            "descripcion": self.descripcion,
            "asignaciones": [dict(a) for a in self.asignaciones],
            "realizada_en_epoch": self.realizada_en_epoch,
        }


@dataclass
class EspacioTrabajoAdminInventario:
    """Representación temporal aislada por sesión del inventario para edición local (Sección 6).

    Garantiza:
    - `inventario_original` permanece inmutable como línea base de comparación.
    - `inventario_trabajo` contiene las cuatro hojas validadas con los cambios locales.
    - `sha_base_remoto` conserva como referencia el SHA de GitHub del que partió la edición,
      sin tratarlo nunca como confirmación de escritura (`confirmado_en_github=False`).
    """

    inventario_original: InventarioDatos
    inventario_trabajo: InventarioDatos
    usuario_propietario: str
    id_sesion_propietaria: str = field(repr=False)
    sha_base_remoto: str | None = None
    origen_remoto_confirmado: bool = True
    codigos_productos_creados: tuple[str, ...] = ()
    codigos_productos_editados: tuple[str, ...] = ()
    historial_operaciones_locales: tuple[OperacionLocalInventario, ...] = ()
    creado_en_epoch: float = 0.0
    actualizado_en_epoch: float = 0.0
    confirmado_en_github: bool = False
    es_copia_local_temporal: bool = True

    @property
    def tiene_cambios_locales_pendientes(self) -> bool:
        """Indica si la copia de trabajo difiere del inventario original cargado."""
        if self.codigos_productos_creados or self.codigos_productos_editados:
            return True
        if self.historial_operaciones_locales:
            return True
        return not inventarios_son_identicos(
            self.inventario_original, self.inventario_trabajo
        )

    @property
    def total_productos_modificados_localmente(self) -> int:
        return len(
            set(self.codigos_productos_creados) | set(self.codigos_productos_editados)
        )

    @property
    def estado_actual(self) -> EstadoInventarioAdmin:
        if self.tiene_cambios_locales_pendientes:
            return EstadoInventarioAdmin.CAMBIOS_LOCALES_PENDIENTES
        return EstadoInventarioAdmin.INVENTARIO_DISPONIBLE_EDICION_LOCAL


@dataclass(frozen=True)
class ResultadoCargaInventarioAdmin:
    """Resultado estructurado de la carga o preparación del inventario para administración."""

    estado: EstadoInventarioAdmin
    mensaje_usuario: str
    detalle_tecnico: str = ""
    espacio_trabajo: EspacioTrabajoAdminInventario | None = None
    sha_base_remoto: str | None = None
    permite_reintentar: bool = False
    permite_inicializar_demo_local: bool = False
    confirmado_en_github: bool = False


@dataclass(frozen=True)
class ResultadoOperacionProductoAdmin:
    """Resultado estructurado de una operación local de creación o edición de producto."""

    exito: bool
    estado: EstadoInventarioAdmin
    mensaje_usuario: str
    codigo_producto: str = ""
    codigo_error: CodigoErrorAdministrativo | None = None
    producto: dict[str, Any] | None = None
    espacio_trabajo: EspacioTrabajoAdminInventario | None = None
    sha_base_remoto: str | None = None
    tiene_cambios_pendientes: bool = False
    confirmado_en_github: bool = False
    es_cambio_local_temporal: bool = True


@dataclass(frozen=True)
class PaquetePublicacionPendienteP10:
    """Contrato de datos preparado para la futura escritura remota del Prompt 10 (Secciones 6 y 9).

    No realiza ninguna escritura remota ni crea archivos locales.
    """

    inventario_validado: InventarioDatos
    sha_base_remoto: str | None
    origen_remoto_confirmado: bool
    tiene_cambios_pendientes: bool
    codigos_productos_creados: tuple[str, ...]
    codigos_productos_editados: tuple[str, ...]
    total_operaciones_locales: int
    confirmado_en_github: bool = False


DescargadorRemotoAdmin = Callable[..., ResultadoLecturaInventarioRemoto]


def escapar_texto_presentacion_segura(texto: Any) -> str:
    """Escapa caracteres HTML especiales para impedir inyecciones en la interfaz (Sección 11)."""
    if texto is None:
        return ""
    return html.escape(str(texto), quote=True)


def clonar_inventario_datos(inventario: InventarioDatos) -> InventarioDatos:
    """Crea una copia profunda e independiente de las cuatro hojas y valida su integridad."""
    if not isinstance(inventario, InventarioDatos):
        raise ErrorValidacionAdministrativa(
            "El objeto proporcionado no es una instancia válida de InventarioDatos.",
            codigo=CodigoErrorAdministrativo.INTEGRIDAD_INVENTARIO_INVALIDA,
        )
    hojas_copia = {
        nombre_hoja: df.copy(deep=True)
        for nombre_hoja, df in inventario.obtener_hojas().items()
    }
    try:
        return construir_inventario_datos(hojas_copia)
    except ErrorInventario as exc:
        raise _convertir_error_motor_inventario(exc) from exc


def inventarios_son_identicos(
    inv_a: InventarioDatos,
    inv_b: InventarioDatos,
) -> bool:
    """Compara si dos instancias de `InventarioDatos` contienen exactamente los mismos datos."""
    hojas_a = inv_a.obtener_hojas()
    hojas_b = inv_b.obtener_hojas()
    for nombre_hoja in ORDEN_HOJAS:
        df_a = hojas_a[nombre_hoja].reset_index(drop=True)
        df_b = hojas_b[nombre_hoja].reset_index(drop=True)
        if not df_a.equals(df_b):
            return False
    return True


def _convertir_error_motor_inventario(
    exc: ErrorInventario,
) -> ErrorValidacionAdministrativa:
    """Traduce una excepción de `inventario.py` a `ErrorValidacionAdministrativa` conservando su detalle."""
    mapa_codigos: dict[CodigoErrorInventario, CodigoErrorAdministrativo] = {
        CodigoErrorInventario.IDENTIFICADOR_DUPLICADO: CodigoErrorAdministrativo.CODIGO_PRODUCTO_DUPLICADO,
        CodigoErrorInventario.CATEGORIA_INEXISTENTE: CodigoErrorAdministrativo.CATEGORIA_INEXISTENTE,
        CodigoErrorInventario.UBICACION_INEXISTENTE: CodigoErrorAdministrativo.UBICACION_INEXISTENTE,
        CodigoErrorInventario.PRODUCTO_INEXISTENTE: CodigoErrorAdministrativo.PRODUCTO_NO_EXISTE,
        CodigoErrorInventario.PRODUCTO_SIN_ASIGNACION: CodigoErrorAdministrativo.PRODUCTO_SIN_UBICACION,
        CodigoErrorInventario.SIN_UBICACION_PRINCIPAL: CodigoErrorAdministrativo.SIN_UBICACION_PRINCIPAL,
        CodigoErrorInventario.UBICACION_PRINCIPAL_MULTIPLE: CodigoErrorAdministrativo.UBICACION_PRINCIPAL_MULTIPLE,
        CodigoErrorInventario.ASIGNACION_DUPLICADA: CodigoErrorAdministrativo.ASIGNACION_DUPLICADA,
        CodigoErrorInventario.VALOR_PRINCIPAL_INVALIDO: CodigoErrorAdministrativo.SIN_UBICACION_PRINCIPAL,
    }
    codigo_admin = mapa_codigos.get(
        exc.codigo, CodigoErrorAdministrativo.INTEGRIDAD_INVENTARIO_INVALIDA
    )
    return ErrorValidacionAdministrativa(
        exc.mensaje,
        codigo=codigo_admin,
        errores_inventario=exc.errores,
    )


def _sincronizar_borrador_tras_expiracion_si_corresponde(
    estado: Any,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> None:
    """Si la sesión acaba de expirar, desactiva el espacio de trabajo activo en sesión."""
    if not isinstance(estado, MutableMapping):
        return
    if not esta_autenticado_en_sesion(estado, reloj=reloj, ahora_epoch=ahora_epoch):
        # No se permite seguir operando sobre el espacio de trabajo sin reautenticación;
        # los cambios previos permanecen en el borrador retenido del servidor por 15 min.
        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = None


def _exigir_sesion_admin_autorizada(
    estado: Any,
    *,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
    registrar_actividad: bool = True,
) -> EstadoSesionAdmin:
    """Verifica autorización administrativa vigente en Python antes de cualquier operación (Sección 7).

    - Comprueba primero que no exista un bloqueo activo.
    - Verifica contexto de dispositivo (rechaza móvil con `DISPOSITIVO_NO_PERMITIDO`).
    - Verifica sesión activa y no expirada en `_SESIONES_ACTIVAS_SERVIDOR`.
    - Registra actividad administrativa únicamente cuando `registrar_actividad=True`.
    """
    estado_bloqueo = consultar_estado_bloqueo_admin(
        reloj=reloj, ahora_epoch=ahora_epoch
    )
    if estado_bloqueo.esta_bloqueado:
        raise ErrorAutorizacionAdmin(
            estado_bloqueo.mensaje_usuario,
            codigo=CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE,
        )

    _sincronizar_borrador_tras_expiracion_si_corresponde(
        estado, reloj=reloj, ahora_epoch=ahora_epoch
    )

    sesion_actual = requerir_autorizacion_admin(
        estado,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
    )
    if registrar_actividad:
        sesion_actual = registrar_actividad_administrativa(
            estado,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
            ahora_epoch=ahora_epoch,
        )
    return sesion_actual


def _obtener_espacio_trabajo_autorizado(
    estado: Any,
    *,
    espacio_explicito: EspacioTrabajoAdminInventario | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
    registrar_actividad: bool = True,
) -> tuple[EstadoSesionAdmin, EspacioTrabajoAdminInventario]:
    """Obtiene el espacio de trabajo verificando que pertenezca exclusivamente a la sesión actual."""
    sesion = _exigir_sesion_admin_autorizada(
        estado,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=registrar_actividad,
    )
    espacio: Any = (
        espacio_explicito
        if espacio_explicito is not None
        else (
            estado.get(CLAVE_ESPACIO_TRABAJO_ADMIN)
            if isinstance(estado, Mapping)
            else None
        )
    )
    if not isinstance(espacio, EspacioTrabajoAdminInventario):
        raise ErrorAdministracionInventario(
            "El inventario administrativo aún no ha sido inicializado en la sesión actual.",
            codigo=CodigoErrorAdministrativo.ESPACIO_TRABAJO_NO_INICIALIZADO,
            estado=EstadoInventarioAdmin.NO_CARGADO,
        )

    # Aislamiento estricto entre sesiones y cuentas administrativas (Secciones 7 y 11)
    if (
        espacio.usuario_propietario != sesion.usuario
        or espacio.id_sesion_propietaria != sesion.token_sesion
    ):
        raise ErrorAutorizacionAdmin(
            "Acceso denegado: el espacio de trabajo administrativo pertenece a otra sesión.",
            codigo=CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS,
        )

    return sesion, espacio


def _validar_codigo_producto_texto(codigo_producto: Any) -> str:
    """Valida que `Codigo_Producto` sea texto no vacío y preserve ceros iniciales (Sección 4)."""
    if not isinstance(codigo_producto, str):
        raise ErrorValidacionAdministrativa(
            "El código de producto debe proporcionarse como texto para conservar ceros iniciales.",
            codigo=CodigoErrorAdministrativo.CODIGO_PRODUCTO_OBLIGATORIO,
        )
    limpio = codigo_producto.strip()
    if not limpio:
        raise ErrorValidacionAdministrativa(
            "El campo 'Codigo_Producto' es obligatorio y no puede estar vacío.",
            codigo=CodigoErrorAdministrativo.CODIGO_PRODUCTO_OBLIGATORIO,
        )
    if len(limpio) > LONGITUD_MAXIMA_CODIGO_PRODUCTO:
        raise ErrorValidacionAdministrativa(
            f"El código de producto excede la longitud máxima permitida ({LONGITUD_MAXIMA_CODIGO_PRODUCTO} caracteres).",
            codigo=CodigoErrorAdministrativo.CODIGO_PRODUCTO_INVALIDO,
        )
    if any(ord(c) < 32 or ord(c) == 127 for c in limpio):
        raise ErrorValidacionAdministrativa(
            "El código de producto contiene caracteres de control no permitidos.",
            codigo=CodigoErrorAdministrativo.CODIGO_PRODUCTO_INVALIDO,
        )
    return limpio


def _validar_nombre_producto_texto(nombre: Any) -> str:
    """Valida que `Nombre` sea texto obligatorio, limpio y sin caracteres de control."""
    if not isinstance(nombre, str):
        raise ErrorValidacionAdministrativa(
            "El nombre del producto es obligatorio y debe ser un texto válido.",
            codigo=CodigoErrorAdministrativo.NOMBRE_PRODUCTO_OBLIGATORIO,
        )
    limpio = nombre.strip()
    if not limpio:
        raise ErrorValidacionAdministrativa(
            "El campo 'Nombre' del producto es obligatorio y no puede estar vacío.",
            codigo=CodigoErrorAdministrativo.NOMBRE_PRODUCTO_OBLIGATORIO,
        )
    if len(limpio) > LONGITUD_MAXIMA_NOMBRE_PRODUCTO:
        raise ErrorValidacionAdministrativa(
            f"El nombre del producto excede la longitud máxima permitida ({LONGITUD_MAXIMA_NOMBRE_PRODUCTO} caracteres).",
            codigo=CodigoErrorAdministrativo.NOMBRE_PRODUCTO_INVALIDO,
        )
    if any(ord(c) < 32 or ord(c) == 127 for c in limpio):
        raise ErrorValidacionAdministrativa(
            "El nombre del producto contiene caracteres de control no permitidos.",
            codigo=CodigoErrorAdministrativo.NOMBRE_PRODUCTO_INVALIDO,
        )
    return limpio


def _validar_descripcion_producto_texto(descripcion: Any) -> str:
    """Valida que `Descripcion` sea texto opcional válido sin caracteres de control."""
    if descripcion is None:
        return ""
    if not isinstance(descripcion, str):
        raise ErrorValidacionAdministrativa(
            "La descripción del producto debe ser una cadena de texto.",
            codigo=CodigoErrorAdministrativo.DESCRIPCION_PRODUCTO_INVALIDA,
        )
    limpio = descripcion.strip()
    if len(limpio) > LONGITUD_MAXIMA_DESCRIPCION_PRODUCTO:
        raise ErrorValidacionAdministrativa(
            f"La descripción excede la longitud máxima permitida ({LONGITUD_MAXIMA_DESCRIPCION_PRODUCTO} caracteres).",
            codigo=CodigoErrorAdministrativo.DESCRIPCION_PRODUCTO_INVALIDA,
        )
    if any((ord(c) < 32 and c not in ("\n", "\r", "\t")) or ord(c) == 127 for c in limpio):
        raise ErrorValidacionAdministrativa(
            "La descripción del producto contiene caracteres de control no permitidos.",
            codigo=CodigoErrorAdministrativo.DESCRIPCION_PRODUCTO_INVALIDA,
        )
    return limpio


def _validar_categoria_existente(
    categoria_id: Any,
    df_categorias: pd.DataFrame,
) -> str:
    """Valida que `Categoria_ID` no esté vacío y exista en la hoja `Categorías`."""
    if not isinstance(categoria_id, str) or not categoria_id.strip():
        raise ErrorValidacionAdministrativa(
            "Debe seleccionarse una categoría válida para el producto.",
            codigo=CodigoErrorAdministrativo.CATEGORIA_OBLIGATORIA,
        )
    limpio = categoria_id.strip()
    categorias_registradas = set(df_categorias["Categoria_ID"].astype(str).str.strip())
    if limpio not in categorias_registradas:
        raise ErrorValidacionAdministrativa(
            f"La categoría '{limpio}' no existe en el catálogo predefinido de Categorías.",
            codigo=CodigoErrorAdministrativo.CATEGORIA_INEXISTENTE,
        )
    return limpio


def _normalizar_y_validar_asignaciones_entrada(
    *,
    df_ubicaciones: pd.DataFrame,
    ubicaciones_ids: Sequence[Any] | None = None,
    ubicacion_principal_id: Any = None,
    asignaciones: Sequence[Mapping[str, Any] | AsignacionUbicacionEntrada] | None = None,
) -> list[dict[str, str]]:
    """Valida que el producto tenga al menos una ubicación existente, sin duplicados y exactamente una principal."""
    ubicaciones_registradas = set(df_ubicaciones["Ubicacion_ID"].astype(str).str.strip())
    filas_normalizadas: list[dict[str, str]] = []

    if asignaciones is not None:
        if not isinstance(asignaciones, Sequence) or isinstance(asignaciones, (str, bytes)):
            raise ErrorValidacionAdministrativa(
                "Las asignaciones de ubicación deben proporcionarse como una secuencia válida.",
                codigo=CodigoErrorAdministrativo.PRODUCTO_SIN_UBICACION,
            )
        if len(asignaciones) == 0:
            raise ErrorValidacionAdministrativa(
                "Cada producto debe tener al menos una ubicación física asignada.",
                codigo=CodigoErrorAdministrativo.PRODUCTO_SIN_UBICACION,
            )

        ubicaciones_vistas: set[str] = set()
        principales_contadas = 0
        for item in asignaciones:
            if isinstance(item, AsignacionUbicacionEntrada):
                ubic_raw = item.ubicacion_id
                prin_raw: Any = item.principal
            elif isinstance(item, Mapping):
                ubic_raw = item.get("Ubicacion_ID", item.get("ubicacion_id", ""))
                if "Principal" in item:
                    prin_raw = item["Principal"]
                elif "principal" in item:
                    prin_raw = item["principal"]
                elif "es_principal" in item:
                    prin_raw = "Sí" if bool(item["es_principal"]) else "No"
                else:
                    prin_raw = "No"
            else:
                raise ErrorValidacionAdministrativa(
                    "Formato de asignación de ubicación inválido.",
                    codigo=CodigoErrorAdministrativo.PRODUCTO_SIN_UBICACION,
                )

            if not isinstance(ubic_raw, str) or not ubic_raw.strip():
                raise ErrorValidacionAdministrativa(
                    "El identificador de ubicación ('Ubicacion_ID') no puede estar vacío.",
                    codigo=CodigoErrorAdministrativo.UBICACION_INEXISTENTE,
                )
            ubic_id = ubic_raw.strip()
            if ubic_id not in ubicaciones_registradas:
                raise ErrorValidacionAdministrativa(
                    f"La ubicación '{ubic_id}' no existe en el catálogo de Ubicaciones.",
                    codigo=CodigoErrorAdministrativo.UBICACION_INEXISTENTE,
                )
            if ubic_id in ubicaciones_vistas:
                raise ErrorValidacionAdministrativa(
                    f"Asignación duplicada: la ubicación '{ubic_id}' se indicó más de una vez para el mismo producto.",
                    codigo=CodigoErrorAdministrativo.ASIGNACION_DUPLICADA,
                )
            ubicaciones_vistas.add(ubic_id)

            if isinstance(prin_raw, bool):
                marca_principal = "Sí" if prin_raw else "No"
            else:
                try:
                    marca_principal = normalizar_valor_principal(prin_raw)
                except ErrorInventario as exc:
                    raise ErrorValidacionAdministrativa(
                        exc.mensaje,
                        codigo=CodigoErrorAdministrativo.SIN_UBICACION_PRINCIPAL,
                    ) from exc

            if marca_principal == "Sí":
                principales_contadas += 1

            filas_normalizadas.append(
                {"Ubicacion_ID": ubic_id, "Principal": marca_principal}
            )

        if principales_contadas == 0:
            raise ErrorValidacionAdministrativa(
                "El producto debe tener exactamente una ubicación marcada como principal ('Sí').",
                codigo=CodigoErrorAdministrativo.SIN_UBICACION_PRINCIPAL,
            )
        if principales_contadas > 1:
            raise ErrorValidacionAdministrativa(
                f"El producto tiene {principales_contadas} ubicaciones marcadas como principales; solo se permite exactamente una.",
                codigo=CodigoErrorAdministrativo.UBICACION_PRINCIPAL_MULTIPLE,
            )
        return filas_normalizadas

    # Construcción desde `ubicaciones_ids` + `ubicacion_principal_id`
    if (
        ubicaciones_ids is None
        or not isinstance(ubicaciones_ids, Sequence)
        or isinstance(ubicaciones_ids, (str, bytes))
        or len(ubicaciones_ids) == 0
    ):
        raise ErrorValidacionAdministrativa(
            "Cada producto debe tener al menos una ubicación física asignada.",
            codigo=CodigoErrorAdministrativo.PRODUCTO_SIN_UBICACION,
        )

    ubic_vistas_seq: set[str] = set()
    lista_ubic_limpias: list[str] = []
    for u_raw in ubicaciones_ids:
        if not isinstance(u_raw, str) or not u_raw.strip():
            raise ErrorValidacionAdministrativa(
                "El identificador de ubicación ('Ubicacion_ID') no puede estar vacío.",
                codigo=CodigoErrorAdministrativo.UBICACION_INEXISTENTE,
            )
        u_id = u_raw.strip()
        if u_id not in ubicaciones_registradas:
            raise ErrorValidacionAdministrativa(
                f"La ubicación '{u_id}' no existe en el catálogo predefinido de Ubicaciones.",
                codigo=CodigoErrorAdministrativo.UBICACION_INEXISTENTE,
            )
        if u_id in ubic_vistas_seq:
            raise ErrorValidacionAdministrativa(
                f"Asignación duplicada: la ubicación '{u_id}' se seleccionó más de una vez.",
                codigo=CodigoErrorAdministrativo.ASIGNACION_DUPLICADA,
            )
        ubic_vistas_seq.add(u_id)
        lista_ubic_limpias.append(u_id)

    if isinstance(ubicacion_principal_id, (list, tuple, set)):
        if len(ubicacion_principal_id) == 0:
            raise ErrorValidacionAdministrativa(
                "Debe seleccionarse explícitamente una ubicación principal para el producto.",
                codigo=CodigoErrorAdministrativo.SIN_UBICACION_PRINCIPAL,
            )
        if len(ubicacion_principal_id) > 1:
            raise ErrorValidacionAdministrativa(
                "No se permite seleccionar dos o más ubicaciones principales para un producto.",
                codigo=CodigoErrorAdministrativo.UBICACION_PRINCIPAL_MULTIPLE,
            )
        ubicacion_principal_id = next(iter(ubicacion_principal_id))

    if not isinstance(ubicacion_principal_id, str) or not ubicacion_principal_id.strip():
        raise ErrorValidacionAdministrativa(
            "Debe seleccionarse explícitamente una ubicación principal válida para el producto.",
            codigo=CodigoErrorAdministrativo.SIN_UBICACION_PRINCIPAL,
        )

    principal_limpia = ubicacion_principal_id.strip()
    if principal_limpia not in ubicaciones_registradas:
        raise ErrorValidacionAdministrativa(
            f"La ubicación principal '{principal_limpia}' no existe en el catálogo de Ubicaciones.",
            codigo=CodigoErrorAdministrativo.UBICACION_INEXISTENTE,
        )
    if principal_limpia not in ubic_vistas_seq:
        raise ErrorValidacionAdministrativa(
            f"La ubicación principal '{principal_limpia}' debe formar parte de las ubicaciones asignadas al producto.",
            codigo=CodigoErrorAdministrativo.SIN_UBICACION_PRINCIPAL,
        )

    for u_id in lista_ubic_limpias:
        filas_normalizadas.append(
            {
                "Ubicacion_ID": u_id,
                "Principal": "Sí" if u_id == principal_limpia else "No",
            }
        )
    return filas_normalizadas


def _construir_resumen_borrador_espacio(
    espacio: EspacioTrabajoAdminInventario,
    formulario_activo: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Construye un diccionario seguro y sin secretos para conservar en el borrador de sesión."""
    operaciones_serializadas = [
        op.a_diccionario_serializable()
        for op in espacio.historial_operaciones_locales
    ]
    datos: dict[str, Any] = {
        "tipo_borrador_p09": "espacio_trabajo_productos",
        "sha_base_remoto": espacio.sha_base_remoto or "",
        "origen_remoto_confirmado": bool(espacio.origen_remoto_confirmado),
        "codigos_creados": list(espacio.codigos_productos_creados),
        "codigos_editados": list(espacio.codigos_productos_editados),
        "operaciones_locales": operaciones_serializadas,
    }
    if formulario_activo is not None:
        datos["formulario_activo"] = dict(formulario_activo)
    return datos


def _sincronizar_borrador_automatico_en_sesion(
    estado: Any,
    espacio: EspacioTrabajoAdminInventario,
    *,
    formulario_activo: Mapping[str, Any] | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> BorradorTemporalAdmin | None:
    """Sincroniza los cambios locales validados con el subsistema de borradores del Prompt 08.

    Si `guardar_borrador_admin()` rechaza la sincronización (por exceso de tamaño máximo,
    estructura inválida o cualquier otra restricción), propaga una excepción controlada
    antes de que las operaciones locales modifiquen el espacio de trabajo activo.
    """
    if not isinstance(estado, MutableMapping):
        return None
    formulario_efectivo: Mapping[str, Any] | None = formulario_activo
    if formulario_efectivo is None:
        previo = estado.get(CLAVE_FORMULARIO_BORRADOR_ADMIN)
        if isinstance(previo, Mapping):
            formulario_efectivo = previo
    if not espacio.tiene_cambios_locales_pendientes and not formulario_efectivo:
        return None
    datos_borrador = _construir_resumen_borrador_espacio(
        espacio, formulario_activo=formulario_efectivo
    )
    try:
        return guardar_borrador_admin(
            estado,
            datos_borrador,
            tipo_operacion="mantenimiento_productos_p09",
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
            ahora_epoch=ahora_epoch,
        )
    except ErrorAutorizacionAdmin:
        raise
    except Exception as exc_borr:
        raise ErrorSincronizacionBorradorAdmin(
            f"No fue posible sincronizar el borrador administrativo de la operación: {exc_borr}",
            codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
        ) from exc_borr


def inicializar_espacio_trabajo_desde_inventario(
    estado: MutableMapping[str, Any],
    inventario_base: InventarioDatos,
    *,
    sha_base_remoto: str | None = None,
    origen_remoto_confirmado: bool = True,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> EspacioTrabajoAdminInventario:
    """Inicializa una copia de trabajo aislada a partir de un `InventarioDatos` validado (Sección 6)."""
    if not isinstance(estado, MutableMapping):
        raise TypeError("Se requiere un mapeo mutable de sesión para inicializar el espacio de trabajo.")

    sesion = _exigir_sesion_admin_autorizada(
        estado,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=True,
    )
    copia_original = clonar_inventario_datos(inventario_base)
    copia_trabajo = clonar_inventario_datos(inventario_base)
    sha_limpio = (
        sha_base_remoto.strip()
        if isinstance(sha_base_remoto, str) and sha_base_remoto.strip()
        else None
    )

    espacio = EspacioTrabajoAdminInventario(
        inventario_original=copia_original,
        inventario_trabajo=copia_trabajo,
        usuario_propietario=sesion.usuario,
        id_sesion_propietaria=sesion.token_sesion,
        sha_base_remoto=sha_limpio,
        origen_remoto_confirmado=bool(origen_remoto_confirmado),
        creado_en_epoch=sesion.ultima_actividad_epoch,
        actualizado_en_epoch=sesion.ultima_actividad_epoch,
        confirmado_en_github=False,
        es_copia_local_temporal=True,
    )
    estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = espacio
    estado[CLAVE_RESULTADO_CARGA_ADMIN] = ResultadoCargaInventarioAdmin(
        estado=EstadoInventarioAdmin.INVENTARIO_DISPONIBLE_EDICION_LOCAL,
        mensaje_usuario=MENSAJE_INVENTARIO_DISPONIBLE_EDICION_LOCAL,
        espacio_trabajo=espacio,
        sha_base_remoto=sha_limpio,
        permite_reintentar=False,
        permite_inicializar_demo_local=False,
        confirmado_en_github=False,
    )
    return espacio


def cargar_inventario_administrativo_en_sesion(
    estado: MutableMapping[str, Any],
    *,
    config_github: ConfiguracionRepositorioGitHub = CONFIGURACION_POR_DEFECTO,
    descargador_remoto: DescargadorRemotoAdmin | None = None,
    inicializar_demo_si_no_existe: bool = False,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> ResultadoCargaInventarioAdmin:
    """Descarga el inventario remoto para administración o prepara copia demostrativa en memoria si no existe."""
    if not isinstance(estado, MutableMapping):
        raise TypeError("Se requiere un estado de sesión mutable para cargar el inventario administrativo.")

    _ = _exigir_sesion_admin_autorizada(
        estado,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=True,
    )
    lector = descargador_remoto or github_inventario.descargar_inventario_remoto

    try:
        lectura = lector(config=config_github)
        espacio = inicializar_espacio_trabajo_desde_inventario(
            estado,
            lectura.inventario,
            sha_base_remoto=lectura.sha_github,
            origen_remoto_confirmado=True,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
            ahora_epoch=ahora_epoch,
        )
        resultado = ResultadoCargaInventarioAdmin(
            estado=EstadoInventarioAdmin.INVENTARIO_DISPONIBLE_EDICION_LOCAL,
            mensaje_usuario=MENSAJE_INVENTARIO_DISPONIBLE_EDICION_LOCAL,
            espacio_trabajo=espacio,
            sha_base_remoto=lectura.sha_github,
            permite_reintentar=False,
            permite_inicializar_demo_local=False,
            confirmado_en_github=False,
        )
        estado[CLAVE_RESULTADO_CARGA_ADMIN] = resultado
        return resultado

    except ErrorArchivoRemotoInexistente as exc_no_existe:
        if inicializar_demo_si_no_existe:
            inv_demo = crear_inventario_demostrativo()
            espacio_demo = inicializar_espacio_trabajo_desde_inventario(
                estado,
                inv_demo,
                sha_base_remoto=None,
                origen_remoto_confirmado=False,
                contexto_dispositivo=contexto_dispositivo,
                reloj=reloj,
                ahora_epoch=ahora_epoch,
            )
            resultado_demo = ResultadoCargaInventarioAdmin(
                estado=EstadoInventarioAdmin.INVENTARIO_DISPONIBLE_EDICION_LOCAL,
                mensaje_usuario=(
                    "GitHub confirmó que 'inventario.xlsx' no existe todavía. Se inicializó "
                    "exclusivamente en memoria una copia local demostrativa para edición temporal "
                    "(sin crear archivos en disco ni escribir en GitHub)."
                ),
                detalle_tecnico=ocultar_secretos_en_texto(exc_no_existe.mensaje),
                espacio_trabajo=espacio_demo,
                sha_base_remoto=None,
                permite_reintentar=True,
                permite_inicializar_demo_local=False,
                confirmado_en_github=False,
            )
            estado[CLAVE_RESULTADO_CARGA_ADMIN] = resultado_demo
            return resultado_demo

        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = None
        resultado_inexistente = ResultadoCargaInventarioAdmin(
            estado=EstadoInventarioAdmin.INVENTARIO_REMOTO_INEXISTENTE,
            mensaje_usuario=MENSAJE_INVENTARIO_REMOTO_INEXISTENTE_ADMIN,
            detalle_tecnico=ocultar_secretos_en_texto(exc_no_existe.mensaje),
            espacio_trabajo=None,
            sha_base_remoto=None,
            permite_reintentar=True,
            permite_inicializar_demo_local=True,
            confirmado_en_github=False,
        )
        estado[CLAVE_RESULTADO_CARGA_ADMIN] = resultado_inexistente
        return resultado_inexistente

    except (ErrorArchivoExcelRemotoCorrupto, ErrorEsquemaInventarioRemoto) as exc_invalido:
        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = None
        resultado_inv = ResultadoCargaInventarioAdmin(
            estado=EstadoInventarioAdmin.DATOS_REMOTOS_INVALIDOS,
            mensaje_usuario=MENSAJE_DATOS_REMOTOS_INVALIDOS_ADMIN,
            detalle_tecnico=ocultar_secretos_en_texto(exc_invalido.mensaje),
            espacio_trabajo=None,
            sha_base_remoto=None,
            permite_reintentar=True,
            permite_inicializar_demo_local=False,
            confirmado_en_github=False,
        )
        estado[CLAVE_RESULTADO_CARGA_ADMIN] = resultado_inv
        return resultado_inv

    except ErrorLecturaGitHub as exc_red:
        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = None
        resultado_red = ResultadoCargaInventarioAdmin(
            estado=EstadoInventarioAdmin.ERROR_CONEXION,
            mensaje_usuario=MENSAJE_ERROR_CONEXION_ADMIN,
            detalle_tecnico=ocultar_secretos_en_texto(exc_red.mensaje),
            espacio_trabajo=None,
            sha_base_remoto=None,
            permite_reintentar=True,
            permite_inicializar_demo_local=False,
            confirmado_en_github=False,
        )
        estado[CLAVE_RESULTADO_CARGA_ADMIN] = resultado_red
        return resultado_red

    except Exception as exc_gen:
        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = None
        resultado_err = ResultadoCargaInventarioAdmin(
            estado=EstadoInventarioAdmin.ERROR_CONEXION,
            mensaje_usuario=MENSAJE_ERROR_CONEXION_ADMIN,
            detalle_tecnico=ocultar_secretos_en_texto(str(exc_gen)),
            espacio_trabajo=None,
            sha_base_remoto=None,
            permite_reintentar=True,
            permite_inicializar_demo_local=False,
            confirmado_en_github=False,
        )
        estado[CLAVE_RESULTADO_CARGA_ADMIN] = resultado_err
        return resultado_err


def descartar_cambios_locales_en_sesion(
    estado: MutableMapping[str, Any],
    *,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> EspacioTrabajoAdminInventario:
    """Restaura la copia de trabajo al inventario original cargado y elimina el borrador temporal."""
    sesion, espacio = _obtener_espacio_trabajo_autorizado(
        estado,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=True,
    )
    espacio_limpio = EspacioTrabajoAdminInventario(
        inventario_original=clonar_inventario_datos(espacio.inventario_original),
        inventario_trabajo=clonar_inventario_datos(espacio.inventario_original),
        usuario_propietario=sesion.usuario,
        id_sesion_propietaria=sesion.token_sesion,
        sha_base_remoto=espacio.sha_base_remoto,
        origen_remoto_confirmado=espacio.origen_remoto_confirmado,
        codigos_productos_creados=(),
        codigos_productos_editados=(),
        historial_operaciones_locales=(),
        creado_en_epoch=espacio.creado_en_epoch,
        actualizado_en_epoch=sesion.ultima_actividad_epoch,
        confirmado_en_github=False,
        es_copia_local_temporal=True,
    )
    estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = espacio_limpio
    estado[CLAVE_FORMULARIO_BORRADOR_ADMIN] = None
    descartar_borrador_admin(estado, reloj=reloj, ahora_epoch=ahora_epoch)
    return espacio_limpio


def limpiar_espacio_trabajo_admin_en_sesion(
    estado: MutableMapping[str, Any] | None,
) -> None:
    """Limpia del estado de sesión todas las estructuras de edición administrativa local."""
    if not isinstance(estado, MutableMapping):
        return
    estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = None
    estado[CLAVE_RESULTADO_CARGA_ADMIN] = None
    estado[CLAVE_MODO_VISTA_ADMIN] = ModoVistaAdmin.INICIAL.value
    estado[CLAVE_PRODUCTO_ADMIN_SELECCIONADO] = None
    estado[CLAVE_TERMINO_FILTRO_ADMIN] = ""
    estado[CLAVE_MENSAJE_OPERACION_ADMIN] = None
    estado[CLAVE_FORMULARIO_BORRADOR_ADMIN] = None


def consultar_productos_administrativos(
    estado: Mapping[str, Any],
    *,
    termino_filtro: str = "",
    espacio_trabajo: EspacioTrabajoAdminInventario | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
    registrar_actividad: bool = False,
) -> list[dict[str, Any]]:
    """Devuelve la lista estructurada de productos de la copia de trabajo para consulta administrativa (Sección 5.1).

    Por defecto `registrar_actividad=False` para que un re-renderizado pasivo de la tabla
    administrativa en Streamlit no renueve automáticamente la sesión.
    """
    _, espacio = _obtener_espacio_trabajo_autorizado(
        estado,
        espacio_explicito=espacio_trabajo,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=registrar_actividad,
    )
    productos = obtener_productos_estructurados(espacio.inventario_trabajo)
    creados_set = set(espacio.codigos_productos_creados)
    editados_set = set(espacio.codigos_productos_editados)
    filtro_norm = normalizar_texto_busqueda(termino_filtro)

    resultado: list[dict[str, Any]] = []
    for prod in productos:
        cod = prod["codigo_producto"]
        nombre = prod["nombre"]
        if filtro_norm:
            coincide_nombre = filtro_norm in normalizar_texto_busqueda(nombre)
            coincide_codigo = filtro_norm in normalizar_texto_busqueda(cod)
            if not (coincide_nombre or coincide_codigo):
                continue

        es_nuevo = cod in creados_set
        es_editado = cod in editados_set
        tiene_cambio_local = es_nuevo or es_editado
        item_enriquecido = dict(prod)
        item_enriquecido["es_nuevo_local"] = es_nuevo
        item_enriquecido["es_editado_local"] = es_editado
        item_enriquecido["tiene_cambios_locales"] = tiene_cambio_local
        item_enriquecido["confirmado_en_github"] = (
            not tiene_cambio_local and espacio.origen_remoto_confirmado
        )
        item_enriquecido["estado_registro_texto"] = (
            "Nuevo (cambio local sin guardar)"
            if es_nuevo
            else (
                "Editado (cambio local sin guardar)"
                if es_editado
                else (
                    "Confirmado en remoto"
                    if espacio.origen_remoto_confirmado
                    else "Base demostrativa local (sin guardar)"
                )
            )
        )
        resultado.append(item_enriquecido)
    return resultado


def consultar_producto_administrativo_por_codigo(
    estado: Mapping[str, Any],
    codigo_producto: Any,
    *,
    espacio_trabajo: EspacioTrabajoAdminInventario | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
    registrar_actividad: bool = False,
) -> dict[str, Any]:
    """Consulta el detalle administrativo completo de un producto por su código exacto (Sección 5.1)."""
    _, espacio = _obtener_espacio_trabajo_autorizado(
        estado,
        espacio_explicito=espacio_trabajo,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=registrar_actividad,
    )
    codigo_limpio = _validar_codigo_producto_texto(codigo_producto)
    for prod in consultar_productos_administrativos(
        estado,
        espacio_trabajo=espacio,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=False,
    ):
        if prod["codigo_producto"] == codigo_limpio:
            return prod

    raise ErrorValidacionAdministrativa(
        f"El producto con código '{codigo_limpio}' no existe en el inventario de trabajo.",
        codigo=CodigoErrorAdministrativo.PRODUCTO_NO_EXISTE,
    )


def obtener_catalogo_categorias_admin(
    estado: Mapping[str, Any],
    *,
    espacio_trabajo: EspacioTrabajoAdminInventario | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> list[dict[str, str]]:
    """Devuelve el catálogo predefinido de categorías disponible para los formularios (Sección 5.4)."""
    _, espacio = _obtener_espacio_trabajo_autorizado(
        estado,
        espacio_explicito=espacio_trabajo,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=False,
    )
    categorias: list[dict[str, str]] = []
    for _, fila in espacio.inventario_trabajo.categorias.iterrows():
        cat_id = str(fila["Categoria_ID"]).strip()
        nom_cat = str(fila["Nombre_Categoria"]).strip()
        categorias.append(
            {
                "categoria_id": cat_id,
                "nombre_categoria": nom_cat,
                "etiqueta": f"{cat_id} — {nom_cat}",
            }
        )
    return categorias


def obtener_catalogo_ubicaciones_admin(
    estado: Mapping[str, Any],
    *,
    espacio_trabajo: EspacioTrabajoAdminInventario | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> list[dict[str, str]]:
    """Devuelve el catálogo predefinido de ubicaciones físicas disponible para los formularios (Sección 5.4)."""
    _, espacio = _obtener_espacio_trabajo_autorizado(
        estado,
        espacio_explicito=espacio_trabajo,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=False,
    )
    ubicaciones: list[dict[str, str]] = []
    for _, fila in espacio.inventario_trabajo.ubicaciones.iterrows():
        u_id = str(fila["Ubicacion_ID"]).strip()
        etiqueta_fisica = formatear_ubicacion_fisica(fila)
        ubicaciones.append(
            {
                "ubicacion_id": u_id,
                "rack": str(fila["Rack"]).strip(),
                "columna": str(fila["Columna"]).strip(),
                "nivel": str(fila["Nivel"]).strip(),
                "posicion": str(fila["Posicion"]).strip(),
                "etiqueta": f"{u_id} ({etiqueta_fisica})",
                "etiqueta_fisica": etiqueta_fisica,
            }
        )
    return ubicaciones


def rechazar_modificacion_catalogo_predefinido(
    nombre_catalogo: str = "Categorías/Ubicaciones",
) -> None:
    """Rechaza cualquier intento de crear, editar o eliminar categorías o ubicaciones en v0 (RF-021, Sección 5.4)."""
    raise ErrorValidacionAdministrativa(
        f"{MENSAJE_CATALOGO_PREDEFINIDO_NO_EDITABLE} (Catálogo solicitado: {nombre_catalogo}).",
        codigo=CodigoErrorAdministrativo.OPERACION_CATALOGO_NO_PERMITIDA,
    )


def crear_producto_local(
    estado: MutableMapping[str, Any],
    *,
    codigo_producto: Any,
    nombre: Any,
    categoria_id: Any,
    descripcion: Any = "",
    ubicaciones_ids: Sequence[Any] | None = None,
    ubicacion_principal_id: Any = None,
    asignaciones: Sequence[Mapping[str, Any] | AsignacionUbicacionEntrada] | None = None,
    espacio_trabajo: EspacioTrabajoAdminInventario | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
    _sincronizar_borrador: bool = True,
    _publicar_en_estado: bool = True,
    _registrar_actividad: bool = True,
) -> ResultadoOperacionProductoAdmin:
    """Crea un producto nuevo en la copia temporal de trabajo validando las cuatro hojas (Secciones 5.2 y 6).

    Garantías de integridad y atomicidad:
    - Exige autorización administrativa vigente en contexto de escritorio.
    - Conserva ceros iniciales en `Codigo_Producto`.
    - Rechaza códigos duplicados, nombres vacíos, categorías inexistentes, ubicaciones inexistentes,
      productos sin ubicación, sin ubicación principal, con dos ubicaciones principales o con
      asignaciones duplicadas.
    - Aplica la modificación sobre copias de las cuatro hojas, ejecuta `construir_inventario_datos`
      y valida la sincronización del borrador temporal sobre un espacio candidato aislado antes de
      mutar el espacio de trabajo activo. Si cualquier validación o sincronización falla, el
      inventario de trabajo, el historial de operaciones y el borrador previo permanecen intactos
      y la sesión no se renueva indebidamente.
    """
    sesion, espacio = _obtener_espacio_trabajo_autorizado(
        estado,
        espacio_explicito=espacio_trabajo,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=False,
    )

    hojas_actuales = espacio.inventario_trabajo.obtener_hojas()
    df_productos_cand = hojas_actuales[HOJA_PRODUCTOS].copy(deep=True)
    df_categorias_cand = hojas_actuales[HOJA_CATEGORIAS].copy(deep=True)
    df_ubicaciones_cand = hojas_actuales[HOJA_UBICACIONES].copy(deep=True)
    df_asignaciones_cand = hojas_actuales[HOJA_ASIGNACIONES].copy(deep=True)

    codigo_limpio = _validar_codigo_producto_texto(codigo_producto)
    codigos_existentes = set(
        df_productos_cand["Codigo_Producto"].astype(str).str.strip()
    )
    if codigo_limpio in codigos_existentes:
        raise ErrorValidacionAdministrativa(
            f"El código de producto '{codigo_limpio}' ya existe en el inventario. No se permiten códigos duplicados.",
            codigo=CodigoErrorAdministrativo.CODIGO_PRODUCTO_DUPLICADO,
        )

    nombre_limpio = _validar_nombre_producto_texto(nombre)
    descripcion_limpia = _validar_descripcion_producto_texto(descripcion)
    categoria_limpia = _validar_categoria_existente(categoria_id, df_categorias_cand)
    asignaciones_limpias = _normalizar_y_validar_asignaciones_entrada(
        df_ubicaciones=df_ubicaciones_cand,
        ubicaciones_ids=ubicaciones_ids,
        ubicacion_principal_id=ubicacion_principal_id,
        asignaciones=asignaciones,
    )

    nueva_fila_producto = pd.DataFrame(
        [
            {
                "Codigo_Producto": codigo_limpio,
                "Nombre": nombre_limpio,
                "Categoria_ID": categoria_limpia,
                "Descripcion": descripcion_limpia,
            }
        ]
    )
    nuevas_filas_asignaciones = pd.DataFrame(
        [
            {
                "Codigo_Producto": codigo_limpio,
                "Ubicacion_ID": asig["Ubicacion_ID"],
                "Principal": asig["Principal"],
            }
            for asig in asignaciones_limpias
        ]
    )

    df_productos_nuevo = pd.concat(
        [df_productos_cand, nueva_fila_producto], ignore_index=True
    )
    df_asignaciones_nuevo = pd.concat(
        [df_asignaciones_cand, nuevas_filas_asignaciones], ignore_index=True
    )

    hojas_candidatas = {
        HOJA_PRODUCTOS: df_productos_nuevo,
        HOJA_CATEGORIAS: df_categorias_cand,
        HOJA_UBICACIONES: df_ubicaciones_cand,
        HOJA_ASIGNACIONES: df_asignaciones_nuevo,
    }

    try:
        inventario_validado = construir_inventario_datos(hojas_candidatas)
    except ErrorInventario as exc_inv:
        raise _convertir_error_motor_inventario(exc_inv) from exc_inv

    codigos_creados_nuevos = (
        (*espacio.codigos_productos_creados, codigo_limpio)
        if codigo_limpio not in espacio.codigos_productos_creados
        else espacio.codigos_productos_creados
    )
    operacion = OperacionLocalInventario(
        tipo_operacion="CREAR_PRODUCTO",
        codigo_producto=codigo_limpio,
        nombre=nombre_limpio,
        categoria_id=categoria_limpia,
        descripcion=descripcion_limpia,
        asignaciones=tuple(
            {"ubicacion_id": a["Ubicacion_ID"], "principal": a["Principal"]}
            for a in asignaciones_limpias
        ),
        realizada_en_epoch=sesion.ultima_actividad_epoch,
    )
    historial_nuevo = (*espacio.historial_operaciones_locales, operacion)

    # Preparar candidato aislado y sincronizar borrador ANTES de mutar el espacio de trabajo activo
    espacio_candidato = EspacioTrabajoAdminInventario(
        inventario_original=espacio.inventario_original,
        inventario_trabajo=inventario_validado,
        sha_base_remoto=espacio.sha_base_remoto,
        origen_remoto_confirmado=espacio.origen_remoto_confirmado,
        usuario_propietario=espacio.usuario_propietario,
        id_sesion_propietaria=espacio.id_sesion_propietaria,
        creado_en_epoch=espacio.creado_en_epoch,
        actualizado_en_epoch=sesion.ultima_actividad_epoch,
        codigos_productos_creados=codigos_creados_nuevos,
        codigos_productos_editados=espacio.codigos_productos_editados,
        historial_operaciones_locales=historial_nuevo,
    )

    if _sincronizar_borrador and isinstance(estado, MutableMapping):
        _sincronizar_borrador_automatico_en_sesion(
            estado,
            espacio_candidato,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
            ahora_epoch=ahora_epoch,
        )
        sesion_post = estado.get(autenticacion.CLAVE_SESION_ADMIN)
        if isinstance(sesion_post, EstadoSesionAdmin):
            sesion = sesion_post
    elif _registrar_actividad and isinstance(estado, MutableMapping):
        sesion = registrar_actividad_administrativa(
            estado,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
            ahora_epoch=ahora_epoch,
        )

    # Confirmar cambio de forma atómica únicamente tras validar inventario y borrador
    espacio.inventario_trabajo = inventario_validado
    espacio.codigos_productos_creados = codigos_creados_nuevos
    espacio.historial_operaciones_locales = historial_nuevo
    espacio.actualizado_en_epoch = sesion.ultima_actividad_epoch

    if _publicar_en_estado and isinstance(estado, MutableMapping):
        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = espacio

    producto_detalle = consultar_producto_administrativo_por_codigo(
        estado,
        codigo_limpio,
        espacio_trabajo=espacio,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=False,
    )
    return ResultadoOperacionProductoAdmin(
        exito=True,
        estado=EstadoInventarioAdmin.MODIFICACION_LOCAL_VALIDA,
        mensaje_usuario=MENSAJE_CREACION_LOCAL_EXITOSA,
        codigo_producto=codigo_limpio,
        producto=producto_detalle,
        espacio_trabajo=espacio,
        sha_base_remoto=espacio.sha_base_remoto,
        tiene_cambios_pendientes=espacio.tiene_cambios_locales_pendientes,
        confirmado_en_github=False,
        es_cambio_local_temporal=True,
    )


def editar_producto_local(
    estado: MutableMapping[str, Any],
    *,
    codigo_producto: Any,
    nuevo_codigo_producto: Any = None,
    nombre: Any = None,
    categoria_id: Any = None,
    descripcion: Any = None,
    ubicaciones_ids: Sequence[Any] | None = None,
    ubicacion_principal_id: Any = None,
    asignaciones: Sequence[Mapping[str, Any] | AsignacionUbicacionEntrada] | None = None,
    espacio_trabajo: EspacioTrabajoAdminInventario | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
    _sincronizar_borrador: bool = True,
    _publicar_en_estado: bool = True,
    _registrar_actividad: bool = True,
) -> ResultadoOperacionProductoAdmin:
    """Edita un producto existente en la copia temporal conservando inmutable su código único (Sección 5.3).

    Garantías de integridad y atomicidad:
    - Si `nuevo_codigo_producto` se especifica y es distinto de `codigo_producto`, rechaza la
      operación inmediatamente con `CODIGO_PRODUCTO_INMUTABLE` (`RF-015`, `CA-044`).
    - Permite actualizar `Nombre`, `Categoria_ID`, `Descripcion` y las asignaciones de ubicación,
      manteniendo siempre al menos una ubicación válida y exactamente una ubicación principal.
    - Valida integralmente las cuatro hojas y la sincronización del borrador antes de sustituir
      `espacio.inventario_trabajo`. Si cualquier validación o sincronización falla, no se realiza
      ninguna modificación parcial en el inventario de trabajo, el historial ni el borrador previo,
      ni se renueva indebidamente la sesión.
    """
    sesion, espacio = _obtener_espacio_trabajo_autorizado(
        estado,
        espacio_explicito=espacio_trabajo,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=False,
    )

    codigo_limpio = _validar_codigo_producto_texto(codigo_producto)
    if nuevo_codigo_producto is not None:
        if not isinstance(nuevo_codigo_producto, str) or (
            nuevo_codigo_producto.strip() != codigo_limpio
        ):
            raise ErrorValidacionAdministrativa(
                f"El código único del producto ('{codigo_limpio}') es inmutable y no puede modificarse una vez creado.",
                codigo=CodigoErrorAdministrativo.CODIGO_PRODUCTO_INMUTABLE,
            )

    hojas_actuales = espacio.inventario_trabajo.obtener_hojas()
    df_productos_cand = hojas_actuales[HOJA_PRODUCTOS].copy(deep=True)
    df_categorias_cand = hojas_actuales[HOJA_CATEGORIAS].copy(deep=True)
    df_ubicaciones_cand = hojas_actuales[HOJA_UBICACIONES].copy(deep=True)
    df_asignaciones_cand = hojas_actuales[HOJA_ASIGNACIONES].copy(deep=True)

    mascara_producto = (
        df_productos_cand["Codigo_Producto"].astype(str).str.strip() == codigo_limpio
    )
    if not mascara_producto.any():
        raise ErrorValidacionAdministrativa(
            f"El producto con código '{codigo_limpio}' no existe en el inventario.",
            codigo=CodigoErrorAdministrativo.PRODUCTO_NO_EXISTE,
        )

    fila_actual = df_productos_cand.loc[mascara_producto].iloc[0]
    nombre_efectivo = (
        _validar_nombre_producto_texto(nombre)
        if nombre is not None
        else _validar_nombre_producto_texto(str(fila_actual["Nombre"]))
    )
    categoria_efectiva = (
        _validar_categoria_existente(categoria_id, df_categorias_cand)
        if categoria_id is not None
        else _validar_categoria_existente(
            str(fila_actual["Categoria_ID"]), df_categorias_cand
        )
    )
    descripcion_efectiva = (
        _validar_descripcion_producto_texto(descripcion)
        if descripcion is not None
        else _validar_descripcion_producto_texto(str(fila_actual["Descripcion"]))
    )

    # Resolver asignaciones de ubicación (nuevas o conservando las actuales con cambio de principal)
    mascara_asig_prod = (
        df_asignaciones_cand["Codigo_Producto"].astype(str).str.strip() == codigo_limpio
    )
    df_asig_actuales_prod = df_asignaciones_cand.loc[mascara_asig_prod]

    if (
        asignaciones is None
        and ubicaciones_ids is None
        and ubicacion_principal_id is None
    ):
        asignaciones_actuales_lista = [
            {
                "Ubicacion_ID": str(f["Ubicacion_ID"]).strip(),
                "Principal": str(f["Principal"]).strip(),
            }
            for _, f in df_asig_actuales_prod.iterrows()
        ]
        asignaciones_limpias = _normalizar_y_validar_asignaciones_entrada(
            df_ubicaciones=df_ubicaciones_cand,
            asignaciones=asignaciones_actuales_lista,
        )
    elif (
        asignaciones is None
        and ubicaciones_ids is None
        and ubicacion_principal_id is not None
    ):
        ubicaciones_actuales_ids = [
            str(f["Ubicacion_ID"]).strip() for _, f in df_asig_actuales_prod.iterrows()
        ]
        asignaciones_limpias = _normalizar_y_validar_asignaciones_entrada(
            df_ubicaciones=df_ubicaciones_cand,
            ubicaciones_ids=ubicaciones_actuales_ids,
            ubicacion_principal_id=ubicacion_principal_id,
        )
    else:
        asignaciones_limpias = _normalizar_y_validar_asignaciones_entrada(
            df_ubicaciones=df_ubicaciones_cand,
            ubicaciones_ids=ubicaciones_ids,
            ubicacion_principal_id=ubicacion_principal_id,
            asignaciones=asignaciones,
        )

    # Actualizar fila en copia de Productos
    df_productos_cand.loc[mascara_producto, "Nombre"] = nombre_efectivo
    df_productos_cand.loc[mascara_producto, "Categoria_ID"] = categoria_efectiva
    df_productos_cand.loc[mascara_producto, "Descripcion"] = descripcion_efectiva

    # Reemplazar las asignaciones de este producto conservando el orden del resto de productos
    df_asignaciones_otros = df_asignaciones_cand.loc[~mascara_asig_prod].copy(deep=True)
    df_asignaciones_prod_nuevas = pd.DataFrame(
        [
            {
                "Codigo_Producto": codigo_limpio,
                "Ubicacion_ID": a["Ubicacion_ID"],
                "Principal": a["Principal"],
            }
            for a in asignaciones_limpias
        ]
    )
    df_asignaciones_nuevo = pd.concat(
        [df_asignaciones_otros, df_asignaciones_prod_nuevas], ignore_index=True
    )

    hojas_candidatas = {
        HOJA_PRODUCTOS: df_productos_cand,
        HOJA_CATEGORIAS: df_categorias_cand,
        HOJA_UBICACIONES: df_ubicaciones_cand,
        HOJA_ASIGNACIONES: df_asignaciones_nuevo,
    }

    try:
        inventario_validado = construir_inventario_datos(hojas_candidatas)
    except ErrorInventario as exc_inv:
        raise _convertir_error_motor_inventario(exc_inv) from exc_inv

    codigos_editados_nuevos = (
        (*espacio.codigos_productos_editados, codigo_limpio)
        if (
            codigo_limpio not in espacio.codigos_productos_creados
            and codigo_limpio not in espacio.codigos_productos_editados
        )
        else espacio.codigos_productos_editados
    )
    operacion = OperacionLocalInventario(
        tipo_operacion="EDITAR_PRODUCTO",
        codigo_producto=codigo_limpio,
        nombre=nombre_efectivo,
        categoria_id=categoria_efectiva,
        descripcion=descripcion_efectiva,
        asignaciones=tuple(
            {"ubicacion_id": a["Ubicacion_ID"], "principal": a["Principal"]}
            for a in asignaciones_limpias
        ),
        realizada_en_epoch=sesion.ultima_actividad_epoch,
    )
    historial_nuevo = (*espacio.historial_operaciones_locales, operacion)

    # Preparar candidato aislado y sincronizar borrador ANTES de mutar el espacio de trabajo activo
    espacio_candidato = EspacioTrabajoAdminInventario(
        inventario_original=espacio.inventario_original,
        inventario_trabajo=inventario_validado,
        sha_base_remoto=espacio.sha_base_remoto,
        origen_remoto_confirmado=espacio.origen_remoto_confirmado,
        usuario_propietario=espacio.usuario_propietario,
        id_sesion_propietaria=espacio.id_sesion_propietaria,
        creado_en_epoch=espacio.creado_en_epoch,
        actualizado_en_epoch=sesion.ultima_actividad_epoch,
        codigos_productos_creados=espacio.codigos_productos_creados,
        codigos_productos_editados=codigos_editados_nuevos,
        historial_operaciones_locales=historial_nuevo,
    )

    if _sincronizar_borrador and isinstance(estado, MutableMapping):
        _sincronizar_borrador_automatico_en_sesion(
            estado,
            espacio_candidato,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
            ahora_epoch=ahora_epoch,
        )
        sesion_post = estado.get(autenticacion.CLAVE_SESION_ADMIN)
        if isinstance(sesion_post, EstadoSesionAdmin):
            sesion = sesion_post
    elif _registrar_actividad and isinstance(estado, MutableMapping):
        sesion = registrar_actividad_administrativa(
            estado,
            contexto_dispositivo=contexto_dispositivo,
            reloj=reloj,
            ahora_epoch=ahora_epoch,
        )

    # Confirmar cambio de forma atómica únicamente tras validar inventario y borrador
    espacio.inventario_trabajo = inventario_validado
    espacio.codigos_productos_editados = codigos_editados_nuevos
    espacio.historial_operaciones_locales = historial_nuevo
    espacio.actualizado_en_epoch = sesion.ultima_actividad_epoch

    if _publicar_en_estado and isinstance(estado, MutableMapping):
        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = espacio

    producto_detalle = consultar_producto_administrativo_por_codigo(
        estado,
        codigo_limpio,
        espacio_trabajo=espacio,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=False,
    )
    return ResultadoOperacionProductoAdmin(
        exito=True,
        estado=EstadoInventarioAdmin.MODIFICACION_LOCAL_VALIDA,
        mensaje_usuario=MENSAJE_EDICION_LOCAL_EXITOSA,
        codigo_producto=codigo_limpio,
        producto=producto_detalle,
        espacio_trabajo=espacio,
        sha_base_remoto=espacio.sha_base_remoto,
        tiene_cambios_pendientes=espacio.tiene_cambios_locales_pendientes,
        confirmado_en_github=False,
        es_cambio_local_temporal=True,
    )


def cambiar_ubicacion_principal_local(
    estado: MutableMapping[str, Any],
    *,
    codigo_producto: Any,
    nueva_ubicacion_principal_id: Any,
    incluir_si_no_estaba_asignada: bool = False,
    espacio_trabajo: EspacioTrabajoAdminInventario | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> ResultadoOperacionProductoAdmin:
    """Cambia la ubicación principal de un producto garantizando que quede exactamente una principal (CA-017)."""
    _, espacio = _obtener_espacio_trabajo_autorizado(
        estado,
        espacio_explicito=espacio_trabajo,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=False,
    )
    codigo_limpio = _validar_codigo_producto_texto(codigo_producto)
    if (
        not isinstance(nueva_ubicacion_principal_id, str)
        or not nueva_ubicacion_principal_id.strip()
    ):
        raise ErrorValidacionAdministrativa(
            "Debe indicarse un identificador de ubicación principal válido.",
            codigo=CodigoErrorAdministrativo.SIN_UBICACION_PRINCIPAL,
        )
    nueva_prin_limpia = nueva_ubicacion_principal_id.strip()

    df_asig = espacio.inventario_trabajo.asignaciones
    mascara_prod = df_asig["Codigo_Producto"].astype(str).str.strip() == codigo_limpio
    if not mascara_prod.any():
        raise ErrorValidacionAdministrativa(
            f"El producto '{codigo_limpio}' no existe en el inventario.",
            codigo=CodigoErrorAdministrativo.PRODUCTO_NO_EXISTE,
        )

    ubicaciones_actuales = [
        str(u).strip() for u in df_asig.loc[mascara_prod, "Ubicacion_ID"].tolist()
    ]
    if incluir_si_no_estaba_asignada and nueva_prin_limpia not in ubicaciones_actuales:
        ubicaciones_actuales.append(nueva_prin_limpia)

    res = editar_producto_local(
        estado,
        codigo_producto=codigo_limpio,
        ubicaciones_ids=ubicaciones_actuales,
        ubicacion_principal_id=nueva_prin_limpia,
        espacio_trabajo=espacio,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
    )
    return ResultadoOperacionProductoAdmin(
        exito=res.exito,
        estado=res.estado,
        mensaje_usuario=MENSAJE_CAMBIO_PRINCIPAL_LOCAL_EXITOSO,
        codigo_producto=res.codigo_producto,
        producto=res.producto,
        espacio_trabajo=res.espacio_trabajo,
        sha_base_remoto=res.sha_base_remoto,
        tiene_cambios_pendientes=res.tiene_cambios_pendientes,
        confirmado_en_github=False,
        es_cambio_local_temporal=True,
    )


def eliminar_asignacion_ubicacion_local(
    estado: MutableMapping[str, Any],
    *,
    codigo_producto: Any,
    ubicacion_id: Any,
    espacio_trabajo: EspacioTrabajoAdminInventario | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> ResultadoOperacionProductoAdmin:
    """Retira una asignación secundaria de ubicación respetando las reglas de integridad (RF-018, CA-045).

    Reglas:
    - Rechaza retirar la única ubicación asignada a un producto (`ELIMINACION_UNICA_UBICACION`).
    - Rechaza retirar la ubicación que actualmente es principal sin antes haber designado otra
      ubicación como principal (`SIN_UBICACION_PRINCIPAL`).
    """
    _, espacio = _obtener_espacio_trabajo_autorizado(
        estado,
        espacio_explicito=espacio_trabajo,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=False,
    )
    codigo_limpio = _validar_codigo_producto_texto(codigo_producto)
    if not isinstance(ubicacion_id, str) or not ubicacion_id.strip():
        raise ErrorValidacionAdministrativa(
            "Debe indicarse el identificador de la ubicación que se desea retirar.",
            codigo=CodigoErrorAdministrativo.UBICACION_INEXISTENTE,
        )
    ubic_retirar = ubicacion_id.strip()

    df_asig = espacio.inventario_trabajo.asignaciones
    mascara_prod = df_asig["Codigo_Producto"].astype(str).str.strip() == codigo_limpio
    if not mascara_prod.any():
        raise ErrorValidacionAdministrativa(
            f"El producto '{codigo_limpio}' no existe en el inventario.",
            codigo=CodigoErrorAdministrativo.PRODUCTO_NO_EXISTE,
        )

    filas_prod = df_asig.loc[mascara_prod]
    asignaciones_actuales = [
        {
            "Ubicacion_ID": str(f["Ubicacion_ID"]).strip(),
            "Principal": str(f["Principal"]).strip(),
        }
        for _, f in filas_prod.iterrows()
    ]
    ids_actuales = [a["Ubicacion_ID"] for a in asignaciones_actuales]
    if ubic_retirar not in ids_actuales:
        raise ErrorValidacionAdministrativa(
            f"La ubicación '{ubic_retirar}' no está asignada al producto '{codigo_limpio}'.",
            codigo=CodigoErrorAdministrativo.UBICACION_INEXISTENTE,
        )

    if len(asignaciones_actuales) <= 1:
        raise ErrorValidacionAdministrativa(
            f"No es posible retirar la ubicación '{ubic_retirar}' porque es la única ubicación "
            f"asignada al producto '{codigo_limpio}'. Todo producto debe conservar al menos una ubicación válida.",
            codigo=CodigoErrorAdministrativo.ELIMINACION_UNICA_UBICACION,
        )

    asignaciones_restantes = [
        a for a in asignaciones_actuales if a["Ubicacion_ID"] != ubic_retirar
    ]
    principales_restantes = [
        a for a in asignaciones_restantes if a["Principal"] == "Sí"
    ]
    if len(principales_restantes) == 0:
        raise ErrorValidacionAdministrativa(
            f"No se puede retirar directamente la ubicación principal '{ubic_retirar}' sin antes "
            f"asignar otra ubicación como principal para el producto '{codigo_limpio}'.",
            codigo=CodigoErrorAdministrativo.SIN_UBICACION_PRINCIPAL,
        )

    res = editar_producto_local(
        estado,
        codigo_producto=codigo_limpio,
        asignaciones=asignaciones_restantes,
        espacio_trabajo=espacio,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
    )
    return ResultadoOperacionProductoAdmin(
        exito=res.exito,
        estado=res.estado,
        mensaje_usuario=MENSAJE_ELIMINACION_SECUNDARIA_LOCAL_EXITOSA,
        codigo_producto=res.codigo_producto,
        producto=res.producto,
        espacio_trabajo=res.espacio_trabajo,
        sha_base_remoto=res.sha_base_remoto,
        tiene_cambios_pendientes=res.tiene_cambios_pendientes,
        confirmado_en_github=False,
        es_cambio_local_temporal=True,
    )


def guardar_borrador_formulario_admin(
    estado: MutableMapping[str, Any],
    datos_formulario: Mapping[str, Any],
    *,
    modo_formulario: str = "CREAR_PRODUCTO",
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> BorradorTemporalAdmin:
    """Guarda un borrador de formulario administrativo junto con las ediciones locales de la sesión (Sección 8)."""
    if not isinstance(datos_formulario, Mapping) or len(datos_formulario) == 0:
        raise ErrorSeguridadBorradorAdmin(
            "Los datos del formulario para el borrador no pueden estar vacíos."
        )

    sesion = _exigir_sesion_admin_autorizada(
        estado,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=True,
    )
    espacio = estado.get(CLAVE_ESPACIO_TRABAJO_ADMIN)
    if (
        isinstance(espacio, EspacioTrabajoAdminInventario)
        and espacio.usuario_propietario == sesion.usuario
        and espacio.id_sesion_propietaria == sesion.token_sesion
    ):
        carga_borrador = _construir_resumen_borrador_espacio(
            espacio,
            formulario_activo={
                "modo_formulario": str(modo_formulario),
                "campos": dict(datos_formulario),
            },
        )
    else:
        carga_borrador = {
            "tipo_borrador_p09": "formulario_producto",
            "formulario_activo": {
                "modo_formulario": str(modo_formulario),
                "campos": dict(datos_formulario),
            },
        }

    borrador = guardar_borrador_admin(
        estado,
        carga_borrador,
        tipo_operacion=f"formulario_{modo_formulario.lower()}",
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
    )
    estado[CLAVE_FORMULARIO_BORRADOR_ADMIN] = copy.deepcopy(
        carga_borrador["formulario_activo"]
    )
    return borrador


def restaurar_borrador_en_espacio_trabajo_admin(
    estado: MutableMapping[str, Any],
    *,
    inventario_base: InventarioDatos | None = None,
    sha_base_remoto: str | None = None,
    eliminar_tras_restaurar: bool = False,
    config_github: ConfiguracionRepositorioGitHub = CONFIGURACION_POR_DEFECTO,
    descargador_remoto: DescargadorRemotoAdmin | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> BorradorTemporalAdmin | None:
    """Restaura un borrador administrativo tras reautenticación y reaplica sus cambios validados (Sección 8).

    Garantías de atomicidad y seguridad:
    1. Valida pasivamente la sesión (`registrar_actividad=False`) y consulta el borrador sin
       destruir ni reemplazar el estado anterior ni consumir prematuramente el borrador fuente.
    2. Si el espacio de trabajo fue eliminado al expirar la sesión y no se suministró
       `inventario_base`, descarga el inventario remoto desde GitHub y verifica que su SHA
       coincida exactamente con el `sha_base_remoto` del borrador. Nunca sustituye
       silenciosamente un inventario remoto previo por un inventario demostrativo, y distingue
       errores de conexión, inventario inexistente y conflictos de SHA.
    3. Reproduce todas las operaciones sobre un espacio de trabajo aislado de preparación sin
       renovar indebidamente la sesión ni alterar `estado` o el borrador del servidor.
    4. Solo tras completar satisfactoriamente toda la validación consume/marca el borrador
       mediante `restaurar_borrador_admin` (que aplica la autoridad temporal del servidor) y
       publica de forma controlada el espacio de trabajo y el formulario en `estado`.
    5. Si falla cualquier validación, descarga u operación, el espacio de trabajo anterior y el
       borrador original recuperable se conservan íntegramente.
    """
    sesion = _exigir_sesion_admin_autorizada(
        estado,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=False,
    )

    # 1. Inspección no destructiva del borrador (no elimina ni muta retenido_por_expiracion aún)
    borrador_previo = obtener_borrador_admin(
        estado,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
    )
    if borrador_previo is None:
        return None

    datos = borrador_previo.datos
    if not isinstance(datos, Mapping):
        raise ErrorValidacionAdministrativa(
            "El contenido del borrador restaurado no tiene una estructura válida.",
            codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
        )

    # Validar estructura del formulario en edición antes de modificar el estado real
    if "formulario_activo" in datos:
        if not isinstance(datos["formulario_activo"], Mapping):
            raise ErrorValidacionAdministrativa(
                "El formulario activo contenido en el borrador tiene una estructura inválida.",
                codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
            )
        formulario_preparado: dict[str, Any] = copy.deepcopy(
            dict(datos["formulario_activo"])
        )
    else:
        formulario_preparado = copy.deepcopy(dict(datos))

    # Verificar titularidad del espacio de trabajo existente en sesión, si lo hay
    espacio_existente = estado.get(CLAVE_ESPACIO_TRABAJO_ADMIN)
    if isinstance(espacio_existente, EspacioTrabajoAdminInventario):
        if espacio_existente.usuario_propietario != sesion.usuario or (
            inventario_base is None
            and espacio_existente.id_sesion_propietaria != sesion.token_sesion
        ):
            raise ErrorAutorizacionAdmin(
                "El espacio de trabajo administrativo activo pertenece a otra sesión y no puede combinarse con el borrador.",
                codigo=CodigoResultadoAutenticacion.SESION_EXPIRADA,
            )

    # Validar coherencia de versión (SHA base remoto) y de origen para no mezclar inventarios distintos
    sha_explicito: str | None = None
    if sha_base_remoto is not None:
        if not isinstance(sha_base_remoto, str):
            raise ErrorValidacionAdministrativa(
                "El SHA base remoto proporcionado para la restauración no es válido.",
                codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
            )
        sha_explicito = sha_base_remoto.strip() or None

    sha_borrador: str | None = None
    if "sha_base_remoto" in datos and datos.get("sha_base_remoto") is not None:
        if not isinstance(datos.get("sha_base_remoto"), str):
            raise ErrorValidacionAdministrativa(
                "El SHA base registrado en el borrador tiene un formato inválido.",
                codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
            )
        sha_borrador = str(datos.get("sha_base_remoto", "")).strip() or None

    origen_remoto_borrador: bool | None = (
        bool(datos["origen_remoto_confirmado"])
        if "origen_remoto_confirmado" in datos
        else None
    )
    if origen_remoto_borrador is False and (
        sha_borrador is not None or sha_explicito is not None
    ):
        raise ErrorValidacionAdministrativa(
            "No se permite combinar un borrador de copia demostrativa local con un SHA remoto.",
            codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
        )

    sha_espacio_existente: str | None = (
        espacio_existente.sha_base_remoto.strip()
        if isinstance(espacio_existente, EspacioTrabajoAdminInventario)
        and isinstance(espacio_existente.sha_base_remoto, str)
        and espacio_existente.sha_base_remoto.strip()
        else None
    )

    if (
        inventario_base is None
        and isinstance(espacio_existente, EspacioTrabajoAdminInventario)
        and origen_remoto_borrador is not None
        and espacio_existente.origen_remoto_confirmado != origen_remoto_borrador
    ):
        raise ErrorValidacionAdministrativa(
            "No se permite restaurar un borrador de origen remoto sobre una copia demostrativa local ni viceversa.",
            codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
        )

    if (
        sha_explicito is not None
        and sha_borrador is not None
        and sha_explicito != sha_borrador
    ):
        raise ErrorValidacionAdministrativa(
            f"Conflicto de versión al restaurar el borrador: el SHA del borrador ('{sha_borrador}') "
            f"no coincide con el SHA base remoto de referencia ('{sha_explicito}').",
            codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
        )

    if (
        inventario_base is None
        and sha_espacio_existente is not None
        and sha_borrador is not None
        and sha_espacio_existente != sha_borrador
    ):
        raise ErrorValidacionAdministrativa(
            f"Conflicto de versión al restaurar el borrador: el SHA del borrador ('{sha_borrador}') "
            f"no coincide con el SHA del espacio de trabajo activo ('{sha_espacio_existente}').",
            codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
        )

    if (
        inventario_base is None
        and sha_espacio_existente is not None
        and sha_explicito is not None
        and sha_espacio_existente != sha_explicito
    ):
        raise ErrorValidacionAdministrativa(
            f"Conflicto de versión al restaurar el borrador: el SHA solicitado ('{sha_explicito}') "
            f"no coincide con el SHA del espacio de trabajo activo ('{sha_espacio_existente}').",
            codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
        )

    sha_efectivo = sha_explicito or sha_borrador or sha_espacio_existente
    origen_remoto = (
        origen_remoto_borrador
        if origen_remoto_borrador is not None
        else (
            espacio_existente.origen_remoto_confirmado
            if isinstance(espacio_existente, EspacioTrabajoAdminInventario)
            else True
        )
    )

    # 2. Preparar y validar operaciones en un espacio de trabajo completamente aislado
    tiene_clave_operaciones = "operaciones_locales" in datos
    operaciones_guardadas = datos.get("operaciones_locales")
    if tiene_clave_operaciones and not isinstance(operaciones_guardadas, list):
        raise ErrorValidacionAdministrativa(
            "El listado de operaciones locales en el borrador tiene una estructura inválida.",
            codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
        )

    base_efectiva: InventarioDatos | None = inventario_base
    if base_efectiva is None and isinstance(
        espacio_existente, EspacioTrabajoAdminInventario
    ):
        base_efectiva = espacio_existente.inventario_original

    espacio_preparacion: EspacioTrabajoAdminInventario | None = None
    if isinstance(operaciones_guardadas, list):
        # Si no hay espacio activo en sesión (p. ej. tras expiración y reautenticación en UI),
        # obtener de forma segura el inventario base verificando origen y SHA contra GitHub.
        if base_efectiva is None:
            lector = (
                descargador_remoto or github_inventario.descargar_inventario_remoto
            )
            if origen_remoto:
                if sha_borrador is None and sha_explicito is None:
                    raise ErrorValidacionAdministrativa(
                        "El borrador de origen remoto carece del SHA original requerido para verificar la versión del inventario base.",
                        codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
                    )
                try:
                    lectura_remota = lector(config=config_github)
                except ErrorArchivoRemotoInexistente as exc_no_existe:
                    # Nunca sustituir silenciosamente un inventario remoto previo por uno demostrativo
                    raise ErrorAdministracionInventario(
                        "No es posible restaurar el borrador porque el inventario remoto original ya no existe en GitHub. "
                        "No se sustituye por un inventario demostrativo.",
                        codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
                        estado=EstadoInventarioAdmin.INVENTARIO_REMOTO_INEXISTENTE,
                    ) from exc_no_existe
                except (
                    ErrorArchivoExcelRemotoCorrupto,
                    ErrorEsquemaInventarioRemoto,
                ) as exc_invalido:
                    raise ErrorAdministracionInventario(
                        f"{MENSAJE_DATOS_REMOTOS_INVALIDOS_ADMIN} Detalle: "
                        f"{ocultar_secretos_en_texto(exc_invalido.mensaje)}",
                        codigo=CodigoErrorAdministrativo.INTEGRIDAD_INVENTARIO_INVALIDA,
                        estado=EstadoInventarioAdmin.DATOS_REMOTOS_INVALIDOS,
                    ) from exc_invalido
                except ErrorLecturaGitHub as exc_red:
                    raise ErrorAdministracionInventario(
                        f"{MENSAJE_ERROR_CONEXION_ADMIN} Detalle: "
                        f"{ocultar_secretos_en_texto(exc_red.mensaje)}",
                        codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
                        estado=EstadoInventarioAdmin.ERROR_CONEXION,
                    ) from exc_red
                except Exception as exc_gen:
                    raise ErrorAdministracionInventario(
                        f"{MENSAJE_ERROR_CONEXION_ADMIN} Detalle: "
                        f"{ocultar_secretos_en_texto(str(exc_gen))}",
                        codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
                        estado=EstadoInventarioAdmin.ERROR_CONEXION,
                    ) from exc_gen

                sha_remoto_actual = (lectura_remota.sha_github or "").strip() or None
                if sha_borrador is not None and sha_remoto_actual != sha_borrador:
                    raise ErrorValidacionAdministrativa(
                        f"Conflicto de versión (SHA) al restaurar el borrador: el borrador se creó sobre "
                        f"el SHA '{sha_borrador}', pero el inventario vigente en GitHub tiene el SHA '{sha_remoto_actual}'.",
                        codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
                    )
                if sha_explicito is not None and sha_remoto_actual != sha_explicito:
                    raise ErrorValidacionAdministrativa(
                        f"Conflicto de versión (SHA) al restaurar el borrador: el SHA de referencia '{sha_explicito}' "
                        f"no coincide con el SHA vigente en GitHub ('{sha_remoto_actual}').",
                        codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
                    )
                base_efectiva = lectura_remota.inventario
                sha_efectivo = sha_borrador or sha_explicito or sha_remoto_actual
            else:
                # Borrador creado explícitamente sobre copia demostrativa local cuando no existía remoto
                try:
                    _ = lector(config=config_github)
                except ErrorArchivoRemotoInexistente:
                    base_efectiva = crear_inventario_demostrativo()
                    sha_efectivo = None
                except ErrorLecturaGitHub as exc_red:
                    raise ErrorAdministracionInventario(
                        f"{MENSAJE_ERROR_CONEXION_ADMIN} Detalle: "
                        f"{ocultar_secretos_en_texto(exc_red.mensaje)}",
                        codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
                        estado=EstadoInventarioAdmin.ERROR_CONEXION,
                    ) from exc_red
                except Exception as exc_gen:
                    raise ErrorAdministracionInventario(
                        f"{MENSAJE_ERROR_CONEXION_ADMIN} Detalle: "
                        f"{ocultar_secretos_en_texto(str(exc_gen))}",
                        codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
                        estado=EstadoInventarioAdmin.ERROR_CONEXION,
                    ) from exc_gen
                else:
                    raise ErrorValidacionAdministrativa(
                        "Conflicto de versión al restaurar el borrador demostrativo: ahora existe un inventario "
                        "remoto confirmado en GitHub y no se permite sobrescribirlo ni mezclarlo.",
                        codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
                    )

        copia_original_prep = clonar_inventario_datos(base_efectiva)
        copia_trabajo_prep = clonar_inventario_datos(base_efectiva)
        espacio_preparacion = EspacioTrabajoAdminInventario(
            inventario_original=copia_original_prep,
            inventario_trabajo=copia_trabajo_prep,
            sha_base_remoto=sha_efectivo,
            origen_remoto_confirmado=origen_remoto,
            usuario_propietario=sesion.usuario,
            id_sesion_propietaria=sesion.token_sesion,
            creado_en_epoch=sesion.ultima_actividad_epoch,
            actualizado_en_epoch=sesion.ultima_actividad_epoch,
        )

        try:
            for op_raw in operaciones_guardadas:
                if not isinstance(op_raw, Mapping):
                    raise ErrorValidacionAdministrativa(
                        "Operación en borrador con estructura inválida.",
                        codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
                    )
                tipo_op = str(op_raw.get("tipo_operacion", "")).strip().upper()
                cod_op = op_raw.get("codigo_producto")
                nom_op = op_raw.get("nombre")
                cat_op = op_raw.get("categoria_id")
                desc_op = op_raw.get("descripcion", "")
                asig_op = op_raw.get("asignaciones")
                if not isinstance(asig_op, Sequence) or isinstance(
                    asig_op, (str, bytes)
                ):
                    raise ErrorValidacionAdministrativa(
                        "Asignaciones de operación en borrador inválidas.",
                        codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
                    )

                if tipo_op == "CREAR_PRODUCTO":
                    crear_producto_local(
                        estado,
                        codigo_producto=cod_op,
                        nombre=nom_op,
                        categoria_id=cat_op,
                        descripcion=desc_op,
                        asignaciones=asig_op,
                        espacio_trabajo=espacio_preparacion,
                        contexto_dispositivo=contexto_dispositivo,
                        reloj=reloj,
                        ahora_epoch=ahora_epoch,
                        _sincronizar_borrador=False,
                        _publicar_en_estado=False,
                        _registrar_actividad=False,
                    )
                elif tipo_op == "EDITAR_PRODUCTO":
                    editar_producto_local(
                        estado,
                        codigo_producto=cod_op,
                        nombre=nom_op,
                        categoria_id=cat_op,
                        descripcion=desc_op,
                        asignaciones=asig_op,
                        espacio_trabajo=espacio_preparacion,
                        contexto_dispositivo=contexto_dispositivo,
                        reloj=reloj,
                        ahora_epoch=ahora_epoch,
                        _sincronizar_borrador=False,
                        _publicar_en_estado=False,
                        _registrar_actividad=False,
                    )
                else:
                    raise ErrorValidacionAdministrativa(
                        f"Tipo de operación desconocido en borrador: '{tipo_op}'.",
                        codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
                    )
        except Exception as exc_rest:
            if isinstance(exc_rest, ErrorValidacionAdministrativa):
                raise
            raise ErrorValidacionAdministrativa(
                f"No fue posible restaurar el borrador por inconsistencia de datos: {exc_rest}",
                codigo=CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
            ) from exc_rest

    # 3. Confirmar la transición del borrador (y su consumo opcional) SOLO tras validar todo
    borrador_confirmado = restaurar_borrador_admin(
        estado,
        eliminar_tras_restaurar=eliminar_tras_restaurar,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
    )
    if borrador_confirmado is None:
        return None

    # 4. Publicar de forma atómica el espacio de trabajo validado y el formulario en estado
    sesion_confirmada = estado.get(autenticacion.CLAVE_SESION_ADMIN)
    marca_confirmada = (
        sesion_confirmada.ultima_actividad_epoch
        if isinstance(sesion_confirmada, EstadoSesionAdmin)
        else sesion.ultima_actividad_epoch
    )
    if espacio_preparacion is not None:
        espacio_preparacion.actualizado_en_epoch = marca_confirmada
        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = espacio_preparacion
        estado[CLAVE_RESULTADO_CARGA_ADMIN] = ResultadoCargaInventarioAdmin(
            estado=EstadoInventarioAdmin.INVENTARIO_DISPONIBLE_EDICION_LOCAL,
            mensaje_usuario=MENSAJE_INVENTARIO_DISPONIBLE_EDICION_LOCAL,
            espacio_trabajo=espacio_preparacion,
            sha_base_remoto=espacio_preparacion.sha_base_remoto,
            permite_reintentar=False,
        )
    estado[CLAVE_FORMULARIO_BORRADOR_ADMIN] = formulario_preparado

    return borrador_confirmado


def preparar_paquete_publicacion_futura_p10(
    estado: Mapping[str, Any],
    *,
    espacio_trabajo: EspacioTrabajoAdminInventario | None = None,
    contexto_dispositivo: ContextoDispositivo | None = None,
    reloj: ProveedorReloj | None = None,
    ahora_epoch: float | None = None,
) -> PaquetePublicacionPendienteP10:
    """Prepara y valida el contrato de datos para la futura publicación remota del Prompt 10 (Secciones 6 y 9).

    No realiza llamadas de red ni crea archivos locales.
    """
    _, espacio = _obtener_espacio_trabajo_autorizado(
        estado,
        espacio_explicito=espacio_trabajo,
        contexto_dispositivo=contexto_dispositivo,
        reloj=reloj,
        ahora_epoch=ahora_epoch,
        registrar_actividad=False,
    )
    copia_validada = clonar_inventario_datos(espacio.inventario_trabajo)
    return PaquetePublicacionPendienteP10(
        inventario_validado=copia_validada,
        sha_base_remoto=espacio.sha_base_remoto,
        origen_remoto_confirmado=espacio.origen_remoto_confirmado,
        tiene_cambios_pendientes=espacio.tiene_cambios_locales_pendientes,
        codigos_productos_creados=espacio.codigos_productos_creados,
        codigos_productos_editados=espacio.codigos_productos_editados,
        total_operaciones_locales=len(espacio.historial_operaciones_locales),
        confirmado_en_github=False,
    )
