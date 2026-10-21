# Informe de Resultados — FERMS-V0-P08: Gestión avanzada de sesiones, bloqueos y borradores

**Proyecto:** FerreteríaMS v0  
**TASK_ID:** `FERMS-V0-P08`  
**Título de la tarea:** Gestión avanzada de sesiones administrativas, bloqueos progresivos tras cinco intentos fallidos, expiración por inactividad, advertencia previa, renovación y conservación temporal de borradores  
**Nivel de tarea:** Seguridad administrativa avanzada (Etapa v0)  
**Fecha real de ejecución:** 2026-10-20  
**Hora real de ejecución (fase inicial antes del reinicio de Windows):** 20:10:50 -04:00 a 20:32:00 -04:00  
**Hora real de auditoría y reanudación controlada (Pasos 1 a 4):** 20:49:19 -04:00 a 21:15:13 -04:00  
**Hora real de corrección final de trazabilidad documental:** 21:21:19 -04:00 a 21:26:00 -04:00  
**Agente de desarrollo:** Antigravity (Gemini) dentro de VS Code  
**Repositorio:** `JunyMSAI/FerreteriaMS`  
**Rama:** `main`  
**Commit base (`HEAD`):** `c24b1a9` (`promt "08_Sesiones_Bloqueos_Borradores" incluido`)  
**Commit nuevo generado en esta tarea:** Ninguno (por instrucción expresa del usuario y de la Sección 15 del Prompt 08)

---

## 1. Trazabilidad Obligatoria (Sección 16 del Prompt 08 y Sección 3.10 de `AGENTS.md`)

### 1.1. Referencia al prompt oficial
- **Archivo del prompt:** `02_Prompts/08_Sesiones_Bloqueos_Borradores.md` (leído íntegramente y conservado sin alteraciones).

### 1.2. Solicitud original íntegra del usuario y reanudación controlada tras congelamiento
1. **Solicitud original (`FERMS-V0-P08`):**
   > Ejecuta la tarea **FERMS-V0-P08 — Gestión avanzada de sesiones, bloqueos y borradores** del proyecto FerreteríaMS v0.
   >
   > Lee íntegramente `02_Prompts/08_Sesiones_Bloqueos_Borradores.md` y cumple exclusivamente las instrucciones aprobadas.
   >
   > Antes de comenzar, consulta `GEMINI.md`, `AGENTS.md`, `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`, `01_Documentacion/02_Especificaciones_v0.md`, el Prompt 07 y su informe de resultados.
   >
   > Verifica el estado Git y el commit base. Si existen cambios inesperados pendientes, detente y solicita indicaciones.
   >
   > **Autorizo únicamente las modificaciones locales previstas en el Prompt 08.**
   >
   > Implementa los controles avanzados de autenticación administrativa:
   > - Cinco intentos fallidos consecutivos.
   > - Bloqueos progresivos de 5, 10, 20 y 30 minutos, con máximo de 30.
   > - Contadores compartidos entre sesiones del servidor, dentro de las garantías reales de la arquitectura utilizada.
   > - Expiración después de 15 minutos de inactividad.
   > - Advertencia dos minutos antes de expirar.
   > - Botón «Continuar sesión».
   > - Conservación temporal de borradores durante 15 minutos adicionales.
   > - Revocación de sesiones expiradas y limpieza de registros temporales.
   >
   > Preserva el funcionamiento y las correcciones de seguridad del Prompt 07: **Argon2id, comprobantes de verificación de un solo uso, firmas HMAC, autorización en Python y Logout**.
   >
   > Utiliza pruebas con tiempo simulado para verificar temporizaciones, bloqueo, renovación y recuperación de borradores. Realiza también las verificaciones de Streamlit y navegador que permitan las herramientas disponibles.
   >
   > **No declares como probado un aviso automático en navegador si únicamente se evaluó mediante tiempo simulado o ejecución de pruebas unitarias.**
   >
   > No incorpores dependencias, servicios externos ni almacenamiento adicional sin solicitar autorización si fueran imprescindibles.
   >
   > No modifiques `inventario.py`, `github_inventario.py`, `busqueda.py`, las especificaciones oficiales, los documentos aprobados ni los prompts anteriores.
   >
   > No crees ni modifiques `inventario.xlsx`. No implementes todavía CRUD administrativo, escrituras en GitHub API, Gemini operativo, ventas, precios ni cantidades.
   >
   > Ejecuta todas las pruebas del Prompt 08 y la regresión completa de los Prompts 02 a 07.
   >
   > Documenta los resultados, la trazabilidad, las limitaciones reales y las verificaciones pendientes en:
   > `05_Resultados/08_Resultado_Sesiones_Bloqueos_Borradores.md`
   >
   > **No ejecutes git commit, git push, git merge, despliegues ni el Prompt 09.**

2. **Recuperación tras congelamiento de Windows y reanudación en 4 pasos autorizados:**
   - **Hecho confirmado:** Durante la fase inicial de ejecución de pruebas del Prompt 08, el sistema operativo Windows se congeló y fue necesario reiniciar el equipo. Al recuperar VS Code, se realizó una **Auditoría de recuperación en modo de solo lectura**, confirmando mediante inspección estática que la implementación de producción en `03_Aplicacion/autenticacion.py` (`2.637` líneas) y `03_Aplicacion/app.py` (`1.447` líneas) se había conservado íntegra en disco sin corrupción ni errores de sintaxis, por lo que **no fue necesario reiniciar ni reescribir la implementación de producción**.
   - **Hipótesis técnica de sobrecarga (distinta de una causa confirmada a nivel de sistema operativo):** No existe diagnóstico del kernel de Windows que demuestre de forma concluyente la causa exacta del congelamiento; como hipótesis técnica preventiva, se identificó que la versión inicial de `04_Pruebas/test_08_sesiones_bloqueos_borradores.py` acumulaba ~140 invocaciones reales de Argon2id (`19.456 KiB` de memoria nativa en CFFI por operación) y lanzaba `18` hilos concurrentes ejecutando Argon2id simultáneamente en `test_12`.
   - Con autorización expresa paso a paso del usuario, se completaron:
     - **Paso 1:** Optimización preventiva de `04_Pruebas/test_08_sesiones_bloqueos_borradores.py` (`1.139` líneas) mediante mocks controlados en las pruebas de contadores/temporizadores y reducción de `test_12` a 6 hilos, sin alterar los parámetros Argon2id de producción.
     - **Paso 2:** Ejecución secuencial en proceso único de las 40 pruebas de `test_08` (`1,042 s`) y de los 6 archivos de regresión `test_02` a `test_07` (`132` pruebas adicionales), sumando **172 pruebas aprobadas** en `9,647 s` sin fallos ni sobrecarga.
     - **Paso 3:** Verificación local controlada del servidor Streamlit en `127.0.0.1:8518` (`/_stcore/health -> 200 ok`, `GET / -> 200`, cierre confirmado del proceso `PID 25888`) y comprobación de disponibilidad pública y rechazo de login sin credenciales configuradas.
     - **Paso 4 y corrección final de trazabilidad:** Creación y revisión estática de exactitud del presente informe de resultados.

### 1.3. Interpretación del agente y decisiones técnicas verificadas en el código
1. **Temporización determinista e inyectable en servidor (`ProveedorReloj` y `_obtener_tiempo_actual`):**
   - En `03_Aplicacion/autenticacion.py` (línea 54) se define el tipo `ProveedorReloj = Callable[[], float]` y el proveedor activo del servidor `_RELOJ_SERVIDOR_ACTIVO: ProveedorReloj = time.time` (línea 583).
   - Todas las funciones públicas e internas de bloqueo, sesión, renovación, borradores y limpieza aceptan los parámetros opcionales `reloj: ProveedorReloj | None = None` y `ahora_epoch: float | None = None`, resolviendo el instante actual mediante `_obtener_tiempo_actual(reloj, ahora_epoch)` (líneas 608–617), que delega en `ahora_epoch` si fue suministrado, en `reloj()` si se inyectó explícitamente, o en `_RELOJ_SERVIDOR_ACTIVO()` (configurable en pruebas mediante `configurar_reloj_servidor_pruebas()`, líneas 601–605).
   - El tiempo de expiración (`TIEMPO_EXPIRACION_INACTIVIDAD_SEGUNDOS = 900`), la ventana de advertencia (`TIEMPO_ADVERTENCIA_INACTIVIDAD_SEGUNDOS = 780`), la duración del bloqueo (`BLOQUEOS_PROGRESIVOS_SEGUNDOS = (300, 600, 1200, 1800)`) y la retención adicional de borradores (`TIEMPO_RETENCION_BORRADOR_SEGUNDOS = 900`) se calculan exclusivamente en el servidor; cualquier intento de modificar `ultima_actividad_epoch` o `autenticado_en_epoch` dentro de `st.session_state` es detectado en `esta_autenticado_en_sesion()` (líneas 1910–1918) al contrastar con `_SESIONES_ACTIVAS_SERVIDOR` y provoca la revocación inmediata del token en `_TOKENS_REVOCADOS_SERVIDOR`.
2. **Estrategia de almacenamiento temporal en memoria del proceso y concurrencia (`_CANDADO_SEGURIDAD_SERVIDOR`):**
   - Sin añadir servicios externos, bases de datos ni archivos locales (respetando la Sección 5.3 y la Sección 14 del Prompt 08), el estado compartido entre sesiones dentro del mismo proceso Python reside en estructuras de módulo protegidas por `_CANDADO_SEGURIDAD_SERVIDOR = threading.RLock()` (línea 580):
     - `_ESTADO_BLOQUEO_SERVIDOR = _EstadoControlIntentosServidor()` (líneas 564–573 y 598): contador `intentos_fallidos_consecutivos`, `intentos_fallidos_totales_acumulados`, `nivel_bloqueo_consecutivo`, `bloqueado_hasta_epoch`, `duracion_bloqueo_actual_segundos` y `ultimo_intento_fallido_epoch`.
     - `_COMPROBANTES_VERIFICACION_SERVIDOR: dict[str, _RegistroComprobanteServidor]` (líneas 503–512 y 586): comprobantes criptográficos efímeros (`_TTL_COMPROBANTE_VERIFICACION_SEGUNDOS = 60.0`, línea 576) de un solo uso emitidos por `verificar_credenciales_admin()`.
     - `_SESIONES_ACTIVAS_SERVIDOR: dict[str, _RegistroSesionServidor]` (líneas 516–527 y 589) y `_TOKENS_REVOCADOS_SERVIDOR: dict[str, float]` (línea 595): sesiones administrativas vigentes con su autoridad temporal en servidor y registro acotado de tokens revocados.
     - `_BORRADORES_TEMPORALES_SERVIDOR: dict[str, _RegistroBorradorServidor]` (líneas 547–560 y 592): borradores no confirmados en GitHub asociados a la cuenta administrativa y vinculados al contenedor de sesión mediante `_VinculoBorradorSesion` (líneas 531–543) firmado con `HMAC-SHA256`.
3. **Diferenciación entre consultas pasivas y actividad administrativa explícita:**
   - `esta_autenticado_en_sesion()` (líneas 1837–1926), `consultar_estado_sesion_admin()` (líneas 1929–2009) y `requerir_autorizacion_admin()` (líneas 2098–2140) son **comprobaciones pasivas**: verifican firmas HMAC, vigencia e inactividad sin modificar `ultima_actividad_epoch`, garantizando que los re-renderizados pasivos de Streamlit no impidan la expiración a los 15 minutos (`test_24`).
   - Solo las acciones administrativas explícitas (`registrar_actividad_administrativa()` en líneas 2143–2183, `renovar_sesion_admin()` en líneas 2186–2206, `guardar_borrador_admin()` en líneas 2266–2382 y `restaurar_borrador_admin()` en líneas 2544–2603) actualizan `ultima_actividad_epoch` en `_SESIONES_ACTIVAS_SERVIDOR` y re-emiten el `EstadoSesionAdmin` en sesión.
4. **Constantes y contratos de activación del Prompt 08 y compatibilidad con `test_07`:**
   - Dado que `04_Pruebas/test_07_autenticacion_administrativa.py` es un archivo protegido que comprueba en su `test_15` la constante legada `CONTROLES_AVANZADOS_P08_ACTIVOS == False` (línea 128) y el contrato declarativo `CONTRATO_EXTENSION_PROMPT_08 = ContratoExtensionPrompt08()` con `activo_en_etapa_actual == False` (líneas 470–482), ambos símbolos legados se conservaron sin cambios para preservar la compatibilidad.
   - La activación efectiva de las políticas implementadas en el Prompt 08 se declara mediante `POLITICAS_SEGURIDAD_P08_ACTIVAS: bool = True` (línea 131) y el contrato `CONTRATO_SEGURIDAD_PROMPT_08 = ContratoSeguridadPrompt08()` con `activo = True` (líneas 486–499).

### 1.4. Archivos modificados y creados
- **Modificado:** `03_Aplicacion/autenticacion.py` (`2.637` líneas — bloqueos progresivos, expiración a los 15 min, advertencia al min 13, renovación, borradores temporales con retención de 15 min adicionales, revocación y limpieza acotada).
- **Modificado:** `03_Aplicacion/app.py` (`1.447` líneas — integración en `_renderizar_seccion_administrativa_productos()`, líneas 1037–1277, de avisos de bloqueo activo, evaluación pasiva de sesión, redirección automática a Login al expirar, advertencia previa al minuto 13, botón «Continuar sesión» y controles de restauración/descarte de borrador temporal).
- **Creado:** `04_Pruebas/test_08_sesiones_bloqueos_borradores.py` (`1.139` líneas — 40 pruebas automatizadas obligatorias optimizadas en consumo de CPU/RAM).
- **Creado:** `05_Resultados/08_Resultado_Sesiones_Bloqueos_Borradores.md` (presente informe).
- **Archivos protegidos verificados sin modificaciones:** `GEMINI.md`, `AGENTS.md`, `01_Documentacion/*`, `02_Prompts/*`, `03_Aplicacion/inventario.py`, `03_Aplicacion/github_inventario.py`, `03_Aplicacion/busqueda.py`, `03_Aplicacion/estilos.css`, `requirements.txt`, `README.md`, `04_Pruebas/test_02_*.py` a `test_07_*.py` y `05_Resultados/01_*.md` a `07_*.md`. Tampoco existe ni fue creado `03_Aplicacion/inventario.xlsx`.

---

## 2. Matriz de Estado de Requisitos Funcionales (RF) y Criterios de Aceptación (CA)

Clasificación basada exclusivamente en las evidencias obtenidas (eligiendo entre **APROBADO**, **PARCIAL** o **PENDIENTE**):

| Código | Descripción oficial (`02_Especificaciones_v0.md`) | Estado en Prompt 08 | Evidencia y justificación |
| :--- | :--- | :---: | :--- |
| **RF-009 / CA-007** | Buscar productos sin necesidad de crear cuenta o iniciar sesión, incluso durante un bloqueo administrativo | **APROBADO** | Verificado en `test_37_aplicacion_publica_disponible_durante_bloqueo_administrativo`, regresión `test_04`/`test_06`/`test_07` y Paso 3 (`127.0.0.1:8518`). |
| **RF-011 / RF-012 / CA-009** | Acceder a Productos sin autenticación o tras expirar la sesión presenta Login antes de permitir operaciones | **APROBADO** | Verificado en `test_18`, `test_20`, `test_40` y regresión `test_07`. |
| **RF-011 / CA-010** | Introducir credenciales válidas autoriza el acceso administrativo (cuando no hay bloqueo activo) | **APROBADO** | Verificado con Argon2id real en `test_09`, `test_14`, `test_34`, `test_40` y `test_07`. |
| **RF-011 / CA-011** | Introducir credenciales incorrectas deniega el acceso e incrementa el contador de intentos fallidos | **APROBADO** | Verificado en `test_01` a `test_08`, `test_11`, `test_12` y `test_40`. |
| **CA-028 / CA-029 / CA-059** | Protección de secretos en UI, ausencia de secretos en repositorio y contraseñas protegidas con Argon2id | **APROBADO** | Verificado en `test_25` (prohibición de secretos en borradores), `test_35` (Argon2id intacto) y `test_07` (`test_08`–`test_10`). |
| **CA-052** | Cinco intentos fallidos consecutivos activan el bloqueo temporal de autenticación | **PARCIAL** | **Lógica y UI en `AppTest` aprobadas** (`test_01` a `test_03`, `test_11`, `test_12`, `test_40`). Se clasifica como **PARCIAL** a nivel de despliegue porque `_ESTADO_BLOQUEO_SERVIDOR` reside en memoria del proceso Python y se pierde si Streamlit se reinicia o si existen múltiples procesos independientes. |
| **CA-053** | Bloqueos progresivos de 5, 10, 20 y 30 minutos (máximo 30 min) y reinicio tras login exitoso | **PARCIAL** | **Progresión `5 -> 10 -> 20 -> 30 -> 30 -> 30` min y reinicio tras login exitoso verificados** (`test_03` a `test_10`). Se clasifica como **PARCIAL** por la misma limitación del almacenamiento en memoria del proceso. |
| **CA-054** | Advertencia dos minutos antes de que expire la sesión (al minuto 13 de inactividad) | **PARCIAL** | **Verificado en lógica de servidor y en re-ejecución de `AppTest`** (`test_16`, `test_17`, `test_40`). Se clasifica como **PARCIAL** porque la advertencia visual automática al minuto 13 sin interacción del usuario no está demostrada en navegador real (las pruebas con reloj simulado no sustituyen esa verificación). |
| **CA-055** | Expiración automática de la sesión tras 15 minutos de inactividad y revocación de permisos | **PARCIAL** | **Expiración a los `900 s`, revocación en `_TOKENS_REVOCADOS_SERVIDOR` y rechazo en Python verificados** (`test_18`, `test_19`, `test_20`, `test_24`, `test_40`). Se clasifica como **PARCIAL** porque la actualización visual en navegador requiere una interacción o re-renderizado de Streamlit y el registro reside en memoria del proceso, aunque cualquier operación posterior es rechazada inmediatamente en Python. |
| **CA-056** | Renovación de sesión activa mediante el botón «Continuar sesión» | **APROBADO** | Verificado en servidor y en interfaz `AppTest` (`test_15`, `test_21`, `test_22`, `test_23`, `test_40`): renueva sesiones activas por `900 s` y rechaza sesiones ya expiradas. |
| **CA-057** | Retención temporal de borradores no guardados durante 15 minutos adicionales tras expirar la sesión y recuperación tras reautenticación | **PARCIAL** | **Ciclo completo de guardado, retención por `900 s` adicionales, restauración autenticada, aislamiento y caducidad verificado** (`test_25` a `test_32`, `test_40`). Se clasifica como **PARCIAL** porque `_BORRADORES_TEMPORALES_SERVIDOR` reside en memoria del proceso y porque la conexión con formularios CRUD reales corresponde al Prompt 09. |
| **CA-030** | Controles administrativos integrales de sesión (Login, Logout, inactividad, advertencia, renovación, bloqueos y borradores) | **PARCIAL** | Todos los mecanismos de servidor y de interfaz en `AppTest` están implementados y verificados (`test_01` a `test_40`), sujeto a las dos limitaciones documentadas (advertencia automática sin interacción en navegador real y persistencia en memoria del proceso). |
| **CA-027 / RF-013 / CA-019 / CA-058** | Rechazo de modificaciones no autorizadas y restricción administrativa desde dispositivos móviles | **PARCIAL** | `requerir_autorizacion_admin()`, `guardar_borrador_admin()`, `obtener_borrador_admin()` y `restaurar_borrador_admin()` rechazan accesos sin sesión, expirados, bloqueados o en contexto móvil (`test_20`, `test_28`, `test_29`); la protección sobre escrituras reales del inventario se completará en el Prompt 09. |
| **RF-032 / RF-033 / RF-034 / CA-031..CA-033** | Sección visual «Asistente Gemini — Próximamente» sin Gemini API funcional ni API key requerida | **APROBADO** | Verificado en `test_39` y en la regresión `test_06`. |

---

## 3. Apartados Técnicos del Informe (Sección 17 del Prompt 08)

### A. Objetivo y alcance
- **Alcance implementado:**
  1. Conteo compartido en servidor de intentos fallidos consecutivos (`MAX_INTENTOS_FALLIDOS_CONSECUTIVOS = 5`) y activación de bloqueo al 5.º intento fallido consecutivo (`CA-052`).
  2. Progresión de bloqueos temporales de **5, 10, 20 y 30 minutos** (`BLOQUEOS_PROGRESIVOS_MINUTOS = (5, 10, 20, 30)`, `DURACION_MAXIMA_BLOQUEO_MINUTOS = 30`, `CA-053`) y reinicio de contadores tras un inicio de sesión exitoso (`_reiniciar_contadores_bloqueo_servidor()`).
  3. Expiración de la sesión administrativa a los **15 minutos (`900 s`) de inactividad** (`CA-055`), revocación efectiva del token en `_TOKENS_REVOCADOS_SERVIDOR` y bloqueo de cualquier operación protegida posterior.
  4. Detección de la ventana de advertencia a los **13 minutos (`780 s`) de inactividad** (2 minutos antes de expirar, `VENTANA_ADVERTENCIA_PREVIA_SEGUNDOS = 120`, `CA-054`) y botón **«Continuar sesión»** (`TEXTO_BOTON_CONTINUAR_SESION`, `CA-056`) para renovar explícitamente la sesión activa.
  5. Subsistema de borradores administrativos temporales (`CA-057`) con retención durante **15 minutos adicionales (`900 s`)** tras la expiración de la sesión (`_transicionar_borrador_por_expiracion_sesion()`), recuperación sujeta a reautenticación válida, aislamiento entre sesiones, prohibición de almacenar secretos y eliminación inmediata en `Logout` voluntario.
  6. Depuración automática y acotada en memoria de comprobantes vencidos, sesiones expiradas, tokens revocados y borradores caducados (`depurar_registros_seguridad_servidor()`, líneas 1202–1239 de `autenticacion.py`).
- **Restricciones respetadas:**
  - No se crearon formularios CRUD de productos ni operaciones de escritura en GitHub API (reservados para el Prompt 09).
  - No se creó ni modificó `03_Aplicacion/inventario.xlsx`.
  - No se incorporaron dependencias externas nuevas en `requirements.txt`.
  - Se preservaron intactas todas las correcciones de seguridad del Prompt 07 (Argon2id, comprobantes criptográficos de un solo uso, firmas HMAC-SHA256, validación de contexto móvil y escapado HTML/XSS).

### B. Arquitectura de seguridad: registros, sesiones, concurrencia y revocación
- **Sincronización y concurrencia:** Todas las lecturas y mutaciones de estado de seguridad en `03_Aplicacion/autenticacion.py` se ejecutan dentro de `with _CANDADO_SEGURIDAD_SERVIDOR:` (`threading.RLock()`, línea 580), evitando condiciones de carrera cuando múltiples hilos o sesiones concurren sobre el mismo proceso Python (`test_12`).
- **Comprobación de bloqueo previa a Argon2id:** En `verificar_credenciales_admin()` (líneas 1375–1390), `consultar_estado_bloqueo_admin()` se ejecuta **antes** de `verificar_contrasena_hash()`. Si la cuenta está bloqueada, la solicitud se rechaza inmediatamente con `CodigoResultadoAutenticacion.CUENTA_BLOQUEADA_TEMPORALMENTE`, sin ejecutar Argon2id y sin emitir comprobantes (`test_08`, `test_13`).
- **Preservación de Argon2id, HMAC y comprobantes de un solo uso del Prompt 07:**
  - `_HASHER_ARGON2ID` (líneas 60–74 de `autenticacion.py`) mantiene `Argon2id` (`Type.ID`) con los parámetros exactos:
    - `ARGON2_TIME_COST_DEFECTO = 2` (`time_cost=2`)
    - `ARGON2_MEMORY_COST_KIB_DEFECTO = 19456` (`memory_cost=19456` KiB)
    - `ARGON2_PARALLELISM_DEFECTO = 1` (`parallelism=1`)
    - `ARGON2_HASH_LEN_DEFECTO = 32` (`hash_len=32`)
    - `ARGON2_SALT_LEN_DEFECTO = 16` (`salt_len=16`)
  - `verificar_credenciales_admin()` solo emite un `ComprobanteVerificacionCredenciales` firmado con `HMAC-SHA256` (`_calcular_firma_comprobante()`) cuando el bloqueo no está activo y la verificación de usuario y contraseña resulta exitosa.
  - `registrar_autenticacion_en_sesion()` consume atómicamente (`pop`, línea 1607) el comprobante en `_COMPROBANTES_VERIFICACION_SERVIDOR`, impidiendo reutilizarlo en una segunda sesión (`test_34`).
- **Revocación efectiva y protección contra manipulación en cliente:**
  - La marca autoritativa de actividad (`ultima_actividad_epoch`) se guarda en `_SESIONES_ACTIVAS_SERVIDOR[token_sesion]`. Si el cliente manipula `EstadoSesionAdmin.ultima_actividad_epoch` o intenta reinyectar un `EstadoSesionAdmin` antiguo tras haber expirado, `esta_autenticado_en_sesion()` detecta que el token está en `_TOKENS_REVOCADOS_SERVIDOR` o que su marca temporal difiere de la del servidor (líneas 1883–1918) y revoca inmediatamente el acceso (`test_19`, `test_36`).
- **Limpieza y límites de memoria (`depurar_registros_seguridad_servidor`):**
  - Se ejecuta en las operaciones de seguridad y aplica las constantes exactas definidas en las líneas 160–165 y 576 de `autenticacion.py`:
    - `_TTL_COMPROBANTE_VERIFICACION_SEGUNDOS: float = 60.0`
    - `MAX_COMPROBANTES_VERIFICACION_SERVIDOR: int = 64`
    - `MAX_SESIONES_ACTIVAS_SERVIDOR: int = 32`
    - `MAX_BORRADORES_TEMPORALES_SERVIDOR: int = 64`
    - `MAX_HISTORIAL_TOKENS_REVOCADOS: int = 128`
    - `MAX_TAMANO_BORRADOR_BYTES: int = 65536` y `MAX_CAMPOS_BORRADOR: int = 64`
  - Libera bloqueos cuyo tiempo ya concluyó (`_actualizar_estado_bloqueo_vencido()`) sin borrar nunca un bloqueo activo ni el `nivel_bloqueo_consecutivo` acumulado (`test_33`).

### C. Bloqueos progresivos tras cinco intentos fallidos

| Nivel de bloqueo consecutivo | Intentos fallidos consecutivos requeridos | Duración del bloqueo | Segundos (`calcular_duracion_bloqueo_segundos`) | Evidencia en `test_08_sesiones_bloqueos_borradores.py` |
| :---: | :---: | :---: | :---: | :--- |
| Sin bloqueo | `1` a `4` | `0 min` | `0 s` | `test_01_primer_intento_fallido`, `test_02_cuatro_intentos_fallidos_sin_bloqueo` |
| **1.er bloqueo** | `5` | **5 minutos** | `300 s` | `test_03_quinto_intento_y_primer_bloqueo_cinco_minutos`, `test_11`, `test_12`, `test_40` |
| **2.º bloqueo** | Nuevos `5` fallos tras vencer el 1.º | **10 minutos** | `600 s` | `test_04_segundo_bloqueo_diez_minutos` |
| **3.er bloqueo** | Nuevos `5` fallos tras vencer el 2.º | **20 minutos** | `1.200 s` | `test_05_tercer_bloqueo_veinte_minutos` |
| **4.º bloqueo** | Nuevos `5` fallos tras vencer el 3.º | **30 minutos** | `1.800 s` | `test_06_cuarto_bloqueo_treinta_minutos` |
| **5.º y 6.º bloqueos (tope máximo)** | Nuevos `5` fallos por ciclo | **30 minutos (máximo)** | `1.800 s` | `test_07_bloqueos_posteriores_sin_exceder_treinta_minutos` |
| **Reinicio tras login válido** | Login exitoso fuera de bloqueo | Reinicia intentos a `0` y nivel a `0` | `0 s` | `test_09_finalizacion_del_bloqueo`, `test_10_reinicio_de_contadores_despues_de_login_exitoso` |

### D. Inactividad, advertencia previa y renovación de sesión
- **Ventana de sesión activa (`0 s` a `< 780 s`):** `consultar_estado_sesion_admin()` devuelve `EstadoTiempoSesionAdmin` con `autenticado=True`, `en_ventana_advertencia=False`, `expirada=False` (`test_14`, `test_16`).
- **Advertencia al minuto 13 (`780 s` a `< 900 s`):** Al alcanzar `780 s` de inactividad (restan `120 s` o menos), `consultar_estado_sesion_admin()` activa `en_ventana_advertencia=True` y genera `mensaje_advertencia` mediante `formatear_mensaje_advertencia_expiracion()`, mostrándose junto con el botón **«Continuar sesión»** (`btn_admin_continuar_sesion`) en `_renderizar_seccion_administrativa_productos()` (`test_17`, `test_40`).
- **Renovación explícita («Continuar sesión»):** Al pulsar «Continuar sesión» antes del minuto 15, `ejecutar_renovacion_sesion_en_sesion()` invoca `renovar_sesion_admin()` -> `registrar_actividad_administrativa()`, actualiza `ultima_actividad_epoch` en `_SESIONES_ACTIVAS_SERVIDOR`, restablece los `900 s` de vigencia y oculta la advertencia (`test_21`, `test_40`). Si la sesión ya había expirado (`>= 900 s`), `renovar_sesion_admin()` lanza `ErrorAutorizacionAdmin` con código `SESION_EXPIRADA` (`test_22`).
- **Expiración al minuto 15 (`>= 900 s`):** Al cumplirse `900 s` sin actividad administrativa explícita, `_revocar_sesion_por_expiracion_en_estado()` elimina la sesión de `_SESIONES_ACTIVAS_SERVIDOR`, registra el token en `_TOKENS_REVOCADOS_SERVIDOR`, limpia `CLAVE_SESION_ADMIN`, guarda `CodigoResultadoAutenticacion.SESION_EXPIRADA.value` en `CLAVE_MOTIVO_FIN_SESION_ADMIN`, transiciona cualquier borrador activo a retención por expiración (`+900 s`) y presenta nuevamente el formulario `Login` con el aviso `MENSAJE_SESION_EXPIRADA_INACTIVIDAD` (`test_18`, `test_19`, `test_20`, `test_24`, `test_40`).

### E. Gestión de borradores temporales durante los 15 minutos adicionales
- **Creación y validación de seguridad (`guardar_borrador_admin`, líneas 2266–2382):** Permite asociar a la sesión administrativa autenticada un `BorradorTemporalAdmin` (`confirmado_en_github=False`, `es_borrador_temporal=True`) con copia profunda de los datos de trabajo (`_validar_y_copiar_datos_borrador()`) y un `_VinculoBorradorSesion` firmado con `HMAC-SHA256` (`_calcular_firma_vinculo_borrador()`). Prohibe almacenar claves en `_CLAVES_PROHIBIDAS_EN_BORRADOR` o valores que contengan hashes `$argon2`, tokens activos o secretos (`ErrorSeguridadBorradorAdmin`, verificado en `test_25`).
- **Retención tras expirar la sesión (`test_26`):** Cuando la sesión expira por inactividad a los 15 minutos, `_transicionar_borrador_por_expiracion_sesion()` (líneas 1055–1081) conserva el borrador con `retenido_por_expiracion=True`, `token_sesion_activa=None` y `expira_retencion_epoch = momento_expiracion_sesion + 900.0` (15 minutos adicionales), sin otorgar permisos administrativos a la sesión expirada (`test_28`).
- **Recuperación tras reautenticación (`test_27`, `test_40`):** Si el administrador vuelve a autenticarse válidamente dentro de esos 15 minutos adicionales en la misma sesión (y con la misma cuenta y `huella_configuracion`), `registrar_autenticacion_en_sesion()` revincula el borrador al nuevo `token_sesion` y permite consultarlo con `obtener_borrador_admin()`, restaurarlo con `restaurar_borrador_admin()` (`btn_admin_restaurar_borrador`, dejándolo en `CLAVE_BORRADOR_RESTAURADO_ADMIN`) o descartarlo con `descartar_borrador_admin()` (`btn_admin_descartar_borrador`).
- **Aislamiento, caducidad y Logout voluntario (`test_29`, `test_30`, `test_31`, `test_32`):**
  - Otra sesión independiente, otra cuenta administrativa, un contexto móvil o un estado de bloqueo activo no pueden leer ni restaurar el borrador (`test_29`, `test_32`).
  - Transcurridos los 15 minutos adicionales sin reautenticación, `_depurar_borradores_vencidos()` elimina definitivamente el registro de `_BORRADORES_TEMPORALES_SERVIDOR` (`test_30`).
  - Cuando el administrador pulsa voluntariamente **Cerrar sesión (Logout)**, `cerrar_sesion_admin(estado, conservar_borrador_temporal=False)` elimina de inmediato cualquier borrador temporal asociado a esa sesión (`test_31`).

### F. Resumen de pruebas ejecutadas y optimización de consumo

#### F.1. Optimización aplicada en el Paso 1 para reducir el consumo de CPU y RAM
- **Hipótesis de sobrecarga abordada:** La versión inicial de `test_08_sesiones_bloqueos_borradores.py` ejecutaba ~140 hashes reales de Argon2id (`19.456 KiB` cada uno) y lanzaba `18` hilos simultáneos con Argon2id real en `test_12`.
- **Optimización implementada en `04_Pruebas/test_08_sesiones_bloqueos_borradores.py` (`1.139` líneas):**
  - Se conservaron **9 ejecuciones reales de Argon2id** en `setUpClass` (1 generación de hash), `test_01` (1 fallo real), `test_03` (1 fallo real en el 5.º intento), `test_09` (1 login válido real tras bloqueo), `test_14` (1 login válido real), `test_34` (1 verificación real con comprobante de un solo uso), `test_35` (2 verificaciones reales: clave correcta e incorrecta) y `test_40` (1 login válido real en `AppTest`).
  - En las pruebas cuyo propósito es evaluar progresión de contadores (`5, 10, 20, 30` min), temporizadores (`13` y `15` min) y ciclo de vida de borradores, `_parche_verificacion_controlada()` (líneas 143–155) sustituye únicamente la llamada CFFI de `autenticacion.verificar_contrasena_hash` conservando el 100 % de la lógica de `autenticacion.py` (cerrojo `_CANDADO_SEGURIDAD_SERVIDOR`, comparación en tiempo constante, contadores, comprobantes de un solo uso, firmas HMAC, sesiones y borradores).
  - En `test_12_proteccion_ante_intentos_concurrentes` (líneas 397–429), se redujo la concurrencia a **6 hilos** en un único `ThreadPoolExecutor(max_workers=6)` sincronizados con `threading.Barrier(6)` y `pausa_segundos=0.002` para comprobar la serialización real bajo `_CANDADO_SEGURIDAD_SERVIDOR` sin saturar la memoria nativa.

#### F.2. Tabla obligatoria de verificaciones del Prompt 08 (Sección 17.F)

| Verificación | Resultado | Evidencia |
| :--- | :---: | :--- |
| Cinco intentos fallidos | **APROBADO** | `test_01_primer_intento_fallido`, `test_02_cuatro_intentos_fallidos_sin_bloqueo`, `test_03_quinto_intento_y_primer_bloqueo_cinco_minutos` |
| Primer bloqueo: 5 min | **APROBADO** | `test_03_quinto_intento_y_primer_bloqueo_cinco_minutos` (`300 s`), `test_40` |
| Segundo bloqueo: 10 min | **APROBADO** | `test_04_segundo_bloqueo_diez_minutos` (`600 s`) |
| Tercer bloqueo: 20 min | **APROBADO** | `test_05_tercer_bloqueo_veinte_minutos` (`1.200 s`) |
| Cuarto bloqueo: 30 min | **APROBADO** | `test_06_cuarto_bloqueo_treinta_minutos` (`1.800 s`) y tope máximo en `test_07` (`5.º` y `6.º` bloqueos a `1.800 s`) |
| Expiración de sesión | **APROBADO** | `test_18_expiracion_al_minuto_quince`, `test_19_revocacion_real_del_token_expirado`, `test_20_rechazo_de_operaciones_despues_de_expirar`, `test_24` |
| Advertencia al minuto 13 | **PARCIAL (Simulado / AppTest)** | `test_17_advertencia_al_minuto_trece`, `test_40` (verificado con reloj simulado en servidor y en re-ejecución de `AppTest`; pendiente demostración automática sin interacción en navegador real) |
| Renovación de sesión | **APROBADO** | `test_15_actividad_administrativa_legitima`, `test_21_renovacion_antes_de_la_expiracion`, `test_22_rechazo_de_renovacion_despues_de_expirar`, `test_40` |
| Borrador retenido | **APROBADO** | `test_25_guardar_un_borrador_temporal`, `test_26_retener_borrador_despues_de_expirar_sesion` (`+900 s` tras expirar sesión) |
| Borrador restaurado | **APROBADO** | `test_27_reautenticarse_y_restaurar_borrador_durante_ventana_permitida`, `test_28`, `test_29`, `test_40` |
| Borrador eliminado tras caducidad | **APROBADO** | `test_30_expirar_y_eliminar_borradores_despues_de_quince_minutos_adicionales`, `test_31_manejo_de_logout_voluntario` |
| Aislamiento de sesiones | **APROBADO** | `test_11_intentos_distribuidos_entre_dos_sesiones`, `test_23_separacion_entre_sesiones_independientes`, `test_32_aislamiento_de_borradores_entre_sesiones` |
| Concurrencia | **APROBADO** | `test_12_proteccion_ante_intentos_concurrentes` (6 hilos concurrentes sincronizados con `Barrier(6)` bajo `_CANDADO_SEGURIDAD_SERVIDOR`) |
| Regresión de Prompts 02–07 | **APROBADO** | **132 pruebas aprobadas** ejecutadas secuencialmente en los archivos `test_02` a `test_07` + **40 pruebas aprobadas** en `test_08` (**total: 172/172 OK**) |

#### F.3. Detalle de ejecución secuencial de las 172 pruebas (Paso 2) y servidor Streamlit (Paso 3)

| Orden | Archivo / Verificación | Pruebas | Aprobadas | Fallos | Duración | Modalidad de verificación |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `04_Pruebas/test_08_sesiones_bloqueos_borradores.py` | 40 | 40 | 0 | `1,042 s` | Unitaria con reloj simulado + integración `AppTest` |
| 2 | `04_Pruebas/test_02_motor_inventario.py` | 23 | 23 | 0 | `0,219 s` | Regresión unitaria (Prompt 02) |
| 3 | `04_Pruebas/test_03_lectura_github.py` | 21 | 21 | 0 | `0,333 s` | Regresión unitaria (Prompt 03) |
| 4 | `04_Pruebas/test_04_busqueda_publica.py` | 25 | 25 | 0 | `1,001 s` | Regresión unitaria + `AppTest` (Prompt 04) |
| 5 | `04_Pruebas/test_05_detalles_ubicaciones.py` | 23 | 23 | 0 | `2,344 s` | Regresión unitaria + `AppTest` (Prompt 05) |
| 6 | `04_Pruebas/test_06_interfaz_responsive_gemini.py` | 18 | 18 | 0 | `3,156 s` | Regresión de interfaz y CSS en `AppTest` (Prompt 06) |
| 7 | `04_Pruebas/test_07_autenticacion_administrativa.py` | 22 | 22 | 0 | `1,552 s` | Regresión de seguridad Argon2id/HMAC/`AppTest` (Prompt 07) |
| **Subtotal** | **Suite automatizada completa (Prompts 02 a 08)** | **172** | **172** | **0** | **`9,647 s`** | **Ejecución secuencial en proceso único** |
| 8 | Servidor real `streamlit run 03_Aplicacion/app.py` (`127.0.0.1:8518`, `PID 25888`) | — | OK | 0 | ~`4,0 s` | `/_stcore/health -> HTTP 200 (ok)`, `GET / -> HTTP 200 (6.463 bytes)`, proceso cerrado (`PROCESS_CLOSED=True`) |

### G. Limitaciones reales y verificaciones pendientes

Conforme a las reglas de trazabilidad y honestidad técnica de `AGENTS.md` y de la Sección 13 del Prompt 08, se registran expresamente las siguientes distinciones y limitaciones:

1. **Diferenciación estricta entre modalidades de verificación:**
   - **Pruebas unitarias con tiempo simulado (`RelojSimulado` inyectado como `ProveedorReloj`):** Verifican de forma exacta todas las transiciones de bloqueo (`5, 10, 20, 30` min), expiración (`15` min), ventana de advertencia (`13` min), renovación, retención de borradores (`15` min adicionales) y limpieza de memoria (`test_01` a `test_36`).
   - **Pruebas de integración con `AppTest`:** Verifican el renderizado de alertas de bloqueo, el aviso de expiración próxima al minuto 13 cuando el script se re-ejecuta, el botón «Continuar sesión», la redirección al formulario de Login tras expirar y la restauración de borradores en la interfaz (`test_37`, `test_40`).
   - **Verificación real del servidor Streamlit (`127.0.0.1:8518`):** Demuestra que el servidor inicia limpiamente (`HTTP 200`, `/_stcore/health -> ok`), que la interfaz pública opera sin credenciales administrativas configuradas y que el acceso administrativo permanece deshabilitado cuando no existen secretos configurados.
2. **Limitaciones técnicas obligatorias a tener en cuenta antes de producción:**
   - **La advertencia visual automática al minuto 13 sin interacción del usuario no está demostrada en navegador real.** En la arquitectura estándar de Streamlit, la interfaz se actualiza al procesarse un evento o re-ejecución del script; las pruebas con reloj simulado y `AppTest` no sustituyen una prueba de 13/15 minutos en tiempo real con un navegador abierto sin interacción del usuario.
   - **Los bloqueos, sesiones y borradores almacenados en memoria del proceso (`_ESTADO_BLOQUEO_SERVIDOR`, `_SESIONES_ACTIVAS_SERVIDOR`, `_BORRADORES_TEMPORALES_SERVIDOR`) se pierden al reiniciar Streamlit y no se comparten entre procesos distintos** (por ejemplo, si el entorno de despliegue reciclara el contenedor o levantara múltiples workers).
   - **Estos aspectos deben revisarse antes de considerar completamente validada la seguridad administrativa para producción.**

### H. Evaluación final y estado del repositorio

- **Resultado de la evaluación:** **COMPLETADO CON OBSERVACIONES**
  - **Justificación:** Se implementaron y verificaron con 100 % de éxito los **40 casos de prueba del Prompt 08** y las **132 pruebas de regresión de los Prompts 02 a 07** (`172/172 OK`), así como el arranque y cierre controlado del servidor Streamlit en `127.0.0.1:8518`. Se elige `COMPLETADO CON OBSERVACIONES` (y se clasifican como `PARCIAL` los criterios `CA-030` y `CA-052` a `CA-058`) exclusivamente para dejar constancia transparente de las dos limitaciones inherentes a la arquitectura actual sin servicios externos: la ausencia de advertencia visual automática demostrada al minuto 13 sin interacción del usuario en navegador real y la no persistencia del estado de seguridad en memoria entre reinicios o procesos distintos.
- **Estado del repositorio Git al finalizar (`git status --short` sobre commit base `c24b1a9`):**
  - `M 03_Aplicacion/app.py`
  - `M 03_Aplicacion/autenticacion.py`
  - `?? 04_Pruebas/test_08_sesiones_bloqueos_borradores.py`
  - `?? 05_Resultados/08_Resultado_Sesiones_Bloqueos_Borradores.md`
  - No se ejecutaron `git commit`, `git push`, `git merge` ni despliegues.
