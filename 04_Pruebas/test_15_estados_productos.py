"""Pruebas focalizadas para FERMS-FINAL-P15: Estados activo/inactivo de productos.

Cubre exclusivamente los escenarios requeridos en 02_Prompts/15_Estados_Productos.md:
1. Compatibilidad con inventario v0 (Productos sin columna Activo -> Activo = 'Sí').
2. Desactivación de producto conservando datos y asignaciones (CA-F-007).
3. Exclusión de productos inactivos en búsqueda pública, detalle público y catálogo activo (RF-F-008, CA-F-007).
4. Reactivación de producto válido y rechazo ante inconsistencias de integridad (CA-F-007).
5. Visibilidad administrativa de productos activos e inactivos con indicador de estado.
6. Protección de ubicaciones asociadas a productos inactivos contra edición física y desactivación.
7. Persistencia simulada en GitHub con control SHA, round-trip Excel de 4 hojas y restauración de borradores (CA-F-008, CA-F-009).
8. Seguridad básica administrativa (exigencia de sesión válida en escritorio y confirmación).
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
import unittest
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_APLICACION = RAIZ_PROYECTO / "03_Aplicacion"
if str(RUTA_APLICACION) not in sys.path:
    sys.path.insert(0, str(RUTA_APLICACION))

import app  # noqa: E402
import autenticacion  # noqa: E402
import github_inventario  # noqa: E402
from administracion_productos import (  # noqa: E402
    CLAVE_ESPACIO_TRABAJO_ADMIN,
    CodigoErrorAdministrativo,
    ErrorValidacionAdministrativa,
    cambiar_estado_producto_local,
    consultar_producto_administrativo_por_codigo,
    consultar_productos_administrativos,
    consultar_ubicacion_administrativa_por_id,
    crear_producto_local,
    desactivar_producto_local,
    desactivar_ubicacion_local,
    editar_producto_local,
    editar_ubicacion_local,
    inicializar_espacio_trabajo_desde_inventario,
    reactivar_producto_local,
)
from autenticacion import (  # noqa: E402
    ContextoDispositivo,
    ErrorAutorizacionAdmin,
)
from busqueda import (  # noqa: E402
    EstadoBusqueda,
    EstadoDetalleProducto,
    buscar_productos_por_nombre,
    consultar_detalle_producto,
    ejecutar_busqueda_productos,
    obtener_catalogo_productos_activos,
)
from github_inventario import (  # noqa: E402
    RespuestaHTTPGitHub,
    ResultadoExistenciaRemota,
)
from inventario import (  # noqa: E402
    ESQUEMA_HOJAS,
    HOJA_ASIGNACIONES,
    HOJA_CATEGORIAS,
    HOJA_PRODUCTOS,
    HOJA_UBICACIONES,
    ORDEN_HOJAS,
    CodigoErrorInventario,
    ErrorValorActivoInvalido,
    cargar_inventario_excel,
    construir_inventario_datos,
    obtener_productos_activos_estructurados,
    validar_inventario,
)
from persistencia_github import (  # noqa: E402
    EstadoResultadoPublicacionGitHub,
    serializar_y_verificar_inventario_xlsx,
)


def _crear_hojas_v0_sin_activo_en_productos() -> dict[str, pd.DataFrame]:
    """Construye las cuatro hojas con formato v0 (sin columna Activo en Productos ni en Ubicaciones)."""
    df_categorias = pd.DataFrame(
        [
            {"Categoria_ID": "CAT01", "Nombre_Categoria": "Herramientas Manuales"},
            {"Categoria_ID": "CAT02", "Nombre_Categoria": "Fijaciones y Tornillería"},
        ]
    )
    df_ubicaciones = pd.DataFrame(
        [
            {"Ubicacion_ID": "U001", "Rack": "R01", "Columna": "C01", "Nivel": "N01", "Posicion": "P01"},
            {"Ubicacion_ID": "U002", "Rack": "R01", "Columna": "C01", "Nivel": "N01", "Posicion": "P02"},
            {"Ubicacion_ID": "U003", "Rack": "R02", "Columna": "C01", "Nivel": "N01", "Posicion": "P01"},
        ]
    )
    df_productos = pd.DataFrame(
        [
            {
                "Codigo_Producto": "0010",
                "Nombre": "Martillo de uña profesional",
                "Categoria_ID": "CAT01",
                "Descripcion": "Martillo de acero forjado con mango ergonómico.",
            },
            {
                "Codigo_Producto": "0020",
                "Nombre": "Martillo de goma",
                "Categoria_ID": "CAT01",
                "Descripcion": "Mazo de goma para acabados.",
            },
            {
                "Codigo_Producto": "0030",
                "Nombre": "Tornillo drywall 1 pulgada",
                "Categoria_ID": "CAT02",
                "Descripcion": "Tornillo fosfatado punta fina.",
            },
        ]
    )
    df_asignaciones = pd.DataFrame(
        [
            {"Codigo_Producto": "0010", "Ubicacion_ID": "U001", "Principal": "Sí"},
            {"Codigo_Producto": "0010", "Ubicacion_ID": "U002", "Principal": "No"},
            {"Codigo_Producto": "0020", "Ubicacion_ID": "U002", "Principal": "Sí"},
            {"Codigo_Producto": "0030", "Ubicacion_ID": "U003", "Principal": "Sí"},
        ]
    )
    return {
        HOJA_PRODUCTOS: df_productos,
        HOJA_CATEGORIAS: df_categorias,
        HOJA_UBICACIONES: df_ubicaciones,
        HOJA_ASIGNACIONES: df_asignaciones,
    }


_USUARIO_ADMIN_PRUEBA = "admin_ferreteria"
_CLAVE_ADMIN_PRUEBA = "ClaveSeguraP15!2026"
_HASH_ADMIN_PRUEBA = autenticacion.generar_hash_contrasena(_CLAVE_ADMIN_PRUEBA)
_SECRETOS_ADMIN_PRUEBA = {
    "admin": {
        "username": _USUARIO_ADMIN_PRUEBA,
        "password_hash": _HASH_ADMIN_PRUEBA,
    }
}


def _crear_estado_sesion_admin_autorizado(
    *,
    sha_remoto: str = "b" * 40,
) -> dict[str, Any]:
    """Inicializa una sesión administrativa autenticada en escritorio con inventario cargado."""
    autenticacion.reiniciar_estado_seguridad_servidor()
    estado: dict[str, Any] = {}
    app.inicializar_estado_sesion(estado)
    res_login = app.ejecutar_login_administrativo_en_sesion(
        _USUARIO_ADMIN_PRUEBA,
        _CLAVE_ADMIN_PRUEBA,
        estado=estado,
        fuente_secretos=_SECRETOS_ADMIN_PRUEBA,
        contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
    )
    assert res_login.autenticado, f"Fallo al autenticar en prueba: {res_login}"
    inv = construir_inventario_datos(_crear_hojas_v0_sin_activo_en_productos())
    espacio = inicializar_espacio_trabajo_desde_inventario(
        estado,
        inv,
        sha_base_remoto=sha_remoto,
        origen_remoto_confirmado=True,
        contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
    )
    estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = espacio
    return estado


class TestEstadosProductosP15(unittest.TestCase):
    """Suite focalizada para FERMS-FINAL-P15."""

    def test_01_compatibilidad_retroactiva_inventario_v0_y_validacion_activo(self) -> None:
        """1. Compatibilidad con inventario v0: carga Productos sin Activo y asigna Activo='Sí'."""
        hojas_v0 = _crear_hojas_v0_sin_activo_en_productos()
        self.assertNotIn("Activo", hojas_v0[HOJA_PRODUCTOS].columns)

        inv = construir_inventario_datos(hojas_v0)
        self.assertIn("Activo", inv.productos.columns)
        self.assertEqual(
            list(inv.productos.columns),
            list(ESQUEMA_HOJAS[HOJA_PRODUCTOS]),
        )
        self.assertEqual(inv.productos["Activo"].tolist(), ["Sí", "Sí", "Sí"])

        # Nuevos productos creados en administración tienen Activo='Sí' por defecto
        estado = _crear_estado_sesion_admin_autorizado()
        res_crear = crear_producto_local(
            estado,
            codigo_producto="0040",
            nombre="Alicate universal 8 pulgadas",
            categoria_id="CAT01",
            descripcion="Alicate aislado.",
            ubicaciones_ids=["U001"],
            ubicacion_principal_id="U001",
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(res_crear.exito)
        self.assertEqual(res_crear.activo, "Sí")
        self.assertTrue(res_crear.es_activo)

        # Rechaza valores inválidos en columna Activo de Productos
        hojas_invalidas = _crear_hojas_v0_sin_activo_en_productos()
        hojas_invalidas[HOJA_PRODUCTOS]["Activo"] = ["Sí", "Quizás", "No"]
        res_val = validar_inventario(hojas_invalidas, lanzar_excepcion=False)
        self.assertFalse(res_val.es_valido)
        self.assertIn(CodigoErrorInventario.VALOR_ACTIVO_INVALIDO, res_val.codigos_error)
        with self.assertRaises(ErrorValorActivoInvalido):
            construir_inventario_datos(hojas_invalidas)

    def test_02_desactivacion_producto_conserva_datos_y_asignaciones(self) -> None:
        """2. Desactivación de producto: cambia Activo='No' conservando todos sus datos y asignaciones."""
        estado = _crear_estado_sesion_admin_autorizado()

        res_des = desactivar_producto_local(
            estado,
            codigo_producto="0010",
            confirmado=True,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(res_des.exito)
        self.assertEqual(res_des.codigo_producto, "0010")
        self.assertEqual(res_des.activo, "No")
        self.assertFalse(res_des.es_activo)

        # Verificar que todos los datos y ubicaciones asignadas del producto 0010 se conservan
        prod_admin = consultar_producto_administrativo_por_codigo(
            estado,
            "0010",
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertEqual(prod_admin["codigo_producto"], "0010")
        self.assertEqual(prod_admin["nombre"], "Martillo de uña profesional")
        self.assertEqual(prod_admin["categoria_id"], "CAT01")
        self.assertEqual(
            prod_admin["descripcion"],
            "Martillo de acero forjado con mango ergonómico.",
        )
        self.assertEqual(prod_admin["activo"], "No")
        self.assertFalse(prod_admin["es_activo"])
        self.assertEqual(prod_admin["ubicacion_principal"]["ubicacion_id"], "U001")
        self.assertEqual(len(prod_admin["ubicaciones_secundarias"]), 1)
        self.assertEqual(
            prod_admin["ubicaciones_secundarias"][0]["ubicacion_id"], "U002"
        )

        # Intentar desactivar nuevamente un producto ya inactivo es rechazado
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx_dup:
            desactivar_producto_local(
                estado,
                codigo_producto="0010",
                confirmado=True,
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            )
        self.assertEqual(
            ctx_dup.exception.codigo,
            CodigoErrorAdministrativo.PRODUCTO_YA_INACTIVO,
        )

    def test_03_exclusion_productos_inactivos_busqueda_detalle_y_catalogo_activo(self) -> None:
        """3. Exclusión en búsqueda pública: inactivo excluido de resultados, detalle público y catálogo activo."""
        estado = _crear_estado_sesion_admin_autorizado()
        desactivar_producto_local(
            estado,
            codigo_producto="0010",
            confirmado=True,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        inv_trabajo = estado[CLAVE_ESPACIO_TRABAJO_ADMIN].inventario_trabajo

        # Búsqueda por "Martillo" solo devuelve el producto activo "0020" ("Martillo de goma")
        coincidencias = buscar_productos_por_nombre(inv_trabajo, "Martillo")
        codigos_encontrados = [p.codigo_producto for p in coincidencias]
        self.assertEqual(codigos_encontrados, ["0020"])
        self.assertNotIn("0010", codigos_encontrados)

        # Búsqueda específica del producto inactivo devuelve SIN_RESULTADOS
        res_busq_inactivo = ejecutar_busqueda_productos(
            inv_trabajo, "Martillo de uña profesional"
        )
        self.assertEqual(res_busq_inactivo.estado, EstadoBusqueda.SIN_RESULTADOS)
        self.assertEqual(res_busq_inactivo.total_resultados, 0)

        # Consulta de detalle público para el producto inactivo devuelve PRODUCTO_NO_DISPONIBLE
        res_detalle_inactivo = consultar_detalle_producto(inv_trabajo, "0010")
        self.assertEqual(
            res_detalle_inactivo.estado,
            EstadoDetalleProducto.PRODUCTO_NO_DISPONIBLE,
        )
        self.assertIsNone(res_detalle_inactivo.detalle)

        # Consulta de detalle público para producto activo sigue funcionando normalmente
        res_detalle_activo = consultar_detalle_producto(inv_trabajo, "0020")
        self.assertEqual(
            res_detalle_activo.estado,
            EstadoDetalleProducto.DETALLE_DISPONIBLE,
        )
        self.assertEqual(res_detalle_activo.detalle.codigo_producto, "0020")

        # Catálogo de productos activos (para público y futuro Gemini Bloque 2) excluye inactivos
        catalogo_activo = obtener_catalogo_productos_activos(inv_trabajo)
        self.assertEqual(
            [p["codigo_producto"] for p in catalogo_activo],
            ["0020", "0030"],
        )
        self.assertEqual(
            [p["codigo_producto"] for p in obtener_productos_activos_estructurados(inv_trabajo)],
            ["0020", "0030"],
        )

    def test_04_reactivacion_producto_valido_y_rechazo_ante_inconsistencias(self) -> None:
        """4. Reactivación de producto: reactiva válido; vuelve a búsqueda; rechaza si hay asignaciones rotas."""
        estado = _crear_estado_sesion_admin_autorizado()
        desactivar_producto_local(
            estado,
            codigo_producto="0010",
            confirmado=True,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )

        # Reactivar producto válido
        res_reac = reactivar_producto_local(
            estado,
            codigo_producto="0010",
            confirmado=True,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(res_reac.exito)
        self.assertEqual(res_reac.activo, "Sí")
        self.assertTrue(res_reac.es_activo)

        inv_trabajo = estado[CLAVE_ESPACIO_TRABAJO_ADMIN].inventario_trabajo
        coincidencias = buscar_productos_por_nombre(inv_trabajo, "Martillo")
        self.assertEqual([p.codigo_producto for p in coincidencias], ["0020", "0010"])
        res_det = consultar_detalle_producto(inv_trabajo, "0010")
        self.assertEqual(res_det.estado, EstadoDetalleProducto.DETALLE_DISPONIBLE)

        # Rechazar reactivación de un producto que ya está activo
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx_ya_act:
            reactivar_producto_local(
                estado,
                codigo_producto="0010",
                confirmado=True,
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            )
        self.assertEqual(
            ctx_ya_act.exception.codigo,
            CodigoErrorAdministrativo.PRODUCTO_YA_ACTIVO,
        )

        # Desactivar nuevamente y simular inconsistencias para comprobar el rechazo en reactivación
        desactivar_producto_local(
            estado,
            codigo_producto="0010",
            confirmado=True,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        espacio = estado[CLAVE_ESPACIO_TRABAJO_ADMIN]

        # Caso A: Sin ubicación principal
        df_asig_orig = espacio.inventario_trabajo.asignaciones.copy(deep=True)
        espacio.inventario_trabajo.asignaciones.loc[
            espacio.inventario_trabajo.asignaciones["Codigo_Producto"] == "0010",
            "Principal",
        ] = "No"
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx_sin_prin:
            reactivar_producto_local(
                estado,
                codigo_producto="0010",
                confirmado=True,
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            )
        self.assertEqual(
            ctx_sin_prin.exception.codigo,
            CodigoErrorAdministrativo.SIN_UBICACION_PRINCIPAL,
        )
        espacio.inventario_trabajo.asignaciones = df_asig_orig.copy(deep=True)

        # Caso B: Con ubicación inactiva asignada
        df_ubic_orig = espacio.inventario_trabajo.ubicaciones.copy(deep=True)
        espacio.inventario_trabajo.ubicaciones.loc[
            espacio.inventario_trabajo.ubicaciones["Ubicacion_ID"] == "U001",
            "Activo",
        ] = "No"
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx_ubic_inact:
            reactivar_producto_local(
                estado,
                codigo_producto="0010",
                confirmado=True,
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            )
        self.assertEqual(
            ctx_ubic_inact.exception.codigo,
            CodigoErrorAdministrativo.UBICACION_INACTIVA,
        )
        espacio.inventario_trabajo.ubicaciones = df_ubic_orig.copy(deep=True)

        # Caso C: Sin asignaciones de ubicación
        espacio.inventario_trabajo.asignaciones = df_asig_orig.loc[
            df_asig_orig["Codigo_Producto"] != "0010"
        ].copy(deep=True)
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx_sin_ubic:
            reactivar_producto_local(
                estado,
                codigo_producto="0010",
                confirmado=True,
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            )
        self.assertEqual(
            ctx_sin_ubic.exception.codigo,
            CodigoErrorAdministrativo.PRODUCTO_SIN_UBICACION,
        )
        espacio.inventario_trabajo.asignaciones = df_asig_orig.copy(deep=True)

    def test_05_visibilidad_administrativa_activos_e_inactivos(self) -> None:
        """5. Visibilidad administrativa: muestra activos e inactivos con indicación clara de estado."""
        estado = _crear_estado_sesion_admin_autorizado()
        app.ejecutar_desactivacion_producto_en_sesion(
            codigo_producto="0020",
            confirmado=True,
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )

        listado_admin = consultar_productos_administrativos(
            estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertEqual(len(listado_admin), 3)
        mapa = {p["codigo_producto"]: p for p in listado_admin}

        self.assertTrue(mapa["0010"]["es_activo"])
        self.assertEqual(mapa["0010"]["estado_producto_texto"], "Activo")

        self.assertFalse(mapa["0020"]["es_activo"])
        self.assertEqual(mapa["0020"]["activo"], "No")
        self.assertEqual(mapa["0020"]["estado_producto_texto"], "Inactivo")
        self.assertTrue(mapa["0020"]["es_desactivado_local"])
        self.assertIn("Desactivado", mapa["0020"]["estado_registro_texto"])

        # Permite editar un producto inactivo conservando su estado Inactivo
        editar_producto_local(
            estado,
            codigo_producto="0020",
            descripcion="Mazo de goma actualizado mientras está inactivo.",
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        prod_0020 = consultar_producto_administrativo_por_codigo(
            estado, "0020", contexto_dispositivo=ContextoDispositivo.ESCRITORIO
        )
        self.assertFalse(prod_0020["es_activo"])
        self.assertEqual(
            prod_0020["descripcion"],
            "Mazo de goma actualizado mientras está inactivo.",
        )

    def test_06_proteccion_ubicaciones_asociadas_a_productos_inactivos(self) -> None:
        """6. Relación con ubicaciones: ubicación asociada a producto inactivo no puede editarse ni desactivarse."""
        estado = _crear_estado_sesion_admin_autorizado()
        # U001 está asociada únicamente al producto "0010"
        desactivar_producto_local(
            estado,
            codigo_producto="0010",
            confirmado=True,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )

        info_u001 = consultar_ubicacion_administrativa_por_id(
            estado,
            "U001",
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(info_u001["tiene_productos_asociados"])
        self.assertIn("0010", info_u001["codigos_productos_asociados"])
        self.assertFalse(info_u001["permite_editar_fisicamente"])
        self.assertFalse(info_u001["permite_desactivar"])

        with self.assertRaises(ErrorValidacionAdministrativa) as ctx_ed:
            editar_ubicacion_local(
                estado,
                ubicacion_id="U001",
                rack="R99",
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            )
        self.assertEqual(
            ctx_ed.exception.codigo,
            CodigoErrorAdministrativo.UBICACION_CON_PRODUCTOS_ASOCIADOS,
        )

        with self.assertRaises(ErrorValidacionAdministrativa) as ctx_des:
            desactivar_ubicacion_local(
                estado,
                ubicacion_id="U001",
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            )
        self.assertEqual(
            ctx_des.exception.codigo,
            CodigoErrorAdministrativo.UBICACION_CON_PRODUCTOS_ASOCIADOS,
        )

    def test_07_persistencia_simulada_roundtrip_y_borradores(self) -> None:
        """7. Persistencia simulada, round-trip de 4 hojas con Activo y restauración de borrador."""
        sha_inicial = "b" * 40
        sha_nuevo = "c" * 40
        estado = _crear_estado_sesion_admin_autorizado(sha_remoto=sha_inicial)

        desactivar_producto_local(
            estado,
            codigo_producto="0010",
            confirmado=True,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        desactivar_producto_local(
            estado,
            codigo_producto="0020",
            confirmado=True,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        reactivar_producto_local(
            estado,
            codigo_producto="0020",
            confirmado=True,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )

        # Simular limpieza del espacio de trabajo y posterior restauración desde el borrador retenido
        inv_base = construir_inventario_datos(_crear_hojas_v0_sin_activo_en_productos())
        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = None

        borrador_rest = app.ejecutar_restauracion_borrador_en_sesion(
            estado,
            inventario_base=inv_base,
            sha_base_remoto=sha_inicial,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertIsNotNone(borrador_rest)

        # Tras restaurar borrador: 0010 sigue Inactivo y 0020 sigue Activo
        p0010 = consultar_producto_administrativo_por_codigo(
            estado, "0010", contexto_dispositivo=ContextoDispositivo.ESCRITORIO
        )
        p0020 = consultar_producto_administrativo_por_codigo(
            estado, "0020", contexto_dispositivo=ContextoDispositivo.ESCRITORIO
        )
        self.assertEqual(p0010["activo"], "No")
        self.assertEqual(p0020["activo"], "Sí")

        # Publicación simulada en GitHub Contents API con verificación round-trip y control SHA
        solicitudes_put: list[tuple[str, Mapping[str, str], bytes]] = []

        def _consultor_existencia_simulado(**_kwargs: Any) -> ResultadoExistenciaRemota:
            cfg = github_inventario.CONFIGURACION_POR_DEFECTO
            return ResultadoExistenciaRemota(
                estado=github_inventario.EstadoExistenciaRemota.EXISTE,
                propietario=cfg.propietario,
                repositorio=cfg.repositorio,
                rama=cfg.rama,
                ruta_archivo=cfg.ruta_archivo,
                categoria_consulta=github_inventario.CategoriaResultadoConsulta.INVENTARIO_DISPONIBLE,
                sha_github=sha_inicial,
                tamano_bytes=4096,
            )

        def _ejecutor_put_simulado(
            url: str,
            encabezados: Mapping[str, str],
            cuerpo_bytes: bytes,
            _timeout: float,
        ) -> RespuestaHTTPGitHub:
            solicitudes_put.append((url, encabezados, cuerpo_bytes))
            payload_resp = {
                "content": {"sha": sha_nuevo, "path": "03_Aplicacion/inventario.xlsx"},
                "commit": {"sha": "e" * 40},
            }
            return RespuestaHTTPGitHub(
                status_code=200,
                cuerpo=json.dumps(payload_resp).encode("utf-8"),
                encabezados={"Content-Type": "application/json"},
            )

        res_pub = app.ejecutar_publicacion_github_en_sesion(
            estado,
            confirmacion_explicita=True,
            token="ghp_token_simulado_pruebas_p15",
            consultor_existencia=_consultor_existencia_simulado,
            ejecutor_http_put=_ejecutor_put_simulado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(res_pub.exito)
        self.assertTrue(res_pub.confirmado_en_github)
        self.assertEqual(res_pub.nuevo_sha_archivo, sha_nuevo)
        self.assertEqual(len(solicitudes_put), 1)
        payload_enviado = json.loads(solicitudes_put[0][2].decode("utf-8"))
        self.assertEqual(payload_enviado["sha"], sha_inicial)

        # Decodificar el Excel enviado a GitHub y verificar las 4 hojas y los estados Activo
        bytes_xlsx = base64.b64decode(payload_enviado["content"])
        inv_recargado = cargar_inventario_excel(bytes_xlsx)
        self.assertEqual(tuple(inv_recargado.obtener_hojas().keys()), ORDEN_HOJAS)
        self.assertEqual(
            list(inv_recargado.productos.columns),
            list(ESQUEMA_HOJAS[HOJA_PRODUCTOS]),
        )
        self.assertEqual(
            list(inv_recargado.ubicaciones.columns),
            list(ESQUEMA_HOJAS[HOJA_UBICACIONES]),
        )
        mapa_activo_prod = dict(
            zip(inv_recargado.productos["Codigo_Producto"], inv_recargado.productos["Activo"])
        )
        self.assertEqual(mapa_activo_prod, {"0010": "No", "0020": "Sí", "0030": "Sí"})

    def test_08_seguridad_administrativa_y_confirmacion_cambio_estado(self) -> None:
        """8. Seguridad básica: exige sesión administrativa en escritorio y confirmación explícita."""
        estado = _crear_estado_sesion_admin_autorizado()

        # Sin confirmación explícita se rechaza el cambio de estado
        with self.assertRaises(ErrorValidacionAdministrativa) as ctx_conf:
            cambiar_estado_producto_local(
                estado,
                codigo_producto="0010",
                activo="No",
                confirmado=False,
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            )
        self.assertEqual(
            ctx_conf.exception.codigo,
            CodigoErrorAdministrativo.CONFIRMACION_CAMBIO_ESTADO_REQUERIDA,
        )

        # Desde dispositivo móvil se rechaza la operación administrativa
        with self.assertRaises(ErrorAutorizacionAdmin):
            desactivar_producto_local(
                estado,
                codigo_producto="0010",
                confirmado=True,
                contexto_dispositivo=ContextoDispositivo.MOVIL,
            )

        # Sin sesión autenticada se rechaza la operación administrativa
        with self.assertRaises(ErrorAutorizacionAdmin):
            desactivar_producto_local(
                {},
                codigo_producto="0010",
                confirmado=True,
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            )

    def test_09_inmutabilidad_archivo_inventario_xlsx_en_disco(self) -> None:
        """Verifica que el archivo maestro local 03_Aplicacion/inventario.xlsx no fue modificado."""
        ruta_excel = RUTA_APLICACION / "inventario.xlsx"
        self.assertTrue(ruta_excel.is_file())
        sha256_antes = hashlib.sha256(ruta_excel.read_bytes()).hexdigest()

        estado = _crear_estado_sesion_admin_autorizado()
        desactivar_producto_local(
            estado,
            codigo_producto="0010",
            confirmado=True,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        paquete = serializar_y_verificar_inventario_xlsx(
            estado[CLAVE_ESPACIO_TRABAJO_ADMIN].inventario_trabajo
        )
        self.assertGreater(len(paquete.contenido_base64), 0)

        sha256_despues = hashlib.sha256(ruta_excel.read_bytes()).hexdigest()
        self.assertEqual(sha256_antes, sha256_despues)


if __name__ == "__main__":
    unittest.main()
