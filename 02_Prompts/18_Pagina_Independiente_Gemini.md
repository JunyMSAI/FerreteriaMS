# PROMPT 18 — Página independiente para el Asistente Gemini

**Proyecto:** FerreteríaMS — Versión Final  
**TASK_ID:** FERMS-FINAL-P18  
**TASK_TITLE:** Interfaz independiente y navegación del Asistente Gemini  
**TASK_LEVEL:** Estándar — Cambio focalizado de interfaz 

## 1. Objetivo

Trasladar el Asistente Gemini desde la columna lateral de Inicio a una página independiente, utilizando el ancho disponible para mejorar la lectura y el uso del chat.

**DEC-FINAL-035 aprobada:** Gemini tendrá su propia página, separada de la búsqueda pública, conservando las funcionalidades existentes.

No reconstruir el asistente ni modificar su lógica de negocio.

## 2. Documentos de referencia

Consultar únicamente lo necesario de:

- `GEMINI.md`
- `AGENTS.md`
- `01_Documentacion/03_Especificaciones_Final.md`
- Código actual de `03_Aplicacion/app.py` y `03_Aplicacion/estilos.css`

El presente prompt complementa las especificaciones finales con la decisión DEC-FINAL-035.

## 3. Navegación

La aplicación tendrá tres opciones principales:

1. **Inicio:** búsqueda y localización pública de productos.
2. **Productos:** administración protegida existente.
3. **Asistente Gemini:** página independiente para consultas y asesoría técnica.

Reutilizar el sistema actual de navegación y estado de sesión.

La página Gemini será pública y no requerirá autenticación administrativa.

No modificar los permisos ni las funciones de administración.

## 4. Diseño del Asistente Gemini

Implementar una presentación de ancho completo dentro del contenedor principal de Streamlit.

La página incluirá:

- Encabezado «Asistente Gemini».
- Aviso fijo de que la IA puede cometer errores.
- Área amplia de conversación.
- Mensajes del cliente y del asistente claramente diferenciados.
- Historial temporal de la sesión.
- Campo cómodo para escribir preguntas.
- Botón «Enviar consulta».
- Botón «Nueva conversación».
- Indicador del límite de consultas.

**Evitar que las respuestas largas aumenten indefinidamente la altura de la página.**

Utilizar un contenedor de conversación con altura apropiada y desplazamiento vertical interno, conservando una presentación adecuada en escritorio y móvil.

Aprovechar los componentes nativos de Streamlit cuando sean suficientes. No incorporar dependencias nuevas sin necesidad.

Las respuestas deben presentarse con formato legible, respetando títulos, párrafos y listas; no mostrar caracteres Markdown como texto literal cuando puedan renderizarse correctamente.

## 5. Integración con la búsqueda pública

Conservar el comportamiento aprobado en DEC-FINAL-017 y DEC-FINAL-020:

- El cliente podrá seleccionar un producto desde Inicio.
- Gemini recibirá ese producto como contexto cuando corresponda.
- El usuario podrá abrir la página Gemini sin perder la referencia del producto seleccionado.
- Al seleccionar otro producto, se actualizará el contexto sin confundir los datos ni borrar innecesariamente la conversación.

No crear un segundo motor de búsqueda.

La página Inicio podrá ofrecer un acceso sencillo a «Asistente Gemini», reutilizando la navegación principal.

## 6. Funcionalidades que deben conservarse

No modificar el comportamiento ya implementado de:

- Conexión con Gemini API.
- Modelo configurado.
- Respuestas en español e inglés.
- Asesoría sobre herramientas y proyectos.
- Restricción a temas de ferretería.
- Productos registrados y recomendaciones generales.
- Seguridad técnica y aviso de IA.
- Límites de consumo.
- Nueva conversación.
- Manejo de errores.
- Protección de secretos.

La reorganización visual no debe reiniciar los contadores de uso ni perder innecesariamente el historial temporal.

## 7. Implementación mínima

Modificar preferentemente:

- `03_Aplicacion/app.py`
- `03_Aplicacion/estilos.css`, únicamente si es necesario.

Reutilizar `03_Aplicacion/asistente_gemini.py` sin modificar su lógica, salvo que se identifique una dependencia indispensable para conservar el estado al navegar.

No crear un sistema de páginas adicional si el mecanismo actual puede utilizarse de forma sencilla.

## 8. Pruebas focalizadas

Comprobar exclusivamente:

1. Navegación entre Inicio, Productos y Asistente Gemini.
2. Renderizado del chat en una página independiente y de mayor ancho.
3. Lectura de respuestas largas sin crecimiento vertical excesivo de la página.
4. Adaptación a escritorio y móvil.
5. Conservación del historial temporal y los límites de uso al navegar.
6. Transferencia correcta del producto seleccionado al asistente.
7. Ausencia de regresiones críticas en la búsqueda y administración.

Utilizar simulaciones de Gemini API cuando corresponda.

No repetir las suites completas de v0, P14, P15, P16 o P17 sin justificación técnica concreta.

## 9. Restricciones

- No modificar `inventario.xlsx`.
- No realizar escrituras GitHub API.
- No utilizar ni mostrar credenciales.
- No realizar consultas reales a Gemini durante las pruebas automatizadas.
- No cambiar el modelo Gemini.
- No añadir funcionalidades nuevas.
- No rediseñar las pantallas de administración.
- No efectuar refactorizaciones generales.
- No realizar commit, push ni despliegue.

## 10. Informe de resultados

Crear:

`05_Resultados/18_Resultado_Pagina_Independiente_Gemini.md`

Registrar los campos de trazabilidad obligatorios de `AGENTS.md`.

Informar:

- Cambios realizados.
- Archivos modificados.
- Pruebas focalizadas y resultados.
- Problemas críticos pendientes, si existen.
- Resultado de `git status --short`.

Detenerse para revisión y aprobación.

## 11. Criterios de aceptación

P18 estará preparado para aprobación cuando:

1. Gemini tenga una página independiente de ancho completo.
2. Inicio conserve la búsqueda pública sin la columna lateral del chat.
3. El chat sea cómodo de utilizar y leer.
4. Las respuestas largas tengan desplazamiento interno.
5. La navegación conserve el contexto temporal y el producto seleccionado.
6. Las funcionalidades existentes sigan operando.
7. Las pruebas focalizadas resulten satisfactorias.

**No iniciar otras funcionalidades sin autorización.**