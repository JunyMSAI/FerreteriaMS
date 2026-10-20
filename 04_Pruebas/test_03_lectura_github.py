"""Pruebas automatizadas (simuladas con mocks) para la lectura del inventario desde GitHub API.

Proyecto: FerreteríaMS v0
Tarea: FERMS-V0-P03
Módulo probado: 03_Aplicacion/github_inventario.py (integrado con 03_Aplicacion/inventario.py)
Requisitos cubiertos: RF-022, RF-023, RF-024, RF-025, RF-027, RF-028, RF-029, RF-030, RF-038.
Criterios cubiertos: CA-020 (parcial), CA-021 (parcial), CA-022, CA-024 (parcial),
CA-025 (parcial), CA-042.

Todas las pruebas de esta suite utilizan respuestas HTTP simuladas (mocks), son 100% reproducibles,
no requieren credenciales reales ni conexión a internet, y verifican que no se realice ninguna
escritura en disco ni en el repositorio remoto.
"""

from __future__ import annotations

import base64
import hashlib
import json
import socket
import sys
import unittest
import urllib.error
from pathlib import Path
from typing import Any, Mapping
from unittest.mock import patch

import pandas as pd

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_APLICACION = RAIZ_PROYECTO / "03_Aplicacion"
RUTA_MAESTRO_DEFINITIVO = RUTA_APLICACION / "inventario.xlsx"

if str(RUTA_APLICACION) not in sys.path:
    sys.path.insert(0, str(RUTA_APLICACION))

import github_inventario as gh  # noqa: E402
import inventario as motor  # noqa: E402


def _respuesta_json(
    status_code: int,
    datos: Any,
    encabezados: Mapping[str, str] | None = None,
    url: str = "https://api.github.com/test",
) -> gh.RespuestaHTTPGitHub:
    """Construye una RespuestaHTTPGitHub simulada con cuerpo JSON."""
    cuerpo = json.dumps(datos).encode("utf-8")
    return gh.RespuestaHTTPGitHub(
        status_code=status_code,
        cuerpo=cuerpo,
        encabezados=dict(encabezados or {"Content-Type": "application/json"}),
        url=url,
    )


def _crear_payload_archivo_github_valido(
    bytes_excel: bytes,
    sha: str = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678",
    ruta: str = "03_Aplicacion/inventario.xlsx",
) -> dict[str, Any]:
    """Construye un payload JSON de GitHub Contents API con contenido Excel codificado en base64."""
    b64 = base64.b64encode(bytes_excel).decode("ascii")
    # Simular saltos de línea cada 60 caracteres como hace GitHub API
    b64_con_saltos = "\n".join(b64[i : i + 60] for i in range(0, len(b64), 60)) + "\n"
    return {
        "name": "inventario.xlsx",
        "path": ruta,
        "sha": sha,
        "size": len(bytes_excel),
        "type": "file",
        "encoding": "base64",
        "content": b64_con_saltos,
    }


class TestConfiguracionYConsultasGitHub(unittest.TestCase):
    """Sección 9.1 — Pruebas de configuración y consulta de existencia y errores de API."""

    def test_configuracion_repositorio_y_rama_por_defecto(self) -> None:
        """Sección 4 y 9.1: Verifica propietario, repositorio, rama y ruta oficiales."""
        cfg = gh.CONFIGURACION_POR_DEFECTO
        self.assertEqual(cfg.propietario, "JunyMSAI")
        self.assertEqual(cfg.repositorio, "FerreteriaMS")
        self.assertEqual(cfg.rama, "main")
        self.assertEqual(cfg.ruta_archivo, "03_Aplicacion/inventario.xlsx")
        self.assertEqual(cfg.repositorio_completo, "JunyMSAI/FerreteriaMS")
        self.assertEqual(
            cfg.url_repositorio(),
            "https://api.github.com/repos/JunyMSAI/FerreteriaMS",
        )
        self.assertEqual(
            cfg.url_rama(),
            "https://api.github.com/repos/JunyMSAI/FerreteriaMS/branches/main",
        )
        self.assertEqual(
            cfg.url_contenido_archivo(),
            "https://api.github.com/repos/JunyMSAI/FerreteriaMS/contents/03_Aplicacion/inventario.xlsx?ref=main",
        )

        # Comprobar encabezados anti-caché para consultar siempre la versión vigente (RF-028)
        headers = gh.construir_encabezados_github()
        self.assertIn("no-cache", headers["Cache-Control"])
        self.assertNotIn("Authorization", headers)

    def test_consulta_archivo_existente(self) -> None:
        """Sección 5.2 y 9.1: Detecta correctamente cuando el archivo maestro existe en GitHub."""
        inv_demo = motor.crear_inventario_demostrativo()
        bytes_xlsx = motor.serializar_inventario_a_bytes(inv_demo)
        sha_esperado = "f00dbabe1234567890abcdef1234567890abcdef"
        payload = _crear_payload_archivo_github_valido(bytes_xlsx, sha=sha_esperado)

        def mock_http(url: str, headers: Mapping[str, str], timeout: float) -> gh.RespuestaHTTPGitHub:
            return _respuesta_json(200, payload, url=url)

        res = gh.consultar_existencia_inventario_remoto(ejecutor_http=mock_http)
        self.assertEqual(res.estado, motor.EstadoExistenciaRemota.EXISTE)
        self.assertTrue(res.existe)
        self.assertFalse(res.inexistencia_confirmada)
        self.assertEqual(res.sha_github, sha_esperado)
        self.assertEqual(res.tamano_bytes, len(bytes_xlsx))
        self.assertEqual(res.categoria_consulta, gh.CategoriaResultadoConsulta.INVENTARIO_DISPONIBLE)
        self.assertIsNone(res.codigo_error)

    def test_consulta_archivo_inexistente_confirmado(self) -> None:
        """Sección 5.2, 7 (escenario 1) y 9.1: Un 404 confirma NO_EXISTE solo si repo y rama responden 200."""
        cfg = gh.CONFIGURACION_POR_DEFECTO
        urls_llamadas: list[str] = []

        def mock_http(url: str, headers: Mapping[str, str], timeout: float) -> gh.RespuestaHTTPGitHub:
            urls_llamadas.append(url)
            if url == cfg.url_contenido_archivo():
                return _respuesta_json(404, {"message": "Not Found"}, url=url)
            if url == cfg.url_repositorio():
                return _respuesta_json(
                    200, {"id": 123, "full_name": "JunyMSAI/FerreteriaMS"}, url=url
                )
            if url == cfg.url_rama():
                return _respuesta_json(
                    200, {"name": "main", "commit": {"sha": "abc1234"}}, url=url
                )
            raise AssertionError(f"URL inesperada: {url}")

        res = gh.consultar_existencia_inventario_remoto(ejecutor_http=mock_http)
        self.assertEqual(res.estado, motor.EstadoExistenciaRemota.NO_EXISTE)
        self.assertTrue(res.inexistencia_confirmada)
        self.assertFalse(res.existe)
        self.assertEqual(res.codigo_error, gh.CodigoErrorGitHub.ARCHIVO_REMOTO_INEXISTENTE)
        self.assertEqual(
            res.categoria_consulta,
            gh.CategoriaResultadoConsulta.INVENTARIO_NO_INICIALIZADO,
        )
        self.assertEqual(
            urls_llamadas,
            [cfg.url_contenido_archivo(), cfg.url_repositorio(), cfg.url_rama()],
        )

    def test_consulta_404_por_repositorio_inaccesible_no_declara_no_existe(self) -> None:
        """Sección 5.2 y 7 (escenario 2): Si el repositorio devuelve 404, el estado es DESCONOCIDO_ERROR."""
        cfg = gh.CONFIGURACION_POR_DEFECTO

        def mock_http(url: str, headers: Mapping[str, str], timeout: float) -> gh.RespuestaHTTPGitHub:
            if url == cfg.url_contenido_archivo():
                return _respuesta_json(404, {"message": "Not Found"}, url=url)
            if url == cfg.url_repositorio():
                return _respuesta_json(404, {"message": "Not Found"}, url=url)
            raise AssertionError(f"No debía consultar rama si el repositorio falló: {url}")

        res = gh.consultar_existencia_inventario_remoto(ejecutor_http=mock_http)
        self.assertEqual(res.estado, motor.EstadoExistenciaRemota.DESCONOCIDO_ERROR)
        self.assertEqual(res.codigo_error, gh.CodigoErrorGitHub.REPOSITORIO_INACCESIBLE)
        self.assertEqual(
            res.categoria_consulta,
            gh.CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO,
        )

        with self.assertRaises(gh.ErrorRepositorioInaccesible):
            gh.consultar_existencia_inventario_remoto(
                ejecutor_http=mock_http, lanzar_excepcion=True
            )

    def test_consulta_404_por_rama_inexistente_no_declara_no_existe(self) -> None:
        """Sección 5.2 y 7 (escenario 3): Si la rama no existe, devuelve DESCONOCIDO_ERROR y RAMA_INEXISTENTE."""
        cfg = gh.CONFIGURACION_POR_DEFECTO

        # Caso A: GitHub responde 404 en contents y luego 404 al verificar la rama
        def mock_http_rama_404(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            if url == cfg.url_contenido_archivo():
                return _respuesta_json(404, {"message": "Not Found"}, url=url)
            if url == cfg.url_repositorio():
                return _respuesta_json(200, {"full_name": "JunyMSAI/FerreteriaMS"}, url=url)
            if url == cfg.url_rama():
                return _respuesta_json(404, {"message": "Branch not found"}, url=url)
            raise AssertionError(f"URL inesperada: {url}")

        res_a = gh.consultar_existencia_inventario_remoto(ejecutor_http=mock_http_rama_404)
        self.assertEqual(res_a.estado, motor.EstadoExistenciaRemota.DESCONOCIDO_ERROR)
        self.assertEqual(res_a.codigo_error, gh.CodigoErrorGitHub.RAMA_INEXISTENTE)

        # Caso B: GitHub informa directamente 'No commit found for the ref main'
        def mock_http_no_commit(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            return _respuesta_json(
                404, {"message": "No commit found for the ref main"}, url=url
            )

        with self.assertRaises(gh.ErrorRamaInexistente):
            gh.consultar_existencia_inventario_remoto(
                ejecutor_http=mock_http_no_commit, lanzar_excepcion=True
            )

    def test_error_autenticacion_401_y_credencial_invalida(self) -> None:
        """Sección 7 (escenario 5) y 9.1: Diferencia error de autenticación (401) y protege el token."""
        token_ficticio = "ghp_TokenSecretoDePruebaNoReal123456789"

        def mock_http_401(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            return _respuesta_json(
                401,
                {"message": f"Bad credentials for token {token_ficticio}"},
                url=url,
            )

        res = gh.consultar_existencia_inventario_remoto(
            token=token_ficticio, ejecutor_http=mock_http_401
        )
        self.assertEqual(res.estado, motor.EstadoExistenciaRemota.DESCONOCIDO_ERROR)
        self.assertEqual(res.codigo_error, gh.CodigoErrorGitHub.CREDENCIAL_INVALIDA)
        self.assertNotIn(token_ficticio, res.mensaje)
        self.assertIn(gh.MARCA_SECRETO_OCULTO, res.mensaje)

        with self.assertRaises(gh.ErrorCredencialInvalidaGitHub) as ctx:
            gh.descargar_inventario_remoto(token=token_ficticio, ejecutor_http=mock_http_401)
        self.assertNotIn(token_ficticio, str(ctx.exception))

    def test_error_permisos_403_acceso_denegado_y_permiso_insuficiente(self) -> None:
        """Sección 7 (escenarios 4 y 5) y 9.1: Diferencia acceso denegado (403) y token sin permisos."""
        # 1. Acceso denegado general sin token
        def mock_http_403_denegado(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            return _respuesta_json(
                403,
                {"message": "Repository access blocked"},
                encabezados={"X-RateLimit-Remaining": "55"},
                url=url,
            )

        res_denegado = gh.consultar_existencia_inventario_remoto(
            ejecutor_http=mock_http_403_denegado
        )
        self.assertEqual(res_denegado.estado, motor.EstadoExistenciaRemota.DESCONOCIDO_ERROR)
        self.assertEqual(res_denegado.codigo_error, gh.CodigoErrorGitHub.ACCESO_DENEGADO)

        with self.assertRaises(gh.ErrorAccesoDenegadoGitHub):
            gh.descargar_inventario_remoto(ejecutor_http=mock_http_403_denegado)

        # 2. Token con permisos insuficientes (403 Resource not accessible by personal access token)
        def mock_http_403_token_insuficiente(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            return _respuesta_json(
                403,
                {"message": "Resource not accessible by personal access token"},
                encabezados={"X-RateLimit-Remaining": "4990"},
                url=url,
            )

        with self.assertRaises(gh.ErrorCredencialInvalidaGitHub) as ctx_insuf:
            gh.descargar_inventario_remoto(
                token="github_pat_TokenFicticioSinPermisos999",
                ejecutor_http=mock_http_403_token_insuficiente,
            )
        self.assertEqual(ctx_insuf.exception.codigo, gh.CodigoErrorGitHub.CREDENCIAL_INVALIDA)

    def test_error_limite_solicitudes_rate_limit(self) -> None:
        """Sección 7 (escenario 6) y 9.1: Detecta límite de solicitudes en HTTP 429 y HTTP 403 con cuota 0."""
        # HTTP 403 con X-RateLimit-Remaining: 0
        def mock_http_ratelimit_403(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            return _respuesta_json(
                403,
                {"message": "API rate limit exceeded for 198.51.100.1."},
                encabezados={"X-RateLimit-Remaining": "0"},
                url=url,
            )

        res = gh.consultar_existencia_inventario_remoto(ejecutor_http=mock_http_ratelimit_403)
        self.assertEqual(res.estado, motor.EstadoExistenciaRemota.DESCONOCIDO_ERROR)
        self.assertEqual(res.codigo_error, gh.CodigoErrorGitHub.LIMITE_SOLICITUDES)

        # HTTP 429 Too Many Requests
        def mock_http_429(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            return _respuesta_json(429, {"message": "Too Many Requests"}, url=url)

        with self.assertRaises(gh.ErrorLimiteSolicitudesGitHub) as ctx:
            gh.descargar_inventario_remoto(ejecutor_http=mock_http_429)
        self.assertTrue(ctx.exception.es_reintentable)

    def test_error_servidor_5xx(self) -> None:
        """Sección 7 (escenario 7) y 9.1: Detecta errores temporales 500/502/503 del servidor de GitHub."""
        for status_5xx in (500, 502, 503, 504):
            def mock_http_5xx(
                url: str, headers: Mapping[str, str], timeout: float, code: int = status_5xx
            ) -> gh.RespuestaHTTPGitHub:
                return _respuesta_json(code, {"message": "Server Error"}, url=url)

            res = gh.consultar_existencia_inventario_remoto(ejecutor_http=mock_http_5xx)
            self.assertEqual(res.estado, motor.EstadoExistenciaRemota.DESCONOCIDO_ERROR)
            self.assertEqual(res.codigo_error, gh.CodigoErrorGitHub.ERROR_SERVIDOR)

            with self.assertRaises(gh.ErrorServidorGitHub) as ctx:
                gh.descargar_inventario_remoto(ejecutor_http=mock_http_5xx)
            self.assertEqual(ctx.exception.status_code, status_5xx)
            self.assertTrue(ctx.exception.es_reintentable)

    def test_error_timeout_y_error_conexion_red(self) -> None:
        """Sección 7 (escenarios 8 y 9) y 9.1 / CA-042: Diferencia timeout y fallo de conexión de red."""
        # 1. Timeout en urlopen
        with patch("urllib.request.urlopen", side_effect=socket.timeout("timed out")):
            res_timeout = gh.consultar_existencia_inventario_remoto()
            self.assertEqual(res_timeout.estado, motor.EstadoExistenciaRemota.DESCONOCIDO_ERROR)
            self.assertEqual(res_timeout.codigo_error, gh.CodigoErrorGitHub.TIEMPO_ESPERA_AGOTADO)

            with self.assertRaises(gh.ErrorTiempoEsperaGitHub) as ctx_to:
                gh.descargar_inventario_remoto()
            self.assertTrue(ctx_to.exception.es_reintentable)

        # 2. Error de conexión de red (URLError por fallo DNS/red)
        error_red = urllib.error.URLError(OSError("Name or service not known"))
        with patch("urllib.request.urlopen", side_effect=error_red):
            res_red = gh.consultar_existencia_inventario_remoto()
            self.assertEqual(res_red.estado, motor.EstadoExistenciaRemota.DESCONOCIDO_ERROR)
            self.assertEqual(res_red.codigo_error, gh.CodigoErrorGitHub.CONEXION_RED_FALLIDA)
            self.assertEqual(
                res_red.categoria_consulta,
                gh.CategoriaResultadoConsulta.ERROR_CONSULTA_INVENTARIO,
            )

            with self.assertRaises(gh.ErrorConexionRedGitHub) as ctx_red:
                gh.descargar_inventario_remoto()
            self.assertTrue(ctx_red.exception.es_reintentable)

    def test_respuesta_inesperada_de_github_api(self) -> None:
        """Sección 7 (escenario 10) y 9.1: Rechaza JSON malformado, listas, directorios o falta de SHA."""
        # 1. Cuerpo no JSON
        def mock_no_json(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            return gh.RespuestaHTTPGitHub(status_code=200, cuerpo=b"<html>No es JSON</html>", url=url)

        with self.assertRaises(gh.ErrorRespuestaInesperadaGitHub):
            gh.descargar_inventario_remoto(ejecutor_http=mock_no_json)

        # 2. JSON lista (como devuelve GitHub cuando la ruta es un directorio)
        def mock_lista(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            return _respuesta_json(200, [{"name": "archivo.txt", "type": "file"}], url=url)

        with self.assertRaises(gh.ErrorRespuestaInesperadaGitHub):
            gh.descargar_inventario_remoto(ejecutor_http=mock_lista)

        # 3. Objeto JSON sin SHA
        def mock_sin_sha(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            return _respuesta_json(
                200,
                {"type": "file", "path": "03_Aplicacion/inventario.xlsx", "sha": ""},
                url=url,
            )

        with self.assertRaises(gh.ErrorRespuestaInesperadaGitHub):
            gh.descargar_inventario_remoto(ejecutor_http=mock_sin_sha)


class TestDescargaYValidacionInventarioRemoto(unittest.TestCase):
    """Sección 9.2 — Pruebas de descarga, identificación de versión SHA y validación con inventario.py."""

    def test_descarga_exitosa_sha_cuatro_hojas_y_ceros_iniciales(self) -> None:
        """Sección 5.3, 5.4, 5.5 y 9.2: Descarga bytes, obtiene SHA, valida 4 hojas y preserva códigos."""
        inv_demo = motor.crear_inventario_demostrativo()
        bytes_xlsx = motor.serializar_inventario_a_bytes(inv_demo)
        sha_github_esperado = "9876543210fedcba9876543210fedcba98765432"
        sha256_local_esperado = hashlib.sha256(bytes_xlsx).hexdigest()
        payload = _crear_payload_archivo_github_valido(bytes_xlsx, sha=sha_github_esperado)

        def mock_http(url: str, headers: Mapping[str, str], timeout: float) -> gh.RespuestaHTTPGitHub:
            return _respuesta_json(200, payload, url=url)

        resultado = gh.descargar_inventario_remoto(ejecutor_http=mock_http)

        # Verificar metadatos de versión (Sección 5.4)
        self.assertEqual(resultado.propietario, "JunyMSAI")
        self.assertEqual(resultado.repositorio, "FerreteriaMS")
        self.assertEqual(resultado.repositorio_completo, "JunyMSAI/FerreteriaMS")
        self.assertEqual(resultado.rama, "main")
        self.assertEqual(resultado.ruta_archivo, "03_Aplicacion/inventario.xlsx")
        self.assertEqual(resultado.sha_github, sha_github_esperado)
        self.assertEqual(resultado.sha256_local, sha256_local_esperado)
        self.assertNotEqual(resultado.sha_github, resultado.sha256_local)
        self.assertEqual(resultado.tamano_bytes, len(bytes_xlsx))
        self.assertEqual(
            resultado.categoria_consulta,
            gh.CategoriaResultadoConsulta.INVENTARIO_DISPONIBLE,
        )

        # Verificar las 4 hojas validadas por el motor existente (CA-022)
        hojas = resultado.inventario.obtener_hojas()
        self.assertEqual(set(hojas.keys()), set(motor.ORDEN_HOJAS))
        self.assertIn("000125", list(resultado.inventario.productos["Codigo_Producto"]))
        prod_cinta = resultado.inventario.obtener_producto_por_codigo("000125")
        self.assertIsNotNone(prod_cinta)
        assert prod_cinta is not None
        self.assertEqual(prod_cinta["ubicacion_principal"]["ubicacion_id"], "U003")

        # Confirmar ausencia de escrituras en disco (Sección 5.3 y 9.2)
        self.assertFalse(RUTA_MAESTRO_DEFINITIVO.exists())

    def test_deteccion_contenido_binario_invalido(self) -> None:
        """Sección 7 (escenario 11) y 9.2: Rechaza base64 corrupto, tamaño 0 o descarga incompleta."""
        # 1. Base64 inválido
        def mock_b64_invalido(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            return _respuesta_json(
                200,
                {
                    "type": "file",
                    "path": "03_Aplicacion/inventario.xlsx",
                    "sha": "abc123456789",
                    "size": 100,
                    "encoding": "base64",
                    "content": "!!!NO_ES_BASE64_VALIDO@@@",
                },
                url=url,
            )

        with self.assertRaises(gh.ErrorContenidoBinarioInvalido) as ctx_b64:
            gh.descargar_inventario_remoto(ejecutor_http=mock_b64_invalido)
        self.assertEqual(
            ctx_b64.exception.codigo, gh.CodigoErrorGitHub.CONTENIDO_BINARIO_INVALIDO
        )

        # 2. Tamaño reportado distinto de los bytes decodificados
        def mock_tamano_inconsistente(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            datos_cortos = b"12345"
            return _respuesta_json(
                200,
                {
                    "type": "file",
                    "path": "03_Aplicacion/inventario.xlsx",
                    "sha": "abc123456789",
                    "size": 999,
                    "encoding": "base64",
                    "content": base64.b64encode(datos_cortos).decode("ascii"),
                },
                url=url,
            )

        with self.assertRaises(gh.ErrorContenidoBinarioInvalido):
            gh.descargar_inventario_remoto(ejecutor_http=mock_tamano_inconsistente)

    def test_deteccion_excel_remoto_corrupto_e_invalido(self) -> None:
        """Sección 5.5, 7 (escenarios 12 y 13) y 9.2: Detecta Excel corrupto o que incumple el esquema."""
        # Escenario 12: Bytes que no son un archivo .xlsx válido
        bytes_corruptos = b"CONTENIDO_QUE_NO_ES_UN_ZIP_NI_EXCEL"
        payload_corrupto = _crear_payload_archivo_github_valido(bytes_corruptos)

        def mock_excel_corrupto(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            return _respuesta_json(200, payload_corrupto, url=url)

        with self.assertRaises(gh.ErrorArchivoExcelRemotoCorrupto) as ctx_corrupto:
            gh.descargar_inventario_remoto(ejecutor_http=mock_excel_corrupto)
        self.assertEqual(
            ctx_corrupto.exception.codigo, gh.CodigoErrorGitHub.ARCHIVO_EXCEL_CORRUPTO
        )
        self.assertEqual(
            ctx_corrupto.exception.categoria,
            gh.CategoriaResultadoConsulta.DATOS_REMOTOS_INVALIDOS,
        )

        # Escenario 13: Archivo .xlsx con datos que violan las reglas del inventario (categoría inexistente)
        inv_demo = motor.crear_inventario_demostrativo()
        hojas_invalidas = inv_demo.obtener_hojas()
        hojas_invalidas[motor.HOJA_PRODUCTOS].loc[0, "Categoria_ID"] = "CAT_INEXISTENTE"

        # Construir bytes .xlsx con esa inconsistencia en memoria
        import io
        import openpyxl

        wb = openpyxl.Workbook()
        if wb.active is not None:
            wb.remove(wb.active)
        for nombre_hoja in motor.ORDEN_HOJAS:
            df = hojas_invalidas[nombre_hoja]
            ws = wb.create_sheet(title=nombre_hoja)
            ws.append(list(df.columns))
            for _, fila in df.iterrows():
                ws.append([str(v) for v in fila])
        buf = io.BytesIO()
        wb.save(buf)
        bytes_esquema_invalido = buf.getvalue()
        payload_invalido = _crear_payload_archivo_github_valido(bytes_esquema_invalido)

        def mock_esquema_invalido(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            return _respuesta_json(200, payload_invalido, url=url)

        with self.assertRaises(gh.ErrorEsquemaInventarioRemoto) as ctx_esquema:
            gh.descargar_inventario_remoto(ejecutor_http=mock_esquema_invalido)
        self.assertEqual(
            ctx_esquema.exception.codigo, gh.CodigoErrorGitHub.ESQUEMA_INVENTARIO_INVALIDO
        )
        self.assertEqual(
            ctx_esquema.exception.categoria,
            gh.CategoriaResultadoConsulta.DATOS_REMOTOS_INVALIDOS,
        )
        self.assertTrue(
            any(
                e.codigo == motor.CodigoErrorInventario.CATEGORIA_INEXISTENTE
                for e in ctx_esquema.exception.errores_inventario
            )
        )


class TestIntegracionInicializacionSegura(unittest.TestCase):
    """Sección 8 y 9.3 — Pruebas de integración entre la consulta GitHub y preparar_inicializacion_segura."""

    def test_estado_existe_impide_inicializacion(self) -> None:
        """Sección 8 y 9.3 (CA-021 parcial): Cuando el archivo existe en GitHub, se bloquea la inicialización."""
        inv_demo = motor.crear_inventario_demostrativo()
        bytes_xlsx = motor.serializar_inventario_a_bytes(inv_demo)
        payload = _crear_payload_archivo_github_valido(bytes_xlsx)

        def mock_existe(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            return _respuesta_json(200, payload, url=url)

        with self.assertRaises(motor.ErrorProteccionInventario) as ctx:
            gh.preparar_inicializacion_desde_consulta_remota(ejecutor_http=mock_existe)
        self.assertEqual(
            ctx.exception.codigo,
            motor.CodigoErrorInventario.PROTECCION_INVENTARIO_EXISTENTE,
        )

    def test_fallos_api_dan_desconocido_error_y_bloquean_inicializacion(self) -> None:
        """Sección 8 y 9.3: Fallos de API nunca se traducen en NO_EXISTE e impiden la inicialización."""
        cfg = gh.CONFIGURACION_POR_DEFECTO

        escenarios_fallo = [
            # Error 503 del servidor
            lambda url, h, t: _respuesta_json(503, {"message": "Service Unavailable"}, url=url),
            # Error 401 de credenciales
            lambda url, h, t: _respuesta_json(401, {"message": "Bad credentials"}, url=url),
            # Error 403 de rate limit
            lambda url, h, t: _respuesta_json(
                403,
                {"message": "API rate limit exceeded"},
                encabezados={"X-RateLimit-Remaining": "0"},
                url=url,
            ),
            # Error 404 porque el repositorio es inaccesible
            lambda url, h, t: _respuesta_json(404, {"message": "Not Found"}, url=url),
            # Error 404 porque la rama no existe
            lambda url, h, t: (
                _respuesta_json(200, {"full_name": "JunyMSAI/FerreteriaMS"}, url=url)
                if url == cfg.url_repositorio()
                else _respuesta_json(404, {"message": "Not Found"}, url=url)
            ),
        ]

        for mock_fallo in escenarios_fallo:
            res_existencia = gh.consultar_existencia_inventario_remoto(ejecutor_http=mock_fallo)
            self.assertEqual(
                res_existencia.estado,
                motor.EstadoExistenciaRemota.DESCONOCIDO_ERROR,
            )
            with self.assertRaises(motor.ErrorProteccionInventario) as ctx:
                gh.preparar_inicializacion_desde_consulta_remota(ejecutor_http=mock_fallo)
            self.assertEqual(
                ctx.exception.codigo,
                motor.CodigoErrorInventario.ESTADO_REMOTO_DESCONOCIDO,
            )

    def test_estado_no_existe_confirmado_prepara_bytes_en_memoria_sin_escribir_disco(self) -> None:
        """Sección 8 y 9.3 (CA-020 parcial): Solo un NO_EXISTE confirmado genera bytes demostrativos en memoria."""
        cfg = gh.CONFIGURACION_POR_DEFECTO

        def mock_no_existe_confirmado(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            if url == cfg.url_contenido_archivo():
                return _respuesta_json(404, {"message": "Not Found"}, url=url)
            if url == cfg.url_repositorio():
                return _respuesta_json(200, {"full_name": "JunyMSAI/FerreteriaMS"}, url=url)
            if url == cfg.url_rama():
                return _respuesta_json(
                    200, {"name": "main", "commit": {"sha": "ca9191d"}}, url=url
                )
            raise AssertionError(f"URL inesperada: {url}")

        res_existencia, bytes_iniciales = gh.preparar_inicializacion_desde_consulta_remota(
            ejecutor_http=mock_no_existe_confirmado
        )
        self.assertEqual(res_existencia.estado, motor.EstadoExistenciaRemota.NO_EXISTE)
        self.assertGreater(len(bytes_iniciales), 0)

        inv_preparado = motor.cargar_inventario_excel(bytes_iniciales)
        self.assertEqual(set(inv_preparado.obtener_hojas().keys()), set(motor.ORDEN_HOJAS))
        self.assertFalse(RUTA_MAESTRO_DEFINITIVO.exists())


class TestSeguridadTransporteYDownloadUrl(unittest.TestCase):
    """Pruebas de seguridad para transporte HTTPS, validación de destino, download_url, redirecciones y token."""

    def test_rechazo_http_no_cifrado_en_solicitudes_y_download_url(self) -> None:
        """Exige HTTPS y rechaza cualquier URL HTTP no cifrada en API y en download_url."""
        # 1. Rechazo directo en ejecutar_solicitud_get_github con HTTP no cifrado
        with patch("urllib.request.urlopen") as mock_urlopen:
            with self.assertRaises(gh.ErrorRespuestaInesperadaGitHub) as ctx_http:
                gh.ejecutar_solicitud_get_github(
                    "http://api.github.com/repos/JunyMSAI/FerreteriaMS",
                    gh.construir_encabezados_github(),
                )
            self.assertEqual(
                ctx_http.exception.codigo, gh.CodigoErrorGitHub.RESPUESTA_INESPERADA
            )
            mock_urlopen.assert_not_called()

        # 2. Rechazo de configuración con url_base_api en HTTP no cifrado
        cfg_http = gh.ConfiguracionRepositorioGitHub(url_base_api="http://api.github.com")
        res_existencia = gh.consultar_existencia_inventario_remoto(config=cfg_http)
        self.assertEqual(
            res_existencia.estado, motor.EstadoExistenciaRemota.DESCONOCIDO_ERROR
        )
        self.assertEqual(
            res_existencia.codigo_error, gh.CodigoErrorGitHub.RESPUESTA_INESPERADA
        )
        with self.assertRaises(gh.ErrorRespuestaInesperadaGitHub):
            gh.descargar_inventario_remoto(config=cfg_http)

        # 3. Rechazo de download_url con esquema HTTP no cifrado sin llegar a invocar la segunda solicitud
        urls_invocadas: list[str] = []

        def mock_download_http(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            urls_invocadas.append(url)
            return _respuesta_json(
                200,
                {
                    "type": "file",
                    "path": "03_Aplicacion/inventario.xlsx",
                    "sha": "1234567890abcdef1234567890abcdef12345678",
                    "size": 128,
                    "encoding": "none",
                    "content": "",
                    "download_url": (
                        "http://raw.githubusercontent.com/JunyMSAI/FerreteriaMS/"
                        "main/03_Aplicacion/inventario.xlsx"
                    ),
                },
                url=url,
            )

        with self.assertRaises(gh.ErrorRespuestaInesperadaGitHub):
            gh.descargar_inventario_remoto(
                token="ghp_TokenDePruebaNoDebeEnviarse12345",
                ejecutor_http=mock_download_http,
            )
        self.assertEqual(len(urls_invocadas), 1)

    def test_rechazo_dominios_externos_y_destinos_no_validos(self) -> None:
        """Valida el dominio y ruta de destino tanto para GitHub API como para download_url."""
        urls_api_invalidas = [
            "https://atacante.ejemplo.com/repos/JunyMSAI/FerreteriaMS",
            "https://api.github.com.atacante.com/repos/JunyMSAI/FerreteriaMS",
            "https://usuario:secreto@api.github.com/repos/JunyMSAI/FerreteriaMS",
            "https://api.github.com:8443/repos/JunyMSAI/FerreteriaMS",
            "https://api.github.com/users/JunyMSAI",
            "https://api.github.com/repos/JunyMSAI/FerreteriaMS/../../otro",
        ]
        with patch("urllib.request.urlopen") as mock_urlopen:
            for url_invalida in urls_api_invalidas:
                with self.assertRaises(
                    gh.ErrorRespuestaInesperadaGitHub, msg=f"Debió fallar: {url_invalida}"
                ):
                    gh.ejecutar_solicitud_get_github(
                        url_invalida, gh.construir_encabezados_github()
                    )
            mock_urlopen.assert_not_called()

        # Validar rechazo de download_url apuntando a dominios externos o a otro repositorio/archivo
        urls_descarga_no_confiables = [
            "https://malicioso.ejemplo.org/JunyMSAI/FerreteriaMS/main/03_Aplicacion/inventario.xlsx",
            "https://raw.githubusercontent.com.atacante.org/JunyMSAI/FerreteriaMS/main/03_Aplicacion/inventario.xlsx",
            "https://raw.githubusercontent.com/OtroPropietario/FerreteriaMS/main/03_Aplicacion/inventario.xlsx",
            "https://raw.githubusercontent.com/JunyMSAI/OtroRepo/main/03_Aplicacion/inventario.xlsx",
            "https://raw.githubusercontent.com/JunyMSAI/FerreteriaMS/main/03_Aplicacion/otro.xlsx",
            "https://raw.githubusercontent.com/JunyMSAI/FerreteriaMS/main/../secreto.xlsx",
        ]
        for url_maliciosa in urls_descarga_no_confiables:
            llamadas: list[tuple[str, dict[str, str]]] = []

            def mock_ejecutor(
                url: str,
                headers: Mapping[str, str],
                timeout: float,
                destino: str = url_maliciosa,
            ) -> gh.RespuestaHTTPGitHub:
                llamadas.append((url, dict(headers)))
                return _respuesta_json(
                    200,
                    {
                        "type": "file",
                        "path": "03_Aplicacion/inventario.xlsx",
                        "sha": "abcdef1234567890abcdef1234567890abcdef12",
                        "size": 256,
                        "encoding": "none",
                        "content": "",
                        "download_url": destino,
                    },
                    url=url,
                )

            with self.assertRaises(
                gh.ErrorRespuestaInesperadaGitHub, msg=f"Debió bloquearse: {url_maliciosa}"
            ):
                gh.descargar_inventario_remoto(
                    token="ghp_TokenDePruebaProtegido987654321",
                    ejecutor_http=mock_ejecutor,
                )
            # Verifica que jamás se realizó una segunda solicitud hacia el download_url no confiable
            self.assertEqual(len(llamadas), 1)

    def test_proteccion_token_en_download_url_y_bloqueo_fuera_de_api_github(self) -> None:
        """Verifica que el token nunca se envíe a raw.githubusercontent.com ni a dominios externos."""
        inv_demo = motor.crear_inventario_demostrativo()
        bytes_xlsx = motor.serializar_inventario_a_bytes(inv_demo)
        sha_esperado = "11223344556677889900aabbccddeeff00112233"
        url_raw_valida = (
            "https://raw.githubusercontent.com/JunyMSAI/FerreteriaMS/"
            "main/03_Aplicacion/inventario.xlsx"
        )
        token_ficticio = "ghp_TokenConfidencialSoloParaApiGitHub123"
        registro_solicitudes: list[tuple[str, dict[str, str]]] = []

        def mock_http_con_download_url(
            url: str, headers: Mapping[str, str], timeout: float
        ) -> gh.RespuestaHTTPGitHub:
            registro_solicitudes.append((url, dict(headers)))
            if url == gh.CONFIGURACION_POR_DEFECTO.url_contenido_archivo():
                return _respuesta_json(
                    200,
                    {
                        "name": "inventario.xlsx",
                        "path": "03_Aplicacion/inventario.xlsx",
                        "sha": sha_esperado,
                        "size": len(bytes_xlsx),
                        "type": "file",
                        "encoding": "none",
                        "content": "",
                        "download_url": url_raw_valida,
                    },
                    url=url,
                )
            if url == url_raw_valida:
                return gh.RespuestaHTTPGitHub(
                    status_code=200,
                    cuerpo=bytes_xlsx,
                    encabezados={"Content-Type": "application/octet-stream"},
                    url=url,
                )
            raise AssertionError(f"URL inesperada: {url}")

        resultado = gh.descargar_inventario_remoto(
            token=token_ficticio,
            ejecutor_http=mock_http_con_download_url,
        )
        self.assertEqual(resultado.sha_github, sha_esperado)
        self.assertEqual(resultado.tamano_bytes, len(bytes_xlsx))
        self.assertEqual(len(registro_solicitudes), 2)

        # Primera solicitud (api.github.com): sí lleva Authorization
        url_1, headers_1 = registro_solicitudes[0]
        self.assertTrue(url_1.startswith("https://api.github.com/"))
        self.assertIn("Authorization", headers_1)

        # Segunda solicitud (raw.githubusercontent.com): NO debe llevar Authorization
        url_2, headers_2 = registro_solicitudes[1]
        self.assertEqual(url_2, url_raw_valida)
        self.assertFalse(
            any(k.lower() == "authorization" for k in headers_2),
            "El encabezado Authorization no debe enviarse a raw.githubusercontent.com",
        )

        # Además, si se invoca directamente ejecutar_solicitud_get_github con Authorization hacia raw.githubusercontent.com, se bloquea
        with patch("urllib.request.urlopen") as mock_urlopen:
            with self.assertRaises(gh.ErrorRespuestaInesperadaGitHub):
                gh.ejecutar_solicitud_get_github(
                    url_raw_valida,
                    gh.construir_encabezados_github(token=token_ficticio),
                )
            mock_urlopen.assert_not_called()

    def test_control_redirecciones_bloquea_http_dominios_externos_y_fuga_de_credenciales(
        self,
    ) -> None:
        """Verifica que las redirecciones bloqueen HTTP, dominios externos y filtración de credenciales."""
        import urllib.request

        manejador = gh._ManejadorRedireccionSeguraGitHub(
            token="ghp_TokenDePruebaEnRedireccion123"
        )
        req_autenticada = urllib.request.Request(
            url="https://api.github.com/repos/JunyMSAI/FerreteriaMS/contents/03_Aplicacion/inventario.xlsx?ref=main",
            headers=gh.construir_encabezados_github(
                token="ghp_TokenDePruebaEnRedireccion123"
            ),
            method="GET",
        )

        # 1. Bloqueo de redirección a HTTP no cifrado
        with self.assertRaises(gh.ErrorRespuestaInesperadaGitHub):
            manejador.redirect_request(
                req_autenticada,
                fp=None,
                code=302,
                msg="Found",
                headers={},
                newurl="http://api.github.com/repos/JunyMSAI/FerreteriaMS",
            )

        # 2. Bloqueo de redirección a dominio externo
        manejador_2 = gh._ManejadorRedireccionSeguraGitHub()
        req_publica = urllib.request.Request(
            url="https://raw.githubusercontent.com/JunyMSAI/FerreteriaMS/main/03_Aplicacion/inventario.xlsx",
            headers=gh.construir_encabezados_github(token=None),
            method="GET",
        )
        with self.assertRaises(gh.ErrorRespuestaInesperadaGitHub):
            manejador_2.redirect_request(
                req_publica,
                fp=None,
                code=302,
                msg="Found",
                headers={},
                newurl="https://atacante.ejemplo.com/inventario.xlsx",
            )

        # 3. Bloqueo de redirección cuando la solicitud original contiene Authorization (incluso hacia dominios de GitHub)
        manejador_3 = gh._ManejadorRedireccionSeguraGitHub(
            token="ghp_TokenDePruebaEnRedireccion123"
        )
        with self.assertRaises(gh.ErrorRespuestaInesperadaGitHub) as ctx_fuga:
            manejador_3.redirect_request(
                req_autenticada,
                fp=None,
                code=302,
                msg="Found",
                headers={},
                newurl="https://objects.githubusercontent.com/github-production-release-asset/123",
            )
        self.assertNotIn("ghp_TokenDePruebaEnRedireccion123", str(ctx_fuga.exception))

        # 4. Redirección HTTPS sin credenciales hacia objects.githubusercontent.com permitida y sin encabezados sensibles
        manejador_4 = gh._ManejadorRedireccionSeguraGitHub()
        req_redirigida = manejador_4.redirect_request(
            req_publica,
            fp=None,
            code=302,
            msg="Found",
            headers={},
            newurl="https://objects.githubusercontent.com/github-production-release-asset/123",
        )
        self.assertIsNotNone(req_redirigida)
        assert req_redirigida is not None
        self.assertEqual(
            req_redirigida.full_url,
            "https://objects.githubusercontent.com/github-production-release-asset/123",
        )
        self.assertFalse(
            any(
                k.lower() in ("authorization", "cookie")
                for k in req_redirigida.headers
            )
        )

        # 5. Límite máximo de redirecciones
        for _ in range(gh.MAX_REDIRECCIONES_GITHUB - 1):
            manejador_4.redirect_request(
                req_publica,
                fp=None,
                code=302,
                msg="Found",
                headers={},
                newurl="https://objects.githubusercontent.com/github-production-release-asset/123",
            )
        with self.assertRaises(gh.ErrorRespuestaInesperadaGitHub):
            manejador_4.redirect_request(
                req_publica,
                fp=None,
                code=302,
                msg="Found",
                headers={},
                newurl="https://objects.githubusercontent.com/github-production-release-asset/123",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)


