# Informe de Resultados — FERMS-V0-P03: Lectura del inventario desde GitHub API (con corrección puntual de seguridad)

**Proyecto:** FerreteríaMS v0  
**Identificador de la tarea:** `FERMS-V0-P03`  
**Título de la tarea:** Integración de lectura del inventario maestro desde GitHub API y endurecimiento de seguridad de transporte/descarga  
**Fecha y hora de ejecución inicial:** 2026-10-19 23:58:15 -04:00 a 2026-10-20 00:06:00 -04:00  
**Fecha y hora de corrección puntual de seguridad:** 2026-10-20 00:13:00 -04:00 a 2026-10-20 00:25:30 -04:00  
**Agente de desarrollo:** Gemini (Antigravity)  
**Repositorio:** `JunyMSAI/FerreteriaMS`  
**Rama local y remota consultada:** `main`  
**Referencia de commit base (`HEAD`):** `ca9191d` (`Prompt "03_Lectura_GitHub" incluido`)  
**Commit nuevo generado en esta tarea:** Ninguno (por instrucción expresa del usuario y del Prompt 03)

---

## 1. Trazabilidad del Prompt y Solicitudes Originales

### 1.1. Referencia al prompt oficial
- **Archivo de prompt:** `02_Prompts/03_Lectura_GitHub.md` (preservado íntegro y sin modificaciones).

### 1.2. Solicitud original de la tarea FERMS-V0-P03
> Ejecuta la tarea **FERMS-V0-P03** de FerreteríaMS v0.
>
> Lee íntegramente `02_Prompts/03_Lectura_GitHub.md` y cumple exclusivamente sus instrucciones aprobadas.
>
> Antes de comenzar, consulta `GEMINI.md`, `AGENTS.md`, `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx` y `01_Documentacion/02_Especificaciones_v0.md`.
>
> Autorizo únicamente las modificaciones locales expresamente permitidas en el Prompt 03 y las consultas de **solo lectura a GitHub API**.
>
> No modifiques `03_Aplicacion/app.py`, `03_Aplicacion/inventario.py`, los documentos aprobados ni los prompts existentes.
>
> No crees ni modifiques `03_Aplicacion/inventario.xlsx`. No ejecutes escrituras remotas, commits, push, merge ni despliegues.
>
> Ejecuta las pruebas correspondientes, verifica que no haya regresiones del Prompt 02 y registra los resultados en `05_Resultados/03_Resultado_Lectura_GitHub.md`.
>
> Al terminar, presenta el informe completo, distingue las pruebas simuladas de las consultas reales y espera mi autorización antes de comenzar el Prompt 04.

### 1.3. Solicitud de corrección puntual de seguridad (FERMS-V0-P03)
> Realiza una corrección puntual de seguridad de la tarea **FERMS-V0-P03**.
>
> En `03_Aplicacion/github_inventario.py`, revisa el transporte HTTP y el tratamiento de `download_url`.
>
> **Problemas detectados:**
> 1. `ejecutar_solicitud_get_github()` admite HTTP no cifrado.
> 2. La descarga mediante `download_url` puede enviar el token de GitHub a un destino que no haya sido validado.
>
> **Cambios autorizados:**
> - Exigir HTTPS para todas las solicitudes.
> - Validar el dominio y destino de las solicitudes a GitHub API.
> - Impedir que tokens de autorización se envíen a dominios externos o URLs de descarga no confiables.
> - Controlar las redirecciones para impedir filtraciones de credenciales.
> - Mantener las funcionalidades existentes de consulta, descarga, SHA y validación Excel.
> - Añadir pruebas automatizadas para HTTP no cifrado, URLs externas, redirecciones y protección del token.
> - Ejecutar toda la suite de pruebas, incluyendo las 23 del Prompt 02 y las 17 originales del Prompt 03.
> - Actualizar `05_Resultados/03_Resultado_Lectura_GitHub.md` con los cambios y sus evidencias.
>
> Antes de modificar, consulta `GEMINI.md`, `AGENTS.md` y `02_Especificaciones_v0.md`.
>
> **Restricciones:** no modifiques documentos oficiales, `app.py`, `inventario.py` ni el inventario maestro. No realices escrituras remotas, commits, push, merge o despliegues.
>
> Entrega los resultados, distingue las pruebas ejecutadas de las pendientes y espera autorización.

### 1.4. Interpretación del agente vs. decisiones técnicas de implementación
- **Contenido procedente de la solicitud y documentación aprobada:**
  - Desarrollar un módulo de solo lectura de GitHub API en `03_Aplicacion/` que consulte `03_Aplicacion/inventario.xlsx` en el repositorio `JunyMSAI/FerreteriaMS` (rama `main`).
  - Exigir HTTPS cifrado para todas las solicitudes HTTP y rechazar cualquier URL con esquema `http` u otros esquemas.
  - Validar el dominio y la ruta de destino en todas las solicitudes a GitHub API y en las descargas por `download_url`.
  - Impedir que el encabezado `Authorization` se envíe a dominios externos, a `raw.githubusercontent.com` o a URLs de descarga no confiables.
  - Controlar las redirecciones HTTP para bloquear degradaciones a HTTP, redirecciones hacia dominios no autorizados y cualquier redirección que pudiera filtrar credenciales de autorización.
  - Conservar íntegras las funcionalidades de consulta de existencia (`EXISTE`, `NO_EXISTE`, `DESCONOCIDO_ERROR`), obtención de `sha_github`, descarga y validación de las cuatro hojas con `cargar_inventario_excel()` de `03_Aplicacion/inventario.py`.
- **Decisiones técnicas tomadas por el agente para la implementación y el endurecimiento de seguridad:**
  - Se definieron listas blancas explícitas de dominios oficiales en `03_Aplicacion/github_inventario.py`:
    - `DOMINIOS_API_GITHUB_PERMITIDOS = ("api.github.com",)`
    - `DOMINIOS_DESCARGA_GITHUB_PERMITIDOS = ("raw.githubusercontent.com", "api.github.com")`
    - `DOMINIOS_REDIRECCION_GITHUB_PERMITIDOS = ("api.github.com", "raw.githubusercontent.com", "objects.githubusercontent.com")`
  - Se implementó `validar_url_solicitud_github(...)` y `validar_url_descarga_github(...)`, verificando en todas las solicitudes:
    1. Esquema estrictamente igual a `https`.
    2. Ausencia de credenciales incrustadas (`username` / `password`) y puerto restringido a `None` o `443`.
    3. Pertenencia del `hostname` a la lista blanca correspondiente.
    4. Ausencia de caracteres de control, barras invertidas (`\`) o segmentos de recorrido de directorios (`..`) tanto en la ruta cruda como en la ruta decodificada.
    5. Coincidencia obligatoria del destino con `/repos/{propietario}/{repositorio}` en `api.github.com` y con `/{propietario}/{repositorio}/{ref}/{ruta_archivo}` en `raw.githubusercontent.com`.
    6. Bloqueo inmediato si existe encabezado `Authorization` y el host de destino no es `api.github.com`.
  - En `_extraer_bytes_archivo_github(...)`, cuando se utiliza `download_url`, primero se valida con `validar_url_descarga_github(...)` y las descargas hacia `raw.githubusercontent.com` se ejecutan siempre con `token=None` (sin encabezado `Authorization`), garantizando que el token de GitHub API jamás salga de `api.github.com`.
  - Se implementó `_ManejadorRedireccionSeguraGitHub(urllib.request.HTTPRedirectHandler)` con límite máximo de `MAX_REDIRECCIONES_GITHUB = 3`, bloqueando cualquier redirección hacia HTTP no cifrado, hacia dominios externos o en solicitudes que porten encabezado `Authorization`, y eliminando encabezados sensibles (`Authorization`, `Cookie`, `Host`) en redirecciones públicas permitidas hacia `objects.githubusercontent.com`.

---

## 2. Implementación del Módulo `03_Aplicacion/github_inventario.py`

### 2.1. Separación de responsabilidades y controles de seguridad
1. **Configuración centralizada (`ConfiguracionRepositorioGitHub` y `CONFIGURACION_POR_DEFECTO`):**
   - Parámetros por defecto: propietario `JunyMSAI`, repositorio `FerreteriaMS`, rama `main`, ruta `03_Aplicacion/inventario.xlsx`, API base `https://api.github.com`.
2. **Validación de transporte, dominio, destino y redirecciones (`validar_url_solicitud_github`, `validar_url_descarga_github`, `_ManejadorRedireccionSeguraGitHub`, `ejecutar_solicitud_get_github`):**
   - Exige `https` y método `GET` exclusivamente.
   - Valida dominio y ruta de repositorio/archivo antes de emitir cualquier solicitud (tanto con el transporte real como con un `ejecutor_http` inyectado).
   - Impide enviar `Authorization` fuera de `api.github.com` y bloquea redirecciones en solicitudes autenticadas o hacia destinos no confiables.
3. **Gestión segura de credenciales opcionales (`obtener_token_configurado`, `ocultar_secretos_en_texto`):**
   - Enmascara cualquier secreto como `[SECRETO_PROTEGIDO]` en todos los mensajes de error (`CA-028`, `CA-029`).
4. **Consulta de existencia (`consultar_existencia_inventario_remoto` -> `ResultadoExistenciaRemota`):**
   - Devuelve `EstadoExistenciaRemota.EXISTE`, `EstadoExistenciaRemota.NO_EXISTE` o `EstadoExistenciaRemota.DESCONOCIDO_ERROR`.
   - Verifica en tres pasos (`_diagnosticar_404_contenido`) cualquier `404` antes de confirmar `NO_EXISTE`.
5. **Descarga, identificación de versión y validación (`descargar_inventario_remoto` -> `ResultadoLecturaInventarioRemoto`):**
   - Verifica metadatos (`type == "file"`, `path`, `sha` y `size`), obtiene el contenido binario por base64 o `download_url` validado sin exponer el token, y valida las 4 hojas con `cargar_inventario_excel()` de `03_Aplicacion/inventario.py`.
6. **Integración con inicialización segura (`preparar_inicializacion_desde_consulta_remota`):**
   - Conecta `consultar_existencia_inventario_remoto()` con `preparar_inicializacion_segura()` de `03_Aplicacion/inventario.py`.

### 2.2. Cobertura de los 13 escenarios de error (Sección 7 del Prompt 03)

| # | Escenario exigido | Código (`CodigoErrorGitHub`) | Excepción específica | Categoría para interfaz (`CategoriaResultadoConsulta`) |
|---|---|---|---|---|
| 1 | Archivo remoto confirmado como inexistente | `ARCHIVO_REMOTO_INEXISTENTE` | `ErrorArchivoRemotoInexistente` | `INVENTARIO_NO_INICIALIZADO` |
| 2 | Repositorio inaccesible | `REPOSITORIO_INACCESIBLE` | `ErrorRepositorioInaccesible` | `ERROR_CONSULTA_INVENTARIO` |
| 3 | Rama inexistente o inaccesible | `RAMA_INEXISTENTE` | `ErrorRamaInexistente` | `ERROR_CONSULTA_INVENTARIO` |
| 4 | Acceso denegado | `ACCESO_DENEGADO` | `ErrorAccesoDenegadoGitHub` | `ERROR_CONSULTA_INVENTARIO` |
| 5 | Credencial inválida o insuficiente | `CREDENCIAL_INVALIDA` | `ErrorCredencialInvalidaGitHub` | `ERROR_CONSULTA_INVENTARIO` |
| 6 | Límite de solicitudes de GitHub API | `LIMITE_SOLICITUDES` | `ErrorLimiteSolicitudesGitHub` | `ERROR_CONSULTA_INVENTARIO` |
| 7 | Error temporal del servidor | `ERROR_SERVIDOR` | `ErrorServidorGitHub` | `ERROR_CONSULTA_INVENTARIO` |
| 8 | Tiempo de espera agotado | `TIEMPO_ESPERA_AGOTADO` | `ErrorTiempoEsperaGitHub` | `ERROR_CONSULTA_INVENTARIO` |
| 9 | Conexión de red fallida | `CONEXION_RED_FALLIDA` | `ErrorConexionRedGitHub` | `ERROR_CONSULTA_INVENTARIO` |
| 10 | Respuesta de API con formato inesperado (incluye rechazo de HTTP, dominios externos y redirecciones inseguras) | `RESPUESTA_INESPERADA` | `ErrorRespuestaInesperadaGitHub` | `ERROR_CONSULTA_INVENTARIO` |
| 11 | Contenido binario inválido | `CONTENIDO_BINARIO_INVALIDO` | `ErrorContenidoBinarioInvalido` | `ERROR_CONSULTA_INVENTARIO` |
| 12 | Archivo Excel corrupto | `ARCHIVO_EXCEL_CORRUPTO` | `ErrorArchivoExcelRemotoCorrupto` | `DATOS_REMOTOS_INVALIDOS` |
| 13 | Inventario que incumple el esquema aprobado | `ESQUEMA_INVENTARIO_INVALIDO` | `ErrorEsquemaInventarioRemoto` | `DATOS_REMOTOS_INVALIDOS` |

---

## 3. Distinción entre Pruebas Simuladas (Mocks), Consulta Real Ejecutada y Pruebas Pendientes

### 3.1. Pruebas automatizadas simuladas (Mocks)
- **Archivos de prueba:**
  - `04_Pruebas/test_02_motor_inventario.py`: **23 pruebas** de regresión del Prompt 02.
  - `04_Pruebas/test_03_lectura_github.py`: **21 pruebas** del Prompt 03 (**17 originales + 4 nuevas de seguridad** sobre transporte HTTPS, URLs externas/destinos, redirecciones y protección del token).
- **Ejecución completa de la suite:**
  - Comando: `python -m unittest discover -s 04_Pruebas -p "test_*.py" -v`
  - Resultado: **44 pruebas ejecutadas en `0.505s` — 44 OK (23 del Prompt 02 + 21 del Prompt 03, 0 fallos, 0 errores)**.

#### Detalle de las 21 pruebas simuladas de `test_03_lectura_github.py`

| # | Prueba automatizada (simulada) | Categoría / RF / CA | Resultado | Evidencia |
|---|---|---|---|---|
| 1 | `test_configuracion_repositorio_y_rama_por_defecto` | Original P03 / RF-025, RF-028 | **APROBADO (Simulado)** | Verifica `JunyMSAI/FerreteriaMS`, rama `main`, ruta `03_Aplicacion/inventario.xlsx` y encabezados anti-caché (`ok`) |
| 2 | `test_consulta_archivo_existente` | Original P03 / RF-025, CA-025 parcial | **APROBADO (Simulado)** | Devuelve `EXISTE`, obtiene `sha_github` y tamaño (`ok`) |
| 3 | `test_consulta_archivo_inexistente_confirmado` | Original P03 / RF-029, CA-020 parcial | **APROBADO (Simulado)** | Comprueba `404` en archivo + `200` en repo + `200` en rama -> `NO_EXISTE` (`ok`) |
| 4 | `test_consulta_404_por_repositorio_inaccesible_no_declara_no_existe` | Original P03 / RF-030, RF-038 | **APROBADO (Simulado)** | `404` en repositorio produce `DESCONOCIDO_ERROR` (`REPOSITORIO_INACCESIBLE`), nunca `NO_EXISTE` (`ok`) |
| 5 | `test_consulta_404_por_rama_inexistente_no_declara_no_existe` | Original P03 / RF-030, RF-038 | **APROBADO (Simulado)** | `404` en rama produce `DESCONOCIDO_ERROR` (`RAMA_INEXISTENTE`), nunca `NO_EXISTE` (`ok`) |
| 6 | `test_error_autenticacion_401_y_credencial_invalida` | Original P03 / RF-038, CA-028, CA-042 | **APROBADO (Simulado)** | Detecta `401` (`CREDENCIAL_INVALIDA`) y oculta tokens con `[SECRETO_PROTEGIDO]` (`ok`) |
| 7 | `test_error_permisos_403_acceso_denegado_y_permiso_insuficiente` | Original P03 / RF-038, CA-042 | **APROBADO (Simulado)** | Diferencia `403` por acceso denegado (`ACCESO_DENEGADO`) y `403` por token sin permisos (`CREDENCIAL_INVALIDA`) (`ok`) |
| 8 | `test_error_limite_solicitudes_rate_limit` | Original P03 / RF-038, CA-042 | **APROBADO (Simulado)** | Detecta `429` y `403` con `X-RateLimit-Remaining: 0` (`LIMITE_SOLICITUDES`) (`ok`) |
| 9 | `test_error_servidor_5xx` | Original P03 / RF-038, CA-042 | **APROBADO (Simulado)** | Detecta errores HTTP `500`, `502`, `503` y `504` (`ERROR_SERVIDOR`) (`ok`) |
| 10 | `test_error_timeout_y_error_conexion_red` | Original P03 / RF-038, CA-042 | **APROBADO (Simulado)** | Diferencia `socket.timeout` (`TIEMPO_ESPERA_AGOTADO`) y `URLError` de red (`CONEXION_RED_FALLIDA`) (`ok`) |
| 11 | `test_respuesta_inesperada_de_github_api` | Original P03 / RF-038 | **APROBADO (Simulado)** | Rechaza HTML/JSON corrupto, listas o respuestas sin `sha` (`RESPUESTA_INESPERADA`) (`ok`) |
| 12 | `test_descarga_exitosa_sha_cuatro_hojas_y_ceros_iniciales` | Original P03 / RF-022, RF-023, RF-024, RF-027, CA-022, CA-025 parcial | **APROBADO (Simulado)** | Descarga Excel en memoria, distingue `sha_github` de `sha256_local`, valida las 4 hojas y preserva `"000125"` como texto sin escribir en disco (`ok`) |
| 13 | `test_deteccion_contenido_binario_invalido` | Original P03 / RF-038 | **APROBADO (Simulado)** | Rechaza base64 inválido o tamaño inconsistente con `size` (`CONTENIDO_BINARIO_INVALIDO`) (`ok`) |
| 14 | `test_deteccion_excel_remoto_corrupto_e_invalido` | Original P03 / RF-023, CA-022, CA-047 | **APROBADO (Simulado)** | Diferencia Excel corrupto (`ARCHIVO_EXCEL_CORRUPTO`) e incumplimiento de esquema/integridad (`ESQUEMA_INVENTARIO_INVALIDO`) (`ok`) |
| 15 | `test_estado_existe_impide_inicializacion` | Original P03 / RF-030, CA-021 parcial | **APROBADO (Simulado)** | Cuando la consulta devuelve `EXISTE`, bloquea `preparar_inicializacion_segura` (`ok`) |
| 16 | `test_fallos_api_dan_desconocido_error_y_bloquean_inicializacion` | Original P03 / RF-029, RF-030, CA-020 parcial, CA-021 parcial | **APROBADO (Simulado)** | Fallos `503`, `401`, `403`, repo `404` y rama `404` producen `DESCONOCIDO_ERROR` y bloquean la inicialización (`ok`) |
| 17 | `test_estado_no_existe_confirmado_prepara_bytes_en_memoria_sin_escribir_disco` | Original P03 / RF-029, CA-020 parcial | **APROBADO (Simulado)** | Con `NO_EXISTE` confirmado genera los bytes demostrativos en memoria sin crear `inventario.xlsx` (`ok`) |
| 18 | `test_rechazo_http_no_cifrado_en_solicitudes_y_download_url` | **Seguridad P03** / CA-028, CA-042 | **APROBADO (Simulado)** | Rechaza `http://` en `ejecutar_solicitud_get_github`, en `url_base_api` y en `download_url` antes de abrir conexión (`ok`) |
| 19 | `test_rechazo_dominios_externos_y_destinos_no_validos` | **Seguridad P03** / CA-028, CA-042 | **APROBADO (Simulado)** | Rechaza dominios externos, credenciales en URL, puertos no estándar, `..` y `download_url` hacia otros repositorios/archivos (`ok`) |
| 20 | `test_proteccion_token_en_download_url_y_bloqueo_fuera_de_api_github` | **Seguridad P03** / CA-028, CA-029 | **APROBADO (Simulado)** | Verifica que `download_url` en `raw.githubusercontent.com` funcione sin enviar `Authorization` y que se bloquee cualquier envío de token fuera de `api.github.com` (`ok`) |
| 21 | `test_control_redirecciones_bloquea_http_dominios_externos_y_fuga_de_credenciales` | **Seguridad P03** / CA-028, CA-029 | **APROBADO (Simulado)** | Verifica bloqueo de redirecciones a `http://`, a dominios externos, en solicitudes autenticadas y por exceso de saltos (`ok`) |

### 3.2. Consulta real de solo lectura a GitHub API (Ejecutada)
- **Ejecución realizada tras la corrección de seguridad:** Se invocó `consultar_existencia_inventario_remoto()` contra `https://api.github.com` empleando el nuevo manejador seguro de transporte HTTPS y redirecciones.
- **Resultado real obtenido de GitHub API:**
  - `estado`: `NO_EXISTE`
  - `categoria_consulta`: `INVENTARIO_NO_INICIALIZADO`
  - `codigo_error`: `ARCHIVO_REMOTO_INEXISTENTE`
  - `sha_github`: `None`
  - `mensaje`: `"Se confirmó que el archivo maestro '03_Aplicacion/inventario.xlsx' todavía no existe en 'JunyMSAI/FerreteriaMS' (rama 'main')."`

### 3.3. Pruebas pendientes (No ejecutables en esta etapa)
1. **Descarga real del archivo maestro desde GitHub (`CA-022` real en GitHub):** Pendiente porque `03_Aplicacion/inventario.xlsx` todavía no existe en el repositorio remoto `JunyMSAI/FerreteriaMS` y está prohibido crearlo o subirlo durante la tarea `FERMS-V0-P03`.
2. **Consulta de cambios confirmados desde la interfaz sin reiniciar Streamlit (`CA-024`):** Pendiente de desarrollo e integración de la interfaz en los siguientes prompts.
3. **Detección de conflictos de versiones al guardar (`CA-025` completo):** Obtención de `sha_github` verificada; comprobación de escritura y conflicto reservada para el Prompt 10.
4. **Lectura desde la aplicación desplegada en Streamlit Community Cloud (`CA-036`):** Pendiente de la etapa de despliegue.

---

## 4. Archivos Creados o Modificados y Restricciones Respetadas

### 4.1. Archivos creados o actualizados localmente en FERMS-V0-P03
1. `03_Aplicacion/github_inventario.py` — Módulo de lectura de GitHub API endurecido con exigencia de HTTPS, validación de dominio/destino, protección de token en `download_url` y control de redirecciones.
2. `04_Pruebas/test_03_lectura_github.py` — Suite de 21 pruebas automatizadas con mocks (17 originales + 4 de seguridad de transporte, `download_url`, redirecciones y token).
3. `05_Resultados/03_Resultado_Lectura_GitHub.md` — Presente informe actualizado con los cambios de seguridad y sus evidencias.

### 4.2. Confirmación de restricciones y archivos protegidos
- **Documentos oficiales (`GEMINI.md`, `AGENTS.md`, `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`, `01_Documentacion/02_Especificaciones_v0.md`, `README.md`):** Sin cambios.
- **Prompts (`02_Prompts/*`):** Sin cambios.
- **`03_Aplicacion/app.py` y `03_Aplicacion/inventario.py`:** Sin cambios.
- **Archivo maestro `03_Aplicacion/inventario.xlsx`:** No creado ni modificado localmente ni remotamente.
- **Operaciones Git y remotas:** No se realizaron escrituras remotas, `git commit`, `git push`, `git merge` ni despliegues.

### 4.3. Estado actual de Git (`git status --short`)
```text
?? 03_Aplicacion/github_inventario.py
?? 04_Pruebas/test_03_lectura_github.py
?? 05_Resultados/03_Resultado_Lectura_GitHub.md
```

---

## 5. Evaluación Final

- **Estado:** **COMPLETADO**
- **Justificación:** Se aplicaron todas las correcciones de seguridad solicitadas en `03_Aplicacion/github_inventario.py`, se añadieron las 4 pruebas automatizadas de seguridad en `04_Pruebas/test_03_lectura_github.py`, se ejecutó la suite completa superando las **44 pruebas automatizadas (`23` del Prompt 02 + `17` originales del Prompt 03 + `4` nuevas de seguridad = `44 OK`)**, y se revalidó la consulta real de solo lectura contra GitHub API sobre HTTPS.
