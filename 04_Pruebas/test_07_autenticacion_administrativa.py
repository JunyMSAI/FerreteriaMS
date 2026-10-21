"""Pruebas automatizadas unitarias, de seguridad y de integración Streamlit para la autenticación administrativa.

Proyecto: FerreteríaMS v0
Tarea: FERMS-V0-P07 (Autenticación administrativa)
Módulos probados: `03_Aplicacion/autenticacion.py`, `03_Aplicacion/app.py` y `03_Aplicacion/estilos.css`.
Requisitos cubiertos: RF-009, RF-011, RF-012, RF-013 (parcial), RF-032, RF-033, RF-034.
Criterios cubiertos: CA-007, CA-009, CA-010, CA-011, CA-019 (parcial), CA-027 (parcial),
CA-028, CA-029, CA-030 (parcial), CA-031, CA-032, CA-033, CA-034, CA-058 (parcial), CA-059.

Nota de seguridad:
Este archivo no contiene contraseñas reales ni hashes de producción. Todas las pruebas
generan valores sintéticos efímeros en memoria (`secrets.token_urlsafe`) durante su ejecución.
"""

from __future__ import annotations

import ast
import os
import re
import secrets
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
RUTA_AUTENTICACION_PY = RUTA_APLICACION / "autenticacion.py"
RUTA_ESTILOS_CSS = RUTA_APLICACION / "estilos.css"
RUTA_MAESTRO_DEFINITIVO = RUTA_APLICACION / "inventario.xlsx"

if str(RUTA_APLICACION) not in sys.path:
    sys.path.insert(0, str(RUTA_APLICACION))

import app as app_ferms  # noqa: E402
import autenticacion as auth  # noqa: E402
import github_inventario as gh  # noqa: E402
import inventario as motor  # noqa: E402


def _construir_inventario_simulado() -> motor.InventarioDatos:
    """Construye un `InventarioDatos` controlado en memoria para pruebas públicas sin login."""
    df_categorias = pd.DataFrame(
        [{"Categoria_ID": "CAT01", "Nombre_Categoria": "Herramientas Manuales"}]
    )
    df_ubicaciones = pd.DataFrame(
        [
            {
                "Ubicacion_ID": "U001",
                "Rack": "R01",
                "Columna": "C01",
                "Nivel": "N01",
                "Posicion": "P01",
            }
        ]
    )
    df_productos = pd.DataFrame(
        [
            {
                "Codigo_Producto": "MAR001",
                "Nombre": "Martillo de uña profesional",
                "Categoria_ID": "CAT01",
                "Descripcion": "Martillo para carpintería.",
            }
        ]
    )
    df_asignaciones = pd.DataFrame(
        [{"Codigo_Producto": "MAR001", "Ubicacion_ID": "U001", "Principal": "Sí"}]
    )
    return motor.construir_inventario_datos(
        {
            motor.HOJA_PRODUCTOS: df_productos,
            motor.HOJA_CATEGORIAS: df_categorias,
            motor.HOJA_UBICACIONES: df_ubicaciones,
            motor.HOJA_ASIGNACIONES: df_asignaciones,
        }
    )


class TestSeguridadAutenticacionAdministrativa(unittest.TestCase):
    """Sección 11.1 del Prompt 07 — 14 pruebas obligatorias de seguridad de autenticación."""

    def setUp(self) -> None:
        self.usuario_sintetico = f"admin_test_{secrets.token_hex(4)}"
        self.clave_sintetica = f"ClaveSinteticaEfimera_{secrets.token_urlsafe(12)}"
        self.hash_valido = auth.generar_hash_contrasena(self.clave_sintetica)
        self.entorno_valido = {
            "FERRETERIAMS_ADMIN_USER": self.usuario_sintetico,
            "FERRETERIAMS_ADMIN_PASSWORD_HASH": self.hash_valido,
        }

    def test_01_configuracion_administrativa_valida(self) -> None:
        """Caso 1 (CA-059): Reconoce configuración válida por entorno o `st.secrets` con hash Argon2id."""
        # Desde fuente de entorno
        res_env = auth.obtener_configuracion_admin(fuente_entorno=self.entorno_valido)
        self.assertEqual(res_env.estado, auth.EstadoConfiguracionAdmin.VALIDA)
        self.assertTrue(res_env.es_valida)
        self.assertIsNotNone(res_env.configuracion)
        assert res_env.configuracion is not None
        self.assertEqual(res_env.configuracion.usuario, self.usuario_sintetico)
        self.assertTrue(auth.verificar_configuracion_admin(fuente_entorno=self.entorno_valido))

        # Desde sección `[admin]` en `st.secrets`
        secretos_simulados = {
            "admin": {
                "usuario": self.usuario_sintetico,
                "password_hash": self.hash_valido,
            }
        }
        res_sec = auth.obtener_configuracion_admin(
            fuente_entorno={},
            fuente_secretos=secretos_simulados,
        )
        self.assertEqual(res_sec.estado, auth.EstadoConfiguracionAdmin.VALIDA)
        self.assertTrue(res_sec.es_valida)

    def test_02_configuracion_inexistente_o_invalida_deshabilita_acceso(self) -> None:
        """Caso 2 (Sección 6.4): Sin credenciales configuradas el acceso permanece deshabilitado."""
        res_vacia = auth.obtener_configuracion_admin(fuente_entorno={}, fuente_secretos={})
        self.assertEqual(res_vacia.estado, auth.EstadoConfiguracionAdmin.NO_CONFIGURADA)
        self.assertFalse(res_vacia.es_valida)
        self.assertIsNone(res_vacia.configuracion)
        self.assertFalse(auth.verificar_configuracion_admin(fuente_entorno={}, fuente_secretos={}))

        # Intentar autenticarse sin configuración rechaza el acceso de forma segura
        res_auth = auth.verificar_credenciales_admin(
            self.usuario_sintetico,
            self.clave_sintetica,
            fuente_entorno={},
            fuente_secretos={},
        )
        self.assertFalse(res_auth.autenticado)
        self.assertEqual(res_auth.codigo, auth.CodigoResultadoAutenticacion.CONFIGURACION_AUSENTE)
        self.assertEqual(res_auth.mensaje_usuario, auth.MENSAJE_ADMIN_NO_CONFIGURADO)

        # Configuración con contraseña en texto plano o hash SHA-256 es rechazada como inválida
        for valor_inseguro in (
            self.clave_sintetica,
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "$md5$inseguro",
        ):
            res_inv = auth.obtener_configuracion_admin(
                fuente_entorno={
                    "FERRETERIAMS_ADMIN_USER": self.usuario_sintetico,
                    "FERRETERIAMS_ADMIN_PASSWORD_HASH": valor_inseguro,
                }
            )
            self.assertEqual(
                res_inv.estado, auth.EstadoConfiguracionAdmin.CONFIGURACION_INVALIDA
            )
            self.assertFalse(res_inv.es_valida)

    def test_03_contrasena_correcta_autoriza_acceso(self) -> None:
        """Caso 3 (CA-010): Usuario y contraseña válidos autorizan el acceso administrativo."""
        res = auth.verificar_credenciales_admin(
            self.usuario_sintetico,
            self.clave_sintetica,
            fuente_entorno=self.entorno_valido,
        )
        self.assertTrue(res.autenticado)
        self.assertEqual(res.codigo, auth.CodigoResultadoAutenticacion.AUTENTICACION_EXITOSA)
        self.assertEqual(res.usuario, self.usuario_sintetico)

    def test_04_contrasena_incorrecta_deniega_acceso(self) -> None:
        """Caso 4 (CA-011): Contraseña incorrecta deniega el acceso administrativo."""
        clave_erronea = f"{self.clave_sintetica}_incorrecta"
        res = auth.verificar_credenciales_admin(
            self.usuario_sintetico,
            clave_erronea,
            fuente_entorno=self.entorno_valido,
        )
        self.assertFalse(res.autenticado)
        self.assertEqual(res.codigo, auth.CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS)
        self.assertIsNone(res.usuario)
        self.assertEqual(res.mensaje_usuario, auth.MENSAJE_CREDENCIALES_INVALIDAS)

    def test_05_usuario_incorrecto_deniega_acceso_sin_enumeracion(self) -> None:
        """Caso 5 (CA-011, Sección 7): Usuario incorrecto deniega el acceso con idéntico mensaje."""
        res_usr_mal = auth.verificar_credenciales_admin(
            "usuario_inexistente_xyz",
            self.clave_sintetica,
            fuente_entorno=self.entorno_valido,
        )
        res_pwd_mal = auth.verificar_credenciales_admin(
            self.usuario_sintetico,
            "clave_incorrecta_xyz",
            fuente_entorno=self.entorno_valido,
        )
        self.assertFalse(res_usr_mal.autenticado)
        self.assertEqual(res_usr_mal.codigo, auth.CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS)
        # El mensaje devuelto no permite distinguir si el usuario existe o no (Sección 7)
        self.assertEqual(res_usr_mal.mensaje_usuario, res_pwd_mal.mensaje_usuario)

    def test_06_usuario_vacio_es_rechazado(self) -> None:
        """Caso 6 (Sección 7): Usuario vacío o solo espacios es rechazado como datos incompletos."""
        for usuario_vacio in ("", "   ", "\t\n", None):
            res = auth.verificar_credenciales_admin(
                usuario_vacio,
                self.clave_sintetica,
                fuente_entorno=self.entorno_valido,
            )
            self.assertFalse(res.autenticado)
            self.assertEqual(res.codigo, auth.CodigoResultadoAutenticacion.DATOS_INCOMPLETOS)

    def test_07_contrasena_vacia_es_rechazada(self) -> None:
        """Caso 7 (Sección 7): Contraseña vacía o solo espacios es rechazada como datos incompletos."""
        for clave_vacia in ("", "   ", "\t", None):
            res = auth.verificar_credenciales_admin(
                self.usuario_sintetico,
                clave_vacia,
                fuente_entorno=self.entorno_valido,
            )
            self.assertFalse(res.autenticado)
            self.assertEqual(res.codigo, auth.CodigoResultadoAutenticacion.DATOS_INCOMPLETOS)

    def test_08_hash_y_verificacion_mediante_argon2id(self) -> None:
        """Caso 8 (Sección 6.3, CA-059): El hash utiliza Argon2id con sal única y parámetros PHC."""
        self.assertEqual(auth.ALGORITMO_HASH_CONTRASENA, "argon2id")
        hash_1 = auth.generar_hash_contrasena(self.clave_sintetica)
        hash_2 = auth.generar_hash_contrasena(self.clave_sintetica)

        self.assertTrue(hash_1.startswith("$argon2id$v=19$"))
        self.assertTrue(hash_2.startswith("$argon2id$v=19$"))
        # Dos hashes de la misma entrada producen salidas distintas gracias a la sal aleatoria
        self.assertNotEqual(hash_1, hash_2)
        self.assertTrue(auth.es_hash_contrasena_valido(hash_1))
        self.assertTrue(auth.es_hash_contrasena_valido(hash_2))
        self.assertTrue(auth.verificar_contrasena_hash(self.clave_sintetica, hash_1))
        self.assertTrue(auth.verificar_contrasena_hash(self.clave_sintetica, hash_2))
        self.assertFalse(auth.verificar_contrasena_hash("otra_cadena", hash_1))

    def test_09_ausencia_de_contrasenas_en_texto_plano_dentro_del_repositorio(self) -> None:
        """Caso 9 (CA-029, CA-059): Ningún archivo rastreado en el repositorio contiene secretos o hashes reales."""
        archivos_codigo_y_config = [
            RUTA_APLICACION / "app.py",
            RUTA_APLICACION / "autenticacion.py",
            RUTA_APLICACION / "busqueda.py",
            RUTA_APLICACION / "github_inventario.py",
            RUTA_APLICACION / "inventario.py",
            RUTA_APLICACION / "estilos.css",
            RAIZ_PROYECTO / "requirements.txt",
        ]
        patron_hash_literal = re.compile(r"\$argon2(?:id|i|d)\$v=\d+\$m=\d+,t=\d+,p=\d+\$[A-Za-z0-9+/=_-]+\$[A-Za-z0-9+/=_-]+")
        for ruta in archivos_codigo_y_config:
            contenido = ruta.read_text(encoding="utf-8")
            self.assertIsNone(
                patron_hash_literal.search(contenido),
                f"No debe existir ningún hash Argon2 literal codificado en {ruta.name}",
            )
            for prohibido in ("admin123", "password123", "123456", "ferreteria123"):
                self.assertNotIn(prohibido, contenido.lower())

        # Verificar que no exista ningún archivo `.streamlit/secrets.toml` versionado o local con secretos
        ruta_secrets_toml = RAIZ_PROYECTO / ".streamlit" / "secrets.toml"
        self.assertFalse(
            ruta_secrets_toml.exists(),
            "No debe incluirse un archivo .streamlit/secrets.toml con credenciales en el repositorio.",
        )

    def test_10_ausencia_de_credenciales_reales_en_mensajes_de_error_y_repr(self) -> None:
        """Caso 10 (CA-028): Ni los mensajes de error ni `repr(ConfiguracionAdmin)` exponen contraseñas o hashes."""
        cfg = auth.ConfiguracionAdmin(
            usuario=self.usuario_sintetico,
            password_hash=self.hash_valido,
        )
        self.assertNotIn(self.hash_valido, repr(cfg))
        self.assertNotIn(self.hash_valido, str(cfg))
        self.assertIn(auth.MARCA_SECRETO_OCULTO, repr(cfg))

        # Sanitización de errores que contengan accidentalmente un hash o contraseña
        texto_contaminado = (
            f"Fallo al verificar password={self.clave_sintetica} contra {self.hash_valido}"
        )
        texto_limpio = auth.ocultar_secretos_autenticacion(
            texto_contaminado, (self.clave_sintetica,)
        )
        self.assertNotIn(self.clave_sintetica, texto_limpio)
        self.assertNotIn(self.hash_valido, texto_limpio)

        # Forzar una excepción interna durante la verificación y comprobar que no filtra la contraseña
        with patch(
            "autenticacion.obtener_configuracion_admin",
            side_effect=RuntimeError(f"Error con secreto {self.clave_sintetica} y {self.hash_valido}"),
        ):
            res_err = auth.verificar_credenciales_admin(
                self.usuario_sintetico,
                self.clave_sintetica,
            )
            self.assertFalse(res_err.autenticado)
            self.assertEqual(
                res_err.codigo,
                auth.CodigoResultadoAutenticacion.ERROR_INTERNO_AUTENTICACION,
            )
            self.assertNotIn(self.clave_sintetica, res_err.mensaje_usuario)
            self.assertNotIn(self.hash_valido, res_err.mensaje_usuario)

    def test_11_acceso_administrativo_denegado_cuando_no_hay_autenticacion(self) -> None:
        """Caso 11 (RF-011, CA-009, CA-027): Sin sesión autenticada, `requerir_autorizacion_admin` rechaza el acceso."""
        estado_no_autenticado: dict[str, Any] = {}
        self.assertFalse(auth.esta_autenticado_en_sesion(estado_no_autenticado))
        self.assertIsNone(auth.obtener_usuario_autenticado(estado_no_autenticado))

        with self.assertRaises(auth.ErrorAutorizacionAdmin) as ctx:
            auth.requerir_autorizacion_admin(estado_no_autenticado)
        self.assertEqual(ctx.exception.mensaje, auth.MENSAJE_ACCESO_NO_AUTORIZADO)

    def test_12_cierre_de_sesion_revoca_autorizacion_e_impide_reutilizar_token(self) -> None:
        """Caso 12 (Sección 7): Cerrar sesión borra marcadores e invalida el token en el servidor."""
        estado_sesion: dict[str, Any] = {}
        res_login = auth.iniciar_sesion_admin(
            self.usuario_sintetico,
            self.clave_sintetica,
            estado_sesion,
            fuente_entorno=self.entorno_valido,
        )
        self.assertTrue(res_login.autenticado)
        self.assertTrue(auth.esta_autenticado_en_sesion(estado_sesion))

        # Conservar una copia del objeto `EstadoSesionAdmin` antes de cerrar sesión
        copia_estado_sesion_antiguo = estado_sesion[auth.CLAVE_SESION_ADMIN]

        auth.cerrar_sesion_admin(estado_sesion)
        self.assertFalse(auth.esta_autenticado_en_sesion(estado_sesion))
        self.assertIsNone(estado_sesion[auth.CLAVE_SESION_ADMIN])

        # Incluso si alguien vuelve a inyectar el objeto anterior tras el logout, el servidor lo rechaza
        estado_sesion[auth.CLAVE_SESION_ADMIN] = copia_estado_sesion_antiguo
        self.assertFalse(auth.esta_autenticado_en_sesion(estado_sesion))
        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.requerir_autorizacion_admin(estado_sesion)

    def test_13_aislamiento_entre_dos_sesiones_independientes(self) -> None:
        """Caso 13 (Sección 11.1): Autenticar o cerrar una sesión no afecta a otra sesión independiente."""
        sesion_a: dict[str, Any] = {}
        sesion_b: dict[str, Any] = {}

        auth.iniciar_sesion_admin(
            self.usuario_sintetico,
            self.clave_sintetica,
            sesion_a,
            fuente_entorno=self.entorno_valido,
        )
        self.assertTrue(auth.esta_autenticado_en_sesion(sesion_a))
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion_b))

        # Autenticar también la sesión B y luego cerrar únicamente la sesión A
        auth.iniciar_sesion_admin(
            self.usuario_sintetico,
            self.clave_sintetica,
            sesion_b,
            fuente_entorno=self.entorno_valido,
        )
        self.assertTrue(auth.esta_autenticado_en_sesion(sesion_a))
        self.assertTrue(auth.esta_autenticado_en_sesion(sesion_b))

        auth.cerrar_sesion_admin(sesion_a)
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion_a))
        self.assertTrue(auth.esta_autenticado_en_sesion(sesion_b))
        auth.cerrar_sesion_admin(sesion_b)

    def test_14_imposibilidad_de_convertir_marcador_publico_en_autorizacion_sin_verificacion(self) -> None:
        """Caso 14 (Sección 8.3 y 11.1): Manipular claves en `session_state` no concede acceso administrativo."""
        sesion_manipulada: dict[str, Any] = {
            "admin": True,
            "is_admin": True,
            "es_admin": True,
            "autenticado": True,
            "ferms_admin_autenticado": True,
            auth.CLAVE_SESION_ADMIN: True,
        }
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion_manipulada))

        # Intentar inyectar un diccionario o un `EstadoSesionAdmin` falsificado sin firma del servidor
        sesion_manipulada[auth.CLAVE_SESION_ADMIN] = {
            "autenticado": True,
            "usuario": self.usuario_sintetico,
            "token_sesion": "token_falso",
            "firma_hmac": "firma_falsa",
        }
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion_manipulada))

        estado_falsificado = auth.EstadoSesionAdmin(
            autenticado=True,
            usuario=self.usuario_sintetico,
            token_sesion="token_inventado_por_atacante",
            firma_hmac="0" * 64,
            autenticado_en_epoch=1700000000.0,
            ultima_actividad_epoch=1700000000.0,
        )
        sesion_manipulada[auth.CLAVE_SESION_ADMIN] = estado_falsificado
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion_manipulada))
        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.requerir_autorizacion_admin(sesion_manipulada)

    def test_15_restriccion_de_contexto_movil_y_contratos_preparados_para_prompt_08(self) -> None:
        """Verifica rechazo en contexto móvil detectado (Sección 9) y contratos inactivos de Prompt 08 (Sección 10)."""
        headers_movil = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Mobile/15E148",
            "Sec-CH-UA-Mobile": "?1",
        }
        self.assertEqual(
            auth.detectar_contexto_dispositivo(encabezados_http=headers_movil),
            auth.ContextoDispositivo.MOVIL,
        )

        sesion_movil: dict[str, Any] = {}
        res_movil = auth.iniciar_sesion_admin(
            self.usuario_sintetico,
            self.clave_sintetica,
            sesion_movil,
            fuente_entorno=self.entorno_valido,
            contexto_dispositivo=auth.ContextoDispositivo.MOVIL,
        )
        self.assertFalse(res_movil.autenticado)
        self.assertEqual(
            res_movil.codigo, auth.CodigoResultadoAutenticacion.DISPOSITIVO_NO_PERMITIDO
        )
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion_movil))

        # Verificar que los controles avanzados del Prompt 08 están declarados como contrato pero no activos aún
        self.assertFalse(auth.CONTROLES_AVANZADOS_P08_ACTIVOS)
        self.assertFalse(auth.CONTRATO_EXTENSION_PROMPT_08.activo_en_etapa_actual)
        self.assertEqual(auth.CONTRATO_EXTENSION_PROMPT_08.max_intentos_fallidos, 5)
        self.assertEqual(
            auth.CONTRATO_EXTENSION_PROMPT_08.bloqueos_progresivos_minutos,
            (5, 10, 20, 30),
        )
        self.assertEqual(
            auth.CONTRATO_EXTENSION_PROMPT_08.expiracion_inactividad_segundos, 900
        )

    def test_16_intento_de_emitir_sesion_directamente_sin_verificar_credenciales_falla(self) -> None:
        """Corrección puntual P07 (Prueba 1): `registrar_autenticacion_en_sesion` falla sin verificación previa."""
        estado_directo: dict[str, Any] = {}

        # 1. Intentar emitir sesión pasando únicamente un nombre de usuario (posicional o por clave)
        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.registrar_autenticacion_en_sesion(estado_directo, self.usuario_sintetico)
        self.assertFalse(auth.esta_autenticado_en_sesion(estado_directo))

        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.registrar_autenticacion_en_sesion(
                estado_directo, usuario=self.usuario_sintetico
            )
        self.assertFalse(auth.esta_autenticado_en_sesion(estado_directo))

        # 2. Intentar emitir sesión sin argumentos de verificación
        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.registrar_autenticacion_en_sesion(estado_directo)
        self.assertFalse(auth.esta_autenticado_en_sesion(estado_directo))

        # 3. Intentar emitir sesión con un `ResultadoAutenticacion` o comprobante construido manualmente
        comprobante_falso = auth.ComprobanteVerificacionCredenciales(
            id_comprobante="comprobante_inventado_no_registrado",
            usuario=self.usuario_sintetico,
            emitido_en_epoch=1700000000.0,
            contexto_dispositivo=auth.ContextoDispositivo.ESCRITORIO,
            huella_configuracion="a" * 64,
            firma_hmac="b" * 64,
        )
        resultado_falso = auth.ResultadoAutenticacion(
            autenticado=True,
            codigo=auth.CodigoResultadoAutenticacion.AUTENTICACION_EXITOSA,
            mensaje_usuario=auth.MENSAJE_AUTENTICACION_EXITOSA,
            usuario=self.usuario_sintetico,
            comprobante_verificacion=comprobante_falso,
        )
        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.registrar_autenticacion_en_sesion(estado_directo, resultado_falso)
        self.assertFalse(auth.esta_autenticado_en_sesion(estado_directo))

        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.registrar_autenticacion_en_sesion(
                estado_directo, comprobante_verificacion=comprobante_falso
            )
        self.assertFalse(auth.esta_autenticado_en_sesion(estado_directo))

    def test_17_credenciales_correctas_permiten_emitir_sesion_una_sola_vez_por_verificacion(self) -> None:
        """Corrección puntual P07 (Pruebas 1 y 2): Credenciales válidas emiten sesión y el comprobante es de un solo uso."""
        estado_a: dict[str, Any] = {}
        estado_b: dict[str, Any] = {}

        res_verificado = auth.verificar_credenciales_admin(
            self.usuario_sintetico,
            self.clave_sintetica,
            fuente_entorno=self.entorno_valido,
        )
        self.assertTrue(res_verificado.autenticado)
        self.assertIsNotNone(res_verificado.comprobante_verificacion)

        # El primer canje del comprobante verificado emite una sesión válida
        estado_sesion = auth.registrar_autenticacion_en_sesion(estado_a, res_verificado)
        self.assertTrue(estado_sesion.autenticado)
        self.assertTrue(auth.esta_autenticado_en_sesion(estado_a))
        self.assertEqual(
            auth.requerir_autorizacion_admin(estado_a).usuario,
            self.usuario_sintetico,
        )

        # Intentar reutilizar el mismo comprobante para emitir una segunda sesión debe fallar
        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.registrar_autenticacion_en_sesion(estado_b, res_verificado)
        self.assertFalse(auth.esta_autenticado_en_sesion(estado_b))
        auth.cerrar_sesion_admin(estado_a)

    def test_18_credenciales_incorrectas_no_permiten_crear_sesion(self) -> None:
        """Corrección puntual P07 (Prueba 3): Credenciales incorrectas no emiten comprobante ni sesión."""
        estado: dict[str, Any] = {}
        res_invalido = auth.verificar_credenciales_admin(
            self.usuario_sintetico,
            "contrasena_erronea_no_autorizada",
            fuente_entorno=self.entorno_valido,
        )
        self.assertFalse(res_invalido.autenticado)
        self.assertIsNone(res_invalido.comprobante_verificacion)

        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.registrar_autenticacion_en_sesion(estado, res_invalido)
        self.assertFalse(auth.esta_autenticado_en_sesion(estado))

        res_login_fallido = auth.iniciar_sesion_admin(
            self.usuario_sintetico,
            "contrasena_erronea_no_autorizada",
            estado,
            fuente_entorno=self.entorno_valido,
        )
        self.assertFalse(res_login_fallido.autenticado)
        self.assertFalse(auth.esta_autenticado_en_sesion(estado))


class TestIntegracionStreamlitAutenticacion(unittest.TestCase):
    """Sección 11.2 del Prompt 07 — Pruebas de integración en Streamlit mediante `AppTest`."""

    def setUp(self) -> None:
        self.ruta_app_str = str(RUTA_APP_PY)
        self.usuario_sintetico = f"admin_ui_{secrets.token_hex(3)}"
        self.clave_sintetica = f"ClaveUI_{secrets.token_urlsafe(10)}"
        self.hash_valido = auth.generar_hash_contrasena(self.clave_sintetica)
        self.entorno_valido = {
            "FERRETERIAMS_ADMIN_USER": self.usuario_sintetico,
            "FERRETERIAMS_ADMIN_PASSWORD_HASH": self.hash_valido,
        }
        self.inventario_base = _construir_inventario_simulado()
        self.lectura_simulada = gh.ResultadoLecturaInventarioRemoto(
            propietario="JunyMSAI",
            repositorio="FerreteriaMS",
            rama="main",
            ruta_archivo="03_Aplicacion/inventario.xlsx",
            sha_github="sha_p07_simulado",
            sha256_local="hash_local_p07",
            tamano_bytes=1024,
            inventario=self.inventario_base,
        )

    def test_01_aplicacion_publica_inicia_y_busca_sin_credenciales_administrativas(self) -> None:
        """Sección 11.2 (CA-007, CA-034): La app pública inicia y permite buscar sin credenciales admin configuradas."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("FERRETERIAMS_ADMIN_USER", None)
            os.environ.pop("FERRETERIAMS_ADMIN_USUARIO", None)
            os.environ.pop("FERRETERIAMS_ADMIN_PASSWORD_HASH", None)
            os.environ.pop("FERRETERIAMS_ADMIN_HASH", None)

            with patch(
                "github_inventario.descargar_inventario_remoto",
                return_value=self.lectura_simulada,
            ):
                at = AppTest.from_file(self.ruta_app_str)
                at.run(timeout=15)
                self.assertFalse(at.exception)

                # Realizar búsqueda pública sin iniciar sesión
                at.text_input(key="campo_nombre_producto").input("martillo")
                at.button(key="btn_ejecutar_busqueda").click()
                at.run(timeout=15)

                self.assertFalse(at.exception)
                self.assertEqual(len(at.success), 1)
                self.assertIn("Mostrando 1–1 de 1", at.success[0].value)

                # Si se abre Productos sin credenciales configuradas, el acceso permanece deshabilitado
                at.button(key="btn_nav_productos").click()
                at.run(timeout=15)
                warnings = [w.value for w in at.warning]
                self.assertTrue(
                    any("deshabilitado" in w.lower() for w in warnings),
                    f"Debe advertir que el acceso admin está deshabilitado: {warnings}",
                )

    def test_02_formulario_login_aparece_en_productos_y_rechaza_credenciales_incorrectas(self) -> None:
        """Sección 11.2 (RF-012, CA-009, CA-011): En Productos aparece Login y rechaza credenciales erróneas."""
        with patch.dict(os.environ, self.entorno_valido, clear=False):
            at = AppTest.from_file(self.ruta_app_str)
            at.run(timeout=15)

            # Navegar a la pestaña/sección Productos
            at.button(key="btn_nav_productos").click()
            at.run(timeout=15)
            self.assertFalse(at.exception)

            # Verificar presencia del formulario Login
            campo_usr = at.text_input(key="campo_admin_usuario")
            campo_pwd = at.text_input(key="campo_admin_contrasena")
            boton_login = at.button(key="btn_admin_iniciar_sesion")
            self.assertIsNotNone(campo_usr)
            self.assertIsNotNone(campo_pwd)
            self.assertEqual(boton_login.label, app_ferms.TEXTO_BOTON_LOGIN_ADMIN)

            # Introducir credenciales incorrectas
            campo_usr.input(self.usuario_sintetico)
            campo_pwd.input("contrasena_incorrecta_prueba")
            boton_login.click()
            at.run(timeout=15)

            self.assertFalse(auth.esta_autenticado_en_sesion(at.session_state))
            errores = [e.value for e in at.error]
            self.assertIn(auth.MENSAJE_CREDENCIALES_INVALIDAS, errores)

    def test_03_autenticacion_correcta_habilita_seccion_inicial_y_logout_revoca_acceso(self) -> None:
        """Sección 11.2 (CA-010, Sección 8.2): Login válido abre el panel inicial sin CRUD; Logout cierra sesión."""
        with patch.dict(os.environ, self.entorno_valido, clear=False):
            at = AppTest.from_file(self.ruta_app_str)
            at.run(timeout=15)

            # Entrar a Productos e iniciar sesión con credenciales válidas
            at.button(key="btn_nav_productos").click()
            at.run(timeout=15)

            at.text_input(key="campo_admin_usuario").input(self.usuario_sintetico)
            at.text_input(key="campo_admin_contrasena").input(self.clave_sintetica)
            at.button(key="btn_admin_iniciar_sesion").click()
            at.run(timeout=15)

            self.assertFalse(at.exception)
            self.assertTrue(auth.esta_autenticado_en_sesion(at.session_state))
            self.assertEqual(
                auth.obtener_usuario_autenticado(at.session_state),
                self.usuario_sintetico,
            )

            # Verificar que se muestra la sección administrativa inicial con aviso de mantenimiento pendiente
            subtitulos = [s.value for s in at.subheader]
            self.assertTrue(
                any(app_ferms.TITULO_SECCION_PRODUCTOS_ADMIN in s for s in subtitulos)
            )
            infos = [i.value for i in at.info]
            self.assertTrue(
                any(app_ferms.MENSAJE_MANTENIMIENTO_PENDIENTE_P09 in i for i in infos)
            )

            # Verificar que NO existen formularios activos de CRUD de inventario (Prompt 09)
            self.assertEqual(len(at.text_input), 0)
            self.assertEqual(len(at.selectbox), 0)
            self.assertEqual(len(at.multiselect), 0)
            self.assertEqual(len(at.text_area), 0)

            # Verificar que Gemini permanece en estado «Próximamente» y no operativo
            self.assertEqual(len(at.chat_input), 0)
            self.assertEqual(len(at.chat_message), 0)
            self.assertTrue(any("Asistente Gemini" in s for s in subtitulos))

            # Ejecutar Logout y comprobar que se revoca el acceso administrativo
            boton_logout = at.button(key="btn_admin_cerrar_sesion")
            self.assertEqual(boton_logout.label, app_ferms.TEXTO_BOTON_LOGOUT_ADMIN)
            boton_logout.click()
            at.run(timeout=15)

            self.assertFalse(auth.esta_autenticado_en_sesion(at.session_state))
            self.assertIsNone(auth.obtener_usuario_autenticado(at.session_state))
            # El formulario Login vuelve a presentarse tras cerrar sesión
            self.assertIsNotNone(at.text_input(key="campo_admin_usuario"))
            self.assertIsNotNone(at.button(key="btn_admin_iniciar_sesion"))

    def test_04_nombre_administrativo_con_caracteres_especiales_no_se_interpreta_como_html(self) -> None:
        """Corrección puntual P07 (Prueba 6): Usuario con caracteres HTML/XSS se presenta de forma segura."""
        usuario_caracteres_especiales = "admin_<script>alert('xss')</script>&\"'"
        escapado_esperado = (
            "admin_&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;&amp;&quot;&#x27;"
        )
        self.assertEqual(
            app_ferms.formatear_nombre_usuario_admin_seguro(usuario_caracteres_especiales),
            escapado_esperado,
        )

        # Inspección estática del código de `app.py` para garantizar que `sesion_admin.usuario`
        # no se interpola directamente dentro de ningún bloque con `unsafe_allow_html=True`
        codigo_app = RUTA_APP_PY.read_text(encoding="utf-8")
        arbol_app = ast.parse(codigo_app)
        for nodo in ast.walk(arbol_app):
            if isinstance(nodo, ast.Call):
                tiene_unsafe_html = any(
                    kw.arg == "unsafe_allow_html"
                    and isinstance(kw.value, ast.Constant)
                    and kw.value.value is True
                    for kw in nodo.keywords
                )
                if tiene_unsafe_html and nodo.args:
                    texto_argumento = ast.get_source_segment(codigo_app, nodo.args[0]) or ""
                    self.assertNotIn(
                        "sesion_admin.usuario",
                        texto_argumento,
                        "No se debe interpolar `sesion_admin.usuario` directamente con `unsafe_allow_html=True`.",
                    )

        # Verificación dinámica en Streamlit (`AppTest`) con un nombre de usuario que contiene etiquetas HTML
        entorno_xss = {
            "FERRETERIAMS_ADMIN_USER": usuario_caracteres_especiales,
            "FERRETERIAMS_ADMIN_PASSWORD_HASH": self.hash_valido,
        }
        with patch.dict(os.environ, entorno_xss, clear=False):
            at = AppTest.from_file(self.ruta_app_str)
            at.run(timeout=15)

            at.button(key="btn_nav_productos").click()
            at.run(timeout=15)

            at.text_input(key="campo_admin_usuario").input(usuario_caracteres_especiales)
            at.text_input(key="campo_admin_contrasena").input(self.clave_sintetica)
            at.button(key="btn_admin_iniciar_sesion").click()
            at.run(timeout=15)

            self.assertFalse(at.exception)
            self.assertTrue(auth.esta_autenticado_en_sesion(at.session_state))

            # Ningún bloque `markdown` o `caption` debe contener la etiqueta `<script>` sin escapar
            for bloque_md in at.markdown:
                self.assertNotIn("<script>", bloque_md.value.lower())
                self.assertNotIn("</script>", bloque_md.value.lower())

            captions = [c.value for c in at.caption]
            for cap in captions:
                self.assertNotIn("<script>", cap.lower())
            self.assertTrue(
                any(escapado_esperado in cap for cap in captions),
                f"El nombre de usuario debe mostrarse escapado de forma segura en caption: {captions}",
            )


if __name__ == "__main__":
    unittest.main()

