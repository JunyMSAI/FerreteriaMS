# PROMPT 06 — Interfaz responsive y Gemini «Próximamente»

**Proyecto:** FerreteríaMS v0  
**TASK_ID:** `FERMS-V0-P06`  
**Etapa:** Diseño e integración visual de la interfaz pública  
**Agente:** Antigravity dentro de VS Code  
**Repositorio:** `JunyMSAI/FerreteriaMS`  
**Rama:** `main`  
**Directorio:** `C:\Projects\FerreteriaMS`  
**Archivo:** `02_Prompts/06_Interfaz_Responsive_Gemini.md`  

---

## 1. Objetivo general

Desarrollar y verificar la presentación visual responsive de FerreteríaMS v0, sobre la aplicación funcional construida durante los Prompts 01 a 05.

La interfaz debe ofrecer una experiencia clara, sencilla, profesional y consistente para localizar productos de una ferretería desde una computadora, tableta o teléfono.

Se implementarán dos áreas funcionalmente diferenciadas:

1. **Área de inventario:** búsqueda, resultados, detalles y localización física de los productos, utilizando exclusivamente los módulos existentes.
2. **Área visual de Gemini:** sección identificada como **«Próximamente»**, sin capacidades operativas de inteligencia artificial durante v0.

No implementar ni simular respuestas de Gemini como si procedieran de un modelo real.

El objetivo es mejorar la presentación y adaptación a distintos tamaños de pantalla sin modificar la lógica de negocio aprobada.

---

## 2. Documentación obligatoria

Antes de realizar modificaciones, lee y comprende:

- `GEMINI.md`.
- `AGENTS.md`.
- `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`.
- `01_Documentacion/02_Especificaciones_v0.md`.
- `02_Prompts/04_Busqueda_Publica.md`.
- `02_Prompts/05_Detalles_Ubicaciones.md`.
- `05_Resultados/04_Resultado_Busqueda_Publica.md`.
- `05_Resultados/05_Resultado_Detalles_Ubicaciones.md`.
- Este Prompt 06.

Inspecciona los módulos:

- `03_Aplicacion/app.py`.
- `03_Aplicacion/busqueda.py`.
- `03_Aplicacion/inventario.py`.
- `03_Aplicacion/github_inventario.py`.

Consulta las pruebas existentes, especialmente las relacionadas con `AppTest` y estado de sesión.

### Referencias conceptuales

Examina las imágenes integradas en el documento Word, especialmente los bocetos de:

- Pantalla pública inicial.
- Búsqueda y resultados.
- Detalles y localización.
- Área reservada para Gemini.

Distingue las imágenes correspondientes a la visión final de aquellas aplicables a v0.

**Las especificaciones aprobadas de v0 prevalecen sobre cualquier función futura representada en una imagen.**

No alteres el documento Word ni sus imágenes.

---

## 3. Límites del Prompt 06

La tarea es principalmente de **presentación visual, accesibilidad y adaptación responsive**.

Puedes reorganizar la interfaz Streamlit existente para mejorar su presentación.

No reescribas los motores de inventario, búsqueda o GitHub API.

No incorpores nuevas funcionalidades de negocio ni cambios de arquitectura.

Conserva:

- Búsqueda pública exclusivamente por nombre.
- Coincidencias parciales.
- Normalización de acentos y mayúsculas.
- Orden por relevancia.
- Diez resultados por página.
- Selección de producto.
- Detalles generales.
- Ubicación principal y secundarias.
- Navegación de regreso a resultados.
- Manejo de errores.
- Actualización de consultas desde GitHub.
- Protección contra estados de sesión obsoletos.

---

## 4. Requisitos y criterios de aceptación

Revisa las definiciones textuales exactas de los requisitos y criterios en `02_Especificaciones_v0.md`.

Considera especialmente:

- **RF-010:** interfaz adaptable a dispositivos.
- **RF-032, RF-033 y RF-034:** presentación visual de Gemini en v0 y delimitación de su funcionamiento.
- **CA-008:** verificación relacionada con la adaptación de la interfaz.
- **CA-031, CA-032, CA-033 y CA-034:** criterios asociados a la interfaz Gemini según sus definiciones oficiales.

Verifica además que continúen cumpliéndose los criterios anteriores sobre búsqueda, paginación, visualización de productos y ubicaciones.

No atribuyas nuevos significados a los RF o CA.

La instalación PWA queda fuera del MVP actual.

---

## 5. Diseño general de la interfaz

### 5.1. Identidad visual

La aplicación debe presentarse como:

**FerreteríaMS**

Con una apariencia:

- Moderna y profesional.
- Minimalista.
- Fácil de comprender.
- De navegación sencilla.
- Apropiada para clientes de una ferretería.
- Compatible con escritorio y dispositivos móviles.

Puedes proponer mejoras visuales coherentes con las referencias del documento de concepto, sin incorporar funciones no aprobadas.

Evita elementos decorativos innecesarios.

### 5.2. Encabezado

Presentar el nombre de la aplicación con una identidad visual consistente.

Incluir una descripción breve de su propósito: ayudar al cliente a encontrar productos dentro de la ferretería.

No utilizar mensajes comerciales que sugieran venta en línea, existencia de inventario por cantidades o transacciones.

### 5.3. Área de búsqueda

Conservar:

- Campo de búsqueda por nombre.
- Botón Buscar.
- Mensaje inicial.
- Indicador «Buscando productos…».
- Mensajes de error.
- Resultados paginados.

En dispositivos pequeños, el campo y su botón deberán organizarse de forma que ambos sean cómodos de utilizar.

No introducir filtros independientes por categorías, marcas, códigos o ubicaciones.

### 5.4. Resultados

Mejorar la presentación de las tarjetas de productos sin alterar su comportamiento.

Mostrar con claridad:

- Nombre.
- Código.
- Categoría.
- Acción «Ver detalles y ubicación».

Garantizar que los nombres largos no dificulten la lectura ni provoquen desbordamiento horizontal.

Conservar los controles de paginación y su estado.

### 5.5. Detalles y ubicación

Presentar los datos generales del producto y sus ubicaciones de forma visualmente ordenada.

Destacar la ubicación principal.

Diferenciar las ubicaciones secundarias.

Los campos **rack, columna, nivel y posición** deben mantenerse legibles y correctamente identificados.

No modificar la interpretación de la ubicación establecida en el Prompt 05.

El botón para volver a los resultados debe permanecer accesible y conservar el estado de la búsqueda.

---

## 6. Área de Gemini «Próximamente»

### 6.1. Propósito

Reservar visualmente una sección para la futura integración de Gemini, sin activar sus capacidades.

La sección deberá identificarse con un encabezado reconocible, por ejemplo:

**Asistente Gemini**

Y mostrar claramente:

**Próximamente**

### 6.2. Contenido permitido

La sección podrá contener un mensaje informativo breve explicando que, en una versión futura, se ofrecerá orientación técnica sobre productos y proyectos.

El contenido debe ser descriptivo, no generado por IA.

Se podrá explicar que la funcionalidad todavía no está disponible.

### 6.3. Restricciones

Queda expresamente prohibido:

- Importar o utilizar `google-genai`.
- Llamar a Gemini API.
- Solicitar una API key.
- Crear un cliente de IA.
- Enviar prompts a modelos externos.
- Crear respuestas ficticias presentadas como respuestas de Gemini.
- Almacenar conversaciones.
- Implementar historial de chat.
- Activar un cuadro de conversación funcional.
- Crear controles que parezcan disponibles cuando no lo están.

Si los bocetos muestran controles futuros de conversación, podrán representarse únicamente como elementos informativos no interactivos, siempre que no confundan al usuario.

Es preferible un área informativa clara a un chat simulado.

### 6.4. Integración futura

La implementación deberá facilitar la incorporación posterior de Gemini sin modificar innecesariamente el motor de inventario.

Sin embargo, no se desarrollarán servicios, clientes, endpoints ni mecanismos de comunicación con Gemini durante el Prompt 06.

---

## 7. Comportamiento responsive

### 7.1. Escritorio

En pantallas amplias se utilizará una composición que distribuya adecuadamente:

- Buscador y contenido del inventario.
- Resultados y detalles.
- Área informativa de Gemini «Próximamente».

La distribución preferida es:

**Inventario a la izquierda y Gemini a la derecha**, siempre que el ancho disponible lo permita y coincida con la intención del diseño conceptual aprobado.

### 7.2. Teléfonos

En pantallas pequeñas, la interfaz debe reorganizarse verticalmente:

1. Identificación de FerreteríaMS.
2. Área de búsqueda.
3. Resultados o detalles del producto.
4. Área Gemini «Próximamente».

No utilizar columnas rígidas que obliguen al usuario a desplazarse horizontalmente.

El contenido importante debe permanecer visible y legible.

### 7.3. Tabletas y tamaños intermedios

Adaptar el diseño según el espacio disponible, conservando la jerarquía de contenido y la facilidad de interacción.

### 7.4. Consideraciones técnicas

Evalúa las capacidades reales de la versión instalada de Streamlit antes de decidir cómo implementar el diseño.

Se permite CSS local, limitado y justificado cuando los componentes nativos de Streamlit no sean suficientes.

Evita depender de selectores internos frágiles o comportamientos no documentados si existe una alternativa estable.

No incorporar frameworks frontend adicionales sin autorización.

No agregar JavaScript personalizado salvo necesidad justificada y autorización previa.

### 7.5. PWA

No implementar:

- Service workers.
- Instalación como aplicación.
- Manifest PWA destinado a instalación.
- Funcionalidad offline.

El alcance aprobado es una aplicación web responsive.

---

## 8. Accesibilidad y experiencia de usuario

Mantener como objetivo **WCAG 2.2 AA**, en la medida verificable con los componentes utilizados.

Considerar:

- Contraste suficiente.
- Textos legibles.
- Estructura clara de encabezados.
- Etiquetas accesibles para campos y botones.
- Navegación mediante teclado.
- Indicadores de foco cuando corresponda.
- Mensajes de error comprensibles.
- Elementos táctiles cómodos.
- No depender exclusivamente de colores para comunicar estados.
- Evitar controles que aparenten funcionar cuando están deshabilitados.

No afirmar conformidad completa con WCAG 2.2 AA sin una auditoría suficiente.

Documentar las comprobaciones reales y las pendientes.

---

## 9. Manejo de estados de la aplicación

La mejora visual deberá conservar el funcionamiento de los siguientes estados:

- Inicio sin búsqueda.
- Búsqueda vacía.
- Búsqueda en progreso.
- Productos encontrados.
- Sin coincidencias.
- Inventario no inicializado.
- Error de conexión o autorización.
- Inventario remoto inválido.
- Detalle de producto seleccionado.
- Regreso a resultados.
- Navegación entre páginas.

No mostrar productos de prueba como si procedieran del repositorio oficial.

Una modificación del diseño no deberá provocar descargas adicionales innecesarias de GitHub al cambiar de página o abrir y cerrar detalles.

La vista de Gemini no deberá intervenir en el estado de búsqueda ni requerir consultas a ningún servicio externo.

---

## 10. Pruebas obligatorias

### 10.1. Archivo de pruebas

Crear:

`04_Pruebas/test_06_interfaz_responsive_gemini.py`

Utilizar `unittest`, `AppTest` y otros mecanismos adecuados cuando estén disponibles.

### 10.2. Pruebas funcionales

Comprobar:

1. Renderizado de la aplicación sin errores.
2. Presencia del nombre FerreteríaMS.
3. Presencia del campo de búsqueda.
4. Funcionamiento del botón Buscar.
5. Presentación de tarjetas de resultados.
6. Funcionamiento de la paginación.
7. Selección de productos.
8. Presentación de detalles.
9. Ubicación principal y secundarias.
10. Regreso a resultados.
11. Conservación del estado de búsqueda.
12. Mensajes de error y ausencia de inventario.
13. Presencia del área Gemini «Próximamente».
14. Ausencia de chat Gemini operativo.
15. Ausencia de importaciones o llamadas a Gemini API.
16. Ausencia de controles comerciales y administrativos no autorizados.
17. Ausencia de operaciones remotas de escritura.

### 10.3. Verificaciones visuales

Realizar comprobaciones de presentación cuando el entorno permita observar la interfaz real.

Evaluar los diseños en tamaños representativos de:

- Escritorio.
- Tableta.
- Teléfono.

Comprobar que no existan desbordamientos horizontales importantes y que los controles continúen siendo utilizables.

Si no se dispone de una herramienta adecuada para observar un tamaño de pantalla, dejar esa verificación como **PENDIENTE**, sin sustituirla por una afirmación no comprobada.

### 10.4. Pruebas de regresión

Ejecutar las pruebas anteriores de los Prompts 02, 03, 04 y 05 junto con las nuevas pruebas.

Comando:

`python -m unittest discover -s 04_Pruebas -p "test_*.py" -v`

El último resultado reportado fue de 92 pruebas aprobadas.

Ese número se utiliza únicamente como referencia histórica; el total final deberá ser el número efectivamente ejecutado después de esta tarea.

### 10.5. Verificación local

Ejecutar Streamlit localmente cuando corresponda:

`streamlit run 03_Aplicacion/app.py`

Distinguir un servidor que inicia correctamente de una comprobación visual completa en navegador.

No declarar pruebas de funcionalidad real contra un inventario remoto con productos si `inventario.xlsx` todavía no existe en GitHub.

---

## 11. Archivos autorizados y protegidos

### Archivos autorizados

Se permite crear o modificar localmente:

- `03_Aplicacion/app.py`.
- Un archivo CSS local, si es necesario y está justificado.
- Archivos auxiliares estrictamente necesarios para la presentación visual.
- `04_Pruebas/test_06_interfaz_responsive_gemini.py`.
- `05_Resultados/06_Resultado_Interfaz_Responsive_Gemini.md`.

Se permite ajustar `requirements.txt` únicamente si una dependencia es imprescindible y ya está expresamente justificada dentro del alcance autorizado.

No modificar archivos de lógica de negocio para resolver una dificultad puramente visual.

### Archivos protegidos

No modificar:

- `GEMINI.md`.
- `AGENTS.md`.
- `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`.
- `01_Documentacion/02_Especificaciones_v0.md`.
- `03_Aplicacion/inventario.py`.
- `03_Aplicacion/github_inventario.py`.
- `03_Aplicacion/busqueda.py`.
- `03_Aplicacion/inventario.xlsx`.
- Documentos y prompts anteriores.
- Pruebas e informes de los Prompts 02–05.
- `README.md`.

Si resulta imprescindible cambiar un archivo protegido, detener esa parte y solicitar autorización.

---

## 12. Operaciones permitidas y prohibidas

### Permitidas

- Leer documentación.
- Inspeccionar código y pruebas.
- Modificar la interfaz dentro del alcance autorizado.
- Crear CSS local justificado.
- Ejecutar pruebas locales.
- Ejecutar Streamlit localmente.
- Realizar consultas de solo lectura a GitHub.
- Registrar resultados.
- Consultar el estado de Git.

### Prohibidas

- Crear o modificar el inventario maestro.
- Realizar escrituras mediante GitHub API.
- Agregar Gemini API funcional.
- Implementar login administrativo.
- Implementar mantenimiento de productos, categorías o ubicaciones.
- Añadir compras, pagos, precios o cantidades.
- Implementar PWA instalable.
- Cambiar la arquitectura aprobada.
- Ejecutar `git commit`, `git push` o `git merge`.
- Crear pull requests.
- Realizar despliegues.
- Modificar documentos aprobados.
- Ejecutar el Prompt 07 automáticamente.

---

## 13. Trazabilidad y documentación

Cumplir `AGENTS.md`.

Registrar:

- `TASK_ID`: FERMS-V0-P06.
- Fecha real.
- Hora real.
- Solicitud original íntegra o referencia verificable.
- Interpretación del agente.
- Acciones ejecutadas.
- Archivos creados y modificados.
- RF y CA relacionados.
- Decisiones técnicas.
- Pruebas ejecutadas y resultados.
- Evidencias visuales disponibles.
- Pruebas pendientes.
- Limitaciones.
- Referencia al commit base.
- Estado de Git al finalizar.

Distinguir requisitos aprobados, decisiones técnicas y mejoras visuales propuestas.

No modificar el concepto ni las especificaciones para justificar una decisión de implementación.

---

## 14. Informe de resultados

Crear:

`05_Resultados/06_Resultado_Interfaz_Responsive_Gemini.md`

El informe deberá incluir:

### A. Objetivo y alcance

Qué se implementó y qué quedó expresamente fuera de v0.

### B. Diseño

Descripción de la distribución en escritorio, tableta y teléfono.

Relación con las imágenes conceptuales.

### C. Gemini «Próximamente»

Evidencia de presencia visual y ausencia de funcionalidad operativa.

### D. Verificaciones

| Verificación | RF/CA | Estado | Evidencia |
|---|---|---|---|
| Interfaz de escritorio | RF-010 / CA correspondiente | | |
| Interfaz de tableta | RF-010 / CA correspondiente | | |
| Interfaz móvil | RF-010 / CA-008 | | |
| Área Gemini visual | RF-032–034 / CA relacionados | | |
| Búsqueda y resultados | RF-001–004 | | |
| Detalles y ubicaciones | RF-005–007 | | |
| Estados y errores | RF-008, RF-038 | | |
| Regresión Prompts 02–05 | RF/CA existentes | | |

No completar con «APROBADO» una verificación que no se ejecutó realmente.

### E. Integridad

Registrar los archivos modificados y confirmar que los documentos aprobados y módulos protegidos permanecen sin cambios.

### F. Pendientes

Indicar lo que corresponde al Prompt 07 y siguientes.

### G. Evaluación

Concluir:

- COMPLETADO.
- COMPLETADO CON OBSERVACIONES.
- INCOMPLETO.

Justificar con evidencias comprobables.

---

## 15. Condiciones de finalización

La tarea estará terminada cuando:

1. La interfaz pública tenga una presentación coherente y profesional.
2. Se haya implementado una distribución responsive adecuada dentro de las capacidades de Streamlit.
3. La búsqueda, resultados y detalles sigan funcionando.
4. Gemini figure únicamente como «Próximamente».
5. No exista dependencia operativa de Gemini API.
6. No se hayan incorporado funciones administrativas o comerciales.
7. Se mantenga la arquitectura existente.
8. Se ejecuten las pruebas obligatorias.
9. Las verificaciones visuales realizadas y pendientes estén claramente diferenciadas.
10. Se entregue el informe de trazabilidad.
11. No se modifiquen documentos o módulos protegidos.
12. No se realicen commits, push, merge ni despliegues.
13. El agente espere la revisión y autorización del usuario.

**No ejecutar el Prompt 07.**