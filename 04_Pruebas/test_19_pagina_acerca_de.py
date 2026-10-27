"""Pruebas focalizadas de la página pública «Acerca de FerreteríaMS» y navegación de 4 botones (P19).

Proyecto: FerreteríaMS — Versión Final
Tarea: FERMS-FINAL-P19
Requisitos relacionados: RF-001, RF-005, RF-010, RF-011, RF-F-012, RF-F-016, RF-F-019, RF-F-021, RF-F-022, RF-F-023.
Criterios relacionados: CA-008, CA-009, CA-F-010, CA-F-012, CA-F-013, CA-F-014, CA-F-015 y Sección 12 de P19.

Verifica exclusivamente los 9 escenarios de la Sección 9 de `02_Prompts/19_Pagina_Acerca_de_FerreteriaMS.md`:
1. Existencia del botón «Acerca de» en cuarta posición.
2. Secuencia exacta de navegación: Inicio → Asistente → Configuración → Acerca de.
3. Funcionamiento de los cuatro botones de navegación.
4. Acceso público sin autenticación a «Acerca de».
5. Presentación completa del contenido oficial aprobado (Sección 4 de P19).
6. Ausencia de sección sobre dispositivos móviles, bibliotecas Python, tecnologías, copyright o carácter académico (Sección 6 de P19).
7. Conservación del historial temporal, producto en contexto y contador de Gemini al navegar hacia y desde «Acerca de».
8. Preservación de la protección administrativa en la sección Configuración (`PRODUCTOS`).
9. Integridad e inmutabilidad de `03_Aplicacion/inventario.xlsx` y funcionamiento de la búsqueda pública.
"""

from __future__ import annotations

import hashlib
import sys
import unittest
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator
from unittest.mock import patch

import pandas as pd

RUTA_RAIZ = Path(__file__).resolve().parents[1]
RUTA_APLICACION = RUTA_RAIZ / "03_Aplicacion"
RUTA_APP_PY = RUTA_APLICACION / "app.py"
RUTA_INVENTARIO_OFICIAL = RUTA_APLICACION / "inventario.xlsx"

if str(RUTA_APLICACION) not in sys.path:
    sys.path.insert(0, str(RUTA_APLICACION))

import app as app_ferms  # noqa: E402
import asistente_gemini as gemini  # noqa: E402
import github_inventario as gh  # noqa: E402
import inventario as inv  # noqa: E402


class _RerunSolicitado(Exception):
    """Excepción interna para capturar `st.rerun()` durante el ciclo simulado de renderizado."""


@dataclass(frozen=True)
class BotonCapturado:
    """Representa un botón renderizado por Streamlit en un ciclo de `renderizar_aplicacion()`."""

    label: str
    key: str | None
    tipo: str
    disabled: bool


class ArnésStreamlitLigeroP19:
    """Arnés determinista en memoria para ejecutar `renderizar_aplicacion()` sin hilos `ScriptRunner`."""

    def __init__(self) -> None:
        self.session_state: dict[str, Any] = {}
        self.botones: list[BotonCapturado] = []
        self.subheaders: list[str] = []
        self.markdowns: list[str] = []
        self.captions: list[str] = []
        self.titles: list[str] = []
        self.warnings: list[str] = []
        self.errors: list[str] = []
        self.infos: list[str] = []
        self.successes: list[str] = []
        self.text_inputs: dict[str, str] = {}
        self.text_areas: dict[str, str] = {}
        self.chat_messages: list[tuple[str, str]] = []
        self._boton_clic_pendiente: str | None = None
        self._rol_chat_activo: str | None = None
        self._buffer_chat_activo: list[str] = []

    def _limpiar_captura_ciclo(self) -> None:
        self.botones.clear()
        self.subheaders.clear()
        self.markdowns.clear()
        self.captions.clear()
        self.titles.clear()
        self.warnings.clear()
        self.errors.clear()
        self.infos.clear()
        self.successes.clear()
        self.text_inputs.clear()
        self.text_areas.clear()
        self.chat_messages.clear()
        self._rol_chat_activo = None
        self._buffer_chat_activo.clear()

    @contextmanager
    def _bloque_contexto(self) -> Iterator[ArnésStreamlitLigeroP19]:
        yield self

    def __enter__(self) -> ArnésStreamlitLigeroP19:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        return False

    @contextmanager
    def _bloque_chat_message(self, rol: str) -> Iterator[ArnésStreamlitLigeroP19]:
        self._rol_chat_activo = rol
        self._buffer_chat_activo = []
        try:
            yield self
        finally:
            self.chat_messages.append((rol, "\n".join(self._buffer_chat_activo)))
            self._rol_chat_activo = None
            self._buffer_chat_activo = []

    def ejecutar_ciclo(
        self,
        *,
        clic_key: str | None = None,
        descargador_remoto: Any = None,
        cliente_generador_gemini: Any = None,
    ) -> None:
        """Ejecuta un ciclo de `app_ferms.renderizar_aplicacion()` y procesa `st.rerun()` si se solicita."""
        self._boton_clic_pendiente = clic_key
        max_reruns = 3
        for _ in range(max_reruns):
            self._limpiar_captura_ciclo()
            try:
                with self._parchar_streamlit():
                    app_ferms.renderizar_aplicacion(
                        descargador_remoto=descargador_remoto,
                        cliente_generador_gemini=cliente_generador_gemini,
                    )
                break
            except _RerunSolicitado:
                self._boton_clic_pendiente = None
                continue

    @contextmanager
    def _parchar_streamlit(self) -> Iterator[None]:
        st_mod = app_ferms.st

        def fake_columns(spec: Any, **_kwargs: Any) -> list[ArnésStreamlitLigeroP19]:
            n = spec if isinstance(spec, int) else len(spec)
            return [self for _ in range(n)]

        def fake_container(**_kwargs: Any) -> Any:
            return self._bloque_contexto()

        def fake_spinner(_texto: str = "") -> Any:
            return self._bloque_contexto()

        def fake_chat_message(name: str, **_kwargs: Any) -> Any:
            return self._bloque_chat_message(name)

        def fake_button(
            label: str,
            key: str | None = None,
            type: str = "secondary",
            disabled: bool = False,
            **_kwargs: Any,
        ) -> bool:
            self.botones.append(
                BotonCapturado(
                    label=str(label),
                    key=key,
                    tipo=str(type),
                    disabled=bool(disabled),
                )
            )
            if (
                not disabled
                and self._boton_clic_pendiente is not None
                and key == self._boton_clic_pendiente
            ):
                self._boton_clic_pendiente = None
                return True
            return False

        def fake_text_input(
            label: str,
            value: str = "",
            key: str | None = None,
            **_kwargs: Any,
        ) -> str:
            if key is not None:
                if key not in self.session_state:
                    self.session_state[key] = value
                val_actual = str(self.session_state.get(key, value))
                self.text_inputs[key] = val_actual
                return val_actual
            return str(value)

        def fake_text_area(
            label: str,
            value: str = "",
            key: str | None = None,
            **_kwargs: Any,
        ) -> str:
            if key is not None:
                if key not in self.session_state:
                    self.session_state[key] = value
                val_actual = str(self.session_state.get(key, value))
                self.text_areas[key] = val_actual
                return val_actual
            return str(value)

        def fake_checkbox(
            label: str,
            value: bool = False,
            key: str | None = None,
            **_kwargs: Any,
        ) -> bool:
            if key is not None:
                if key not in self.session_state:
                    self.session_state[key] = bool(value)
                return bool(self.session_state[key])
            return bool(value)

        def fake_markdown(body: Any, **_kwargs: Any) -> None:
            texto = str(body)
            self.markdowns.append(texto)
            if self._rol_chat_activo is not None:
                self._buffer_chat_activo.append(texto)

        def fake_subheader(body: Any, **_kwargs: Any) -> None:
            self.subheaders.append(str(body))

        def fake_caption(body: Any, **_kwargs: Any) -> None:
            self.captions.append(str(body))

        def fake_title(body: Any, **_kwargs: Any) -> None:
            self.titles.append(str(body))

        def fake_write(*args: Any, **_kwargs: Any) -> None:
            self.markdowns.append(" ".join(str(a) for a in args))

        def fake_warning(body: Any, **_kwargs: Any) -> None:
            self.warnings.append(str(body))

        def fake_error(body: Any, **_kwargs: Any) -> None:
            self.errors.append(str(body))

        def fake_info(body: Any, **_kwargs: Any) -> None:
            self.infos.append(str(body))

        def fake_success(body: Any, **_kwargs: Any) -> None:
            self.successes.append(str(body))

        def fake_rerun() -> None:
            raise _RerunSolicitado()

        with patch.multiple(
            st_mod,
            session_state=self.session_state,
            set_page_config=lambda **_k: None,
            columns=fake_columns,
            container=fake_container,
            spinner=fake_spinner,
            chat_message=fake_chat_message,
            button=fake_button,
            text_input=fake_text_input,
            text_area=fake_text_area,
            checkbox=fake_checkbox,
            markdown=fake_markdown,
            subheader=fake_subheader,
            caption=fake_caption,
            title=fake_title,
            write=fake_write,
            warning=fake_warning,
            error=fake_error,
            info=fake_info,
            success=fake_success,
            divider=lambda **_k: None,
            rerun=fake_rerun,
        ):
            yield


def _construir_inventario_prueba_p19() -> inv.InventarioDatos:
    """Construye un inventario en memoria válido con productos activos para pruebas focalizadas de P19."""
    df_categorias = pd.DataFrame(
        [
            {"Categoria_ID": "CAT-HER", "Nombre_Categoria": "Herramientas manuales"},
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
        ]
    )
    df_asignaciones = pd.DataFrame(
        [
            {"Codigo_Producto": "0007", "Ubicacion_ID": "UBI-01", "Principal": "Sí"},
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


class PruebasFocalizadasPaginaAcercaDeP19(unittest.TestCase):
    """Suite focalizada para validar `FERMS-FINAL-P19`."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.inventario = _construir_inventario_prueba_p19()
        cls.hash_inventario_inicial = (
            hashlib.sha256(RUTA_INVENTARIO_OFICIAL.read_bytes()).hexdigest()
            if RUTA_INVENTARIO_OFICIAL.is_file()
            else None
        )

    def test_01_02_03_cuatro_botones_secuencia_y_navegacion(self) -> None:
        """Escenarios 1, 2 y 3: Botón «Acerca de» en 4.ª posición, orden Inicio → Asistente → Configuración → Acerca de y navegación."""
        estado: dict[str, Any] = {}
        app_ferms.inicializar_estado_sesion(estado)
        self.assertEqual(
            app_ferms.obtener_seccion_activa(estado),
            app_ferms.SeccionInterfaz.INICIO,
        )

        # Verificar resolución por enum y texto para las cuatro secciones
        self.assertEqual(
            app_ferms.seleccionar_seccion_interfaz(app_ferms.SeccionInterfaz.ACERCA_DE, estado),
            app_ferms.SeccionInterfaz.ACERCA_DE,
        )
        self.assertEqual(
            app_ferms.obtener_seccion_activa(estado),
            app_ferms.SeccionInterfaz.ACERCA_DE,
        )
        self.assertEqual(
            app_ferms.seleccionar_seccion_interfaz("Acerca de", estado),
            app_ferms.SeccionInterfaz.ACERCA_DE,
        )

        # Verificar en renderizar_aplicacion() el orden exacto de los 4 botones de navegación superior
        ui = ArnésStreamlitLigeroP19()
        ui.ejecutar_ciclo()

        botones_nav = [
            b
            for b in ui.botones
            if b.key
            in {
                "btn_nav_inicio",
                "btn_nav_gemini",
                "btn_nav_productos",
                "btn_nav_acerca_de",
            }
        ]
        self.assertEqual(len(botones_nav), 4)
        self.assertEqual(
            [b.key for b in botones_nav],
            [
                "btn_nav_inicio",
                "btn_nav_gemini",
                "btn_nav_productos",
                "btn_nav_acerca_de",
            ],
        )
        self.assertEqual(botones_nav[3].key, "btn_nav_acerca_de")
        self.assertIn("Acerca de", botones_nav[3].label)

        # Conservar las modificaciones manuales del menú
        self.assertEqual(botones_nav[0].label, app_ferms.TEXTO_BOTON_NAV_INICIO)
        self.assertEqual(botones_nav[1].label, app_ferms.TEXTO_BOTON_NAV_GEMINI)
        self.assertEqual(botones_nav[2].label, app_ferms.TEXTO_BOTON_NAV_PRODUCTOS)
        self.assertEqual(botones_nav[3].label, app_ferms.TEXTO_BOTON_NAV_ACERCA_DE)

        # Probar clic en cada uno de los cuatro botones de navegación
        ui.ejecutar_ciclo(clic_key="btn_nav_gemini")
        self.assertEqual(
            ui.session_state[app_ferms.CLAVE_SECCION_ACTIVA],
            app_ferms.SeccionInterfaz.ASISTENTE_GEMINI.value,
        )

        ui.ejecutar_ciclo(clic_key="btn_nav_productos")
        self.assertEqual(
            ui.session_state[app_ferms.CLAVE_SECCION_ACTIVA],
            app_ferms.SeccionInterfaz.PRODUCTOS.value,
        )

        ui.ejecutar_ciclo(clic_key="btn_nav_acerca_de")
        self.assertEqual(
            ui.session_state[app_ferms.CLAVE_SECCION_ACTIVA],
            app_ferms.SeccionInterfaz.ACERCA_DE.value,
        )

        ui.ejecutar_ciclo(clic_key="btn_nav_inicio")
        self.assertEqual(
            ui.session_state[app_ferms.CLAVE_SECCION_ACTIVA],
            app_ferms.SeccionInterfaz.INICIO.value,
        )

    def test_04_05_06_acceso_publico_contenido_aprobado_y_exclusiones(self) -> None:
        """Escenarios 4, 5 y 6: Acceso público a «Acerca de», textos oficiales completos y exclusiones expresas."""
        ui = ArnésStreamlitLigeroP19()
        ui.ejecutar_ciclo()
        ui.ejecutar_ciclo(clic_key="btn_nav_acerca_de")

        # 4. Acceso público sin requerir login ni mostrar campos de usuario/contraseña
        self.assertNotIn("campo_admin_usuario", ui.text_inputs)
        self.assertNotIn("campo_admin_contrasena", ui.text_inputs)
        self.assertNotIn("campo_nombre_producto", ui.text_inputs)

        subheaders_texto = "\n".join(ui.subheaders)
        markdowns_visibles = [
            m for m in ui.markdowns if not m.lstrip().startswith("<style>")
        ]
        markdowns_texto = "\n".join(markdowns_visibles)
        texto_completo_pagina = f"{subheaders_texto}\n{markdowns_texto}"

        # 5. Presentación completa del contenido oficial aprobado (Sección 4.1 a 4.6)
        textos_oficiales_esperados = [
            "Acerca de FerreteríaMS",
            "Encuentra lo que necesitas. Aprende cómo utilizarlo.",
            "¿Qué es FerreteríaMS?",
            "FerreteríaMS es una aplicación diseñada para mejorar la experiencia de los clientes dentro de una ferretería",
            "Nuestro objetivo es facilitar la búsqueda de herramientas y materiales",
            "¿Qué puedes hacer con FerreteríaMS?",
            "Buscar productos fácilmente",
            "Conocer su ubicación exacta",
            "Recibir orientación con inteligencia artificial",
            "Puedes comunicarte en español o inglés.",
            "¿Cómo funciona?",
            "1. Escribe el nombre del producto que necesitas en el buscador.",
            "2. Selecciona el producto para consultar sus detalles y ubicación en la tienda.",
            "3. Si necesitas orientación adicional, accede al Asistente y describe lo que deseas realizar.",
            "4. Consulta las recomendaciones y verifica las instrucciones de seguridad antes de comenzar tu proyecto.",
            "Nuestro propósito",
            "FerreteríaMS combina localización de productos y orientación inteligente en una misma experiencia.",
            "Las recomendaciones generadas por inteligencia artificial pueden contener errores y no sustituyen las instrucciones del fabricante ni la asesoría de un profesional cualificado. La información del catálogo no confirma cantidades disponibles en inventario.",
        ]
        for fragmento in textos_oficiales_esperados:
            self.assertIn(fragmento, texto_completo_pagina)

        # 6. Exclusiones expresas (Sección 6: sin dispositivos móviles, sin bibliotecas/tecnologías/licencias/académico)
        terminos_excluidos = [
            "Acceder desde distintos dispositivos",
            "compatibilidad móvil",
            "computadora, tableta o teléfono",
            "Streamlit",
            "pandas",
            "openpyxl",
            "argon2",
            "Python",
            "GitHub API",
            "MIT License",
            "Apache",
            "Copyright",
            "derechos de autor",
            "proyecto académico",
            "trabajo universitario",
        ]
        texto_minusculas = texto_completo_pagina.lower()
        for prohibido in terminos_excluidos:
            self.assertNotIn(prohibido.lower(), texto_minusculas)

    def test_07_08_09_conservacion_estado_gemini_admin_e_inventario(self) -> None:
        """Escenarios 7, 8 y 9: Conservación de Gemini al entrar/salir de «Acerca de», protección de Configuración e inventario intacto."""
        lectura_remota = gh.ResultadoLecturaInventarioRemoto(
            propietario="JunyMSAI",
            repositorio="FerreteriaMS",
            rama="main",
            ruta_archivo="03_Aplicacion/inventario.xlsx",
            sha_github="sha_ui_p19",
            sha256_local="hash_ui_p19",
            tamano_bytes=2048,
            inventario=self.inventario,
        )

        def mock_descargador(**_kwargs: Any) -> gh.ResultadoLecturaInventarioRemoto:
            return lectura_remota

        def mock_cliente_gemini(
            solicitud: gemini.SolicitudModeloGemini,
        ) -> gemini.RespuestaModeloGemini:
            return gemini.RespuestaModeloGemini(
                texto="Respuesta técnica simulada conservada tras visitar Acerca de.",
                modelo_utilizado=solicitud.modelo,
            )

        with patch(
            "asistente_gemini.obtener_clave_api_gemini",
            return_value="clave_simulada_p19",
        ):
            ui = ArnésStreamlitLigeroP19()
            ui.ejecutar_ciclo(descargador_remoto=mock_descargador)

            # Buscar y seleccionar producto "0007" en Inicio
            ui.session_state["campo_nombre_producto"] = "martillo"
            ui.ejecutar_ciclo(
                clic_key="btn_ejecutar_busqueda",
                descargador_remoto=mock_descargador,
            )
            ui.ejecutar_ciclo(
                clic_key="btn_ver_detalle_0007",
                descargador_remoto=mock_descargador,
            )

            # Realizar una consulta en Asistente
            ui.ejecutar_ciclo(
                clic_key="btn_nav_gemini",
                descargador_remoto=mock_descargador,
                cliente_generador_gemini=mock_cliente_gemini,
            )
            ui.session_state["campo_pregunta_gemini"] = "¿Cómo usar este martillo?"
            ui.ejecutar_ciclo(
                clic_key="btn_enviar_pregunta_gemini",
                descargador_remoto=mock_descargador,
                cliente_generador_gemini=mock_cliente_gemini,
            )
            self.assertEqual(len(ui.chat_messages), 2)
            self.assertIn("1/10", "\n".join(ui.captions))

            # Entrar a «Acerca de» y luego volver a «Asistente»
            ui.ejecutar_ciclo(
                clic_key="btn_nav_acerca_de",
                descargador_remoto=mock_descargador,
                cliente_generador_gemini=mock_cliente_gemini,
            )
            self.assertIn(
                app_ferms.TITULO_SECCION_ACERCA_DE,
                "\n".join(ui.subheaders),
            )

            ui.ejecutar_ciclo(
                clic_key="btn_nav_gemini",
                descargador_remoto=mock_descargador,
                cliente_generador_gemini=mock_cliente_gemini,
            )

            # Verificar que historial, contador (1/10) y producto en contexto ("0007") se mantienen intactos
            self.assertEqual(len(ui.chat_messages), 2)
            self.assertIn("1/10", "\n".join(ui.captions))
            self.assertIn("0007", "\n".join(ui.markdowns))

            # Verificar que Configuración sigue exigiendo autenticación administrativa
            ui.ejecutar_ciclo(
                clic_key="btn_nav_productos",
                descargador_remoto=mock_descargador,
                cliente_generador_gemini=mock_cliente_gemini,
            )
            self.assertIn(
                app_ferms.TITULO_SECCION_ADMIN_LOGIN,
                "\n".join(ui.markdowns),
            )

        if self.hash_inventario_inicial is not None:
            hash_actual = hashlib.sha256(RUTA_INVENTARIO_OFICIAL.read_bytes()).hexdigest()
            self.assertEqual(
                hash_actual,
                self.hash_inventario_inicial,
                "El archivo maestro 03_Aplicacion/inventario.xlsx no debe sufrir alteraciones.",
            )


if __name__ == "__main__":
    unittest.main()
