# PROMPT 19 — Página «Acerca de FerreteríaMS»

**Proyecto:** FerreteríaMS  
**TASK_ID:** FERMS-FINAL-P19  
**TASK_TITLE:** Incorporación de la página informativa «Acerca de FerreteríaMS»  

---

## 1. Objetivo

Incorporar una nueva sección pública llamada **«Acerca de»** dentro de FerreteríaMS.

Su propósito es explicar de manera profesional, clara y sencilla qué es FerreteríaMS, qué problema resuelve, sus principales funcionalidades y cómo utilizarla.

La nueva página debe conservar la identidad visual de la aplicación y reutilizar la navegación existente.

**No reconstruir funcionalidades previamente implementadas.**

## 2. Documentos de referencia

Consultar únicamente lo necesario de:

- `GEMINI.md`
- `AGENTS.md`
- `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`
- `01_Documentacion/03_Especificaciones_Final.md`
- `02_Prompts/18_Pagina_Independiente_Gemini.md`
- `03_Aplicacion/app.py`
- `03_Aplicacion/estilos.css`

Respetar las decisiones funcionales ya aprobadas y los cambios manuales recientes del usuario.

## 3. Navegación principal

Incorporar «Acerca de» como cuarta opción de la navegación superior.

El orden final de los botones debe ser exactamente:

1. **🏠 Inicio**
2. **✨ Asistente**
3. **⚙️ Configuración**
4. **ℹ️ Acerca de**

Importante:

- El usuario ha realizado o está realizando modificaciones manuales a los nombres y al orden de los botones.
- Inspeccionar primero el código actual y conservar esos cambios.
- Los nombres «Asistente» y «Configuración» son exclusivamente etiquetas de navegación.
- No renombrar módulos, identificadores internos, constantes, claves de sesión ni secciones administrativas por motivos cosméticos.
- No alterar las reglas de autenticación de Configuración.
- La nueva página «Acerca de» será pública y no requerirá inicio de sesión.

La navegación deberá permitir entrar y salir de «Acerca de» sin afectar el historial temporal de Gemini, los límites de consultas ni el estado administrativo existente.

## 4. Contenido de la nueva página

Utilizar el siguiente contenido como texto oficial, conservando su significado y tono profesional.

### 4.1. Encabezado

**Acerca de FerreteríaMS**

*Encuentra lo que necesitas. Aprende cómo utilizarlo.*

### 4.2. ¿Qué es FerreteríaMS?

FerreteríaMS es una aplicación diseñada para mejorar la experiencia de los clientes dentro de una ferretería, facilitando la búsqueda de productos, su localización física y el acceso a orientación técnica mediante inteligencia artificial.

Nuestro objetivo es facilitar la búsqueda de herramientas y materiales, ofreciendo una forma rápida y sencilla de localizar productos y obtener información útil para realizar diferentes proyectos.

### 4.3. ¿Qué puedes hacer con FerreteríaMS?

**Buscar productos fácilmente**

Encuentra artículos por su nombre, incluso utilizando palabras parciales, y consulta los productos registrados en el catálogo de la ferretería.

**Conocer su ubicación exacta**

Identifica dónde se encuentra registrado cada producto mediante su rack, columna, nivel y posición, sin tener que recorrer innecesariamente toda la tienda.

**Recibir orientación con inteligencia artificial**

Consulta al asistente sobre herramientas, materiales, métodos de uso, precauciones y recomendaciones para realizar reparaciones o proyectos. Puedes comunicarte en español o inglés.

### 4.4. ¿Cómo funciona?

1. Escribe el nombre del producto que necesitas en el buscador.
2. Selecciona el producto para consultar sus detalles y ubicación en la tienda.
3. Si necesitas orientación adicional, accede al Asistente y describe lo que deseas realizar.
4. Consulta las recomendaciones y verifica las instrucciones de seguridad antes de comenzar tu proyecto.

### 4.5. Nuestro propósito

Queremos que la tecnología facilite las tareas cotidianas, ayudando a las personas a encontrar lo que necesitan y a comprender mejor las herramientas y materiales que utilizan.

**FerreteríaMS combina localización de productos y orientación inteligente en una misma experiencia.**

### 4.6. Nota informativa

Incluir al final de la página, con presentación discreta:

> Las recomendaciones generadas por inteligencia artificial pueden contener errores y no sustituyen las instrucciones del fabricante ni la asesoría de un profesional cualificado. La información del catálogo no confirma cantidades disponibles en inventario.

## 5. Diseño y presentación

Implementar una página visualmente coherente con FerreteríaMS:

- Encabezado claramente identificado.
- Secciones separadas visualmente sin exceso de elementos decorativos.
- Tipografía legible.
- Espaciado equilibrado.
- Iconos discretos cuando mejoren la comprensión.
- Contenido organizado en un orden lógico.
- Utilizar componentes nativos de Streamlit siempre que resulten adecuados.

Evitar textos excesivamente grandes, tarjetas innecesarias o una presentación sobrecargada.

La página debe adaptarse razonablemente al espacio disponible, pero **no afirmar compatibilidad móvil perfecta ni añadir publicidad sobre dispositivos móviles**.

## 6. Exclusiones expresas

No incluir en la página:

- Listas de bibliotecas Python.
- Versiones de dependencias.
- Reconocimientos de tecnologías.
- Referencias de copyright o licencias de terceros.
- Información sobre herramientas de programación.
- Descripciones del proyecto como académico.
- Credenciales, información interna de administración ni datos sensibles.
- Afirmaciones sobre cantidades, existencias físicas o precios que el inventario no gestiona.

La gestión de licencias de bibliotecas Python, si fuera necesaria, se atenderá por separado en la documentación técnica del repositorio. **No crear ni modificar archivos de avisos legales como parte de P19.**

Tampoco incluir la sección «Acceder desde distintos dispositivos», eliminada expresamente por decisión del usuario.

## 7. Implementación técnica

Realizar una modificación mínima y focalizada.

Archivos preferentes:

- `03_Aplicacion/app.py`
- `03_Aplicacion/estilos.css`, únicamente si hacen falta estilos adicionales.

Tareas:

1. Identificar el mecanismo actual de navegación.
2. Incorporar una nueva sección interna para «Acerca de».
3. Añadir el cuarto botón al menú existente.
4. Crear la función de renderizado correspondiente.
5. Integrar el contenido aprobado.
6. Mantener las secciones anteriores y sus comportamientos.

No incorporar dependencias nuevas, rutas innecesarias ni otro mecanismo de navegación si el existente permite implementar la funcionalidad.

## 8. Funcionalidades que deben permanecer intactas

No modificar:

- Búsqueda pública de productos.
- Detalles y localización de productos.
- Archivo maestro `inventario.xlsx`.
- Administración de productos, categorías y ubicaciones.
- Autenticación y sesiones.
- Persistencia mediante GitHub API.
- Modelo y configuración de Gemini.
- Conversaciones y límites del asistente.
- Manejo de errores y protección de secretos.

La pantalla «Acerca de» será exclusivamente informativa y no tendrá funciones de escritura o modificación de datos.

## 9. Pruebas focalizadas

Verificar:

1. La existencia del botón «Acerca de» en cuarta posición.
2. La secuencia correcta: Inicio → Asistente → Configuración → Acerca de.
3. El funcionamiento de los cuatro botones de navegación.
4. El acceso público a «Acerca de».
5. La presentación completa del contenido aprobado.
6. La ausencia de la sección sobre dispositivos y de reconocimientos de tecnologías.
7. La conservación del estado de Gemini al navegar.
8. Que la sección Configuración conserve la protección administrativa existente.
9. Que el archivo Excel y las funcionalidades principales no sufran cambios.

Realizar únicamente las pruebas necesarias para esta modificación.

No ejecutar suites extensas ni consultas reales a Gemini salvo necesidad técnica justificada y autorización.

## 10. Restricciones de ejecución

- No modificar el inventario.
- No cambiar las especificaciones del proyecto.
- No añadir funcionalidades adicionales.
- No refactorizar módulos que ya funcionan.
- No alterar los cambios manuales aprobados del menú.
- No utilizar credenciales reales en pruebas.
- No realizar escrituras mediante GitHub API.
- No efectuar commit ni push.
- No publicar cambios en Streamlit Cloud.

## 11. Informe de resultados

Crear el documento:

`05_Resultados/19_Resultado_Pagina_Acerca_de_FerreteriaMS.md`

Incluir los campos de trazabilidad establecidos en `AGENTS.md`, además de:

- Objetivo ejecutado.
- Cambios realizados.
- Archivos modificados.
- Resultado de las pruebas focalizadas.
- Problemas pendientes, únicamente si son relevantes.
- Resultado de `git status --short`.

No modificar todavía `01_Documentacion/04_Definicion_de_Prompts.md`. Su actualización se realizará después de aceptar P19, incorporando la descripción correspondiente.

## 12. Criterios de aceptación

P19 se considerará listo para revisión cuando:

1. Exista una página independiente «Acerca de».
2. El menú tenga cuatro botones en el orden aprobado.
3. La página muestre todos los textos oficiales.
4. No incluya referencias a bibliotecas, tecnologías o carácter académico.
5. No incluya afirmaciones sobre compatibilidad móvil.
6. Las secciones existentes conserven su funcionamiento.
7. Las pruebas focalizadas sean satisfactorias.
8. Antigravity entregue el informe correspondiente.

**Al finalizar, detenerse y esperar la aprobación del usuario antes de registrar o publicar los cambios.**