"""Pruebas automatizadas funcionales y de integración para la interfaz responsive y el área visual de Gemini «Próximamente».

Proyecto: FerreteríaMS v0
Tarea: FERMS-V0-P06
Módulos probados: `03_Aplicacion/app.py` y `03_Aplicacion/estilos.css`
(integrados con `03_Aplicacion/busqueda.py`, `03_Aplicacion/inventario.py` y `03_Aplicacion/github_inventario.py`).
Requisitos cubiertos: RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007, RF-008,
RF-009, RF-010, RF-024, RF-025, RF-028, RF-032, RF-033, RF-034, RF-035, RF-036, RF-037, RF-038.
Criterios cubiertos: CA-001, CA-002, CA-003, CA-004, CA-005, CA-006, CA-007, CA-008,
CA-031, CA-032, CA-033, CA-034, CA-039, CA-040, CA-041, CA-042, CA-043, CA-060, CA-061.

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
RUTA_APP_PY = RUTA_APLICACION / "app.py"
RUTA_ESTILOS_CSS = RUTA_APLICACION / "estilos.css"
RUTA_MAESTRO_DEFINITIVO = RUTA_APLICACION / "inventario.xlsx"
BYTES_MAESTRO_INICIAL = (
    RUTA_MAESTRO_DEFINITIVO.read_bytes() if RUTA_MAESTRO_DEFINITIVO.exists() else None
)

if str(RUTA_APLICACION) not in sys.path:
    sys.path.insert(0, str(RUTA_APLICACION))

import app as app_ferms  # noqa: E402
import busqueda  # noqa: E402
import github_inventario as gh  # noqa: E402
import inventario as motor  # noqa: E402


def _construir_inventario_p06(total_extra_martillos: int = 0) -> motor.InventarioDatos:
    """Construye un `InventarioDatos` controlado con ubicaciones principal y secundarias para pruebas de interfaz."""
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
        ]
    )
    filas_productos: list[dict[str, str]] = [
        {
            "Codigo_Producto": "0007",
            "Nombre": "Martillo de uña profesional con mango ergonómico reforzado",
            "Categoria_ID": "CAT01",
            "Descripcion": "Martillo de acero forjado para carpintería, obra y taller.",
        },
        {
            "Codigo_Producto": "MAR002",
            "Nombre": "Martillo de goma 16 oz",
            "Categoria_ID": "CAT01",
            "Descripcion": "",
        },
        {
            "Codigo_Producto": "000125",
            "Nombre": "Cinta aislante eléctrica negra",
            "Categoria_ID": "CAT03",
            "Descripcion": "Cinta aislante de PVC.",
        },
    ]
    filas_asignaciones: list[dict[str, str]] = [
        {"Codigo_Producto": "0007", "Ubicacion_ID": "U002", "Principal": "No"},
        {"Codigo_Producto": "0007", "Ubicacion_ID": "U001", "Principal": "Sí"},
        {"Codigo_Producto": "0007", "Ubicacion_ID": "U003", "Principal": "No"},
        {"Codigo_Producto": "MAR002", "Ubicacion_ID": "U003", "Principal": "Sí"},
        {"Codigo_Producto": "000125", "Ubicacion_ID": "U001", "Principal": "Sí"},
    ]

    for idx in range(1, total_extra_martillos + 1):
        cod = f"MAR1{idx:02d}"
        filas_productos.append(
            {
                "Codigo_Producto": cod,
                "Nombre": f"Martillo serie especial modelo {idx:02d}",
                "Categoria_ID": "CAT01",
                "Descripcion": f"Martillo de prueba serie {idx:02d}.",
            }
        )
        filas_asignaciones.append(
            {
                "Codigo_Producto": cod,
                "Ubicacion_ID": "U001" if idx % 2 == 1 else "U002",
                "Principal": "Sí",
            }
        )

    return motor.construir_inventario_datos(
        {
            motor.HOJA_PRODUCTOS: pd.DataFrame(filas_productos),
            motor.HOJA_CATEGORIAS: df_categorias,
            motor.HOJA_UBICACIONES: df_ubicaciones,
            motor.HOJA_ASIGNACIONES: pd.DataFrame(filas_asignaciones),
        }
    )


def _crear_lectura_remota(
    inventario: motor.InventarioDatos,
    sha: str = "sha_p06_simulado",
) -> gh.ResultadoLecturaInventarioRemoto:
    return gh.ResultadoLecturaInventarioRemoto(
        propietario="JunyMSAI",
        repositorio="FerreteriaMS",
        rama="main",
        ruta_archivo="03_Aplicacion/inventario.xlsx",
        sha_github=sha,
        sha256_local="hash_local_p06",
        tamano_bytes=2048,
        inventario=inventario,
    )


class TestInterfazResponsiveYGeminiFuncional(unittest.TestCase):
    """Sección 10.2 del Prompt 06 — 17 pruebas funcionales obligatorias y verificaciones de estilo/accesibilidad."""

    def setUp(self) -> None:
        self.inventario_base = _construir_inventario_p06(total_extra_martillos=0)
        self.inventario_paginado = _construir_inventario_p06(total_extra_martillos=12)
        self.lectura_base = _crear_lectura_remota(self.inventario_base)
        self.lectura_paginada = _crear_lectura_remota(self.inventario_paginado)
        self.ruta_app_str = str(RUTA_APP_PY)

    def test_01_renderizado_de_la_aplicacion_sin_errores(self) -> None:
        """Caso 1 (CA-034): La aplicación se renderiza inicialmente sin lanzar excepciones."""
        at = AppTest.from_file(self.ruta_app_str)
        at.run(timeout=15)
        self.assertFalse(at.exception, f"Excepción inesperada al renderizar app.py: {at.exception}")

    def test_02_presencia_del_nombre_ferreteriams_y_descripcion(self) -> None:
        """Caso 2 (Sección 5.1 y 5.2): Presenta el nombre FerreteríaMS y descripción de su propósito."""
        at = AppTest.from_file(self.ruta_app_str)
        at.run(timeout=15)
        titulos = [t.value for t in at.title]
        self.assertTrue(any("FerreteríaMS" in t for t in titulos))
        captions = [c.value for c in at.caption]
        self.assertTrue(any("Busca productos por su nombre" in c for c in captions))
        markdowns = "\n".join(m.value for m in at.markdown)
        self.assertIn("ferms-banner-encabezado", markdowns)

    def test_03_presencia_del_campo_de_busqueda_unico(self) -> None:
        """Caso 3 (RF-001, CA-043, Sección 5.3): Existe un único campo de búsqueda por nombre sin filtros extra."""
        at = AppTest.from_file(self.ruta_app_str)
        at.run(timeout=15)
        self.assertEqual(len(at.text_input), 1)
        campo = at.text_input(key="campo_nombre_producto")
        self.assertEqual(campo.placeholder, app_ferms.PLACEHOLDER_CAMPO_BUSQUEDA)
        self.assertEqual(campo.label, busqueda.MENSAJE_INICIAL_BUSQUEDA)
        self.assertEqual(len(at.selectbox), 0)
        self.assertEqual(len(at.multiselect), 0)
        self.assertEqual(len(at.radio), 0)

    def test_04_funcionamiento_del_boton_buscar(self) -> None:
        """Caso 4 (RF-001, RF-004, CA-001): El botón Buscar ejecuta la consulta y actualiza los resultados."""
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at = AppTest.from_file(self.ruta_app_str)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)

            self.assertFalse(at.exception)
            self.assertEqual(len(at.success), 1)
            self.assertIn("Mostrando 1–2 de 2", at.success[0].value)

    def test_05_presentacion_de_tarjetas_de_resultados(self) -> None:
        """Caso 5 (RF-004, Sección 5.4): Cada tarjeta muestra Nombre, Código, Categoría y botón de detalle."""
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at = AppTest.from_file(self.ruta_app_str)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)

            textos_md = "\n".join(m.value for m in at.markdown)
            textos_cap = "\n".join(c.value for c in at.caption)
            self.assertIn("Martillo de uña profesional con mango ergonómico reforzado", textos_md)
            self.assertIn("Código: 0007", textos_md)
            self.assertIn("Categoría: Herramientas Manuales", textos_cap)
            boton = at.button(key="btn_ver_detalle_0007")
            self.assertEqual(boton.label, "Ver detalles y ubicación")

    def test_06_funcionamiento_de_la_paginacion(self) -> None:
        """Caso 6 (RF-036, CA-040): Paginación de diez resultados por página y navegación Anterior/Siguiente."""
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_paginada):
            at = AppTest.from_file(self.ruta_app_str)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)

            self.assertIn("Mostrando 1–10 de 14", at.success[0].value)
            self.assertTrue(at.button(key="btn_pagina_anterior").disabled)
            self.assertFalse(at.button(key="btn_pagina_siguiente").disabled)

            at.button(key="btn_pagina_siguiente").click()
            at.run(timeout=15)
            self.assertIn("Mostrando 11–14 de 14", at.success[0].value)
            self.assertFalse(at.button(key="btn_pagina_anterior").disabled)
            self.assertTrue(at.button(key="btn_pagina_siguiente").disabled)

    def test_07_seleccion_de_productos(self) -> None:
        """Caso 7 (RF-004, RF-005): Seleccionar un producto registra su código exacto en sesión y abre el detalle."""
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at = AppTest.from_file(self.ruta_app_str)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)

            at.button(key="btn_ver_detalle_0007").click()
            at.run(timeout=15)
            self.assertEqual(at.session_state[app_ferms.CLAVE_PRODUCTO_SELECCIONADO], "0007")

    def test_08_presentacion_de_detalles(self) -> None:
        """Caso 8 (RF-005, Sección 5.5): Muestra Nombre, Código con ceros iniciales, Categoría y Descripción."""
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at = AppTest.from_file(self.ruta_app_str)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)
            at.button(key="btn_ver_detalle_0007").click()
            at.run(timeout=15)

            textos_md = "\n".join(m.value for m in at.markdown)
            self.assertIn("Martillo de uña profesional con mango ergonómico reforzado", textos_md)
            self.assertIn("0007", textos_md)
            self.assertIn("Herramientas Manuales", textos_md)
            self.assertIn("Martillo de acero forjado para carpintería, obra y taller.", textos_md)

    def test_09_ubicacion_principal_y_secundarias(self) -> None:
        """Caso 9 (RF-006, RF-007, CA-005, Sección 5.5): Destaca la ubicación principal y diferencia las secundarias."""
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at = AppTest.from_file(self.ruta_app_str)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)
            at.button(key="btn_ver_detalle_0007").click()
            at.run(timeout=15)

            textos_success = "\n".join(s.value for s in at.success)
            self.assertIn("Rack R01 → Columna C02 → Nivel N03 → Posición P04", textos_success)

            textos_md = "\n".join(m.value for m in at.markdown)
            self.assertIn("Ubicación secundaria 1", textos_md)
            self.assertIn("Ubicación secundaria 2", textos_md)
            self.assertIn("Rack R01 → Columna C01 → Nivel N02 → Posición P01", textos_md)
            self.assertIn("Rack R02 → Columna C01 → Nivel N01 → Posición P02", textos_md)

    def test_10_regreso_a_resultados(self) -> None:
        """Caso 10 (Sección 5.5): El botón de regreso vuelve a la lista de productos."""
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at = AppTest.from_file(self.ruta_app_str)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)
            at.button(key="btn_ver_detalle_0007").click()
            at.run(timeout=15)

            at.button(key="btn_volver_resultados").click()
            at.run(timeout=15)
            self.assertIsNone(at.session_state[app_ferms.CLAVE_PRODUCTO_SELECCIONADO])
            self.assertEqual(len(at.success), 1)
            self.assertIn("Mostrando 1–2 de 2", at.success[0].value)

    def test_11_conservacion_del_estado_de_busqueda_sin_descargas_adicionales(self) -> None:
        """Caso 11 (Sección 9): Cambiar de página y abrir/cerrar detalles conserva el estado sin recargar GitHub."""
        llamadas_github = {"n": 0}

        def descargador_espia(
            config: gh.ConfiguracionRepositorioGitHub = gh.CONFIGURACION_POR_DEFECTO,
        ) -> gh.ResultadoLecturaInventarioRemoto:
            llamadas_github["n"] += 1
            return self.lectura_paginada

        with patch("github_inventario.descargar_inventario_remoto", side_effect=descargador_espia):
            at = AppTest.from_file(self.ruta_app_str)
            at.run(timeout=15)
            self.assertEqual(llamadas_github["n"], 0)

            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)
            self.assertEqual(llamadas_github["n"], 1)

            # Avanzar a página 2
            at.button(key="btn_pagina_siguiente").click()
            at.run(timeout=15)
            self.assertEqual(llamadas_github["n"], 1)
            self.assertEqual(at.session_state[app_ferms.CLAVE_PAGINA_ACTUAL], 2)

            # Seleccionar un producto de la página 2 y regresar
            producto_p2 = at.session_state[app_ferms.CLAVE_RESPUESTA_BUSQUEDA].resultado_busqueda.resultados_pagina[0]
            at.button(key=f"btn_ver_detalle_{producto_p2.codigo_producto}").click()
            at.run(timeout=15)
            self.assertEqual(llamadas_github["n"], 1)

            at.button(key="btn_volver_resultados").click()
            at.run(timeout=15)
            self.assertEqual(llamadas_github["n"], 1)
            self.assertEqual(at.session_state[app_ferms.CLAVE_PAGINA_ACTUAL], 2)
            self.assertEqual(at.session_state[app_ferms.CLAVE_TERMINO_BUSCADO], "martillo")

    def test_12_mensajes_de_error_busqueda_vacia_sin_coincidencias_y_ausencia_de_inventario(self) -> None:
        """Caso 12 (RF-008, RF-037, RF-038, CA-006, CA-041, CA-042): Verifica todos los estados y errores."""
        # 1. Búsqueda vacía
        at_vacio = AppTest.from_file(self.ruta_app_str)
        at_vacio.run(timeout=15)
        at_vacio.button(key="btn_ejecutar_busqueda").click()
        at_vacio.run(timeout=15)
        self.assertEqual(len(at_vacio.warning), 1)
        self.assertEqual(at_vacio.warning[0].value, busqueda.MENSAJE_BUSQUEDA_VACIA)

        # 2. Sin coincidencias
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at_sin = AppTest.from_file(self.ruta_app_str)
            at_sin.run(timeout=15)
            at_sin.text_input(key="campo_nombre_producto").input("compresor_inexistente_xyz")
            at_sin.button(key="btn_ejecutar_busqueda").click()
            at_sin.run(timeout=15)
            infos = [i.value for i in at_sin.info]
            self.assertIn("No encontramos este producto en nuestro inventario", infos)

        # 3. Inventario no inicializado en GitHub
        with patch(
            "github_inventario.descargar_inventario_remoto",
            side_effect=gh.ErrorArchivoRemotoInexistente("No existe inventario.xlsx"),
        ):
            at_no_init = AppTest.from_file(self.ruta_app_str)
            at_no_init.run(timeout=15)
            at_no_init.text_input(key="campo_nombre_producto").input("martillo")
            at_no_init.button(key="btn_ejecutar_busqueda").click()
            at_no_init.run(timeout=15)
            self.assertEqual(len(at_no_init.warning), 1)
            self.assertEqual(at_no_init.warning[0].value, app_ferms.MENSAJE_INVENTARIO_NO_INICIALIZADO)
            self.assertIsNotNone(at_no_init.button(key="btn_reintentar_no_inicializado"))

        # 4. Error técnico de conexión/autorización
        with patch(
            "github_inventario.descargar_inventario_remoto",
            side_effect=gh.ErrorConexionRedGitHub("Fallo de red simulado"),
        ):
            at_err = AppTest.from_file(self.ruta_app_str)
            at_err.run(timeout=15)
            at_err.text_input(key="campo_nombre_producto").input("martillo")
            at_err.button(key="btn_ejecutar_busqueda").click()
            at_err.run(timeout=15)
            self.assertEqual(len(at_err.error), 1)
            self.assertEqual(at_err.error[0].value, app_ferms.MENSAJE_ERROR_TECNICO_CONSULTA)
            self.assertIsNotNone(at_err.button(key="btn_reintentar_error_tecnico"))

        # 5. Inventario remoto inválido
        with patch(
            "github_inventario.descargar_inventario_remoto",
            side_effect=gh.ErrorEsquemaInventarioRemoto("Esquema inválido"),
        ):
            at_inv = AppTest.from_file(self.ruta_app_str)
            at_inv.run(timeout=15)
            at_inv.text_input(key="campo_nombre_producto").input("martillo")
            at_inv.button(key="btn_ejecutar_busqueda").click()
            at_inv.run(timeout=15)
            self.assertEqual(len(at_inv.error), 1)
            self.assertEqual(at_inv.error[0].value, app_ferms.MENSAJE_INVENTARIO_REMOTO_INVALIDO)
            self.assertIsNotNone(at_inv.button(key="btn_reintentar_invalido"))

    def test_13_presencia_del_area_gemini_proximamente_en_todos_los_estados(self) -> None:
        """Caso 13 (RF-032, RF-033, CA-031, Sección 6): El área Asistente Gemini — Próximamente está visible."""
        # Estado inicial
        at = AppTest.from_file(self.ruta_app_str)
        at.run(timeout=15)
        subtitulos = [s.value for s in at.subheader]
        self.assertTrue(any("Asistente Gemini" in s for s in subtitulos))

        markdowns = "\n".join(m.value for m in at.markdown)
        self.assertIn("Asistente Gemini", markdowns)
        self.assertIn("Próximamente", markdowns)
        self.assertIn(app_ferms.SUBTITULO_GEMINI_V0, markdowns)
        self.assertIn(app_ferms.DESCRIPCION_GEMINI_V0, markdowns)

        # Estado con resultados y vista de detalle
        with patch("github_inventario.descargar_inventario_remoto", return_value=self.lectura_base):
            at_det = AppTest.from_file(self.ruta_app_str)
            at_det.run(timeout=15)
            at_det.text_input(key="campo_nombre_producto").input("martillo")
            at_det.button(key="btn_ejecutar_busqueda").click()
            at_det.run(timeout=15)
            at_det.button(key="btn_ver_detalle_0007").click()
            at_det.run(timeout=15)

            subtitulos_det = [s.value for s in at_det.subheader]
            self.assertTrue(any("Asistente Gemini" in s for s in subtitulos_det))
            md_det = "\n".join(m.value for m in at_det.markdown)
            self.assertIn("Próximamente", md_det)

    def test_14_ausencia_de_chat_gemini_operativo(self) -> None:
        """Caso 14 (RF-034, CA-033, Sección 6.3): No existen controles de chat ni respuestas simuladas de IA."""
        at = AppTest.from_file(self.ruta_app_str)
        at.run(timeout=15)

        self.assertEqual(len(at.chat_input), 0)
        self.assertEqual(len(at.chat_message), 0)
        # Solo existe un campo de texto en toda la aplicación: el buscador de productos por nombre
        self.assertEqual(len(at.text_input), 1)
        self.assertEqual(at.text_input[0].key, "campo_nombre_producto")
        self.assertEqual(len(at.text_area), 0)

        # No existe ningún botón para enviar mensajes a Gemini
        for boton in at.button:
            etiqueta_min = boton.label.lower()
            self.assertNotIn("gemini", etiqueta_min)
            self.assertNotIn("enviar", etiqueta_min)
            self.assertNotIn("preguntar", etiqueta_min)
            self.assertNotIn("consultar ia", etiqueta_min)

    def test_15_ausencia_de_importaciones_o_llamadas_a_gemini_api(self) -> None:
        """Caso 15 (RF-034, CA-032, CA-033, Sección 6.3): Ningún módulo importa `google-genai` ni exige API key."""
        for nombre_archivo in ("app.py", "busqueda.py", "inventario.py", "github_inventario.py"):
            ruta = RUTA_APLICACION / nombre_archivo
            contenido = ruta.read_text(encoding="utf-8")
            arbol = ast.parse(contenido, filename=str(ruta))

            for nodo in ast.walk(arbol):
                if isinstance(nodo, ast.Import):
                    for alias in nodo.names:
                        self.assertFalse(
                            alias.name.startswith("google") or "genai" in alias.name,
                            f"Importación prohibida en {nombre_archivo}: {alias.name}",
                        )
                elif isinstance(nodo, ast.ImportFrom) and nodo.module:
                    self.assertFalse(
                        nodo.module.startswith("google") or "genai" in nodo.module,
                        f"Importación prohibida en {nombre_archivo}: {nodo.module}",
                    )

            for cadena_prohibida in (
                "GEMINI_API_KEY",
                "GOOGLE_API_KEY",
                "generate_content",
                "genai.Client",
                "chat_input",
                "chat_message",
            ):
                self.assertNotIn(
                    cadena_prohibida,
                    contenido,
                    f"Referencia prohibida '{cadena_prohibida}' encontrada en {nombre_archivo}",
                )

    def test_16_ausencia_de_controles_comerciales_pwa_y_administrativos_no_autorizados(self) -> None:
        """Caso 16 (Secciones 5.2, 7.5 y 12, CA-060, CA-061): Sin comercio electrónico, login ni PWA instalable."""
        at = AppTest.from_file(self.ruta_app_str)
        at.run(timeout=15)

        textos_totales = "\n".join(
            [m.value.lower() for m in at.markdown]
            + [c.value.lower() for c in at.caption]
            + [b.label.lower() for b in at.button]
        )
        terminos_prohibidos = (
            "añadir al carrito",
            "agregar al carrito",
            "comprar ahora",
            "precio:",
            "unidades en stock",
            "iniciar sesión como administrador",
            "nuevo producto",
            "serviceworker",
            "manifest.json",
        )
        for prohibido in terminos_prohibidos:
            self.assertNotIn(prohibido, textos_totales)

        # Verificar que no se crearon archivos de PWA (manifest o service worker)
        for archivo in RUTA_APLICACION.iterdir():
            nombre_low = archivo.name.lower()
            self.assertNotIn("manifest", nombre_low)
            self.assertNotIn("service-worker", nombre_low)
            self.assertNotIn("sw.js", nombre_low)

    def test_17_ausencia_de_operaciones_remotas_de_escritura_y_archivo_maestro(self) -> None:
        """Caso 17 (Sección 10.2 y 12): No se modifica `inventario.xlsx` oficial ni existen métodos HTTP de escritura en UI."""
        self.assertTrue(RUTA_MAESTRO_DEFINITIVO.is_file())
        self.assertEqual(
            RUTA_MAESTRO_DEFINITIVO.read_bytes(),
            BYTES_MAESTRO_INICIAL,
            "No debe modificarse 03_Aplicacion/inventario.xlsx.",
        )
        inv_oficial = motor.cargar_inventario_excel(RUTA_MAESTRO_DEFINITIVO)
        self.assertEqual(tuple(inv_oficial.obtener_hojas().keys()), motor.ORDEN_HOJAS)

        for nombre_archivo in ("app.py", "busqueda.py"):
            codigo = (RUTA_APLICACION / nombre_archivo).read_text(encoding="utf-8")
            for metodo in ('"PUT"', '"POST"', '"DELETE"', '"PATCH"', "'PUT'", "'POST'", "'DELETE'", "'PATCH'"):
                self.assertNotIn(metodo, codigo)

    def test_18_verificacion_de_estilos_css_responsive_y_accesibilidad(self) -> None:
        """Verifica que `estilos.css` exista, se inyecte en `app.py` y contenga reglas para tableta, móvil y foco."""
        self.assertTrue(RUTA_ESTILOS_CSS.is_file(), "Debe existir 03_Aplicacion/estilos.css")
        css_texto = app_ferms.cargar_estilos_locales()
        self.assertTrue(len(css_texto) > 100)

        # Puntos de corte responsive para tableta (992px) y teléfono (640px)
        self.assertIn("@media screen and (max-width: 992px)", css_texto)
        self.assertIn("@media screen and (max-width: 640px)", css_texto)
        # Prevención de desbordamiento horizontal y ajuste de palabras largas
        self.assertIn("overflow-x: hidden", css_texto)
        self.assertIn("overflow-wrap: anywhere", css_texto)
        # Indicadores de foco accesible (WCAG 2.2 AA)
        self.assertIn(":focus-visible", css_texto)
        # Clases del área visual Gemini y encabezado
        self.assertIn(".ferms-gemini-panel", css_texto)
        self.assertIn(".ferms-gemini-badge", css_texto)
        self.assertIn(".ferms-banner-encabezado", css_texto)


if __name__ == "__main__":
    unittest.main()

