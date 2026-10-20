"""Pruebas automatizadas funcionales y de integración para la búsqueda pública de productos.

Proyecto: FerreteríaMS v0
Tarea: FERMS-V0-P04
Módulos probados: `03_Aplicacion/busqueda.py` y `03_Aplicacion/app.py`
(integrados con `03_Aplicacion/inventario.py` y `03_Aplicacion/github_inventario.py`).
Requisitos cubiertos: RF-001, RF-002, RF-003, RF-004, RF-008, RF-009, RF-024, RF-025,
RF-028, RF-034, RF-035, RF-036, RF-037, RF-038.
Criterios cubiertos: CA-001, CA-002, CA-003, CA-004, CA-006, CA-007, CA-032, CA-033,
CA-034, CA-039, CA-040, CA-041, CA-042, CA-043.

Todas las pruebas se ejecutan sobre datos controlados en memoria y simulaciones (mocks),
sin realizar escrituras locales ni remotas en GitHub.
"""

from __future__ import annotations

import ast
import base64
import json
import sys
import unittest
from pathlib import Path
from typing import Any, Mapping
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


def _construir_inventario_controlado(
    lista_productos: list[dict[str, str]],
) -> motor.InventarioDatos:
    """Construye un objeto `InventarioDatos` válido a partir de una lista controlada de productos."""
    df_categorias = pd.DataFrame(
        [
            {"Categoria_ID": "CAT01", "Nombre_Categoria": "Herramientas Manuales"},
            {"Categoria_ID": "CAT02", "Nombre_Categoria": "Tornillería y Fijación"},
            {"Categoria_ID": "CAT03", "Nombre_Categoria": "Electricidad e Iluminación"},
            {"Categoria_ID": "CAT04", "Nombre_Categoria": "Pinturas y Acabados"},
        ]
    )
    df_ubicaciones = pd.DataFrame(
        [
            {"Ubicacion_ID": "U001", "Rack": "R01", "Columna": "C01", "Nivel": "N01", "Posicion": "P01"},
            {"Ubicacion_ID": "U002", "Rack": "R02", "Columna": "C02", "Nivel": "N01", "Posicion": "P02"},
        ]
    )

    filas_productos: list[dict[str, str]] = []
    filas_asignaciones: list[dict[str, str]] = []

    for idx, prod in enumerate(lista_productos, start=1):
        cod = prod.get("Codigo_Producto", f"P{idx:04d}")
        filas_productos.append(
            {
                "Codigo_Producto": cod,
                "Nombre": prod["Nombre"],
                "Categoria_ID": prod.get("Categoria_ID", "CAT01"),
                "Descripcion": prod.get("Descripcion", ""),
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


def _crear_payload_github_desde_inventario(
    inv: motor.InventarioDatos,
    sha: str = "1111222233334444555566667777888899990000",
) -> dict[str, Any]:
    """Serializa un inventario validado a bytes `.xlsx` y arma el payload JSON de GitHub Contents API."""
    bytes_xlsx = motor.serializar_inventario_a_bytes(inv)
    b64 = base64.b64encode(bytes_xlsx).decode("ascii")
    return {
        "name": "inventario.xlsx",
        "path": "03_Aplicacion/inventario.xlsx",
        "sha": sha,
        "size": len(bytes_xlsx),
        "type": "file",
        "encoding": "base64",
        "content": b64,
    }


class TestMotorBusquedaFuncional(unittest.TestCase):
    """Sección 10.2 — Pruebas funcionales de los 14 escenarios del motor de búsqueda."""

    def setUp(self) -> None:
        self.inventario_base = _construir_inventario_controlado(
            [
                {
                    "Codigo_Producto": "MAR001",
                    "Nombre": "Martillo de uña",
                    "Categoria_ID": "CAT01",
                    "Descripcion": "Marca Truper profesional para carpintería",
                },
                {
                    "Codigo_Producto": "MAR002",
                    "Nombre": "Martillo de bola 16 oz",
                    "Categoria_ID": "CAT01",
                    "Descripcion": "Marca Pretul acero forjado",
                },
                {
                    "Codigo_Producto": "PER001",
                    "Nombre": "Taladro percutor y martillo eléctrico",
                    "Categoria_ID": "CAT03",
                    "Descripcion": "Herramienta rotomartillo",
                },
                {
                    "Codigo_Producto": "SOP001",
                    "Nombre": "Porta martillo de cuero",
                    "Categoria_ID": "CAT01",
                    "Descripcion": "Accesorio para cinturón",
                },
                {
                    "Codigo_Producto": "DES001",
                    "Nombre": "Destornillador estrella aislado",
                    "Categoria_ID": "CAT03",
                    "Descripcion": "Para trabajos de electricidad",
                },
                {
                    "Codigo_Producto": "000125",
                    "Nombre": "Cinta aislante eléctrica",
                    "Categoria_ID": "CAT03",
                    "Descripcion": "Cinta de PVC negra",
                },
            ]
        )

    def test_01_busqueda_por_nombre_completo(self) -> None:
        """Caso 1 (RF-001 / CA-001): Encontrar un producto registrado buscando su nombre completo."""
        res = busqueda.ejecutar_busqueda_productos(self.inventario_base, "Martillo de uña")
        self.assertEqual(res.estado, busqueda.EstadoBusqueda.CON_RESULTADOS)
        self.assertEqual(res.total_resultados, 1)
        self.assertEqual(res.resultados_pagina[0].codigo_producto, "MAR001")
        self.assertEqual(res.resultados_pagina[0].nombre, "Martillo de uña")
        self.assertEqual(res.resultados_pagina[0].nombre_categoria, "Herramientas Manuales")

    def test_02_busqueda_por_parte_del_nombre(self) -> None:
        """Caso 2 (RF-002 / CA-002): Encontrar productos mediante coincidencias parciales."""
        res = busqueda.ejecutar_busqueda_productos(self.inventario_base, "destornillador")
        self.assertEqual(res.estado, busqueda.EstadoBusqueda.CON_RESULTADOS)
        self.assertEqual(res.total_resultados, 1)
        self.assertEqual(res.resultados_pagina[0].codigo_producto, "DES001")

        # Subcadena en medio de una palabra o frase
        res_parcial = busqueda.ejecutar_busqueda_productos(self.inventario_base, "aisla")
        codigos = [p.codigo_producto for p in res_parcial.resultados_pagina]
        self.assertEqual(set(codigos), {"000125", "DES001"})

    def test_03_busqueda_sin_diferencias_entre_mayusculas_y_minusculas(self) -> None:
        """Caso 3 (RF-003 / CA-003): Ignorar diferencias entre mayúsculas y minúsculas."""
        res_min = busqueda.ejecutar_busqueda_productos(self.inventario_base, "martillo")
        res_may = busqueda.ejecutar_busqueda_productos(self.inventario_base, "MARTILLO")
        res_mix = busqueda.ejecutar_busqueda_productos(self.inventario_base, "MaRtIlLo")

        codigos_min = [p.codigo_producto for p in res_min.todos_los_resultados]
        codigos_may = [p.codigo_producto for p in res_may.todos_los_resultados]
        codigos_mix = [p.codigo_producto for p in res_mix.todos_los_resultados]

        self.assertEqual(len(codigos_min), 4)
        self.assertEqual(codigos_min, codigos_may)
        self.assertEqual(codigos_min, codigos_mix)

    def test_04_busqueda_sin_diferencias_de_acentuacion_conservando_originales(self) -> None:
        """Caso 4 (RF-003 / CA-004): Ignorar acentos sin alterar los nombres originales del inventario."""
        # Ejemplo explícito del Prompt 04: ELECTRICO -> Eléctrico / eléctrica
        res_sin_tilde = busqueda.ejecutar_busqueda_productos(self.inventario_base, "ELECTRICO")
        res_con_tilde = busqueda.ejecutar_busqueda_productos(self.inventario_base, "eléctrico")
        self.assertEqual(res_sin_tilde.total_resultados, 1)
        self.assertEqual(
            [p.codigo_producto for p in res_sin_tilde.resultados_pagina],
            [p.codigo_producto for p in res_con_tilde.resultados_pagina],
        )
        # Verificar que el nombre original conserva sus tildes y mayúsculas intactas
        self.assertEqual(
            res_sin_tilde.resultados_pagina[0].nombre,
            "Taladro percutor y martillo eléctrico",
        )

        # Búsqueda de "Martillo de una" -> "Martillo de uña"
        res_una = busqueda.ejecutar_busqueda_productos(self.inventario_base, "martillo de una")
        self.assertEqual(res_una.total_resultados, 1)
        self.assertEqual(res_una.resultados_pagina[0].nombre, "Martillo de uña")

    def test_05_prioridad_coincidencias_al_inicio_del_nombre(self) -> None:
        """Caso 5 (RF-035 / CA-039): Priorizar productos cuyos nombres comienzan con el término buscado."""
        res = busqueda.ejecutar_busqueda_productos(self.inventario_base, "martillo")
        codigos = [p.codigo_producto for p in res.resultados_pagina]
        # MAR002 ("Martillo de bola 16 oz") y MAR001 ("Martillo de uña") comienzan con "martillo"
        # SOP001 ("Porta martillo de cuero") y PER001 ("Taladro percutor y martillo eléctrico") no comienzan con "martillo"
        self.assertEqual(codigos[:2], ["MAR002", "MAR001"])
        self.assertTrue(res.resultados_pagina[0].coincide_al_inicio)
        self.assertTrue(res.resultados_pagina[1].coincide_al_inicio)

    def test_06_coincidencias_en_otras_posiciones_aparecen_despues(self) -> None:
        """Caso 6 (RF-035 / CA-039): Productos con el término en posición interior aparecen después."""
        res = busqueda.ejecutar_busqueda_productos(self.inventario_base, "martillo")
        codigos = [p.codigo_producto for p in res.resultados_pagina]
        self.assertEqual(codigos[2:], ["SOP001", "PER001"])
        self.assertFalse(res.resultados_pagina[2].coincide_al_inicio)
        self.assertFalse(res.resultados_pagina[3].coincide_al_inicio)
        self.assertEqual(
            res.resultados_pagina[2].prioridad,
            busqueda.PrioridadRelevancia.COINCIDENCIA_INTERIOR,
        )

    def test_07_orden_reproducible_y_estable(self) -> None:
        """Caso 7 (RF-035): El orden dentro de cada grupo es estable y reproducible sin importar el orden de entrada."""
        productos_orden_a = [
            {"Codigo_Producto": "P003", "Nombre": "Broca para madera"},
            {"Codigo_Producto": "P001", "Nombre": "Juego de brocas"},
            {"Codigo_Producto": "P002", "Nombre": "Broca para concreto"},
            {"Codigo_Producto": "P004", "Nombre": "Broca para concreto"},
        ]
        productos_orden_b = list(reversed(productos_orden_a))

        inv_a = _construir_inventario_controlado(productos_orden_a)
        inv_b = _construir_inventario_controlado(productos_orden_b)

        res_a = busqueda.ejecutar_busqueda_productos(inv_a, "broca")
        res_b = busqueda.ejecutar_busqueda_productos(inv_b, "broca")

        codigos_a = [p.codigo_producto for p in res_a.todos_los_resultados]
        codigos_b = [p.codigo_producto for p in res_b.todos_los_resultados]

        self.assertEqual(codigos_a, ["P002", "P004", "P003", "P001"])
        self.assertEqual(codigos_a, codigos_b)

    def test_08_diez_resultados_por_pagina(self) -> None:
        """Caso 8 (RF-036 / CA-040): Mostrar como máximo diez resultados por página."""
        veinticinco_productos = [
            {"Codigo_Producto": f"TOR{i:03d}", "Nombre": f"Tornillo hexagonal medida {i:02d}"}
            for i in range(1, 26)
        ]
        inv_25 = _construir_inventario_controlado(veinticinco_productos)

        res_p1 = busqueda.ejecutar_busqueda_productos(inv_25, "tornillo", pagina=1)
        self.assertEqual(res_p1.total_resultados, 25)
        self.assertEqual(res_p1.tamano_pagina, 10)
        self.assertEqual(len(res_p1.resultados_pagina), 10)
        self.assertEqual(res_p1.total_paginas, 3)
        self.assertTrue(res_p1.requiere_paginacion)
        self.assertEqual(res_p1.indice_inicio_mostrado, 1)
        self.assertEqual(res_p1.indice_fin_mostrado, 10)

        # Cuando hay <= 10 resultados, no requiere paginación
        res_pocos = busqueda.ejecutar_busqueda_productos(self.inventario_base, "martillo")
        self.assertEqual(res_pocos.total_resultados, 4)
        self.assertFalse(res_pocos.requiere_paginacion)

    def test_09_navegacion_entre_paginas_sin_duplicados(self) -> None:
        """Caso 9 (RF-036 / CA-040): Navegación entre páginas respetando el orden y sin duplicar productos."""
        veintitres_productos = [
            {"Codigo_Producto": f" item_{i:03d}".strip(), "Nombre": f"Llave combinada número {i:02d}"}
            for i in range(1, 24)
        ]
        inv_23 = _construir_inventario_controlado(veintitres_productos)

        p1 = busqueda.ejecutar_busqueda_productos(inv_23, "llave", pagina=1)
        p2 = busqueda.ejecutar_busqueda_productos(inv_23, "llave", pagina=2)
        p3 = busqueda.ejecutar_busqueda_productos(inv_23, "llave", pagina=3)

        self.assertFalse(p1.tiene_pagina_anterior)
        self.assertTrue(p1.tiene_pagina_siguiente)

        self.assertTrue(p2.tiene_pagina_anterior)
        self.assertTrue(p2.tiene_pagina_siguiente)

        self.assertTrue(p3.tiene_pagina_anterior)
        self.assertFalse(p3.tiene_pagina_siguiente)

        codigos_p1 = [p.codigo_producto for p in p1.resultados_pagina]
        codigos_p2 = [p.codigo_producto for p in p2.resultados_pagina]
        codigos_p3 = [p.codigo_producto for p in p3.resultados_pagina]
        todos_concatenados = codigos_p1 + codigos_p2 + codigos_p3

        self.assertEqual(len(todos_concatenados), 23)
        self.assertEqual(len(set(todos_concatenados)), 23)
        self.assertEqual(
            todos_concatenados,
            [p.codigo_producto for p in p1.todos_los_resultados],
        )

    def test_10_ultima_pagina_con_menos_de_diez_resultados(self) -> None:
        """Caso 10 (RF-036 / CA-040): Manejo exacto de la última página cuando tiene menos de diez elementos."""
        trece_productos = [
            {"Codigo_Producto": f"CLV{i:03d}", "Nombre": f"Clavo de acero {i:02d} pulgadas"}
            for i in range(1, 14)
        ]
        inv_13 = _construir_inventario_controlado(trece_productos)

        p2 = busqueda.ejecutar_busqueda_productos(inv_13, "clavo", pagina=2)
        self.assertEqual(p2.pagina_actual, 2)
        self.assertEqual(p2.total_paginas, 2)
        self.assertEqual(len(p2.resultados_pagina), 3)
        self.assertEqual(p2.indice_inicio_mostrado, 11)
        self.assertEqual(p2.indice_fin_mostrado, 13)

        # Solicitar una página mayor al máximo ajusta de forma segura a la última página disponible
        p_exceso = busqueda.ejecutar_busqueda_productos(inv_13, "clavo", pagina=99)
        self.assertEqual(p_exceso.pagina_actual, 2)
        self.assertEqual(len(p_exceso.resultados_pagina), 3)

    def test_11_reinicio_de_paginacion_al_cambiar_termino(self) -> None:
        """Caso 11 (Sección 6.6): La paginación se reinicia a la página 1 cuando cambia el término buscado."""
        self.assertEqual(
            busqueda.resolver_pagina_busqueda("tornillo", "tornillo", pagina_solicitada=3),
            3,
        )
        self.assertEqual(
            busqueda.resolver_pagina_busqueda("tornillo", "TORNILLO ", pagina_solicitada=3),
            3,
        )
        self.assertEqual(
            busqueda.resolver_pagina_busqueda("tornillo", "martillo", pagina_solicitada=3),
            1,
        )

    def test_12_busqueda_vacia(self) -> None:
        """Caso 12 (RF-037 / CA-041): Manejo de búsqueda vacía sin ejecutar consulta sobre el inventario."""
        for termino_vacio in ("", "   ", "\t\n "):
            # Se pasa origen_datos=None para demostrar que ni siquiera intenta acceder a los datos
            res = busqueda.ejecutar_busqueda_productos(None, termino_vacio)
            self.assertEqual(res.estado, busqueda.EstadoBusqueda.BUSQUEDA_VACIA)
            self.assertFalse(res.tiene_resultados)
            self.assertEqual(res.total_resultados, 0)
            self.assertEqual(res.mensaje_usuario, busqueda.MENSAJE_BUSQUEDA_VACIA)

    def test_13_busqueda_sin_coincidencias(self) -> None:
        """Caso 13 (RF-008 / CA-006): Muestra exactamente el mensaje aprobado cuando no existen coincidencias."""
        res = busqueda.ejecutar_busqueda_productos(
            self.inventario_base, " motosierra industrial inexistente "
        )
        self.assertEqual(res.estado, busqueda.EstadoBusqueda.SIN_RESULTADOS)
        self.assertFalse(res.tiene_resultados)
        self.assertEqual(res.total_resultados, 0)
        self.assertEqual(
            res.mensaje_usuario,
            "No encontramos este producto en nuestro inventario",
        )

    def test_14_ausencia_de_busqueda_por_marca_categoria_codigo_descripcion_o_ubicacion(self) -> None:
        """Caso 14 (RF-001 / CA-043): La búsqueda evalúa exclusivamente `Nombre` y no busca por otros campos."""
        # "Truper" y "Pretul" están en Descripcion, no en Nombre
        self.assertEqual(
            busqueda.ejecutar_busqueda_productos(self.inventario_base, "Truper").total_resultados,
            0,
        )
        self.assertEqual(
            busqueda.ejecutar_busqueda_productos(self.inventario_base, "Pretul").total_resultados,
            0,
        )
        # "Herramientas Manuales" y "CAT01" son categoría, no Nombre
        self.assertEqual(
            busqueda.ejecutar_busqueda_productos(
                self.inventario_base, "Herramientas Manuales"
            ).total_resultados,
            0,
        )
        self.assertEqual(
            busqueda.ejecutar_busqueda_productos(self.inventario_base, "CAT01").total_resultados,
            0,
        )
        # "MAR001" y "000125" son códigos de producto, no Nombre
        self.assertEqual(
            busqueda.ejecutar_busqueda_productos(self.inventario_base, "MAR001").total_resultados,
            0,
        )
        self.assertEqual(
            busqueda.ejecutar_busqueda_productos(self.inventario_base, "000125").total_resultados,
            0,
        )
        # "R01" y "U001" son ubicaciones, no Nombre
        self.assertEqual(
            busqueda.ejecutar_busqueda_productos(self.inventario_base, "R01").total_resultados,
            0,
        )


class TestIntegracionInventarioGitHubYApp(unittest.TestCase):
    """Sección 10.3 — Pruebas de integración con `inventario.py`, `github_inventario.py` y `app.py`."""

    def test_01_integracion_con_datos_estructurados_de_inventario_py(self) -> None:
        """Verifica compatibilidad directa con `crear_inventario_demostrativo()` y preservación de ceros iniciales."""
        inv_demo = motor.crear_inventario_demostrativo()
        res = busqueda.ejecutar_busqueda_productos(inv_demo, "cinta")
        self.assertEqual(res.estado, busqueda.EstadoBusqueda.CON_RESULTADOS)
        self.assertEqual(res.total_resultados, 1)
        prod = res.resultados_pagina[0]
        # Verifica conservación de ceros iniciales ("000125") y estructura para el Prompt 05
        self.assertEqual(prod.codigo_producto, "000125")
        self.assertEqual(prod.nombre, "Cinta aislante negra")
        self.assertIn("Electricidad", prod.nombre_categoria)
        self.assertIsNotNone(prod.ubicacion_principal)
        self.assertEqual(len(prod.ubicaciones_secundarias), 1)

    def test_02_compatibilidad_con_github_inventario_y_actualizacion_sin_reinicio(self) -> None:
        """Verifica lectura mediante `github_inventario.py` y actualización vigente sin reiniciar Streamlit (RF-028)."""
        inv_v1 = _construir_inventario_controlado(
            [{"Codigo_Producto": "MAR001", "Nombre": "Martillo de uña"}]
        )
        inv_v2 = _construir_inventario_controlado(
            [
                {"Codigo_Producto": "MAR001", "Nombre": "Martillo de uña"},
                {"Codigo_Producto": "MAR009", "Nombre": "Martillo demoledor pesado"},
            ]
        )
        payloads = [
            _crear_payload_github_desde_inventario(inv_v1, sha="sha_version_1"),
            _crear_payload_github_desde_inventario(inv_v2, sha="sha_version_2"),
        ]
        indice_llamada = {"n": 0}

        def mock_http(url: str, headers: Mapping[str, str], timeout: float) -> gh.RespuestaHTTPGitHub:
            idx = min(indice_llamada["n"], len(payloads) - 1)
            indice_llamada["n"] += 1
            return gh.RespuestaHTTPGitHub(
                status_code=200,
                cuerpo=json.dumps(payloads[idx]).encode("utf-8"),
                encabezados={"Content-Type": "application/json"},
                url=url,
            )

        def descargador_con_mock(
            config: gh.ConfiguracionRepositorioGitHub = gh.CONFIGURACION_POR_DEFECTO,
        ) -> gh.ResultadoLecturaInventarioRemoto:
            return gh.descargar_inventario_remoto(config=config, ejecutor_http=mock_http)

        estado_sesion: dict[str, Any] = {}

        # Primera búsqueda: obtiene versión 1 desde GitHub
        r1 = app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "martillo",
            estado=estado_sesion,
            descargador_remoto=descargador_con_mock,
        )
        self.assertEqual(r1.estado_operativo, app_ferms.EstadoOperativoInterfaz.RESULTADOS_ENCONTRADOS)
        self.assertEqual(r1.sha_github, "sha_version_1")
        self.assertIsNotNone(r1.resultado_busqueda)
        assert r1.resultado_busqueda is not None
        self.assertEqual(r1.resultado_busqueda.total_resultados, 1)

        # Segunda búsqueda sin reiniciar sesión/Streamlit: reconoce el cambio confirmado en versión 2
        r2 = app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "martillo",
            estado=estado_sesion,
            descargador_remoto=descargador_con_mock,
        )
        self.assertEqual(r2.estado_operativo, app_ferms.EstadoOperativoInterfaz.RESULTADOS_ENCONTRADOS)
        self.assertEqual(r2.sha_github, "sha_version_2")
        assert r2.resultado_busqueda is not None
        self.assertEqual(r2.resultado_busqueda.total_resultados, 2)

    def test_03_manejo_de_inventario_inexistente(self) -> None:
        """Verifica que el inventario confirmado como inexistente se distinga de 'producto no encontrado'."""
        def mock_http_404_archivo(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            if "/contents/" in url:
                return gh.RespuestaHTTPGitHub(
                    status_code=404,
                    cuerpo=json.dumps({"message": "Not Found"}).encode("utf-8"),
                    url=url,
                )
            if "/branches/" in url:
                return gh.RespuestaHTTPGitHub(
                    status_code=200,
                    cuerpo=json.dumps({"name": "main", "commit": {"sha": "abc"}}).encode("utf-8"),
                    url=url,
                )
            return gh.RespuestaHTTPGitHub(
                status_code=200,
                cuerpo=json.dumps({"id": 1, "full_name": "JunyMSAI/FerreteriaMS"}).encode("utf-8"),
                url=url,
            )

        def descargador_404(
            config: gh.ConfiguracionRepositorioGitHub = gh.CONFIGURACION_POR_DEFECTO,
        ) -> gh.ResultadoLecturaInventarioRemoto:
            return gh.descargar_inventario_remoto(
                config=config, ejecutor_http=mock_http_404_archivo
            )

        resp = app_ferms.procesar_consulta_busqueda_publica(
            "martillo", descargador_remoto=descargador_404
        )
        self.assertEqual(
            resp.estado_operativo,
            app_ferms.EstadoOperativoInterfaz.INVENTARIO_NO_INICIALIZADO,
        )
        self.assertEqual(
            resp.categoria_consulta,
            gh.CategoriaResultadoConsulta.INVENTARIO_NO_INICIALIZADO,
        )
        self.assertEqual(
            resp.codigo_error_github,
            gh.CodigoErrorGitHub.ARCHIVO_REMOTO_INEXISTENTE,
        )
        self.assertNotEqual(resp.mensaje_principal, busqueda.MENSAJE_PRODUCTO_NO_ENCONTRADO)
        self.assertTrue(resp.permite_reintentar)

    def test_04_manejo_de_errores_tecnicos_de_github_y_ocultamiento_de_secretos(self) -> None:
        """Verifica RF-038 / CA-042: distingue errores técnicos de búsquedas sin resultados y protege tokens."""
        errores_simulados = [
            gh.ErrorConexionRedGitHub(
                "Fallo de red simulado con token ghp_SecretoSuperConfidencial123456",
                es_reintentable=True,
            ),
            gh.ErrorTiempoEsperaGitHub("Timeout simulado", es_reintentable=True),
            gh.ErrorServidorGitHub("Error 503 de GitHub", status_code=503, es_reintentable=True),
            gh.ErrorLimiteSolicitudesGitHub("Rate limit alcanzado", status_code=429, es_reintentable=True),
            gh.ErrorCredencialInvalidaGitHub(
                "Credencial rechazada Bearer github_pat_TokenPrivado999", status_code=401
            ),
        ]

        for error_sim in errores_simulados:
            def descargador_fallido(
                config: gh.ConfiguracionRepositorioGitHub = gh.CONFIGURACION_POR_DEFECTO,
                _err: Exception = error_sim,
            ) -> gh.ResultadoLecturaInventarioRemoto:
                raise _err

            resp = app_ferms.procesar_consulta_busqueda_publica(
                "martillo", descargador_remoto=descargador_fallido
            )
            self.assertEqual(
                resp.estado_operativo,
                app_ferms.EstadoOperativoInterfaz.ERROR_CONEXION_O_AUTORIZACION,
            )
            self.assertEqual(
                resp.categoria_consulta,
                gh.CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO,
            )
            self.assertTrue(resp.permite_reintentar)
            self.assertNotEqual(resp.mensaje_principal, busqueda.MENSAJE_PRODUCTO_NO_ENCONTRADO)
            self.assertNotIn("ghp_SecretoSuperConfidencial123456", resp.detalle_estado)
            self.assertNotIn("github_pat_TokenPrivado999", resp.detalle_estado)

    def test_05_manejo_de_inventario_remoto_invalido_o_corrupto(self) -> None:
        """Verifica que un archivo Excel remoto corrupto o con esquema inválido se reporte adecuadamente."""
        for error_datos in (
            gh.ErrorArchivoExcelRemotoCorrupto("Archivo .xlsx ilegible"),
            gh.ErrorEsquemaInventarioRemoto("Falta la hoja Ubicaciones"),
        ):
            def descargador_invalido(
                config: gh.ConfiguracionRepositorioGitHub = gh.CONFIGURACION_POR_DEFECTO,
                _err: Exception = error_datos,
            ) -> gh.ResultadoLecturaInventarioRemoto:
                raise _err

            resp = app_ferms.procesar_consulta_busqueda_publica(
                "martillo", descargador_remoto=descargador_invalido
            )
            self.assertEqual(
                resp.estado_operativo,
                app_ferms.EstadoOperativoInterfaz.INVENTARIO_REMOTO_INVALIDO,
            )
            self.assertEqual(
                resp.categoria_consulta,
                gh.CategoriaResultadoConsulta.DATOS_REMOTOS_INVALIDOS,
            )
            self.assertTrue(resp.permite_reintentar)
            self.assertNotEqual(resp.mensaje_principal, busqueda.MENSAJE_PRODUCTO_NO_ENCONTRADO)

    def test_06_ausencia_de_escrituras_remotas_y_locales(self) -> None:
        """Verifica que la búsqueda pública no crea `03_Aplicacion/inventario.xlsx` ni realiza escrituras HTTP."""
        self.assertFalse(
            RUTA_MAESTRO_DEFINITIVO.exists(),
            "El archivo maestro definitivo no debe existir localmente en esta etapa.",
        )

        # Verificar que ni busqueda.py ni app.py contienen llamadas HTTP de escritura (PUT, POST, DELETE, PATCH)
        for ruta_archivo in (
            RUTA_APLICACION / "busqueda.py",
            RUTA_APLICACION / "app.py",
        ):
            codigo = ruta_archivo.read_text(encoding="utf-8")
            for metodo_prohibido in ('"PUT"', '"POST"', '"DELETE"', '"PATCH"', "'PUT'", "'POST'", "'DELETE'", "'PATCH'"):
                self.assertNotIn(metodo_prohibido, codigo)

        self.assertFalse(RUTA_MAESTRO_DEFINITIVO.exists())

    def test_07_ausencia_de_dependencias_operativas_de_gemini_api(self) -> None:
        """Verifica CA-032 y CA-033: `app.py` y `busqueda.py` no importan ni invocan `google-genai` ni exigen API key."""
        for nombre_modulo in ("app.py", "busqueda.py"):
            ruta = RUTA_APLICACION / nombre_modulo
            texto = ruta.read_text(encoding="utf-8")
            arbol = ast.parse(texto, filename=str(ruta))

            modulos_importados: list[str] = []
            for nodo in ast.walk(arbol):
                if isinstance(nodo, ast.Import):
                    modulos_importados.extend(alias.name for alias in nodo.names)
                elif isinstance(nodo, ast.ImportFrom) and nodo.module:
                    modulos_importados.append(nodo.module)

            for mod in modulos_importados:
                self.assertFalse(
                    mod.startswith("google") or "genai" in mod,
                    f"No debe existir importación de Gemini API en {nombre_modulo}: {mod}",
                )

            self.assertNotIn("GEMINI_API_KEY", texto)
            self.assertNotIn("generate_content", texto)
            self.assertNotIn("st.chat_input", texto)

    def test_08_interfaz_streamlit_apptest_flujos_principales(self) -> None:
        """Verifica CA-007, CA-032, CA-034, CA-040, CA-041, CA-042 y CA-043 en la interfaz Streamlit (`app.py`)."""
        ruta_app = str(RUTA_APLICACION / "app.py")

        # 1. Inicio sin GEMINI_API_KEY: estado inicial antes de buscar
        at = AppTest.from_file(ruta_app)
        at.run(timeout=15)
        self.assertFalse(at.exception, f"La app no debe lanzar excepción al iniciar: {at.exception}")
        self.assertTrue(any("FerreteríaMS" in t.value for t in at.title))
        # No debe existir sino un único campo de texto (búsqueda por nombre, sin filtros de marca/categoría)
        self.assertEqual(len(at.text_input), 1)
        self.assertEqual(len(at.selectbox), 0)
        self.assertEqual(len(at.multiselect), 0)

        # 2. Búsqueda vacía al presionar Buscar sin texto
        at.button(key="btn_ejecutar_busqueda").click()
        at.run(timeout=15)
        self.assertEqual(len(at.warning), 1)
        self.assertIn("escribe el nombre de un producto", at.warning[0].value.lower())

        # 3. Búsqueda con más de 10 resultados y navegación de páginas (simulando inventario en GitHub)
        quince_productos = [
            {"Codigo_Producto": f"TAL{i:03d}", "Nombre": f"Taladro rotomartillo modelo {i:02d}"}
            for i in range(1, 16)
        ]
        inv_15 = _construir_inventario_controlado(quince_productos)
        lectura_simulada = gh.ResultadoLecturaInventarioRemoto(
            propietario="JunyMSAI",
            repositorio="FerreteriaMS",
            rama="main",
            ruta_archivo="03_Aplicacion/inventario.xlsx",
            sha_github="sha_test_15",
            sha256_local="hash_local_15",
            tamano_bytes=1024,
            inventario=inv_15,
        )

        with patch("github_inventario.descargar_inventario_remoto", return_value=lectura_simulada):
            at_busq = AppTest.from_file(ruta_app)
            at_busq.run(timeout=15)
            at_busq.text_input(key="campo_nombre_producto").input("taladro")
            at_busq.button(key="btn_ejecutar_busqueda").click()
            at_busq.run(timeout=15)

            self.assertFalse(at_busq.exception)
            self.assertEqual(len(at_busq.success), 1)
            self.assertIn("Mostrando 1–10 de 15", at_busq.success[0].value)

            # Avanzar a la página 2 (debe mostrar 11–15 de 15)
            at_busq.button(key="btn_pagina_siguiente").click()
            at_busq.run(timeout=15)
            self.assertIn("Mostrando 11–15 de 15", at_busq.success[0].value)

            # Búsqueda sin coincidencias
            at_busq.text_input(key="campo_nombre_producto").input("producto_que_no_existe_xyz")
            at_busq.button(key="btn_ejecutar_busqueda").click()
            at_busq.run(timeout=15)
            textos_info = [elem.value for elem in at_busq.info]
            self.assertIn("No encontramos este producto en nuestro inventario", textos_info)

        # 4. Estado cuando el inventario maestro no ha sido inicializado en GitHub
        error_no_init = gh.ErrorArchivoRemotoInexistente(
            "El archivo maestro todavía no existe en GitHub."
        )
        with patch("github_inventario.descargar_inventario_remoto", side_effect=error_no_init):
            at_no_init = AppTest.from_file(ruta_app)
            at_no_init.run(timeout=15)
            at_no_init.text_input(key="campo_nombre_producto").input("martillo")
            at_no_init.button(key="btn_ejecutar_busqueda").click()
            at_no_init.run(timeout=15)

            self.assertEqual(len(at_no_init.warning), 1)
            self.assertIn("todavía no ha sido inicializado", at_no_init.warning[0].value)
            textos_info_no_init = [elem.value for elem in at_no_init.info]
            self.assertNotIn(
                "No encontramos este producto en nuestro inventario",
                textos_info_no_init,
            )

    def test_09_regresion_busqueda_vacia_despues_de_busqueda_exitosa_limpia_sesion(self) -> None:
        """Verifica que una búsqueda vacía tras una búsqueda exitosa limpie inventario, SHA, término, página y selección."""
        quince_productos = [
            {"Codigo_Producto": f"TAL{i:03d}", "Nombre": f"Taladro percutor modelo {i:02d}"}
            for i in range(1, 16)
        ]
        inv_v1 = _construir_inventario_controlado(quince_productos)
        inv_v2 = _construir_inventario_controlado(
            quince_productos
            + [{"Codigo_Producto": "TAL099", "Nombre": "Taladro industrial extra"}]
        )
        lecturas = [
            gh.ResultadoLecturaInventarioRemoto(
                propietario="JunyMSAI",
                repositorio="FerreteriaMS",
                rama="main",
                ruta_archivo="03_Aplicacion/inventario.xlsx",
                sha_github="sha_v1_activo",
                sha256_local="hash_v1",
                tamano_bytes=1024,
                inventario=inv_v1,
            ),
            gh.ResultadoLecturaInventarioRemoto(
                propietario="JunyMSAI",
                repositorio="FerreteriaMS",
                rama="main",
                ruta_archivo="03_Aplicacion/inventario.xlsx",
                sha_github="sha_v2_nuevo",
                sha256_local="hash_v2",
                tamano_bytes=1024,
                inventario=inv_v2,
            ),
        ]
        llamadas_remotas = {"total": 0}

        def descargador_controlado(
            config: gh.ConfiguracionRepositorioGitHub = gh.CONFIGURACION_POR_DEFECTO,
        ) -> gh.ResultadoLecturaInventarioRemoto:
            idx = min(llamadas_remotas["total"], len(lecturas) - 1)
            llamadas_remotas["total"] += 1
            return lecturas[idx]

        estado_sesion: dict[str, Any] = {}

        # 1. Búsqueda válida inicial
        r_exito = app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "taladro",
            pagina=1,
            forzar_recarga_remota=True,
            estado=estado_sesion,
            descargador_remoto=descargador_controlado,
        )
        self.assertEqual(r_exito.estado_operativo, app_ferms.EstadoOperativoInterfaz.RESULTADOS_ENCONTRADOS)
        self.assertEqual(llamadas_remotas["total"], 1)
        self.assertIs(estado_sesion[app_ferms.CLAVE_INVENTARIO_SESION], inv_v1)
        self.assertEqual(estado_sesion[app_ferms.CLAVE_SHA_SESION], "sha_v1_activo")

        # 2. Navegación a página 2 de la búsqueda válida sin volver a descargar de GitHub
        r_pag2 = app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "taladro",
            pagina=2,
            forzar_recarga_remota=False,
            estado=estado_sesion,
            descargador_remoto=descargador_controlado,
        )
        self.assertEqual(r_pag2.estado_operativo, app_ferms.EstadoOperativoInterfaz.RESULTADOS_ENCONTRADOS)
        self.assertEqual(llamadas_remotas["total"], 1)
        self.assertEqual(estado_sesion[app_ferms.CLAVE_PAGINA_ACTUAL], 2)
        app_ferms.preparar_seleccion_producto_para_detalle("TAL001", estado=estado_sesion)
        self.assertEqual(estado_sesion[app_ferms.CLAVE_PRODUCTO_SELECCIONADO], "TAL001")

        # 3. Búsqueda vacía posterior: no debe conservar referencias al inventario ni SHA anteriores
        for termino_vacio, recarga in (("", True), ("   ", False)):
            r_vacia = app_ferms.ejecutar_flujo_busqueda_en_sesion(
                termino_vacio,
                pagina=2,
                forzar_recarga_remota=recarga,
                estado=estado_sesion,
                descargador_remoto=descargador_controlado,
            )
            self.assertEqual(r_vacia.estado_operativo, app_ferms.EstadoOperativoInterfaz.BUSQUEDA_VACIA)
            self.assertEqual(llamadas_remotas["total"], 1)
            self.assertIsNone(r_vacia.inventario_vigente)
            self.assertIsNone(r_vacia.sha_github)
            self.assertIsNone(estado_sesion[app_ferms.CLAVE_INVENTARIO_SESION])
            self.assertIsNone(estado_sesion[app_ferms.CLAVE_SHA_SESION])
            self.assertEqual(estado_sesion[app_ferms.CLAVE_TERMINO_BUSCADO], "")
            self.assertEqual(estado_sesion[app_ferms.CLAVE_PAGINA_ACTUAL], 1)
            self.assertIsNone(estado_sesion[app_ferms.CLAVE_PRODUCTO_SELECCIONADO])

        # 4. Intentar invocar con forzar_recarga_remota=False tras búsqueda vacía obliga a descargar versión nueva
        r_posterior = app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "taladro",
            pagina=2,
            forzar_recarga_remota=False,
            estado=estado_sesion,
            descargador_remoto=descargador_controlado,
        )
        self.assertEqual(llamadas_remotas["total"], 2)
        self.assertEqual(r_posterior.sha_github, "sha_v2_nuevo")
        self.assertIs(estado_sesion[app_ferms.CLAVE_INVENTARIO_SESION], inv_v2)
        self.assertEqual(estado_sesion[app_ferms.CLAVE_SHA_SESION], "sha_v2_nuevo")
        self.assertEqual(estado_sesion[app_ferms.CLAVE_PAGINA_ACTUAL], 1)

    def test_10_regresion_errores_remotos_despues_de_busqueda_exitosa_limpian_sesion(self) -> None:
        """Verifica que cualquier error remoto posterior a una búsqueda exitosa limpie los datos previos en sesión."""
        inv_inicial = _construir_inventario_controlado(
            [
                {"Codigo_Producto": f"MAR{i:03d}", "Nombre": f"Martillo profesional {i:02d}"}
                for i in range(1, 15)
            ]
        )
        lectura_ok = gh.ResultadoLecturaInventarioRemoto(
            propietario="JunyMSAI",
            repositorio="FerreteriaMS",
            rama="main",
            ruta_archivo="03_Aplicacion/inventario.xlsx",
            sha_github="sha_ok_inicial",
            sha256_local="hash_ok",
            tamano_bytes=1024,
            inventario=inv_inicial,
        )

        errores_remotos = [
            (
                gh.ErrorConexionRedGitHub("Caída de red simulada", es_reintentable=True),
                app_ferms.EstadoOperativoInterfaz.ERROR_CONEXION_O_AUTORIZACION,
            ),
            (
                gh.ErrorArchivoRemotoInexistente("Archivo eliminado o no inicializado"),
                app_ferms.EstadoOperativoInterfaz.INVENTARIO_NO_INICIALIZADO,
            ),
            (
                gh.ErrorArchivoExcelRemotoCorrupto("Archivo .xlsx dañado"),
                app_ferms.EstadoOperativoInterfaz.INVENTARIO_REMOTO_INVALIDO,
            ),
        ]

        for exc_remota, estado_esperado in errores_remotos:
            estado_sesion: dict[str, Any] = {}
            app_ferms.ejecutar_flujo_busqueda_en_sesion(
                "martillo",
                pagina=1,
                forzar_recarga_remota=True,
                estado=estado_sesion,
                descargador_remoto=lambda config=gh.CONFIGURACION_POR_DEFECTO: lectura_ok,
            )
            app_ferms.ejecutar_flujo_busqueda_en_sesion(
                "martillo",
                pagina=2,
                forzar_recarga_remota=False,
                estado=estado_sesion,
                descargador_remoto=lambda config=gh.CONFIGURACION_POR_DEFECTO: lectura_ok,
            )
            app_ferms.preparar_seleccion_producto_para_detalle("MAR001", estado=estado_sesion)
            self.assertIs(estado_sesion[app_ferms.CLAVE_INVENTARIO_SESION], inv_inicial)
            self.assertEqual(estado_sesion[app_ferms.CLAVE_SHA_SESION], "sha_ok_inicial")
            self.assertEqual(estado_sesion[app_ferms.CLAVE_PAGINA_ACTUAL], 2)

            def descargador_error(
                config: gh.ConfiguracionRepositorioGitHub = gh.CONFIGURACION_POR_DEFECTO,
                _exc: Exception = exc_remota,
            ) -> gh.ResultadoLecturaInventarioRemoto:
                raise _exc

            r_fallida = app_ferms.ejecutar_flujo_busqueda_en_sesion(
                "martillo",
                pagina=1,
                forzar_recarga_remota=True,
                estado=estado_sesion,
                descargador_remoto=descargador_error,
            )
            self.assertEqual(r_fallida.estado_operativo, estado_esperado)
            self.assertIsNone(r_fallida.inventario_vigente)
            self.assertIsNone(r_fallida.sha_github)
            self.assertIsNone(estado_sesion[app_ferms.CLAVE_INVENTARIO_SESION])
            self.assertIsNone(estado_sesion[app_ferms.CLAVE_SHA_SESION])
            self.assertEqual(estado_sesion[app_ferms.CLAVE_TERMINO_BUSCADO], "")
            self.assertEqual(estado_sesion[app_ferms.CLAVE_PAGINA_ACTUAL], 1)
            self.assertIsNone(estado_sesion[app_ferms.CLAVE_PRODUCTO_SELECCIONADO])

            # Incluso si se intenta paginar después del fallo, no puede reutilizar datos obsoletos
            r_reintento_pag = app_ferms.ejecutar_flujo_busqueda_en_sesion(
                "martillo",
                pagina=2,
                forzar_recarga_remota=False,
                estado=estado_sesion,
                descargador_remoto=descargador_error,
            )
            self.assertEqual(r_reintento_pag.estado_operativo, estado_esperado)
            self.assertIsNone(estado_sesion[app_ferms.CLAVE_INVENTARIO_SESION])
            self.assertIsNone(estado_sesion[app_ferms.CLAVE_SHA_SESION])

    def test_11_regresion_cambio_de_termino_despues_de_busqueda_exitosa_no_reutiliza_obsoletos(self) -> None:
        """Verifica que cambiar el término tras una búsqueda exitosa reinicie página y descargue inventario vigente."""
        productos_v1 = [
            {"Codigo_Producto": f"TAL{i:03d}", "Nombre": f"Taladro percutor {i:02d}"}
            for i in range(1, 15)
        ] + [{"Codigo_Producto": "MAR001", "Nombre": "Martillo de uña"}]
        productos_v2 = productos_v1 + [
            {"Codigo_Producto": "MAR002", "Nombre": "Martillo de bola"}
        ]
        inv_v1 = _construir_inventario_controlado(productos_v1)
        inv_v2 = _construir_inventario_controlado(productos_v2)

        lecturas = [
            gh.ResultadoLecturaInventarioRemoto(
                propietario="JunyMSAI",
                repositorio="FerreteriaMS",
                rama="main",
                ruta_archivo="03_Aplicacion/inventario.xlsx",
                sha_github="sha_busqueda_taladro",
                sha256_local="hash_1",
                tamano_bytes=1024,
                inventario=inv_v1,
            ),
            gh.ResultadoLecturaInventarioRemoto(
                propietario="JunyMSAI",
                repositorio="FerreteriaMS",
                rama="main",
                ruta_archivo="03_Aplicacion/inventario.xlsx",
                sha_github="sha_busqueda_martillo",
                sha256_local="hash_2",
                tamano_bytes=1024,
                inventario=inv_v2,
            ),
        ]
        conteo_descargas = {"n": 0}

        def descargador_versionado(
            config: gh.ConfiguracionRepositorioGitHub = gh.CONFIGURACION_POR_DEFECTO,
        ) -> gh.ResultadoLecturaInventarioRemoto:
            idx = min(conteo_descargas["n"], len(lecturas) - 1)
            conteo_descargas["n"] += 1
            return lecturas[idx]

        estado_sesion: dict[str, Any] = {}

        # 1. Búsqueda de "taladro" y avance a página 2 reutilizando inventario en sesión
        app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "taladro",
            pagina=1,
            forzar_recarga_remota=True,
            estado=estado_sesion,
            descargador_remoto=descargador_versionado,
        )
        self.assertEqual(conteo_descargas["n"], 1)

        app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "taladro",
            pagina=2,
            forzar_recarga_remota=False,
            estado=estado_sesion,
            descargador_remoto=descargador_versionado,
        )
        self.assertEqual(conteo_descargas["n"], 1)
        self.assertEqual(estado_sesion[app_ferms.CLAVE_PAGINA_ACTUAL], 2)
        app_ferms.preparar_seleccion_producto_para_detalle("TAL001", estado=estado_sesion)

        # 2. Cambio de término a "martillo" incluso si se pasa forzar_recarga_remota=False y pagina=2:
        #    no debe reutilizar inv_v1 ni sha_busqueda_taladro, debe descargar inv_v2 y reiniciar a página 1
        r_nuevo_termino = app_ferms.ejecutar_flujo_busqueda_en_sesion(
            "martillo",
            pagina=2,
            forzar_recarga_remota=False,
            estado=estado_sesion,
            descargador_remoto=descargador_versionado,
        )
        self.assertEqual(conteo_descargas["n"], 2)
        self.assertEqual(r_nuevo_termino.sha_github, "sha_busqueda_martillo")
        assert r_nuevo_termino.resultado_busqueda is not None
        self.assertEqual(r_nuevo_termino.resultado_busqueda.total_resultados, 2)
        self.assertEqual(estado_sesion[app_ferms.CLAVE_TERMINO_BUSCADO], "martillo")
        self.assertEqual(estado_sesion[app_ferms.CLAVE_PAGINA_ACTUAL], 1)
        self.assertIs(estado_sesion[app_ferms.CLAVE_INVENTARIO_SESION], inv_v2)
        self.assertEqual(estado_sesion[app_ferms.CLAVE_SHA_SESION], "sha_busqueda_martillo")
        self.assertIsNone(estado_sesion[app_ferms.CLAVE_PRODUCTO_SELECCIONADO])

        # 3. Verificación en AppTest: búsqueda vacía tras búsqueda exitosa limpia st.session_state en la UI
        ruta_app = str(RUTA_APLICACION / "app.py")
        with patch("github_inventario.descargar_inventario_remoto", return_value=lecturas[0]):
            at = AppTest.from_file(ruta_app)
            at.run(timeout=15)
            at.text_input(key="campo_nombre_producto").input("taladro")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)
            self.assertIsNotNone(at.session_state[app_ferms.CLAVE_INVENTARIO_SESION])
            self.assertEqual(at.session_state[app_ferms.CLAVE_SHA_SESION], "sha_busqueda_taladro")

            # Ejecutar búsqueda vacía en la interfaz
            at.text_input(key="campo_nombre_producto").input("   ")
            at.button(key="btn_ejecutar_busqueda").click()
            at.run(timeout=15)
            self.assertIsNone(at.session_state[app_ferms.CLAVE_INVENTARIO_SESION])
            self.assertIsNone(at.session_state[app_ferms.CLAVE_SHA_SESION])
            self.assertEqual(at.session_state[app_ferms.CLAVE_TERMINO_BUSCADO], "")
            self.assertEqual(at.session_state[app_ferms.CLAVE_PAGINA_ACTUAL], 1)
            self.assertIsNone(at.session_state[app_ferms.CLAVE_PRODUCTO_SELECCIONADO])


if __name__ == "__main__":
    unittest.main()

