"""Pruebas automatizadas funcionales y de integración para detalles y localización física de productos.

Proyecto: FerreteríaMS v0
Tarea: FERMS-V0-P05
Módulos probados: `03_Aplicacion/app.py` y `03_Aplicacion/busqueda.py`
(integrados con `03_Aplicacion/inventario.py` y `03_Aplicacion/github_inventario.py`).
Requisitos cubiertos: RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007, RF-008,
RF-009, RF-024, RF-025, RF-028, RF-034, RF-035, RF-036, RF-037, RF-038.
Criterios cubiertos: CA-001, CA-002, CA-003, CA-004, CA-005, CA-006, CA-007, CA-022,
CA-028, CA-032, CA-033, CA-034, CA-039, CA-040, CA-041, CA-042, CA-043.

Todas las pruebas se ejecutan sobre datos controlados en memoria y simulaciones (mocks),
sin crear ni modificar `03_Aplicacion/inventario.xlsx` y sin realizar escrituras en GitHub.
"""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_APLICACION = RAIZ_PROYECTO / "03_Aplicacion"
RUTA_MAESTRO_DEFINITIVO = RUTA_APLICACION / "inventario.xlsx"

if str(RUTA_APLICACION) not in sys.path:
    sys.path.insert(0, str(RUTA_APLICACION))

import app as app_ferms  # noqa: E402
import busqueda  # noqa: E402
import github_inventario as gh  # noqa: E402
import inventario as motor  # noqa: E402


def _construir_inventario_detalles_controlado(
    *,
    invertir_orden_asignaciones: bool = False,
) -> motor.InventarioDatos:
    """Construye un `InventarioDatos` válido con productos de 1 y múltiples ubicaciones y ceros iniciales."""
    df_categorias = pd.DataFrame(
        [
            {"Categoria_ID": "CAT01", "Nombre_Categoria": "Herramientas Manuales"},
            {"Categoria_ID": "CAT02", "Nombre_Categoria": "Tornillería y Fijación"},
            {"Categoria_ID": "CAT03", "Nombre_Categoria": "Electricidad e Iluminación"},
        ]
    )
    df_ubicaciones = pd.DataFrame(
        [
            {"Ubicacion_ID": "U001", "Rack": "R01", "Columna": "C02", "Nivel": "N03", "Posicion": "P04"},
            {"Ubicacion_ID": "U002", "Rack": "R02", "Columna": "C01", "Nivel": "N01", "Posicion": "P02"},
            {"Ubicacion_ID": "U003", "Rack": "R01", "Columna": "C01", "Nivel": "N02", "Posicion": "P01"},
            {"Ubicacion_ID": "U004", "Rack": "R03", "Columna": "C04", "Nivel": "N02", "Posicion": "P05"},
        ]
    )
    df_productos = pd.DataFrame(
        [
            {
                "Codigo_Producto": "0007",
                "Nombre": "Martillo de uña profesional",
                "Categoria_ID": "CAT01",
                "Descripcion": "Martillo de acero forjado con mango de fibra de vidrio.",
            },
            {
                "Codigo_Producto": "MAR002",
                "Nombre": "Martillo de goma",
                "Categoria_ID": "CAT01",
                "Descripcion": "",
            },
            {
                "Codigo_Producto": "000125",
                "Nombre": "Cinta aislante eléctrica",
                "Categoria_ID": "CAT03",
                "Descripcion": "Cinta de PVC negra de alta resistencia dieléctrica.",
            },
            {
                "Codigo_Producto": "TOR010",
                "Nombre": "Tornillo galvanizado para madera",
                "Categoria_ID": "CAT02",
                "Descripcion": "Tornillo anticorrosivo para exteriores.",
            },
        ]
    )

    # Nota: para "0007", la asignación principal (U001) se coloca deliberadamente después de una secundaria (U002)
    # para comprobar que la ubicación principal nunca se deduce por posición de fila (Sección 6).
    asignaciones = [
        {"Codigo_Producto": "0007", "Ubicacion_ID": "U002", "Principal": "No"},
        {"Codigo_Producto": "0007", "Ubicacion_ID": "U001", "Principal": "Sí"},
        {"Codigo_Producto": "0007", "Ubicacion_ID": "U004", "Principal": "No"},
        {"Codigo_Producto": "0007", "Ubicacion_ID": "U003", "Principal": "No"},
        {"Codigo_Producto": "MAR002", "Ubicacion_ID": "U003", "Principal": "Sí"},
        {"Codigo_Producto": "000125", "Ubicacion_ID": "U004", "Principal": "No"},
        {"Codigo_Producto": "000125", "Ubicacion_ID": "U002", "Principal": "Sí"},
        {"Codigo_Producto": "TOR010", "Ubicacion_ID": "U001", "Principal": "Sí"},
    ]
    if invertir_orden_asignaciones:
        asignaciones = list(reversed(asignaciones))

    return motor.construir_inventario_datos(
        {
            motor.HOJA_PRODUCTOS: df_productos,
            motor.HOJA_CATEGORIAS: df_categorias,
            motor.HOJA_UBICACIONES: df_ubicaciones,
            motor.HOJA_ASIGNACIONES: pd.DataFrame(asignaciones),
        }
    )


def _construir_inventario_paginado_15() -> motor.InventarioDatos:
    """Construye un inventario válido con 15 martillos para pruebas de paginación y selección."""
    df_categorias = pd.DataFrame(
        [{"Categoria_ID": "CAT01", "Nombre_Categoria": "Herramientas Manuales"}]
    )
    df_ubicaciones = pd.DataFrame(
        [
            {"Ubicacion_ID": "U001", "Rack": "R01", "Columna": "C01", "Nivel": "N01", "Posicion": "P01"},
            {"Ubicacion_ID": "U002", "Rack": "R02", "Columna": "C03", "Nivel": "N02", "Posicion": "P04"},
        ]
    )
    filas_prod: list[dict[str, str]] = []
    filas_asig: list[dict[str, str]] = []
    for i in range(1, 16):
        cod = f"00{i:02d}"
        filas_prod.append(
            {
                "Codigo_Producto": cod,
                "Nombre": f"Martillo serie {i:02d}",
                "Categoria_ID": "CAT01",
                "Descripcion": f"Descripción técnica del martillo serie {i:02d}.",
            }
        )
        filas_asig.append(
            {
                "Codigo_Producto": cod,
                "Ubicacion_ID": "U001" if i % 2 == 1 else "U002",
                "Principal": "Sí",
            }
        )
        if i == 12:
            filas_asig.append(
                {
                    "Codigo_Producto": cod,
                    "Ubicacion_ID": "U001",
                    "Principal": "No",
                }
            )

    return motor.construir_inventario_datos(
        {
            motor.HOJA_PRODUCTOS: pd.DataFrame(filas_prod),
            motor.HOJA_CATEGORIAS: df_categorias,
            motor.HOJA_UBICACIONES: df_ubicaciones,
            motor.HOJA_ASIGNACIONES: pd.DataFrame(filas_asig),
        }
    )


def _crear_lectura_simulada(
    inventario: motor.InventarioDatos,
    sha: str = "sha_simulado_p05",
) -> gh.ResultadoLecturaInventarioRemoto:
    return gh.ResultadoLecturaInventarioRemoto(
        propietario="JunyMSAI",
        repositorio="FerreteriaMS",
        rama="main",
        ruta_archivo="03_Aplicacion/inventario.xlsx",
        sha_github=sha,
        sha256_local="hash_local_simulado",
        tamano_bytes=2048,
        inventario=inventario,
    )


class TestDetallesYUbicacionesFuncional(unittest.TestCase):
    """Sección 10 — 16 pruebas funcionales de selección, detalles y localización física."""

    def setUp(self) -> None:
        self.inventario = _construir_inventario_detalles_controlado()
        self.lectura_base = _crear_lectura_simulada(self.inventario)

    def test_01_seleccion_de_producto_desde_resultados(self) -> None:
        """Caso 1 (RF-004, RF-005): Seleccionar un producto desde los resultados de búsqueda."""
        estado_sesion: dict[str, Any] = {}
        app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "martillo",
            estado=estado_sesion,
            descargador_remoto=lambda config=gh.CONFIGURACION_POR_DEFECTO: self.lectura_base,
        )
        self.assertIsNone(estado_sesion[app_ferms.CLAVE_PRODUCTO_SELECCIONADO])

        res_detalle = app_ferms.seleccionar_producto_en_sesion("0007", estado=estado_sesion)
        self.assertEqual(estado_sesion[app_ferms.CLAVE_PRODUCTO_SELECCIONADO], "0007")
        self.assertEqual(res_detalle.estado, busqueda.EstadoDetalleProducto.DETALLE_DISPONIBLE)
        self.assertTrue(res_detalle.tiene_detalle)
        assert res_detalle.detalle is not None
        self.assertEqual(res_detalle.detalle.nombre, "Martillo de uña profesional")

        # Verificación mediante botón "Ver detalles y ubicación" en AppTest
        ruta_app = str(RUTA_APLICACION / "app.py")
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at = AppTest.from_file(ruta_app)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)

            # Verificar que existe el botón "Ver detalles y ubicación" para el producto "0007"
            boton_detalle = at.button(key="btn_ver_detalle_0007")
            self.assertEqual(boton_detalle.label, "Ver detalles y ubicación")
            boton_detalle.click()
            at.run(timeout=15)

            self.assertEqual(
                at.session_state[app_ferms.CLAVE_PRODUCTO_SELECCIONADO], "0007"
            )
            subtitulos = [s.value for s in at.subheader]
            self.assertTrue(any("Detalles del producto" in s for s in subtitulos))
            self.assertTrue(any("Ubicación principal" in s for s in subtitulos))

    def test_02_identificacion_correcta_mediante_codigo(self) -> None:
        """Caso 2 (Sección 4.1): Identificación exacta mediante `Codigo_Producto`, no por posición visual."""
        estado_sesion: dict[str, Any] = {}
        app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "martillo",
            estado=estado_sesion,
            descargador_remoto=lambda config=gh.CONFIGURACION_POR_DEFECTO: self.lectura_base,
        )
        # En la búsqueda "martillo", MAR002 ("Martillo de goma") aparece primero y "0007" ("Martillo de uña profesional") segundo
        res_busq = estado_sesion[app_ferms.CLAVE_RESPUESTA_BUSQUEDA].resultado_busqueda
        self.assertEqual(
            [p.codigo_producto for p in res_busq.resultados_pagina],
            ["MAR002", "0007"],
        )

        # Seleccionar por código "0007" (segunda tarjeta) y luego "MAR002" (primera tarjeta)
        det_0007 = app_ferms.seleccionar_producto_en_sesion("0007", estado=estado_sesion)
        assert det_0007.detalle is not None
        self.assertEqual(det_0007.detalle.codigo_producto, "0007")
        self.assertEqual(det_0007.detalle.nombre, "Martillo de uña profesional")

        det_mar002 = app_ferms.seleccionar_producto_en_sesion("MAR002", estado=estado_sesion)
        assert det_mar002.detalle is not None
        self.assertEqual(det_mar002.detalle.codigo_producto, "MAR002")
        self.assertEqual(det_mar002.detalle.nombre, "Martillo de goma")

    def test_03_conservacion_de_codigos_con_ceros_iniciales(self) -> None:
        """Caso 3 (Secciones 4.1 y 5): Conserva códigos con ceros iniciales como texto y rechaza enteros."""
        res_000125 = busqueda.consultar_detalle_producto(self.inventario, "000125")
        self.assertEqual(res_000125.estado, busqueda.EstadoDetalleProducto.DETALLE_DISPONIBLE)
        assert res_000125.detalle is not None
        self.assertIsInstance(res_000125.detalle.codigo_producto, str)
        self.assertEqual(res_000125.detalle.codigo_producto, "000125")

        res_0007 = busqueda.consultar_detalle_producto(self.inventario, "0007")
        self.assertEqual(res_0007.estado, busqueda.EstadoDetalleProducto.DETALLE_DISPONIBLE)
        assert res_0007.detalle is not None
        self.assertEqual(res_0007.detalle.codigo_producto, "0007")

        # Si se pasa el número entero 125 o el texto sin ceros "125", no debe coincidir con "000125"
        res_int = busqueda.consultar_detalle_producto(self.inventario, 125)
        self.assertEqual(res_int.estado, busqueda.EstadoDetalleProducto.PRODUCTO_NO_DISPONIBLE)
        self.assertIsNone(res_int.detalle)

        res_sin_ceros = busqueda.consultar_detalle_producto(self.inventario, "125")
        self.assertEqual(res_sin_ceros.estado, busqueda.EstadoDetalleProducto.PRODUCTO_NO_DISPONIBLE)
        self.assertIsNone(res_sin_ceros.detalle)

    def test_04_presentacion_de_nombre_categoria_y_descripcion(self) -> None:
        """Caso 4 (RF-005 / Sección 5): Presenta código, nombre, categoría y descripción (incluyendo vacía neutra)."""
        # Producto con descripción registrada
        res_con_desc = busqueda.consultar_detalle_producto(self.inventario, "0007")
        assert res_con_desc.detalle is not None
        self.assertEqual(res_con_desc.detalle.codigo_producto, "0007")
        self.assertEqual(res_con_desc.detalle.nombre, "Martillo de uña profesional")
        self.assertEqual(res_con_desc.detalle.categoria_id, "CAT01")
        self.assertEqual(res_con_desc.detalle.nombre_categoria, "Herramientas Manuales")
        self.assertTrue(res_con_desc.detalle.tiene_descripcion)
        self.assertEqual(
            res_con_desc.detalle.descripcion,
            "Martillo de acero forjado con mango de fibra de vidrio.",
        )
        self.assertEqual(
            res_con_desc.detalle.descripcion_presentacion,
            "Martillo de acero forjado con mango de fibra de vidrio.",
        )

        # Producto con descripción opcional vacía (presentación neutra sin inventar datos)
        res_sin_desc = busqueda.consultar_detalle_producto(self.inventario, "MAR002")
        assert res_sin_desc.detalle is not None
        self.assertEqual(res_sin_desc.detalle.descripcion, "")
        self.assertFalse(res_sin_desc.detalle.tiene_descripcion)
        self.assertEqual(
            res_sin_desc.detalle.descripcion_presentacion,
            busqueda.TEXTO_SIN_DESCRIPCION,
        )

    def test_05_obtencion_de_rack_columna_nivel_y_posicion_principales(self) -> None:
        """Caso 5 (RF-006 / Sección 6): Obtiene Rack, Columna, Nivel y Posición de la asignación marcada como Principal."""
        # En self.inventario, para "0007", la primera fila en Asignaciones es U002 (Principal="No")
        # y la segunda fila es U001 (Principal="Sí"). Debe obtener U001 (R01, C02, N03, P04).
        res = busqueda.consultar_detalle_producto(self.inventario, "0007")
        assert res.detalle is not None
        prin = res.detalle.ubicacion_principal
        self.assertTrue(prin.es_principal)
        self.assertEqual(prin.ubicacion_id, "U001")
        self.assertEqual(prin.rack, "R01")
        self.assertEqual(prin.columna, "C02")
        self.assertEqual(prin.nivel, "N03")
        self.assertEqual(prin.posicion, "P04")
        self.assertEqual(
            prin.etiqueta_flechas,
            "Rack R01 → Columna C02 → Nivel N03 → Posición P04",
        )

    def test_06_distincion_entre_ubicacion_principal_y_secundaria(self) -> None:
        """Caso 6 (RF-007 / CA-005): Distingue claramente la ubicación principal de las secundarias."""
        res = busqueda.consultar_detalle_producto(self.inventario, "000125")
        assert res.detalle is not None
        self.assertTrue(res.detalle.ubicacion_principal.es_principal)
        self.assertEqual(res.detalle.ubicacion_principal.ubicacion_id, "U002")
        self.assertEqual(len(res.detalle.ubicaciones_secundarias), 1)
        sec = res.detalle.ubicaciones_secundarias[0]
        self.assertFalse(sec.es_principal)
        self.assertEqual(sec.ubicacion_id, "U004")
        self.assertNotEqual(
            res.detalle.ubicacion_principal.ubicacion_id,
            sec.ubicacion_id,
        )
        # En todas_las_ubicaciones, la primera es siempre la ubicación principal
        self.assertEqual(res.detalle.todas_las_ubicaciones[0], res.detalle.ubicacion_principal)
        self.assertEqual(res.detalle.todas_las_ubicaciones[1], sec)

    def test_07_producto_con_una_sola_ubicacion(self) -> None:
        """Caso 7 (Sección 7): Producto con una sola ubicación no muestra ubicaciones secundarias ficticias."""
        res = busqueda.consultar_detalle_producto(self.inventario, "MAR002")
        assert res.detalle is not None
        self.assertFalse(res.detalle.tiene_ubicaciones_secundarias)
        self.assertEqual(res.detalle.ubicaciones_secundarias, ())
        self.assertEqual(res.detalle.total_ubicaciones, 1)
        self.assertEqual(res.detalle.ubicacion_principal.ubicacion_id, "U003")

        # Verificación en la interfaz Streamlit con AppTest
        ruta_app = str(RUTA_APLICACION / "app.py")
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at = AppTest.from_file(ruta_app)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)

            at.button(key="btn_ver_detalle_MAR002").click()
            at.run(timeout=15)

            textos_caption = [c.value for c in at.caption]
            self.assertIn(busqueda.MENSAJE_SIN_UBICACIONES_SECUNDARIAS, textos_caption)
            textos_markdown = [m.value for m in at.markdown]
            self.assertFalse(any("Ubicación secundaria 1" in m for m in textos_markdown))

    def test_08_producto_con_varias_ubicaciones(self) -> None:
        """Caso 8 (RF-007 / CA-005): Producto con varias ubicaciones muestra principal y todas sus secundarias."""
        res = busqueda.consultar_detalle_producto(self.inventario, "0007")
        assert res.detalle is not None
        self.assertTrue(res.detalle.tiene_ubicaciones_secundarias)
        self.assertEqual(res.detalle.total_ubicaciones, 4)
        self.assertEqual(len(res.detalle.ubicaciones_secundarias), 3)

        # Verificación en la interfaz Streamlit con AppTest
        ruta_app = str(RUTA_APLICACION / "app.py")
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at = AppTest.from_file(ruta_app)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)

            at.button(key="btn_ver_detalle_0007").click()
            at.run(timeout=15)

            # Ubicación principal destacada en st.success
            textos_success = [s.value for s in at.success]
            self.assertTrue(
                any(
                    "Rack R01 → Columna C02 → Nivel N03 → Posición P04" in s
                    for s in textos_success
                )
            )
            # Las 3 ubicaciones secundarias aparecen en markdown
            textos_markdown = "\n".join(m.value for m in at.markdown)
            self.assertIn("Ubicación secundaria 1", textos_markdown)
            self.assertIn("Ubicación secundaria 2", textos_markdown)
            self.assertIn("Ubicación secundaria 3", textos_markdown)
            self.assertIn("Rack R01 → Columna C01 → Nivel N02 → Posición P01", textos_markdown)
            self.assertIn("Rack R02 → Columna C01 → Nivel N01 → Posición P02", textos_markdown)
            self.assertIn("Rack R03 → Columna C04 → Nivel N02 → Posición P05", textos_markdown)

    def test_09_ausencia_de_duplicaciones_entre_ubicaciones(self) -> None:
        """Caso 9 (Sección 7): La ubicación principal nunca se duplica en la lista secundaria."""
        res = busqueda.consultar_detalle_producto(self.inventario, "0007")
        assert res.detalle is not None
        id_prin = res.detalle.ubicacion_principal.ubicacion_id
        ids_sec = [u.ubicacion_id for u in res.detalle.ubicaciones_secundarias]
        self.assertNotIn(id_prin, ids_sec)
        self.assertEqual(len(ids_sec), len(set(ids_sec)))

        # Verificar también el filtro defensivo ante diccionarios con duplicados
        principal_raw = {"ubicacion_id": "U001", "rack": "R01", "columna": "C02", "nivel": "N03", "posicion": "P04"}
        secundarias_con_dup = [
            {"ubicacion_id": "U001", "rack": "R01", "columna": "C02", "nivel": "N03", "posicion": "P04"},
            {"ubicacion_id": "U002", "rack": "R02", "columna": "C01", "nivel": "N01", "posicion": "P02"},
            {"ubicacion_id": "U002", "rack": "R02", "columna": "C01", "nivel": "N01", "posicion": "P02"},
        ]
        depuradas = busqueda._ordenar_ubicaciones_secundarias_dict(
            secundarias_con_dup,
            ubicacion_principal=principal_raw,
        )
        self.assertEqual(len(depuradas), 1)
        self.assertEqual(depuradas[0]["ubicacion_id"], "U002")

    def test_10_orden_estable_de_ubicaciones_secundarias(self) -> None:
        """Caso 10 (Sección 7): Las ubicaciones secundarias mantienen un orden estable y reproducible."""
        inv_orden_a = _construir_inventario_detalles_controlado(invertir_orden_asignaciones=False)
        inv_orden_b = _construir_inventario_detalles_controlado(invertir_orden_asignaciones=True)

        det_a = busqueda.consultar_detalle_producto(inv_orden_a, "0007").detalle
        det_b = busqueda.consultar_detalle_producto(inv_orden_b, "0007").detalle
        assert det_a is not None and det_b is not None

        self.assertEqual(det_a.ubicacion_principal, det_b.ubicacion_principal)
        self.assertEqual(det_a.ubicaciones_secundarias, det_b.ubicaciones_secundarias)
        self.assertEqual(
            [u.ubicacion_id for u in det_a.ubicaciones_secundarias],
            ["U003", "U002", "U004"],
        )

    def test_11_regreso_desde_detalle_hacia_los_resultados(self) -> None:
        """Caso 11 (Sección 4.2): Permite regresar desde la vista de detalle hacia la lista de resultados."""
        estado_sesion: dict[str, Any] = {}
        app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "martillo",
            estado=estado_sesion,
            descargador_remoto=lambda config=gh.CONFIGURACION_POR_DEFECTO: self.lectura_base,
        )
        app_ferms.seleccionar_producto_en_sesion("0007", estado=estado_sesion)
        self.assertEqual(estado_sesion[app_ferms.CLAVE_PRODUCTO_SELECCIONADO], "0007")

        app_ferms.volver_a_resultados_en_sesion(estado=estado_sesion)
        self.assertIsNone(estado_sesion[app_ferms.CLAVE_PRODUCTO_SELECCIONADO])
        self.assertEqual(
            app_ferms.obtener_detalle_producto_en_sesion(estado=estado_sesion).estado,
            busqueda.EstadoDetalleProducto.SIN_SELECCION,
        )

        # Verificación en AppTest con el botón "⬅️ Volver a los resultados"
        ruta_app = str(RUTA_APLICACION / "app.py")
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at = AppTest.from_file(ruta_app)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)

            at.button(key="btn_ver_detalle_0007").click()
            at.run(timeout=15)
            self.assertEqual(at.session_state[app_ferms.CLAVE_PRODUCTO_SELECCIONADO], "0007")

            at.button(key="btn_volver_resultados").click()
            at.run(timeout=15)
            self.assertIsNone(at.session_state[app_ferms.CLAVE_PRODUCTO_SELECCIONADO])
            self.assertEqual(len(at.success), 1)
            self.assertIn("Mostrando 1–2 de 2", at.success[0].value)

    def test_12_conservacion_de_pagina_y_termino_de_busqueda(self) -> None:
        """Caso 12 (Sección 4.2 y 8.4): Abrir y cerrar detalle conserva el término buscado y la página actual."""
        inv_15 = _construir_inventario_paginado_15()
        lectura_15 = _crear_lectura_simulada(inv_15, sha="sha_15_martillos")

        ruta_app = str(RUTA_APLICACION / "app.py")
        with patch("github_inventario.descargar_inventario_remoto", return_value=lectura_15):
            at = AppTest.from_file(ruta_app)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)

            # Ir a la página 2 (productos 0011 a 0015)
            at.button(key="btn_pagina_siguiente").click()
            at.run(timeout=15)
            self.assertEqual(at.session_state[app_ferms.CLAVE_PAGINA_ACTUAL], 2)
            self.assertEqual(at.session_state[app_ferms.CLAVE_TERMINO_BUSCADO], "martillo")

            # Seleccionar el producto "0012" en la página 2
            at.button(key="btn_ver_detalle_0012").click()
            at.run(timeout=15)
            self.assertEqual(at.session_state[app_ferms.CLAVE_PRODUCTO_SELECCIONADO], "0012")
            self.assertEqual(at.session_state[app_ferms.CLAVE_PAGINA_ACTUAL], 2)
            self.assertEqual(at.session_state[app_ferms.CLAVE_TERMINO_BUSCADO], "martillo")

            # Volver a los resultados: debe permanecer en la página 2 de "martillo"
            at.button(key="btn_volver_resultados").click()
            at.run(timeout=15)
            self.assertIsNone(at.session_state[app_ferms.CLAVE_PRODUCTO_SELECCIONADO])
            self.assertEqual(at.session_state[app_ferms.CLAVE_PAGINA_ACTUAL], 2)
            self.assertEqual(at.session_state[app_ferms.CLAVE_TERMINO_BUSCADO], "martillo")
            self.assertIn("Mostrando 11–15 de 15", at.success[0].value)

    def test_13_eliminacion_de_la_seleccion_al_comenzar_otra_busqueda(self) -> None:
        """Caso 13 (Sección 4.3): Una nueva búsqueda descarta la selección previa y evita detalles obsoletos."""
        ruta_app = str(RUTA_APLICACION / "app.py")
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at = AppTest.from_file(ruta_app)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)

            # Abrir detalle de "0007"
            at.button(key="btn_ver_detalle_0007").click()
            at.run(timeout=15)
            self.assertEqual(at.session_state[app_ferms.CLAVE_PRODUCTO_SELECCIONADO], "0007")

            # Ejecutar nueva búsqueda ("tornillo") estando dentro de la vista de detalle
            at.text_input(key="campo_nombre_producto").input("tornillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)

            self.assertIsNone(at.session_state[app_ferms.CLAVE_PRODUCTO_SELECCIONADO])
            self.assertEqual(at.session_state[app_ferms.CLAVE_TERMINO_BUSCADO], "tornillo")
            self.assertEqual(len(at.success), 1)
            self.assertIn("para «tornillo»", at.success[0].value)
            # Ya no se muestra el encabezado de detalle de Martillo
            subtitulos = [s.value for s in at.subheader]
            self.assertFalse(any("Detalles del producto" in s for s in subtitulos))

    def test_14_prevencion_de_detalles_obsoletos_tras_errores_remotos(self) -> None:
        """Caso 14 (Sección 4.3 y 8.4): Un error remoto en una búsqueda nueva limpia la selección y el inventario."""
        estado_sesion: dict[str, Any] = {}
        app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "martillo",
            estado=estado_sesion,
            descargador_remoto=lambda config=gh.CONFIGURACION_POR_DEFECTO: self.lectura_base,
        )
        app_ferms.seleccionar_producto_en_sesion("0007", estado=estado_sesion)
        self.assertEqual(estado_sesion[app_ferms.CLAVE_PRODUCTO_SELECCIONADO], "0007")

        def descargador_error(
            config: gh.ConfiguracionRepositorioGitHub = gh.CONFIGURACION_POR_DEFECTO,
        ) -> gh.ResultadoLecturaInventarioRemoto:
            raise gh.ErrorConexionRedGitHub("Error de conexión simulado", es_reintentable=True)

        r_error = app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "cinta",
            estado=estado_sesion,
            descargador_remoto=descargador_error,
        )
        self.assertEqual(
            r_error.estado_operativo,
            app_ferms.EstadoOperativoInterfaz.ERROR_CONEXION_O_AUTORIZACION,
        )
        self.assertIsNone(estado_sesion[app_ferms.CLAVE_PRODUCTO_SELECCIONADO])
        self.assertIsNone(estado_sesion[app_ferms.CLAVE_INVENTARIO_SESION])
        self.assertIsNone(estado_sesion[app_ferms.CLAVE_SHA_SESION])

        # Incluso si alguien intentara pedir el detalle en ese estado de error, no hay datos obsoletos
        estado_sesion[app_ferms.CLAVE_PRODUCTO_SELECCIONADO] = "0007"
        res_obsoleto = app_ferms.obtener_detalle_producto_en_sesion(estado=estado_sesion)
        self.assertEqual(
            res_obsoleto.estado,
            busqueda.EstadoDetalleProducto.PRODUCTO_NO_DISPONIBLE,
        )
        self.assertIsNone(res_obsoleto.detalle)

    def test_15_manejo_de_codigos_de_producto_invalidos_e_inconsistencias_de_integridad(self) -> None:
        """Caso 15 (Secciones 4.4 y 6): Rechaza códigos inválidos o ajenos a la búsqueda y detecta fallos de integridad."""
        estado_sesion: dict[str, Any] = {}
        app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "martillo",
            estado=estado_sesion,
            descargador_remoto=lambda config=gh.CONFIGURACION_POR_DEFECTO: self.lectura_base,
        )

        # 1. Código inexistente en el inventario
        res_inexistente = app_ferms.seleccionar_producto_en_sesion(
            "CODIGO_INEXISTENTE_999", estado=estado_sesion
        )
        self.assertEqual(
            res_inexistente.estado,
            busqueda.EstadoDetalleProducto.PRODUCTO_NO_DISPONIBLE,
        )
        self.assertIsNone(res_inexistente.detalle)
        self.assertEqual(
            res_inexistente.mensaje_usuario,
            busqueda.MENSAJE_PRODUCTO_SELECCIONADO_NO_DISPONIBLE,
        )

        # 2. Código que existe en el inventario ("TOR010"), pero NO pertenece a la búsqueda activa ("martillo")
        res_ajeno = app_ferms.seleccionar_producto_en_sesion("TOR010", estado=estado_sesion)
        self.assertEqual(
            res_ajeno.estado,
            busqueda.EstadoDetalleProducto.PRODUCTO_NO_DISPONIBLE,
        )
        self.assertIsNone(res_ajeno.detalle)

        # 3. Verificación en AppTest: muestra advertencia y permite volver a los resultados
        ruta_app = str(RUTA_APLICACION / "app.py")
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at = AppTest.from_file(ruta_app)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)

            at.session_state[app_ferms.CLAVE_PRODUCTO_SELECCIONADO] = "CODIGO_INVALIDO"
            at.run(timeout=15)
            self.assertEqual(len(at.warning), 1)
            self.assertEqual(
                at.warning[0].value,
                busqueda.MENSAJE_PRODUCTO_SELECCIONADO_NO_DISPONIBLE,
            )
            at.button(key="btn_volver_resultados").click()
            at.run(timeout=15)
            self.assertIsNone(at.session_state[app_ferms.CLAVE_PRODUCTO_SELECCIONADO])

        # 4. Inconsistencia de integridad en memoria (p. ej. producto con dos ubicaciones principales)
        hojas_corruptas = self.inventario.obtener_hojas()
        df_asig_corrupta = hojas_corruptas[motor.HOJA_ASIGNACIONES].copy()
        df_asig_corrupta["Principal"] = "Sí"
        inv_manipulado = motor.InventarioDatos(
            productos=hojas_corruptas[motor.HOJA_PRODUCTOS],
            categorias=hojas_corruptas[motor.HOJA_CATEGORIAS],
            ubicaciones=hojas_corruptas[motor.HOJA_UBICACIONES],
            asignaciones=df_asig_corrupta,
        )
        res_integridad = busqueda.consultar_detalle_producto(inv_manipulado, "0007")
        self.assertEqual(
            res_integridad.estado,
            busqueda.EstadoDetalleProducto.ERROR_INTEGRIDAD_UBICACION,
        )
        self.assertIsNone(res_integridad.detalle)
        self.assertEqual(
            res_integridad.mensaje_usuario,
            busqueda.MENSAJE_ERROR_INTEGRIDAD_DETALLE,
        )

    def test_16_ausencia_de_controles_administrativos_de_venta_o_ia(self) -> None:
        """Caso 16 (Secciones 5, 7 y 9): La vista de detalle no incluye controles de venta, stock, login ni IA."""
        ruta_app = str(RUTA_APLICACION / "app.py")
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at = AppTest.from_file(ruta_app)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)
            at.button(key="btn_ver_detalle_0007").click()
            at.run(timeout=15)

            etiquetas_botones = [b.label.lower() for b in at.button]
            terminos_prohibidos_botones = (
                "comprar",
                "carrito",
                "agregar",
                "editar",
                "eliminar",
                "guardar",
                "login",
                "iniciar sesión",
                "precio",
                "stock",
            )
            for etq in etiquetas_botones:
                for prohibido in terminos_prohibidos_botones:
                    self.assertNotIn(prohibido, etq)

            textos_vista = "\n".join(
                [m.value.lower() for m in at.markdown]
                + [c.value.lower() for c in at.caption]
            )
            for termino_comercial in ("precio:", "stock:", "unidades disponibles", "añadir al carrito"):
                self.assertNotIn(termino_comercial, textos_vista)


class TestIntegracionDetallesInventarioBusquedaYApp(unittest.TestCase):
    """Sección 10 — Pruebas de integración entre `inventario.py`, `busqueda.py`, `github_inventario.py` y `app.py`."""

    def setUp(self) -> None:
        self.inventario = _construir_inventario_detalles_controlado()
        self.lectura_base = _crear_lectura_simulada(self.inventario)

    def test_01_compatibilidad_con_inventario_py(self) -> None:
        """Verifica que `consultar_detalle_producto` delegue en `obtener_producto_por_codigo` de `inventario.py`."""
        inv_demo = motor.crear_inventario_demostrativo()
        with patch(
            "busqueda.obtener_producto_por_codigo",
            wraps=motor.obtener_producto_por_codigo,
        ) as spy_obtener:
            res = busqueda.consultar_detalle_producto(inv_demo, "000125")
            self.assertEqual(res.estado, busqueda.EstadoDetalleProducto.DETALLE_DISPONIBLE)
            spy_obtener.assert_called_once_with(inv_demo, "000125")

        assert res.detalle is not None
        datos_directos = motor.obtener_producto_por_codigo(inv_demo, "000125")
        assert datos_directos is not None
        self.assertEqual(res.detalle.codigo_producto, datos_directos["codigo_producto"])
        self.assertEqual(res.detalle.nombre, datos_directos["nombre"])
        self.assertEqual(res.detalle.nombre_categoria, datos_directos["nombre_categoria"])
        self.assertEqual(
            res.detalle.ubicacion_principal.ubicacion_id,
            datos_directos["ubicacion_principal"]["ubicacion_id"],
        )

    def test_02_compatibilidad_con_busqueda_py(self) -> None:
        """Verifica la consistencia entre `ejecutar_busqueda_productos` y `consultar_detalle_producto`."""
        res_busq = busqueda.ejecutar_busqueda_productos(self.inventario, "martillo")
        self.assertEqual(res_busq.estado, busqueda.EstadoBusqueda.CON_RESULTADOS)

        for prod_coincidente in res_busq.todos_los_resultados:
            res_det = busqueda.consultar_detalle_producto(
                self.inventario,
                prod_coincidente.codigo_producto,
                resultados_activos=res_busq.todos_los_resultados,
            )
            self.assertEqual(res_det.estado, busqueda.EstadoDetalleProducto.DETALLE_DISPONIBLE)
            assert res_det.detalle is not None
            self.assertEqual(res_det.detalle.codigo_producto, prod_coincidente.codigo_producto)
            self.assertEqual(res_det.detalle.nombre, prod_coincidente.nombre)
            self.assertEqual(res_det.detalle.nombre_categoria, prod_coincidente.nombre_categoria)
            assert prod_coincidente.ubicacion_principal is not None
            self.assertEqual(
                res_det.detalle.ubicacion_principal.ubicacion_id,
                prod_coincidente.ubicacion_principal["ubicacion_id"],
            )
            self.assertEqual(
                [u.ubicacion_id for u in res_det.detalle.ubicaciones_secundarias],
                [u["ubicacion_id"] for u in prod_coincidente.ubicaciones_secundarias],
            )

    def test_03_uso_del_inventario_previamente_validado_en_sesion(self) -> None:
        """Verifica que la vista de detalle utilice el objeto `InventarioDatos` validado de la búsqueda activa."""
        estado_sesion: dict[str, Any] = {}
        app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "martillo",
            estado=estado_sesion,
            descargador_remoto=lambda config=gh.CONFIGURACION_POR_DEFECTO: self.lectura_base,
        )
        self.assertIs(estado_sesion[app_ferms.CLAVE_INVENTARIO_SESION], self.inventario)

        res_det = app_ferms.seleccionar_producto_en_sesion("0007", estado=estado_sesion)
        self.assertTrue(res_det.tiene_detalle)
        assert res_det.detalle is not None
        self.assertEqual(res_det.detalle.codigo_producto, "0007")

    def test_04_ausencia_de_descargas_innecesarias_al_abrir_y_cerrar_detalles(self) -> None:
        """Sección 4.2 y 10: Abrir y cerrar detalles no vuelve a descargar el inventario desde GitHub."""
        conteo_descargas = {"n": 0}

        def descargador_contado(
            config: gh.ConfiguracionRepositorioGitHub = gh.CONFIGURACION_POR_DEFECTO,
        ) -> gh.ResultadoLecturaInventarioRemoto:
            conteo_descargas["n"] += 1
            return self.lectura_base

        ruta_app = str(RUTA_APLICACION / "app.py")
        with patch("github_inventario.descargar_inventario_remoto", side_effect=descargador_contado):
            at = AppTest.from_file(ruta_app)
            at.run(timeout=15)
            self.assertEqual(conteo_descargas["n"], 0)

            # 1. Ejecutar búsqueda: 1 descarga desde GitHub
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)
            self.assertEqual(conteo_descargas["n"], 1)

            # 2. Abrir detalle del producto "0007": 0 descargas adicionales
            at.button(key="btn_ver_detalle_0007").click()
            at.run(timeout=15)
            self.assertEqual(conteo_descargas["n"], 1)

            # 3. Volver a los resultados: 0 descargas adicionales
            at.button(key="btn_volver_resultados").click()
            at.run(timeout=15)
            self.assertEqual(conteo_descargas["n"], 1)

            # 4. Abrir detalle del segundo producto "MAR002" y volver: 0 descargas adicionales
            at.button(key="btn_ver_detalle_MAR002").click()
            at.run(timeout=15)
            self.assertEqual(conteo_descargas["n"], 1)

            at.button(key="btn_volver_resultados").click()
            at.run(timeout=15)
            self.assertEqual(conteo_descargas["n"], 1)

    def test_05_distincion_entre_inventario_real_y_datos_demostrativos(self) -> None:
        """Sección 8.3: Si el inventario remoto no existe o falla, no se muestran datos demostrativos."""
        error_no_init = gh.ErrorArchivoRemotoInexistente(
            "El archivo maestro todavía no existe en GitHub."
        )
        with patch("github_inventario.descargar_inventario_remoto", side_effect=error_no_init):
            ruta_app = str(RUTA_APLICACION / "app.py")
            at = AppTest.from_file(ruta_app)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)

            self.assertIsNone(at.session_state[app_ferms.CLAVE_INVENTARIO_SESION])
            self.assertIsNone(at.session_state[app_ferms.CLAVE_PRODUCTO_SELECCIONADO])
            textos_totales = "\n".join(
                [m.value for m in at.markdown]
                + [w.value for w in at.warning]
                + [c.value for c in at.caption]
            )
            self.assertNotIn("[DEMOSTRATIVO]", textos_totales)
            self.assertNotIn("MAR001", textos_totales)

    def test_06_ausencia_de_modificaciones_al_archivo_maestro(self) -> None:
        """Verifica que `03_Aplicacion/inventario.xlsx` no ha sido creado ni modificado."""
        self.assertFalse(
            RUTA_MAESTRO_DEFINITIVO.exists(),
            "No debe crearse `03_Aplicacion/inventario.xlsx` durante el Prompt 05.",
        )

    def test_07_ausencia_de_operaciones_remotas_de_escritura_y_gemini(self) -> None:
        """Verifica que `app.py` y `busqueda.py` no contienen escrituras HTTP ni llamadas a Gemini API."""
        for nombre_modulo in ("app.py", "busqueda.py"):
            ruta = RUTA_APLICACION / nombre_modulo
            codigo = ruta.read_text(encoding="utf-8")
            arbol = ast.parse(codigo, filename=str(ruta))

            for metodo_http in (
                '"PUT"',
                '"POST"',
                '"DELETE"',
                '"PATCH"',
                "'PUT'",
                "'POST'",
                "'DELETE'",
                "'PATCH'",
            ):
                self.assertNotIn(metodo_http, codigo)

            for nodo in ast.walk(arbol):
                if isinstance(nodo, ast.Import):
                    for alias in nodo.names:
                        self.assertFalse(
                            alias.name.startswith("google") or "genai" in alias.name
                        )
                elif isinstance(nodo, ast.ImportFrom) and nodo.module:
                    self.assertFalse(
                        nodo.module.startswith("google") or "genai" in nodo.module
                    )

            self.assertNotIn("GEMINI_API_KEY", codigo)
            self.assertNotIn("generate_content", codigo)


if __name__ == "__main__":
    unittest.main()

