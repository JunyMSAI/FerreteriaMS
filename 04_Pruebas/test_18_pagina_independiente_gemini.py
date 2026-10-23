"""Pruebas focalizadas de la página independiente y navegación del Asistente Gemini (P18).

Proyecto: FerreteríaMS — Versión Final (Bloque 2)
Tarea: FERMS-FINAL-P18
Decisión: DEC-FINAL-035 (Página independiente para Gemini conservando funcionalidades)
Requisitos relacionados: RF-001, RF-005, RF-011, RF-F-012, RF-F-016, RF-F-019, RF-F-021,
RF-F-022, RF-F-023, RF-F-024, RF-F-025.
Criterios relacionados: CA-F-010, CA-F-011, CA-F-012, CA-F-013, CA-F-014, CA-F-015,
CA-F-017, CA-F-018.

Verifica exclusivamente los 7 escenarios de la Sección 8 de `02_Prompts/18_Pagina_Independiente_Gemini.md`:
1. Navegación entre Inicio, Productos y Asistente Gemini.
2. Renderizado del chat en una página independiente de ancho completo y retiro de la columna lateral en Inicio.
3. Lectura de respuestas largas con títulos, listas y párrafos en contenedor con desplazamiento vertical interno.
4. Adaptación responsive a escritorio y móvil en `03_Aplicacion/estilos.css`.
5. Conservación del historial temporal y límites de uso al navegar entre páginas.
6. Transferencia y actualización del producto seleccionado al asistente al cambiar de página.
7. Ausencia de regresiones críticas en la búsqueda pública, administración e inmutabilidad de `inventario.xlsx`.
"""

from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

RUTA_RAIZ = Path(__file__).resolve().parents[1]
RUTA_APLICACION = RUTA_RAIZ / "03_Aplicacion"
RUTA_APP_PY = RUTA_APLICACION / "app.py"
RUTA_ESTILOS_CSS = RUTA_APLICACION / "estilos.css"
RUTA_INVENTARIO_OFICIAL = RUTA_APLICACION / "inventario.xlsx"

if str(RUTA_APLICACION) not in sys.path:
    sys.path.insert(0, str(RUTA_APLICACION))

import app as app_ferms  # noqa: E402
import asistente_gemini as gemini  # noqa: E402
import github_inventario as gh  # noqa: E402
import inventario as inv  # noqa: E402


def _construir_inventario_prueba_p18() -> inv.InventarioDatos:
    """Construye un inventario en memoria válido con productos activos para pruebas de P18."""
    df_categorias = pd.DataFrame(
        [
            {"Categoria_ID": "CAT-HER", "Nombre_Categoria": "Herramientas manuales"},
            {"Categoria_ID": "CAT-ELE", "Nombre_Categoria": "Electricidad"},
        ]
    )
    df_ubicaciones = pd.DataFrame(
        [
            {
                "Ubicacion_ID": "UBI-01",
                "Rack": "R01",
                "Columna": "C02",
                "Nivel": "N03",
                "Posicion": "P04",
                "Activo": "Sí",
            },
            {
                "Ubicacion_ID": "UBI-02",
                "Rack": "R02",
                "Columna": "C01",
                "Nivel": "N02",
                "Posicion": "P01",
                "Activo": "Sí",
            },
        ]
    )
    df_productos = pd.DataFrame(
        [
            {
                "Codigo_Producto": "0007",
                "Nombre": "Martillo de uña 16 oz",
                "Categoria_ID": "CAT-HER",
                "Descripcion": "Martillo con mango ergonómico para carpintería.",
                "Activo": "Sí",
            },
            {
                "Codigo_Producto": "0012",
                "Nombre": "Cinta aislante negra 3M",
                "Categoria_ID": "CAT-ELE",
                "Descripcion": "Cinta aislante de PVC para aislamiento eléctrico.",
                "Activo": "Sí",
            },
        ]
    )
    df_asignaciones = pd.DataFrame(
        [
            {"Codigo_Producto": "0007", "Ubicacion_ID": "UBI-01", "Principal": "Sí"},
            {"Codigo_Producto": "0012", "Ubicacion_ID": "UBI-02", "Principal": "Sí"},
        ]
    )
    return inv.construir_inventario_datos(
        {
            inv.HOJA_PRODUCTOS: df_productos,
            inv.HOJA_CATEGORIAS: df_categorias,
            inv.HOJA_UBICACIONES: df_ubicaciones,
            inv.HOJA_ASIGNACIONES: df_asignaciones,
        }
    )


class PruebasFocalizadasPaginaIndependienteGeminiP18(unittest.TestCase):
    """Suite focalizada para validar `FERMS-FINAL-P18` (DEC-FINAL-035)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.inventario = _construir_inventario_prueba_p18()
        cls.hash_inventario_inicial = (
            hashlib.sha256(RUTA_INVENTARIO_OFICIAL.read_bytes()).hexdigest()
            if RUTA_INVENTARIO_OFICIAL.is_file()
            else None
        )

    def test_01_navegacion_tres_secciones_principales(self) -> None:
        """Escenario 1: Navegación entre Inicio, Productos y Asistente Gemini reutilizando estado de sesión."""
        estado: dict[str, Any] = {}
        app_ferms.inicializar_estado_sesion(estado)
        self.assertEqual(
            app_ferms.obtener_seccion_activa(estado),
            app_ferms.SeccionInterfaz.INICIO,
        )

        # Cambiar a Productos
        sec_prod = app_ferms.seleccionar_seccion_interfaz(
            app_ferms.SeccionInterfaz.PRODUCTOS, estado
        )
        self.assertEqual(sec_prod, app_ferms.SeccionInterfaz.PRODUCTOS)
        self.assertEqual(
            app_ferms.obtener_seccion_activa(estado),
            app_ferms.SeccionInterfaz.PRODUCTOS,
        )

        # Cambiar a Asistente Gemini (tanto por enum como por texto)
        sec_gem = app_ferms.seleccionar_seccion_interfaz(
            app_ferms.SeccionInterfaz.ASISTENTE_GEMINI, estado
        )
        self.assertEqual(sec_gem, app_ferms.SeccionInterfaz.ASISTENTE_GEMINI)
        self.assertEqual(
            app_ferms.obtener_seccion_activa(estado),
            app_ferms.SeccionInterfaz.ASISTENTE_GEMINI,
        )

        sec_alias = app_ferms.seleccionar_seccion_interfaz("GEMINI", estado)
        self.assertEqual(sec_alias, app_ferms.SeccionInterfaz.ASISTENTE_GEMINI)

        # Volver a Inicio
        sec_ini = app_ferms.seleccionar_seccion_interfaz(
            app_ferms.SeccionInterfaz.INICIO, estado
        )
        self.assertEqual(sec_ini, app_ferms.SeccionInterfaz.INICIO)

    def test_02_chat_pagina_independiente_sin_columna_lateral_en_inicio(self) -> None:
        """Escenario 2: Inicio no muestra columna lateral de Gemini y Asistente Gemini abre en su propia página."""
        at = AppTest.from_file(str(RUTA_APP_PY))
        at.run(timeout=15)
        self.assertFalse(at.exception)

        # En Inicio deben existir los tres botones de navegación superior
        claves_botones_inicio = {b.key for b in at.button}
        self.assertIn("btn_nav_inicio", claves_botones_inicio)
        self.assertIn("btn_nav_productos", claves_botones_inicio)
        self.assertIn("btn_nav_gemini", claves_botones_inicio)

        # En Inicio está el buscador público pero NO el campo de chat de Gemini (columna lateral retirada)
        claves_text_input_inicio = {ti.key for ti in at.text_input}
        claves_text_area_inicio = {ta.key for ta in at.text_area}
        self.assertIn("campo_nombre_producto", claves_text_input_inicio)
        self.assertNotIn("campo_pregunta_gemini", claves_text_area_inicio)

        # Navegar a la página independiente «Asistente Gemini»
        at.button(key="btn_nav_gemini").click()
        at.run(timeout=15)
        self.assertFalse(at.exception)

        # En la página Asistente Gemini se renderiza el chat de ancho completo y no el buscador de Inicio
        claves_text_area_gemini = {ta.key for ta in at.text_area}
        claves_botones_gemini = {b.key for b in at.button}
        self.assertIn("campo_pregunta_gemini", claves_text_area_gemini)
        self.assertIn("btn_enviar_pregunta_gemini", claves_botones_gemini)
        self.assertIn("btn_nueva_conversacion_gemini", claves_botones_gemini)

        markdowns_gemini = "\n".join(m.value for m in at.markdown)
        self.assertIn(gemini.AVISO_PERMANENTE_IA_GEMINI, markdowns_gemini)

    def test_03_respuestas_largas_markdown_y_contenedor_desplazamiento_interno(self) -> None:
        """Escenario 3: Títulos, listas y párrafos Markdown renderizados en contenedor con altura fija y scroll."""
        self.assertGreaterEqual(app_ferms.ALTURA_CONTENEDOR_CHAT_GEMINI_PX, 350)
        self.assertLessEqual(app_ferms.ALTURA_CONTENEDOR_CHAT_GEMINI_PX, 650)

        respuesta_markdown_larga = (
            "### Guía de instalación de repisa\n\n"
            "Para fijar una repisa resistente en muro de concreto te recomiendo:\n\n"
            "- **Martillo de uña 16 oz** (`0007`) — `[Producto registrado en catálogo FerreteríaMS]`\n"
            "- **Nivel de burbuja** — `[Recomendación general — no confirmado en el catálogo de FerreteríaMS]`\n\n"
            "1. Verifica que no pasen tuberías ni cables eléctricos.\n"
            "2. Utiliza gafas de protección ocular durante toda la perforación.\n\n"
            + ("Párrafo adicional de orientación técnica detallada. " * 20)
        )
        texto_preparado = app_ferms.preparar_markdown_mensaje_gemini(
            respuesta_markdown_larga
        )
        # No debe convertir saltos de línea en `<br/>` ni escapar caracteres Markdown válidos
        self.assertNotIn("<br/>", texto_preparado)
        self.assertIn("### Guía de instalación de repisa", texto_preparado)
        self.assertIn("- **Martillo de uña 16 oz**", texto_preparado)
        self.assertIn("1. Verifica que no pasen tuberías", texto_preparado)

    def test_04_adaptacion_escritorio_y_movil_estilos_css(self) -> None:
        """Escenario 4: Reglas CSS para mensajes Markdown del chat y adaptación responsive en escritorio y móvil."""
        css = app_ferms.cargar_estilos_locales(RUTA_ESTILOS_CSS)
        self.assertIn('[data-testid="stChatMessage"]', css)
        self.assertIn("@media screen and (max-width: 820px)", css)
        self.assertIn("@media screen and (max-width: 640px)", css)
        self.assertIn(".ferms-gemini-aviso-permanente", css)
        self.assertIn(".ferms-gemini-contexto-producto", css)

    def test_05_6_conservacion_historial_limites_y_producto_seleccionado_al_navegar(self) -> None:
        """Escenarios 5 y 6: Conservación de historial, contador de uso y producto seleccionado entre páginas."""
        lectura_remota = gh.ResultadoLecturaInventarioRemoto(
            propietario="JunyMSAI",
            repositorio="FerreteriaMS",
            rama="main",
            ruta_archivo="03_Aplicacion/inventario.xlsx",
            sha_github="sha_ui_p18",
            sha256_local="hash_ui_p18",
            tamano_bytes=2048,
            inventario=self.inventario,
        )

        def mock_invocar_sdk(
            solicitud: gemini.SolicitudModeloGemini,
            *,
            api_key: str,
            timeout_segundos: float = 20.0,
        ) -> gemini.RespuestaModeloGemini:
            cod_ctx = (
                solicitud.producto_seleccionado.codigo_producto
                if solicitud.producto_seleccionado is not None
                else "SIN_PRODUCTO"
            )
            ubic_ctx = (
                solicitud.producto_seleccionado.ubicacion_principal_etiqueta
                if solicitud.producto_seleccionado is not None
                else ""
            )
            return gemini.RespuestaModeloGemini(
                texto=(
                    f"### Asesoría para producto `{cod_ctx}`\n\n"
                    f"- Ubicación confirmada: **{ubic_ctx}** `[Producto registrado en catálogo FerreteríaMS]`\n"
                    f"- Usa guantes de seguridad `[Recomendación general — no confirmado en el catálogo de FerreteríaMS]`."
                ),
                modelo_utilizado=solicitud.modelo,
            )

        with (
            patch(
                "github_inventario.descargar_inventario_remoto",
                return_value=lectura_remota,
            ),
            patch(
                "asistente_gemini.obtener_clave_api_gemini",
                return_value="clave_simulada_p18",
            ),
            patch(
                "asistente_gemini.invocar_modelo_gemini_sdk",
                side_effect=mock_invocar_sdk,
            ),
        ):
            at = AppTest.from_file(str(RUTA_APP_PY))
            at.run(timeout=15)

            # 1. En Inicio: buscar "martillo" y seleccionar producto "0007"
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)
            at.button(key="btn_ver_detalle_0007").click()
            at.run(timeout=15)
            self.assertFalse(at.exception)

            # 2. Abrir Asistente Gemini desde el botón directo de la vista de detalle
            at.button(key="btn_ir_gemini_desde_detalle").click()
            at.run(timeout=15)
            self.assertFalse(at.exception)

            md_gemini_1 = "\n".join(m.value for m in at.markdown)
            self.assertIn("Producto seleccionado en contexto", md_gemini_1)
            self.assertIn("0007", md_gemini_1)
            self.assertIn("Rack R01 → Columna C02 → Nivel N03 → Posición P04", md_gemini_1)

            # 3. Enviar una consulta en la página independiente de Gemini
            at.text_area(key="campo_pregunta_gemini").input(
                "¿Para qué sirve este martillo y dónde se ubica?"
            )
            at.button(key="btn_enviar_pregunta_gemini").click()
            at.run(timeout=15)
            self.assertFalse(at.exception)

            # Verificar que se renderizó con st.chat_message y conserva formato Markdown sin escapar
            self.assertEqual(len(at.chat_message), 2)
            md_tras_consulta = "\n".join(m.value for m in at.markdown)
            self.assertIn("### Asesoría para producto `0007`", md_tras_consulta)
            self.assertIn("1/10", "\n".join(c.value for c in at.caption))

            # 4. Navegar a Productos y luego a Inicio y comprobar que el historial, el contador (1/10)
            #    y el producto seleccionado ("0007") se conservan intactos
            at.button(key="btn_nav_productos").click()
            at.run(timeout=15)
            self.assertFalse(at.exception)

            at.button(key="btn_nav_inicio").click()
            at.run(timeout=15)
            self.assertFalse(at.exception)
            self.assertEqual(
                at.session_state[app_ferms.CLAVE_PRODUCTO_SELECCIONADO], "0007"
            )

            # 5. Cambiar a otro producto ("0012") en Inicio y volver a Asistente Gemini
            at.button(key="btn_volver_resultados").click()
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("cinta")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)
            at.button(key="btn_ver_detalle_0012").click()
            at.run(timeout=15)

            at.button(key="btn_nav_gemini").click()
            at.run(timeout=15)
            self.assertFalse(at.exception)

            # El contexto ahora refleja "0012", el historial previo de 2 mensajes sigue presente y el uso es 1/10
            md_gemini_2 = "\n".join(m.value for m in at.markdown)
            self.assertIn("0012", md_gemini_2)
            self.assertIn("Cinta aislante negra 3M", md_gemini_2)
            self.assertEqual(len(at.chat_message), 2)
            self.assertIn("1/10", "\n".join(c.value for c in at.caption))

            # 6. «Nueva conversación» limpia el historial pero mantiene el contador 1/10
            at.button(key="btn_nueva_conversacion_gemini").click()
            at.run(timeout=15)
            self.assertEqual(len(at.chat_message), 0)
            self.assertIn("1/10", "\n".join(c.value for c in at.caption))

    def test_07_ausencia_regresiones_busqueda_admin_e_inmutabilidad_inventario(self) -> None:
        """Escenario 7: Búsqueda pública, acceso administrativo protegido e `inventario.xlsx` sin modificaciones."""
        at = AppTest.from_file(str(RUTA_APP_PY))
        at.run(timeout=15)
        at.button(key="btn_nav_productos").click()
        at.run(timeout=15)
        self.assertFalse(at.exception)

        # Verifica que Productos continúa exigiendo autenticación administrativa
        md_admin = "\n".join(m.value for m in at.markdown)
        self.assertIn(app_ferms.TITULO_SECCION_ADMIN_LOGIN, md_admin)

        if self.hash_inventario_inicial is not None:
            hash_actual = hashlib.sha256(RUTA_INVENTARIO_OFICIAL.read_bytes()).hexdigest()
            self.assertEqual(
                hash_actual,
                self.hash_inventario_inicial,
                "El archivo oficial 03_Aplicacion/inventario.xlsx no debe modificarse.",
            )


if __name__ == "__main__":
    unittest.main()
