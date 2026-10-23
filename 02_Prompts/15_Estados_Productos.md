# PROMPT 15 — Desactivación y reactivación de productos

**Proyecto:** FerreteríaMS — Versión Final  
**TASK_ID:** FERMS-FINAL-P15  
**TASK_TITLE:** Estados activo/inactivo de productos  
**TASK_LEVEL:** Estándar — implementación focalizada  


## 1. Objetivo

Permitir al administrador desactivar y reactivar productos sin eliminarlos ni perder su información, reutilizando los módulos y la persistencia existentes de FerreteríaMS.

Este prompt completa el Bloque 1 de la versión final.

**No reconstruir funcionalidades que ya funcionan.**

## 2. Documentos de referencia

Consultar:

- `GEMINI.md`
- `AGENTS.md`
- `01_Documentacion/03_Especificaciones_Final.md`
- `05_Resultados/14_Resultado_Administracion_Catalogos.md`

Consultar las especificaciones v0 únicamente para comprobar compatibilidad.

**Requisitos:** RF-F-008, RF-F-009, RF-F-010 y RF-F-011.  
**Criterios de aceptación:** CA-F-007, CA-F-008 y CA-F-009.

## 3. Estados de productos

Implementar el campo lógico `Activo` en la hoja `Productos`, reutilizando la misma representación `"Sí"` / `"No"` introducida en P14 para las ubicaciones.

Aplicar estas reglas:

1. Los productos existentes que no tengan la columna `Activo` se interpretarán como activos.
2. Los productos nuevos serán activos por defecto.
3. El administrador podrá desactivar y reactivar productos.
4. Los productos desactivados conservarán código, nombre, categoría, descripción y asignaciones.
5. `Codigo_Producto` continuará siendo inmutable.
6. No implementar eliminación definitiva.

## 4. Búsqueda pública

- Los productos inactivos no aparecerán en los resultados de búsqueda.
- Tampoco podrán consultarse como artículos activos mediante el detalle público.
- Los productos activos conservarán el comportamiento actual de búsqueda y localización.
- La administración seguirá mostrando los productos inactivos, identificando claramente su estado.

Preparar la consulta del inventario para que Gemini, cuando se implemente en el Bloque 2, utilice únicamente productos activos como referencias del catálogo.

No integrar Gemini API en P15.

## 5. Reactivación e integridad

Antes de reactivar un producto, comprobar que:

- Su categoría siga siendo válida.
- Conserve al menos una ubicación válida y activa.
- Tenga exactamente una ubicación principal.
- No existan asignaciones duplicadas ni referencias inválidas.

Si alguna condición no se cumple, bloquear la reactivación y mostrar una explicación.

Los productos inactivos conservarán sus asignaciones. La desactivación de una ubicación continuará exigiendo que no tenga productos asociados, incluidos los inactivos.

## 6. Administración e interfaz

Incorporar una opción sencilla para cambiar el estado del producto dentro de la administración existente.

Requisitos:

- Mostrar claramente si el producto está activo o inactivo.
- Solicitar confirmación antes de modificar su estado.
- Actualizar el estado local sin publicar automáticamente.
- Reutilizar el botón de publicación GitHub existente.

No crear una pantalla administrativa adicional si puede incorporarse en la sección actual de productos.

## 7. Persistencia y compatibilidad

Reutilizar:

- Las cuatro hojas oficiales de `inventario.xlsx`.
- El motor de lectura, validación y serialización.
- Los cambios locales y borradores existentes.
- La confirmación administrativa.
- El control de concurrencia SHA.
- La publicación mediante GitHub Contents API.

Preservar la compatibilidad con inventarios v0 y los datos existentes.

No crear otra base de datos ni un segundo mecanismo de guardado.

**No modificar el inventario maestro real durante esta tarea.**

## 8. Pruebas focalizadas

Comprobar únicamente:

1. Lectura de productos antiguos sin `Activo`, interpretándolos como activos.
2. Desactivación de un producto sin pérdida de datos ni ubicaciones.
3. Exclusión de productos inactivos de búsqueda y detalle público.
4. Reactivación válida y recuperación de visibilidad pública.
5. Rechazo de reactivación cuando existan relaciones inválidas.
6. Protección de ubicaciones asociadas a productos inactivos.
7. Serialización y lectura del Excel con los nuevos estados.
8. Publicación simulada mediante GitHub, con confirmación y control SHA.

Ejecutar únicamente las pruebas existentes directamente afectadas y las nuevas pruebas necesarias.

No repetir suites completas de v0 ni las pruebas de P14 sin una razón técnica concreta.

## 9. Restricciones

- No implementar nuevas funcionalidades administrativas.
- No añadir desactivación de categorías.
- No implementar eliminación definitiva de productos.
- No modificar la arquitectura aprobada.
- No integrar Gemini API.
- No modificar ni regenerar `03_Aplicacion/inventario.xlsx`.
- No ejecutar escrituras HTTP PUT reales.
- No utilizar ni exponer tokens.
- No realizar commit, push ni despliegue.
- No modificar especificaciones aprobadas.
- No realizar refactorizaciones o mejoras cosméticas.

Si surge una incompatibilidad que requiera cambiar requisitos aprobados, detener la operación afectada e informar.

## 10. Trazabilidad y resultado

Crear:

`05_Resultados/15_Resultado_Estados_Productos.md`

Registrar los campos obligatorios definidos en `AGENTS.md`, incluyendo solicitud original, interpretación, acciones, archivos modificados, pruebas y resultados.

Al finalizar, presentar:

- Funcionalidades implementadas.
- Archivos creados o modificados.
- Pruebas ejecutadas y resultados.
- Riesgos o errores bloqueantes.
- Confirmación de que el inventario maestro no fue modificado.
- Resultado de `git status --short`.

Detenerse para revisión y aprobación.

## 11. Criterios de aceptación

P15 estará listo cuando:

1. Los productos puedan desactivarse y reactivarse desde la administración.
2. Los inactivos no aparezcan en el catálogo público.
3. La información y las asignaciones se conserven.
4. La reactivación respete las reglas de integridad.
5. Los inventarios anteriores sigan siendo compatibles.
6. La publicación simulada utilice los mecanismos GitHub existentes.
7. Las pruebas focalizadas terminen satisfactoriamente.

**No iniciar el Bloque 2 — Gemini sin autorización.**