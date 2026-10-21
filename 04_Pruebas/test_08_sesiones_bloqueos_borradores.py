"""Pruebas automatizadas de sesiones, bloqueos progresivos y borradores temporales.

Proyecto: FerreteríaMS v0
Tarea: FERMS-V0-P08 (Gestión avanzada de sesiones, bloqueos y borradores)
Módulos probados: `03_Aplicacion/autenticacion.py`, `03_Aplicacion/app.py` y `03_Aplicacion/estilos.css`.
Requisitos cubiertos: RF-009, RF-011, RF-012, RF-013 (parcial), RF-032, RF-033, RF-034,
Sección 5.3 y Sección 6.3 (6.3.1 a 6.3.6).
Criterios cubiertos: CA-007, CA-009, CA-010, CA-011, CA-019 (parcial), CA-027 (parcial),
CA-028, CA-029, CA-030, CA-031, CA-032, CA-033, CA-034, CA-052, CA-053, CA-054, CA-055,
CA-056, CA-057, CA-058 (parcial), CA-059.

Nota de seguridad:
Este archivo utiliza exclusivamente credenciales sintéticas efímeras generadas en memoria
y un reloj simulado inyectable (`RelojSimulado`), sin modificar el reloj del sistema operativo
y sin incluir secretos reales ni hashes de producción.
"""

from __future__ import annotations

import ast
import os
import secrets
import sys
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_APLICACION = RAIZ_PROYECTO / "03_Aplicacion"
RUTA_APP_PY = RUTA_APLICACION / "app.py"
RUTA_AUTENTICACION_PY = RUTA_APLICACION / "autenticacion.py"
RUTA_MAESTRO_DEFINITIVO = RUTA_APLICACION / "inventario.xlsx"

if str(RUTA_APLICACION) not in sys.path:
    sys.path.insert(0, str(RUTA_APLICACION))

import app as app_ferms  # noqa: E402
import autenticacion as auth  # noqa: E402
import github_inventario as gh  # noqa: E402
import inventario as motor  # noqa: E402


class RelojSimulado:
    """Reloj determinista seguro para hilos que permite simular temporizaciones sin espera real."""

    def __init__(self, tiempo_inicial_epoch: float = 1_750_000_000.0) -> None:
        self._lock = threading.RLock()
        self._actual = float(tiempo_inicial_epoch)

    def __call__(self) -> float:
        with self._lock:
            return self._actual

    def avanzar(self, segundos: float) -> float:
        with self._lock:
            self._actual += float(segundos)
            return self._actual

    def fijar(self, epoch: float) -> float:
        with self._lock:
            self._actual = float(epoch)
            return self._actual


def _construir_inventario_simulado_p08() -> motor.InventarioDatos:
    """Construye un `InventarioDatos` controlado en memoria para pruebas de interfaz pública."""
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


class TestSesionesBloqueosYBorradores(unittest.TestCase):
    """Sección 12 del Prompt 08 — 40 verificaciones obligatorias de bloqueos, sesiones y borradores."""

    # Credenciales sintéticas compartidas a nivel de clase para acelerar las 40 pruebas sin debilitar Argon2id
    USUARIO_SINTETICO: str = ""
    CLAVE_SINTETICA: str = ""
    HASH_VALIDO: str = ""
    ENTORNO_VALIDO: dict[str, str] = {}

    @classmethod
    def setUpClass(cls) -> None:
        cls.USUARIO_SINTETICO = f"admin_p08_{secrets.token_hex(4)}"
        cls.CLAVE_SINTETICA = f"ClaveP08_{secrets.token_urlsafe(12)}"
        cls.HASH_VALIDO = auth.generar_hash_contrasena(cls.CLAVE_SINTETICA)
        cls.ENTORNO_VALIDO = {
            "FERRETERIAMS_ADMIN_USER": cls.USUARIO_SINTETICO,
            "FERRETERIAMS_ADMIN_PASSWORD_HASH": cls.HASH_VALIDO,
        }

    def setUp(self) -> None:
        auth.reiniciar_estado_seguridad_servidor()
        self.reloj = RelojSimulado(1_750_000_000.0)
        auth.configurar_reloj_servidor_pruebas(self.reloj)
        self.usuario = self.USUARIO_SINTETICO
        self.clave = self.CLAVE_SINTETICA
        self.hash_valido = self.HASH_VALIDO
        self.entorno = dict(self.ENTORNO_VALIDO)

    def tearDown(self) -> None:
        auth.reiniciar_estado_seguridad_servidor()

    def _parche_verificacion_controlada(self, pausa_segundos: float = 0.0) -> Any:
        """Sustituye únicamente el cálculo Argon2id repetitivo conservando todas las validaciones de `autenticacion.py`."""

        def _verificar_rapido(contrasena_plana: str, hash_almacenado: str) -> bool:
            if pausa_segundos > 0.0:
                time.sleep(pausa_segundos)
            if not isinstance(contrasena_plana, str) or not contrasena_plana:
                return False
            if not auth.es_hash_contrasena_valido(hash_almacenado):
                return False
            return hash_almacenado == self.hash_valido and contrasena_plana == self.clave

        return patch("autenticacion.verificar_contrasena_hash", side_effect=_verificar_rapido)

    def _fallar_intentos(
        self,
        cantidad: int,
        estado: dict[str, Any] | None = None,
        *,
        usar_argon2_real: bool = False,
    ) -> auth.ResultadoAutenticacion:
        ultimo_res: auth.ResultadoAutenticacion | None = None
        with ExitStack() as pila:
            if not usar_argon2_real:
                pila.enter_context(self._parche_verificacion_controlada())
            for _ in range(cantidad):
                if estado is not None:
                    ultimo_res = auth.iniciar_sesion_admin(
                        self.usuario,
                        "clave_incorrecta_sintetica",
                        estado,
                        fuente_entorno=self.entorno,
                        reloj=self.reloj,
                    )
                else:
                    ultimo_res = auth.verificar_credenciales_admin(
                        self.usuario,
                        "clave_incorrecta_sintetica",
                        fuente_entorno=self.entorno,
                        reloj=self.reloj,
                    )
        assert ultimo_res is not None
        return ultimo_res

    def _iniciar_sesion_controlada(
        self,
        estado: dict[str, Any],
        *,
        usuario: str | None = None,
        clave: str | None = None,
        fuente_entorno: dict[str, str] | None = None,
        usar_argon2_real: bool = False,
    ) -> auth.ResultadoAutenticacion:
        with ExitStack() as pila:
            if not usar_argon2_real:
                pila.enter_context(self._parche_verificacion_controlada())
            return auth.iniciar_sesion_admin(
                self.usuario if usuario is None else usuario,
                self.clave if clave is None else clave,
                estado,
                fuente_entorno=self.entorno if fuente_entorno is None else fuente_entorno,
                reloj=self.reloj,
            )

    # =========================================================================
    # 12.1. Pruebas de bloqueo (Casos 1 a 13)
    # =========================================================================

    def test_01_primer_intento_fallido(self) -> None:
        """Caso 1 (CA-052): El primer intento fallido (con Argon2id real) incrementa el contador a 1 sin bloquear."""
        res = self._fallar_intentos(1, usar_argon2_real=True)
        self.assertFalse(res.autenticado)
        self.assertEqual(res.codigo, auth.CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS)
        self.assertEqual(res.intentos_fallidos_acumulados, 1)
        self.assertIsNone(res.bloqueado_hasta_epoch)
        self.assertFalse(res.bloqueo_activo)

        estado_bloq = auth.consultar_estado_bloqueo_admin(reloj=self.reloj)
        self.assertFalse(estado_bloq.esta_bloqueado)
        self.assertEqual(estado_bloq.intentos_fallidos_consecutivos, 1)
        self.assertEqual(estado_bloq.intentos_restantes_antes_bloqueo, 4)

    def test_02_cuatro_intentos_fallidos_sin_bloqueo(self) -> None:
        """Caso 2 (CA-052): Cuatro intentos fallidos consecutivos aún no aplican bloqueo."""
        res = self._fallar_intentos(4)
        self.assertFalse(res.autenticado)
        self.assertEqual(res.codigo, auth.CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS)
        self.assertEqual(res.intentos_fallidos_acumulados, 4)
        self.assertIsNone(res.bloqueado_hasta_epoch)

        estado_bloq = auth.consultar_estado_bloqueo_admin(reloj=self.reloj)
        self.assertFalse(estado_bloq.esta_bloqueado)
        self.assertEqual(estado_bloq.intentos_fallidos_consecutivos, 4)
        self.assertEqual(estado_bloq.intentos_restantes_antes_bloqueo, 1)
        self.assertEqual(estado_bloq.nivel_bloqueo_consecutivo, 0)

    def test_03_quinto_intento_y_primer_bloqueo_cinco_minutos(self) -> None:
        """Caso 3 (CA-052, CA-053): El quinto fallo consecutivo (con Argon2id real en el 5º intento) aplica bloqueo de 5 minutos (300 s)."""
        self._fallar_intentos(4)
        res = self._fallar_intentos(1, usar_argon2_real=True)
        self.assertFalse(res.autenticado)
        self.assertEqual(
            res.codigo, auth.CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE
        )
        self.assertTrue(res.bloqueo_activo)
        self.assertEqual(res.intentos_fallidos_acumulados, 5)
        self.assertEqual(res.nivel_bloqueo_consecutivo, 1)
        self.assertEqual(res.duracion_bloqueo_segundos, 5 * 60)
        self.assertAlmostEqual(res.bloqueado_hasta_epoch or 0.0, self.reloj() + 300.0)

        estado_bloq = auth.consultar_estado_bloqueo_admin(reloj=self.reloj)
        self.assertTrue(estado_bloq.esta_bloqueado)
        self.assertEqual(estado_bloq.duracion_bloqueo_minutos, 5)
        self.assertAlmostEqual(estado_bloq.segundos_restantes_bloqueo, 300.0)

    def test_04_segundo_bloqueo_diez_minutos(self) -> None:
        """Caso 4 (CA-053): Tras vencer el 1er bloqueo, otros 5 fallos aplican 2º bloqueo de 10 min (600 s)."""
        self._fallar_intentos(5)  # 1er bloqueo: 5 min
        self.reloj.avanzar(5 * 60 + 1)

        # Los primeros 4 intentos de la segunda serie no bloquean todavía
        res_4 = self._fallar_intentos(4)
        self.assertFalse(res_4.bloqueo_activo)
        self.assertEqual(res_4.intentos_fallidos_acumulados, 4)

        # El 5º intento de la segunda serie activa el 2º bloqueo de 10 minutos
        res_5 = self._fallar_intentos(1)
        self.assertTrue(res_5.bloqueo_activo)
        self.assertEqual(res_5.nivel_bloqueo_consecutivo, 2)
        self.assertEqual(res_5.duracion_bloqueo_segundos, 10 * 60)
        self.assertAlmostEqual(res_5.bloqueado_hasta_epoch or 0.0, self.reloj() + 600.0)

    def test_05_tercer_bloqueo_veinte_minutos(self) -> None:
        """Caso 5 (CA-053): Tercer ciclo consecutivo de 5 fallos aplica bloqueo de 20 minutos (1200 s)."""
        self._fallar_intentos(5)  # 1º: 5 min
        self.reloj.avanzar(5 * 60 + 1)
        self._fallar_intentos(5)  # 2º: 10 min
        self.reloj.avanzar(10 * 60 + 1)

        res_3 = self._fallar_intentos(5)  # 3º: 20 min
        self.assertTrue(res_3.bloqueo_activo)
        self.assertEqual(res_3.nivel_bloqueo_consecutivo, 3)
        self.assertEqual(res_3.duracion_bloqueo_segundos, 20 * 60)
        self.assertAlmostEqual(res_3.bloqueado_hasta_epoch or 0.0, self.reloj() + 1200.0)

    def test_06_cuarto_bloqueo_treinta_minutos(self) -> None:
        """Caso 6 (CA-053): Cuarto ciclo consecutivo de 5 fallos aplica bloqueo de 30 minutos (1800 s)."""
        self._fallar_intentos(5)  # 1º: 5 min
        self.reloj.avanzar(5 * 60 + 1)
        self._fallar_intentos(5)  # 2º: 10 min
        self.reloj.avanzar(10 * 60 + 1)
        self._fallar_intentos(5)  # 3º: 20 min
        self.reloj.avanzar(20 * 60 + 1)

        res_4 = self._fallar_intentos(5)  # 4º: 30 min
        self.assertTrue(res_4.bloqueo_activo)
        self.assertEqual(res_4.nivel_bloqueo_consecutivo, 4)
        self.assertEqual(res_4.duracion_bloqueo_segundos, 30 * 60)
        self.assertAlmostEqual(res_4.bloqueado_hasta_epoch or 0.0, self.reloj() + 1800.0)

    def test_07_bloqueos_posteriores_sin_exceder_treinta_minutos(self) -> None:
        """Caso 7 (CA-053): Quinto y sexto bloqueos consecutivos se mantienen en el máximo de 30 minutos."""
        for minutos_esperados in (5, 10, 20, 30):
            res = self._fallar_intentos(5)
            self.assertEqual(res.duracion_bloqueo_segundos, minutos_esperados * 60)
            self.reloj.avanzar(minutos_esperados * 60 + 1)

        # 5º bloqueo consecutivo -> máximo 30 minutos (1800 s)
        res_5 = self._fallar_intentos(5)
        self.assertTrue(res_5.bloqueo_activo)
        self.assertEqual(res_5.nivel_bloqueo_consecutivo, 5)
        self.assertEqual(res_5.duracion_bloqueo_segundos, 30 * 60)
        self.reloj.avanzar(30 * 60 + 1)

        # 6º bloqueo consecutivo -> máximo 30 minutos (1800 s)
        res_6 = self._fallar_intentos(5)
        self.assertTrue(res_6.bloqueo_activo)
        self.assertEqual(res_6.nivel_bloqueo_consecutivo, 6)
        self.assertEqual(res_6.duracion_bloqueo_segundos, 30 * 60)

    def test_08_contrasena_correcta_durante_bloqueo_activo(self) -> None:
        """Caso 8 (Sección 4.4): Durante un bloqueo activo se rechaza incluso la contraseña correcta antes de Argon2id."""
        self._fallar_intentos(5)
        self.reloj.avanzar(60)  # Aún restan 4 minutos de bloqueo

        estado_sesion: dict[str, Any] = {}
        with patch(
            "autenticacion.verificar_contrasena_hash",
            side_effect=AssertionError("No debe ejecutarse Argon2id durante un bloqueo activo"),
        ):
            res = auth.iniciar_sesion_admin(
                self.usuario,
                self.clave,
                estado_sesion,
                fuente_entorno=self.entorno,
                reloj=self.reloj,
            )

        self.assertFalse(res.autenticado)
        self.assertEqual(
            res.codigo, auth.CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE
        )
        self.assertFalse(auth.esta_autenticado_en_sesion(estado_sesion, reloj=self.reloj))

    def test_09_finalizacion_del_bloqueo(self) -> None:
        """Caso 9 (Sección 4.2): Al cumplirse el tiempo del bloqueo en el servidor, se permite autenticarse (Argon2id real)."""
        self._fallar_intentos(5)
        self.reloj.avanzar(299.0)  # A 1 segundo de finalizar sigue bloqueado
        self.assertTrue(auth.consultar_estado_bloqueo_admin(reloj=self.reloj).esta_bloqueado)

        self.reloj.avanzar(1.0)  # Exactamente a los 300 segundos el bloqueo termina
        estado_bloq = auth.consultar_estado_bloqueo_admin(reloj=self.reloj)
        self.assertFalse(estado_bloq.esta_bloqueado)
        self.assertEqual(estado_bloq.intentos_fallidos_consecutivos, 0)
        # El nivel progresivo se conserva hasta que ocurra un login exitoso
        self.assertEqual(estado_bloq.nivel_bloqueo_consecutivo, 1)

        sesion: dict[str, Any] = {}
        res_ok = self._iniciar_sesion_controlada(sesion, usar_argon2_real=True)
        self.assertTrue(res_ok.autenticado)
        self.assertTrue(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))

    def test_10_reinicio_de_contadores_despues_de_login_exitoso(self) -> None:
        """Caso 10 (Sección 4.3): Un login exitoso reinicia tanto los intentos fallidos como el nivel progresivo."""
        # Alcanzar el 2º bloqueo (10 min) y dejarlo vencer
        self._fallar_intentos(5)
        self.reloj.avanzar(5 * 60 + 1)
        self._fallar_intentos(5)
        self.reloj.avanzar(10 * 60 + 1)
        self._fallar_intentos(3)

        # Iniciar sesión exitosamente
        sesion: dict[str, Any] = {}
        res_ok = self._iniciar_sesion_controlada(sesion)
        self.assertTrue(res_ok.autenticado)

        estado_bloq = auth.consultar_estado_bloqueo_admin(reloj=self.reloj)
        self.assertFalse(estado_bloq.esta_bloqueado)
        self.assertEqual(estado_bloq.intentos_fallidos_consecutivos, 0)
        self.assertEqual(estado_bloq.intentos_fallidos_totales, 0)
        self.assertEqual(estado_bloq.nivel_bloqueo_consecutivo, 0)

        # Si vuelve a fallar 5 veces después del login exitoso, el bloqueo empieza de nuevo en 5 minutos (nivel 1)
        auth.cerrar_sesion_admin(sesion, reloj=self.reloj)
        res_nuevo_bloq = self._fallar_intentos(5)
        self.assertEqual(res_nuevo_bloq.nivel_bloqueo_consecutivo, 1)
        self.assertEqual(res_nuevo_bloq.duracion_bloqueo_segundos, 5 * 60)

    def test_11_intentos_distribuidos_entre_dos_sesiones(self) -> None:
        """Caso 11 (Sección 5): Intentos fallidos repartidos entre dos sesiones acumulan bloqueo compartido."""
        sesion_a: dict[str, Any] = {}
        sesion_b: dict[str, Any] = {}
        sesion_nueva_pestana: dict[str, Any] = {}

        self._fallar_intentos(3, estado=sesion_a)
        self.assertEqual(
            auth.consultar_estado_bloqueo_admin(reloj=self.reloj).intentos_fallidos_consecutivos,
            3,
        )

        res_5 = self._fallar_intentos(2, estado=sesion_b)
        self.assertTrue(res_5.bloqueo_activo)
        self.assertEqual(res_5.duracion_bloqueo_segundos, 5 * 60)

        # Abrir una tercera pestaña/sesión no elude el bloqueo activo
        res_pestana = auth.iniciar_sesion_admin(
            self.usuario,
            self.clave,
            sesion_nueva_pestana,
            fuente_entorno=self.entorno,
            reloj=self.reloj,
        )
        self.assertFalse(res_pestana.autenticado)
        self.assertEqual(
            res_pestana.codigo,
            auth.CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE,
        )
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion_nueva_pestana, reloj=self.reloj))

    def test_12_proteccion_ante_intentos_concurrentes(self) -> None:
        """Caso 12 (Sección 5): Hilos concurrentes actualizan el contador bajo `_CANDADO_SEGURIDAD_SERVIDOR` sin carrera."""
        total_hilos = 6
        barrera_fallos = threading.Barrier(total_hilos)

        def tarea_fallo(_: int) -> auth.ResultadoAutenticacion:
            barrera_fallos.wait(timeout=5)
            return auth.verificar_credenciales_admin(
                self.usuario,
                "clave_incorrecta_concurrente",
                fuente_entorno=self.entorno,
                reloj=self.reloj,
            )

        with self._parche_verificacion_controlada(pausa_segundos=0.002):
            with ThreadPoolExecutor(max_workers=total_hilos) as ejecutor:
                res_concurrentes = list(ejecutor.map(tarea_fallo, range(total_hilos)))

        self.assertEqual(len(res_concurrentes), total_hilos)
        estado_bloq = auth.consultar_estado_bloqueo_admin(reloj=self.reloj)
        self.assertTrue(estado_bloq.esta_bloqueado)
        self.assertEqual(estado_bloq.nivel_bloqueo_consecutivo, 1)
        self.assertEqual(estado_bloq.intentos_fallidos_totales, 5)
        # Exactamente 4 intentos devolvieron CREDENCIALES_INVALIDAS y 2 vieron CUENTA_BLOQUEADA_TEMPORALMENTE
        codigos = [r.codigo for r in res_concurrentes]
        self.assertEqual(
            codigos.count(auth.CodigoResultadoAutenticacion.CREDENCIALES_INVALIDAS), 4
        )
        self.assertEqual(
            codigos.count(auth.CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE),
            2,
        )

    def test_13_ausencia_de_emision_de_comprobantes_durante_bloqueo(self) -> None:
        """Caso 13 (Sección 4.4): Durante un bloqueo activo no se emite ningún comprobante de verificación."""
        self._fallar_intentos(5)
        self.assertEqual(len(auth._COMPROBANTES_VERIFICACION_SERVIDOR), 0)

        res = auth.verificar_credenciales_admin(
            self.usuario,
            self.clave,
            fuente_entorno=self.entorno,
            reloj=self.reloj,
        )
        self.assertFalse(res.autenticado)
        self.assertIsNone(res.comprobante_verificacion)
        self.assertEqual(len(auth._COMPROBANTES_VERIFICACION_SERVIDOR), 0)

    # =========================================================================
    # 12.2. Pruebas de sesión (Casos 14 a 24)
    # =========================================================================

    def test_14_sesion_recien_autenticada(self) -> None:
        """Caso 14 (Sección 6): Una sesión recién autenticada (Argon2id real) es válida y dispone de 15 minutos (900 s)."""
        sesion: dict[str, Any] = {}
        res = self._iniciar_sesion_controlada(sesion, usar_argon2_real=True)
        self.assertTrue(res.autenticado)
        self.assertTrue(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))

        estado_t = auth.consultar_estado_sesion_admin(sesion, reloj=self.reloj)
        self.assertTrue(estado_t.autenticado)
        self.assertFalse(estado_t.expirada)
        self.assertFalse(estado_t.en_ventana_advertencia)
        self.assertAlmostEqual(estado_t.inactividad_segundos, 0.0)
        self.assertAlmostEqual(estado_t.segundos_restantes, 900.0)

    def test_15_actividad_administrativa_legitima(self) -> None:
        """Caso 15 (Sección 6.2): La actividad administrativa explícita actualiza la marca en el servidor."""
        sesion: dict[str, Any] = {}
        t_inicio = self.reloj()
        self._iniciar_sesion_controlada(sesion)
        self.reloj.avanzar(10 * 60)  # Minuto 10

        sesion_act = auth.registrar_actividad_administrativa(sesion, reloj=self.reloj)
        self.assertAlmostEqual(sesion_act.ultima_actividad_epoch, t_inicio + 600.0)

        # Avanzar otros 10 minutos (20 min desde el login, pero solo 10 min desde la última actividad)
        self.reloj.avanzar(10 * 60)
        self.assertTrue(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))
        estado_t = auth.consultar_estado_sesion_admin(sesion, reloj=self.reloj)
        self.assertAlmostEqual(estado_t.segundos_restantes, 300.0)

    def test_16_inactividad_inferior_a_quince_minutos(self) -> None:
        """Caso 16 (Sección 6.1): Antes de los 13 minutos la sesión sigue activa y sin advertencia."""
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        self.reloj.avanzar(12 * 60 + 59)  # 779 segundos

        estado_t = auth.consultar_estado_sesion_admin(sesion, reloj=self.reloj)
        self.assertTrue(estado_t.autenticado)
        self.assertFalse(estado_t.expirada)
        self.assertFalse(estado_t.en_ventana_advertencia)
        self.assertEqual(estado_t.mensaje_advertencia, "")
        self.assertAlmostEqual(estado_t.segundos_restantes, 121.0)

    def test_17_advertencia_al_minuto_trece(self) -> None:
        """Caso 17 (Sección 7, CA-054): Al minuto 13 (780 s) se activa la advertencia previa (restan 2 min)."""
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        self.reloj.avanzar(13 * 60)  # Exactamente minuto 13 (780 s)

        estado_t = auth.consultar_estado_sesion_admin(sesion, reloj=self.reloj)
        self.assertTrue(estado_t.autenticado)
        self.assertFalse(estado_t.expirada)
        self.assertTrue(estado_t.en_ventana_advertencia)
        self.assertAlmostEqual(estado_t.segundos_restantes, 120.0)
        self.assertIn("próxima a expirar", estado_t.mensaje_advertencia)
        self.assertIn(auth.TEXTO_BOTON_CONTINUAR_SESION, estado_t.mensaje_advertencia)

    def test_18_expiracion_al_minuto_quince(self) -> None:
        """Caso 18 (Sección 6.1, CA-055): Al minuto 15 (900 s) de inactividad la sesión expira."""
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        self.reloj.avanzar(15 * 60)  # 900 segundos

        estado_t = auth.consultar_estado_sesion_admin(sesion, reloj=self.reloj)
        self.assertFalse(estado_t.autenticado)
        self.assertTrue(estado_t.expirada)
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))
        self.assertIsNone(sesion[auth.CLAVE_SESION_ADMIN])

    def test_19_revocacion_real_del_token_expirado(self) -> None:
        """Caso 19 (Sección 6.3): Al expirar, el token queda revocado en el servidor y no puede reinyectarse."""
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        copia_estado_sesion: auth.EstadoSesionAdmin = sesion[auth.CLAVE_SESION_ADMIN]
        token_original = copia_estado_sesion.token_sesion
        self.assertIn(token_original, auth._SESIONES_ACTIVAS_SERVIDOR)

        self.reloj.avanzar(15 * 60 + 1)
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))
        self.assertNotIn(token_original, auth._SESIONES_ACTIVAS_SERVIDOR)
        self.assertIn(token_original, auth._TOKENS_REVOCADOS_SERVIDOR)

        # Intentar reinyectar el objeto de sesión antiguo en `session_state` es rechazado
        sesion[auth.CLAVE_SESION_ADMIN] = copia_estado_sesion
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))

    def test_20_rechazo_de_operaciones_despues_de_expirar(self) -> None:
        """Caso 20 (Sección 6.3, CA-055): Toda operación protegida es rechazada tras expirar la sesión."""
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        self.reloj.avanzar(15 * 60)

        with self.assertRaises(auth.ErrorAutorizacionAdmin) as ctx:
            auth.requerir_autorizacion_admin(sesion, reloj=self.reloj)
        self.assertEqual(
            ctx.exception.codigo, auth.CodigoResultadoAutenticacion.SESION_EXPIRADA
        )

        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.guardar_borrador_admin(
                sesion, {"nombre": "Producto no autorizado"}, reloj=self.reloj
            )

    def test_21_renovacion_antes_de_la_expiracion(self) -> None:
        """Caso 21 (Sección 8, CA-056): «Continuar sesión» antes de expirar renueva por 15 minutos."""
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        # Avanzar al minuto 14 (en plena ventana de advertencia)
        self.reloj.avanzar(14 * 60)
        self.assertTrue(
            auth.consultar_estado_sesion_admin(sesion, reloj=self.reloj).en_ventana_advertencia
        )

        # Renovar sesión («Continuar sesión»)
        sesion_renovada = auth.renovar_sesion_admin(sesion, reloj=self.reloj)
        self.assertAlmostEqual(sesion_renovada.ultima_actividad_epoch, self.reloj())

        estado_post = auth.consultar_estado_sesion_admin(sesion, reloj=self.reloj)
        self.assertTrue(estado_post.autenticado)
        self.assertFalse(estado_post.en_ventana_advertencia)
        self.assertAlmostEqual(estado_post.segundos_restantes, 900.0)

        # Avanzar 14 minutos adicionales (28 min desde el login original): sigue activa gracias a la renovación
        self.reloj.avanzar(14 * 60)
        self.assertTrue(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))

    def test_22_rechazo_de_renovacion_despues_de_expirar(self) -> None:
        """Caso 22 (Sección 8): Una sesión ya expirada no puede renovarse con «Continuar sesión»."""
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        self.reloj.avanzar(15 * 60)

        with self.assertRaises(auth.ErrorAutorizacionAdmin) as ctx:
            auth.renovar_sesion_admin(sesion, reloj=self.reloj)
        self.assertEqual(
            ctx.exception.codigo, auth.CodigoResultadoAutenticacion.SESION_EXPIRADA
        )
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))

    def test_23_separacion_entre_sesiones_independientes(self) -> None:
        """Caso 23 (Sección 8): La expiración de una sesión no invalida otra sesión activa y renovada."""
        sesion_a: dict[str, Any] = {}
        sesion_b: dict[str, Any] = {}

        self._iniciar_sesion_controlada(sesion_a)
        self._iniciar_sesion_controlada(sesion_b)

        # En el minuto 10, solo la sesión B realiza actividad / renueva
        self.reloj.avanzar(10 * 60)
        auth.renovar_sesion_admin(sesion_b, reloj=self.reloj)

        # En el minuto 16 desde el inicio: la sesión A expira (16 min inactiva), la sesión B sigue activa (6 min inactiva)
        self.reloj.avanzar(6 * 60)
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion_a, reloj=self.reloj))
        self.assertTrue(auth.esta_autenticado_en_sesion(sesion_b, reloj=self.reloj))

    def test_24_comportamiento_ante_rerenderizados_pasivos(self) -> None:
        """Caso 24 (Sección 6.2): Las comprobaciones pasivas de estado o interfaz no renuevan la actividad."""
        sesion: dict[str, Any] = {}
        t0 = self.reloj()
        self._iniciar_sesion_controlada(sesion)

        # Simular re-renderizados pasivos cada minuto durante 14 minutos
        for minuto in range(1, 15):
            self.reloj.fijar(t0 + minuto * 60)
            self.assertTrue(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))
            _ = auth.requerir_autorizacion_admin(sesion, reloj=self.reloj)
            estado_t = auth.consultar_estado_sesion_admin(sesion, reloj=self.reloj)
            self.assertAlmostEqual(estado_t.ultima_actividad_epoch or 0.0, t0)

        # Al minuto 15 exacto, pese a las 14 consultas pasivas previas, la sesión expira puntualmente
        self.reloj.fijar(t0 + 15 * 60)
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))

    # =========================================================================
    # 12.3. Pruebas de borradores (Casos 25 a 32)
    # =========================================================================

    def test_25_guardar_un_borrador_temporal(self) -> None:
        """Caso 25 (Sección 9.2): Permite guardar un borrador sintético y prohíbe guardar secretos."""
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        datos_sinteticos = {
            "codigo_producto": "TAL009",
            "nombre": "Taladro percutor 1/2 pulgada",
            "categoria_id": "CAT01",
            "ubicaciones": ["U001", "U002"],
            "ubicacion_principal": "U001",
        }
        borrador = auth.guardar_borrador_admin(
            sesion,
            datos_sinteticos,
            tipo_operacion="creacion_producto",
            reloj=self.reloj,
        )
        self.assertEqual(borrador.datos, datos_sinteticos)
        self.assertEqual(borrador.usuario, self.usuario)
        self.assertFalse(borrador.confirmado_en_github)
        self.assertTrue(borrador.es_borrador_temporal)
        self.assertTrue(auth.tiene_borrador_pendiente_en_sesion(sesion, reloj=self.reloj))

        # Intentar guardar contraseñas, hashes o tokens dentro de un borrador es rechazado
        for borrador_inseguro in (
            {"nombre": "Taladro", "password": "mi_clave_secreta"},
            {"nombre": "Taladro", "hash_contrasena": self.hash_valido},
            {"nombre": "Taladro", "nota": f"Usar hash {self.hash_valido}"},
            {"nombre": "Taladro", "token": sesion[auth.CLAVE_SESION_ADMIN].token_sesion},
        ):
            with self.assertRaises(auth.ErrorSeguridadBorradorAdmin):
                auth.guardar_borrador_admin(sesion, borrador_inseguro, reloj=self.reloj)

    def test_26_retener_borrador_despues_de_expirar_sesion(self) -> None:
        """Caso 26 (Sección 9.2, CA-057): Al expirar la sesión, el borrador se retiene sin mantener permisos."""
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        datos_borrador = {"codigo_producto": "ESM001", "nombre": "Esmeril angular 4.5"}
        t_guardado = self.reloj()
        auth.guardar_borrador_admin(sesion, datos_borrador, reloj=self.reloj)

        # Avanzar 15 minutos -> la sesión expira
        self.reloj.avanzar(15 * 60)
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))

        # La sesión ya NO tiene autorización administrativa, pero el borrador continúa retenido
        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.requerir_autorizacion_admin(sesion, reloj=self.reloj)
        self.assertTrue(auth.tiene_borrador_pendiente_en_sesion(sesion, reloj=self.reloj))

        # Verificar que la ventana de retención es de 15 minutos adicionales tras expirar la sesión
        vinculo = sesion[auth.CLAVE_VINCULO_BORRADOR_SESION]
        reg_servidor = auth._BORRADORES_TEMPORALES_SERVIDOR[vinculo.id_borrador]
        self.assertTrue(reg_servidor.retenido_por_expiracion)
        self.assertIsNone(reg_servidor.token_sesion_activa)
        self.assertAlmostEqual(
            reg_servidor.expira_retencion_epoch or 0.0,
            t_guardado + 15 * 60 + 15 * 60,
        )

    def test_27_reautenticarse_y_restaurar_borrador_durante_ventana_permitida(self) -> None:
        """Caso 27 (Sección 9.2, CA-057): Tras reautenticarse dentro de los 15 min adicionales, el borrador se restaura."""
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        datos_originales = {
            "codigo_producto": "SIE004",
            "nombre": "Sierra circular 7 1/4",
            "categoria_id": "CAT01",
        }
        auth.guardar_borrador_admin(sesion, datos_originales, reloj=self.reloj)

        # Expira la sesión a los 15 minutos
        self.reloj.avanzar(15 * 60)
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))

        # Transcurren 10 minutos adicionales (dentro de los 15 min de retención) y se reautentica
        self.reloj.avanzar(10 * 60)
        res_relogin = self._iniciar_sesion_controlada(sesion)
        self.assertTrue(res_relogin.autenticado)

        borrador_consultado = auth.obtener_borrador_admin(sesion, reloj=self.reloj)
        self.assertIsNotNone(borrador_consultado)
        assert borrador_consultado is not None
        self.assertEqual(borrador_consultado.datos, datos_originales)

        borrador_restaurado = auth.restaurar_borrador_admin(sesion, reloj=self.reloj)
        self.assertIsNotNone(borrador_restaurado)
        assert borrador_restaurado is not None
        self.assertEqual(borrador_restaurado.datos, datos_originales)
        self.assertFalse(borrador_restaurado.confirmado_en_github)

    def test_28_rechazar_recuperacion_sin_autenticacion(self) -> None:
        """Caso 28 (Sección 9.3): No se puede consultar ni restaurar un borrador sin sesión autenticada."""
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        auth.guardar_borrador_admin(
            sesion, {"codigo_producto": "LLA002", "nombre": "Llave ajustable"}, reloj=self.reloj
        )

        # Expirar sesión
        self.reloj.avanzar(15 * 60 + 1)
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))

        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.obtener_borrador_admin(sesion, reloj=self.reloj)

        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.restaurar_borrador_admin(sesion, reloj=self.reloj)

    def test_29_rechazar_recuperacion_desde_cuenta_o_contexto_no_autorizado(self) -> None:
        """Caso 29 (Sección 9.3): Rechaza recuperar un borrador desde otra cuenta, móvil o sesión bloqueada."""
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        borr = auth.guardar_borrador_admin(
            sesion, {"codigo_producto": "PIN001", "nombre": "Pinza universal"}, reloj=self.reloj
        )

        # 1. Contexto móvil es rechazado
        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.obtener_borrador_admin(
                sesion,
                contexto_dispositivo=auth.ContextoDispositivo.MOVIL,
                reloj=self.reloj,
            )

        # 2. Durante un bloqueo activo (p. ej. provocado desde otra pestaña), se rechaza recuperar borradores
        self._fallar_intentos(5)
        with self.assertRaises(auth.ErrorAutorizacionAdmin) as ctx_bloq:
            auth.obtener_borrador_admin(sesion, reloj=self.reloj)
        self.assertEqual(
            ctx_bloq.exception.codigo,
            auth.CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE,
        )

        # 3. Expirar bloqueo y sesión, e intentar recuperar con otra cuenta administrativa configurada
        self.reloj.avanzar(16 * 60)
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))

        # Reinyectar el vínculo antes de autenticar con otra cuenta distinta
        vinculo_original = auth._VinculoBorradorSesion(
            id_borrador=borr.id_borrador,
            usuario=self.usuario,
            huella_configuracion="huella_antigua",
            creado_en_epoch=borr.creado_en_epoch,
            firma_hmac="firma_invalida",
        )
        entorno_otro_admin = {
            "FERRETERIAMS_ADMIN_USER": "otro_admin_diferente",
            "FERRETERIAMS_ADMIN_PASSWORD_HASH": self.hash_valido,
        }
        self._iniciar_sesion_controlada(
            sesion,
            usuario="otro_admin_diferente",
            fuente_entorno=entorno_otro_admin,
        )
        sesion[auth.CLAVE_VINCULO_BORRADOR_SESION] = vinculo_original
        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.obtener_borrador_admin(sesion, reloj=self.reloj)

    def test_30_expirar_y_eliminar_borradores_despues_de_quince_minutos_adicionales(self) -> None:
        """Caso 30 (Sección 9.2, CA-057): Pasados 15 min adicionales tras expirar la sesión, el borrador se elimina."""
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        borr = auth.guardar_borrador_admin(
            sesion, {"codigo_producto": "CIN005", "nombre": "Cinta métrica 5m"}, reloj=self.reloj
        )

        # Minuto 15: expira la sesión
        self.reloj.avanzar(15 * 60)
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))
        self.assertTrue(auth.tiene_borrador_pendiente_en_sesion(sesion, reloj=self.reloj))

        # Minuto 29 y 59 s (14m 59s después de expirar): el borrador aún está disponible
        self.reloj.avanzar(14 * 60 + 59)
        self.assertTrue(auth.tiene_borrador_pendiente_en_sesion(sesion, reloj=self.reloj))

        # 1 segundo después (exactamente 15 minutos adicionales tras expirar la sesión): el borrador caduca y se elimina
        self.reloj.avanzar(1.0)
        self.assertFalse(auth.tiene_borrador_pendiente_en_sesion(sesion, reloj=self.reloj))
        self.assertNotIn(borr.id_borrador, auth._BORRADORES_TEMPORALES_SERVIDOR)

        # Aunque el administrador se reautentique después, el borrador vencido ya no existe
        self._iniciar_sesion_controlada(sesion)
        self.assertIsNone(auth.obtener_borrador_admin(sesion, reloj=self.reloj))
        self.assertIsNone(auth.restaurar_borrador_admin(sesion, reloj=self.reloj))

    def test_31_manejo_de_logout_voluntario(self) -> None:
        """Caso 31 (Sección 9.3): El Logout voluntario elimina inmediatamente el borrador temporal."""
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        borr = auth.guardar_borrador_admin(
            sesion, {"codigo_producto": "DES001", "nombre": "Destornillador"}, reloj=self.reloj
        )
        self.assertIn(borr.id_borrador, auth._BORRADORES_TEMPORALES_SERVIDOR)

        # Ejecutar Logout voluntario
        auth.cerrar_sesion_admin(sesion, reloj=self.reloj)
        self.assertNotIn(borr.id_borrador, auth._BORRADORES_TEMPORALES_SERVIDOR)
        self.assertFalse(auth.tiene_borrador_pendiente_en_sesion(sesion, reloj=self.reloj))
        self.assertIsNone(sesion.get(auth.CLAVE_VINCULO_BORRADOR_SESION))

        # Si vuelve a iniciar sesión tras un Logout voluntario, no hay borrador residual
        self._iniciar_sesion_controlada(sesion)
        self.assertIsNone(auth.obtener_borrador_admin(sesion, reloj=self.reloj))

    def test_32_aislamiento_de_borradores_entre_sesiones(self) -> None:
        """Caso 32 (Sección 9.2): Dos sesiones independientes no pueden leer ni pisar el borrador de la otra."""
        sesion_a: dict[str, Any] = {}
        sesion_b: dict[str, Any] = {}

        self._iniciar_sesion_controlada(sesion_a)
        self._iniciar_sesion_controlada(sesion_b)

        borr_a = auth.guardar_borrador_admin(
            sesion_a, {"codigo_producto": "PROD_A", "nombre": "Producto Sesión A"}, reloj=self.reloj
        )

        # La sesión B no ve el borrador de la sesión A
        self.assertIsNone(auth.obtener_borrador_admin(sesion_b, reloj=self.reloj))

        # Si la sesión B intenta pedir explícitamente el `id_borrador` de la sesión A, se rechaza
        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.obtener_borrador_admin(
                sesion_b, id_borrador=borr_a.id_borrador, reloj=self.reloj
            )

        # Si la sesión B guarda su propio borrador, ambos coexisten aislados
        borr_b = auth.guardar_borrador_admin(
            sesion_b, {"codigo_producto": "PROD_B", "nombre": "Producto Sesión B"}, reloj=self.reloj
        )
        self.assertNotEqual(borr_a.id_borrador, borr_b.id_borrador)
        self.assertEqual(
            auth.obtener_borrador_admin(sesion_a, reloj=self.reloj).datos["codigo_producto"],  # type: ignore[union-attr]
            "PROD_A",
        )
        self.assertEqual(
            auth.obtener_borrador_admin(sesion_b, reloj=self.reloj).datos["codigo_producto"],  # type: ignore[union-attr]
            "PROD_B",
        )

    # =========================================================================
    # 12.4. Pruebas de integración y robustez (Casos 33 a 40)
    # =========================================================================

    def test_33_limpieza_de_registros_expirados_y_limites_de_memoria(self) -> None:
        """Caso 33 (Sección 10): Depura registros vencidos sin borrar bloqueos activos ni el nivel progresivo."""
        # 1. Crear una sesión y un borrador, y emitir un comprobante sin canjear
        sesion: dict[str, Any] = {}
        self._iniciar_sesion_controlada(sesion)
        auth.guardar_borrador_admin(
            sesion, {"codigo_producto": "LIM001", "nombre": "Producto limpieza"}, reloj=self.reloj
        )
        with self._parche_verificacion_controlada():
            _ = auth.verificar_credenciales_admin(
                self.usuario,
                self.clave,
                fuente_entorno=self.entorno,
                reloj=self.reloj,
            )
        self.assertEqual(len(auth._COMPROBANTES_VERIFICACION_SERVIDOR), 1)
        self.assertEqual(len(auth._SESIONES_ACTIVAS_SERVIDOR), 1)
        self.assertEqual(len(auth._BORRADORES_TEMPORALES_SERVIDOR), 1)

        # 2. Provocar un bloqueo activo de 5 minutos
        self._fallar_intentos(5)
        self.assertTrue(auth.consultar_estado_bloqueo_admin(reloj=self.reloj).esta_bloqueado)

        # 3. Avanzar 2 minutos: el comprobante (TTL 60 s) caduca, pero el bloqueo (5 min) y la sesión siguen activos
        self.reloj.avanzar(2 * 60)
        resumen_1 = auth.depurar_registros_seguridad_servidor(reloj=self.reloj)
        self.assertEqual(resumen_1.comprobantes_eliminados, 1)
        self.assertEqual(resumen_1.sesiones_expiradas_revocadas, 0)
        self.assertFalse(resumen_1.bloqueo_finalizado_liberado)
        # El bloqueo activo NO fue eliminado por la limpieza
        self.assertTrue(auth.consultar_estado_bloqueo_admin(reloj=self.reloj).esta_bloqueado)

        # 4. Avanzar otros 14 minutos (total 16 min): la sesión expira y el bloqueo termina, conservando nivel 1 y borrador retenido
        self.reloj.avanzar(14 * 60)
        resumen_2 = auth.depurar_registros_seguridad_servidor(reloj=self.reloj)
        self.assertEqual(resumen_2.sesiones_expiradas_revocadas, 1)
        self.assertTrue(resumen_2.bloqueo_finalizado_liberado)
        estado_bloq = auth.consultar_estado_bloqueo_admin(reloj=self.reloj)
        self.assertFalse(estado_bloq.esta_bloqueado)
        self.assertEqual(estado_bloq.nivel_bloqueo_consecutivo, 1)
        self.assertEqual(len(auth._BORRADORES_TEMPORALES_SERVIDOR), 1)

        # 5. Avanzar 15 minutos adicionales: el borrador retenido caduca y se elimina
        self.reloj.avanzar(15 * 60)
        resumen_3 = auth.depurar_registros_seguridad_servidor(reloj=self.reloj)
        self.assertEqual(resumen_3.borradores_vencidos_eliminados, 1)
        self.assertEqual(len(auth._BORRADORES_TEMPORALES_SERVIDOR), 0)

    def test_34_comprobantes_de_un_solo_uso_del_prompt_07(self) -> None:
        """Caso 34 (Sección 2): Los comprobantes criptográficos siguen siendo obligatorios y de un solo uso (Argon2id real)."""
        res = auth.verificar_credenciales_admin(
            self.usuario,
            self.clave,
            fuente_entorno=self.entorno,
            reloj=self.reloj,
        )
        self.assertTrue(res.autenticado)
        self.assertIsNotNone(res.comprobante_verificacion)

        s1: dict[str, Any] = {}
        s2: dict[str, Any] = {}
        auth.registrar_autenticacion_en_sesion(s1, res, reloj=self.reloj)
        self.assertTrue(auth.esta_autenticado_en_sesion(s1, reloj=self.reloj))

        with self.assertRaises(auth.ErrorAutorizacionAdmin):
            auth.registrar_autenticacion_en_sesion(s2, res, reloj=self.reloj)
        self.assertFalse(auth.esta_autenticado_en_sesion(s2, reloj=self.reloj))

    def test_35_uso_de_argon2id_sin_degradacion(self) -> None:
        """Caso 35 (Sección 2, CA-059): El hashing sigue utilizando exclusivamente Argon2id con parámetros intactos."""
        self.assertEqual(auth.ALGORITMO_HASH_CONTRASENA, "argon2id")
        self.assertTrue(self.hash_valido.startswith("$argon2id$v=19$"))
        self.assertTrue(auth.es_hash_contrasena_valido(self.hash_valido))
        self.assertFalse(auth.es_hash_contrasena_valido("texto_plano_inseguro"))
        self.assertTrue(auth.verificar_contrasena_hash(self.clave, self.hash_valido))
        self.assertFalse(auth.verificar_contrasena_hash("clave_incorrecta_p08", self.hash_valido))

    def test_36_rechazo_de_marcadores_de_sesion_y_tiempos_falsificados(self) -> None:
        """Caso 36 (Secciones 6.1 y 12): Manipular `ultima_actividad_epoch` o claves en cliente revoca la sesión."""
        sesion: dict[str, Any] = {"admin": True, "is_admin": True}
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))

        self._iniciar_sesion_controlada(sesion)
        estado_legitimo: auth.EstadoSesionAdmin = sesion[auth.CLAVE_SESION_ADMIN]

        # Intentar prolongar la sesión modificando `ultima_actividad_epoch` desde el cliente
        self.reloj.avanzar(14 * 60)
        estado_alterado = auth.EstadoSesionAdmin(
            autenticado=True,
            usuario=estado_legitimo.usuario,
            token_sesion=estado_legitimo.token_sesion,
            firma_hmac=estado_legitimo.firma_hmac,
            autenticado_en_epoch=estado_legitimo.autenticado_en_epoch,
            ultima_actividad_epoch=self.reloj() + 3600.0,
            contexto_dispositivo=estado_legitimo.contexto_dispositivo,
        )
        sesion[auth.CLAVE_SESION_ADMIN] = estado_alterado

        # El servidor detecta la discrepancia frente a `_SESIONES_ACTIVAS_SERVIDOR` y revoca la sesión
        self.assertFalse(auth.esta_autenticado_en_sesion(sesion, reloj=self.reloj))
        self.assertIsNone(sesion[auth.CLAVE_SESION_ADMIN])

    def test_37_aplicacion_publica_disponible_durante_bloqueo_administrativo(self) -> None:
        """Caso 37 (Sección 6.3, CA-007): El buscador público funciona normalmente durante un bloqueo administrativo."""
        self._fallar_intentos(5)
        self.assertTrue(auth.consultar_estado_bloqueo_admin(reloj=self.reloj).esta_bloqueado)

        lectura_simulada = gh.ResultadoLecturaInventarioRemoto(
            propietario="JunyMSAI",
            repositorio="FerreteriaMS",
            rama="main",
            ruta_archivo="03_Aplicacion/inventario.xlsx",
            sha_github="sha_p08_simulado",
            sha256_local="hash_local_p08",
            tamano_bytes=1024,
            inventario=_construir_inventario_simulado_p08(),
        )
        with patch.dict(os.environ, self.entorno, clear=False):
            with patch(
                "github_inventario.descargar_inventario_remoto",
                return_value=lectura_simulada,
            ):
                at = AppTest.from_file(str(RUTA_APP_PY))
                at.run(timeout=15)
                self.assertFalse(at.exception)

                at.text_input(key="campo_nombre_producto").input("martillo")
                at.button(key="btn_ejecutar_busqueda").click()
                at.run(timeout=15)

                self.assertFalse(at.exception)
                self.assertEqual(len(at.success), 1)
                self.assertIn("Mostrando 1–1 de 1", at.success[0].value)

    def test_38_no_implementacion_de_crud_o_escritura_remota(self) -> None:
        """Caso 38 (Secciones 1 y 15): No existen formularios CRUD ni llamadas HTTP de escritura ni `inventario.xlsx`."""
        self.assertFalse(
            RUTA_MAESTRO_DEFINITIVO.exists(),
            "No debe existir ni crearse 03_Aplicacion/inventario.xlsx en el Prompt 08.",
        )
        for ruta in (RUTA_APP_PY, RUTA_AUTENTICACION_PY):
            codigo = ruta.read_text(encoding="utf-8")
            for metodo in ('"PUT"', '"POST"', '"DELETE"', '"PATCH"', "'PUT'", "'POST'", "'DELETE'", "'PATCH'"):
                self.assertNotIn(metodo, codigo)

    def test_39_gemini_visual_no_operativo(self) -> None:
        """Caso 39 (Sección 11, RF-032..RF-034): Gemini permanece como «Próximamente» sin llamadas a IA."""
        for ruta in (RUTA_APP_PY, RUTA_AUTENTICACION_PY):
            contenido = ruta.read_text(encoding="utf-8")
            arbol = ast.parse(contenido)
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

    def test_40_compatibilidad_e_integracion_ui_sesiones_advertencia_y_borradores(self) -> None:
        """Caso 40 (Secciones 11, 12 y 13): Flujo UI en `AppTest` de bloqueo, aviso al min 13, renovación, expiración y borrador."""
        with patch.dict(os.environ, self.entorno, clear=False):
            at = AppTest.from_file(str(RUTA_APP_PY))
            at.run(timeout=15)

            # 1. Ir a Productos y provocar 5 intentos fallidos desde la interfaz (con mock controlado en los 5 fallos)
            at.button(key="btn_nav_productos").click()
            at.run(timeout=15)

            with self._parche_verificacion_controlada():
                for _ in range(5):
                    at.text_input(key="campo_admin_usuario").input(self.usuario)
                    at.text_input(key="campo_admin_contrasena").input("clave_erronea_ui")
                    at.button(key="btn_admin_iniciar_sesion").click()
                    at.run(timeout=15)

            errores_bloq = [e.value for e in at.error]
            self.assertTrue(
                any("bloqueado temporalmente" in e.lower() for e in errores_bloq),
                f"Debe mostrarse el mensaje de bloqueo en UI: {errores_bloq}",
            )

            # 2. Avanzar el reloj simulado 5 minutos + 1 segundo e iniciar sesión válidamente con Argon2id real
            self.reloj.avanzar(5 * 60 + 1)
            at.text_input(key="campo_admin_usuario").input(self.usuario)
            at.text_input(key="campo_admin_contrasena").input(self.clave)
            at.button(key="btn_admin_iniciar_sesion").click()
            at.run(timeout=15)

            self.assertTrue(auth.esta_autenticado_en_sesion(at.session_state, reloj=self.reloj))
            boton_continuar = at.button(key="btn_admin_continuar_sesion")
            self.assertEqual(boton_continuar.label, "Continuar sesión")

            # 3. Registrar un borrador temporal en la sesión y avanzar al minuto 13 para verificar el aviso en UI
            auth.guardar_borrador_admin(
                at.session_state,
                {"codigo_producto": "BRO001", "nombre": "Broca para concreto 3/8"},
                reloj=self.reloj,
            )
            self.reloj.avanzar(13 * 60 + 10)
            at.run(timeout=15)

            advertencias = [w.value for w in at.warning]
            self.assertTrue(
                any("próxima a expirar" in w.lower() for w in advertencias),
                f"Debe mostrarse el aviso previo de expiración al minuto 13: {advertencias}",
            )

            # 4. Pulsar el botón «Continuar sesión» y comprobar que la sesión se renueva y desaparece la advertencia
            at.button(key="btn_admin_continuar_sesion").click()
            at.run(timeout=15)
            self.assertEqual(len(at.warning), 0)
            exitos = [s.value for s in at.success]
            self.assertTrue(any("renovada" in s.lower() for s in exitos))

            # 5. Avanzar 15 minutos sin actividad -> redirige automáticamente a Login y avisa del borrador retenido
            self.reloj.avanzar(15 * 60 + 1)
            at.run(timeout=15)
            self.assertFalse(auth.esta_autenticado_en_sesion(at.session_state, reloj=self.reloj))
            self.assertIsNotNone(at.text_input(key="campo_admin_usuario"))
            advertencias_exp = [w.value for w in at.warning]
            self.assertTrue(any("expirado tras 15 minutos" in w.lower() for w in advertencias_exp))
            infos_exp = [i.value for i in at.info]
            self.assertTrue(any("borrador" in i.lower() for i in infos_exp))

            # 6. Reautenticarse dentro de los 15 min adicionales y restaurar el borrador desde el botón de la interfaz
            self.reloj.avanzar(5 * 60)
            with self._parche_verificacion_controlada():
                at.text_input(key="campo_admin_usuario").input(self.usuario)
                at.text_input(key="campo_admin_contrasena").input(self.clave)
                at.button(key="btn_admin_iniciar_sesion").click()
                at.run(timeout=15)

            at.button(key="btn_admin_restaurar_borrador").click()
            at.run(timeout=15)
            borrador_rest = at.session_state[auth.CLAVE_BORRADOR_RESTAURADO_ADMIN]
            self.assertIsNotNone(borrador_rest)
            self.assertEqual(borrador_rest.datos["codigo_producto"], "BRO001")


if __name__ == "__main__":
    unittest.main()
