# PROMPT 17 — Activación y validación real de Gemini

**Proyecto:** FerreteríaMS — Versión Final  
**TASK_ID:** FERMS-FINAL-P17  
**TASK_TITLE:** Activación y validación real de Gemini  

## 1. Objetivo

Completar la integración funcional de Gemini mediante una prueba real en Streamlit Community Cloud, reutilizando la implementación aprobada en P16.

Priorizar calidad, seguridad, costo monetario cero y finalización rápida.

No desarrollar funcionalidades nuevas ni repetir las pruebas simuladas ya aprobadas.

## 2. Documentos de referencia

Consultar únicamente lo necesario de:

- `GEMINI.md`
- `AGENTS.md`
- `01_Documentacion/03_Especificaciones_Final.md`
- `05_Resultados/16_Resultado_Integracion_Gemini.md`

Aplicar `RF-F-012` a `RF-F-025` y los criterios de aceptación `CA-F-010` a `CA-F-019`.

## 3. Verificación del servicio gratuito

Antes de activar Gemini:

1. Confirmar en la documentación oficial de Google la disponibilidad del modelo configurado, inicialmente `gemini-2.5-flash`.
2. Verificar que el proyecto y la clave de API pertenezcan efectivamente al nivel gratuito.
3. Comprobar los límites vigentes en Google AI Studio.
4. No activar facturación, suscripciones ni servicios de pago.
5. Si el modelo configurado ya no está disponible en el nivel gratuito, identificar una alternativa gratuita compatible y presentar el cambio mínimo necesario antes de modificarlo.

No asumir que todos los modelos tienen la misma cuota.

## 4. Configuración de la clave API

Preparar la aplicación para recibir la clave de Gemini exclusivamente desde la configuración privada del servidor Streamlit.

Nombre esperado:

`GEMINI_API_KEY`

El responsable configurará la clave directamente en Streamlit Community Cloud.

El agente no deberá solicitar que se pegue la clave en el chat, inspeccionarla, imprimirla, registrarla ni incorporarla al repositorio.

Si se requiere alguna adaptación técnica, limitarla al módulo existente de integración.

## 5. Verificación de compatibilidad

Revisar solamente los componentes afectados por la conexión real:

- `03_Aplicacion/asistente_gemini.py`
- Integración del chat en `03_Aplicacion/app.py`
- Dependencia `google-genai` en `requirements.txt`

Confirmar que el mecanismo de autenticación de la API utilizado por el SDK sea compatible con las claves actualmente emitidas por Google AI Studio.

No modificar la administración, la persistencia GitHub ni el inventario.

## 6. Prueba real controlada

La prueba real será autorizada y ejecutada por el responsable desde Streamlit Community Cloud.

Comprobar mediante una cantidad mínima de consultas:

1. **Consulta técnica en español:** orientación para instalar una repisa, incluyendo herramientas y precauciones.
2. **Consulta relacionada con un producto:** Gemini debe distinguir productos existentes en el catálogo de recomendaciones generales.
3. **Consulta fuera de alcance:** una pregunta claramente ajena a ferretería debe recibir una redirección amable.
4. **Continuidad operativa:** la búsqueda de productos debe continuar funcionando.

Comprobar visualmente que el aviso fijo de inteligencia artificial permanece visible.

No realizar pruebas de carga ni consumir deliberadamente toda la cuota gratuita.

## 7. Manejo de problemas

Si aparece un error:

- Identificar si proviene de credenciales, modelo, cuota, integración o conexión.
- Corregir únicamente la causa demostrada.
- Ejecutar la prueba afectada, sin repetir todo P16.
- Evitar reintentos innecesarios que consuman cuota.
- Mantener la búsqueda pública disponible.

No reemplazar la arquitectura existente ni incorporar servicios adicionales.

## 8. Autorizaciones y restricciones

Este prompt autoriza revisar la preparación técnica y corregir bloqueos mínimos, pero **no autoriza al agente a realizar llamadas reales utilizando credenciales privadas ni a desplegar cambios automáticamente**.

La configuración de Secrets, el despliegue y las consultas reales se realizarán por separado, bajo autorización y supervisión del responsable.

No ejecutar:

- Escrituras sobre `inventario.xlsx`.
- Operaciones de modificación mediante GitHub API.
- Activación de facturación.
- Cambios en funcionalidades ya aprobadas.
- Auditorías generales.
- `git add`, `git commit`, `git push` o despliegues sin autorización.

## 9. Informe de resultados

Crear:

`05_Resultados/17_Resultado_Activacion_Gemini.md`

Registrar:

- Modelo seleccionado y evidencia de las condiciones gratuitas.
- Configuración técnica verificada.
- Cambios indispensables realizados.
- Pruebas ejecutadas y sus resultados.
- Resultados de las pruebas reales proporcionados por el responsable.
- Problemas pendientes, si existen.
- Archivos modificados.
- `git status --short`.

Distinguir pruebas simuladas de pruebas reales.

## 10. Criterios de aceptación

P17 podrá cerrarse cuando:

1. Gemini responda realmente desde Streamlit Community Cloud.
2. Las respuestas estén relacionadas con ferretería y sean técnicamente pertinentes.
3. Se utilice correctamente el contexto del inventario y se distingan recomendaciones generales.
4. La búsqueda continúe funcionando independientemente.
5. El servicio se mantenga dentro del nivel gratuito autorizado.
6. No se expongan secretos.
7. No existan errores críticos conocidos que bloqueen la funcionalidad aprobada.

**Al completar la tarea, detenerse para revisión y aprobación.**

No iniciar funcionalidades nuevas ni otras etapas sin autorización.