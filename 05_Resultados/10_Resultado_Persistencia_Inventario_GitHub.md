# Informe de Resultados — Prompt 10: Persistencia del Inventario Excel con GitHub API y Control de Versiones

**Proyecto:** FerreteríaMS  
**Etapa:** FerreteríaMS v0  
**Identificador de la tarea:** `FERMS-V0-P10`  
**Fecha de ejecución:** 21 de octubre de 2026  
**Título de la tarea:** Persistencia del Inventario Excel con GitHub API y Control de Versiones (incluye correcciones obligatorias post-auditoría)  
**Documento prompt de origen:** `02_Prompts/10_Persistencia_Inventario_GitHub.md`  
**Rama de trabajo:** `main`  
**Último commit funcional previo (P09):** `97f91ce` (`feat(p09): implementar gestion administrativa de productos y ubicaciones`)  
**Commit documental base (P10):** `8ac0b7e` (`docs: registrar cierre del Prompt 09 y prompt 10 de persistencia en GitHub`)  
**Agente de desarrollo:** Gemini  

---

## 1. Solicitud / Prompt Original

### 1.1. Instrucción inicial de ejecución recibida del usuario (conservada íntegramente sin alteraciones)

```markdown
**FERMS-V0-P10 — EJECUCIÓN AUTORIZADA DEL PROMPT 10**

Proyecto: FerreteríaMS v0.

Ejecuta exclusivamente el documento aprobado:

`02_Prompts/10_Persistencia_Inventario_GitHub.md`

Antes de modificar archivos, lee íntegramente `GEMINI.md`, `AGENTS.md`, el documento conceptual, las especificaciones oficiales, el Prompt 09 y su informe de resultados.

### Verificación inicial

- Rama esperada: `main`.
- Último commit funcional P09: `97f91ce`.
- Commit documental actual P10: `8ac0b7e`.
- Verifica que `97f91ce` sea un antecesor del commit actual.
- Confirma que el área de trabajo esté limpia.
- Si encuentras modificaciones inesperadas o contradicciones importantes, detente y solicita autorización.

### Trabajo autorizado

Implementa el mecanismo completo de persistencia del inventario Excel utilizando GitHub Contents API, incluyendo serialización validada, autenticación administrativa, confirmación explícita, control de concurrencia por SHA, manejo de errores e integración con Streamlit.

Prepara el código para que pueda utilizarse después de recibir autorización de activación.

### Restricción crítica

**Esta ejecución NO autoriza escrituras reales en GitHub.**

- No crees ni modifiques `03_Aplicacion/inventario.xlsx`, ni localmente ni en GitHub.
- No ejecutes solicitudes reales de escritura HTTP PUT, POST, PATCH o DELETE.
- Todas las pruebas de escritura deberán utilizar mocks o simulaciones.
- No uses credenciales reales para probar publicaciones.
- No realices ninguna creación inicial real del inventario.
- No publiques datos demostrativos.
- No actives automáticamente una escritura al iniciar la aplicación.
- No avances al Prompt 11.

Respeta estrictamente los archivos autorizados y las decisiones oficiales del proyecto. Si necesitas modificar archivos protegidos o introducir dependencias nuevas, detente y solicita autorización.

### Pruebas y entrega

Ejecuta primero las pruebas del Prompt 10 y después las regresiones P02–P09, individualmente y de forma secuencial, sin paralelismo ni pruebas intensivas.

Documenta los resultados en:

`05_Resultados/10_Resultado_Persistencia_Inventario_GitHub.md`

El informe debe identificar los archivos afectados, las pruebas realizadas, el comportamiento de escritura simulada, los controles de seguridad, los conflictos SHA y las limitaciones pendientes.

Al finalizar, presenta `git status --short`.

**No ejecutes git commit, git push, git merge, git reset, git restore, git clean ni despliegues.**

Detente al terminar y espera mi revisión independiente y aprobación.
```

### 1.2. Instrucción de correcciones obligatorias tras auditoría independiente (conservada íntegramente sin alteraciones)

```markdown
# FERMS-V0-P10 — Correcciones obligatorias tras auditoría independiente

La revisión independiente del Prompt 10 encontró deficiencias de seguridad y trazabilidad que deben corregirse antes de aprobar el commit.

**No ejecutes escrituras reales, commits, push ni despliegues. No crees `inventario.xlsx`.**

## Corrección 1 — Bloqueo de escrituras reales

En `03_Aplicacion/persistencia_github.py`, el parámetro `permitir_red_real=True` puede anular `ESCRITURA_REAL_GITHUB_HABILITADA=False`.

Corrige el mecanismo para que ninguna llamada de producción pueda realizar HTTP PUT real mientras la activación global esté deshabilitada.

No utilices la identificación del módulo de `urllib.request.urlopen` como prueba de que una función es simulada.

Mantén las pruebas con ejecutores falsos inyectados, pero separa claramente el transporte simulado de la capacidad real de escritura. Ningún parámetro público debe permitir saltarse la prohibición global.

Añade pruebas que demuestren que los intentos de anular la compuerta son rechazados.

## Corrección 2 — Publicación accidental de inventario demostrativo

Actualmente, la interfaz puede preparar un inventario demostrativo y ofrece inicializar el archivo maestro a partir de él.

Impide que los productos demostrativos puedan publicarse accidentalmente como inventario real.

Implementa una separación comprobable entre datos de demostración y datos autorizados para la inicialización oficial.

Conserva la posibilidad de realizar pruebas simuladas, pero bloquea la publicación real de datos de prueba. No implementes una activación real durante esta corrección.

## Corrección 3 — Informe de resultados

El informe `05_Resultados/10_Resultado_Persistencia_Inventario_GitHub.md` contiene nombres de funciones, constantes y casos de prueba que no corresponden exactamente al código entregado.

Corrige el informe utilizando los nombres reales del código y las pruebas.

El documento debe distinguir entre:

- Controles implementados.
- Pruebas efectivamente ejecutadas.
- Resultados obtenidos.
- Controles todavía pendientes de verificación.
- Riesgos residuales.

No atribuyas resultados a pruebas que no se ejecutaron.

## Verificación de secretos

Realiza adicionalmente una auditoría estática y pruebas con credenciales ficticias para detectar exposición de tokens, contraseñas, hashes y encabezados de autorización en excepciones, logs, interfaces y representaciones de objetos.

Verifica también los archivos versionados y las exclusiones de secretos, sin revelar ningún valor sensible.

Si detectas un secreto real, detente e informa sin reproducirlo.

## Entrega

Ejecuta las pruebas nuevas de P10 y después las regresiones P02–P09 secuencialmente.

Actualiza exclusivamente los archivos necesarios y el informe P10.

Presenta los resultados exactos y `git status --short`.

No ejecutes `git add`, `git commit`, `git push`, despliegues ni operaciones reales de GitHub Contents API.

Detente al finalizar para una nueva revisión independiente.
```

### 1.3. Referencia al documento oficial del Prompt 10

El texto íntegro del prompt de desarrollo se conserva sin alteraciones en `02_Prompts/10_Persistencia_Inventario_GitHub.md` (commit `8ac0b7e`).

---

## 2. Interpretación del Agente

1. **Verificación inicial y gobernanza:**
   - Se leyeron íntegramente `GEMINI.md`, `AGENTS.md`, `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`, `01_Documentacion/02_Especificaciones_v0.md`, `02_Prompts/09_Gestion_Administrativa_Productos_Ubicaciones.md`, `05_Resultados/09_Resultado_Gestion_Administrativa_Productos_Ubicaciones.md` y `02_Prompts/10_Persistencia_Inventario_GitHub.md`.
   - Se verificó en Git que la rama activa es `main`, que `HEAD` apunta a `8ac0b7e`, que `97f91ce` es antecesor directo de `HEAD` (`git merge-base --is-ancestor 97f91ce HEAD` con código `0`), y que no existen archivos protegidos modificados ni existe `03_Aplicacion/inventario.xlsx`.

2. **Alcance funcional y técnico del Prompt 10 y de las correcciones post-auditoría:**
   - Implementar el motor de persistencia del archivo maestro `03_Aplicacion/inventario.xlsx` hacia GitHub Contents API en `03_Aplicacion/persistencia_github.py`, integrándolo con `03_Aplicacion/administracion_productos.py` y `03_Aplicacion/app.py`.
   - **Corrección 1 (Bloqueo estricto de escrituras reales):** Eliminar cualquier parámetro (`permitir_red_real`) que pudiera anular `ESCRITURA_REAL_GITHUB_HABILITADA = False`, y eliminar cualquier inspección del módulo de `urllib.request.urlopen` (`__module__` o `assert_called`). `ejecutar_solicitud_put_github(solicitud, *, token)` debe lanzar incondicionalmente `ErrorEscrituraRealNoAutorizadaGitHub` mientras `ESCRITURA_REAL_GITHUB_HABILITADA` sea `False`. Las pruebas utilizan exclusivamente el transporte simulado inyectado mediante `ejecutor_http_put` en `publicar_inventario_administrativo_github`, mientras que cuando `ejecutor_http_put` es `None` (ruta de producción) se invoca `ejecutar_solicitud_put_github` y la compuerta global bloquea cualquier intento de salida HTTP real.
   - **Corrección 2 (Bloqueo de publicación accidental de inventario demostrativo):** Separar de forma comprobable los espacios de trabajo demostrativos (`es_copia_demostrativa=True` o que contengan los marcadores `MARCADOR_PRODUCTO_DEMOSTRATIVO = "[DEMOSTRATIVO]"` / `MARCADOR_DESCRIPCION_DEMOSTRATIVA = "(Demostrativo)"` evaluados por `contiene_datos_demostrativos(inventario)`) de los datos autorizados para inicialización oficial (`inicializacion_oficial_autorizada=True` mediante `inventario_inicializacion_oficial` y `autorizar_inicializacion_oficial=True` en `cargar_espacio_trabajo_administrativo`). Bloquear en `publicar_inventario_administrativo_github` tanto la publicación de datos demostrativos (`CodigoResultadoPersistenciaGitHub.DATOS_DEMOSTRATIVOS_NO_PUBLICABLES`) como la inicialización sin autorización oficial (`CodigoResultadoPersistenciaGitHub.INICIALIZACION_NO_AUTORIZADA`), e impedir que la interfaz en `03_Aplicacion/app.py` ofrezca botones de publicación o inicialización en GitHub cuando el espacio de trabajo es una copia demostrativa.
   - **Corrección 3 (Trazabilidad exacta del informe):** Alinear todos los nombres de funciones, clases, constantes y los 43 casos de prueba con el código real entregado, distinguiendo explícitamente entre controles implementados, pruebas efectivamente ejecutadas, resultados obtenidos, controles pendientes de verificación y riesgos residuales.
   - **Verificación de secretos:** Ejecutar auditoría estática y pruebas dinámicas con credenciales ficticias sobre excepciones, logs, interfaz, representaciones de objetos (`repr`/`str`), archivos versionados (`git ls-files`) y `.gitignore`.

---

## 3. Requisitos Funcionales (RF) y Criterios de Aceptación (CA) Relacionados

### 3.1. Requisitos Funcionales (`01_Documentacion/02_Especificaciones_v0.md`)

| Código RF | Descripción | Estado en P10 |
| :--- | :--- | :--- |
| **RF-021** | Permitir confirmar y guardar los cambios realizados por el administrador sobre el inventario. | Implementado en código y verificado mediante transporte simulado (`ejecutor_http_put`); escritura HTTP real deshabilitada por `ESCRITURA_REAL_GITHUB_HABILITADA = False`. |
| **RF-022** | Mantener la persistencia de los cambios confirmados en el archivo maestro `03_Aplicacion/inventario.xlsx` almacenado en GitHub. | Implementado en `03_Aplicacion/persistencia_github.py` (`publicar_inventario_administrativo_github`). |
| **RF-023** | Conservar la estructura de cuatro hojas (`Productos`, `Categorias`, `Ubicaciones`, `Asignaciones`) y sus columnas obligatorias al guardar. | Implementado en `serializar_inventario_a_xlsx_bytes` y `verificar_roundtrip_xlsx_bytes`. |
| **RF-024** | Conservar la información existente en todas las hojas que no haya sido objeto de modificación administrativa. | Implementado y verificado mediante comparación exacta (`inventarios_son_identicos`). |
| **RF-025** | Utilizar GitHub API para actualizar el archivo maestro `03_Aplicacion/inventario.xlsx` en la rama `main` del repositorio `JunyMSAI/FerreteriaMS`. | Implementado en `validar_destino_oficial_escritura_github` y `construir_solicitud_put_contents_github`. |
| **RF-026** | Verificar la versión (`sha`) del archivo maestro antes de guardar para detectar modificaciones concurrentes. | Implementado con consulta remota previa (`consultor_estado_remoto`) y envío de `sha` en `SolicitudPutContentsGitHub`. |
| **RF-027** | Impedir la sobrescritura automática cuando exista conflicto de versiones e informar al administrador. | Implementado (`CodigoResultadoPersistenciaGitHub.CONFLICTO_SHA`, preservando cambios locales y borrador). |
| **RF-028** | Reflejar los cambios confirmados en las consultas posteriores sin requerir reinicio manual de la aplicación. | Implementado en `sincronizar_estado_busqueda_publica_tras_publicacion` (`03_Aplicacion/app.py`). |
| **RF-029** | Permitir la creación inicial del archivo `03_Aplicacion/inventario.xlsx` únicamente cuando se confirme que todavía no existe en GitHub. | Implementado (requiere `EstadoArchivoRemoto.NO_EXISTE`, `sha_base_remoto is None`, `inicializacion_oficial_autorizada=True`, ausencia de datos demostrativos, sesión admin válida y `confirmacion_explicita=True`). |
| **RF-030** | Impedir que el proceso de inicialización reemplace o sobrescriba un archivo `03_Aplicacion/inventario.xlsx` existente en GitHub. | Implementado (`CodigoResultadoPersistenciaGitHub.ARCHIVO_REMOTO_YA_EXISTE`). |
| **RF-031** | Poblar la creación inicial con un inventario válido autorizado cuando corresponda y sea confirmado explícitamente por el administrador, impidiendo publicar datos demostrativos de prueba. | Implementado con separación estricta entre copia demostrativa (`es_copia_demostrativa=True`) e inicialización oficial (`inicializacion_oficial_autorizada=True`). |
| **RF-039** | Informar de manera comprensible cuando falle una operación de guardado en GitHub y conservar los cambios locales no confirmados. | Implementado para HTTP 401, 403, 404, 409, 422, 429, 500/502/503, *timeout*, errores de red y respuestas malformadas. |

### 3.2. Criterios de Aceptación (`01_Documentacion/02_Especificaciones_v0.md`)

| Código CA | Descripción | Estado en P10 |
| :--- | :--- | :--- |
| **CA-017** | Al confirmar cambios administrativos válidos, el sistema actualiza el archivo Excel maestro en GitHub y confirma la operación al administrador. | Comprobado en simulación (`ejecutor_http_put` con `HTTP 200` / `HTTP 201`); pendiente de verificación contra GitHub real cuando se autorice. |
| **CA-018** | Los cambios confirmados pueden consultarse desde la búsqueda pública sin reiniciar manualmente Streamlit. | Comprobado en pruebas de integración y sincronización de sesión. |
| **CA-019** | Los cambios confirmados permanecen disponibles tras reiniciar la aplicación o iniciar una nueva sesión al residir en GitHub. | Comprobado mediante ciclo simulado de publicación y lectura remota posterior. |
| **CA-020** | Si `03_Aplicacion/inventario.xlsx` no existe en GitHub, el sistema permite su creación inicial válida sin errores de estructura. | Comprobado en simulación con inventario oficial autorizado (`inicializacion_oficial_autorizada=True`, `es_copia_demostrativa=False`). |
| **CA-021** | Si `03_Aplicacion/inventario.xlsx` ya existe en GitHub, el sistema nunca lo recrea ni sobrescribe con datos iniciales. | Comprobado (`ARCHIVO_REMOTO_YA_EXISTE`). |
| **CA-022** | El archivo Excel guardado mantiene exactamente las cuatro hojas oficiales y sus encabezados exactos. | Comprobado (`serializar_inventario_a_xlsx_bytes` + `verificar_roundtrip_xlsx_bytes`). |
| **CA-023** | Si el archivo remoto cambió desde que fue leído por el administrador, el sistema detecta el conflicto de `sha` e impide sobrescribirlo. | Comprobado (tanto en consulta previa como en respuesta `409`/`422`). |
| **CA-024** | Si falla la escritura en GitHub, el sistema no declara éxito, informa el error y conserva los cambios pendientes en la sesión. | Comprobado. |
| **CA-025** | Al guardar cambios en `Productos` y `Asignaciones`, las hojas `Categorias` y `Ubicaciones` permanecen íntegras. | Comprobado. |
| **CA-027** | Ninguna operación de escritura puede ejecutarse sin sesión administrativa activa y válida. | Comprobado (`ACCESO_DENEGADO`). |
| **CA-028** | Los mensajes de error o diagnóstico no exponen el token de GitHub, contraseñas ni hashes administrativos. | Comprobado (`sanitizar_mensaje_escritura_github` y `__repr__`/`__str__` seguros). |
| **CA-044** | Las operaciones de escritura hacia GitHub se realizan mediante solicitudes HTTPS autenticadas a `api.github.com`. | Comprobado (`validar_destino_oficial_escritura_github` y `construir_solicitud_put_contents_github`). |
| **CA-045** | Toda confirmación de guardado devuelve y registra el nuevo `sha` del archivo actualizado en el espacio de trabajo administrativo. | Comprobado (`aplicar_confirmacion_publicacion_github`). |
| **CA-051** | Si la sesión administrativa expira antes de confirmar la publicación, se bloquea la escritura en GitHub y se preserva el borrador temporal para recuperación tras reautenticación. | Comprobado. |
| **CA-058** | Desde dispositivos móviles no es posible invocar ni ejecutar la publicación en GitHub. | Comprobado. |

---

## 4. Archivos Creados o Modificados

### 4.1. Archivos creados

1. **`03_Aplicacion/persistencia_github.py`**
   - Módulo dedicado a la serialización validada de `InventarioDatos` a `.xlsx`, construcción de solicitudes `PUT` para GitHub Contents API, compuerta global de bloqueo de escrituras reales (`ESCRITURA_REAL_GITHUB_HABILITADA = False`), control de concurrencia por `SHA`, separación entre datos demostrativos e inicialización oficial, manejo de errores HTTP/red y sanitización de secretos.
2. **`04_Pruebas/test_10_persistencia_inventario_github.py`**
   - Suite de 43 pruebas automatizadas (`TestPrompt10PersistenciaInventarioGitHub`) que verifican serialización, *round-trip*, construcción de solicitudes `PUT`, control de concurrencia `SHA`, manejo de errores, controles de acceso, bloqueo incondicional de escrituras reales, bloqueo de publicación de datos demostrativos y auditoría estática/dinámica de secretos.
3. **`05_Resultados/10_Resultado_Persistencia_Inventario_GitHub.md`**
   - Informe de resultados y trazabilidad del Prompt 10 y de sus correcciones post-auditoría.

### 4.2. Archivos modificados

1. **`03_Aplicacion/administracion_productos.py`**
   - Se incorporaron los marcadores y el detector de datos demostrativos: `MARCADOR_PRODUCTO_DEMOSTRATIVO = "[DEMOSTRATIVO]"`, `MARCADOR_DESCRIPCION_DEMOSTRATIVA = "(Demostrativo)"` y `contiene_datos_demostrativos(inventario)`.
   - Se añadieron a `EspacioTrabajoInventarioAdmin` los atributos `es_copia_demostrativa: bool = False` e `inicializacion_oficial_autorizada: bool = False`.
   - En `cargar_espacio_trabajo_administrativo` se diferenciaron dos rutas explícitas cuando el archivo remoto `NO_EXISTE`:
     - Copia demostrativa en memoria (`permitir_copia_demostrativa_si_no_existe=True`), que marca `es_copia_demostrativa=True` e `inicializacion_oficial_autorizada=False` (bloqueada para publicación en GitHub).
     - Inicialización oficial autorizada (`inventario_inicializacion_oficial` con `autorizar_inicializacion_oficial=True`), que rechaza cualquier inventario con marcadores demostrativos y marca `es_copia_demostrativa=False` e `inicializacion_oficial_autorizada=True`.
   - Se añadió `aplicar_confirmacion_publicacion_github(espacio, *, nuevo_sha_remoto, timestamp_utc=None)` para actualizar `inventario_original`, `inventario_trabajo`, `sha_base_remoto`, `origen_remoto_confirmado=True`, `es_copia_demostrativa=False` e `inicializacion_oficial_autorizada=False` tras una confirmación exitosa.
2. **`03_Aplicacion/app.py`**
   - Se integró `03_Aplicacion/persistencia_github.py` mediante las claves de sesión `CLAVE_CONFIRMACION_GUARDADO_GITHUB`, `CLAVE_PUBLICACION_GITHUB_EN_CURSO`, `CLAVE_ULTIMA_HUELLA_PUBLICADA_GITHUB`, `CLAVE_ULTIMA_PUBLICACION_GITHUB_ADMIN` y `CLAVE_CONFLICTO_SHA_ADMIN`, la clase `EstadoConflictoShaAdmin`, y las funciones `sincronizar_estado_busqueda_publica_tras_publicacion`, `ejecutar_publicacion_github_en_sesion`, `ejecutar_recarga_remota_tras_conflicto_en_sesion` y `ejecutar_preparacion_copia_demostrativa_en_sesion`.
   - En `renderizar_panel_gestion_inventario_admin` se bloqueó en la interfaz la aparición de la casilla `chk_admin_confirmar_publicacion_github` y del botón `btn_admin_publicar_github` cuando el espacio de trabajo es demostrativo (`es_espacio_demostrativo=True`), mostrando el aviso informativo con `MENSAJE_DATOS_DEMOSTRATIVOS_NO_PUBLICABLES`.

### 4.3. Archivos protegidos sin modificaciones

- `03_Aplicacion/inventario.py`
- `03_Aplicacion/github_inventario.py`
- `03_Aplicacion/busqueda.py`
- `03_Aplicacion/autenticacion.py`
- `requirements.txt`
- `01_Documentacion/*`, `02_Prompts/*`, `04_Pruebas/test_02..09`, `05_Resultados/02..09`
- No se creó ni modificó `03_Aplicacion/inventario.xlsx`.

---

## 5. Distinción Expresa: Controles Implementados, Pruebas Ejecutadas, Resultados, Pendientes y Riesgos Residuales

### 5.1. Controles implementados

1. **Bloqueo incondicional de escrituras HTTP reales (`Corrección 1`):**
   - `ESCRITURA_REAL_GITHUB_HABILITADA: bool = False` en `03_Aplicacion/persistencia_github.py`.
   - `ejecutar_solicitud_put_github(solicitud, *, token)` no acepta ningún parámetro para eludir la compuerta (`permitir_red_real` fue eliminado de todo el código) ni realiza inspección del módulo de `urllib.request.urlopen`. Si `ESCRITURA_REAL_GITHUB_HABILITADA` es `False`, lanza incondicionalmente `ErrorEscrituraRealNoAutorizadaGitHub(MENSAJE_ESCRITURA_REAL_BLOQUEADA)` antes de construir cualquier `urllib.request.Request` o invocar `urlopen`.
   - `publicar_inventario_administrativo_github` separa el transporte simulado para pruebas (`ejecutor_http_put` inyectado explícitamente en los tests) de la ruta de producción (`ejecutor_http_put=None`, que delega en `ejecutar_solicitud_put_github` y devuelve `CodigoResultadoPersistenciaGitHub.ESCRITURA_REAL_NO_AUTORIZADA` mientras la compuerta global esté deshabilitada).
   - `ejecutar_publicacion_github_en_sesion` en `03_Aplicacion/app.py` tampoco expone ningún parámetro para habilitar red real.

2. **Separación comprobable e imposibilidad de publicar inventario demostrativo (`Corrección 2`):**
   - `contiene_datos_demostrativos(inventario)` en `03_Aplicacion/administracion_productos.py` inspecciona todos los registros de `Productos` buscando `MARCADOR_PRODUCTO_DEMOSTRATIVO` (`"[DEMOSTRATIVO]"`) o `MARCADOR_DESCRIPCION_DEMOSTRATIVA` (`"(Demostrativo)"`).
   - `crear_inventario_demostrativo()` genera productos marcados con `[DEMOSTRATIVO]` y `(Demostrativo)`.
   - `cargar_espacio_trabajo_administrativo` asigna `es_copia_demostrativa=True` e `inicializacion_oficial_autorizada=False` cuando se prepara la copia demostrativa en memoria, y rechaza con `ErrorIntegridadInventario` cualquier intento de pasar un inventario con marcadores demostrativos como `inventario_inicializacion_oficial`.
   - `publicar_inventario_administrativo_github` bloquea antes de cualquier serialización o consulta de red:
     - Cualquier espacio con `es_copia_demostrativa=True` o `contiene_datos_demostrativos(inventario_trabajo)==True` o `contiene_datos_demostrativos(inventario_original)==True`, devolviendo `CodigoResultadoPersistenciaGitHub.DATOS_DEMOSTRATIVOS_NO_PUBLICABLES`.
     - Cualquier intento de creación inicial (`not origen_remoto_confirmado` o `sha_base_remoto is None`) donde `inicializacion_oficial_autorizada` sea `False`, devolviendo `CodigoResultadoPersistenciaGitHub.INICIALIZACION_NO_AUTORIZADA`.
   - En `03_Aplicacion/app.py`, cuando el archivo remoto no existe, el botón `"🧪 Preparar copia demostrativa solo en memoria (no publicable en GitHub)"` (`btn_admin_preparar_copia_demostrativa`) carga los datos únicamente para pruebas locales en memoria, y el panel administrativo oculta la casilla de confirmación y el botón de publicación en GitHub mientras el espacio sea demostrativo.

3. **Serialización validada y verificación *round-trip* en memoria:**
   - `serializar_inventario_a_xlsx_bytes(inventario)` valida el esquema y las reglas de integridad sobre una copia profunda y escribe las cuatro hojas oficiales (`Productos`, `Categorias`, `Ubicaciones`, `Asignaciones`) en el orden exacto de `ORDEN_HOJAS_INVENTARIO` y `ESQUEMA_HOJAS_INVENTARIO`, forzando formato texto (`@`) en las columnas `Codigo_Producto`, `Categoria_ID` y `Ubicacion_ID`.
   - `verificar_roundtrip_xlsx_bytes(contenido_xlsx, inventario_esperado)` relee los bytes con `cargar_inventario_excel` y comprueba identidad exacta mediante `inventarios_son_identicos`.
   - `preparar_artefacto_xlsx_para_github(inventario)` ejecuta ambos pasos, codifica en Base64 y verifica que la decodificación Base64 coincida byte a byte con el `.xlsx` generado, devolviendo `ArtefactoXlsxSerializado`.

4. **Validación de destino oficial, control de concurrencia `SHA` y manejo de errores:**
   - `validar_destino_oficial_escritura_github(config)` exige propietario `JunyMSAI`, repositorio `FerreteriaMS`, rama `main`, ruta `03_Aplicacion/inventario.xlsx`, esquema `https://` y host `api.github.com`.
   - `publicar_inventario_administrativo_github` exige contexto de escritorio, sesión administrativa activa y no expirada en el servidor, ausencia de bloqueo progresivo, `confirmacion_explicita=True`, existencia de cambios pendientes y no duplicidad de huella (`calcular_huella_publicacion`).
   - Antes de invocar el transporte `PUT`, consulta el estado remoto (`consultor_estado_remoto`) para detectar conflictos de versión (`CONFLICTO_SHA`), apariciones remotas previas a una inicialización (`ARCHIVO_REMOTO_YA_EXISTE`) o eliminaciones remotas (`ARCHIVO_REMOTO_DESAPARECIO`).
   - Clasifica respuestas `HTTP 200`/`201` (exigiendo `content.sha` y `commit.sha` válidos), `401` (`ERROR_AUTENTICACION_GITHUB`), `403` (`ERROR_PERMISOS_GITHUB` o `LIMITE_TASA_GITHUB`), `404` (`ARCHIVO_REMOTO_DESAPARECIO` / `CONFIGURACION_INVALIDA`), `409`/`422` (`CONFLICTO_SHA`), `429` (`LIMITE_TASA_GITHUB`), `500`/`502`/`503` (`ERROR_SERVIDOR_GITHUB`) y errores de red/timeout (`ERROR_RED_O_TIMEOUT`), preservando intactos los cambios locales y el borrador temporal cuando la escritura no se confirma.

5. **Protección de secretos y representaciones seguras:**
   - `sanitizar_mensaje_escritura_github(mensaje, token=None)` redacta cualquier aparición del token configurado, tokens `ghp_...`, `github_pat_...`, `gho_...`, `ghs_...`, `ghu_...`, encabezados `Authorization`/`Bearer`/`token` y hashes `$argon2...`.
   - `ConfiguracionGitHub` (`03_Aplicacion/github_inventario.py`) y `CredencialAdministrativa` (`03_Aplicacion/autenticacion.py`) definen `repr=False` y métodos `__repr__`/`__str__` que enmascaran `token` y `password_hash` como `'***REDACTED***'`.

### 5.2. Pruebas efectivamente ejecutadas y resultados obtenidos

#### 5.2.1. Suite del Prompt 10 (`04_Pruebas/test_10_persistencia_inventario_github.py`)

Comando ejecutado:
```powershell
python -m unittest -v 04_Pruebas/test_10_persistencia_inventario_github.py
```

Resultado obtenido: **43 pruebas ejecutadas en 5.793s — `OK` (100% exitosas)**.

Listado exacto de los 43 métodos de prueba ejecutados en `TestPrompt10PersistenciaInventarioGitHub`:
1. `test_01_serializacion_inventario_a_bytes_xlsx_en_memoria` — `ok`
2. `test_02_preservacion_exacta_cuatro_hojas` — `ok`
3. `test_03_preservacion_orden_columnas_en_cada_hoja` — `ok`
4. `test_04_preservacion_codigos_como_texto_con_ceros_iniciales` — `ok`
5. `test_05_verificacion_roundtrip_con_cargar_inventario_excel` — `ok`
6. `test_06_rechazo_serializacion_con_errores_esquema_o_integridad` — `ok`
7. `test_07_construccion_correcta_payload_json_github_contents_api` — `ok`
8. `test_08_codificacion_base64_valida_del_archivo_xlsx` — `ok`
9. `test_09_inclusion_branch_main_y_ruta_oficial_y_rechazo_destinos_no_autorizados` — `ok`
10. `test_10_inclusion_sha_vigente_al_actualizar_archivo_existente` — `ok`
11. `test_11_creacion_inicial_permitida_solo_cuando_github_confirma_inexistencia_real` — `ok`
12. `test_12_rechazo_creacion_inicial_si_archivo_remoto_aparece_antes_de_publicar` — `ok`
13. `test_13_rechazo_creacion_inicial_cuando_consulta_previa_devuelve_error` — `ok`
14. `test_14_actualizacion_simulada_exitosa_cuando_sha_base_coincide_con_remoto` — `ok`
15. `test_15_actualizacion_sha_local_al_nuevo_sha_devuelto_por_github` — `ok`
16. `test_16_limpieza_estado_cambios_pendientes_tras_confirmacion_exitosa` — `ok`
17. `test_17_limpieza_descarte_borrador_temporal_tras_confirmacion_exitosa` — `ok`
18. `test_18_deteccion_conflicto_sha_cuando_sha_remoto_cambio_antes_de_publicar` — `ok`
19. `test_19_deteccion_conflicto_sha_cuando_github_responde_409_o_422` — `ok`
20. `test_20_conservacion_intacta_cambios_pendientes_y_borrador_en_conflicto_sha` — `ok`
21. `test_21_opcion_controlada_para_recargar_version_remota_tras_conflicto` — `ok`
22. `test_22_manejo_error_401_sin_declarar_exito_ni_exponer_token` — `ok`
23. `test_23_manejo_error_403_permisos_insuficientes_sin_declarar_exito` — `ok`
24. `test_24_manejo_error_404_inesperado_en_actualizacion_sin_convertir_en_inicializacion` — `ok`
25. `test_25_manejo_error_429_o_rate_limit_agotado_sin_declarar_exito` — `ok`
26. `test_26_manejo_error_500_502_503_sin_declarar_exito` — `ok`
27. `test_27_manejo_timeout_o_error_red_sin_declarar_exito_ni_perder_cambios` — `ok`
28. `test_28_rechazo_respuesta_200_201_malformada_o_sin_nuevo_sha` — `ok`
29. `test_29_bloqueo_publicacion_sin_sesion_administrativa_autenticada` — `ok`
30. `test_30_bloqueo_publicacion_con_sesion_expirada_y_preservacion_borrador` — `ok`
31. `test_31_bloqueo_publicacion_durante_bloqueo_administrativo_activo` — `ok`
32. `test_32_bloqueo_publicacion_desde_contexto_movil` — `ok`
33. `test_33_bloqueo_publicacion_sin_confirmacion_explicita_del_administrador` — `ok`
34. `test_34_prevencion_doble_envio_o_publicacion_duplicada` — `ok`
35. `test_35_flujo_completo_login_crear_producto_publicar_y_busqueda_publica` — `ok`
36. `test_36_flujo_completo_login_editar_producto_ubicaciones_publicar_y_busqueda_publica` — `ok`
37. `test_37_cambios_locales_no_confirmados_no_aparecen_en_busqueda_publica` — `ok`
38. `test_38_no_se_crea_ni_modifica_inventario_xlsx_local_ni_solicitudes_reales` — `ok`
39. `test_39_ausencia_exposicion_secretos_tokens_contrasenas_hashes` — `ok`
40. `test_40_integracion_interfaz_streamlit_p10_y_regresion_prompts_02_a_09` — `ok`
41. `test_41_rechazo_intentos_anular_compuerta_escritura_real_github` — `ok`
42. `test_42_bloqueo_publicacion_datos_demostrativos_y_separacion_inicializacion_oficial` — `ok`
43. `test_43_auditoria_estatica_y_dinamica_no_exposicion_secretos_y_gitignore` — `ok`

#### 5.2.2. Suites de regresión P02–P09 ejecutadas individual y secuencialmente

| Suite de prueba | Comando ejecutado | Pruebas | Tiempo | Resultado |
| :--- | :--- | :---: | :---: | :---: |
| **Prompt 02** (`04_Pruebas/test_02_motor_inventario.py`) | `python -m unittest -v 04_Pruebas/test_02_motor_inventario.py` | 23 | 0.205s | **OK** |
| **Prompt 03** (`04_Pruebas/test_03_lectura_github.py`) | `python -m unittest -v 04_Pruebas/test_03_lectura_github.py` | 21 | 0.325s | **OK** |
| **Prompt 04** (`04_Pruebas/test_04_busqueda_publica.py`) | `python -m unittest -v 04_Pruebas/test_04_busqueda_publica.py` | 25 | 1.191s | **OK** |
| **Prompt 05** (`04_Pruebas/test_05_detalles_ubicaciones.py`) | `python -m unittest -v 04_Pruebas/test_05_detalles_ubicaciones.py` | 23 | 3.099s | **OK** |
| **Prompt 06** (`04_Pruebas/test_06_interfaz_responsive_gemini.py`) | `python -m unittest -v 04_Pruebas/test_06_interfaz_responsive_gemini.py` | 18 | 4.068s | **OK** |
| **Prompt 07** (`04_Pruebas/test_07_autenticacion_administrativa.py`) | `python -m unittest -v 04_Pruebas/test_07_autenticacion_administrativa.py` | 22 | 1.785s | **OK** |
| **Prompt 08** (`04_Pruebas/test_08_sesiones_bloqueos_borradores.py`) | `python -m unittest -v 04_Pruebas/test_08_sesiones_bloqueos_borradores.py` | 40 | 1.262s | **OK** |
| **Prompt 09** (`04_Pruebas/test_09_gestion_administrativa_productos_ubicaciones.py`) | `python -m unittest -v 04_Pruebas/test_09_gestion_administrativa_productos_ubicaciones.py` | 51 | 2.689s | **OK** |
| **Prompt 10** (`04_Pruebas/test_10_persistencia_inventario_github.py`) | `python -m unittest -v 04_Pruebas/test_10_persistencia_inventario_github.py` | 43 | 5.793s | **OK** |
| **TOTAL** | **9 suites ejecutadas secuencialmente** | **266** | **20.417s** | **100% OK** |

### 5.3. Controles todavía pendientes de verificación en entorno real

Dado que esta ejecución prohíbe expresamente realizar escrituras reales hacia GitHub (`ESCRITURA_REAL_GITHUB_HABILITADA = False`) y usar credenciales reales:
1. **Ejecución real de `urllib.request.urlopen` con método `PUT` contra `https://api.github.com/repos/JunyMSAI/FerreteriaMS/contents/03_Aplicacion/inventario.xlsx`:** Todas las pruebas del Prompt 10 utilizaron ejecutores falsos inyectados (`ejecutor_http_put`) o verificaron que la llamada sin ejecutor simulado es bloqueada por `ErrorEscrituraRealNoAutorizadaGitHub`. La escritura HTTP real contra GitHub Contents API solo podrá verificarse cuando el responsable del proyecto autorice habilitar `ESCRITURA_REAL_GITHUB_HABILITADA = True` y configure el token real en Streamlit Secrets.
2. **Inicialización oficial real del archivo maestro `03_Aplicacion/inventario.xlsx` en GitHub:** El flujo de creación inicial (`HTTP 201`) fue probado únicamente en simulación con un inventario oficial autorizado libre de marcadores demostrativos; el archivo aún no existe ni localmente ni en el repositorio remoto.
3. **Verificación extremo a extremo en Streamlit Community Cloud:** La persistencia tras un reinicio real del contenedor en la nube y la lectura con token configurado en el panel de Secrets de Streamlit Community Cloud quedan pendientes para la etapa de despliegue autorizado (Prompt 11).

### 5.4. Riesgos residuales

1. **Activación futura de `ESCRITURA_REAL_GITHUB_HABILITADA`:** Mientras `ESCRITURA_REAL_GITHUB_HABILITADA` permanezca en `False`, ninguna llamada de producción puede escribir en GitHub. Cuando se autorice su cambio a `True` en una etapa posterior, será indispensable suministrar un conjunto de datos inicial oficial (no demostrativo) autorizado explícitamente si `03_Aplicacion/inventario.xlsx` aún no existe en `main`.
2. **Concurrencia entre múltiples instancias de servidor:** El control de concurrencia por `SHA` (`RF-026`, `RF-027`) protege la integridad del archivo en GitHub ante ediciones simultáneas desde distintas sesiones o instancias, pero los bloqueos progresivos de login y los borradores temporales residen en la memoria del proceso de servidor de Streamlit (según el alcance aprobado de v0).
3. **Límites de tamaño de GitHub Contents API:** La API de contenidos de GitHub soporta archivos de hasta 1 MB para actualización directa por Base64 en `PUT`; esto es amplio para el catálogo de FerreteríaMS v0, pero constituye una cota técnica inherente a la arquitectura aprobada.

---

## 6. Verificación y Auditoría de Secretos

Se realizó una auditoría estática sobre el código fuente, archivos seguidos por Git y reglas de `.gitignore`, complementada con pruebas dinámicas con credenciales ficticias (`test_39_ausencia_exposicion_secretos_tokens_contrasenas_hashes` y `test_43_auditoria_estatica_y_dinamica_no_exposicion_secretos_y_gitignore`):

1. **Inspección de archivos versionados y árbol de trabajo:**
   - Se verificó que no existen archivos `.streamlit/secrets.toml`, `.env` ni `03_Aplicacion/inventario.xlsx` en el árbol de trabajo ni en `git ls-files`.
   - Se comprobó que `.gitignore` incluye las reglas de exclusión para `.streamlit/secrets.toml`, `secrets.toml`, `.env`, `*.pem` y `*.key`.
2. **Escaneo estático de patrones de credenciales reales:**
   - Se escanearon todos los módulos de `03_Aplicacion/` verificando la ausencia de literales con formato de tokens reales de GitHub (`ghp_`, `github_pat_`, `gho_`, `ghs_`, `ghu_`) o hashes Argon2 codificados en duro. No se encontró ningún secreto real.
3. **Pruebas dinámicas con credenciales ficticias:**
   - Se inyectaron tokens ficticios, contraseñas ficticias y hashes Argon2 ficticios en `ConfiguracionGitHub`, `CredencialAdministrativa`, `SolicitudPutContentsGitHub`, excepciones HTTP/red simuladas (`401`, `403`, `500`, `URLError`), registros de `logging` (`ferreteria_ms.persistencia_github` y `ferreteria_ms.auditoria_admin`) y renderizado en `AppTest` de Streamlit.
   - Se comprobó que `repr()` y `str()` de `ConfiguracionGitHub`, `CredencialAdministrativa` y `ResultadoPublicacionGitHub`, así como todos los mensajes de error devueltos al usuario y escritos en logs, enmascaran íntegramente los valores sensibles (`***REDACTED***` / `[TOKEN_GITHUB_OCULTO]` / `[CREDENCIAL_OCULTA]` / `[HASH_OCULTO]`).

---

## 7. Referencia al Commit y Estado del Repositorio

- **Commit base al iniciar la tarea:** `8ac0b7e` (`main`)
- **Commit creado en esta ejecución:** Ninguno (de acuerdo con la instrucción expresa de no ejecutar `git add`, `git commit` ni `git push` hasta la nueva revisión independiente).
- **Verificación de ausencia de `03_Aplicacion/inventario.xlsx`:** Confirmado que el archivo no existe localmente ni en GitHub.
