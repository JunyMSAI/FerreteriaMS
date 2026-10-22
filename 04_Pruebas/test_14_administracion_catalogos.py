"""Pruebas focalizadas de administración de categorías y ubicaciones (FERMS-FINAL-P14).

Verifica los requisitos y criterios de aceptación de `02_Prompts/14_Administracion_Catalogos.md`:
- RF-F-001, RF-F-002, RF-F-003 / CA-F-001, CA-F-002, CA-F-003:
  Consulta, alta y renombrado de categorías con `Categoria_ID` inmutable, reflejo inmediato
  en productos asociados y rechazo de nombres duplicados normalizados (mayúsculas, acentos, espacios).
- RF-F-004, RF-F-005, RF-F-006, RF-F-007, RF-F-009 / CA-F-004, CA-F-005, CA-F-006:
  Consulta, alta, edición de coordenadas físicas sin productos asociados (`Ubicacion_ID` inmutable),
  desactivación lógica (`Activo = "No"`) sin productos asociados, rechazo de combinaciones físicas
  duplicadas y bloqueo de asignación de ubicaciones inactivas.
- RF-F-010, RF-F-011 / CA-F-008, CA-F-009:
  Compatibilidad retroactiva con archivos Excel v0 sin columna `Activo` en `Ubicaciones`,
  conservación íntegra de las 4 hojas oficiales y publicación simulada en GitHub con round-trip.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
import unittest
from pathlib import Path
from typing import Any, Mapping
from unittest.mock import patch

import pandas as pd

RUTA_RAIZ = Path(__file__).resolve().parent.parent
RUTA_APP = RUTA_RAIZ / "03_Aplicacion"
RUTA_EXCEL_MAESTRO = RUTA_APP / "inventario.xlsx"

if str(RUTA_APP) not in sys.path:
    sys.path.insert(0, str(RUTA_APP))

import administracion_productos  # noqa: E402
import app  # noqa: E402
import autenticacion  # noqa: E402
import busqueda  # noqa: E402
import github_inventario  # noqa: E402
import inventario  # noqa: E402
import persistencia_github  # noqa: E402
from administracion_productos import (  # noqa: E402
    CLAVE_ESPACIO_TRABAJO_ADMIN,
    CodigoErrorAdministrativo,
    ErrorAdministracionInventario,
    ErrorValidacionAdministrativa,
    ModoVistaAdmin,
    cargar_inventario_administrativo_en_sesion,
    consultar_categoria_administrativa_por_id,
    consultar_categorias_administrativas,
    consultar_producto_administrativo_por_codigo,
    consultar_productos_administrativos,
    consultar_ubicacion_administrativa_por_id,
    consultar_ubicaciones_administrativas,
    crear_categoria_local,
    crear_producto_local,
    crear_ubicacion_local,
    desactivar_ubicacion_local,
    editar_producto_local,
    editar_ubicacion_local,
    inicializar_espacio_trabajo_desde_inventario,
    obtener_catalogo_categorias_admin,
    obtener_catalogo_ubicaciones_admin,
    renombrar_categoria_local,
    restaurar_borrador_en_espacio_trabajo_admin,
)
from autenticacion import (  # noqa: E402
    ContextoDispositivo,
    ErrorAutorizacionAdmin,
    EstadoSesionAdmin,
    CLAVE_SESION_ADMIN,
)
from github_inventario import (  # noqa: E402
    RespuestaHTTPGitHub,
    ResultadoExistenciaRemota,
    ResultadoLecturaInventarioRemoto,
)
from inventario import (  # noqa: E402
    ESQUEMA_HOJAS,
    HOJA_ASIGNACIONES,
    HOJA_CATEGORIAS,
    HOJA_PRODUCTOS,
    HOJA_UBICACIONES,
    ORDEN_HOJAS,
    CodigoErrorInventario,
    ErrorNombreCategoriaDuplicado,
    ErrorUbicacionFisicaDuplicada,
    ErrorUbicacionInactivaAsignada,
    ErrorValorActivoInvalido,
    cargar_inventario_excel,
    construir_inventario_datos,
    normalizar_texto_comparacion_catalogo,
    normalizar_valor_activo,
    obtener_productos_estructurados,
    serializar_inventario_a_bytes,
    validar_inventario,
)
from persistencia_github import (  # noqa: E402
    publicar_cambios_administrativos_github,
    serializar_y_verificar_inventario_xlsx,
)


def _construir_hojas_v0_sin_activo() -> dict[str, pd.DataFrame]:
    """Construye un inventario válido de esquema v0 (sin columna `Activo` en `Ubicaciones`)."""
    df_categorias = pd.DataFrame(
        [
            {"Categoria_ID": "CAT-01", "Nombre_Categoria": "Herramientas Manuales"},
            {"Categoria_ID": "CAT-02", "Nombre_Categoria": "Fijaciones y Tornillería"},
            {"Categoria_ID": "CAT-03", "Nombre_Categoria": "Eléctricos e Iluminación"},
        ]
    )
    df_ubicaciones = pd.DataFrame(
        [
            {"Ubicacion_ID": "U-01", "Rack": "R1", "Columna": "C1", "Nivel": "N1", "Posicion": "P1"},
            {"Ubicacion_ID": "U-02", "Rack": "R1", "Columna": "C1", "Nivel": "N1", "Posicion": "P2"},
            {"Ubicacion_ID": "U-03", "Rack": "R2", "Columna": "C3", "Nivel": "N2", "Posicion": "P4"},
        ]
    )
    df_productos = pd.DataFrame(
        [
            {
                "Codigo_Producto": "001",
                "Nombre": "Martillo de uña 16 oz",
                "Categoria_ID": "CAT-01",
                "Descripcion": "Martillo forjado con mango ergonómico",
            },
            {
                "Codigo_Producto": "002",
                "Nombre": "Tornillo autoperforante 1 pulg",
                "Categoria_ID": "CAT-02",
                "Descripcion": "Caja de tornillos galvanizados",
            },
        ]
    )
    df_asignaciones = pd.DataFrame(
        [
            {"Codigo_Producto": "001", "Ubicacion_ID": "U-01", "Principal": "Sí"},
            {"Codigo_Producto": "001", "Ubicacion_ID": "U-02", "Principal": "No"},
            {"Codigo_Producto": "002", "Ubicacion_ID": "U-02", "Principal": "Sí"},
        ]
    )
    return {
        HOJA_PRODUCTOS: df_productos,
        HOJA_CATEGORIAS: df_categorias,
        HOJA_UBICACIONES: df_ubicaciones,
        HOJA_ASIGNACIONES: df_asignaciones,
    }


_USUARIO_ADMIN_PRUEBA = "admin_ferms"
_CLAVE_ADMIN_PRUEBA = "ClaveSeguraP14!2026"
_HASH_ADMIN_PRUEBA = autenticacion.generar_hash_contrasena(_CLAVE_ADMIN_PRUEBA)
_SECRETOS_ADMIN_PRUEBA = {
    "admin": {
        "username": _USUARIO_ADMIN_PRUEBA,
        "password_hash": _HASH_ADMIN_PRUEBA,
    }
}


def _crear_estado_sesion_admin_autorizado(
    *,
    sha_remoto: str = "a" * 40,
) -> dict[str, Any]:
    """Inicializa una sesión administrativa autenticada con inventario cargado en memoria."""
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
    inv = construir_inventario_datos(_construir_hojas_v0_sin_activo())
    espacio = inicializar_espacio_trabajo_desde_inventario(
        estado,
        inv,
        sha_base_remoto=sha_remoto,
        origen_remoto_confirmado=True,
        contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
    )
    estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = espacio
    return estado


class TestP14CompatibilidadRetroactivaYEsquema(unittest.TestCase):
    """Verifica `CA-F-008` y `CA-F-009`: retrocompatibilidad con archivo v0 y esquema de 4 hojas."""

    def test_retrocompatibilidad_hoja_ubicaciones_sin_columna_activo(self) -> None:
        """Un inventario v0 sin columna `Activo` en `Ubicaciones` se carga e interpreta como `Sí`."""
        hojas_v0 = _construir_hojas_v0_sin_activo()
        self.assertNotIn("Activo", hojas_v0[HOJA_UBICACIONES].columns)

        res_val = validar_inventario(hojas_v0, lanzar_excepcion=True)
        self.assertTrue(res_val.es_valido)

        inv = construir_inventario_datos(hojas_v0)
        self.assertEqual(
            tuple(inv.ubicaciones.columns),
            ("Ubicacion_ID", "Rack", "Columna", "Nivel", "Posicion", "Activo"),
        )
        self.assertEqual(list(inv.ubicaciones["Activo"]), ["Sí", "Sí", "Sí"])
        self.assertNotIn("Activo", inv.categorias.columns)

        # También al leer bytes Excel v0 sin la columna Activo
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            for nombre_hoja in ORDEN_HOJAS:
                hojas_v0[nombre_hoja].to_excel(writer, sheet_name=nombre_hoja, index=False)
        inv_desde_bytes = cargar_inventario_excel(buffer.getvalue())
        self.assertEqual(list(inv_desde_bytes.ubicaciones["Activo"]), ["Sí", "Sí", "Sí"])

    def test_normalizacion_valores_activo_y_rechazo_valor_invalido(self) -> None:
        """`normalizar_valor_activo` acepta variantes Sí/No/True/False/vacío y rechaza valores inválidos."""
        self.assertEqual(normalizar_valor_activo(""), "Sí")
        self.assertEqual(normalizar_valor_activo(None), "Sí")
        self.assertEqual(normalizar_valor_activo("si"), "Sí")
        self.assertEqual(normalizar_valor_activo("SÍ"), "Sí")
        self.assertEqual(normalizar_valor_activo(True), "Sí")
        self.assertEqual(normalizar_valor_activo("No"), "No")
        self.assertEqual(normalizar_valor_activo("false"), "No")
        self.assertEqual(normalizar_valor_activo(False), "No")

        with self.assertRaises(ErrorValorActivoInvalido) as ctx:
            normalizar_valor_activo("TalVez")
        self.assertEqual(ctx.exception.codigo, CodigoErrorInventario.VALOR_ACTIVO_INVALIDO)

    def test_archivo_maestro_local_intacto_y_compatible(self) -> None:
        """El archivo real `03_Aplicacion/inventario.xlsx` se lee con retrocompatibilidad sin modificarse."""
        bytes_antes = RUTA_EXCEL_MAESTRO.read_bytes()
        sha_antes = hashlib.sha256(bytes_antes).hexdigest()

        inv_maestro = cargar_inventario_excel(RUTA_EXCEL_MAESTRO)
        self.assertIn("Activo", inv_maestro.ubicaciones.columns)
        self.assertTrue((inv_maestro.ubicaciones["Activo"] == "Sí").all())

        bytes_despues = RUTA_EXCEL_MAESTRO.read_bytes()
        self.assertEqual(sha_antes, hashlib.sha256(bytes_despues).hexdigest())


class TestP14AdministracionCategorias(unittest.TestCase):
    """Verifica `RF-F-001` a `RF-F-003` y `CA-F-001` a `CA-F-003`."""

    def test_crear_categoria_exitosa_y_disponibilidad_inmediata_en_selectores(self) -> None:
        """Crear una categoría válida la incorpora en `Categorías` y en el selector de productos (`CA-F-001`)."""
        estado = _crear_estado_sesion_admin_autorizado()

        res = app.ejecutar_creacion_categoria_en_sesion(
            categoria_id="CAT-04",
            nombre_categoria="Plomería y Gasfitería",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(res.exito)
        self.assertEqual(res.categoria_id, "CAT-04")
        self.assertEqual(res.nombre_categoria, "Plomería y Gasfitería")

        catalogo = obtener_catalogo_categorias_admin(
            estado, contexto_dispositivo=ContextoDispositivo.ESCRITORIO
        )
        ids_catalogo = [c["categoria_id"] for c in catalogo]
        self.assertIn("CAT-04", ids_catalogo)

        detalle_cat = consultar_categoria_administrativa_por_id(
            estado, "CAT-04", contexto_dispositivo=ContextoDispositivo.ESCRITORIO
        )
        self.assertIsNotNone(detalle_cat)
        assert detalle_cat is not None
        self.assertEqual(detalle_cat["nombre_categoria"], "Plomería y Gasfitería")
        self.assertEqual(detalle_cat["total_productos_asociados"], 0)
        self.assertTrue(detalle_cat["es_creada_en_sesion"])

        # Crear un producto asignado a la nueva categoría
        res_prod = app.ejecutar_creacion_producto_en_sesion(
            codigo_producto="003",
            nombre="Llave de paso bronce 1/2",
            categoria_id="CAT-04",
            descripcion="Válvula esférica",
            ubicaciones_ids=["U-03"],
            ubicacion_principal_id="U-03",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(res_prod.exito)

    def test_rechazo_nombre_categoria_duplicado_normalizado(self) -> None:
        """Rechaza crear o renombrar una categoría con nombre equivalente ignorando mayúsculas, tildes y espacios (`CA-F-003`)."""
        estado = _crear_estado_sesion_admin_autorizado()

        # Intento de crear con variación de mayúsculas, acentos y espacios múltiples
        res_dup = app.ejecutar_creacion_categoria_en_sesion(
            categoria_id="CAT-99",
            nombre_categoria="  ELÉCTRICOS   e   iluminación  ",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertFalse(res_dup.exito)
        self.assertEqual(res_dup.codigo_error, CodigoErrorAdministrativo.NOMBRE_CATEGORIA_DUPLICADO)

        # Intento de crear con Categoria_ID duplicado
        res_id_dup = app.ejecutar_creacion_categoria_en_sesion(
            categoria_id="CAT-01",
            nombre_categoria="Categoría totalmente distinta",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertFalse(res_id_dup.exito)
        self.assertEqual(res_id_dup.codigo_error, CodigoErrorAdministrativo.CATEGORIA_ID_DUPLICADO)

        # Intento de renombrar CAT-01 al nombre de CAT-02 con distinta capitalización y sin tilde
        res_ren_dup = app.ejecutar_renombrado_categoria_en_sesion(
            categoria_id="CAT-01",
            nuevo_nombre_categoria="fijaciones y tornilleria",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertFalse(res_ren_dup.exito)
        self.assertEqual(
            res_ren_dup.codigo_error, CodigoErrorAdministrativo.NOMBRE_CATEGORIA_DUPLICADO
        )

    def test_renombrar_categoria_conserva_id_y_refleja_en_productos_asociados(self) -> None:
        """Renombrar una categoría mantiene `Categoria_ID` inmutable y actualiza el nombre en productos asociados (`CA-F-002`)."""
        estado = _crear_estado_sesion_admin_autorizado()

        # Intento de alterar Categoria_ID debe ser rechazado
        res_inmutable = app.ejecutar_renombrado_categoria_en_sesion(
            categoria_id="CAT-01",
            nuevo_categoria_id="CAT-999",
            nuevo_nombre_categoria="Herramientas de Mano Profesionales",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertFalse(res_inmutable.exito)
        self.assertEqual(
            res_inmutable.codigo_error, CodigoErrorAdministrativo.CATEGORIA_ID_INMUTABLE
        )

        # Renombrado válido
        res_ok = app.ejecutar_renombrado_categoria_en_sesion(
            categoria_id="CAT-01",
            nuevo_nombre_categoria="Herramientas de Mano Profesionales",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(res_ok.exito)
        self.assertEqual(res_ok.categoria_id, "CAT-01")
        self.assertEqual(res_ok.nombre_categoria, "Herramientas de Mano Profesionales")

        # Verificar reflejo inmediato en consulta administrativa de productos
        prod_001 = consultar_producto_administrativo_por_codigo(
            estado, "001", contexto_dispositivo=ContextoDispositivo.ESCRITORIO
        )
        self.assertIsNotNone(prod_001)
        assert prod_001 is not None
        self.assertEqual(prod_001["categoria_id"], "CAT-01")
        self.assertEqual(prod_001["nombre_categoria"], "Herramientas de Mano Profesionales")

        # Verificar reflejo inmediato en motor de búsqueda pública y vista de detalle
        espacio = estado[CLAVE_ESPACIO_TRABAJO_ADMIN]
        res_busq = busqueda.ejecutar_busqueda_productos(
            espacio.inventario_trabajo, "Martillo"
        )
        self.assertEqual(res_busq.total_resultados, 1)
        self.assertEqual(
            res_busq.resultados_pagina[0].nombre_categoria,
            "Herramientas de Mano Profesionales",
        )
        res_det = busqueda.consultar_detalle_producto(espacio.inventario_trabajo, "001")
        self.assertIsNotNone(res_det.detalle)
        assert res_det.detalle is not None
        self.assertEqual(
            res_det.detalle.nombre_categoria,
            "Herramientas de Mano Profesionales",
        )


class TestP14AdministracionUbicaciones(unittest.TestCase):
    """Verifica `RF-F-004` a `RF-F-007`, `RF-F-009` y `CA-F-004` a `CA-F-006`."""

    def test_crear_ubicacion_exitosa_y_rechazo_combinacion_fisica_duplicada(self) -> None:
        """Crear una ubicación con coordenadas únicas la registra activa; rechaza combinaciones físicas duplicadas (`CA-F-004`)."""
        estado = _crear_estado_sesion_admin_autorizado()

        res = app.ejecutar_creacion_ubicacion_en_sesion(
            ubicacion_id="U-04",
            rack="R3",
            columna="C2",
            nivel="N1",
            posicion="P5",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(res.exito)
        self.assertEqual(res.ubicacion_id, "U-04")
        self.assertEqual(res.activo, "Sí")

        # Intento de crear otra ubicación con distinto Ubicacion_ID pero misma combinación física (normalizada)
        res_dup_fis = app.ejecutar_creacion_ubicacion_en_sesion(
            ubicacion_id="U-05",
            rack=" r3 ",
            columna="c2",
            nivel="N1",
            posicion="p5",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertFalse(res_dup_fis.exito)
        self.assertEqual(
            res_dup_fis.codigo_error, CodigoErrorAdministrativo.UBICACION_FISICA_DUPLICADA
        )

        # Intento de crear ubicación con Ubicacion_ID duplicado
        res_dup_id = app.ejecutar_creacion_ubicacion_en_sesion(
            ubicacion_id="U-01",
            rack="R9",
            columna="C9",
            nivel="N9",
            posicion="P9",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertFalse(res_dup_id.exito)
        self.assertEqual(
            res_dup_id.codigo_error, CodigoErrorAdministrativo.UBICACION_ID_DUPLICADO
        )

    def test_editar_ubicacion_sin_productos_vs_bloqueo_con_productos_asociados(self) -> None:
        """Permite editar coordenadas de `U-03` (sin productos) pero rechaza editar `U-01` o `U-02` (con productos) (`CA-F-005`)."""
        estado = _crear_estado_sesion_admin_autorizado()

        # U-01 tiene asociado el producto 001 -> debe rechazarse su edición física
        res_bloq = app.ejecutar_edicion_ubicacion_en_sesion(
            ubicacion_id="U-01",
            rack="R8",
            columna="C8",
            nivel="N8",
            posicion="P8",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertFalse(res_bloq.exito)
        self.assertEqual(
            res_bloq.codigo_error,
            CodigoErrorAdministrativo.UBICACION_CON_PRODUCTOS_ASOCIADOS,
        )
        self.assertIn("001", res_bloq.mensaje_usuario)

        # Intento de modificar Ubicacion_ID de U-03 -> inmutable
        res_inm = app.ejecutar_edicion_ubicacion_en_sesion(
            ubicacion_id="U-03",
            nuevo_ubicacion_id="U-300",
            rack="R5",
            columna="C1",
            nivel="N1",
            posicion="P1",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertFalse(res_inm.exito)
        self.assertEqual(
            res_inm.codigo_error, CodigoErrorAdministrativo.UBICACION_ID_INMUTABLE
        )

        # Edición válida de U-03 (0 productos asociados)
        res_ed = app.ejecutar_edicion_ubicacion_en_sesion(
            ubicacion_id="U-03",
            rack="R5",
            columna="C4",
            nivel="N3",
            posicion="P2",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(res_ed.exito)
        self.assertEqual(res_ed.ubicacion_id, "U-03")
        self.assertEqual(res_ed.rack, "R5")
        self.assertEqual(res_ed.columna, "C4")
        self.assertEqual(res_ed.nivel, "N3")
        self.assertEqual(res_ed.posicion, "P2")

    def test_desactivar_ubicacion_sin_productos_y_bloqueo_asignacion_inactiva(self) -> None:
        """Permite desactivar ubicación libre, la excluye del catálogo asignable y rechaza asignarla (`CA-F-005`, `CA-F-006`)."""
        estado = _crear_estado_sesion_admin_autorizado()

        # U-02 tiene 2 productos asociados (001 secundaria y 002 principal) -> rechaza desactivar
        res_bloq = app.ejecutar_desactivacion_ubicacion_en_sesion(
            ubicacion_id="U-02",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertFalse(res_bloq.exito)
        self.assertEqual(
            res_bloq.codigo_error,
            CodigoErrorAdministrativo.UBICACION_CON_PRODUCTOS_ASOCIADOS,
        )

        # U-03 no tiene productos asociados -> permite desactivar
        res_des = app.ejecutar_desactivacion_ubicacion_en_sesion(
            ubicacion_id="U-03",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(res_des.exito)
        self.assertEqual(res_des.ubicacion_id, "U-03")
        self.assertEqual(res_des.activo, "No")

        # La fila U-03 se conserva en la hoja Ubicaciones con Activo == "No" (no se elimina)
        espacio = estado[CLAVE_ESPACIO_TRABAJO_ADMIN]
        df_ubic = espacio.inventario_trabajo.ubicaciones
        self.assertEqual(len(df_ubic), 3)
        fila_u03 = df_ubic[df_ubic["Ubicacion_ID"] == "U-03"].iloc[0]
        self.assertEqual(fila_u03["Activo"], "No")

        # El catálogo para formularios de productos excluye por defecto las ubicaciones inactivas
        catalogo_asignable = obtener_catalogo_ubicaciones_admin(
            estado, contexto_dispositivo=ContextoDispositivo.ESCRITORIO
        )
        ids_asignables = [u["ubicacion_id"] for u in catalogo_asignable]
        self.assertEqual(ids_asignables, ["U-01", "U-02"])
        self.assertNotIn("U-03", ids_asignables)

        # Intentar crear un producto asignándole la ubicación inactiva U-03 debe rechazarse
        res_crear_inact = app.ejecutar_creacion_producto_en_sesion(
            codigo_producto="009",
            nombre="Alicate universal 8 pulg",
            categoria_id="CAT-01",
            ubicaciones_ids=["U-03"],
            ubicacion_principal_id="U-03",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertFalse(res_crear_inact.exito)
        self.assertEqual(
            res_crear_inact.codigo_error, CodigoErrorAdministrativo.UBICACION_INACTIVA
        )

        # Intentar editar un producto existente para asignarle U-03 también debe rechazarse
        res_ed_inact = app.ejecutar_edicion_producto_en_sesion(
            codigo_producto="001",
            ubicaciones_ids=["U-01", "U-03"],
            ubicacion_principal_id="U-01",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertFalse(res_ed_inact.exito)
        self.assertEqual(
            res_ed_inact.codigo_error, CodigoErrorAdministrativo.UBICACION_INACTIVA
        )

    def test_flujo_reasignacion_previa_habilita_edicion_y_desactivacion_ubicacion(self) -> None:
        """Al reasignar el producto `001` fuera de `U-01`, `U-01` queda libre y puede editarse y desactivarse (`RF-F-007`)."""
        estado = _crear_estado_sesion_admin_autorizado()

        # Inicialmente U-01 está bloqueada porque 001 la tiene como ubicación principal
        info_u01_antes = consultar_ubicacion_administrativa_por_id(
            estado, "U-01", contexto_dispositivo=ContextoDispositivo.ESCRITORIO
        )
        assert info_u01_antes is not None
        self.assertFalse(info_u01_antes["puede_editarse"])
        self.assertFalse(info_u01_antes["puede_desactivarse"])
        self.assertEqual(info_u01_antes["codigos_productos_asociados"], ["001"])

        # Reasignamos el producto 001 para que su única ubicación sea U-02
        res_reasig = app.ejecutar_edicion_producto_en_sesion(
            codigo_producto="001",
            ubicaciones_ids=["U-02"],
            ubicacion_principal_id="U-02",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(res_reasig.exito)

        # Ahora U-01 tiene 0 productos asociados y puede editarse y desactivarse
        info_u01_despues = consultar_ubicacion_administrativa_por_id(
            estado, "U-01", contexto_dispositivo=ContextoDispositivo.ESCRITORIO
        )
        assert info_u01_despues is not None
        self.assertTrue(info_u01_despues["puede_editarse"])
        self.assertTrue(info_u01_despues["puede_desactivarse"])

        res_ed_u01 = app.ejecutar_edicion_ubicacion_en_sesion(
            ubicacion_id="U-01",
            rack="R10",
            columna="C1",
            nivel="N1",
            posicion="P1",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(res_ed_u01.exito)

        res_des_u01 = app.ejecutar_desactivacion_ubicacion_en_sesion(
            ubicacion_id="U-01",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(res_des_u01.exito)
        self.assertEqual(res_des_u01.activo, "No")


class TestP14PersistenciaGitHubBorradoresYSeguridad(unittest.TestCase):
    """Verifica persistencia simulada en GitHub (`CA-F-008`), borradores y controles de seguridad."""

    def test_publicacion_simulada_github_con_cambios_de_categorias_y_ubicaciones(self) -> None:
        """Publica cambios de categorías y ubicaciones mediante simulación HTTP PUT y verifica round-trip de las 4 hojas (`CA-F-008`)."""
        sha_inicial = "b" * 40
        sha_nuevo = "c" * 40
        estado = _crear_estado_sesion_admin_autorizado(sha_remoto=sha_inicial)

        # 1. Crear categoría, renombrar categoría existente, crear ubicación, editar y desactivar ubicación libre
        self.assertTrue(
            app.ejecutar_creacion_categoria_en_sesion(
                categoria_id="CAT-04",
                nombre_categoria="Seguridad Industrial",
                estado=estado,
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            ).exito
        )
        self.assertTrue(
            app.ejecutar_renombrado_categoria_en_sesion(
                categoria_id="CAT-01",
                nuevo_nombre_categoria="Herramientas Manuales y de Golpe",
                estado=estado,
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            ).exito
        )
        self.assertTrue(
            app.ejecutar_creacion_ubicacion_en_sesion(
                ubicacion_id="U-04",
                rack="R4",
                columna="C2",
                nivel="N1",
                posicion="P3",
                estado=estado,
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            ).exito
        )
        self.assertTrue(
            app.ejecutar_edicion_ubicacion_en_sesion(
                ubicacion_id="U-03",
                rack="R7",
                columna="C1",
                nivel="N2",
                posicion="P1",
                estado=estado,
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            ).exito
        )
        self.assertTrue(
            app.ejecutar_desactivacion_ubicacion_en_sesion(
                ubicacion_id="U-03",
                estado=estado,
                contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
            ).exito
        )

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
                "commit": {"sha": "d" * 40},
            }
            return RespuestaHTTPGitHub(
                status_code=200,
                cuerpo=json.dumps(payload_resp).encode("utf-8"),
                encabezados={"Content-Type": "application/json"},
            )

        res_pub = app.ejecutar_publicacion_github_en_sesion(
            estado,
            confirmacion_explicita=True,
            token="ghp_token_simulado_prueba_p14",
            consultor_existencia=_consultor_existencia_simulado,
            ejecutor_http_put=_ejecutor_put_simulado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertTrue(res_pub.exito)
        self.assertTrue(res_pub.confirmado_en_github)
        self.assertEqual(res_pub.nuevo_sha_archivo, sha_nuevo)
        self.assertEqual(len(solicitudes_put), 1)

        # Verificar que el inventario confirmado en el espacio de trabajo quedó sincronizado y verificado round-trip
        espacio_confirmado = estado[CLAVE_ESPACIO_TRABAJO_ADMIN]
        self.assertIsNotNone(espacio_confirmado)
        self.assertTrue(espacio_confirmado.confirmado_en_github)
        self.assertFalse(espacio_confirmado.tiene_cambios_locales_pendientes)
        inv_publicado = espacio_confirmado.inventario_trabajo
        self.assertIsNotNone(inv_publicado)
        self.assertEqual(tuple(inv_publicado.obtener_hojas().keys()), ORDEN_HOJAS)
        self.assertEqual(
            list(inv_publicado.categorias["Categoria_ID"]),
            ["CAT-01", "CAT-02", "CAT-03", "CAT-04"],
        )
        fila_cat01 = inv_publicado.categorias[
            inv_publicado.categorias["Categoria_ID"] == "CAT-01"
        ].iloc[0]
        self.assertEqual(
            fila_cat01["Nombre_Categoria"], "Herramientas Manuales y de Golpe"
        )
        fila_u03 = inv_publicado.ubicaciones[
            inv_publicado.ubicaciones["Ubicacion_ID"] == "U-03"
        ].iloc[0]
        self.assertEqual(fila_u03["Rack"], "R7")
        self.assertEqual(fila_u03["Activo"], "No")

    def test_recuperacion_borrador_reaplica_operaciones_de_categorias_y_ubicaciones(self) -> None:
        """Al expirar la sesión y reautenticar, la restauración del borrador reaplica cambios de catálogos."""
        estado = _crear_estado_sesion_admin_autorizado()
        app.ejecutar_creacion_categoria_en_sesion(
            categoria_id="CAT-09",
            nombre_categoria="Jardinería y Riego",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        app.ejecutar_creacion_ubicacion_en_sesion(
            ubicacion_id="U-09",
            rack="R9",
            columna="C1",
            nivel="N1",
            posicion="P1",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        app.ejecutar_desactivacion_ubicacion_en_sesion(
            ubicacion_id="U-03",
            estado=estado,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )

        # Simular limpieza del espacio de trabajo y posterior restauración desde el borrador retenido
        inv_base = construir_inventario_datos(_construir_hojas_v0_sin_activo())
        estado[CLAVE_ESPACIO_TRABAJO_ADMIN] = None

        borrador = app.ejecutar_restauracion_borrador_en_sesion(
            estado,
            inventario_base=inv_base,
            sha_base_remoto="a" * 40,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertIsNotNone(borrador)
        espacio_rest = estado[CLAVE_ESPACIO_TRABAJO_ADMIN]
        self.assertIsNotNone(espacio_rest)
        self.assertIn("CAT-09", espacio_rest.categorias_creadas)
        self.assertIn("U-09", espacio_rest.ubicaciones_creadas)
        self.assertIn("U-03", espacio_rest.ubicaciones_desactivadas)

    def test_proteccion_autorizacion_y_restriccion_movil_en_operaciones_catalogos(self) -> None:
        """Rechaza cualquier operación sobre categorías o ubicaciones sin sesión o desde móvil (`RF-013`)."""
        estado_sin_auth: dict[str, Any] = {}
        app.inicializar_estado_sesion(estado_sin_auth)

        res_no_auth = app.ejecutar_creacion_categoria_en_sesion(
            categoria_id="CAT-10",
            nombre_categoria="Pinturas",
            estado=estado_sin_auth,
            contexto_dispositivo=ContextoDispositivo.ESCRITORIO,
        )
        self.assertFalse(res_no_auth.exito)
        self.assertEqual(
            res_no_auth.codigo_error, CodigoErrorAdministrativo.AUTORIZACION_INVALIDA
        )

        estado_auth = _crear_estado_sesion_admin_autorizado()
        res_movil = app.ejecutar_creacion_ubicacion_en_sesion(
            ubicacion_id="U-10",
            rack="R10",
            columna="C1",
            nivel="N1",
            posicion="P1",
            estado=estado_auth,
            contexto_dispositivo=ContextoDispositivo.MOVIL,
        )
        self.assertFalse(res_movil.exito)
        self.assertEqual(
            res_movil.codigo_error, CodigoErrorAdministrativo.AUTORIZACION_INVALIDA
        )


if __name__ == "__main__":
    unittest.main()
