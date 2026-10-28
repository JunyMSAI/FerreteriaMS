# PROMPT 16 — Integración funcional de Gemini

**Proyecto:** FerreteríaMS — Versión Final  
**TASK_ID:** FERMS-FINAL-P16  
**TASK_TITLE:** Integración de Gemini AI con FerreteríaMS  


## 1. Objetivo

Implementar un asistente Gemini funcional, basado en texto, para proporcionar asesoría técnica sobre productos, herramientas, materiales, reparaciones y proyectos relacionados con una ferretería.

Reutilizar la interfaz, el motor de búsqueda y el inventario ya existentes.

**No reconstruir las funcionalidades de FerreteríaMS v0 ni del Bloque 1.**

## 2. Documentos de referencia

Consultar:

- `GEMINI.md`
- `AGENTS.md`
- `01_Documentacion/03_Especificaciones_Final.md`
- `01_Documentacion/02_Especificaciones_v0.md`, solamente para compatibilidad.

**Requisitos aplicables:** RF-F-012 a RF-F-025.  
**Criterios de aceptación:** CA-F-010 a CA-F-019.

La implementación debe respetar las decisiones aprobadas DEC-FINAL-002, DEC-FINAL-009 a DEC-FINAL-023, DEC-FINAL-030 y DEC-FINAL-033 a DEC-FINAL-034.

## 3. Integración de Gemini API

- Integrar Gemini mediante Python, utilizando el SDK oficial compatible.
- Ejecutar las llamadas desde el servidor Streamlit.
- Obtener la clave API exclusivamente desde Streamlit Secrets o variables de entorno seguras.
- No exponer la clave al navegador ni incluirla en código, registros o documentación.
- No incorporar otro backend, base de datos ni infraestructura adicional.
- Verificar la disponibilidad y condiciones vigentes del nivel gratuito antes de seleccionar un modelo.
- No habilitar facturación ni servicios de pago.

La búsqueda pública deberá funcionar independientemente de Gemini.

## 4. Chat de texto

Utilizar el área visual de Gemini existente en FerreteríaMS.

Implementar:

1. Campo para escribir preguntas.
2. Presentación de respuestas en el chat.
3. Preguntas de seguimiento durante la sesión.
4. Historial temporal limitado y configurable.
5. Botón «Nueva conversación».
6. Detección automática de español o inglés.
7. Cambio de idioma mediante instrucciones del cliente.

No guardar conversaciones permanentemente.

El botón «Nueva conversación» deberá borrar los mensajes y el contexto temporal, pero no reiniciar los límites de consumo de la sesión.

No implementar voz, imágenes ni cuentas de clientes.

## 5. Asesoría técnica y alcance temático

Gemini responderá únicamente sobre temas relacionados con:

- Ferretería y herramientas.
- Materiales de construcción.
- Instalación y reparación.
- Mantenimiento.
- Mejoras del hogar.
- Proyectos de carpintería, plomería, electricidad y áreas relacionadas.
- Seguridad, utilización y almacenamiento de productos.

Cuando reciba consultas claramente ajenas a estos temas, indicará amablemente su especialización y redirigirá la conversación.

No utilizar otro modelo de inteligencia artificial exclusivamente para clasificar preguntas.

## 6. Integración con el inventario

Reutilizar el motor de búsqueda existente para obtener productos relacionados con la consulta del cliente.

Gemini deberá:

1. Priorizar productos activos registrados en FerreteríaMS cuando sean técnicamente adecuados.
2. Utilizar sus nombres, códigos, descripciones y ubicaciones confirmadas.
3. Recibir el producto seleccionado por el cliente como contexto.
4. Actualizar esa referencia cuando cambie la selección, conservando la conversación.
5. Evitar mezclar características de productos distintos.
6. Recomendar también materiales o herramientas no registrados cuando sean necesarios para resolver correctamente un problema.
7. Distinguir claramente productos registrados de recomendaciones generales.
8. No inventar códigos, ubicaciones, cantidades ni disponibilidad física.

**Principio fundamental:** la calidad, pertinencia y seguridad de la asesoría prevalecerán sobre la intención de recomendar productos de la tienda.

Gemini tendrá acceso de solo lectura al contexto del inventario y no podrá ejecutar operaciones administrativas.

## 7. Aviso permanente y seguridad técnica

Mostrar de forma visible en el chat:

> Este asistente utiliza inteligencia artificial y puede cometer errores. Verifica la información técnica y sigue las instrucciones del fabricante. Para trabajos que impliquen riesgos, consulta a un profesional cualificado.

El aviso permanecerá visible durante la conversación.

Ante preguntas técnicas potencialmente peligrosas, Gemini deberá reconocer incertidumbre, solicitar datos indispensables cuando corresponda y comunicar precauciones apropiadas.

No presentar recomendaciones inciertas como garantías técnicas.

## 8. Límites de consumo

Implementar límites sencillos y configurables para:

- Cantidad de preguntas por ventana de uso de la sesión.
- Longitud máxima de preguntas.
- Cantidad de mensajes recientes enviados como contexto.
- Longitud de las respuestas, cuando lo permita la API.

Cuando se alcance el límite de consultas, bloquear nuevas solicitudes hasta la siguiente ventana de uso.

La búsqueda pública continuará funcionando.

No reiniciar el contador mediante «Nueva conversación».

Los límites por sesión son una protección básica y no garantizan una cuota global entre todos los usuarios.

## 9. Manejo de errores

Mostrar mensajes comprensibles ante:

- Clave API inexistente o inválida.
- Servicio Gemini no disponible.
- Tiempo de espera agotado.
- Cuota gratuita agotada.
- Errores de conexión o respuesta.

Permitir reintentar manualmente cuando corresponda, sin generar solicitudes duplicadas innecesarias.

No mostrar excepciones con secretos ni fallos técnicos internos al cliente.

La búsqueda y localización deberán mantenerse operativas.

## 10. Implementación eficiente

Reutilizar los componentes existentes.

Agregar únicamente los módulos, dependencias y controles necesarios.

Evitar:

- Refactorizaciones generales.
- Nuevas pantallas innecesarias.
- Bases de datos de conversaciones.
- Sistemas avanzados de memoria.
- Funcionalidades multimodales.
- Auditorías extensas.
- Repetición de pruebas aprobadas no afectadas.

Actualizar `requirements.txt` únicamente con las dependencias indispensables.

## 11. Pruebas focalizadas

Utilizar simulaciones de Gemini API, sin credenciales reales.

Comprobar:

1. Preguntas de ferretería en español e inglés.
2. Preguntas de seguimiento.
3. Restricción de consultas ajenas a ferretería.
4. Contexto del producto seleccionado y cambio de selección.
5. Recomendaciones de productos registrados y no registrados.
6. Exclusión de productos inactivos.
7. Aviso permanente de IA y precauciones técnicas.
8. Nueva conversación y preservación del contador de uso.
9. Límites de preguntas, tamaño de entrada e historial temporal.
10. Manejo de errores y continuidad de la búsqueda pública.
11. Ausencia de exposición de credenciales.

No repetir suites completas de v0, P14 o P15 salvo impacto directo de una modificación.

## 12. Restricciones de ejecución

Durante esta etapa:

- No utilizar la clave real de Gemini API.
- No realizar solicitudes reales a Gemini.
- No activar servicios de pago.
- No modificar `inventario.xlsx`.
- No realizar escrituras GitHub API.
- No modificar la administración existente.
- No iniciar nuevas funcionalidades.
- No ejecutar commit, push ni despliegue.
- No cambiar especificaciones aprobadas.

La activación real se realizará posteriormente, con autorización expresa.

## 13. Informe de resultados

Crear:

`05_Resultados/16_Resultado_Integracion_Gemini.md`

Registrar la trazabilidad exigida por `AGENTS.md`, los archivos modificados, las pruebas ejecutadas y sus resultados.

Indicar expresamente qué funciona con simulaciones y qué queda pendiente de verificar mediante Gemini API real.

Al finalizar, presentar:

- Funcionalidades implementadas.
- Archivos creados o modificados.
- Pruebas focalizadas ejecutadas.
- Resultados y errores críticos.
- Configuración necesaria para activar Gemini.
- Resultado de `git status --short`.

Detenerse y esperar aprobación.

## 14. Criterios de aceptación

P16 podrá considerarse implementado cuando:

1. El chat funcione con simulaciones de Gemini.
2. Utilice correctamente productos activos del inventario.
3. Permita asesoría sobre productos no registrados sin inventar datos del catálogo.
4. Mantenga el contexto temporal y el producto seleccionado.
5. Aplique los límites y controles de seguridad aprobados.
6. Gestione errores sin afectar la búsqueda.
7. Mantenga protegidos los secretos.
8. Las pruebas focalizadas finalicen satisfactoriamente.

La **activación real de Gemini** y su comprobación en Streamlit Community Cloud requerirán una autorización posterior.

**No comenzar tareas posteriores sin aprobación del responsable.**