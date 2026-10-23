"""Pruebas focalizadas para la integración del Asistente Gemini con el inventario (Bloque 2 — P16).

Proyecto: FerreteríaMS — Versión Final
Tarea: FERMS-FINAL-P16
Módulos probados: `03_Aplicacion/asistente_gemini.py` y `03_Aplicacion/app.py`
(integrados en modo lectura con `03_Aplicacion/busqueda.py` y `03_Aplicacion/inventario.py`).
Requisitos cubiertos: RF-F-012 a RF-F-025 (y compatibilidad con RF-F-008).
Criterios cubiertos: CA-F-010 a CA-F-019 (y compatibilidad con CA-F-007).

Todas las pruebas se ejecutan con simulaciones controladas de Gemini API (sin clave real ni
llamadas de red reales), sin modificar `03_Aplicacion/inventario.xlsx` y sin escrituras en GitHub.
"""

from __future__ import annotations

import hashlib
import os
import sys
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pandas as pd
from streamlit.testing.v1 import AppTest

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_APLICACION = RAIZ_PROYECTO / "03_Aplicacion"
RUTA_APP_PY = RUTA_APLICACION / "app.py"
RUTA_INVENTARIO_OFICIAL = RUTA_APLICACION / "inventario.xlsx"

if str(RUTA_APLICACION) not in sys.path:
    sys.path.insert(0, str(RUTA_APLICACION))

import app as app_ferms  # noqa: E402
import asistente_gemini as gemini  # noqa: E402
import busqueda  # noqa: E402
import github_inventario as gh  # noqa: E402
import inventario as motor  # noqa: E402


def _construir_inventario_pruebas_p16() -> motor.InventarioDatos:
    """Construye un inventario validado con productos activos e inactivos para las pruebas de P16."""
    df_categorias = pd.DataFrame(
        [
            {"Categoria_ID": "CAT-01", "Nombre_Categoria": "Herramientas Manuales"},
            {"Categoria_ID": "CAT-02", "Nombre_Categoria": "Tornillería y Fijación"},
            {"Categoria_ID": "CAT-03", "Nombre_Categoria": "Electricidad e Iluminación"},
            {"Categoria_ID": "CAT-04", "Nombre_Categoria": "Plomería y Tuberías"},
        ]
    )
    df_ubicaciones = pd.DataFrame(
        [
            {
                "Ubicacion_ID": "U-001",
                "Rack": "R01",
                "Columna": "C02",
                "Nivel": "N03",
                "Posicion": "P04",
                "Activo": "Sí",
            },
            {
                "Ubicacion_ID": "U-002",
                "Rack": "R02",
                "Columna": "C01",
                "Nivel": "N01",
                "Posicion": "P02",
                "Activo": "Sí",
            },
            {
                "Ubicacion_ID": "U-003",
                "Rack": "R03",
                "Columna": "C04",
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
                "Nombre": "Martillo de uña profesional 16 oz",
                "Categoria_ID": "CAT-01",
                "Descripcion": "Martillo de acero forjado con mango ergonómico para carpintería y obra.",
                "Activo": "Sí",
            },
            {
                "Codigo_Producto": "0012",
                "Nombre": "Cinta aislante eléctrica de PVC negra",
                "Categoria_ID": "CAT-03",
                "Descripcion": "Cinta aislante para empalmes eléctricos de baja tensión.",
                "Activo": "Sí",
            },
            {
                "Codigo_Producto": "TOR-05",
                "Nombre": "Tornillo autoperforante para madera 2 pulgadas",
                "Categoria_ID": "CAT-02",
                "Descripcion": "Tornillo galvanizado para fijación en madera y tableros.",
                "Activo": "Sí",
            },
            {
                "Codigo_Producto": "TUB-09",
                "Nombre": "Tubo de PVC hidráulico 1/2 pulgada",
                "Categoria_ID": "CAT-04",
                "Descripcion": "Tubo para conducción de agua fría en instalaciones de plomería.",
                "Activo": "Sí",
            },
            {
                "Codigo_Producto": "INA-99",
                "Nombre": "Martillo demoledor industrial descontinuado",
                "Categoria_ID": "CAT-01",
                "Descripcion": "Producto inactivo que no debe mostrarse ni enviarse a Gemini.",
                "Activo": "No",
            },
        ]
    )
    df_asignaciones = pd.DataFrame(
        [
            {"Codigo_Producto": "0007", "Ubicacion_ID": "U-001", "Principal": "Sí"},
            {"Codigo_Producto": "0007", "Ubicacion_ID": "U-002", "Principal": "No"},
            {"Codigo_Producto": "0012", "Ubicacion_ID": "U-003", "Principal": "Sí"},
            {"Codigo_Producto": "TOR-05", "Ubicacion_ID": "U-002", "Principal": "Sí"},
            {"Codigo_Producto": "TUB-09", "Ubicacion_ID": "U-001", "Principal": "Sí"},
            {"Codigo_Producto": "INA-99", "Ubicacion_ID": "U-003", "Principal": "Sí"},
        ]
    )
    return motor.construir_inventario_datos(
        {
            motor.HOJA_PRODUCTOS: df_productos,
            motor.HOJA_CATEGORIAS: df_categorias,
            motor.HOJA_UBICACIONES: df_ubicaciones,
            motor.HOJA_ASIGNACIONES: df_asignaciones,
        }
    )


def _crear_simulador_gemini_inteligente(
    registro_solicitudes: list[gemini.SolicitudModeloGemini] | None = None,
) -> gemini.ClienteGeneradorGemini:
    """Crea un generador simulado que inspecciona la solicitud y responde según idioma y catálogo."""

    def _simulador(
        solicitud: gemini.SolicitudModeloGemini,
    ) -> gemini.RespuestaModeloGemini:
        if registro_solicitudes is not None:
            registro_solicitudes.append(solicitud)

        codigos_recibidos = [
            p.codigo_producto for p in solicitud.productos_relevantes_catalogo
        ]
        if solicitud.idioma_respuesta == gemini.IdiomaAsistente.INGLES:
            if solicitud.producto_seleccionado is not None:
                sel = solicitud.producto_seleccionado
                texto = (
                    f"[Registered product in FerreteríaMS catalog]: **{sel.nombre}** "
                    f"(Code: `{sel.codigo_producto}`, Primary location: {sel.ubicacion_principal_etiqueta}). "
                    f"[General recommendation — not confirmed in FerreteríaMS catalog]: safety goggles and work gloves."
                )
            elif solicitud.productos_relevantes_catalogo:
                primero = solicitud.productos_relevantes_catalogo[0]
                texto = (
                    f"For your project, you can use [Registered product in FerreteríaMS catalog]: "
                    f"**{primero.nombre}** (Code: `{primero.codigo_producto}`, "
                    f"Location: {primero.ubicacion_principal_etiqueta}). "
                    f"[General recommendation — not confirmed in FerreteríaMS catalog]: wood glue or clamps."
                )
            else:
                texto = (
                    "[General recommendation — not confirmed in FerreteríaMS catalog]: "
                    "Use a spirit level and wall anchors appropriate for your wall type."
                )
            return gemini.RespuestaModeloGemini(texto=texto)

        # Respuesta en español
        if solicitud.producto_seleccionado is not None:
            sel = solicitud.producto_seleccionado
            texto = (
                f"[Producto registrado en catálogo FerreteríaMS]: **{sel.nombre}** "
                f"(Código: `{sel.codigo_producto}`, Ubicación principal: {sel.ubicacion_principal_etiqueta}). "
                f"[Recomendación general — no confirmado en el catálogo de FerreteríaMS]: gafas de protección."
            )
        elif solicitud.productos_relevantes_catalogo:
            primero = solicitud.productos_relevantes_catalogo[0]
            texto = (
                f"Te sugiero utilizar [Producto registrado en catálogo FerreteríaMS]: "
                f"**{primero.nombre}** (Código: `{primero.codigo_producto}`, "
                f"Ubicación principal: {primero.ubicacion_principal_etiqueta}; "
                f"códigos activos consultados: {', '.join(codigos_recibidos)}). "
                f"Además, como [Recomendación general — no confirmado en el catálogo de FerreteríaMS], "
                f"puedes emplear prensa sargento y gafas de seguridad."
            )
        else:
            texto = (
                "Para esta tarea no hay un artículo exacto confirmado en la búsqueda, pero como "
                "[Recomendación general — no confirmado en el catálogo de FerreteríaMS] te sugiero "
                "utilizar sellador de poliuretano y espátula metálica."
            )
        return gemini.RespuestaModeloGemini(texto=texto)

    return _simulador


class TestIntegracionGeminiP16(unittest.TestCase):
    """Suite focalizada de 12 pruebas para verificar RF-F-012..RF-F-025 y CA-F-010..CA-F-019."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.hash_inventario_inicial = (
            hashlib.sha256(RUTA_INVENTARIO_OFICIAL.read_bytes()).hexdigest()
            if RUTA_INVENTARIO_OFICIAL.exists()
            else None
        )

    def setUp(self) -> None:
        self.inventario = _construir_inventario_pruebas_p16()
        self.solicitudes_capturadas: list[gemini.SolicitudModeloGemini] = []
        self.simulador = _crear_simulador_gemini_inteligente(
            self.solicitudes_capturadas
        )

    def test_01_preguntas_ferreteria_espanol_ingles_y_cambio_idioma(self) -> None:
        """Escenario 1 (RF-F-012, RF-F-017, CA-F-010): Consultas en español e inglés y cambio de idioma por instrucción."""
        estado: dict[str, Any] = {}

        # 1. Consulta en español
        res_es = gemini.procesar_consulta_gemini_en_sesion(
            "¿Qué martillo me recomiendas para carpintería en madera?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
        )
        self.assertTrue(res_es.exito)
        self.assertEqual(res_es.idioma, gemini.IdiomaAsistente.ESPANOL)
        self.assertIn("0007", res_es.respuesta_asistente)
        self.assertIn("Martillo de uña profesional 16 oz", res_es.respuesta_asistente)

        # 2. Consulta directamente en inglés (detección automática)
        res_en = gemini.procesar_consulta_gemini_en_sesion(
            "What hammer or screw do you recommend for wood repair?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
        )
        self.assertTrue(res_en.exito)
        self.assertEqual(res_en.idioma, gemini.IdiomaAsistente.INGLES)
        self.assertIn("Registered product in FerreteríaMS catalog", res_en.respuesta_asistente)

        # 3. Solicitud explícita del cliente para cambiar el idioma a español
        res_cambio_es = gemini.procesar_consulta_gemini_en_sesion(
            "Por favor responde en español sobre este tornillo",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
        )
        self.assertTrue(res_cambio_es.exito)
        self.assertEqual(res_cambio_es.idioma, gemini.IdiomaAsistente.ESPANOL)

        # 4. Solicitud explícita del cliente para cambiar a inglés
        res_cambio_en = gemini.procesar_consulta_gemini_en_sesion(
            "Please answer in English from now on: how do I use electrical tape?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
        )
        self.assertTrue(res_cambio_en.exito)
        self.assertEqual(res_cambio_en.idioma, gemini.IdiomaAsistente.INGLES)

    def test_02_preguntas_de_seguimiento_en_sesion(self) -> None:
        """Escenario 2 (RF-F-012, RF-F-021, CA-F-010): Preguntas de seguimiento mantienen el contexto conversacional."""
        estado: dict[str, Any] = {}

        r1 = gemini.procesar_consulta_gemini_en_sesion(
            "Necesito instalar un tubo de PVC para agua fría.",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
        )
        self.assertTrue(r1.exito)
        self.assertEqual(len(gemini.obtener_historial_chat_gemini(estado)), 2)

        # Pregunta breve de seguimiento que depende de la conversación previa
        r2 = gemini.procesar_consulta_gemini_en_sesion(
            "¿Y cómo se usa o en qué ubicación está?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
        )
        self.assertTrue(r2.exito)
        self.assertEqual(len(gemini.obtener_historial_chat_gemini(estado)), 4)
        # El modelo recibió los turnos previos más la nueva pregunta (3 mensajes en contents)
        ultima_solicitud = self.solicitudes_capturadas[-1]
        self.assertEqual(len(ultima_solicitud.contenidos), 3)
        self.assertEqual(ultima_solicitud.contenidos[0]["role"], "user")
        self.assertEqual(ultima_solicitud.contenidos[1]["role"], "model")
        self.assertEqual(ultima_solicitud.contenidos[2]["role"], "user")

    def test_03_restriccion_consultas_ajenas_a_ferreteria(self) -> None:
        """Escenario 3 (RF-F-020, CA-F-015): Redirección amable ante consultas fuera del alcance de ferretería."""
        estado: dict[str, Any] = {}

        # Consulta sobre pronóstico del tiempo en español
        res_clima = gemini.procesar_consulta_gemini_en_sesion(
            "¿Cuál es el pronóstico del tiempo para hoy y quién ganó el partido de fútbol?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
        )
        self.assertTrue(res_clima.exito)
        self.assertEqual(
            res_clima.estado,
            gemini.EstadoRespuestaGemini.REDIRECCION_FUERA_DE_ALCANCE,
        )
        self.assertIn("FerreteríaMS", res_clima.respuesta_asistente)
        self.assertIn("ferretería", res_clima.respuesta_asistente.lower())
        # No se invocó innecesariamente al modelo para preguntas fuera de alcance
        self.assertEqual(len(self.solicitudes_capturadas), 0)

        # Consulta sobre recetas de cocina en inglés
        res_receta_en = gemini.procesar_consulta_gemini_en_sesion(
            "What is the best recipe for cooking a chocolate cake?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
        )
        self.assertTrue(res_receta_en.exito)
        self.assertEqual(
            res_receta_en.estado,
            gemini.EstadoRespuestaGemini.REDIRECCION_FUERA_DE_ALCANCE,
        )
        self.assertEqual(res_receta_en.idioma, gemini.IdiomaAsistente.INGLES)
        self.assertIn("hardware", res_receta_en.respuesta_asistente.lower())

    def test_04_contexto_producto_seleccionado_y_cambio_de_seleccion(self) -> None:
        """Escenario 4 (RF-F-016, CA-F-012): Recibe el producto seleccionado y actualiza el contexto al cambiarlo."""
        estado: dict[str, Any] = {}

        # 1. Seleccionar producto "0007" (Martillo de uña profesional 16 oz)
        r1 = gemini.procesar_consulta_gemini_en_sesion(
            "¿Para qué sirve este producto y dónde está ubicado?",
            estado=estado,
            inventario=self.inventario,
            codigo_producto_seleccionado="0007",
            cliente_generador=self.simulador,
        )
        self.assertTrue(r1.exito)
        self.assertIsNotNone(r1.producto_seleccionado)
        assert r1.producto_seleccionado is not None
        self.assertEqual(r1.producto_seleccionado.codigo_producto, "0007")
        self.assertIn("0007", r1.respuesta_asistente)
        self.assertIn("Rack R01 → Columna C02 → Nivel N03 → Posición P04", r1.respuesta_asistente)

        # 2. Cambiar el producto seleccionado a "0012" (Cinta aislante eléctrica) conservando la conversación
        r2 = gemini.procesar_consulta_gemini_en_sesion(
            "¿Y este otro producto en qué ubicación está?",
            estado=estado,
            inventario=self.inventario,
            codigo_producto_seleccionado="0012",
            cliente_generador=self.simulador,
        )
        self.assertTrue(r2.exito)
        self.assertTrue(r2.cambio_producto_detectado)
        self.assertEqual(r2.codigo_producto_anterior, "0007")
        assert r2.producto_seleccionado is not None
        self.assertEqual(r2.producto_seleccionado.codigo_producto, "0012")
        self.assertIn("0012", r2.respuesta_asistente)
        self.assertIn("Rack R03 → Columna C04 → Nivel N02 → Posición P01", r2.respuesta_asistente)
        # Verificar que la conversación anterior se conservó (4 mensajes en total)
        self.assertEqual(len(gemini.obtener_historial_chat_gemini(estado)), 4)
        # Verificar que la instrucción del sistema advirtió explícitamente del cambio de producto
        solicitud_cambio = self.solicitudes_capturadas[-1]
        self.assertIn("0007", solicitud_cambio.instruccion_sistema)
        self.assertIn("0012", solicitud_cambio.instruccion_sistema)
        self.assertIn("NUNCA mezcles", solicitud_cambio.instruccion_sistema)

    def test_05_recomendaciones_productos_registrados_y_no_registrados(self) -> None:
        """Escenario 5 (RF-F-013, RF-F-014, RF-F-015, CA-F-011): Distingue productos confirmados de recomendaciones generales."""
        estado: dict[str, Any] = {}

        # Consulta donde existe producto registrado ("Martillo" -> 0007) y recomendaciones complementarias
        res_con_catalogo = gemini.procesar_consulta_gemini_en_sesion(
            "Necesito un martillo y prensa para fijar madera.",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
        )
        self.assertTrue(res_con_catalogo.exito)
        self.assertIn("[Producto registrado en catálogo FerreteríaMS]", res_con_catalogo.respuesta_asistente)
        self.assertIn("0007", res_con_catalogo.respuesta_asistente)
        self.assertIn(
            "[Recomendación general — no confirmado en el catálogo de FerreteríaMS]",
            res_con_catalogo.respuesta_asistente,
        )

        # Consulta sobre un material no registrado en el catálogo (p. ej. impermeabilizante asfáltico)
        res_sin_catalogo = gemini.procesar_consulta_gemini_en_sesion(
            "¿Cómo aplico impermeabilizante en una azotea de concreto?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
        )
        self.assertTrue(res_sin_catalogo.exito)
        self.assertEqual(len(res_sin_catalogo.productos_relevantes_catalogo), 0)
        self.assertIn(
            "[Recomendación general — no confirmado en el catálogo de FerreteríaMS]",
            res_sin_catalogo.respuesta_asistente,
        )

    def test_06_exclusion_estricta_de_productos_inactivos(self) -> None:
        """Escenario 6 (RF-F-008, RF-F-014, CA-F-007): Los productos inactivos nunca se envían ni citan en Gemini."""
        # 1. Búsqueda de "martillo" nunca incluye el producto inactivo "INA-99" ("Martillo demoledor industrial descontinuado")
        relevantes = gemini.obtener_productos_relevantes_para_consulta(
            self.inventario,
            "martillo demoledor industrial",
        )
        codigos_relevantes = [p.codigo_producto for p in relevantes]
        self.assertIn("0007", codigos_relevantes)
        self.assertNotIn("INA-99", codigos_relevantes)

        # 2. Incluso si se pasa "INA-99" como producto seleccionado, Gemini lo ignora por estar inactivo
        estado: dict[str, Any] = {}
        res = gemini.procesar_consulta_gemini_en_sesion(
            "Háblame del martillo demoledor industrial",
            estado=estado,
            inventario=self.inventario,
            codigo_producto_seleccionado="INA-99",
            cliente_generador=self.simulador,
        )
        self.assertTrue(res.exito)
        self.assertIsNone(res.producto_seleccionado)
        self.assertNotIn("INA-99", res.respuesta_asistente)
        for prod_ctx in self.solicitudes_capturadas[-1].productos_relevantes_catalogo:
            self.assertNotEqual(prod_ctx.codigo_producto, "INA-99")

    def test_07_aviso_permanente_ia_y_precauciones_tecnicas_ante_riesgo(self) -> None:
        """Escenario 7 (RF-F-018, RF-F-019, CA-F-015, CA-F-016): Aviso fijo de IA y precauciones ante riesgos técnicos."""
        # Verificar texto exacto del aviso permanente aprobado en la Sección 7 del Prompt 16
        aviso_esperado = (
            "Este asistente utiliza inteligencia artificial y puede cometer errores. "
            "Verifica la información técnica y sigue las instrucciones del fabricante. "
            "Para trabajos que impliquen riesgos, consulta a un profesional cualificado."
        )
        self.assertEqual(gemini.AVISO_PERMANENTE_IA_GEMINI, aviso_esperado)

        # Simulador que devuelve una respuesta breve sin mencionar explícitamente al profesional
        def simulador_breve(_sol: gemini.SolicitudModeloGemini) -> str:
            return "Puedes usar cinta aislante de PVC código 0012 para cubrir el empalme."

        estado: dict[str, Any] = {}
        res_riesgo = gemini.procesar_consulta_gemini_en_sesion(
            "¿Cómo conecto un cable eléctrico de 220V en el tablero principal con un breaker?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=simulador_breve,
        )
        self.assertTrue(res_riesgo.exito)
        self.assertTrue(res_riesgo.requiere_precaucion_tecnica)
        self.assertEqual(res_riesgo.aviso_permanente, aviso_esperado)
        # Se garantiza que la respuesta final incluya precauciones, fabricante y profesional cualificado
        resp_low = res_riesgo.respuesta_asistente.lower()
        self.assertIn("precaución", resp_low)
        self.assertIn("fabricante", resp_low)
        self.assertIn("profesional cualificado", resp_low)

    def test_08_nueva_conversacion_limpia_historial_conservando_contador_uso(self) -> None:
        """Escenario 8 (RF-F-022, CA-F-013): «Nueva conversación» borra mensajes y contexto pero NO reinicia el uso."""
        estado: dict[str, Any] = {}
        reloj_fijo = lambda: 1000.0

        app_ferms.ejecutar_consulta_gemini_en_sesion(
            "¿Qué martillo tienen registrado?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
            reloj=reloj_fijo,
        )
        app_ferms.ejecutar_consulta_gemini_en_sesion(
            "¿Y qué tornillo para madera me sirve?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
            reloj=reloj_fijo,
        )
        self.assertEqual(len(gemini.obtener_historial_chat_gemini(estado)), 4)
        uso_antes = gemini.obtener_estado_uso_gemini_en_sesion(estado, reloj=reloj_fijo)
        self.assertEqual(uso_antes.consultas_realizadas, 2)

        # Ejecutar «Nueva conversación»
        uso_despues = app_ferms.ejecutar_nueva_conversacion_gemini_en_sesion(
            estado, reloj=reloj_fijo
        )
        self.assertEqual(len(gemini.obtener_historial_chat_gemini(estado)), 0)
        self.assertEqual(uso_despues.consultas_realizadas, 2)
        self.assertEqual(uso_despues.consultas_restantes, uso_antes.consultas_restantes)

    def test_09_limites_de_preguntas_longitud_entrada_e_historial_temporal(self) -> None:
        """Escenario 9 (RF-F-021, RF-F-023, CA-F-014): Límites por sesión, tamaño de pregunta, historial y renovación de ventana."""
        config_estricta = gemini.ConfiguracionLimitesGemini(
            max_consultas_por_ventana=2,
            duracion_ventana_segundos=600,
            longitud_maxima_pregunta=80,
            max_mensajes_historial_contexto=2,
            max_productos_contexto=2,
            max_tokens_salida=250,
        )
        tiempo_actual = {"t": 5000.0}
        reloj = lambda: tiempo_actual["t"]
        estado: dict[str, Any] = {}

        # 1. Rechazo por pregunta demasiado larga (> 80 caracteres) sin consumir cuota
        pregunta_larga = "Necesito saber cómo instalar " + ("muchos materiales de ferretería " * 5)
        res_larga = gemini.procesar_consulta_gemini_en_sesion(
            pregunta_larga,
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
            config_limites=config_estricta,
            reloj=reloj,
        )
        self.assertFalse(res_larga.exito)
        self.assertEqual(res_larga.codigo_error, gemini.CodigoErrorGemini.PREGUNTA_DEMASIADO_LARGA)
        self.assertEqual(
            gemini.obtener_estado_uso_gemini_en_sesion(
                estado, config_limites=config_estricta, reloj=reloj
            ).consultas_realizadas,
            0,
        )

        # 2. Consumir las 2 consultas permitidas en la ventana
        r1 = gemini.procesar_consulta_gemini_en_sesion(
            "¿Tienen martillo de uña?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
            config_limites=config_estricta,
            reloj=reloj,
        )
        r2 = gemini.procesar_consulta_gemini_en_sesion(
            "¿Y cinta aislante eléctrica?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
            config_limites=config_estricta,
            reloj=reloj,
        )
        self.assertTrue(r1.exito)
        self.assertTrue(r2.exito)

        # 3. La tercera consulta dentro de la misma ventana queda bloqueada
        r3_bloqueada = gemini.procesar_consulta_gemini_en_sesion(
            "¿Dónde está el tubo de PVC?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
            config_limites=config_estricta,
            reloj=reloj,
        )
        self.assertFalse(r3_bloqueada.exito)
        self.assertEqual(
            r3_bloqueada.estado, gemini.EstadoRespuestaGemini.LIMITE_USO_ALCANZADO
        )
        self.assertEqual(
            r3_bloqueada.codigo_error,
            gemini.CodigoErrorGemini.LIMITE_USO_SESION_ALCANZADO,
        )

        # Incluso si presiona «Nueva conversación», el bloqueo por límite se mantiene en la ventana actual
        gemini.iniciar_nueva_conversacion_gemini(
            estado, config_limites=config_estricta, reloj=reloj
        )
        r4_sigue_bloqueada = gemini.procesar_consulta_gemini_en_sesion(
            "¿Dónde está el tubo de PVC?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
            config_limites=config_estricta,
            reloj=reloj,
        )
        self.assertFalse(r4_sigue_bloqueada.exito)
        self.assertEqual(
            r4_sigue_bloqueada.codigo_error,
            gemini.CodigoErrorGemini.LIMITE_USO_SESION_ALCANZADO,
        )

        # 4. Mientras tanto, el buscador público sigue funcionando sin ninguna restricción (CA-F-014)
        res_busqueda = busqueda.ejecutar_busqueda_productos(self.inventario, "martillo")
        self.assertTrue(res_busqueda.tiene_resultados)
        self.assertEqual(res_busqueda.resultados_pagina[0].codigo_producto, "0007")

        # 5. Al avanzar el reloj a la siguiente ventana de uso (+601 s), se permiten nuevas consultas
        tiempo_actual["t"] += 601.0
        r5_nueva_ventana = gemini.procesar_consulta_gemini_en_sesion(
            "¿Dónde está el tubo de PVC?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
            config_limites=config_estricta,
            reloj=reloj,
        )
        self.assertTrue(r5_nueva_ventana.exito)

    def test_10_manejo_errores_api_reintento_manual_y_continuidad_busqueda(self) -> None:
        """Escenario 10 (RF-F-024, CA-F-017): Ausencia de clave, clave inválida, cuota agotada, timeout, red y reintento."""
        estado: dict[str, Any] = {}

        # 1. Clave API ausente (sin cliente simulado y sin secretos configurados)
        res_sin_clave = gemini.procesar_consulta_gemini_en_sesion(
            "¿Qué martillo me recomiendas?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=None,
            fuente_secretos={},
            fuente_entorno={},
        )
        self.assertFalse(res_sin_clave.exito)
        self.assertEqual(res_sin_clave.codigo_error, gemini.CodigoErrorGemini.CLAVE_API_AUSENTE)
        self.assertFalse(res_sin_clave.permite_reintentar)

        # 2. Clave API inválida (HTTP 401/403)
        def gen_clave_invalida(_sol: gemini.SolicitudModeloGemini) -> str:
            raise RuntimeError("401 API_KEY_INVALID: API key AIzaSyClaveFalsaDePrueba123456789 not valid")

        res_invalida = gemini.procesar_consulta_gemini_en_sesion(
            "¿Qué martillo me recomiendas?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=gen_clave_invalida,
        )
        self.assertFalse(res_invalida.exito)
        self.assertEqual(res_invalida.codigo_error, gemini.CodigoErrorGemini.CLAVE_API_INVALIDA)
        self.assertNotIn("AIzaSyClaveFalsaDePrueba123456789", res_invalida.mensaje_error_usuario)

        # 3. Cuota gratuita agotada (HTTP 429 RESOURCE_EXHAUSTED)
        def gen_cuota_agotada(_sol: gemini.SolicitudModeloGemini) -> str:
            raise RuntimeError("429 RESOURCE_EXHAUSTED: Quota exceeded for free tier")

        res_cuota = gemini.procesar_consulta_gemini_en_sesion(
            "¿Qué martillo me recomiendas?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=gen_cuota_agotada,
        )
        self.assertFalse(res_cuota.exito)
        self.assertEqual(res_cuota.codigo_error, gemini.CodigoErrorGemini.CUOTA_AGOTADA)
        self.assertTrue(res_cuota.permite_reintentar)

        # 4. Tiempo de espera agotado (Timeout) y posterior reintento manual exitoso
        def gen_timeout(_sol: gemini.SolicitudModeloGemini) -> str:
            raise TimeoutError("Request timed out after 20s")

        res_timeout = gemini.procesar_consulta_gemini_en_sesion(
            "¿Dónde está la cinta aislante?",
            estado=estado,
            inventario=self.inventario,
            cliente_generador=gen_timeout,
        )
        self.assertFalse(res_timeout.exito)
        self.assertEqual(res_timeout.codigo_error, gemini.CodigoErrorGemini.TIEMPO_ESPERA_AGOTADO)
        self.assertTrue(res_timeout.permite_reintentar)
        self.assertEqual(
            estado[gemini.CLAVE_ULTIMA_PREGUNTA_FALLIDA_GEMINI],
            "¿Dónde está la cinta aislante?",
        )

        # Reintentar manualmente cuando el servicio se recupera
        res_reintento = gemini.reintentar_ultima_consulta_gemini_en_sesion(
            estado=estado,
            inventario=self.inventario,
            cliente_generador=self.simulador,
        )
        self.assertIsNotNone(res_reintento)
        assert res_reintento is not None
        self.assertTrue(res_reintento.exito)
        self.assertIn("0012", res_reintento.respuesta_asistente)
        self.assertIsNone(estado[gemini.CLAVE_ULTIMA_PREGUNTA_FALLIDA_GEMINI])

        # 5. Confirmar que el buscador público opera normalmente tras cualquier error de Gemini
        lectura_remota = gh.ResultadoLecturaInventarioRemoto(
            propietario="JunyMSAI",
            repositorio="FerreteriaMS",
            rama="main",
            ruta_archivo="03_Aplicacion/inventario.xlsx",
            sha_github="sha_p16_ok",
            sha256_local="hash_p16",
            tamano_bytes=2048,
            inventario=self.inventario,
        )
        resp_busq = app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "martillo",
            estado=estado,
            descargador_remoto=lambda config=gh.CONFIGURACION_POR_DEFECTO: lectura_remota,
        )
        self.assertEqual(
            resp_busq.estado_operativo,
            app_ferms.EstadoOperativoInterfaz.RESULTADOS_ENCONTRADOS,
        )

    def test_11_proteccion_secretos_verificacion_capa_gratuita_e_inmutabilidad(self) -> None:
        """Escenario 11 (RF-F-025, CA-F-018, CA-F-019): Ocultamiento de secretos, capa gratuita $0 e inventario intacto."""
        # 1. Resolución de clave desde Streamlit Secrets y variables de entorno
        clave_secrets = gemini.obtener_clave_api_gemini(
            fuente_secretos={"GEMINI_API_KEY": "  clave_simulada_secrets_123  "},
            fuente_entorno={},
        )
        self.assertEqual(clave_secrets, "clave_simulada_secrets_123")

        clave_anidada = gemini.obtener_clave_api_gemini(
            fuente_secretos={"gemini": {"api_key": "clave_anidada_456"}},
            fuente_entorno={},
        )
        self.assertEqual(clave_anidada, "clave_anidada_456")

        # 2. Saneamiento de claves AIza..., GEMINI_API_KEY y tokens GitHub
        texto_sucio = (
            "Fallo con AIzaSyD9876543210abcdefGHIJKLMN y GEMINI_API_KEY=SecretoInterno999 "
            "y token ghp_TokenGitHubSecreto12345"
        )
        texto_limpio = gemini.ocultar_secretos_gemini(
            texto_sucio, api_key="SecretoInterno999"
        )
        self.assertNotIn("AIzaSyD9876543210abcdefGHIJKLMN", texto_limpio)
        self.assertNotIn("SecretoInterno999", texto_limpio)
        self.assertNotIn("ghp_TokenGitHubSecreto12345", texto_limpio)
        self.assertIn(gh.MARCA_SECRETO_OCULTO, texto_limpio)

        # 3. Verificación explícita de condiciones de capa gratuita ($0, sin facturación habilitada)
        verificacion = gemini.verificar_condiciones_capa_gratuita()
        self.assertTrue(verificacion.es_compatible_capa_gratuita)
        self.assertFalse(verificacion.facturacion_automatica_habilitada)
        self.assertTrue(verificacion.requiere_autorizacion_para_pago)
        self.assertIn("$0", verificacion.costo_monetario_previsto)

        # 4. Prueba unitaria del adaptador SDK con mock de `google.genai.Client` (sin red real)
        cliente_mock = MagicMock()
        respuesta_mock = MagicMock()
        respuesta_mock.text = "Respuesta simulada desde SDK oficial google-genai."
        cliente_mock.models.generate_content.return_value = respuesta_mock

        solicitud_prueba = gemini.SolicitudModeloGemini(
            modelo=gemini.MODELO_GEMINI_DEFECTO,
            pregunta_usuario="¿Cómo usar un martillo?",
            idioma_respuesta=gemini.IdiomaAsistente.ESPANOL,
            instruccion_sistema="Instrucción de prueba",
            contenidos=({"role": "user", "parts": [{"text": "¿Cómo usar un martillo?"}]},),
            producto_seleccionado=None,
            productos_relevantes_catalogo=(),
            cambio_producto_detectado=False,
            codigo_producto_anterior=None,
            evaluacion_riesgo=gemini.EvaluacionRiesgoTecnico(False),
        )
        with patch("google.genai.Client", return_value=cliente_mock) as mock_cls:
            res_sdk = gemini.invocar_modelo_gemini_sdk(
                solicitud_prueba,
                api_key="clave_ficticia_test_sdk",
                timeout_segundos=10.0,
            )
            self.assertEqual(
                res_sdk.texto,
                "Respuesta simulada desde SDK oficial google-genai.",
            )
            mock_cls.assert_called_once()
            cliente_mock.models.generate_content.assert_called_once()

        # 5. Inmutabilidad de `03_Aplicacion/inventario.xlsx` en disco
        if self.hash_inventario_inicial is not None:
            hash_actual = hashlib.sha256(RUTA_INVENTARIO_OFICIAL.read_bytes()).hexdigest()
            self.assertEqual(
                hash_actual,
                self.hash_inventario_inicial,
                "El archivo oficial 03_Aplicacion/inventario.xlsx no debe modificarse.",
            )

    def test_12_interfaz_streamlit_apptest_chat_gemini_y_busqueda(self) -> None:
        """Escenario 12: Integración completa en la UI de `app.py` con AppTest y simulaciones."""
        lectura_remota = gh.ResultadoLecturaInventarioRemoto(
            propietario="JunyMSAI",
            repositorio="FerreteriaMS",
            rama="main",
            ruta_archivo="03_Aplicacion/inventario.xlsx",
            sha_github="sha_ui_p16",
            sha256_local="hash_ui_p16",
            tamano_bytes=2048,
            inventario=self.inventario,
        )

        def mock_invocar_sdk(
            solicitud: gemini.SolicitudModeloGemini,
            *,
            api_key: str,
            timeout_segundos: float = 20.0,
        ) -> gemini.RespuestaModeloGemini:
            return self.simulador(solicitud)

        with (
            patch(
                "github_inventario.descargar_inventario_remoto",
                return_value=lectura_remota,
            ),
            patch(
                "asistente_gemini.obtener_clave_api_gemini",
                return_value="clave_simulada_ui",
            ),
            patch(
                "asistente_gemini.invocar_modelo_gemini_sdk",
                side_effect=mock_invocar_sdk,
            ),
        ):
            at = AppTest.from_file(str(RUTA_APP_PY))
            at.run(timeout=15)
            self.assertFalse(at.exception)

            # 1. Verificar que el aviso permanente de IA está visible en el área de Gemini
            markdowns_iniciales = "\n".join(m.value for m in at.markdown)
            self.assertIn(gemini.AVISO_PERMANENTE_IA_GEMINI, markdowns_iniciales)

            # 2. Buscar "martillo" y seleccionar el producto "0007"
            at.text_input(key="campo_nombre_producto").input("martillo")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)
            at.button(key="btn_ver_detalle_0007").click()
            at.run(timeout=15)

            md_con_seleccion = "\n".join(m.value for m in at.markdown)
            self.assertIn("Producto seleccionado en contexto", md_con_seleccion)
            self.assertIn("0007", md_con_seleccion)

            # 3. Enviar una pregunta en el chat Gemini sobre el producto seleccionado
            at.text_area(key="campo_pregunta_gemini").input(
                "¿Para qué trabajo me sirve este martillo y dónde está ubicado?"
            )
            at.button(key="btn_enviar_pregunta_gemini").click()
            at.run(timeout=15)
            self.assertFalse(at.exception)

            md_tras_pregunta = "\n".join(m.value for m in at.markdown)
            self.assertIn("Asistente Gemini:", md_tras_pregunta)
            self.assertIn("0007", md_tras_pregunta)
            self.assertIn("Rack R01 → Columna C02 → Nivel N03 → Posición P04", md_tras_pregunta)

            # 4. Presionar «Nueva conversación» y verificar que limpia mensajes pero mantiene contador 1/10
            at.button(key="btn_nueva_conversacion_gemini").click()
            at.run(timeout=15)
            self.assertFalse(at.exception)
            captions_tras_limpiar = "\n".join(c.value for c in at.caption)
            self.assertIn("1/10", captions_tras_limpiar)
            self.assertEqual(
                len(at.session_state[gemini.CLAVE_HISTORIAL_CHAT_GEMINI]), 0
            )


if __name__ == "__main__":
    unittest.main()

