# GEMINI.md — FerreteríaMS

**Proyecto:** FerreteríaMS
**Etapa activa:** FerreteríaMS — Versión Final
**Agente de desarrollo:** Gemini (Antigravity)

## Instrucciones del proyecto

Este archivo es el punto de entrada a las instrucciones de desarrollo de FerreteríaMS.

Antes de realizar cualquier tarea, el agente (Gemini / Antigravity) deberá cargar y seguir las instrucciones del documento rector `AGENTS.md`:

@./AGENTS.md

## Documentos oficiales de referencia

Los documentos aprobados para la etapa activa son:

1. `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx` — Concepto general, objetivos, alcance e imágenes conceptuales de FerreteríaMS.
2. `01_Documentacion/02_Especificaciones_v0.md` — Especificaciones de referencia para las funcionalidades, validaciones y controles ya desarrollados en v0.
3. `01_Documentacion/03_Especificaciones_Final.md` — Especificaciones incrementales aprobadas para la versión final (`RF-F`, `CA-F`, restricciones y fuera de alcance).
4. `AGENTS.md` — Documento rector con las reglas permanentes de desarrollo, seguridad, trazabilidad, pruebas y control de cambios.

El agente deberá consultar estos documentos antes de realizar tareas de programación.

## Ejecución de tareas

Las tareas se ejecutarán mediante prompts autorizados y organizados en `02_Prompts/`.

El agente deberá:

- Trabajar exclusivamente en la etapa y bloque autorizados.
- Conservar sin reconstruir ni modificar innecesariamente las funcionalidades terminadas en v0.
- Cumplir los requisitos y criterios de aceptación aplicables (`RF`/`CA` y `RF-F`/`CA-F`).
- Respetar la estructura de carpetas y archivos aprobada.
- Ejecutar pruebas focalizadas sobre las funcionalidades nuevas o directamente afectadas.
- Documentar las acciones realizadas y los resultados.
- Registrar evidencias en las carpetas correspondientes.
- Solicitar autorización antes de realizar cambios de alcance, `commit`, `push`, `merge` o despliegues.

Las instrucciones específicas de comportamiento, seguridad y autorización se encuentran en `AGENTS.md` y no se duplican en este documento.

## Orden de desarrollo de la versión final

La implementación de las funcionalidades aprobadas en `01_Documentacion/03_Especificaciones_Final.md` se organizará secuencialmente en dos bloques:

1. **Bloque 1:** Administración de categorías, ubicaciones y estados de productos.
2. **Bloque 2:** Integración de Gemini con el inventario.

Ninguno de los dos bloques deberá iniciarse sin el prompt de desarrollo correspondiente y la autorización expresa.