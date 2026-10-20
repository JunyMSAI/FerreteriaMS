# PROMPT 05 — Detalles y localización física de productos

**Proyecto:** FerreteríaMS v0  
**TASK_ID:** FERMS-V0-P05  
**Etapa:** Consulta pública de detalles y ubicaciones  
**Agente:** Antigravity dentro de VS Code  
**Repositorio:** `JunyMSAI/FerreteriaMS`  
**Rama de referencia:** `main`  
**Directorio local:** `C:\Projects\FerreteriaMS`  
**Archivo del prompt:** `02_Prompts/05_Detalles_Ubicaciones.md`  

---

## 1. Objetivo general

Desarrollar la funcionalidad que permita seleccionar un producto desde los resultados de búsqueda de FerreteríaMS y consultar sus detalles y ubicación física en la ferretería.

El usuario deberá poder identificar con claridad:

- Código del producto.
- Nombre del producto.
- Categoría.
- Descripción.
- Ubicación principal: rack, columna, nivel y posición.
- Ubicaciones secundarias, cuando existan.

La aplicación deberá utilizar las estructuras y relaciones ya validadas por `inventario.py`, sin crear un mecanismo independiente para interpretar las asignaciones de ubicación.

El resultado deberá integrarse en la aplicación pública Streamlit desarrollada en el Prompt 04.

**No implementar administración, escritura remota, inventario definitivo ni Gemini API operativo.**

---

## 2. Lectura y verificación previa obligatoria

Antes de modificar código, consulta íntegramente los documentos vigentes:

- `GEMINI.md`
- `AGENTS.md`
- `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`
- `01_Documentacion/02_Especificaciones_v0.md`
- `02_Prompts/04_Busqueda_Publica.md`
- `05_Resultados/04_Resultado_Busqueda_Publica.md`
- Este Prompt 05.

Revisa también, para conocer los contratos y estructuras existentes:

- `03_Aplicacion/app.py`
- `03_Aplicacion/busqueda.py`
- `03_Aplicacion/inventario.py`
- `03_Aplicacion/github_inventario.py`
- Las pruebas automatizadas de los Prompts 02, 03 y 04.

Confirma que el estado Git no presenta modificaciones inesperadas antes de comenzar.

Si existe trabajo pendiente sin confirmar de una tarea anterior, informa al usuario antes de modificar archivos.

### Referencia visual

Consulta las imágenes conceptuales incluidas en el documento Word aprobado.

Utilízalas como guía para organizar los detalles de producto y la presentación de ubicaciones.

La imagen conceptual no debe prevalecer sobre los requisitos funcionales y criterios de aceptación del documento oficial.

No modificar dibujos conceptuales ni documentación aprobada.

---

## 3. Requisitos funcionales

Implementa principalmente las funcionalidades definidas en la documentación aprobada para:

- **RF-004:** presentación de resultados y acceso al producto.
- **RF-005:** detalles del producto.
- **RF-006:** ubicación principal.
- **RF-007:** ubicaciones secundarias.
- **RF-009:** acceso público sin autenticación.

Mantén la compatibilidad con los requisitos de búsqueda existentes, incluyendo:

- RF-001, RF-002 y RF-003.
- RF-008.
- RF-024, RF-025 y RF-028.
- RF-035, RF-036, RF-037 y RF-038.

Identifica en las especificaciones oficiales los criterios de aceptación exactos correspondientes a selección, detalles y ubicaciones, incluyendo **CA-005**, y conserva su redacción y significado.

No atribuyas a un RF o CA comportamientos que no estén realmente definidos en el documento.

---

## 4. Selección de productos

### 4.1. Selección desde resultados

Cada producto que aparezca en la búsqueda pública deberá ofrecer una acción clara para consultar sus detalles.

Puedes utilizar un botón denominado:

`Ver detalles y ubicación`

La acción deberá identificar el producto mediante `Codigo_Producto`, conservándolo como texto, incluidos los ceros iniciales.

No utilizar la posición visual en la lista como identificador único.

### 4.2. Un producto seleccionado

Cuando el usuario seleccione un producto:

1. Registrar el código seleccionado en el estado de sesión correspondiente.
2. Recuperar la información desde el inventario validado de la búsqueda activa.
3. Presentar el detalle del producto correcto.
4. Mantener la búsqueda y página actual cuando sea apropiado.
5. Permitir regresar a los resultados.

No consultar nuevamente GitHub solo por abrir o cerrar el detalle de un producto ya obtenido de una búsqueda válida.

### 4.3. Cambios de búsqueda

Si el usuario realiza una búsqueda nueva:

- Descartar la selección anterior.
- No mostrar detalles de un producto de una consulta previa.
- Utilizar el inventario vigente de la nueva consulta.
- Evitar referencias obsoletas entre diferentes versiones del inventario.

Respeta la limpieza y consistencia de `st.session_state` implementada durante la corrección del Prompt 04.

### 4.4. Selección inválida

Si el código seleccionado no pertenece al inventario validado de la búsqueda activa, no mostrar información perteneciente a otro producto.

Comunicar que el producto seleccionado no está disponible en la consulta actual y permitir regresar a los resultados.

No inventar datos ni ubicaciones.

---

## 5. Presentación de información del producto

La vista de detalle deberá mostrar los valores originales almacenados en el inventario.

### Campos

| Campo | Origen |
|---|---|
| Código | `Productos.Codigo_Producto` |
| Nombre | `Productos.Nombre` |
| Categoría | Relación con `Categorías` |
| Descripción | `Productos.Descripcion` |

Mantener la identidad del producto utilizando el código original.

No convertir automáticamente los códigos a números.

No incluir precios, cantidades, disponibilidad de stock, ventas ni recomendaciones generadas por IA.

Si una descripción es opcional y está vacía conforme al esquema aprobado, utilizar una presentación neutra sin inventar información.

---

## 6. Ubicación principal

La ubicación principal deberá obtenerse a partir de las relaciones oficiales entre:

- `Productos`
- `Asignaciones`
- `Ubicaciones`

Utiliza la marca `Principal` de la hoja `Asignaciones`, conforme a los valores definidos en las especificaciones.

### Información requerida

La interfaz deberá mostrar:

**Ubicación principal**

- Rack.
- Columna.
- Nivel.
- Posición.

Se podrá utilizar una disposición visual clara, como:

`Rack R01 → Columna C02 → Nivel N03 → Posición P04`

Este ejemplo es ilustrativo y no representa información real de la ferretería.

Nunca mostrar estos valores de ejemplo como si pertenecieran al inventario operativo.

### Reglas

- No calcular ubicaciones basándose en el orden de las filas.
- No asumir que la primera ubicación de un producto es necesariamente la principal.
- Utilizar la asignación marcada como principal en el inventario validado.
- No cambiar ni guardar ubicaciones.
- No reinterpretar valores de rack, columna, nivel o posición.

Si se detecta una inconsistencia que normalmente debería haber sido rechazada por `inventario.py`, comunicarla como un problema de integridad y no intentar corregirla silenciosamente.

---

## 7. Ubicaciones secundarias

Cuando un producto tenga varias ubicaciones válidas:

1. Mostrar primero la ubicación principal.
2. Mostrar las ubicaciones secundarias claramente diferenciadas.
3. Presentar rack, columna, nivel y posición de cada una.
4. Evitar duplicar la ubicación principal en la lista secundaria.
5. Utilizar un orden estable y reproducible.

Cuando no haya ubicaciones secundarias, no mostrar ubicaciones ficticias.

Puedes ocultar la sección secundaria o indicar de forma discreta que el producto solamente tiene una ubicación registrada, según resulte más claro y coherente con el concepto aprobado.

La existencia de ubicaciones secundarias no significa que existan múltiples unidades en inventario; no mostrar cantidades ni disponibilidad.

---

## 8. Integración con los módulos existentes

### 8.1. Motor de inventario

Reutiliza `InventarioDatos` y las funciones existentes de `inventario.py`, especialmente las que ya permiten recuperar información estructurada por código.

No vuelvas a implementar las relaciones entre las cuatro hojas.

### 8.2. Motor de búsqueda

Reutiliza `ProductoCoincidente` y la información de producto preparada en `busqueda.py`.

Antes de añadir funciones, comprueba si la información requerida ya está disponible en sus estructuras.

Mantén la búsqueda por nombre como único mecanismo de búsqueda pública.

No introducir filtros por categoría, marca, código o ubicación.

### 8.3. Integración de GitHub

Continúa utilizando `github_inventario.py` exclusivamente para lectura.

La vista de detalle debe utilizar el inventario validado de la búsqueda activa.

Si el inventario remoto no existe, está corrupto o no puede descargarse, no mostrar productos demostrativos como si fueran datos oficiales.

### 8.4. Estado de sesión

Mantener consistentes:

- Término de búsqueda activo.
- Página actual.
- Respuesta estructurada de la búsqueda.
- Inventario validado de la consulta.
- SHA remoto asociado.
- Código del producto seleccionado.

Evitar que se muestre información de una versión anterior después de ejecutar otra búsqueda.

No romper las correcciones incorporadas al final del Prompt 04.

---

## 9. Organización de la interfaz

En este incremento se autoriza integrar una vista de detalle sencilla y funcional.

La organización deberá:

- Respetar la identidad visual inicial de FerreteríaMS.
- Mantener visible una forma clara de regresar a los resultados.
- Diferenciar visualmente los detalles generales y las ubicaciones.
- Destacar la ubicación principal.
- Presentar correctamente varias ubicaciones.
- Evitar información excesiva o controles innecesarios.

La adaptación responsive integral se completará en el Prompt 06.

No utilizar componentes que dependan de Gemini API ni introducir una interfaz administrativa.

La selección y el detalle deberán funcionar dentro de la experiencia pública, sin exigir inicio de sesión.

---

## 10. Pruebas obligatorias

Crear:

`04_Pruebas/test_05_detalles_ubicaciones.py`

Utilizar `unittest` y, cuando corresponda, `streamlit.testing.v1.AppTest`.

### Pruebas funcionales

Verificar:

1. Selección de un producto desde resultados.
2. Identificación correcta mediante código.
3. Conservación de códigos con ceros iniciales.
4. Presentación de nombre, categoría y descripción.
5. Obtención de rack, columna, nivel y posición principales.
6. Distinción entre ubicación principal y secundaria.
7. Producto con una sola ubicación.
8. Producto con varias ubicaciones.
9. Ausencia de duplicaciones entre ubicaciones.
10. Orden estable de ubicaciones secundarias.
11. Regreso desde detalle hacia los resultados.
12. Conservación de página y término de búsqueda.
13. Eliminación de la selección al comenzar otra búsqueda.
14. Prevención de detalles obsoletos tras errores remotos.
15. Manejo de códigos de producto inválidos.
16. Ausencia de controles administrativos o de venta.

### Pruebas de integración

Verificar:

- Compatibilidad con `inventario.py`.
- Compatibilidad con `busqueda.py`.
- Uso del inventario previamente validado en sesión.
- Ausencia de descargas innecesarias al abrir detalles.
- Distinción entre inventario real y datos demostrativos.
- Ausencia de modificaciones al archivo maestro.
- Ausencia de operaciones remotas de escritura.

### Pruebas de regresión

Ejecutar todas las pruebas existentes de los Prompts 02, 03 y 04, junto con las del Prompt 05:

`python -m unittest discover -s 04_Pruebas -p "test_*.py" -v`

Registrar el total real ejecutado, las pruebas aprobadas, fallidas y no ejecutadas.

### Verificación Streamlit

Cuando sea posible, ejecutar localmente:

`streamlit run 03_Aplicacion/app.py`

Verificar el flujo de selección, detalle, ubicaciones y regreso a resultados.

Debido a que el inventario maestro todavía puede no existir en GitHub, utilizar mocks o datos demostrativos controlados para validar la funcionalidad sin publicarlos como inventario oficial.

No declarar como verificada una consulta real de detalle de producto si no se ha descargado efectivamente un inventario remoto que contenga productos.

---

## 11. Archivos autorizados

Se autoriza modificar o crear localmente:

- `03_Aplicacion/app.py`.
- `03_Aplicacion/busqueda.py`, únicamente si se requiere una adaptación pequeña y justificada para integrar detalles.
- Un módulo nuevo de detalles dentro de `03_Aplicacion/`, si mejora la separación de responsabilidades y está justificado.
- `04_Pruebas/test_05_detalles_ubicaciones.py`.
- Archivos auxiliares de pruebas estrictamente necesarios.
- `05_Resultados/05_Resultado_Detalles_Ubicaciones.md`.

No introducir un módulo nuevo si la funcionalidad puede implementarse limpiamente reutilizando las estructuras existentes.

### Archivos protegidos

No modificar:

- `GEMINI.md`.
- `AGENTS.md`.
- `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`.
- `01_Documentacion/02_Especificaciones_v0.md`.
- `03_Aplicacion/inventario.py`.
- `03_Aplicacion/github_inventario.py`.
- `03_Aplicacion/inventario.xlsx`.
- Los prompts existentes.
- Las pruebas e informes de los Prompts 02, 03 y 04.
- `requirements.txt`, salvo autorización adicional.
- `README.md`.

Si alguna modificación protegida resulta imprescindible, detener esa parte y solicitar autorización.

---

## 12. Restricciones y permisos

### Operaciones autorizadas

- Leer documentación y código.
- Modificar los archivos locales permitidos.
- Crear pruebas e informe.
- Ejecutar pruebas locales.
- Iniciar Streamlit localmente.
- Realizar consultas de solo lectura a GitHub.
- Consultar el estado de Git.

### Operaciones prohibidas

- Crear o modificar `inventario.xlsx`.
- Ejecutar solicitudes de escritura en GitHub API.
- Introducir autenticación administrativa.
- Implementar gestión de productos, categorías o ubicaciones.
- Implementar Gemini API funcional.
- Crear o publicar tokens y secretos.
- Ejecutar commits, push o merge.
- Crear pull requests.
- Desplegar en Streamlit Community Cloud.
- Modificar documentos oficiales.
- Comenzar el Prompt 06 automáticamente.

No realizar cambios fuera del alcance autorizado.

---

## 13. Trazabilidad obligatoria

Cumple las reglas de `AGENTS.md`.

Registrar como mínimo:

- `TASK_ID`: FERMS-V0-P05.
- Fecha real de ejecución.
- Hora real de ejecución.
- Título y nivel de tarea conforme a las reglas del proyecto.
- Solicitud original del usuario, preservada literalmente o mediante referencia íntegra verificable al prompt.
- Interpretación del agente.
- Acciones realizadas.
- Archivos creados y modificados.
- RF y CA relacionados.
- Pruebas ejecutadas y evidencias.
- Resultados pendientes.
- Limitaciones y observaciones.
- Commit base.
- Estado Git al finalizar.

Mantener diferenciadas las decisiones aprobadas por el usuario y las decisiones técnicas del agente.

---

## 14. Informe de resultados

Crear:

`05_Resultados/05_Resultado_Detalles_Ubicaciones.md`

Incluir:

### A. Objetivo y alcance

Funcionalidades implementadas y restricciones respetadas.

### B. Integración técnica

Explicar cómo se utilizan `inventario.py`, `busqueda.py`, `github_inventario.py` y `app.py`.

### C. Interfaz pública

Describir la selección de productos, la visualización de detalles, la ubicación principal, las ubicaciones secundarias y el regreso a resultados.

### D. Pruebas

Incluir una tabla como la siguiente:

| Prueba | RF/CA | Resultado | Evidencia |
|---|---|---|---|
| Selección de producto | RF-004 | | |
| Datos generales | RF-005 | | |
| Ubicación principal | RF-006 | | |
| Ubicaciones secundarias | RF-007 | | |
| Persistencia de búsqueda | RF relacionados | | |
| Limpieza de selección obsoleta | RF relacionados | | |
| Integración Streamlit | CA relacionados | | |
| Regresión de Prompts 02–04 | RF/CA existentes | | |

Completar las referencias exactas tras verificar las especificaciones aprobadas.

### E. Integridad y seguridad

Confirmar los archivos modificados y las restricciones respetadas.

### F. Pendientes

Registrar funcionalidades reservadas para el Prompt 06 y tareas posteriores.

### G. Evaluación

Concluir con:

- COMPLETADO.
- COMPLETADO CON OBSERVACIONES.
- INCOMPLETO.

Justificar el estado con pruebas reales y verificables.

---

## 15. Condiciones de finalización

El Prompt 05 estará completado cuando:

1. Un producto pueda seleccionarse desde los resultados.
2. Se presenten correctamente sus datos generales.
3. Se visualice la ubicación principal completa.
4. Se visualicen las ubicaciones secundarias sin duplicaciones.
5. Se preserve correctamente el estado de búsqueda.
6. No aparezcan detalles obsoletos después de cambiar la búsqueda.
7. Se reutilicen los módulos existentes.
8. No se modifique el inventario maestro.
9. No existan operaciones remotas de escritura.
10. Las pruebas estén ejecutadas y documentadas.
11. Se conserve el funcionamiento de los Prompts 02, 03 y 04.
12. Se entregue el informe de trazabilidad.
13. El agente espere autorización antes de comenzar otra etapa.

**No ejecutar el Prompt 06.**