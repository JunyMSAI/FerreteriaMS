# PROMPT 04 — Construcción de la búsqueda pública de productos

**Proyecto:** FerreteríaMS v0  
**Identificador:** `FERMS-V0-P04`  
**Etapa:** Desarrollo de la búsqueda pública  
**Agente:** Antigravity dentro de VS Code  
**Repositorio:** `JunyMSAI/FerreteriaMS`  
**Rama de referencia:** `main`  
**Directorio local:** `C:\Projects\FerreteriaMS`  
**Archivo del prompt:** `02_Prompts/04_Busqueda_Publica.md`  
**Estado:** Pendiente de aprobación y autorización de ejecución

---

## 1. Objetivo general

Desarrollar la primera interfaz funcional de búsqueda pública de FerreteríaMS v0 utilizando Streamlit.

Adaptar la plantilla académica existente en `03_Aplicacion/app.py` para convertirla en una aplicación orientada a localizar productos dentro de una ferretería.

La aplicación deberá permitir buscar productos exclusivamente por nombre, presentar coincidencias parciales, ordenar los resultados según la relevancia aprobada y mostrar hasta diez productos por página.

Se deberán reutilizar los módulos existentes:

- `03_Aplicacion/inventario.py`
- `03_Aplicacion/github_inventario.py`

No duplicar sus responsabilidades de lectura, validación ni comunicación con GitHub API.

Este prompt autoriza la modificación local de `app.py` para construir la interfaz de búsqueda, sin incorporar todavía las funcionalidades administrativas ni Gemini operativo.

---

## 2. Documentación obligatoria

Antes de implementar, consulta íntegramente:

1. `GEMINI.md`.
2. `AGENTS.md`.
3. `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`.
4. `01_Documentacion/02_Especificaciones_v0.md`.
5. `02_Prompts/02_Motor_Inventario.md`.
6. `02_Prompts/03_Lectura_GitHub.md`.
7. `05_Resultados/02_Resultado_Motor_Inventario.md`.
8. `05_Resultados/03_Resultado_Lectura_GitHub.md`.
9. Este Prompt 04.

Inspecciona también el código de `app.py`, `inventario.py`, `github_inventario.py` y las pruebas existentes.

No modifiques los documentos oficiales aprobados.

Utiliza las imágenes conceptuales del documento Word como referencia visual para la pantalla pública.

Si existe una contradicción entre una imagen ilustrativa y un requisito aprobado, respeta el comportamiento definido en las especificaciones y comunica la observación.

---

## 3. Requisitos funcionales aplicables

Implementar y verificar:

| Requisito | Descripción |
|---|---|
| RF-001 | Búsqueda por nombre |
| RF-002 | Coincidencias parciales |
| RF-003 | Ignorar diferencias de mayúsculas y acentos |
| RF-004 | Presentación de resultados |
| RF-008 | Mensaje cuando no existen coincidencias |
| RF-009 | Búsqueda pública sin autenticación |
| RF-035 | Orden por relevancia |
| RF-036 | Diez resultados por página |
| RF-037 | Manejo de búsqueda vacía |
| RF-038 | Manejo de errores de consulta |
| RF-024 | Reutilización de los datos procesados por pandas |
| RF-025 | Lectura del inventario almacenado en GitHub |
| RF-028 | Consulta de información vigente sin reiniciar Streamlit |

RF-005, RF-006 y RF-007 corresponden a la presentación completa de detalles y ubicaciones, que se desarrollará específicamente durante el Prompt 05.

RF-010, relacionado con la adaptación responsive integral, se completará durante el Prompt 06.

RF-032, RF-033 y RF-034, relacionados con el área visual «Próximamente» de Gemini, también se completarán durante el Prompt 06.

---

## 4. Criterios de aceptación

Los criterios principales serán:

| CA | Verificación |
|---|---|
| CA-001 | Encontrar un producto registrado |
| CA-002 | Encontrar coincidencias parciales |
| CA-003 | Ignorar diferencias de mayúsculas |
| CA-004 | Ignorar diferencias de acentos |
| CA-006 | Mostrar mensaje cuando no se encuentra un producto |
| CA-007 | Permitir búsquedas sin iniciar sesión |
| CA-039 | Priorizar productos cuyos nombres comienzan con el término |
| CA-040 | Mostrar hasta diez resultados por página |
| CA-041 | Manejar búsquedas vacías |
| CA-042 | Distinguir errores técnicos de búsquedas sin coincidencias |
| CA-043 | No ofrecer controles independientes para buscar por marca o categoría |

Los criterios CA-024 y CA-036 permanecerán sujetos a las verificaciones integradas y de despliegue que correspondan a etapas posteriores.

No marques como aprobado ningún criterio que no se haya comprobado mediante pruebas.

---

## 5. Etapa A — Adaptación de la plantilla académica app.py

### 5.1. Archivo principal

Trabaja sobre:

`03_Aplicacion/app.py`

Este archivo contiene la plantilla original proporcionada por el profesor.

No la utilices sin adaptarla porque actualmente funciona como un chat conectado a Gemini API.

### 5.2. Transformaciones necesarias

Adapta el archivo para que:

1. Utilice Streamlit como interfaz principal.
2. Identifique la aplicación como FerreteríaMS.
3. Presente un campo de búsqueda por nombre de producto.
4. Permita ejecutar la búsqueda mediante el botón Buscar.
5. Muestre los resultados obtenidos.
6. Maneje adecuadamente estados y errores.
7. Mantenga el código organizado y comprensible.

Retira del funcionamiento v0:

- Importaciones de `google-genai`.
- Exigencia de `GEMINI_API_KEY`.
- Llamadas a `generate_content`.
- Interfaz de chat funcional.
- Cualquier otra dependencia operativa de Gemini API.

### 5.3. Conservación académica

Antes de modificar `app.py`, revisa su estructura original e identifica qué conceptos pueden reutilizarse, como:

- Inicialización de Streamlit.
- Configuración de la página.
- Presentación de títulos y componentes.
- Uso apropiado de `st.session_state`.
- Manejo de errores.

En el informe de resultados explica qué elementos se conservaron, cuáles fueron adaptados y cuáles se retiraron debido al alcance aprobado de v0.

No es necesario conservar código de chat que no corresponda a FerreteríaMS.

No modifiques la plantilla del profesor en otros archivos que no estén expresamente autorizados.

---

## 6. Etapa B — Motor de búsqueda por nombre

### 6.1. Separación de responsabilidades

Implementa la lógica de búsqueda de forma que pueda probarse sin ejecutar la interfaz Streamlit.

Puedes crear un módulo específico, por ejemplo:

`03_Aplicacion/busqueda.py`

Su responsabilidad será recibir información estructurada y devolver coincidencias ordenadas y paginadas.

El módulo no deberá conectarse directamente con GitHub ni duplicar las validaciones del motor Excel.

### 6.2. Búsqueda exclusivamente por nombre

Las coincidencias deberán calcularse utilizando el campo `Nombre` de la hoja Productos.

No se implementarán búsquedas independientes por:

- Marca.
- Categoría.
- Código.
- Descripción.
- Ubicación.

La aplicación podrá mostrar códigos y categorías como información de los resultados, pero no serán campos de búsqueda.

### 6.3. Normalización de texto

La búsqueda deberá ignorar:

- Diferencias entre letras mayúsculas y minúsculas.
- Diferencias de acentuación.

Ejemplos:

- `martillo` deberá coincidir con `Martillo`.
- `ELECTRICO` deberá coincidir con `Eléctrico`.
- `destornillador` deberá encontrar productos cuyo nombre contenga ese término.

Utiliza una normalización consistente entre el texto introducido y los nombres de productos.

No modifiques los nombres originales del inventario al normalizarlos para la búsqueda.

### 6.4. Coincidencias parciales

Se encontrarán los productos cuyos nombres contengan el término buscado, aunque no coincida con el nombre completo.

La búsqueda no deberá exigir coincidencia exacta.

### 6.5. Orden por relevancia

Aplicar exactamente el criterio aprobado:

1. Primero, productos cuyos nombres comiencen con el término buscado.
2. Después, productos cuyos nombres contengan el término en otra posición.

Dentro de cada grupo deberá existir un orden estable y reproducible.

Puedes utilizar el nombre normalizado y un identificador estable para resolver empates, sin cambiar el criterio principal de relevancia.

### 6.6. Paginación

Mostrar como máximo diez resultados por página.

Permitir que el usuario navegue entre las páginas disponibles.

La paginación deberá:

- Conservar la búsqueda activa.
- Respetar el orden establecido.
- Evitar duplicar resultados entre páginas.
- Manejar correctamente la última página.
- Reiniciarse cuando el usuario ejecute una búsqueda diferente.

No mostrar controles de paginación innecesarios cuando todos los resultados quepan en una página.

---

## 7. Etapa C — Interfaz pública de búsqueda

### 7.1. Pantalla inicial

Utiliza la imagen conceptual de la pantalla de inicio v0 como referencia.

La interfaz deberá incluir:

- Identificación de FerreteríaMS.
- Texto introductorio breve y comprensible.
- Campo para introducir el nombre del producto.
- Botón Buscar.
- Área para mostrar resultados.
- Mensajes adecuados según el estado de la consulta.

No presentar FerreteríaMS como tienda de ventas en línea.

### 7.2. Antes de buscar

Mostrar un mensaje inicial orientado al cliente, por ejemplo:

«Escribe el nombre del producto que deseas encontrar».

No presentar una lista de resultados ficticios como si ya se hubiera consultado el inventario real.

### 7.3. Durante la búsqueda

Mostrar un indicador comprensible, como:

«Buscando productos…»

No mostrar resultados anteriores como si correspondieran a una consulta nueva todavía pendiente.

### 7.4. Resultados encontrados

Presentar una lista clara de productos coincidentes.

En esta etapa podrá mostrarse:

- Código del producto.
- Nombre del producto.
- Categoría.

La presentación completa de las descripciones, ubicaciones principales y secundarias se desarrollará durante el Prompt 05.

Prepara una separación que permita integrar posteriormente la selección del producto y sus detalles sin reescribir el motor de búsqueda.

### 7.5. Sin resultados

Mostrar exactamente:

«No encontramos este producto en nuestro inventario».

Este mensaje solo se utilizará cuando la consulta haya terminado correctamente y no existan coincidencias.

No deberá utilizarse ante errores de conexión, inventario corrupto o archivo maestro inexistente.

### 7.6. Búsqueda vacía

Cuando el usuario presione Buscar sin introducir un nombre, solicitar que escriba el nombre de un producto.

No intentar realizar una consulta de productos utilizando un término vacío.

### 7.7. Errores técnicos

Cuando ocurra un error al consultar GitHub o procesar el inventario:

- Mostrar un mensaje comprensible.
- Distinguir el problema de una búsqueda sin coincidencias.
- Permitir un nuevo intento.
- Evitar mostrar detalles sensibles, tokens o trazas internas al usuario.

---

## 8. Etapa D — Lectura del inventario desde GitHub

### 8.1. Fuente de datos

La versión operativa de la búsqueda utilizará como fuente de información el inventario maestro vigente almacenado en:

Repositorio: `JunyMSAI/FerreteriaMS`  
Rama: `main`  
Archivo: `03_Aplicacion/inventario.xlsx`

Deberá reutilizar el módulo:

`03_Aplicacion/github_inventario.py`

### 8.2. Estados obligatorios

La aplicación deberá distinguir entre:

**Inventario existente y válido:** permite realizar la búsqueda.

**Inventario confirmado como inexistente:** informa que el inventario todavía no ha sido inicializado.

**Error de conexión o autorización:** comunica un error técnico y permite reintentar.

**Inventario remoto inválido o corrupto:** informa que no puede procesarse correctamente.

Ninguno de estos estados autoriza a modificar GitHub.

### 8.3. Situación actual del proyecto

Durante el Prompt 03, Antigravity informó que `inventario.xlsx` todavía no existe en GitHub.

Vuelve a consultar su estado cuando corresponda.

No supongas que continúa sin existir únicamente porque esa fue la situación durante una tarea anterior.

### 8.4. Uso de datos demostrativos

Para desarrollar y probar la búsqueda podrás utilizar los datos demostrativos en memoria generados por `crear_inventario_demostrativo()`.

Sin embargo:

- Los datos de prueba deberán permanecer separados del funcionamiento normal de la aplicación.
- No se mostrarán automáticamente a los clientes como si fueran el inventario oficial de GitHub.
- No se escribirá el inventario demostrativo en el archivo maestro.
- No se activará un modo de simulación pública permanente sin autorización.
- No se sustituirá silenciosamente un error remoto por resultados demostrativos.

Las pruebas automatizadas podrán invocar directamente el motor de búsqueda utilizando esos datos ficticios.

### 8.5. Información vigente

Las búsquedas deben poder consultar los cambios confirmados en GitHub sin exigir un reinicio manual de Streamlit.

No almacenes indefinidamente una copia del inventario que impida reconocer cambios posteriores.

Evita llamadas innecesarias, pero no comprometas la vigencia de los datos.

Documenta cualquier estrategia de actualización que utilices.

---

## 9. Restricciones funcionales de v0

No implementar durante este prompt:

- Login administrativo.
- Administración de productos.
- Formularios para crear o editar inventario.
- Asignación o eliminación administrativa de ubicaciones.
- Escritura mediante GitHub API.
- Creación del archivo maestro definitivo.
- Precios.
- Cantidades o existencias.
- Carritos de compra.
- Facturación.
- Ventas.
- Búsquedas independientes por marca o categoría.
- Gemini API funcional.
- Asesoría técnica generada por IA.
- Instalación PWA.

La interfaz detallada de ubicaciones y la adaptación visual responsive completa estarán reservadas para los Prompts 05 y 06.

No incorpores funcionalidades adicionales por iniciativa propia.

---

## 10. Etapa E — Pruebas automatizadas

### 10.1. Organización

Crea pruebas correspondientes al Prompt 04 dentro de:

`04_Pruebas/`

Utiliza un archivo con nombre compatible con `unittest`, por ejemplo:

`test_04_busqueda_publica.py`

Las pruebas deberán ejecutarse sobre datos controlados, sin depender de llamadas reales de escritura a GitHub.

### 10.2. Pruebas funcionales

Comprueba:

1. Búsqueda por nombre completo.
2. Búsqueda por parte del nombre.
3. Búsqueda sin diferencias entre mayúsculas y minúsculas.
4. Búsqueda sin diferencias de acentuación.
5. Prioridad de coincidencias al inicio del nombre.
6. Coincidencias que aparecen en otras posiciones.
7. Orden reproducible.
8. Diez resultados por página.
9. Navegación entre páginas.
10. Última página con menos de diez resultados.
11. Reinicio de paginación al cambiar el término.
12. Búsqueda vacía.
13. Búsqueda sin coincidencias.
14. Ausencia de búsqueda por marca o categoría.

### 10.3. Pruebas de integración

Comprueba:

- Uso de datos estructurados por `inventario.py`.
- Compatibilidad con `github_inventario.py`.
- Manejo del inventario inexistente.
- Manejo de errores de GitHub.
- Manejo del inventario remoto inválido.
- Ausencia de escrituras remotas.
- Ausencia de dependencias operativas de Gemini API.

### 10.4. Pruebas de regresión

Ejecuta las pruebas existentes de los Prompts 02 y 03 junto con las nuevas pruebas del Prompt 04.

Comando de referencia:

`python -m unittest discover -s 04_Pruebas -p "test_*.py" -v`

Registra el número real de pruebas ejecutadas, aprobadas y fallidas.

No declares aprobadas pruebas que no fueron ejecutadas.

### 10.5. Verificación de la aplicación

Ejecuta la aplicación localmente cuando el código esté preparado:

`streamlit run 03_Aplicacion/app.py`

Verifica que:

- La aplicación puede iniciarse sin Gemini API key.
- No intenta llamar a Gemini API.
- La interfaz de búsqueda se presenta correctamente.
- Cuando falta el inventario maestro, se muestra el estado correspondiente.
- No hay controles de venta ni administración.
- La aplicación no modifica GitHub.

Si una funcionalidad solo puede comprobarse con datos simulados, documéntalo.

No declares completadas pruebas visuales o de interacción que no pudiste realizar realmente.

---

## 11. Archivos autorizados

Se autoriza crear o modificar localmente:

- `03_Aplicacion/app.py`.
- Un módulo de búsqueda dentro de `03_Aplicacion/`.
- Archivos auxiliares estrictamente necesarios para la búsqueda.
- Pruebas del Prompt 04 dentro de `04_Pruebas/`.
- El informe del Prompt 04 dentro de `05_Resultados/`.
- `requirements.txt`, únicamente cuando una dependencia nueva esté justificada.

### Archivos protegidos

No modificar:

- `GEMINI.md`.
- `AGENTS.md`.
- `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`.
- `01_Documentacion/02_Especificaciones_v0.md`.
- `03_Aplicacion/inventario.py`.
- `03_Aplicacion/github_inventario.py`.
- `README.md`.
- Los prompts anteriores y el propio Prompt 04.
- Las pruebas e informes existentes de los Prompts 02 y 03.
- `03_Aplicacion/inventario.xlsx`.

Si un archivo protegido requiere modificaciones, informa del motivo y solicita aprobación antes de realizar cambios.

---

## 12. Operaciones autorizadas y prohibidas

### Autorizadas

- Leer documentación y código existente.
- Adaptar localmente `app.py`.
- Crear el módulo de búsqueda.
- Crear y ejecutar pruebas locales.
- Ejecutar Streamlit localmente para comprobar la interfaz.
- Utilizar datos demostrativos exclusivamente para pruebas controladas.
- Realizar consultas reales de solo lectura a GitHub.
- Registrar resultados y evidencias.
- Consultar el estado local de Git.

### Prohibidas

- Crear, actualizar o eliminar archivos remotos en GitHub.
- Generar o publicar automáticamente `inventario.xlsx`.
- Modificar documentos aprobados.
- Implementar autenticación o administración.
- Incorporar Gemini API funcional.
- Crear secretos o tokens.
- Ejecutar `git commit`, `git push` o `git merge`.
- Crear pull requests.
- Desplegar en Streamlit Community Cloud.
- Ejecutar el Prompt 05 automáticamente.

Las autorizaciones de este prompt no reemplazan las reglas de `AGENTS.md`.

---

## 13. Trazabilidad obligatoria

Registra:

- Identificador `FERMS-V0-P04`.
- Fecha y hora reales de ejecución.
- Título de la tarea.
- Solicitud original íntegra o referencia verificable al prompt conservado.
- Interpretación del agente.
- Acciones realizadas.
- Archivos creados y modificados.
- Requisitos RF relacionados.
- Criterios CA relacionados.
- Pruebas ejecutadas.
- Resultados y evidencias.
- Errores, limitaciones y observaciones.
- Estado del repositorio.
- Referencia al commit base.

Distingue las decisiones técnicas del agente de los requisitos aprobados por el usuario.

No inventes resultados ni modifiques los documentos oficiales para justificar el código.

---

## 14. Informe final

Crea el informe:

`05_Resultados/04_Resultado_Busqueda_Publica.md`

Y entrega también un resumen en Antigravity.

El informe deberá contener:

### A. Preparación y adaptación de app.py

Explica:

- Qué elementos de la plantilla se reutilizaron.
- Qué elementos se modificaron.
- Qué componentes de Gemini API se retiraron.
- Cómo quedó organizada la interfaz inicial.

### B. Motor de búsqueda

Describe:

- Normalización.
- Coincidencias parciales.
- Orden por relevancia.
- Paginación.
- Tratamiento de búsquedas vacías.
- Tratamiento de búsquedas sin resultados.

### C. Integración con GitHub

Indica:

- Cómo se utiliza `github_inventario.py`.
- Estado del inventario remoto observado.
- Manejo de errores.
- Limitaciones pendientes por no existir todavía el archivo maestro.

### D. Pruebas

Incluye:

| Prueba | RF/CA relacionado | Estado | Evidencia |
|---|---|---|---|
| Búsqueda por nombre | RF-001 / CA-001 | | |
| Coincidencias parciales | RF-002 / CA-002 | | |
| Normalización | RF-003 / CA-003, CA-004 | | |
| Orden por relevancia | RF-035 / CA-039 | | |
| Paginación | RF-036 / CA-040 | | |
| Búsqueda vacía | RF-037 / CA-041 | | |
| Sin coincidencias | RF-008 / CA-006 | | |
| Error de consulta | RF-038 / CA-042 | | |
| Acceso público | RF-009 / CA-007 | | |
| Regresión | Prompts 02 y 03 | | |

Añade las demás pruebas realizadas.

### E. Restricciones

Confirma:

- Documentos oficiales sin cambios.
- Motor Excel sin cambios.
- Lector de GitHub sin cambios.
- Inventario maestro no creado ni modificado.
- Sin operaciones remotas de escritura.
- Sin Gemini API funcional.
- Sin interfaz administrativa.
- Sin commit, push, merge o despliegue.

### F. Pendientes

Identifica lo necesario para continuar con:

- Prompt 05 — Detalle y localización de productos.
- Prompt 06 — Interfaz responsive y Gemini visual.
- Integración futura de escritura mediante GitHub API.
- Inicialización autorizada del inventario maestro.

### G. Evaluación

Concluye con uno de estos estados:

- COMPLETADO.
- COMPLETADO CON OBSERVACIONES.
- INCOMPLETO.

Justifica la evaluación con evidencias verificables.

---

## 15. Condición de finalización

El Prompt 04 estará terminado cuando:

1. `app.py` se haya adaptado al alcance de v0.
2. La búsqueda pública por nombre esté implementada.
3. Las coincidencias parciales funcionen.
4. Se ignoren diferencias de mayúsculas y acentos.
5. Se aplique el orden aprobado.
6. La paginación de diez resultados funcione.
7. Se distingan búsquedas sin resultados, inventario no inicializado y errores técnicos.
8. La integración de lectura reutilice los módulos existentes.
9. No existan llamadas operativas a Gemini API.
10. Se hayan ejecutado y documentado pruebas.
11. Los archivos protegidos permanezcan sin modificaciones.
12. No se hayan realizado operaciones remotas de escritura.
13. El agente entregue su informe y espere autorización.

**No comiences el Prompt 05.**