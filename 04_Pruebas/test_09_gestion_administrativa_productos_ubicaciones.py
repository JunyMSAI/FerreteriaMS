"""Pruebas automatizadas del Prompt 09: Gestión administrativa de productos y ubicaciones.

Proyecto: FerreteríaMS v0
Tarea: FERMS-V0-P09
Cobertura: 40 pruebas obligatorias de la Sección 12 del Prompt 09 (RF-011..RF-024,
RF-027 preparación SHA, CA-009..CA-019, CA-022, CA-027..CA-030, CA-044..CA-051 local,
CA-055, CA-057, CA-058).
"""

from __future__ import annotations

import os
import secrets
import sys
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_APLICACION = RAIZ_PROYECTO / "03_Aplicacion"
RUTA_APP = RUTA_APLICACION / "app.py"
RUTA_ADMIN_PRODUCTOS = RUTA_APLICACION / "administracion_productos.py"
RUTA_AUTENTICACION = RUTA_APLICACION / "autenticacion.py"
RUTA_INVENTARIO_XLSX = RUTA_APLICACION / "inventario.xlsx"
BYTES_INVENTARIO_XLSX_INICIAL = (
    RUTA_INVENTARIO_XLSX.read_bytes() if RUTA_INVENTARIO_XLSX.exists() else None
)

if str(RUTA_APLICACION) not in sys.path:
    sys.path.insert(0, str(RUTA_APLICACION))

import administracion_productos as admin_prod  # noqa: E402
import app as app_ferms  # noqa: E402
import autenticacion  # noqa: E402
import busqueda  # noqa: E402
import github_inventario  # noqa: E402
import inventario as motor_inventario  # noqa: E402
from administracion_productos import (  # noqa: E402
    CLAVE_ESPACIO_TRABAJO_ADMIN,
    CLAVE_FORMULARIO_BORRADOR_ADMIN,
    CLAVE_MENSAJE_OPERACION_ADMIN,
    CLAVE_MODO_VISTA_ADMIN,
    CLAVE_PRODUCTO_ADMIN_SELECCIONADO,
    CLAVE_RESULTADO_CARGA_ADMIN,
    AsignacionUbicacionEntrada,
    CodigoErrorAdministrativo,
    ErrorAdministracionInventario,
    ErrorValidacionAdministrativa,
    EspacioTrabajoAdminInventario,
    EstadoInventarioAdmin,
    ModoVistaAdmin,
    cambiar_ubicacion_principal_local,
    cargar_inventario_administrativo_en_sesion,
    clonar_inventario_datos,
    consultar_producto_administrativo_por_codigo,
    consultar_productos_administrativos,
    crear_producto_local,
    descartar_cambios_locales_en_sesion,
    editar_producto_local,
    eliminar_asignacion_ubicacion_local,
    guardar_borrador_formulario_admin,
    inicializar_espacio_trabajo_desde_inventario,
    inventarios_son_identicos,
    obtener_catalogo_categorias_admin,
    obtener_catalogo_ubicaciones_admin,
    preparar_paquete_publicacion_futura_p10,
    rechazar_modificacion_catalogo_predefinido,
    restaurar_borrador_en_espacio_trabajo_admin,
)
from autenticacion import (  # noqa: E402
    CLAVE_CONTEXTO_DISPOSITIVO,
    CLAVE_SESION_ADMIN,
    TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS,
    TIEMPO_RETENCION_BORRADOR_SEGUNDOS,
    CodigoResultadoAutenticacion,
    ContextoDispositivo,
    ErrorAutorizacionAdmin,
    configurar_reloj_servidor_pruebas,
    es_hash_contrasena_valido,
    generar_hash_contrasena,
    iniciar_sesion_admin,
    obtener_borrador_admin,
    reiniciar_estado_seguridad_servidor,
    tiene_borrador_pendiente_en_sesion,
)
from github_inventario import (  # noqa: E402
    CategoriaResultadoConsulta,
    ErrorArchivoRemotoInexistente,
    ResultadoLecturaInventarioRemoto,
)
from inventario import (  # noqa: E402
    ESQUEMA_HOJAS,
    ORDEN_HOJAS,
    crear_inventario_demostrativo,
)

SHA_REMOTO_SIMULADO = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"


class RelojSimuladoP09:
    """Reloj determinista para simular expiración de sesión, bloqueos y retención de borradores."""

    def __init__(self, epoch_inicial: float = 2_000_000.0) -> None:
        self.actual: float = float(epoch_inicial)

    def __call__(self) -> float:
        return self.actual

    def avanzar(self, segundos: float) -> float:
        self.actual += float(segundos)
        return self.actual


class PruebasPrompt09GestionAdministrativaProductosUbicaciones(unittest.TestCase):
    """Suite oficial de 40 pruebas obligatorias del Prompt 09 (Sección 12)."""

    USUARIO_PRUEBA: str = ""
    CONTRASENA_PRUEBA: str = ""
    HASH_PRUEBA_ARGON2ID: str = ""
    SECRETOS_VALIDOS: dict[str, str] = {}

    @classmethod
    def setUpClass(cls) -> None:
        cls.USUARIO_PRUEBA = f"admin_p09_{secrets.token_hex(4)}"
        cls.CONTRASENA_PRUEBA = f"ClaveSeguraP09_{secrets.token_urlsafe(10)}"
        cls.HASH_PRUEBA_ARGON2ID = generar_hash_contrasena(cls.CONTRASENA_PRUEBA)
        cls.SECRETOS_VALIDOS = {
            "FERRETERIAMS_ADMIN_USER": cls.USUARIO_PRUEBA,
            "FERRETERIAMS_ADMIN_PASSWORD_HASH": cls.HASH_PRUEBA_ARGON2ID,
        }

    def setUp(self) -> None:
        reiniciar_estado_seguridad_servidor()
        self.reloj = RelojSimuladoP09(epoch_inicial=2_000_000.0)
        configurar_reloj_servidor_pruebas(self.reloj)
        self.secretos_validos = dict(self.SECRETOS_VALIDOS)
        self.inventario_base = crear_inventario_demostrativo()

        def _verificar_rapido(contrasena_plana: Any, hash_almacenado: str) -> bool:
            if not isinstance(contrasena_plana, str) or not contrasena_plana:
                return False
            if not es_hash_contrasena_valido(hash_almacenado):
                return False
            return (
                contrasena_plana == self.CONTRASENA_PRUEBA
                and hash_almacenado == self.HASH_PRUEBA_ARGON2ID
            )

        self.patcher_argon2 = patch.object(
            autenticacion,
            "verificar_contrasena_hash",
            side_effect=_verificar_rapido,
        )
        self.patcher_argon2.start()

    def tearDown(self) -> None:
        self.patcher_argon2.stop()
        reiniciar_estado_seguridad_servidor()

    def _crear_sesion_y_espacio_admin(
        self,
        *,
        sha_remoto: str | None = SHA_REMOTO_SIMULADO,
    ) -> tuple[dict[str, Any], EspacioTrabajoAdminInventario]:
        """Crea una sesión administrativa autenticada en escritorio e inicializa el espacio de trabajo."""
        estado: dict[str, Any] = {}
        app_ferms.inicializar_estado_sesion(estado)
        res_login = iniciar_sesion_admin(
            usuario=self.USUARIO_PRUEBA,
            contrasena=self.CONTRASENA_PRUEBA,
            estado=estado,
            fuente_secretos=self.secretos_validos,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )
        self.assertTrue(res_login.autenticado)
        espacio = inicializar_espacio_trabajo_desde_inventario(
            estado,
            self.inventario_base,
            sha_base_remoto=sha_remoto,
            origen_remoto_confirmado=True,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )
        return estado, espacio

    # ------------------------------------------------------------------
    # 01. Consulta administrativa del inventario con sesión válida
    # ------------------------------------------------------------------
    def test_01_consulta_administrativa_inventario_con_sesion_valida(self) -> None:
        estado, espacio = self._crear_sesion_y_espacio_admin()
        productos = consultar_productos_administrativos(
            estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )
        self.assertEqual(len(productos), len(self.inventario_base.productos))
        primer_prod = productos[0]
        self.assertEqual(primer_prod["codigo_producto"], "MAR001")
        self.assertIn("Martillo", primer_prod["nombre"])
        self.assertEqual(primer_prod["categoria_id"], "CAT01")
        self.assertIsNotNone(primer_prod["ubicacion_principal"])
        self.assertTrue(primer_prod["confirmado_en_github"])
        self.assertFalse(primer_prod["tiene_cambios_locales"])
        self.assertEqual(espacio.sha_base_remoto, SHA_REMOTO_SIMULADO)

        # Filtro administrativo interno por código o nombre
        filtrados = consultar_productos_administrativos(
            estado,
            termino_filtro="TOR001",
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )
        self.assertEqual(len(filtrados), 1)
        self.assertEqual(filtrados[0]["codigo_producto"], "TOR001")

    # ------------------------------------------------------------------
    # 02. Creación válida de producto con una ubicación principal
    # ------------------------------------------------------------------
    def test_02_creacion_valida_producto_con_una_ubicacion_principal(self) -> None:
        estado, espacio = self._crear_sesion_y_espacio_admin()
        res = crear_producto_local(
            estado,
            codigo_producto="P-100",
            nombre="Taladro Percutor Industrial 850W",
            categoria_id="CAT01",
            descripcion="Taladro con mandril de 1/2 pulgada para concreto y metal.",
            ubicaciones_ids=["U001"],
            ubicacion_principal_id="U001",
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )
        self.assertTrue(res.exito)
        self.assertEqual(res.estado, EstadoInventarioAdmin.MODIFICACION_LOCAL_VALIDA)
        self.assertFalse(res.confirmado_en_github)
        self.assertTrue(res.es_cambio_local_temporal)
        self.assertTrue(espacio.tiene_cambios_locales_pendientes)
        self.assertIn("P-100", espacio.codigos_productos_creados)

        detalle = consultar_producto_administrativo_por_codigo(
            estado, "P-100", reloj=self.reloj
        )
        self.assertEqual(detalle["nombre"], "Taladro Percutor Industrial 850W")
        self.assertEqual(detalle["ubicacion_principal"]["ubicacion_id"], "U001")
        self.assertEqual(len(detalle["ubicaciones_secundarias"]), 0)
        self.assertTrue(detalle["es_nuevo_local"])
        self.assertFalse(detalle["confirmado_en_github"])

    # ------------------------------------------------------------------
    # 03. Creación válida de producto con ubicación principal y secundarias
    # ------------------------------------------------------------------
    def test_03_creacion_valida_producto_con_principal_y_secundarias(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        res = crear_producto_local(
            estado,
            codigo_producto="P-101",
            nombre="Juego de Llaves Combinadas Milimétricas",
            categoria_id="CAT01",
            descripcion="Set de 12 piezas en acero cromo-vanadio.",
            ubicaciones_ids=["U001", "U002", "U003"],
            ubicacion_principal_id="U002",
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )
        self.assertTrue(res.exito)
        detalle = consultar_producto_administrativo_por_codigo(
            estado, "P-101", reloj=self.reloj
        )
        self.assertEqual(detalle["ubicacion_principal"]["ubicacion_id"], "U002")
        ids_secundarias = [
            u["ubicacion_id"] for u in detalle["ubicaciones_secundarias"]
        ]
        self.assertEqual(ids_secundarias, ["U001", "U003"])

    # ------------------------------------------------------------------
    # 04. Conservación de ceros iniciales en Codigo_Producto
    # ------------------------------------------------------------------
    def test_04_conservacion_ceros_iniciales_en_codigo_producto(self) -> None:
        estado, espacio = self._crear_sesion_y_espacio_admin()
        res = crear_producto_local(
            estado,
            codigo_producto="00045",
            nombre="Broca para concreto 3/8",
            categoria_id="CAT02",
            descripcion="Broca con punta de carburo de tungsteno.",
            ubicaciones_ids=["U003"],
            ubicacion_principal_id="U003",
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )
        self.assertTrue(res.exito)
        self.assertEqual(res.codigo_producto, "00045")
        codigos_df = espacio.inventario_trabajo.productos["Codigo_Producto"].tolist()
        self.assertIn("00045", codigos_df)
        self.assertNotIn("45", codigos_df)

        # También rechaza enteros para evitar pérdida silenciosa de ceros iniciales
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
            crear_producto_local(
                estado,
                codigo_producto=45,
                nombre="Broca numérica",
                categoria_id="CAT02",
                ubicaciones_ids=["U003"],
                ubicacion_principal_id="U003",
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo,
            CodigoErrorAdministrativo.CODIGO_PRODUCTO_OBLIGATORIO,
        )

    # ------------------------------------------------------------------
    # 05. Rechazo de código de producto vacío
    # ------------------------------------------------------------------
    def test_05_rechazo_codigo_producto_vacio(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        for codigo_invalido in ("", "   ", None):
            with self.subTest(codigo=codigo_invalido):
                with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
                    crear_producto_local(
                        estado,
                        codigo_producto=codigo_invalido,
                        nombre="Producto con código vacío",
                        categoria_id="CAT01",
                        ubicaciones_ids=["U001"],
                        ubicacion_principal_id="U001",
                        reloj=self.reloj,
                    )
                self.assertEqual(
                    ctx.exception.codigo,
                    CodigoErrorAdministrativo.CODIGO_PRODUCTO_OBLIGATORIO,
                )

    # ------------------------------------------------------------------
    # 06. Rechazo de código de producto duplicado
    # ------------------------------------------------------------------
    def test_06_rechazo_codigo_producto_duplicado(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
            crear_producto_local(
                estado,
                codigo_producto="MAR001",
                nombre="Intento duplicar código MAR001",
                categoria_id="CAT01",
                ubicaciones_ids=["U001"],
                ubicacion_principal_id="U001",
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo,
            CodigoErrorAdministrativo.CODIGO_PRODUCTO_DUPLICADO,
        )

    # ------------------------------------------------------------------
    # 07. Rechazo de nombre de producto vacío
    # ------------------------------------------------------------------
    def test_07_rechazo_nombre_producto_vacio(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        for nombre_invalido in ("", "    ", None):
            with self.subTest(nombre=nombre_invalido):
                with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
                    crear_producto_local(
                        estado,
                        codigo_producto="P-200",
                        nombre=nombre_invalido,
                        categoria_id="CAT01",
                        ubicaciones_ids=["U001"],
                        ubicacion_principal_id="U001",
                        reloj=self.reloj,
                    )
                self.assertEqual(
                    ctx.exception.codigo,
                    CodigoErrorAdministrativo.NOMBRE_PRODUCTO_OBLIGATORIO,
                )

    # ------------------------------------------------------------------
    # 08. Rechazo de categoría inexistente
    # ------------------------------------------------------------------
    def test_08_rechazo_categoria_inexistente(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
            crear_producto_local(
                estado,
                codigo_producto="P-201",
                nombre="Producto con categoría inexistente",
                categoria_id="CAT-999",
                ubicaciones_ids=["U001"],
                ubicacion_principal_id="U001",
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo,
            CodigoErrorAdministrativo.CATEGORIA_INEXISTENTE,
        )

    # ------------------------------------------------------------------
    # 09. Rechazo de ubicación inexistente
    # ------------------------------------------------------------------
    def test_09_rechazo_ubicacion_inexistente(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
            crear_producto_local(
                estado,
                codigo_producto="P-202",
                nombre="Producto con ubicación inexistente",
                categoria_id="CAT01",
                ubicaciones_ids=["UBI-999"],
                ubicacion_principal_id="UBI-999",
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo,
            CodigoErrorAdministrativo.UBICACION_INEXISTENTE,
        )

    # ------------------------------------------------------------------
    # 10. Rechazo de producto sin ubicación asignada
    # ------------------------------------------------------------------
    def test_10_rechazo_producto_sin_ubicacion_asignada(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
            crear_producto_local(
                estado,
                codigo_producto="P-203",
                nombre="Producto sin ubicaciones",
                categoria_id="CAT01",
                ubicaciones_ids=[],
                ubicacion_principal_id="U001",
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo,
            CodigoErrorAdministrativo.PRODUCTO_SIN_UBICACION,
        )

    # ------------------------------------------------------------------
    # 11. Rechazo de producto sin ubicación principal
    # ------------------------------------------------------------------
    def test_11_rechazo_producto_sin_ubicacion_principal(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
            crear_producto_local(
                estado,
                codigo_producto="P-204",
                nombre="Producto sin ubicación principal",
                categoria_id="CAT01",
                asignaciones=[
                    {"Ubicacion_ID": "U001", "Principal": "No"},
                    {"Ubicacion_ID": "U002", "Principal": "No"},
                ],
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo,
            CodigoErrorAdministrativo.SIN_UBICACION_PRINCIPAL,
        )

    # ------------------------------------------------------------------
    # 12. Rechazo de producto con dos ubicaciones principales
    # ------------------------------------------------------------------
    def test_12_rechazo_producto_con_dos_ubicaciones_principales(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
            crear_producto_local(
                estado,
                codigo_producto="P-205",
                nombre="Producto con doble principal",
                categoria_id="CAT01",
                asignaciones=[
                    {"Ubicacion_ID": "U001", "Principal": "Sí"},
                    {"Ubicacion_ID": "U002", "Principal": "Sí"},
                ],
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo,
            CodigoErrorAdministrativo.UBICACION_PRINCIPAL_MULTIPLE,
        )

    # ------------------------------------------------------------------
    # 13. Rechazo de asignación duplicada (Codigo_Producto, Ubicacion_ID)
    # ------------------------------------------------------------------
    def test_13_rechazo_asignacion_duplicada_mismo_producto_ubicacion(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
            crear_producto_local(
                estado,
                codigo_producto="P-206",
                nombre="Producto con asignación repetida",
                categoria_id="CAT01",
                ubicaciones_ids=["U001", "U001"],
                ubicacion_principal_id="U001",
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo,
            CodigoErrorAdministrativo.ASIGNACION_DUPLICADA,
        )

    # ------------------------------------------------------------------
    # 14. Edición válida de nombre de producto
    # ------------------------------------------------------------------
    def test_14_edicion_valida_nombre_producto(self) -> None:
        estado, espacio = self._crear_sesion_y_espacio_admin()
        res = editar_producto_local(
            estado,
            codigo_producto="MAR001",
            nombre="Martillo Carpintero Mango Fibra 16 oz",
            reloj=self.reloj,
        )
        self.assertTrue(res.exito)
        self.assertIn("MAR001", espacio.codigos_productos_editados)
        detalle = consultar_producto_administrativo_por_codigo(
            estado, "MAR001", reloj=self.reloj
        )
        self.assertEqual(detalle["nombre"], "Martillo Carpintero Mango Fibra 16 oz")
        self.assertEqual(detalle["codigo_producto"], "MAR001")

    # ------------------------------------------------------------------
    # 15. Edición válida de categoría de producto
    # ------------------------------------------------------------------
    def test_15_edicion_valida_categoria_producto(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        res = editar_producto_local(
            estado,
            codigo_producto="MAR001",
            categoria_id="CAT02",
            reloj=self.reloj,
        )
        self.assertTrue(res.exito)
        detalle = consultar_producto_administrativo_por_codigo(
            estado, "MAR001", reloj=self.reloj
        )
        self.assertEqual(detalle["categoria_id"], "CAT02")

    # ------------------------------------------------------------------
    # 16. Edición válida de descripción de producto
    # ------------------------------------------------------------------
    def test_16_edicion_valida_descripcion_producto(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        nueva_desc = "Descripción actualizada en copia local validada."
        res = editar_producto_local(
            estado,
            codigo_producto="TOR001",
            descripcion=nueva_desc,
            reloj=self.reloj,
        )
        self.assertTrue(res.exito)
        detalle = consultar_producto_administrativo_por_codigo(
            estado, "TOR001", reloj=self.reloj
        )
        self.assertEqual(detalle["descripcion"], nueva_desc)

    # ------------------------------------------------------------------
    # 17. Rechazo de intento de modificar Codigo_Producto existente
    # ------------------------------------------------------------------
    def test_17_rechazo_modificar_codigo_producto_en_producto_existente(self) -> None:
        estado, espacio = self._crear_sesion_y_espacio_admin()
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
            editar_producto_local(
                estado,
                codigo_producto="MAR001",
                nuevo_codigo_producto="MAR001-MOD",
                nombre="Intento cambiar código",
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo,
            CodigoErrorAdministrativo.CODIGO_PRODUCTO_INMUTABLE,
        )
        self.assertFalse(espacio.tiene_cambios_locales_pendientes)

    # ------------------------------------------------------------------
    # 18. Cambio válido de ubicación principal entre ubicaciones asignadas
    # ------------------------------------------------------------------
    def test_18_cambio_valido_ubicacion_principal_entre_asignadas(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        # MAR001 tiene U001 (Principal) y U002 (Secundaria)
        res = cambiar_ubicacion_principal_local(
            estado,
            codigo_producto="MAR001",
            nueva_ubicacion_principal_id="U002",
            reloj=self.reloj,
        )
        self.assertTrue(res.exito)
        detalle = consultar_producto_administrativo_por_codigo(
            estado, "MAR001", reloj=self.reloj
        )
        self.assertEqual(detalle["ubicacion_principal"]["ubicacion_id"], "U002")
        ids_secundarias = [
            u["ubicacion_id"] for u in detalle["ubicaciones_secundarias"]
        ]
        self.assertEqual(ids_secundarias, ["U001"])

    # ------------------------------------------------------------------
    # 19. Asignación válida de nueva ubicación secundaria a producto existente
    # ------------------------------------------------------------------
    def test_19_asignacion_valida_nueva_ubicacion_secundaria_producto_existente(
        self,
    ) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        # TOR001 tiene originalmente U002 como principal; añadimos U001 como secundaria
        res = editar_producto_local(
            estado,
            codigo_producto="TOR001",
            ubicaciones_ids=["U002", "U001"],
            ubicacion_principal_id="U002",
            reloj=self.reloj,
        )
        self.assertTrue(res.exito)
        detalle = consultar_producto_administrativo_por_codigo(
            estado, "TOR001", reloj=self.reloj
        )
        self.assertEqual(detalle["ubicacion_principal"]["ubicacion_id"], "U002")
        ids_secundarias = [
            u["ubicacion_id"] for u in detalle["ubicaciones_secundarias"]
        ]
        self.assertEqual(ids_secundarias, ["U001"])

    # ------------------------------------------------------------------
    # 20. Eliminación válida de ubicación secundaria conservando principal
    # ------------------------------------------------------------------
    def test_20_eliminacion_valida_ubicacion_secundaria_con_principal_valida(
        self,
    ) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        # MAR001 tiene U001 (Principal) y U002 (Secundaria)
        res = eliminar_asignacion_ubicacion_local(
            estado,
            codigo_producto="MAR001",
            ubicacion_id="U002",
            reloj=self.reloj,
        )
        self.assertTrue(res.exito)
        detalle = consultar_producto_administrativo_por_codigo(
            estado, "MAR001", reloj=self.reloj
        )
        self.assertEqual(detalle["ubicacion_principal"]["ubicacion_id"], "U001")
        self.assertEqual(len(detalle["ubicaciones_secundarias"]), 0)

    # ------------------------------------------------------------------
    # 21. Rechazo de eliminación de la única ubicación de un producto
    # ------------------------------------------------------------------
    def test_21_rechazo_eliminacion_unica_ubicacion_de_un_producto(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        # TOR001 tiene únicamente U002 asignada
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
            eliminar_asignacion_ubicacion_local(
                estado,
                codigo_producto="TOR001",
                ubicacion_id="U002",
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo,
            CodigoErrorAdministrativo.ELIMINACION_UNICA_UBICACION,
        )

    # ------------------------------------------------------------------
    # 22. Rechazo de eliminación que deje al producto sin ubicación principal
    # ------------------------------------------------------------------
    def test_22_rechazo_eliminacion_que_deje_sin_ubicacion_principal(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        # MAR001 tiene U001 (Principal) y U002 (Secundaria); intentar retirar U001 falla
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
            eliminar_asignacion_ubicacion_local(
                estado,
                codigo_producto="MAR001",
                ubicacion_id="U001",
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo,
            CodigoErrorAdministrativo.SIN_UBICACION_PRINCIPAL,
        )

    # ------------------------------------------------------------------
    # 23. Atomicidad de creación: si falla asignación, no se agrega Producto
    # ------------------------------------------------------------------
    def test_23_atomicidad_creacion_fallo_asignacion_no_agrega_producto(self) -> None:
        estado, espacio = self._crear_sesion_y_espacio_admin()
        inv_antes = clonar_inventario_datos(espacio.inventario_trabajo)
        with self.assertRaises(ErrorValidacionAdministrativa):
            crear_producto_local(
                estado,
                codigo_producto="P-ATOM-01",
                nombre="Producto con asignación inválida",
                categoria_id="CAT01",
                ubicaciones_ids=["U001", "UBI-INEXISTENTE"],
                ubicacion_principal_id="U001",
                reloj=self.reloj,
            )
        self.assertTrue(inventarios_son_identicos(inv_antes, espacio.inventario_trabajo))
        codigos = espacio.inventario_trabajo.productos["Codigo_Producto"].tolist()
        self.assertNotIn("P-ATOM-01", codigos)
        self.assertFalse(espacio.tiene_cambios_locales_pendientes)

    # ------------------------------------------------------------------
    # 24. Atomicidad de edición: si falla validación, conserva estado previo
    # ------------------------------------------------------------------
    def test_24_atomicidad_edicion_fallo_validacion_conserva_estado_previo(
        self,
    ) -> None:
        estado, espacio = self._crear_sesion_y_espacio_admin()
        inv_antes = clonar_inventario_datos(espacio.inventario_trabajo)
        with self.assertRaises(ErrorValidacionAdministrativa):
            editar_producto_local(
                estado,
                codigo_producto="MAR001",
                nombre="Nombre que no debe aplicarse porque falla ubicación",
                asignaciones=[
                    {"Ubicacion_ID": "U001", "Principal": "No"},
                    {"Ubicacion_ID": "U002", "Principal": "No"},
                ],
                reloj=self.reloj,
            )
        self.assertTrue(inventarios_son_identicos(inv_antes, espacio.inventario_trabajo))
        detalle_mar = consultar_producto_administrativo_por_codigo(
            estado, "MAR001", reloj=self.reloj
        )
        self.assertNotEqual(
            detalle_mar["nombre"],
            "Nombre que no debe aplicarse porque falla ubicación",
        )
        self.assertFalse(espacio.tiene_cambios_locales_pendientes)

    # ------------------------------------------------------------------
    # 25. Preservación de las cuatro hojas Excel y el orden exacto de columnas
    # ------------------------------------------------------------------
    def test_25_preservacion_cuatro_hojas_y_orden_exacto_columnas(self) -> None:
        estado, espacio = self._crear_sesion_y_espacio_admin()
        crear_producto_local(
            estado,
            codigo_producto="P-HOJAS-01",
            nombre="Nivel Láser Autonivelante",
            categoria_id="CAT01",
            ubicaciones_ids=["U001", "U003"],
            ubicacion_principal_id="U001",
            reloj=self.reloj,
        )
        editar_producto_local(
            estado,
            codigo_producto="MAR001",
            nombre="Martillo Profesional Editado",
            reloj=self.reloj,
        )
        hojas = espacio.inventario_trabajo.obtener_hojas()
        self.assertEqual(tuple(hojas.keys()), ORDEN_HOJAS)
        for nombre_hoja in ORDEN_HOJAS:
            self.assertEqual(
                list(hojas[nombre_hoja].columns),
                list(ESQUEMA_HOJAS[nombre_hoja]),
            )

    # ------------------------------------------------------------------
    # 26. Preservación de los demás productos y relaciones no modificados
    # ------------------------------------------------------------------
    def test_26_preservacion_demas_productos_y_relaciones_no_modificados(self) -> None:
        estado, espacio = self._crear_sesion_y_espacio_admin()
        prod_tor_antes = consultar_producto_administrativo_por_codigo(
            estado, "TOR001", reloj=self.reloj
        )
        editar_producto_local(
            estado,
            codigo_producto="MAR001",
            nombre="Martillo Modificado Solamente",
            reloj=self.reloj,
        )
        prod_tor_despues = consultar_producto_administrativo_por_codigo(
            estado, "TOR001", reloj=self.reloj
        )
        self.assertEqual(prod_tor_antes["nombre"], prod_tor_despues["nombre"])
        self.assertEqual(
            prod_tor_antes["categoria_id"], prod_tor_despues["categoria_id"]
        )
        self.assertEqual(
            prod_tor_antes["ubicacion_principal"],
            prod_tor_despues["ubicacion_principal"],
        )
        # El inventario original dentro del espacio de trabajo permanece intacto
        self.assertTrue(
            inventarios_son_identicos(
                self.inventario_base, espacio.inventario_original
            )
        )

    # ------------------------------------------------------------------
    # 27. Rechazo de creación, edición o eliminación de categorías o ubicaciones
    # ------------------------------------------------------------------
    def test_27_rechazo_modificacion_catalogos_categorias_ubicaciones_en_v0(
        self,
    ) -> None:
        for catalogo in ("Categorías", "Ubicaciones"):
            with self.subTest(catalogo=catalogo):
                with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
                    rechazar_modificacion_catalogo_predefinido(catalogo)
                self.assertEqual(
                    ctx.exception.codigo,
                    CodigoErrorAdministrativo.OPERACION_CATALOGO_NO_PERMITIDA,
                )

    # ------------------------------------------------------------------
    # 28. Rechazo de operaciones administrativas sin sesión autenticada
    # ------------------------------------------------------------------
    def test_28_rechazo_operaciones_administrativas_sin_sesion_autenticada(
        self,
    ) -> None:
        estado_no_auth: dict[str, Any] = {}
        app_ferms.inicializar_estado_sesion(estado_no_auth)
        with self.assertRaises(ErrorAutorizacionAdmin):
            consultar_productos_administrativos(estado_no_auth, reloj=self.reloj)
        with self.assertRaises(ErrorAutorizacionAdmin):
            crear_producto_local(
                estado_no_auth,
                codigo_producto="P-NOAUTH",
                nombre="Intento sin sesión",
                categoria_id="CAT01",
                ubicaciones_ids=["U001"],
                ubicacion_principal_id="U001",
                reloj=self.reloj,
            )
        with self.assertRaises(ErrorAutorizacionAdmin):
            editar_producto_local(
                estado_no_auth,
                codigo_producto="MAR001",
                nombre="Intento editar sin sesión",
                reloj=self.reloj,
            )

    # ------------------------------------------------------------------
    # 29. Rechazo de operaciones administrativas tras expiración de sesión
    # ------------------------------------------------------------------
    def test_29_rechazo_operaciones_administrativas_tras_expiracion_sesion(
        self,
    ) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        self.reloj.avanzar(TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS + 1)
        with self.assertRaises(ErrorAutorizacionAdmin) as ctx:
            crear_producto_local(
                estado,
                codigo_producto="P-EXP",
                nombre="Producto con sesión expirada",
                categoria_id="CAT01",
                ubicaciones_ids=["U001"],
                ubicacion_principal_id="U001",
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo,
            CodigoResultadoAutenticacion.SESION_EXPIRADA,
        )
        self.assertIsNone(estado.get(CLAVE_ESPACIO_TRABAJO_ADMIN))

    # ------------------------------------------------------------------
    # 30. Rechazo de operaciones administrativas durante bloqueo activo
    # ------------------------------------------------------------------
    def test_30_rechazo_operaciones_administrativas_durante_bloqueo_activo(
        self,
    ) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        estado_intento: dict[str, Any] = {}
        for _ in range(5):
            iniciar_sesion_admin(
                usuario=self.USUARIO_PRUEBA,
                contrasena="ClaveIncorrecta!",
                estado=estado_intento,
                fuente_secretos=self.secretos_validos,
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
                reloj=self.reloj,
            )
        with self.assertRaises(ErrorAutorizacionAdmin) as ctx:
            crear_producto_local(
                estado,
                codigo_producto="P-BLOQ",
                nombre="Intento durante bloqueo activo",
                categoria_id="CAT01",
                ubicaciones_ids=["U001"],
                ubicacion_principal_id="U001",
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo,
            CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE,
        )

    # ------------------------------------------------------------------
    # 31. Rechazo de operaciones administrativas en contexto móvil
    # ------------------------------------------------------------------
    def test_31_rechazo_operaciones_administrativas_en_contexto_movil(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        with self.assertRaises(ErrorAutorizacionAdmin) as ctx:
            crear_producto_local(
                estado,
                codigo_producto="P-MOVIL",
                nombre="Intento desde móvil",
                categoria_id="CAT01",
                ubicaciones_ids=["U001"],
                ubicacion_principal_id="U001",
                contexto_dispositivo=ContextoDispositivo.MOVIL,
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo,
            CodigoResultadoAutenticacion.DISPOSITIVO_NO_PERMITIDO,
        )

    # ------------------------------------------------------------------
    # 32. Retención de cambios locales en borrador cuando expira la sesión
    # ------------------------------------------------------------------
    def test_32_retencion_cambios_locales_en_borrador_cuando_expira_sesion(
        self,
    ) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        crear_producto_local(
            estado,
            codigo_producto="P-BORR-32",
            nombre="Producto retenido en borrador",
            categoria_id="CAT01",
            ubicaciones_ids=["U001"],
            ubicacion_principal_id="U001",
            reloj=self.reloj,
        )
        self.reloj.avanzar(TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS + 5)
        self.assertTrue(tiene_borrador_pendiente_en_sesion(estado, reloj=self.reloj))
        estado_tiempo = autenticacion.consultar_estado_sesion_admin(
            estado, reloj=self.reloj
        )
        self.assertTrue(estado_tiempo.expirada)
        self.assertTrue(estado_tiempo.tiene_borrador_retenido)
        # Mientras no se reautentique, obtener_borrador_admin rechaza la lectura directa
        with self.assertRaises(ErrorAutorizacionAdmin):
            obtener_borrador_admin(estado, reloj=self.reloj)

    # ------------------------------------------------------------------
    # 33. Recuperación válida del borrador tras reautenticación dentro de 15 min
    # ------------------------------------------------------------------
    def test_33_recuperacion_valida_borrador_tras_reautenticacion_dentro_15_min(
        self,
    ) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        crear_producto_local(
            estado,
            codigo_producto="P-REC-33",
            nombre="Esmeriladora Angular 4-1/2",
            categoria_id="CAT01",
            descripcion="Esmeriladora de 900W.",
            ubicaciones_ids=["U001", "U002"],
            ubicacion_principal_id="U001",
            reloj=self.reloj,
        )
        # Expira la sesión a los 15 minutos
        self.reloj.avanzar(TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS + 10)
        # 5 minutos después (dentro de la ventana de 15 min post-expiración), el admin se reautentica
        self.reloj.avanzar(300)
        res_relogin = iniciar_sesion_admin(
            usuario=self.USUARIO_PRUEBA,
            contrasena=self.CONTRASENA_PRUEBA,
            estado=estado,
            fuente_secretos=self.secretos_validos,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )
        self.assertTrue(res_relogin.autenticado)
        self.assertTrue(tiene_borrador_pendiente_en_sesion(estado, reloj=self.reloj))

        borrador = restaurar_borrador_en_espacio_trabajo_admin(
            estado,
            inventario_base=self.inventario_base,
            sha_base_remoto=SHA_REMOTO_SIMULADO,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )
        self.assertIsNotNone(borrador)
        prod_recuperado = consultar_producto_administrativo_por_codigo(
            estado, "P-REC-33", reloj=self.reloj
        )
        self.assertEqual(prod_recuperado["nombre"], "Esmeriladora Angular 4-1/2")
        self.assertEqual(
            prod_recuperado["ubicacion_principal"]["ubicacion_id"], "U001"
        )

    # ------------------------------------------------------------------
    # 34. Eliminación del borrador tras vencer los 15 min posteriores a expiración
    # ------------------------------------------------------------------
    def test_34_eliminacion_borrador_tras_vencer_15_minutos_post_expiracion(
        self,
    ) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        crear_producto_local(
            estado,
            codigo_producto="P-VENC-34",
            nombre="Producto cuyo borrador vencerá",
            categoria_id="CAT01",
            ubicaciones_ids=["U001"],
            ubicacion_principal_id="U001",
            reloj=self.reloj,
        )
        self.reloj.avanzar(
            TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS
            + TIEMPO_RETENCION_BORRADOR_SEGUNDOS
            + 2
        )
        self.assertFalse(tiene_borrador_pendiente_en_sesion(estado, reloj=self.reloj))
        iniciar_sesion_admin(
            usuario=self.USUARIO_PRUEBA,
            contrasena=self.CONTRASENA_PRUEBA,
            estado=estado,
            fuente_secretos=self.secretos_validos,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )
        self.assertIsNone(obtener_borrador_admin(estado, reloj=self.reloj))

    # ------------------------------------------------------------------
    # 35. Eliminación de cambios y borradores al ejecutar Logout
    # ------------------------------------------------------------------
    def test_35_eliminacion_cambios_y_borradores_al_ejecutar_logout(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        crear_producto_local(
            estado,
            codigo_producto="P-LOGOUT-35",
            nombre="Producto descartado en logout",
            categoria_id="CAT01",
            ubicaciones_ids=["U001"],
            ubicacion_principal_id="U001",
            reloj=self.reloj,
        )
        guardar_borrador_formulario_admin(
            estado,
            {"codigo_producto": "P-BORR-FORM", "nombre": "En edición"},
            reloj=self.reloj,
        )
        app_ferms.ejecutar_logout_administrativo_en_sesion(estado, reloj=self.reloj)
        self.assertIsNone(estado.get(CLAVE_ESPACIO_TRABAJO_ADMIN))
        self.assertIsNone(estado.get(CLAVE_FORMULARIO_BORRADOR_ADMIN))
        self.assertFalse(tiene_borrador_pendiente_en_sesion(estado, reloj=self.reloj))
        iniciar_sesion_admin(
            usuario=self.USUARIO_PRUEBA,
            contrasena=self.CONTRASENA_PRUEBA,
            estado=estado,
            fuente_secretos=self.secretos_validos,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )
        self.assertIsNone(obtener_borrador_admin(estado, reloj=self.reloj))

    # ------------------------------------------------------------------
    # 36. Aislamiento de edición local y borradores entre sesiones distintas
    # ------------------------------------------------------------------
    def test_36_aislamiento_edicion_local_y_borradores_entre_sesiones_distintas(
        self,
    ) -> None:
        estado_a, espacio_a = self._crear_sesion_y_espacio_admin()
        crear_producto_local(
            estado_a,
            codigo_producto="P-SESION-A",
            nombre="Producto exclusivo sesión A",
            categoria_id="CAT01",
            ubicaciones_ids=["U001"],
            ubicacion_principal_id="U001",
            reloj=self.reloj,
        )

        estado_b, espacio_b = self._crear_sesion_y_espacio_admin()
        self.assertNotEqual(
            espacio_a.id_sesion_propietaria, espacio_b.id_sesion_propietaria
        )
        codigos_b = [
            p["codigo_producto"]
            for p in consultar_productos_administrativos(estado_b, reloj=self.reloj)
        ]
        self.assertNotIn("P-SESION-A", codigos_b)

        with self.assertRaises(ErrorAutorizacionAdmin):
            editar_producto_local(
                estado_b,
                codigo_producto="MAR001",
                nombre="Intento cruzado entre sesiones",
                espacio_trabajo=espacio_a,
                reloj=self.reloj,
            )

    # ------------------------------------------------------------------
    # 37. Verificación de ausencia de llamadas HTTP PUT, POST, DELETE o PATCH
    # ------------------------------------------------------------------
    def test_37_ausencia_llamadas_escritura_http_put_post_delete_patch_a_github(
        self,
    ) -> None:
        for ruta_modulo in (RUTA_APP, RUTA_ADMIN_PRODUCTOS, RUTA_AUTENTICACION):
            codigo_fuente = ruta_modulo.read_text(encoding="utf-8")
            for metodo_prohibido in ("PUT", "POST", "DELETE", "PATCH"):
                self.assertNotIn(f'"{metodo_prohibido}"', codigo_fuente)
                self.assertNotIn(f"'{metodo_prohibido}'", codigo_fuente)

        estado, _ = self._crear_sesion_y_espacio_admin()
        crear_producto_local(
            estado,
            codigo_producto="P-P10-PREP",
            nombre="Producto preparado para futuro P10",
            categoria_id="CAT01",
            ubicaciones_ids=["U001"],
            ubicacion_principal_id="U001",
            reloj=self.reloj,
        )
        paquete = preparar_paquete_publicacion_futura_p10(estado, reloj=self.reloj)
        self.assertFalse(paquete.confirmado_en_github)
        self.assertTrue(paquete.tiene_cambios_pendientes)
        self.assertEqual(paquete.sha_base_remoto, SHA_REMOTO_SIMULADO)

    # ------------------------------------------------------------------
    # 38. Verificación de que no se modifica 03_Aplicacion/inventario.xlsx oficial
    # ------------------------------------------------------------------
    def test_38_no_se_crea_ni_modifica_archivo_local_inventario_xlsx(self) -> None:
        self.assertTrue(
            RUTA_INVENTARIO_XLSX.is_file(),
            "El archivo oficial 03_Aplicacion/inventario.xlsx debe existir.",
        )
        self.assertEqual(
            RUTA_INVENTARIO_XLSX.read_bytes(),
            BYTES_INVENTARIO_XLSX_INICIAL,
            "El archivo 03_Aplicacion/inventario.xlsx no debe modificarse en el Prompt 09.",
        )
        estado: dict[str, Any] = {}
        app_ferms.inicializar_estado_sesion(estado)
        iniciar_sesion_admin(
            usuario=self.USUARIO_PRUEBA,
            contrasena=self.CONTRASENA_PRUEBA,
            estado=estado,
            fuente_secretos=self.secretos_validos,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )

        def _descargador_inexistente(*args: Any, **kwargs: Any) -> Any:
            raise ErrorArchivoRemotoInexistente("No existe inventario.xlsx en remoto")

        res_inexistente = cargar_inventario_administrativo_en_sesion(
            estado,
            descargador_remoto=_descargador_inexistente,
            inicializar_demo_si_no_existe=False,
            reloj=self.reloj,
        )
        self.assertEqual(
            res_inexistente.estado,
            EstadoInventarioAdmin.INVENTARIO_REMOTO_INEXISTENTE,
        )
        self.assertTrue(res_inexistente.permite_inicializar_demo_local)
        self.assertEqual(RUTA_INVENTARIO_XLSX.read_bytes(), BYTES_INVENTARIO_XLSX_INICIAL)

        res_demo_memoria = cargar_inventario_administrativo_en_sesion(
            estado,
            descargador_remoto=_descargador_inexistente,
            inicializar_demo_si_no_existe=True,
            reloj=self.reloj,
        )
        self.assertEqual(
            res_demo_memoria.estado,
            EstadoInventarioAdmin.INVENTARIO_DISPONIBLE_EDICION_LOCAL,
        )
        self.assertIsNotNone(res_demo_memoria.espacio_trabajo)
        self.assertEqual(RUTA_INVENTARIO_XLSX.read_bytes(), BYTES_INVENTARIO_XLSX_INICIAL)
        inv_oficial = motor_inventario.cargar_inventario_excel(RUTA_INVENTARIO_XLSX)
        self.assertEqual(tuple(inv_oficial.obtener_hojas().keys()), motor_inventario.ORDEN_HOJAS)
        self.assertEqual(len(inv_oficial.productos), 0)
        self.assertEqual(len(inv_oficial.categorias), 3)
        self.assertEqual(len(inv_oficial.ubicaciones), 3)
        self.assertEqual(len(inv_oficial.asignaciones), 0)

        lectura_oficial = ResultadoLecturaInventarioRemoto(
            propietario="JunyMSAI",
            repositorio="FerreteriaMS",
            rama="main",
            ruta_archivo="03_Aplicacion/inventario.xlsx",
            sha_github=SHA_REMOTO_SIMULADO,
            sha256_local="0" * 64,
            tamano_bytes=len(BYTES_INVENTARIO_XLSX_INICIAL or b""),
            inventario=inv_oficial,
            categoria_consulta=CategoriaResultadoConsulta.INVENTARIO_DISPONIBLE,
        )
        cargar_inventario_administrativo_en_sesion(
            estado,
            descargador_remoto=lambda **_: lectura_oficial,
            inicializar_demo_si_no_existe=False,
            reloj=self.reloj,
        )
        cats_oficiales = admin_prod.obtener_catalogo_categorias_admin(
            estado, reloj=self.reloj
        )
        ubics_oficiales = admin_prod.obtener_catalogo_ubicaciones_admin(
            estado, reloj=self.reloj
        )
        self.assertEqual(
            [c["categoria_id"] for c in cats_oficiales],
            ["CAT001", "CAT002", "CAT003"],
        )
        self.assertEqual(
            [u["ubicacion_id"] for u in ubics_oficiales],
            ["U001", "U002", "U003"],
        )
        with patch.dict(
            os.environ, self.secretos_validos, clear=False
        ), patch.object(
            github_inventario,
            "descargar_inventario_remoto",
            return_value=lectura_oficial,
        ):
            at_oficial = AppTest.from_file(str(RUTA_APP), default_timeout=15)
            at_oficial.run()
            self.assertFalse(at_oficial.exception)
            at_oficial.button(key="btn_nav_productos").click()
            at_oficial.run()
            at_oficial.text_input(key="campo_admin_usuario").set_value(self.USUARIO_PRUEBA)
            at_oficial.text_input(key="campo_admin_contrasena").set_value(
                self.CONTRASENA_PRUEBA
            )
            at_oficial.button(key="btn_admin_iniciar_sesion").click()
            at_oficial.run()
            at_oficial.button(key="btn_admin_abrir_crear").click()
            at_oficial.run()
            self.assertFalse(at_oficial.exception)
            opciones_cat_ui = list(
                at_oficial.selectbox(key="campo_admin_crear_categoria").options
            )
            opciones_ubic_ui = list(
                at_oficial.multiselect(key="campo_admin_crear_ubicaciones").options
            )
            opciones_prin_ui = list(
                at_oficial.selectbox(key="campo_admin_crear_ubicacion_principal").options
            )
            self.assertEqual(len(opciones_cat_ui), 3)
            self.assertTrue(all(cid in " ".join(opciones_cat_ui) for cid in ("CAT001", "CAT002", "CAT003")))
            self.assertEqual(len(opciones_ubic_ui), 3)
            self.assertTrue(all(uid in " ".join(opciones_ubic_ui) for uid in ("U001", "U002", "U003")))
            self.assertEqual(len(opciones_prin_ui), 3)
            self.assertTrue(all(uid in " ".join(opciones_prin_ui) for uid in ("U001", "U002", "U003")))
        self.assertEqual(RUTA_INVENTARIO_XLSX.read_bytes(), BYTES_INVENTARIO_XLSX_INICIAL)

    # ------------------------------------------------------------------
    # 39. Ausencia de exposición de secretos, tokens o hashes
    # ------------------------------------------------------------------
    def test_39_ausencia_exposicion_secretos_tokens_hashes_y_verificacion_argon2_real(
        self,
    ) -> None:
        self.patcher_argon2.stop()
        try:
            estado_real: dict[str, Any] = {}
            app_ferms.inicializar_estado_sesion(estado_real)
            res_auth = iniciar_sesion_admin(
                usuario=self.USUARIO_PRUEBA,
                contrasena=self.CONTRASENA_PRUEBA,
                estado=estado_real,
                fuente_secretos=self.secretos_validos,
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
                reloj=self.reloj,
            )
            self.assertTrue(res_auth.autenticado)
        finally:
            self.patcher_argon2.start()

        token_simulado = "ghp_1234567890abcdefghijklmnopqrstuvwx"
        err = ErrorAdministracionInventario(
            f"Fallo con token {token_simulado} y hash {self.HASH_PRUEBA_ARGON2ID}"
        )
        self.assertNotIn(token_simulado, err.mensaje)
        self.assertNotIn("$argon2id$", err.mensaje)
        self.assertNotIn(self.CONTRASENA_PRUEBA, repr(estado_real))
        self.assertNotIn(self.HASH_PRUEBA_ARGON2ID, repr(estado_real))

    # ------------------------------------------------------------------
    # 40. Regresión integrada de Prompts 02..08 e interfaz Streamlit P09
    # ------------------------------------------------------------------
    def test_40_integracion_interfaz_streamlit_p09_y_contratos_prompts_02_a_08(
        self,
    ) -> None:
        lectura_simulada = ResultadoLecturaInventarioRemoto(
            propietario="mock-owner",
            repositorio="FerreteriaMS",
            rama="main",
            ruta_archivo="03_Aplicacion/inventario.xlsx",
            sha_github=SHA_REMOTO_SIMULADO,
            sha256_local="0" * 64,
            tamano_bytes=4096,
            inventario=clonar_inventario_datos(self.inventario_base),
            categoria_consulta=CategoriaResultadoConsulta.INVENTARIO_DISPONIBLE,
        )

        with patch.dict(
            os.environ, self.secretos_validos, clear=False
        ), patch.object(
            github_inventario,
            "descargar_inventario_remoto",
            return_value=lectura_simulada,
        ):
            at = AppTest.from_file(str(RUTA_APP), default_timeout=15)
            at.run()
            self.assertFalse(at.exception)

            at.button(key="btn_nav_productos").click()
            at.run()
            at.text_input(key="campo_admin_usuario").set_value(self.USUARIO_PRUEBA)
            at.text_input(key="campo_admin_contrasena").set_value(
                self.CONTRASENA_PRUEBA
            )
            at.button(key="btn_admin_iniciar_sesion").click()
            at.run()
            self.assertFalse(at.exception)

            at.button(key="btn_admin_abrir_crear").click()
            at.run()
            self.assertFalse(at.exception)

            at.text_input(key="campo_admin_crear_codigo").set_value("0099")
            at.text_input(key="campo_admin_crear_nombre").set_value(
                "Prensa Sargento de Hierro 6 Pulgadas"
            )
            at.text_area(key="campo_admin_crear_descripcion").set_value(
                "Prensa de sujeción pesada para carpintería y herrería."
            )
            at.button(key="btn_admin_confirmar_crear_producto").click()
            at.run()
            self.assertFalse(at.exception)

            mensajes_exito = [s.value for s in at.success]
            self.assertTrue(
                any(
                    admin_prod.MENSAJE_CREACION_LOCAL_EXITOSA in m
                    for m in mensajes_exito
                )
            )

            at.button(key="btn_admin_abrir_editar").click()
            at.run()
            self.assertFalse(at.exception)

            # Cambiar entre dos productos con datos distintos (MAR001 y TOR001) actualiza todos los campos
            at.selectbox(key="campo_admin_editar_selector_codigo").set_value("MAR001")
            at.run()
            self.assertFalse(at.exception)
            self.assertEqual(
                at.text_input(key="campo_admin_editar_nombre").value,
                "Martillo de uña",
            )
            self.assertEqual(
                at.selectbox(key="campo_admin_editar_categoria").value,
                "CAT01",
            )
            self.assertEqual(
                at.text_area(key="campo_admin_editar_descripcion").value,
                "[DEMOSTRATIVO] Martillo para carpintería con mango ergonómico.",
            )
            self.assertEqual(
                list(at.multiselect(key="campo_admin_editar_ubicaciones").value),
                ["U001", "U002"],
            )
            self.assertEqual(
                at.selectbox(key="campo_admin_editar_ubicacion_principal").value,
                "U001",
            )

            at.selectbox(key="campo_admin_editar_selector_codigo").set_value("TOR001")
            at.run()
            self.assertFalse(at.exception)
            self.assertEqual(
                at.text_input(key="campo_admin_editar_nombre").value,
                "Tornillo galvanizado",
            )
            self.assertEqual(
                at.selectbox(key="campo_admin_editar_categoria").value,
                "CAT02",
            )
            self.assertEqual(
                at.text_area(key="campo_admin_editar_descripcion").value,
                "[DEMOSTRATIVO] Tornillo de uso general resistente a la corrosión.",
            )
            self.assertEqual(
                list(at.multiselect(key="campo_admin_editar_ubicaciones").value),
                ["U002"],
            )
            self.assertEqual(
                at.selectbox(key="campo_admin_editar_ubicacion_principal").value,
                "U002",
            )

            # Seleccionar 0099 y editar varios campos sin perder los cambios introducidos entre reruns
            at.selectbox(key="campo_admin_editar_selector_codigo").set_value("0099")
            at.run()
            self.assertFalse(at.exception)
            at.text_input(key="campo_admin_editar_nombre").set_value(
                "Prensa Sargento Reforzada 6 Pulgadas"
            )
            at.run()
            at.text_area(key="campo_admin_editar_descripcion").set_value(
                "Prensa reforzada de hierro nodular."
            )
            at.run()
            self.assertEqual(
                at.text_input(key="campo_admin_editar_nombre").value,
                "Prensa Sargento Reforzada 6 Pulgadas",
            )
            self.assertEqual(
                at.text_area(key="campo_admin_editar_descripcion").value,
                "Prensa reforzada de hierro nodular.",
            )
            at.button(key="btn_admin_confirmar_editar_producto").click()
            at.run()
            self.assertFalse(at.exception)

            mensajes_exito_ed = [s.value for s in at.success]
            self.assertTrue(
                any(
                    admin_prod.MENSAJE_EDICION_LOCAL_EXITOSA in m
                    for m in mensajes_exito_ed
                )
            )
            # Verificar que 0099 se actualizó y TOR001 / MAR001 conservaron intactos sus propios datos
            espacio_ui = at.session_state[CLAVE_ESPACIO_TRABAJO_ADMIN]
            prod_0099 = espacio_ui.inventario_trabajo.obtener_producto_por_codigo("0099")
            self.assertIsNotNone(prod_0099)
            self.assertEqual(prod_0099["nombre"], "Prensa Sargento Reforzada 6 Pulgadas")
            self.assertEqual(prod_0099["descripcion"], "Prensa reforzada de hierro nodular.")
            prod_tor = espacio_ui.inventario_trabajo.obtener_producto_por_codigo("TOR001")
            self.assertIsNotNone(prod_tor)
            self.assertEqual(prod_tor["nombre"], "Tornillo galvanizado")
            self.assertEqual(prod_tor["categoria_id"], "CAT02")
            self.assertEqual(
                prod_tor["ubicacion_principal"]["ubicacion_id"], "U002"
            )

    # ------------------------------------------------------------------
    # 41. Auditoría: Restauración con una operación válida seguida de otra inválida
    # ------------------------------------------------------------------
    def test_41_restauracion_operacion_valida_seguida_de_invalida_es_atomica(
        self,
    ) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        borrador_mixto = {
            "tipo_borrador_p09": "espacio_trabajo_productos",
            "sha_base_remoto": SHA_REMOTO_SIMULADO,
            "origen_remoto_confirmado": True,
            "operaciones_locales": [
                {
                    "tipo_operacion": "CREAR_PRODUCTO",
                    "codigo_producto": "P-AUD-41-OK",
                    "nombre": "Producto Válido Previo al Fallo",
                    "categoria_id": "CAT01",
                    "descripcion": "Primera operación válida del borrador.",
                    "asignaciones": [{"ubicacion_id": "U001", "principal": "Sí"}],
                },
                {
                    "tipo_operacion": "CREAR_PRODUCTO",
                    "codigo_producto": "P-AUD-41-FAIL",
                    "nombre": "Producto Inválido Sin Ubicación Principal",
                    "categoria_id": "CAT01",
                    "descripcion": "Segunda operación inválida que debe abortar todo.",
                    "asignaciones": [{"ubicacion_id": "U002", "principal": "No"}],
                },
            ],
        }
        autenticacion.guardar_borrador_admin(
            estado,
            borrador_mixto,
            tipo_operacion="mantenimiento_productos_p09",
            reloj=self.reloj,
        )

        with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
            restaurar_borrador_en_espacio_trabajo_admin(
                estado,
                inventario_base=self.inventario_base,
                sha_base_remoto=SHA_REMOTO_SIMULADO,
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo, CodigoErrorAdministrativo.SIN_UBICACION_PRINCIPAL
        )

        # Ninguna de las dos operaciones debe haber quedado en el espacio de trabajo activo
        espacio_actual = estado[CLAVE_ESPACIO_TRABAJO_ADMIN]
        self.assertTrue(
            inventarios_son_identicos(
                espacio_actual.inventario_trabajo, self.inventario_base
            )
        )
        self.assertEqual(espacio_actual.codigos_productos_creados, ())
        self.assertEqual(len(espacio_actual.historial_operaciones_locales), 0)
        with self.assertRaises(ErrorValidacionAdministrativa):
            consultar_producto_administrativo_por_codigo(
                estado, "P-AUD-41-OK", reloj=self.reloj
            )

    # ------------------------------------------------------------------
    # 42. Auditoría: Conservación exacta del espacio de trabajo anterior si falla restauración
    # ------------------------------------------------------------------
    def test_42_conservacion_exacta_espacio_trabajo_anterior_cuando_falla_restauracion(
        self,
    ) -> None:
        estado, espacio_previo = self._crear_sesion_y_espacio_admin()
        crear_producto_local(
            estado,
            codigo_producto="P-PREV-42",
            nombre="Producto Preexistente en Espacio Activo",
            categoria_id="CAT01",
            descripcion="Cambio legítimo previo en memoria.",
            ubicaciones_ids=["U001"],
            ubicacion_principal_id="U001",
            reloj=self.reloj,
        )
        editar_producto_local(
            estado,
            codigo_producto="MAR001",
            nombre="Martillo Previo Editado",
            reloj=self.reloj,
        )
        formulario_previo = {
            "modo_formulario": "EDITAR_PRODUCTO",
            "campos": {"codigo_producto": "MAR001", "nombre": "Borrador previo UI"},
        }
        estado[CLAVE_FORMULARIO_BORRADOR_ADMIN] = dict(formulario_previo)

        instantanea_trabajo_previa = clonar_inventario_datos(
            espacio_previo.inventario_trabajo
        )
        creados_previos = espacio_previo.codigos_productos_creados
        editados_previos = espacio_previo.codigos_productos_editados
        historial_previo = espacio_previo.historial_operaciones_locales

        # Inyectar un borrador con la 1ª operación válida y la 2ª con categoría inexistente
        borrador_corrupto = {
            "tipo_borrador_p09": "espacio_trabajo_productos",
            "sha_base_remoto": SHA_REMOTO_SIMULADO,
            "origen_remoto_confirmado": True,
            "formulario_activo": {
                "modo_formulario": "CREAR_PRODUCTO",
                "campos": {"codigo_producto": "P-NO-APLICAR"},
            },
            "operaciones_locales": [
                {
                    "tipo_operacion": "CREAR_PRODUCTO",
                    "codigo_producto": "P-TEMP-42",
                    "nombre": "Producto Temporal",
                    "categoria_id": "CAT01",
                    "descripcion": "Operación 1 válida.",
                    "asignaciones": [{"ubicacion_id": "U001", "principal": "Sí"}],
                },
                {
                    "tipo_operacion": "EDITAR_PRODUCTO",
                    "codigo_producto": "MAR001",
                    "nombre": "Martillo con Categoría Inexistente",
                    "categoria_id": "CAT-999-INVALIDA",
                    "descripcion": "Operación 2 inválida.",
                    "asignaciones": [{"ubicacion_id": "U001", "principal": "Sí"}],
                },
            ],
        }
        autenticacion.guardar_borrador_admin(
            estado,
            borrador_corrupto,
            tipo_operacion="mantenimiento_productos_p09",
            reloj=self.reloj,
        )

        with self.assertRaises(ErrorValidacionAdministrativa) as ctx:
            restaurar_borrador_en_espacio_trabajo_admin(
                estado,
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx.exception.codigo, CodigoErrorAdministrativo.CATEGORIA_INEXISTENTE
        )

        # El objeto de espacio de trabajo y todo su estado previo deben conservarse exactamente igual
        espacio_post = estado[CLAVE_ESPACIO_TRABAJO_ADMIN]
        self.assertIs(espacio_post, espacio_previo)
        self.assertTrue(
            inventarios_son_identicos(
                espacio_post.inventario_trabajo, instantanea_trabajo_previa
            )
        )
        self.assertEqual(espacio_post.codigos_productos_creados, creados_previos)
        self.assertEqual(espacio_post.codigos_productos_editados, editados_previos)
        self.assertEqual(espacio_post.historial_operaciones_locales, historial_previo)
        self.assertEqual(estado[CLAVE_FORMULARIO_BORRADOR_ADMIN], formulario_previo)

    # ------------------------------------------------------------------
    # 43. Auditoría: Conservación del borrador fuente cuando falla la restauración
    # ------------------------------------------------------------------
    def test_43_conservacion_borrador_fuente_cuando_falla_restauracion(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        operaciones_originales = [
            {
                "tipo_operacion": "CREAR_PRODUCTO",
                "codigo_producto": "P-BORR-43-A",
                "nombre": "Producto A en Borrador",
                "categoria_id": "CAT01",
                "descripcion": "Operación válida inicial.",
                "asignaciones": [{"ubicacion_id": "U001", "principal": "Sí"}],
            },
            {
                "tipo_operacion": "CREAR_PRODUCTO",
                "codigo_producto": "P-BORR-43-B",
                "nombre": "Producto B con Ubicación Inexistente",
                "categoria_id": "CAT01",
                "descripcion": "Operación inválida.",
                "asignaciones": [{"ubicacion_id": "UBIC-NO-EXISTE", "principal": "Sí"}],
            },
        ]
        datos_borrador_fuente = {
            "tipo_borrador_p09": "espacio_trabajo_productos",
            "sha_base_remoto": SHA_REMOTO_SIMULADO,
            "origen_remoto_confirmado": True,
            "operaciones_locales": operaciones_originales,
        }
        autenticacion.guardar_borrador_admin(
            estado,
            datos_borrador_fuente,
            tipo_operacion="mantenimiento_productos_p09",
            reloj=self.reloj,
        )

        # Incluso solicitando eliminar_tras_restaurar=True, un fallo NO debe consumir ni alterar el borrador
        with self.assertRaises(ErrorValidacionAdministrativa):
            restaurar_borrador_en_espacio_trabajo_admin(
                estado,
                inventario_base=self.inventario_base,
                sha_base_remoto=SHA_REMOTO_SIMULADO,
                eliminar_tras_restaurar=True,
                reloj=self.reloj,
            )

        self.assertTrue(tiene_borrador_pendiente_en_sesion(estado, reloj=self.reloj))
        borrador_conservado = obtener_borrador_admin(estado, reloj=self.reloj)
        self.assertIsNotNone(borrador_conservado)
        assert borrador_conservado is not None
        self.assertEqual(
            len(borrador_conservado.datos["operaciones_locales"]),
            2,
            "El borrador fuente no debe haber sido sobrescrito por la 1ª operación durante la reproducción.",
        )
        self.assertEqual(
            borrador_conservado.datos["operaciones_locales"][0]["codigo_producto"],
            "P-BORR-43-A",
        )
        self.assertEqual(
            borrador_conservado.datos["operaciones_locales"][1]["codigo_producto"],
            "P-BORR-43-B",
        )

    # ------------------------------------------------------------------
    # 44. Auditoría: Restauración correcta de varias operaciones válidas
    # ------------------------------------------------------------------
    def test_44_restauracion_correcta_multiples_operaciones_validas(self) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        crear_producto_local(
            estado,
            codigo_producto="0044A",
            nombre="Pinza Amperimétrica Digital",
            categoria_id="CAT02",
            descripcion="Medidor eléctrico de corriente alterna.",
            ubicaciones_ids=["U001", "U002"],
            ubicacion_principal_id="U001",
            reloj=self.reloj,
        )
        crear_producto_local(
            estado,
            codigo_producto="0044B",
            nombre="Cinta Aislar Alta Tensión",
            categoria_id="CAT02",
            descripcion="Cinta vulcanizada profesional.",
            ubicaciones_ids=["U003"],
            ubicacion_principal_id="U003",
            reloj=self.reloj,
        )
        editar_producto_local(
            estado,
            codigo_producto="MAR001",
            nombre="Martillo Carpintero 16oz Profesional",
            descripcion="Mango fibra de vidrio.",
            ubicaciones_ids=["U001", "U003"],
            ubicacion_principal_id="U003",
            reloj=self.reloj,
        )
        editar_producto_local(
            estado,
            codigo_producto="0044A",
            nombre="Pinza Amperimétrica True RMS",
            ubicaciones_ids=["U001", "U002"],
            ubicacion_principal_id="U002",
            reloj=self.reloj,
        )

        # Simular expiración por inactividad y posterior reautenticación
        self.reloj.avanzar(TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS + 30)
        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = None
        iniciar_sesion_admin(
            usuario=self.USUARIO_PRUEBA,
            contrasena=self.CONTRASENA_PRUEBA,
            estado=estado,
            fuente_secretos=self.secretos_validos,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )

        borrador_rest = restaurar_borrador_en_espacio_trabajo_admin(
            estado,
            inventario_base=self.inventario_base,
            sha_base_remoto=SHA_REMOTO_SIMULADO,
            eliminar_tras_restaurar=True,
            reloj=self.reloj,
        )
        self.assertIsNotNone(borrador_rest)
        self.assertFalse(tiene_borrador_pendiente_en_sesion(estado, reloj=self.reloj))

        espacio_rest = estado[CLAVE_ESPACIO_TRABAJO_ADMIN]
        self.assertIsNotNone(espacio_rest)
        self.assertEqual(espacio_rest.sha_base_remoto, SHA_REMOTO_SIMULADO)
        self.assertEqual(espacio_rest.codigos_productos_creados, ("0044A", "0044B"))
        self.assertEqual(espacio_rest.codigos_productos_editados, ("MAR001",))
        self.assertEqual(len(espacio_rest.historial_operaciones_locales), 4)

        prod_44a = consultar_producto_administrativo_por_codigo(
            estado, "0044A", reloj=self.reloj
        )
        self.assertEqual(prod_44a["nombre"], "Pinza Amperimétrica True RMS")
        self.assertEqual(prod_44a["ubicacion_principal"]["ubicacion_id"], "U002")

        prod_mar = consultar_producto_administrativo_por_codigo(
            estado, "MAR001", reloj=self.reloj
        )
        self.assertEqual(prod_mar["nombre"], "Martillo Carpintero 16oz Profesional")
        self.assertEqual(prod_mar["ubicacion_principal"]["ubicacion_id"], "U003")

    # ------------------------------------------------------------------
    # 45. Auditoría: Rechazo por exceso de tamaño del borrador tras crear o editar
    # ------------------------------------------------------------------
    def test_45_rechazo_exceso_tamano_borrador_tras_crear_o_editar_revierte_cambios(
        self,
    ) -> None:
        estado, espacio = self._crear_sesion_y_espacio_admin()
        # Realizar una primera creación válida que queda registrada y guardada en borrador
        crear_producto_local(
            estado,
            codigo_producto="P-BASE-45",
            nombre="Producto Base Dentro de Límite",
            categoria_id="CAT01",
            descripcion="Descripción moderada.",
            ubicaciones_ids=["U001"],
            ubicacion_principal_id="U001",
            reloj=self.reloj,
        )
        instantanea_inventario = clonar_inventario_datos(espacio.inventario_trabajo)
        creados_antes = espacio.codigos_productos_creados
        editados_antes = espacio.codigos_productos_editados
        historial_antes = espacio.historial_operaciones_locales
        borrador_antes = obtener_borrador_admin(estado, reloj=self.reloj)
        self.assertIsNotNone(borrador_antes)

        # Reducir temporalmente MAX_TAMANO_BORRADOR_BYTES para forzar el rechazo por tamaño al sincronizar
        with patch.object(autenticacion, "MAX_TAMANO_BORRADOR_BYTES", 250):
            # 1) Intento de creación que supera el límite del borrador
            res_crear = app_ferms.ejecutar_creacion_producto_en_sesion(
                codigo_producto="P-EXCESO-45",
                nombre="Producto que excede el tamaño máximo del borrador del servidor",
                categoria_id="CAT01",
                descripcion="X" * 300,
                ubicaciones_ids=["U001"],
                ubicacion_principal_id="U001",
                estado=estado,
                reloj=self.reloj,
            )
            self.assertFalse(res_crear.exito)
            self.assertEqual(
                estado[CLAVE_MENSAJE_OPERACION_ADMIN]["tipo"],
                "error",
                "No debe emitirse un mensaje de creación exitosa cuando falla guardar_borrador_admin.",
            )

            # 2) Intento de edición que supera el límite del borrador
            res_editar = app_ferms.ejecutar_edicion_producto_en_sesion(
                codigo_producto="MAR001",
                nombre="Martillo editado que excede el tamaño del borrador",
                descripcion="Y" * 300,
                estado=estado,
                reloj=self.reloj,
            )
            self.assertFalse(res_editar.exito)
            self.assertEqual(
                estado[CLAVE_MENSAJE_OPERACION_ADMIN]["tipo"],
                "error",
                "No debe emitirse un mensaje de edición exitosa cuando falla guardar_borrador_admin.",
            )

        # Comprobar que el inventario de trabajo, códigos, historial y borrador previo quedaron intactos
        self.assertTrue(
            inventarios_son_identicos(espacio.inventario_trabajo, instantanea_inventario)
        )
        self.assertEqual(espacio.codigos_productos_creados, creados_antes)
        self.assertEqual(espacio.codigos_productos_editados, editados_antes)
        self.assertEqual(espacio.historial_operaciones_locales, historial_antes)
        with self.assertRaises(ErrorValidacionAdministrativa):
            consultar_producto_administrativo_por_codigo(
                estado, "P-EXCESO-45", reloj=self.reloj
            )
        prod_mar = consultar_producto_administrativo_por_codigo(
            estado, "MAR001", reloj=self.reloj
        )
        self.assertNotEqual(
            prod_mar["nombre"], "Martillo editado que excede el tamaño del borrador"
        )

        borrador_despues = obtener_borrador_admin(estado, reloj=self.reloj)
        self.assertIsNotNone(borrador_despues)
        assert borrador_antes is not None and borrador_despues is not None
        self.assertEqual(borrador_despues.datos, borrador_antes.datos)

    # ------------------------------------------------------------------
    # 46. Auditoría: Ninguna excepción deja registros parcialmente aplicados
    # ------------------------------------------------------------------
    def test_46_excepcion_en_sincronizacion_nunca_deja_registros_parcialmente_aplicados(
        self,
    ) -> None:
        estado, espacio = self._crear_sesion_y_espacio_admin()
        instantanea_inicial = clonar_inventario_datos(espacio.inventario_trabajo)

        with patch.object(
            admin_prod,
            "guardar_borrador_admin",
            side_effect=autenticacion.ErrorSeguridadBorradorAdmin(
                "Fallo simulado de almacenamiento de borrador"
            ),
        ):
            with self.assertRaises(ErrorAdministracionInventario):
                crear_producto_local(
                    estado,
                    codigo_producto="P-NO-QUEDA-46",
                    nombre="Producto Abortado por Excepción",
                    categoria_id="CAT01",
                    ubicaciones_ids=["U001"],
                    ubicacion_principal_id="U001",
                    reloj=self.reloj,
                )
            with self.assertRaises(ErrorAdministracionInventario):
                editar_producto_local(
                    estado,
                    codigo_producto="MAR001",
                    nombre="Edición Abortada",
                    reloj=self.reloj,
                )
            with self.assertRaises(ErrorAdministracionInventario):
                cambiar_ubicacion_principal_local(
                    estado,
                    codigo_producto="MAR001",
                    nueva_ubicacion_principal_id="U002",
                    reloj=self.reloj,
                )
            with self.assertRaises(ErrorAdministracionInventario):
                eliminar_asignacion_ubicacion_local(
                    estado,
                    codigo_producto="MAR001",
                    ubicacion_id="U002",
                    reloj=self.reloj,
                )

        self.assertTrue(
            inventarios_son_identicos(espacio.inventario_trabajo, instantanea_inicial)
        )
        self.assertEqual(espacio.codigos_productos_creados, ())
        self.assertEqual(espacio.codigos_productos_editados, ())
        self.assertEqual(espacio.historial_operaciones_locales, ())
        self.assertFalse(espacio.tiene_cambios_locales_pendientes)

    # ------------------------------------------------------------------
    # 47. Auditoría: Conservación del aislamiento entre sesiones y del SHA base
    # ------------------------------------------------------------------
    def test_47_conservacion_aislamiento_entre_sesiones_y_sha_base_en_restauracion(
        self,
    ) -> None:
        estado_a, espacio_a = self._crear_sesion_y_espacio_admin()
        crear_producto_local(
            estado_a,
            codigo_producto="P-SHA-47",
            nombre="Producto con SHA Original",
            categoria_id="CAT01",
            ubicaciones_ids=["U001"],
            ubicacion_principal_id="U001",
            reloj=self.reloj,
        )
        instantanea_a = clonar_inventario_datos(espacio_a.inventario_trabajo)

        # 1) Rechazo de mezcla de inventarios con SHA base distinto
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx_sha:
            restaurar_borrador_en_espacio_trabajo_admin(
                estado_a,
                inventario_base=self.inventario_base,
                sha_base_remoto="ffff000011112222333344445555666677778888",
                eliminar_tras_restaurar=True,
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx_sha.exception.codigo,
            CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
        )
        # El SHA de referencia del espacio activo y el borrador no deben haberse alterado
        self.assertEqual(espacio_a.sha_base_remoto, SHA_REMOTO_SIMULADO)
        self.assertTrue(
            inventarios_son_identicos(espacio_a.inventario_trabajo, instantanea_a)
        )
        self.assertTrue(tiene_borrador_pendiente_en_sesion(estado_a, reloj=self.reloj))

        # 2) Rechazo si se intenta restaurar cuando el espacio activo en estado pertenece a otra sesión
        estado_b, espacio_b = self._crear_sesion_y_espacio_admin()
        estado_a[CLAVE_ESPACIO_TRABAJO_ADMIN] = espacio_b
        with self.assertRaises(ErrorAutorizacionAdmin):
            restaurar_borrador_en_espacio_trabajo_admin(
                estado_a,
                eliminar_tras_restaurar=True,
                reloj=self.reloj,
            )
        # El borrador de la sesión A sigue intacto
        self.assertTrue(tiene_borrador_pendiente_en_sesion(estado_a, reloj=self.reloj))

    # ------------------------------------------------------------------
    # 48. Integración AppTest: Expiración → Reautenticación → Botón Restaurar en UI
    # ------------------------------------------------------------------
    def test_48_integracion_apptest_flujo_completo_expiracion_reautenticacion_y_boton_restaurar(
        self,
    ) -> None:
        lectura_simulada = ResultadoLecturaInventarioRemoto(
            propietario="mock-owner",
            repositorio="FerreteriaMS",
            rama="main",
            ruta_archivo="03_Aplicacion/inventario.xlsx",
            sha_github=SHA_REMOTO_SIMULADO,
            sha256_local="0" * 64,
            tamano_bytes=4096,
            inventario=clonar_inventario_datos(self.inventario_base),
            categoria_consulta=CategoriaResultadoConsulta.INVENTARIO_DISPONIBLE,
        )

        with patch.dict(
            os.environ, self.secretos_validos, clear=False
        ), patch.object(
            github_inventario,
            "descargar_inventario_remoto",
            return_value=lectura_simulada,
        ):
            at = AppTest.from_file(str(RUTA_APP), default_timeout=15)
            at.run()
            self.assertFalse(at.exception)

            # 1) Navegar a Productos e iniciar sesión administrativa
            at.button(key="btn_nav_productos").click()
            at.run()
            at.text_input(key="campo_admin_usuario").set_value(self.USUARIO_PRUEBA)
            at.text_input(key="campo_admin_contrasena").set_value(
                self.CONTRASENA_PRUEBA
            )
            at.button(key="btn_admin_iniciar_sesion").click()
            at.run()
            self.assertFalse(at.exception)

            # 2) Crear un producto nuevo en memoria
            at.button(key="btn_admin_abrir_crear").click()
            at.run()
            self.assertFalse(at.exception)
            at.text_input(key="campo_admin_crear_codigo").set_value("0098")
            at.text_input(key="campo_admin_crear_nombre").set_value(
                "Cinta Métrica Magnética 8 Metros"
            )
            at.text_area(key="campo_admin_crear_descripcion").set_value(
                "Cinta métrica profesional con freno y punta imantada."
            )
            at.button(key="btn_admin_confirmar_crear_producto").click()
            at.run()
            self.assertFalse(at.exception)

            # 3) Editar un producto existente del catálogo base (MAR001) en memoria
            at.button(key="btn_admin_abrir_editar").click()
            at.run()
            self.assertFalse(at.exception)
            at.selectbox(key="campo_admin_editar_selector_codigo").set_value("MAR001")
            at.run()
            self.assertFalse(at.exception)
            at.text_input(key="campo_admin_editar_nombre").set_value(
                "Martillo Carpintero Recuperado UI"
            )
            at.button(key="btn_admin_confirmar_editar_producto").click()
            at.run()
            self.assertFalse(at.exception)

            # 4) Avanzar reloj más allá de los 15 minutos de inactividad (dentro de los 15 min adicionales del borrador)
            self.reloj.avanzar(TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS + 30)
            at.run()
            self.assertFalse(at.exception)

            # Verificar que app.py limpió el espacio activo y mostró aviso de expiración + borrador retenido
            self.assertIsNone(at.session_state[CLAVE_ESPACIO_TRABAJO_ADMIN])
            warnings_exp = [w.value for w in at.warning]
            infos_exp = [i.value for i in at.info]
            self.assertTrue(
                any(
                    autenticacion.MENSAJE_SESION_EXPIRADA_INACTIVIDAD in w
                    for w in warnings_exp
                )
            )
            self.assertTrue(
                any(
                    autenticacion.MENSAJE_BORRADOR_RETENIDO_REAUTENTICACION in i
                    for i in infos_exp
                )
            )

            # 5) Reautenticarse dentro de la ventana de retención
            at.text_input(key="campo_admin_usuario").set_value(self.USUARIO_PRUEBA)
            at.text_input(key="campo_admin_contrasena").set_value(
                self.CONTRASENA_PRUEBA
            )
            at.button(key="btn_admin_iniciar_sesion").click()
            at.run()
            self.assertFalse(at.exception)

            # 6) Pulsar el botón real «Restaurar borrador temporal» en Streamlit
            at.button(key="btn_admin_restaurar_borrador").click()
            at.run()
            self.assertFalse(at.exception)

            # 7) Verificar reconstrucción del espacio, mensaje de éxito y presentación de productos recuperados
            mensajes_exito = [s.value for s in at.success]
            self.assertTrue(
                any(
                    autenticacion.MENSAJE_BORRADOR_RESTAURADO in m
                    for m in mensajes_exito
                )
            )
            espacio_recuperado = at.session_state[CLAVE_ESPACIO_TRABAJO_ADMIN]
            self.assertIsNotNone(espacio_recuperado)
            self.assertEqual(espacio_recuperado.sha_base_remoto, SHA_REMOTO_SIMULADO)
            self.assertEqual(espacio_recuperado.codigos_productos_creados, ("0098",))
            self.assertEqual(espacio_recuperado.codigos_productos_editados, ("MAR001",))

            warnings_post = [w.value for w in at.warning]
            self.assertTrue(
                any("Cambios locales pendientes de guardar" in w for w in warnings_post)
            )
            markdowns_post = "\n".join(m.value for m in at.markdown)
            self.assertIn("0098", markdowns_post)
            self.assertIn("Cinta Métrica Magnética 8 Metros", markdowns_post)
            self.assertIn("Martillo Carpintero Recuperado UI", markdowns_post)

    # ------------------------------------------------------------------
    # 49. Restauración sin espacio activo: errores GitHub, inexistente y conflicto SHA
    # ------------------------------------------------------------------
    def test_49_restauracion_sin_espacio_activo_distingue_errores_github_inexistente_y_conflicto_sha(
        self,
    ) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        crear_producto_local(
            estado,
            codigo_producto="0049",
            nombre="Llave Stilson 14 Pulgadas",
            categoria_id="CAT01",
            descripcion="Llave para tubería pesada.",
            ubicaciones_ids=["U001"],
            ubicacion_principal_id="U001",
            reloj=self.reloj,
        )

        # Simular expiración (limpieza del espacio activo en memoria) y reautenticación
        self.reloj.avanzar(TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS + 15)
        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = None
        res_relogin = iniciar_sesion_admin(
            usuario=self.USUARIO_PRUEBA,
            contrasena=self.CONTRASENA_PRUEBA,
            estado=estado,
            fuente_secretos=self.secretos_validos,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )
        self.assertTrue(res_relogin.autenticado)

        # Caso A: Error de conexión a GitHub al recuperar inventario base
        def _descargador_fallo_red(*_args: Any, **_kwargs: Any) -> Any:
            raise github_inventario.ErrorLecturaGitHub(
                "Fallo de conexión simulado al restaurar borrador."
            )

        with self.assertRaises(ErrorAdministracionInventario) as ctx_red:
            restaurar_borrador_en_espacio_trabajo_admin(
                estado,
                descargador_remoto=_descargador_fallo_red,
                eliminar_tras_restaurar=True,
                reloj=self.reloj,
            )
        self.assertEqual(ctx_red.exception.estado, EstadoInventarioAdmin.ERROR_CONEXION)
        self.assertIsNone(estado[CLAVE_ESPACIO_TRABAJO_ADMIN])
        self.assertTrue(tiene_borrador_pendiente_en_sesion(estado, reloj=self.reloj))

        # Caso B: Inventario remoto inexistente (nunca debe sustituirse por inventario demostrativo)
        def _descargador_inexistente(*_args: Any, **_kwargs: Any) -> Any:
            raise ErrorArchivoRemotoInexistente("No existe inventario.xlsx en GitHub.")

        with self.assertRaises(ErrorAdministracionInventario) as ctx_inex:
            restaurar_borrador_en_espacio_trabajo_admin(
                estado,
                descargador_remoto=_descargador_inexistente,
                eliminar_tras_restaurar=True,
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx_inex.exception.estado,
            EstadoInventarioAdmin.INVENTARIO_REMOTO_INEXISTENTE,
        )
        self.assertIsNone(estado[CLAVE_ESPACIO_TRABAJO_ADMIN])
        self.assertTrue(tiene_borrador_pendiente_en_sesion(estado, reloj=self.reloj))

        # Caso C: Conflicto de SHA (el inventario en GitHub cambió respecto al SHA del borrador)
        def _descargador_sha_distinto(
            *_args: Any, **_kwargs: Any
        ) -> ResultadoLecturaInventarioRemoto:
            return ResultadoLecturaInventarioRemoto(
                propietario="mock-owner",
                repositorio="FerreteriaMS",
                rama="main",
                ruta_archivo="03_Aplicacion/inventario.xlsx",
                sha_github="9999888877776666555544443333222211110000",
                sha256_local="0" * 64,
                tamano_bytes=4096,
                inventario=clonar_inventario_datos(self.inventario_base),
                categoria_consulta=CategoriaResultadoConsulta.INVENTARIO_DISPONIBLE,
            )

        with self.assertRaises(ErrorValidacionAdministrativa) as ctx_sha:
            restaurar_borrador_en_espacio_trabajo_admin(
                estado,
                descargador_remoto=_descargador_sha_distinto,
                eliminar_tras_restaurar=True,
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx_sha.exception.codigo,
            CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO,
        )
        self.assertIsNone(estado[CLAVE_ESPACIO_TRABAJO_ADMIN])
        self.assertTrue(tiene_borrador_pendiente_en_sesion(estado, reloj=self.reloj))

        # Caso D: Descarga remota exitosa con el mismo SHA original reconstruye el espacio
        def _descargador_sha_correcto(
            *_args: Any, **_kwargs: Any
        ) -> ResultadoLecturaInventarioRemoto:
            return ResultadoLecturaInventarioRemoto(
                propietario="mock-owner",
                repositorio="FerreteriaMS",
                rama="main",
                ruta_archivo="03_Aplicacion/inventario.xlsx",
                sha_github=SHA_REMOTO_SIMULADO,
                sha256_local="0" * 64,
                tamano_bytes=4096,
                inventario=clonar_inventario_datos(self.inventario_base),
                categoria_consulta=CategoriaResultadoConsulta.INVENTARIO_DISPONIBLE,
            )

        borrador_ok = restaurar_borrador_en_espacio_trabajo_admin(
            estado,
            descargador_remoto=_descargador_sha_correcto,
            reloj=self.reloj,
        )
        self.assertIsNotNone(borrador_ok)
        espacio_rest = estado[CLAVE_ESPACIO_TRABAJO_ADMIN]
        self.assertIsNotNone(espacio_rest)
        self.assertEqual(espacio_rest.sha_base_remoto, SHA_REMOTO_SIMULADO)
        self.assertTrue(espacio_rest.origen_remoto_confirmado)
        prod_0049 = consultar_producto_administrativo_por_codigo(
            estado, "0049", reloj=self.reloj
        )
        self.assertEqual(prod_0049["nombre"], "Llave Stilson 14 Pulgadas")

    # ------------------------------------------------------------------
    # 50. Preparación y operaciones fallidas no renuevan indebidamente la sesión
    # ------------------------------------------------------------------
    def test_50_operaciones_preparacion_y_fallos_no_renuevan_indebidamente_la_sesion(
        self,
    ) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        t_inicio = self.reloj()

        # Avanzar 10 minutos (quedan 5 minutos de sesión)
        self.reloj.avanzar(600)

        # 1) Creación inválida no debe renovar ultima_actividad_epoch
        with self.assertRaises(ErrorValidacionAdministrativa):
            crear_producto_local(
                estado,
                codigo_producto="",
                nombre="Producto Inválido",
                categoria_id="CAT01",
                ubicaciones_ids=["U001"],
                ubicacion_principal_id="U001",
                reloj=self.reloj,
            )
        self.assertEqual(
            estado[CLAVE_SESION_ADMIN].ultima_actividad_epoch,
            t_inicio,
        )

        # 2) Edición inválida no debe renovar ultima_actividad_epoch
        with self.assertRaises(ErrorValidacionAdministrativa):
            editar_producto_local(
                estado,
                codigo_producto="NO-EXISTE",
                nombre="Nombre Inválido",
                reloj=self.reloj,
            )
        self.assertEqual(
            estado[CLAVE_SESION_ADMIN].ultima_actividad_epoch,
            t_inicio,
        )

        # 3) Restauración fallida de borrador no debe renovar ultima_actividad_epoch
        autenticacion.guardar_borrador_admin(
            estado,
            {
                "tipo_borrador_p09": "espacio_trabajo_productos",
                "sha_base_remoto": SHA_REMOTO_SIMULADO,
                "origen_remoto_confirmado": True,
                "operaciones_locales": [
                    {
                        "tipo_operacion": "CREAR_PRODUCTO",
                        "codigo_producto": "P-OK-50",
                        "nombre": "Operación 1 Válida de Preparación",
                        "categoria_id": "CAT01",
                        "descripcion": "No debe renovar sesión real si falla la 2ª.",
                        "asignaciones": [{"ubicacion_id": "U001", "principal": "Sí"}],
                    },
                    {
                        "tipo_operacion": "CREAR_PRODUCTO",
                        "codigo_producto": "P-FAIL-50",
                        "nombre": "Operación 2 Inválida",
                        "categoria_id": "CAT-INEXISTENTE",
                        "descripcion": "Falla en preparación.",
                        "asignaciones": [{"ubicacion_id": "U001", "principal": "Sí"}],
                    },
                ],
            },
            reloj=lambda: t_inicio,
        )
        with self.assertRaises(ErrorValidacionAdministrativa):
            restaurar_borrador_en_espacio_trabajo_admin(
                estado,
                reloj=self.reloj,
            )
        self.assertEqual(
            estado[CLAVE_SESION_ADMIN].ultima_actividad_epoch,
            t_inicio,
            "La reproducción en preparación no debe renovar la actividad de la sesión si la restauración falla.",
        )

        # 4) Avanzar los 5 minutos + 1 segundo restantes desde t_inicio: la sesión debe expirar autoritativamente
        self.reloj.avanzar(TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS - 600 + 1)
        with self.assertRaises(ErrorAutorizacionAdmin) as ctx_exp:
            crear_producto_local(
                estado,
                codigo_producto="0050",
                nombre="Intento Tras Expiración Autoritativa",
                categoria_id="CAT01",
                ubicaciones_ids=["U001"],
                ubicacion_principal_id="U001",
                reloj=self.reloj,
            )
        self.assertEqual(
            ctx_exp.exception.codigo,
            CodigoResultadoAutenticacion.SESION_EXPIRADA,
        )

    # ------------------------------------------------------------------
    # 51. Configuración GitHub predeterminada e inyectada en ruta de restauración
    # ------------------------------------------------------------------
    def test_51_configuracion_github_predeterminada_e_inyectada_en_ruta_restauracion(
        self,
    ) -> None:
        estado, _ = self._crear_sesion_y_espacio_admin()
        crear_producto_local(
            estado,
            codigo_producto="0051",
            nombre="Arco de Sierra Profesional 12 Pulgadas",
            categoria_id="CAT01",
            descripcion="Arco metálico ergonómico para corte de metal.",
            ubicaciones_ids=["U001"],
            ubicacion_principal_id="U001",
            reloj=self.reloj,
        )

        # Simular expiración (limpieza del espacio activo) y reautenticación
        self.reloj.avanzar(TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS + 10)
        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = None
        res_relogin = iniciar_sesion_admin(
            usuario=self.USUARIO_PRUEBA,
            contrasena=self.CONTRASENA_PRUEBA,
            estado=estado,
            fuente_secretos=self.secretos_validos,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            reloj=self.reloj,
        )
        self.assertTrue(res_relogin.autenticado)

        configs_recibidas: list[Any] = []

        def _lector_espia(*, config: Any = None, **_kwargs: Any) -> ResultadoLecturaInventarioRemoto:
            configs_recibidas.append(config)
            return ResultadoLecturaInventarioRemoto(
                propietario="mock-owner",
                repositorio="FerreteriaMS",
                rama="main",
                ruta_archivo="03_Aplicacion/inventario.xlsx",
                sha_github=SHA_REMOTO_SIMULADO,
                sha256_local="0" * 64,
                tamano_bytes=4096,
                inventario=clonar_inventario_datos(self.inventario_base),
                categoria_consulta=CategoriaResultadoConsulta.INVENTARIO_DISPONIBLE,
            )

        # 1) Llamada por defecto (sin config_github ni descargador_remoto): nunca debe pasar config=None
        with patch.object(
            github_inventario,
            "descargar_inventario_remoto",
            side_effect=_lector_espia,
        ):
            borrador_defecto = app_ferms.ejecutar_restauracion_borrador_en_sesion(
                estado,
                reloj=self.reloj,
            )
        self.assertIsNotNone(borrador_defecto)
        self.assertEqual(len(configs_recibidas), 1)
        self.assertIsNotNone(configs_recibidas[0])
        self.assertIsInstance(
            configs_recibidas[0],
            github_inventario.ConfiguracionRepositorioGitHub,
        )
        self.assertEqual(configs_recibidas[0], github_inventario.CONFIGURACION_POR_DEFECTO)

        # 2) Llamada con config_github=None explícito: también debe usar CONFIGURACION_POR_DEFECTO
        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = None
        borrador_none = app_ferms.ejecutar_restauracion_borrador_en_sesion(
            estado,
            config_github=None,
            descargador_remoto=_lector_espia,
            reloj=self.reloj,
        )
        self.assertIsNotNone(borrador_none)
        self.assertEqual(len(configs_recibidas), 2)
        self.assertEqual(configs_recibidas[1], github_inventario.CONFIGURACION_POR_DEFECTO)

        # 3) Llamada con ConfiguracionRepositorioGitHub personalizada y descargador inyectado
        config_personalizada = github_inventario.ConfiguracionRepositorioGitHub(
            propietario="org-pruebas",
            repositorio="FerreteriaMS-Test",
            rama="main",
            ruta_archivo="03_Aplicacion/inventario.xlsx",
        )
        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = None
        borrador_custom = app_ferms.ejecutar_restauracion_borrador_en_sesion(
            estado,
            config_github=config_personalizada,
            descargador_remoto=_lector_espia,
            reloj=self.reloj,
        )
        self.assertIsNotNone(borrador_custom)
        self.assertEqual(len(configs_recibidas), 3)
        self.assertEqual(configs_recibidas[2], config_personalizada)


if __name__ == "__main__":
    unittest.main()
