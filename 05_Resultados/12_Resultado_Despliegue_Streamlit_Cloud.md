# Informe de Resultados — Prompt 12: Puesta en funcionamiento real y despliegue de FerreteríaMS v0

**Proyecto:** FerreteríaMS v0  
**TASK_ID:** `FERMS-V0-P12`  
**TASK_TITLE:** Puesta en funcionamiento real, navegación e integración GitHub  
**TASK_LEVEL:** Estándar — ejecución rápida y focalizada  
**TASK_DATE:** `2026-10-21`  
**TASK_TIME:** `19:22:17 -04:00`  
**Documento prompt de origen:** `02_Prompts/12_Despliegue_Streamlit_Cloud.md`  
**Rama de trabajo:** `main`  
**Commit base al iniciar:** `99e1787` (`Prompt "12_Despliegue_Streamlit_Cloud" incluido`)  
**Estado de persistencia real en GitHub:** **Preparado para activación** (`ESCRITURA_REAL_GITHUB_HABILITADA = False`; pendiente la prueba manual autorizada sobre GitHub y Streamlit Cloud).

---

## 1. Trazabilidad Obligatoria (`AGENTS.md` §3.10 y Prompt 12 §5)

### 1.1. `USER_REQUEST_ORIGINAL`

#### A. Instrucción de ejecución recibida del usuario (conservada textualmente sin alteraciones)

```markdown
**FERMS-V0-P12 — AUTORIZACIÓN DE EJECUCIÓN**

Ejecuta exclusivamente el documento oficial:

`02_Prompts/12_Despliegue_Streamlit_Cloud.md`

**Prioridad: finalizar FerreteríaMS v0 rápidamente y sin tareas redundantes.**

Antes de comenzar, consulta las instrucciones del proyecto y verifica que no existan cambios locales pendientes que puedan sobrescribirse.

Sigue estos criterios:

- No rehacer funcionalidades que ya funcionan.
- Corregir únicamente problemas que afecten la funcionalidad, seguridad o entrega.
- Ejecutar solamente las pruebas relacionadas con los cambios realizados.
- Conservar la barra superior de Streamlit y los enlaces de GitHub visibles, según la última decisión del responsable.
- No modificar el inventario maestro oficial.
- No utilizar ni revelar credenciales reales.
- Mantener deshabilitadas las escrituras HTTP PUT reales hasta autorización expresa.
- No realizar commits, pushes ni despliegues automáticamente.

Documenta los resultados en:

`05_Resultados/12_Resultado_Despliegue_Streamlit_Cloud.md`

Al finalizar, presenta las modificaciones, las pruebas ejecutadas, los problemas pendientes y el resultado de `git status --short`.

Detente para revisión y aprobación antes de continuar.
```

#### B. Contenido del documento oficial ejecutado (`02_Prompts/12_Despliegue_Streamlit_Cloud.md`)

Conservado sin alteraciones en `02_Prompts/12_Despliegue_Streamlit_Cloud.md` (commit `99e1787`).

---

### 1.2. `CODEX_UNDERSTANDING` (Interpretación del agente)

1. **Verificación inicial y respeto de decisiones vigentes:**
   - Se comprobó al inicio que `git status --short` estaba limpio en la rama `main` (commit `99e1787`) y se respetó la última decisión del responsable en `.streamlit/config.toml` (`toolbarMode = "auto"`) y `03_Aplicacion/app.py` (barra superior de Streamlit y enlaces de GitHub visibles).
2. **Navegación en pantalla (§3.A):**
   - En `_renderizar_banner_encabezado()` (`03_Aplicacion/app.py`), las tres columnas `[3.4, 0.8, 0.9]` provocaban que los botones `🏠 Inicio` y `📦 Productos` quedaran comprimidos (~15% del ancho) o desplazados hacia la esquina superior derecha donde la barra superior de Streamlit Cloud se superpone.
   - Se requería alinear la cabecera con la proporción `[2.35, 1]` del cuerpo principal (`vertical_alignment="center"`), alojando ambos botones en dos subcolumnas simétricas dentro de la columna derecha y aplicando un margen superior seguro (`padding-top: 2.75rem`) y ajuste de texto (`white-space: normal; max-width: 100%`) en `03_Aplicacion/estilos.css`, sin alterar `key`, flujos de navegación ni autenticación.
3. **Inventario oficial y actualización focalizada de aserciones (§3.B):**
   - El archivo oficial `03_Aplicacion/inventario.xlsx` ya fue inicializado en la rama `main` (commit `26d26eb`, con 0 productos, 3 categorías `CAT001`–`CAT003`, 3 ubicaciones `U001`–`U003` y 0 asignaciones).
   - Se debían actualizar únicamente las aserciones de las suites `P02`–`P10` que exigían la inexistencia física del archivo (`assertFalse(RUTA_MAESTRO_DEFINITIVO.exists())` / `assertNotIn("03_Aplicacion/inventario.xlsx", archivos_versionados)`), reemplazándolas por verificaciones de existencia, **no modificación byte a byte** (`BYTES_MAESTRO_INICIAL`) y lectura válida mediante `cargar_inventario_excel()`.
4. **Catálogos y administración (§3.C):**
   - Comprobar con el archivo oficial `03_Aplicacion/inventario.xlsx` que la carga administrativa y el formulario de creación de productos (`ModoVistaAdmin.CREAR_PRODUCTO`) exponen las 3 categorías (`CAT001`, `CAT002`, `CAT003`) y las 3 ubicaciones (`U001`, `U002`, `U003`) existentes.
5. **Preparación para guardado real vía GitHub API y frontera de autorización (§3.D):**
   - Verificar que la ruta de publicación en `03_Aplicacion/app.py` y `03_Aplicacion/persistencia_github.py` utiliza el destino fijo `JunyMSAI/FerreteriaMS`, rama `main`, ruta `03_Aplicacion/inventario.xlsx`, autenticación administrativa, confirmación explícita, validación round-trip de las 4 hojas Excel y control de conflicto `SHA`.
   - Mantener `ESCRITURA_REAL_GITHUB_HABILITADA: bool = False` en `03_Aplicacion/persistencia_github.py` y documentar el cambio mínimo de una sola línea para su activación posterior autorizada por el responsable.

---

### 1.3. `CODEX_ACTIONS_TAKEN` (Acciones realizadas)

1. **Corrección mínima de navegación y posicionamiento en `03_Aplicacion/app.py` y `03_Aplicacion/estilos.css`:**
   - En `_renderizar_banner_encabezado()` (`03_Aplicacion/app.py`), se reemplazó la fila de tres columnas desbalanceadas `st.columns([3.4, 0.8, 0.9])` por `col_marca, col_nav = st.columns([2.35, 1], vertical_alignment="center")` con dos columnas internas `st.columns(2, gap="small")` para `btn_nav_inicio` (`🏠 Inicio`) y `btn_nav_productos` (`📦 Productos`), resaltando visualmente la sección activa (`type="primary"` / `"secondary"`) sin cambiar las claves `key="btn_nav_inicio"` ni `key="btn_nav_productos"`.
   - En `03_Aplicacion/estilos.css`, se ajustó `padding-top: 2.75rem` en `.main .block-container, .stMainBlockContainer` (`2.25rem` en pantallas `<= 640px`) para evitar solapamiento con la barra superior visible de Streamlit Cloud, se añadió `min-width: 0` a las columnas horizontales y se configuró `.stButton > button` con `max-width: 100%; white-space: normal; line-height: 1.25; padding: 0.4rem 0.75rem`.
2. **Actualización de aserciones desactualizadas sobre `03_Aplicacion/inventario.xlsx` en pruebas `P02`–`P10`:**
   - En `test_02_motor_inventario.py`, `test_03_lectura_github.py`, `test_04_busqueda_publica.py`, `test_05_detalles_ubicaciones.py`, `test_06_interfaz_responsive_gemini.py`, `test_08_sesiones_bloqueos_borradores.py`, `test_09_gestion_administrativa_productos_ubicaciones.py` y `test_10_persistencia_inventario_github.py`, se reemplazaron exclusivamente las aserciones que suponían que `03_Aplicacion/inventario.xlsx` no existía por comprobaciones de que el archivo oficial existe, permanece idéntico byte a byte (`read_bytes() == BYTES_MAESTRO_INICIAL`) antes y después de las pruebas, y es validado por `cargar_inventario_excel()`.
3. **Verificación del formulario administrativo de creación con los catálogos del inventario oficial:**
   - En `test_38_no_se_crea_ni_modifica_archivo_local_inventario_xlsx` (`04_Pruebas/test_09_gestion_administrativa_productos_ubicaciones.py`), se verificó la carga de `03_Aplicacion/inventario.xlsx` real (0 productos, 3 categorías, 3 ubicaciones, 0 asignaciones) tanto en funciones de dominio como en el flujo `AppTest` de la pestaña `Productos` -> login -> `➕ Crear producto`, comprobando que los selectores `campo_admin_crear_categoria`, `campo_admin_crear_ubicaciones` y `campo_admin_crear_ubicacion_principal` cargan exactamente `CAT001`, `CAT002`, `CAT003` y `U001`, `U002`, `U003` sin errores.
4. **Verificación de la ruta de persistencia GitHub y compuerta `ESCRITURA_REAL_GITHUB_HABILITADA = False`:**
   - Se comprobó mediante pruebas focalizadas que `persistencia_github.py` mantiene `ESCRITURA_REAL_GITHUB_HABILITADA: bool = False` (línea 122), bloquea cualquier escritura HTTP `PUT` real y valida destino, `SHA`, confirmación explícita, *round-trip* Excel y protección contra doble envío.

---

## 2. Archivos Creados o Modificados

| Archivo | Tipo de cambio | Descripción concisa |
| :--- | :---: | :--- |
| `03_Aplicacion/app.py` | Modificado | Alineación y proporción de columnas `[2.35, 1]` con subcolumnas simétricas para los botones `🏠 Inicio` y `📦 Productos` en `_renderizar_banner_encabezado()`. Conserva visible la barra superior de Streamlit. |
| `03_Aplicacion/estilos.css` | Modificado | Ajuste de `padding-top` del contenedor principal para convivir con la barra superior de Streamlit Cloud y prevención de desbordamiento en botones y columnas (`min-width: 0`, `white-space: normal`, `max-width: 100%`). |
| `04_Pruebas/test_02_motor_inventario.py` | Modificado | Sustitución de `assertFalse(RUTA_MAESTRO_DEFINITIVO.exists())` por comprobación de no modificación byte a byte y lectura con `cargar_inventario_excel()`. |
| `04_Pruebas/test_03_lectura_github.py` | Modificado | Sustitución de aserción de inexistencia local por comprobación de no modificación byte a byte de `03_Aplicacion/inventario.xlsx`. |
| `04_Pruebas/test_04_busqueda_publica.py` | Modificado | Sustitución de aserción de inexistencia local por comprobación de no modificación y validez del archivo maestro oficial. |
| `04_Pruebas/test_05_detalles_ubicaciones.py` | Modificado | Sustitución de aserción de inexistencia local por comprobación de no modificación y lectura con el motor de inventario. |
| `04_Pruebas/test_06_interfaz_responsive_gemini.py` | Modificado | Sustitución de aserción de inexistencia local en `test_17` por comprobación de no modificación del archivo maestro oficial. |
| `04_Pruebas/test_08_sesiones_bloqueos_borradores.py` | Modificado | Sustitución de aserción de inexistencia local en `test_38` por comprobación de no modificación del archivo maestro oficial. |
| `04_Pruebas/test_09_gestion_administrativa_productos_ubicaciones.py` | Modificado | Sustitución de aserción de inexistencia en `test_38` por comprobación de no modificación y verificación en UI (`AppTest`) de las 3 categorías (`CAT001`–`CAT003`) y 3 ubicaciones (`U001`–`U003`) del inventario oficial en el formulario de alta. |
| `04_Pruebas/test_10_persistencia_inventario_github.py` | Modificado | Actualización de `test_01`, `test_38` y `test_43` para comprobar que `03_Aplicacion/inventario.xlsx` está versionado y no sufre modificaciones durante las pruebas. |
| `05_Resultados/12_Resultado_Despliegue_Streamlit_Cloud.md` | Creado | Presente informe oficial de resultados y trazabilidad del Prompt 12. |

- **¿Se modificó `03_Aplicacion/inventario.xlsx`?:** **NO** (`git diff -- 03_Aplicacion/inventario.xlsx` vacío; hash SHA-256 intacto).
- **¿Se modificó `.streamlit/config.toml`?:** **NO** (permanece `toolbarMode = "auto"`).
- **Requisitos RF relacionados:** `RF-001` a `RF-038`.
- **Criterios CA relacionados:** `CA-001` a `CA-036`, `CA-039` a `CA-061` (y preparación lista para `CA-037` y `CA-038` tras la prueba manual autorizada).

---

## 3. Pruebas Efectivamente Ejecutadas y Resultados

Siguiendo la instrucción de ejecutar únicamente las pruebas relacionadas con los cambios realizados (evitando correr de nuevo las 266 pruebas completas), se ejecutaron **31 pruebas focalizadas** en total:

### 3.1. Comandos ejecutados

```powershell
python -m unittest discover -s 04_Pruebas -k "test_generacion_demostrativa_en_memoria_y_serializacion_ciclica" -k "test_importar_modulo_no_crea_inventario_maestro" -k "test_06_ausencia_de_escrituras_remotas_y_locales" -k "test_06_ausencia_de_modificaciones_al_archivo_maestro" -k "TestInterfazResponsiveYGeminiFuncional" -k "test_38_no_implementacion_de_crud_o_escritura_remota" -k "test_38_no_se_crea_ni_modifica_archivo_local_inventario_xlsx" -k "test_01_serializacion_inventario_a_bytes_xlsx_en_memoria" -k "test_38_no_se_crea_ni_modifica_inventario_xlsx_local_ni_solicitudes_reales" -k "test_40_integracion_interfaz_streamlit_p10_y_regresion_prompts_02_a_09" -k "test_41_rechazo_intentos_anular_compuerta_escritura_real_github" -k "test_43_auditoria_estatica_y_dinamica_no_exposicion_secretos_y_gitignore" -v

python -m unittest discover -s 04_Pruebas -k "test_descarga_exitosa_sha_cuatro_hojas_y_ceros_iniciales" -k "test_estado_no_existe_confirmado_prepara_bytes_en_memoria_sin_escribir_disco" -v
```

### 3.2. Resumen de resultados

| Suite | Pruebas ejecutadas | Resultado | Qué se comprobó |
| :--- | :---: | :---: | :--- |
| `test_02_motor_inventario.py` | 2 | **OK** | Lectura íntegra de las 4 hojas de `03_Aplicacion/inventario.xlsx` con `cargar_inventario_excel()` y no modificación byte a byte. |
| `test_03_lectura_github.py` | 2 | **OK** | Lectura remota simulada, preparación en memoria y no modificación del archivo maestro oficial. |
| `test_04_busqueda_publica.py` | 1 | **OK** | Ausencia de escrituras y preservación intacta de `03_Aplicacion/inventario.xlsx`. |
| `test_05_detalles_ubicaciones.py` | 1 | **OK** | Preservación intacta de `03_Aplicacion/inventario.xlsx` y validación de sus 4 hojas. |
| `test_06_interfaz_responsive_gemini.py` | 18 | **OK** | Renderizado de `03_Aplicacion/app.py`, navegación corregida, estilos responsive (`estilos.css`), sección Gemini «Próximamente» y no modificación de `inventario.xlsx`. |
| `test_08_sesiones_bloqueos_borradores.py` | 1 | **OK** | Preservación intacta de `03_Aplicacion/inventario.xlsx` y ausencia de llamadas HTTP de escritura directas en `app.py`/`autenticacion.py`. |
| `test_09_gestion_administrativa_productos_ubicaciones.py` | 1 | **OK** | Carga del `03_Aplicacion/inventario.xlsx` oficial (0 productos, 3 categorías, 3 ubicaciones, 0 asignaciones) y verificación en `AppTest` de que el formulario `➕ Crear producto` permite seleccionar `CAT001`–`CAT003` y `U001`–`U003`. |
| `test_10_persistencia_inventario_github.py` | 5 | **OK** | Serialización `.xlsx`, compuerta `ESCRITURA_REAL_GITHUB_HABILITADA = False`, flujo completo `AppTest` de alta + confirmación explícita + guardado simulado + búsqueda inmediata sin reiniciar Streamlit, bloqueo de doble envío y auditoría de secretos/`.gitignore`. |
| **TOTAL FOCALIZADO** | **31** | **100% OK** | **Todas las verificaciones focalizadas aprobadas sin tocar credenciales reales ni modificar `inventario.xlsx`.** |

---

## 4. Verificación de Compuerta de Escritura Real y Cambio Mínimo para Activación Posterior

### 4.1. Estado actual verificado

- En `03_Aplicacion/persistencia_github.py` (línea 122):
  ```python
  ESCRITURA_REAL_GITHUB_HABILITADA: bool = False
  ```
- Mientras permanezca en `False`, cualquier llamada a `ejecutar_solicitud_put_github` lanza inmediatamente `ErrorEscrituraRealNoAutorizadaGitHub` antes de abrir cualquier conexión de red.
- La ruta operativa desde el botón `☁️ Guardar y publicar cambios en GitHub` en `03_Aplicacion/app.py` invoca `ejecutar_publicacion_github_en_sesion` -> `publicar_cambios_administrativos_github`, que valida:
  1. Contexto de escritorio (`ContextoDispositivo.ESCRITORIO`), sesión administrativa activa y ausencia de bloqueo.
  2. Casilla de confirmación explícita marcada (`chk_admin_confirmar_publicacion_github`).
  3. Rechazo de datos demostrativos (`[DEMOSTRATIVO]`).
  4. Serialización a `.xlsx` en memoria y verificación *round-trip* de las 4 hojas con `cargar_inventario_excel()`.
  5. Destino fijo `https://api.github.com/repos/JunyMSAI/FerreteriaMS/contents/03_Aplicacion/inventario.xlsx` en la rama `main`.
  6. Consulta previa del `SHA` remoto vigente y aborto seguro ante conflicto (`409` / `422` / diferencia de `SHA`) conservando cambios locales y borrador.
  7. Revocación automática de la confirmación ante cualquier fallo o respuesta ambigua para impedir doble envío.

### 4.2. Cambio mínimo, delimitado y reversible para habilitar escrituras reales (solo tras aprobación del responsable)

Cuando el responsable autorice habilitar el guardado real en producción, el único cambio requerido en todo el código es modificar la línea 122 de `03_Aplicacion/persistencia_github.py`:

```diff
--- a/03_Aplicacion/persistencia_github.py
+++ b/03_Aplicacion/persistencia_github.py
@@ -119,4 +119,4 @@
 # Compuerta de seguridad para escrituras de red reales.
 # Durante la ejecución de pruebas y mientras no se active en despliegue autorizado,
 # permanece en False para impedir cualquier solicitud HTTP PUT real hacia GitHub.
-ESCRITURA_REAL_GITHUB_HABILITADA: bool = False
+ESCRITURA_REAL_GITHUB_HABILITADA: bool = True
```

*(Nota: Para revertirlo en cualquier momento, basta con volver a establecer `ESCRITURA_REAL_GITHUB_HABILITADA: bool = False`).*

---

## 5. Problemas Críticos Pendientes y Pasos Manuales Exactos para la Prueba Autorizada y P13

### 5.1. Problemas críticos pendientes

- **Ningún defecto crítico de código o interfaz pendiente.**
- **Pendiente operativo externo (requiere autorización expresa del responsable):** la activación de `ESCRITURA_REAL_GITHUB_HABILITADA = True` y la ejecución de la prueba manual única de guardado real en Streamlit Community Cloud (`CA-037` y `CA-038`), que este documento prohíbe ejecutar de forma autónoma.

### 5.2. Pasos manuales exactos para la prueba autorizada en Streamlit Cloud y cierre en P13

1. **Revisión y commit de los cambios de P12:**
   - Revisar los cambios actuales (`git diff`) y confirmar que `03_Aplicacion/inventario.xlsx` no tiene modificaciones.
2. **Habilitación autorizada de la compuerta de escritura real (cuando el responsable lo decida):**
   - Antes de cambiar `ESCRITURA_REAL_GITHUB_HABILITADA` a `True` para desplegar en Streamlit Cloud, tener en cuenta que `test_38` y `test_41` de `04_Pruebas/test_10_persistencia_inventario_github.py` comprueban específicamente que la constante esté en `False` durante la ejecución de pruebas automatizadas.
   - Cambiar `ESCRITURA_REAL_GITHUB_HABILITADA: bool = True` en `03_Aplicacion/persistencia_github.py` (línea 122), hacer commit y `git push origin main` para que Streamlit Community Cloud actualice el despliegue.
3. **Verificación previa en Streamlit Community Cloud:**
   - Abrir la aplicación desplegada en computadora y teléfono para verificar que los botones **🏠 Inicio** y **📦 Productos** se muestran alineados y sin solaparse con la barra superior de Streamlit.
   - Confirmar que en `App settings -> Secrets` están definidos `FERRETERIAMS_ADMIN_USER`, `FERRETERIAMS_ADMIN_PASSWORD_HASH` y `FERRETERIAMS_GITHUB_TOKEN` (con permiso `Contents: Read and write` sobre `JunyMSAI/FerreteriaMS`).
4. **Ejecución de la prueba manual única de guardado real (en computadora):**
   - Entrar a **📦 Productos** e iniciar sesión administrativa.
   - Pulsar **➕ Crear producto**.
   - Verificar que aparecen las 3 categorías (`CAT001`, `CAT002`, `CAT003`) y las 3 ubicaciones (`U001`, `U002`, `U003`).
   - Completar **un único producto de evaluación explícitamente aprobado** por el responsable y pulsar **✅ Validar y registrar en copia local**.
   - Marcar la casilla **«Confirmo explícitamente publicar y versionar estos cambios en GitHub (rama main)»** y pulsar **una sola vez** el botón **☁️ Guardar y publicar cambios en GitHub**.
   - *(Si ocurriera un error o resultado ambiguo, no repetir automáticamente la escritura; revisar primero el historial de commits en GitHub).*
5. **Comprobación posterior en GitHub y en búsqueda pública (`CA-023`, `CA-024`, `CA-037`, `CA-038`):**
   - Confirmar en el repositorio `JunyMSAI/FerreteriaMS` (rama `main`) que se registró el commit sobre `03_Aplicacion/inventario.xlsx` con un nuevo `SHA`.
   - Ir a **🏠 Inicio** sin reiniciar manualmente Streamlit y buscar por nombre el producto recién creado, comprobando que aparece en los resultados y muestra su detalle y ubicación física.
   - Hacer `git pull` en el repositorio local antes de ejecutar el cierre documental en **P13**.

---

## 6. Estado del Repositorio (`git status --short`)

```text
 M 03_Aplicacion/app.py
 M 03_Aplicacion/estilos.css
 M 04_Pruebas/test_02_motor_inventario.py
 M 04_Pruebas/test_03_lectura_github.py
 M 04_Pruebas/test_04_busqueda_publica.py
 M 04_Pruebas/test_05_detalles_ubicaciones.py
 M 04_Pruebas/test_06_interfaz_responsive_gemini.py
 M 04_Pruebas/test_08_sesiones_bloqueos_borradores.py
 M 04_Pruebas/test_09_gestion_administrativa_productos_ubicaciones.py
 M 04_Pruebas/test_10_persistencia_inventario_github.py
?? 05_Resultados/12_Resultado_Despliegue_Streamlit_Cloud.md
```

