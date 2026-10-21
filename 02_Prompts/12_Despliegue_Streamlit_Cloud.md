# PROMPT 12 — Puesta en funcionamiento real y despliegue de FerreteríaMS v0

**Proyecto:** FerreteríaMS v0  
**TASK_ID:** FERMS-V0-P12  
**TASK_TITLE:** Puesta en funcionamiento real, navegación e integración GitHub  
**TASK_LEVEL:** Estándar — ejecución rápida y focalizada  
**TASK_DATE:** Completar al iniciar la ejecución (hora local del responsable)  
**TASK_TIME:** Completar al iniciar la ejecución (hora local del responsable)  
**Estado:** DOCUMENTO PROPUESTO — requiere aprobación y commit antes de ejecutarse  
**Responsable de ejecución:** Antigravity / Gemini

## 1. Objetivo y punto de partida

Completar únicamente los pendientes que impiden entregar FerreteríaMS v0 funcional en Streamlit Community Cloud.

**Estado ya alcanzado:** P11 registrado; aplicación desplegada en Streamlit Cloud con Python 3.12; búsqueda pública sin resultados y login administrativo observados operando; Secrets configurados por el responsable; `03_Aplicacion/inventario.xlsx` publicado en GitHub con 0 productos, 3 categorías, 3 ubicaciones y 0 asignaciones. El guardado HTTP PUT real permanece deshabilitado.

**Regla principal:** no reconstruir, repetir ni auditar de nuevo lo ya comprobado, salvo impacto directo de un cambio o riesgo concreto. La evidencia previa no sustituye las pruebas pendientes en el ambiente real.

## 2. Fuentes obligatorias

Leer selectivamente `GEMINI.md`, `AGENTS.md`, `01_Documentacion/02_Especificaciones_v0.md`, el presente prompt y `05_Resultados/11_Resultado_Integracion_Seguridad.md`. Consultar los módulos y pruebas relevantes, evitando releer archivos no afectados.

Respetar requisitos y decisiones aprobados. No iniciar `03_Especificaciones_Final.md` ni integrar Gemini API. Ante conflicto material de requisitos, detener el cambio afectado y reportarlo brevemente.

## 3. Alcance mínimo autorizado de implementación

### A. Navegación en pantalla

Corregir el desbordamiento o mala posición de los botones **Inicio** y **Productos** observado en Streamlit Cloud, con cambios mínimos en `03_Aplicacion/app.py` y/o `03_Aplicacion/estilos.css`. Deben quedar accesibles y alineados dentro de la página en escritorio y móvil, sin alterar claves, navegación ni autenticación. No rediseñar la interfaz.

### B. Inventario oficial y pruebas anteriores

El archivo `03_Aplicacion/inventario.xlsx` **ya existe oficialmente** en `main`; no regenerarlo, sobrescribirlo, vaciarlo ni publicarlo otra vez.

Modificar exclusivamente las aserciones de pruebas P02–P10 que trataban su inexistencia como requisito, reemplazándolas por comprobaciones pertinentes de **no modificación** del archivo oficial y del uso del motor de inventario. No modificar la lógica de negocio para satisfacer pruebas desactualizadas.

Ejecutar únicamente las pruebas afectadas y dependientes. Evitar ejecutar las 266 pruebas completas salvo regresión fundamentada.

### C. Catálogos y administración

Comprobar en el flujo real de la interfaz que el inventario publicado se carga y que los formularios de creación de productos permiten seleccionar las tres categorías y tres ubicaciones existentes. Si no funciona, corregir solo la causa identificada. No crear nuevos catálogos ni productos sin autorización.

### D. GitHub API: preparación para guardado real

Verificar que la ruta operativa utiliza `03_Aplicacion/persistencia_github.py`, destino fijo `JunyMSAI/FerreteriaMS`, rama `main`, archivo `03_Aplicacion/inventario.xlsx`, autenticación administrativa, confirmación explícita, validación Excel y control de conflicto SHA.

**Frontera de autorización:** se permite preparar el código y las pruebas simuladas para escritura real, pero **NO cambiar `ESCRITURA_REAL_GITHUB_HABILITADA` a `True`, NO efectuar HTTP PUT real, NO acceder a valores de Secrets ni pedir que sean copiados al chat y NO crear ni publicar productos reales** durante la ejecución autónoma de Antigravity.

Si el código necesita habilitar escrituras en producción, presentar un cambio mínimo, claramente delimitado y reversible, para aprobación expresa posterior del responsable. No usar transportes de prueba como mecanismo de producción; no modificar globalmente APIs de red.

## 4. Verificaciones focalizadas

- Inicio de Streamlit y navegación corregida (pruebas UI P06 o equivalentes afectadas).
- Integridad y lectura del Excel oficial sin modificación ni exposición de secretos.
- Formulario de alta con catálogos existentes.
- Persistencia con simulaciones: confirmación, SHA, errores y protección contra doble envío; solo las pruebas tocadas.
- `git diff --check`, comprobación de configuración y `git status --short`.

**Prueba manual posterior, separada y autorizada por el responsable:** en Streamlit Cloud, habilitar escritura real únicamente después de aprobar el cambio y confirmar respaldo/estado del inventario; crear **un producto de evaluación explícitamente aprobado**, guardar una sola vez y comprobar su aparición en GitHub y en la búsqueda pública. Si falla o el resultado es ambiguo, no repetir automáticamente la escritura. Esta prueba NO está autorizada por este documento para ejecución autónoma.

## 5. Entregables y límites

Crear `05_Resultados/12_Resultado_Despliegue_Streamlit_Cloud.md` con: qué cambió, archivos, pruebas efectivamente ejecutadas y resultados, problemas críticos pendientes, si se modificó el inventario (debe ser **NO**), verificación de compuerta de escritura `False`, estado Git y pasos manuales exactos para la prueba autorizada y P13.

Completar campos de trazabilidad `TASK_ID`, `TASK_DATE`, `TASK_TIME`, `TASK_LEVEL`, `TASK_TITLE`, `USER_REQUEST_ORIGINAL`, `CODEX_UNDERSTANDING`, `CODEX_ACTIONS_TAKEN`. Actualizar historial obligatorio si lo exige `AGENTS.md`, sin cambios ajenos al alcance. `USER_REQUEST_ORIGINAL` debe distinguir textualmente la instrucción de ejecución del usuario del contenido de este prompt; no inventar una cita literal.

**Prohibiciones:** nuevas funcionalidades, refactorización general, mejoras cosméticas fuera de la navegación, Gemini API, cambio de alcance, exponer secretos, escribir en GitHub API, desplegar automáticamente, modificar `inventario.xlsx`, realizar `git add`, `git commit`, `git push`, `git merge`, `git reset`, `git restore` o `git clean`.

Al concluir, detenerse para revisión y aprobación.

## 6. Criterios para aceptar P12

1. Navegación funcional, sin desbordamientos visibles, en escritorio y móvil.
2. Inventario oficial y sus catálogos legibles, sin alteraciones.
3. Administración puede iniciar el flujo de creación usando catálogos válidos.
4. Pruebas afectadas aprobadas y evidencia breve en el informe; problemas bloqueantes identificados.
5. Seguridad y compuerta de escritura real preservadas hasta autorización específica.
6. Cambios limitados a lo imprescindible para entregar, sin trabajos redundantes.

**Nota:** P12 solo podrá declararse «funcionalidad real de guardado verificada» después de completar, por separado, la prueba manual autorizada sobre GitHub y Streamlit Cloud. Hasta ese momento, informar «preparado para activación», no «guardado real comprobado».
