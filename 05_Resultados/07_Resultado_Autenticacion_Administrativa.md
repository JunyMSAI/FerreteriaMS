# Informe de Resultados — FERMS-V0-P07: Autenticación administrativa

**Proyecto:** FerreteríaMS v0  
**TASK_ID:** `FERMS-V0-P07`  
**Título de la tarea:** Implementación de la autenticación administrativa segura (cuenta única, hashing Argon2id, Login/Logout y protección de sesión en Python)  
**Fecha real de ejecución:** 2026-10-20  
**Hora real de ejecución inicial:** 19:21:42 -04:00 a 19:42:30 -04:00  
**Hora real de corrección puntual de seguridad:** 19:49:22 -04:00 a 19:58:00 -04:00  
**Agente de desarrollo:** Gemini (Antigravity dentro de VS Code)  
**Repositorio:** `JunyMSAI/FerreteriaMS`  
**Rama:** `main`  
**Commit base (`HEAD`):** `0fe1acf` (`Prompt "07_Autenticacion_Administrativa" incluido`)  
**Commit nuevo generado en esta tarea:** Ninguno (por instrucción expresa del usuario y de la Sección 13 del Prompt 07)

---

## 1. Trazabilidad Obligatoria (Sección 14 del Prompt 07 y Sección 3.10 de `AGENTS.md`)

### 1.1. Referencia al prompt oficial
- **Archivo del prompt:** `02_Prompts/07_Autenticacion_Administrativa.md` (consultado íntegramente y conservado sin alteraciones).

### 1.2. Solicitud original íntegra del usuario
> Ejecuta la tarea **FERMS-V0-P07 — Autenticación administrativa** del proyecto FerreteríaMS v0.
>
> Lee íntegramente `02_Prompts/07_Autenticacion_Administrativa.md` y ejecuta exclusivamente sus instrucciones aprobadas.
>
> Antes de comenzar, consulta `GEMINI.md`, `AGENTS.md`, `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`, `01_Documentacion/02_Especificaciones_v0.md` y los resultados de los Prompts 05 y 06.
>
> Verifica el estado actual de Git y el commit base. Si existen modificaciones pendientes inesperadas, detente e informa antes de modificar archivos.
>
> **Autorizo únicamente las modificaciones locales previstas en el Prompt 07**, incluyendo el módulo `03_Aplicacion/autenticacion.py`, la adaptación de Login/Logout en `03_Aplicacion/app.py`, los ajustes visuales necesarios, las pruebas, el informe y la dependencia de hashing segura si está justificada.
>
> Implementa una sola cuenta administrativa, credenciales configuradas mediante mecanismos seguros, verificación de contraseña mediante hash y protección del acceso administrativo desde Python.
>
> Conserva el funcionamiento público de búsqueda, paginación, detalles, ubicaciones y Gemini «Próximamente».
>
> No incluyas credenciales reales, contraseñas por defecto ni secretos en el repositorio. Si las credenciales administrativas todavía no están configuradas, mantén el acceso administrativo deshabilitado de forma segura.
>
> Respeta la restricción conceptual de administración desde computadora. No afirmes que está protegida a nivel de servidor si solo se oculta mediante CSS.
>
> **No implementes todavía las reglas avanzadas del Prompt 08:** expiración de 15 minutos, advertencia previa, renovación, cinco intentos fallidos, bloqueos progresivos y conservación de borradores.
>
> No modifiques `inventario.py`, `github_inventario.py`, `busqueda.py`, los documentos oficiales, los prompts anteriores ni el archivo maestro `inventario.xlsx`.
>
> No implementes CRUD de productos, escritura mediante GitHub API, Gemini operativo, ventas, precios, cantidades ni PWA.
>
> Ejecuta las pruebas de autenticación y toda la regresión de los Prompts 02 a 06. Comprueba que Streamlit continúe funcionando sin credenciales administrativas configuradas.
>
> Registra los resultados y la trazabilidad en `05_Resultados/07_Resultado_Autenticacion_Administrativa.md`.
>
> **No ejecutes git commit, git push, git merge, despliegues ni el Prompt 08.**
>
> Al finalizar, entrega un informe detallado, identifica los archivos modificados, distingue las protecciones implementadas de las pendientes y espera mi revisión y autorización.

### 1.3. Interpretación del agente y decisiones técnicas de autenticación
- **Interpretación de los requisitos aprobados:**
  - Desarrollar en un módulo dedicado (`03_Aplicacion/autenticacion.py`) la base de autenticación para la **única cuenta administrativa** de FerreteríaMS v0 (`RF-011`, `RF-012`, `Sección 6.3.1`), desacoplada del código de interfaz para que todas sus funciones puedan verificarse unitariamente sin iniciar Streamlit.
  - Leer las credenciales administrativas exclusivamente desde mecanismos seguros del entorno (`FERRETERIAMS_ADMIN_USER` / `FERRETERIAMS_ADMIN_PASSWORD_HASH` o `st.secrets`), manteniendo deshabilitado el acceso administrativo si no están configuradas o si el hash no es válido (`CA-028`, `CA-029`, `CA-059`).
  - Integrar en `03_Aplicacion/app.py` la navegación hacia la sección **Productos** (`RF-012`, `CA-009`), el formulario **Login**, la verificación en Python (`CA-010`, `CA-011`) y el botón **Logout** (`Cerrar sesión`), mostrando una vista administrativa inicial informativa sin formularios de mantenimiento de inventario (reservados para el Prompt 09) y sin activar todavía los bloqueos progresivos ni la expiración por inactividad (reservados para el Prompt 08).
- **Decisiones técnicas tomadas por el agente:**
  1. **Selección de algoritmo y biblioteca (`Argon2id` mediante `argon2-cffi>=23.1.0`):** Conforme a la preferencia explícita de la Sección 6.3 del Prompt 07, se incorporó `argon2-cffi` en `requirements.txt` y se configuró `PasswordHasher` con variante `Type.ID` (`Argon2id`, `time_cost=2`, `memory_cost=19456 KiB`, `parallelism=1`, `salt_len=16`, `hash_len=32`). `es_hash_contrasena_valido()` rechaza cualquier valor en texto plano, MD5, SHA-1 o SHA-256.
  2. **Resistencia a enumeración de usuarios y ataques de tiempo:** `verificar_credenciales_admin()` compara el nombre de usuario con `hmac.compare_digest()` y ejecuta siempre una verificación Argon2id (contra el hash configurado o contra `_HASH_FANTASMA_TIEMPO_CONSTANTE`) antes de emitir el resultado, devolviendo exactamente el mismo mensaje (`MENSAJE_CREDENCIALES_INVALIDAS`) cuando falla el usuario o la contraseña.
  3. **Protección contra manipulación de claves públicas de sesión (Secciones 8.3 y 11.1.14):** `registrar_autenticacion_en_sesion()` emite un objeto inmutable `EstadoSesionAdmin` firmado con `HMAC-SHA256` mediante una clave efímera del servidor (`_CLAVE_FIRMA_SESION_PROCESO`) y registra el `token_sesion` en `_SESIONES_ACTIVAS_SERVIDOR`. `esta_autenticado_en_sesion()` y `requerir_autorizacion_admin()` ignoran y limpian cualquier marcador booleano público (`estado["admin"] = True`, `estado["ferms_admin_autenticado"] = True`, etc.) y rechazan tokens no registrados o revocados tras `cerrar_sesion_admin()`.
  4. **Navegación condicional en Python:** La conmutación entre `🏠 Inicio` (público) y `📦 Productos` (administrativo) se realiza en Python (`SeccionInterfaz.INICIO` / `SeccionInterfaz.PRODUCTOS`), de modo que la vista pública inicial conserva intacto su árbol de componentes para clientes y todas las pruebas de regresión de los Prompts 02 a 06.

### 1.4. Acciones realizadas
1. Verificación inicial del árbol de trabajo (`git status` y `git log -n 1 --oneline`), confirmando estado limpio sobre el commit base `0fe1acf`.
2. Lectura íntegra de `GEMINI.md`, `AGENTS.md`, `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx` (incluyendo las imágenes conceptuales `image1.png`, `image4.png` e `image5.png`), `01_Documentacion/02_Especificaciones_v0.md`, los Prompts 05, 06 y 07, y los informes de resultados 05 y 06.
3. Instalación y registro justificado de `argon2-cffi>=23.1.0` en `requirements.txt`.
4. Creación del módulo `03_Aplicacion/autenticacion.py` con verificación Argon2id, lectura segura de configuración, sanitización de secretos, estado de sesión firmado por servidor y contratos preparados para el Prompt 08.
5. Adaptación de `03_Aplicacion/app.py` y `03_Aplicacion/estilos.css` para incorporar la navegación `Inicio` / `Productos`, el formulario Login, el panel administrativo inicial autorizado y la acción Logout.
6. Creación y ejecución de `04_Pruebas/test_07_autenticacion_administrativa.py` (22 pruebas automatizadas tras la corrección puntual de seguridad: 18 de seguridad/unidad + 4 flujos integrales en `AppTest`) y ejecución de la regresión completa de los Prompts 02 a 07 (**132 pruebas ejecutadas, 132 OK**).
7. Verificación de arranque real del servidor local Streamlit (`streamlit run 03_Aplicacion/app.py`) sin credenciales administrativas configuradas (`HTTP 200 OK`, `/_stcore/health -> ok`).
8. **Corrección puntual de seguridad posterior a revisión independiente (2026-10-20 19:49 -04:00):**
   - **Problema 1 detectado (Emisión de sesiones administrativas):** En la versión inicial de `03_Aplicacion/autenticacion.py`, `registrar_autenticacion_en_sesion(estado, usuario)` permitía emitir un `EstadoSesionAdmin` firmado a partir de un nombre de usuario en texto sin exigir evidencia criptográfica de una verificación previa de credenciales.
   - **Corrección aplicada al Problema 1:** Se incorporó `ComprobanteVerificacionCredenciales` y el registro efímero en servidor `_COMPROBANTES_VERIFICACION_SERVIDOR` (firmado con `HMAC-SHA256` mediante `_CLAVE_FIRMA_SESION_PROCESO`, vinculado a la huella de configuración y con vigencia máxima de 60 segundos). Solo `verificar_credenciales_admin()` emite este comprobante cuando tanto la comparación en tiempo constante del usuario como la verificación Argon2id de la contraseña resultan satisfactorias. `registrar_autenticacion_en_sesion()` exige y consume atómicamente (`pop`) dicho comprobante de un solo uso; cualquier intento de invocarla pasando únicamente un nombre de usuario, un `ResultadoAutenticacion` fallido/falsificado o un comprobante ya consumido revoca el estado y lanza `ErrorAutorizacionAdmin`. Asimismo, `_RegistroSesionServidor` y `_calcular_firma_sesion()` quedan vinculados al `id_comprobante_origen`.
   - **Problema 2 detectado (Presentación segura del usuario):** En `03_Aplicacion/app.py`, `_renderizar_seccion_administrativa_productos()` interpolaba `{sesion_admin.usuario}` directamente dentro de un bloque `st.markdown(..., unsafe_allow_html=True)`.
   - **Corrección aplicada al Problema 2:** Se eliminó toda interpolación de `sesion_admin.usuario` dentro del bloque `unsafe_allow_html=True` (dejándolo como plantilla estática) y se añadió `formatear_nombre_usuario_admin_seguro()` con `html.escape(..., quote=True)`, presentando el identificador mediante `st.caption()` sin `unsafe_allow_html`.

### 1.5. Archivos creados y modificados
- **Creado:** `03_Aplicacion/autenticacion.py`
- **Modificado:** `03_Aplicacion/app.py`
- **Modificado:** `03_Aplicacion/estilos.css`
- **Modificado:** `requirements.txt`
- **Creado:** `04_Pruebas/test_07_autenticacion_administrativa.py`
- **Creado:** `05_Resultados/07_Resultado_Autenticacion_Administrativa.md`

### 1.6. Matriz de estado de Requisitos Funcionales (RF) y Criterios de Aceptación (CA) (Sección 4 del Prompt 07)

| Código | Descripción oficial (`02_Especificaciones_v0.md`) | Clasificación en Prompt 07 | Detalle de estado |
|---|---|---|---|
| **RF-009 / CA-007** | Buscar productos sin necesidad de crear cuenta o iniciar sesión | **Implementado en Prompt 07 (Conservado)** | La sección pública `Inicio` funciona sin sesión ni credenciales administrativas configuradas. |
| **RF-011 / RF-012 / CA-009** | Acceder a Productos sin autenticación presenta Login/Logout antes de permitir modificaciones | **Implementado en Prompt 07** | Al abrir `📦 Productos` sin sesión válida se presenta exclusivamente el acceso `Login` en Python; no se exponen controles administrativos. |
| **RF-011 / CA-010** | Introducir credenciales válidas autoriza el acceso | **Implementado en Prompt 07** | La verificación válida de usuario y contraseña (Argon2id) emite una sesión firmada y habilita el panel administrativo inicial. |
| **RF-011 / CA-011** | Introducir credenciales incorrectas no autoriza el acceso | **Implementado en Prompt 07** | Usuario o contraseña erróneos o vacíos deniegan el acceso con mensaje uniforme y mantienen la sesión no autenticada. |
| **CA-028** | Verificar exposición de secretos en la interfaz | **Implementado en Prompt 07** | `ocultar_secretos_autenticacion()` y `ConfiguracionAdmin(repr=False)` impiden mostrar contraseñas, hashes o tokens en la UI. |
| **CA-029** | Verificar secretos en código y documentación pública | **Implementado en Prompt 07** | No existen contraseñas reales, cuentas por defecto, tokens ni `.streamlit/secrets.toml` en el repositorio. |
| **CA-059** | Inspeccionar configuración de credenciales: las contraseñas no están en texto plano | **Implementado en Prompt 07** | `es_hash_contrasena_valido()` exige formato PHC `$argon2id$` y rechaza texto plano o hashes rápidos. |
| **CA-027** | Intentar modificar sin autorización: operación denegada | **Implementado parcialmente** | `requerir_autorizacion_admin()` deniega en Python cualquier acceso sin sesión verificada; la aplicación sobre escrituras de inventario se completará en el Prompt 09. |
| **CA-030** | Probar controles administrativos de sesión | **Implementado parcialmente** | Implementados inicio de sesión, estado autenticado firmado por sesión, aislamiento entre sesiones y Logout; la expiración (15 min), advertencia (13 min) y renovación quedan para el Prompt 08. |
| **RF-013 / CA-019 / CA-058** | Restricción de administración móvil en interfaz y operaciones | **Implementado parcialmente** | Se rechaza en Python cuando se detecta contexto móvil (`Sec-CH-UA-Mobile` / `User-Agent` / estado) y se advierte en CSS móvil (`<= 820px`), documentando que los encabezados HTTP pueden ser falsificados por un cliente y que las operaciones de modificación corresponden al Prompt 09. |
| **CA-052, CA-053** | Cinco intentos fallidos consecutivos y bloqueos progresivos (5, 10, 20 y 30 min) | **Pendiente de Prompt 08** | Contratos declarados en `ContratoExtensionPrompt08` (`CONTROLES_AVANZADOS_P08_ACTIVOS = False`); se implementarán en el Prompt 08. |
| **CA-054, CA-055, CA-056, CA-057** | Advertencia a los 13 min, expiración a los 15 min, «Continuar sesión» y retención temporal de borradores | **Pendiente de Prompt 08** | `EstadoSesionAdmin` ya registra `autenticado_en_epoch` y `ultima_actividad_epoch`; la lógica de temporización y borradores corresponde al Prompt 08. |
| **RF-014..RF-021 / CA-012..CA-018, CA-044..CA-046** | Creación y edición de productos, asignación/retiro de ubicaciones y guardado en GitHub | **Pendiente de Prompt 09 o posterior** | No existen formularios de CRUD ni escrituras remotas en esta etapa. |

---

## 2. Parte A — Objetivo y Alcance

### 2.1. Funciones implementadas en el Prompt 07
- **Módulo dedicado `03_Aplicacion/autenticacion.py`:** Gestión de la única cuenta administrativa de FerreteríaMS v0 sin registro público de usuarios, sin múltiples roles y sin dependencia de proveedores externos.
- **Configuración segura de credenciales:** Lectura desde variables de entorno (`FERRETERIAMS_ADMIN_USER`, `FERRETERIAMS_ADMIN_PASSWORD_HASH`) o `st.secrets` (`[admin]`). Si las credenciales no están configuradas o el hash es inválido, el acceso administrativo permanece deshabilitado de forma segura mientras la búsqueda pública continúa operando normalmente.
- **Verificación de contraseña con Argon2id:** Generación y validación de hashes mediante `argon2-cffi`, rechazando contraseñas en texto plano o algoritmos rápidos inseguros.
- **Integración de Login/Logout en `03_Aplicacion/app.py`:** Navegación entre `🏠 Inicio` y `📦 Productos`, formulario de inicio de sesión, validación de autorización en Python, panel administrativo inicial informativo y cierre de sesión con revocación en servidor.

### 2.2. Responsabilidades reservadas para el Prompt 08 y etapas posteriores
- **Reservado para el Prompt 08:** Política de cinco intentos fallidos consecutivos, bloqueos progresivos de 5, 10, 20 y 30 minutos, reinicio de contador tras login exitoso, expiración de sesión tras 15 minutos de inactividad, advertencia dos minutos antes (minuto 13), botón «Continuar sesión» y conservación temporal de borradores durante 15 minutos adicionales.
- **Reservado para el Prompt 09 y posteriores:** Formularios de creación y edición de productos, asignación y retiro de ubicaciones físicas y persistencia de cambios mediante GitHub API.

---

## 3. Parte B — Arquitectura

1. **Separación entre seguridad (`autenticacion.py`) e interfaz (`app.py`):**
   - `03_Aplicacion/autenticacion.py` concentra toda la lógica criptográfica, validación de configuración, emisión y revocación de sesiones y guardas de autorización. Ninguna de sus funciones requiere iniciar un servidor Streamlit para ser probada unitariamente.
   - `03_Aplicacion/app.py` consume los contratos públicos de `autenticacion.py` (`obtener_configuracion_admin`, `esta_autenticado_en_sesion`, `iniciar_sesion_admin`, `cerrar_sesion_admin`, `requerir_autorizacion_admin`) sin manipular directamente hashes ni firmas.
2. **Protección contra falsificación de estado en sesión:**
   - A diferencia de un marcador booleano simple en `st.session_state`, cada autenticación exitosa genera un `token_sesion` aleatorio de 256 bits (`secrets.token_urlsafe(32)`), lo registra en el almacén en memoria del proceso `_SESIONES_ACTIVAS_SERVIDOR` y calcula una firma `HMAC-SHA256` con `_CLAVE_FIRMA_SESION_PROCESO`.
   - Si un control público o código externo inyecta `st.session_state["admin"] = True` o un `EstadoSesionAdmin` sin firma válida ni registro activo en el servidor, `esta_autenticado_en_sesion()` devuelve `False` y `requerir_autorizacion_admin()` lanza `ErrorAutorizacionAdmin`.
3. **Preparación para el Prompt 08 (Sección 10):**
   - `EstadoSesionAdmin` incorpora desde ahora `autenticado_en_epoch` y `ultima_actividad_epoch`.
   - `ResultadoAutenticacion` incluye los campos opcionales `intentos_fallidos_acumulados` y `bloqueado_hasta_epoch`.
   - El diseño de `_SESIONES_ACTIVAS_SERVIDOR` a nivel de módulo/proceso (fuera de `st.session_state`) establece la base técnica para que en el Prompt 08 los contadores de intentos fallidos y bloqueos progresivos se compartan entre sesiones del servidor y no puedan eludirse abriendo una nueva pestaña del navegador.

---

## 4. Parte C — Credenciales y Hashing

- **Algoritmo seleccionado:** **Argon2id** (`argon2.Type.ID`), ganador de la Password Hashing Competition y recomendado por OWASP como estándar principal para almacenamiento de contraseñas.
- **Dependencia incorporada en `requirements.txt`:** `argon2-cffi>=23.1.0` (instalada y verificada en versión `25.1.0`).
- **Parámetros configurados:** `time_cost=2`, `memory_cost=19456` KiB (~19 MiB), `parallelism=1`, `salt_len=16` bytes, `hash_len=32` bytes.
- **Validación estricta del hash almacenado:** `es_hash_contrasena_valido()` comprueba que la cadena comience con `$argon2id$`, posea las 6 secciones del formato PHC y pueda analizarse con `argon2.extract_parameters()`. Si un administrador configura por error una contraseña en texto plano o un hash SHA-256/MD5, el módulo clasifica el estado como `EstadoConfiguracionAdmin.CONFIGURACION_INVALIDA` y mantiene deshabilitado el inicio de sesión.
- **Tratamiento de errores y protección de secretos:**
  - `ConfiguracionAdmin` oculta `password_hash` en `__repr__` y `__str__` reemplazándolo por `[SECRETO_PROTEGIDO]`.
  - `ocultar_secretos_autenticacion()` filtra cualquier patrón `$argon2...$`, asignaciones `password=...` o tokens antes de presentar mensajes en la interfaz.

---

## 5. Parte D — Interfaz Administrativa

1. **Navegación superior (`🏠 Inicio` / `📦 Productos`):**
   - En el encabezado de `03_Aplicacion/app.py` se presentan los botones de navegación `🏠 Inicio` (vista pública activa por defecto) y `📦 Productos` (acceso administrativo, coherente con `RF-012` y las imágenes conceptuales `image1.png`, `image4.png` e `image5.png`).
2. **Vista de Login cuando la sesión no está autenticada (`CA-009`):**
   - Muestra la tarjeta de **Acceso de administración**, los campos `Usuario administrativo` y `Contraseña administrativa` (`type="password"`), el botón primario `🔐 Iniciar sesión` y el botón `🏠 Volver al buscador público`.
   - Si las credenciales no están configuradas en el servidor, presenta un aviso claro (`MENSAJE_ADMIN_NO_CONFIGURADO`) e impide cualquier acceso por defecto.
3. **Vista administrativa inicial tras autenticación válida (`CA-010`):**
   - Tras verificar la sesión con `requerir_autorizacion_admin()`, muestra el encabezado `📦 Productos — Panel administrativo`, el identificador de la cuenta administrativa autenticada, el botón `🚪 Cerrar sesión (Logout)` y el mensaje informativo de que las operaciones de mantenimiento de inventario se implementarán en el Prompt 09 y los controles avanzados de sesión/bloqueo en el Prompt 08.

---

## 6. Parte E — Pruebas Ejecutadas y Evidencias

### 6.1. Ejecución de pruebas automatizadas y regresión (Secciones 11.1 a 11.3 y Corrección Puntual)
- **Comando ejecutado:**
  `python -m unittest discover -s 04_Pruebas -p "test_*.py" -v`
- **Resultado real obtenido:**
  - **Total de pruebas ejecutadas:** **132 pruebas** en `7.287s` (`23` del Prompt 02 + `21` del Prompt 03 + `25` del Prompt 04 + `23` del Prompt 05 + `18` del Prompt 06 + `22` del Prompt 07).
  - **Pruebas aprobadas:** **132 (`OK`)**.
  - **Pruebas fallidas o con error:** **0**.
- **Nuevas pruebas obligatorias añadidas en `04_Pruebas/test_07_autenticacion_administrativa.py`:**
  1. `test_16_intento_de_emitir_sesion_directamente_sin_verificar_credenciales_falla`: Comprueba que llamar a `registrar_autenticacion_en_sesion()` solo con nombre de usuario, sin argumentos o con un comprobante/`ResultadoAutenticacion` falsificado lanza `ErrorAutorizacionAdmin` y no autentica la sesión.
  2. `test_17_credenciales_correctas_permiten_emitir_sesion_una_sola_vez_por_verificacion`: Comprueba que `verificar_credenciales_admin()` con credenciales válidas emite un comprobante legítimo que permite crear una sesión válida y que dicho comprobante es de un solo uso (no reutilizable para una segunda sesión).
  3. `test_18_credenciales_incorrectas_no_permiten_crear_sesion`: Comprueba que credenciales incorrectas no generan comprobante ni permiten emitir sesión.
  4. `test_04_nombre_administrativo_con_caracteres_especiales_no_se_interpreta_como_html`: Comprueba mediante análisis AST de `app.py`, prueba unitaria de `formatear_nombre_usuario_admin_seguro()` y prueba dinámica `AppTest` que un usuario con caracteres HTML/XSS (`admin_<script>alert('xss')</script>&"'`) no se inserta en `unsafe_allow_html=True` ni aparece como etiqueta `<script>` ejecutable.
- **Verificación de ejecución local de Streamlit sin credenciales administrativas:**
  - Se inició `python -m streamlit run 03_Aplicacion/app.py --server.headless true --server.port 8520` habiendo limpiado previamente las variables `FERRETERIAMS_ADMIN_*`. El servidor respondió `ok` en `/_stcore/health` y `HTTP 200 OK` (`6463` bytes) en `/`.

### 6.2. Tabla oficial de verificaciones (Sección 15.E del Prompt 07)

| Verificación | Resultado | Evidencia |
|---|---|---|
| Configuración segura | **APROBADO** | `test_01_configuracion_administrativa_valida`, `test_02_configuracion_inexistente_o_invalida_deshabilita_acceso` y `test_09_ausencia_de_contrasenas_en_texto_plano_dentro_del_repositorio` (`ok`) |
| Hash y verificación | **APROBADO** | `test_08_hash_y_verificacion_mediante_argon2id` (`ok`, Argon2id `$argon2id$v=19$`, sal aleatoria única y rechazo de texto plano/SHA-256) |
| Login válido | **APROBADO** | `test_03_contrasena_correcta_autoriza_acceso`, `test_17_credenciales_correctas_permiten_emitir_sesion_una_sola_vez_por_verificacion` y `test_03_autenticacion_correcta_habilita_seccion_inicial_y_logout_revoca_acceso` (`ok`) |
| Login inválido | **APROBADO** | `test_04_contrasena_incorrecta_deniega_acceso`, `test_05_usuario_incorrecto_deniega_acceso_sin_enumeracion`, `test_06_usuario_vacio_es_rechazado`, `test_07_contrasena_vacia_es_rechazada`, `test_18_credenciales_incorrectas_no_permiten_crear_sesion` y `test_02_formulario_login_aparece_en_productos_y_rechaza_credenciales_incorrectas` (`ok`) |
| Acceso sin autenticación / Emisión directa bloqueada | **APROBADO** | `test_11_acceso_administrativo_denegado_cuando_no_hay_autenticacion`, `test_14_imposibilidad_de_convertir_marcador_publico_en_autorizacion_sin_verificacion` y `test_16_intento_de_emitir_sesion_directamente_sin_verificar_credenciales_falla` (`ok`) |
| Logout | **APROBADO** | `test_12_cierre_de_sesion_revoca_autorizacion_e_impide_reutilizar_token` y `test_03_autenticacion_correcta_habilita_seccion_inicial_y_logout_revoca_acceso` (`ok`) |
| Aislamiento entre sesiones | **APROBADO** | `test_13_aislamiento_entre_dos_sesiones_independientes` (`ok`) |
| Presentación segura del usuario (anti-XSS/HTML) | **APROBADO** | `test_04_nombre_administrativo_con_caracteres_especiales_no_se_interpreta_como_html` (`ok`) |
| Funcionamiento público sin login | **APROBADO** | `test_01_aplicacion_publica_inicia_y_busca_sin_credenciales_administrativas` (`ok`) + arranque real de Streamlit en puerto `8520` (`HTTP 200 OK`) |
| Restricción de acceso desde escritorio | **IMPLEMENTADO PARCIALMENTE (Con limitación técnica documentada)** | `test_15_restriccion_de_contexto_movil_y_contratos_preparados_para_prompt_08` (`ok`) + aviso CSS `@media (max-width: 820px)`. Se documenta que sin mecanismos adicionales fuera del alcance actual, los encabezados HTTP pueden ser modificados por el cliente, por lo que la autenticación Argon2id en Python es obligatoria siempre |
| Ausencia de operaciones administrativas activas | **APROBADO** | `test_03_autenticacion_correcta_habilita_seccion_inicial_y_logout_revoca_acceso` (`ok`, 0 campos de formulario CRUD en la vista autenticada) |
| Regresión Prompts 02–06 | **APROBADO (110 / 110 OK + 22 de P07 = 132 / 132 OK)** | `test_02_motor_inventario.py` (`23 OK`), `test_03_lectura_github.py` (`21 OK`), `test_04_busqueda_publica.py` (`25 OK`), `test_05_detalles_ubicaciones.py` (`23 OK`), `test_06_interfaz_responsive_gemini.py` (`18 OK`) y `test_07_autenticacion_administrativa.py` (`22 OK`) |

---

## 7. Parte F — Restricciones, Limitaciones de Seguridad y Pendientes

> **Advertencia expresa de alcance (Sección 11.4 del Prompt 07):**  
> La aplicación **no está lista todavía para administrar datos reales en producción** hasta que se integren y validen en el **Prompt 08** las protecciones contra fuerza bruta (bloqueos progresivos) y expiración de sesiones por inactividad.

1. **Controles de seguridad pendientes para el Prompt 08 (`CA-030` completo, `CA-052` a `CA-057`):**
   - Conteo de cinco intentos fallidos consecutivos y aplicación de bloqueos progresivos de `5, 10, 20 y 30` minutos en almacenamiento compartido de servidor.
   - Expiración automática de la sesión administrativa tras `15` minutos de inactividad, advertencia previa a los `13` minutos y renovación mediante el botón «Continuar sesión».
   - Conservación temporal durante `15` minutos adicionales de borradores no guardados cuando expire la sesión y recuperación tras reautenticación.
2. **Funciones operativas de mantenimiento pendientes para el Prompt 09 (`RF-014` a `RF-021`, `RF-026`, `RF-027`, `CA-012` a `CA-026`, `CA-044` a `CA-051`):**
   - Formularios administrativos para crear y editar productos, seleccionar categorías predefinidas, asignar/retirar ubicaciones conservando una única ubicación principal y guardar cambios en `03_Aplicacion/inventario.xlsx` mediante GitHub API con control de conflictos SHA.
3. **Limitación técnica sobre identificación de dispositivo móvil (`RF-013`, `CA-019`, `CA-058`):**
   - En la arquitectura actual de Streamlit sin JavaScript invasivo ni servicios externos, la detección de dispositivo en servidor mediante encabezados HTTP (`Sec-CH-UA-Mobile`, `User-Agent`) y las reglas CSS responsive impiden el uso administrativo accidental desde teléfonos, pero no constituyen una prueba criptográfica ineludible frente a un cliente que falsifique encabezados HTTP. Por ello, todas las operaciones administrativas exigen verificación de sesión autenticada en Python.

### Estado Git al finalizar (`git status --short`)
```text
 M 03_Aplicacion/app.py
 M 03_Aplicacion/estilos.css
 M requirements.txt
?? 03_Aplicacion/autenticacion.py
?? 04_Pruebas/test_07_autenticacion_administrativa.py
?? 05_Resultados/07_Resultado_Autenticacion_Administrativa.md
```

---

## 8. Parte G — Evaluación

- **Estado:** **COMPLETADO**
- **Justificación con evidencias:**
  1. Se implementó el módulo independiente `03_Aplicacion/autenticacion.py` con soporte para la única cuenta administrativa de FerreteríaMS v0, verificación de contraseñas mediante **Argon2id** (`argon2-cffi`), resistencia a enumeración de usuarios y estado de sesión firmado con `HMAC-SHA256` y registrado en memoria del servidor.
  2. Se integraron en `03_Aplicacion/app.py` y `03_Aplicacion/estilos.css` la sección `📦 Productos`, el formulario `Login`, la vista administrativa inicial protegida en Python y la función `Logout`, sin incluir credenciales por defecto ni formularios de mantenimiento de inventario.
  3. Se conservaron intactos `inventario.py`, `github_inventario.py`, `busqueda.py`, los documentos oficiales y los prompts existentes, y se verificó el cumplimiento mediante **132 pruebas automatizadas aprobadas (`132 OK`)** y el arranque local de Streamlit sin credenciales configuradas.

