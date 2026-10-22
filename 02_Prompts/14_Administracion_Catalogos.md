# PROMPT 14 — Administración de categorías y ubicaciones

**Proyecto:** FerreteríaMS — Versión Final  
**TASK_ID:** FERMS-FINAL-P14  
**TASK_TITLE:** Administración de categorías y ubicaciones  
**TASK_LEVEL:** Estándar — implementación focalizada  

## 1. Objetivo

Implementar la administración básica de categorías y ubicaciones físicas desde FerreteríaMS, reutilizando los módulos, validaciones y mecanismos de persistencia existentes.

No desarrollar funcionalidades adicionales ni modificar componentes estables sin necesidad demostrada.

## 2. Documentos obligatorios

Consultar:

- `GEMINI.md`
- `AGENTS.md`
- `01_Documentacion/03_Especificaciones_Final.md`
- `01_Documentacion/02_Especificaciones_v0.md`, exclusivamente cuando sea necesario verificar compatibilidad.

Las especificaciones aprobadas determinan el alcance. No redefinir requisitos.

## 3. Categorías

Permitir al administrador autenticado:

- Consultar las categorías existentes.
- Crear categorías nuevas con identificador único y nombre obligatorio.
- Renombrar categorías conservando `Categoria_ID` inmutable.
- Reflejar automáticamente el nombre actualizado en los productos asociados.
- Rechazar nombres duplicados, ignorando diferencias de mayúsculas, acentos y espacios sobrantes.
- Mostrar mensajes comprensibles ante validaciones fallidas.

No implementar desactivación ni eliminación de categorías.

## 4. Ubicaciones físicas

Permitir al administrador autenticado:

- Consultar las ubicaciones existentes.
- Crear ubicaciones con identificador único y campos Rack, Columna, Nivel y Posición.
- Editar ubicaciones que no tengan productos asociados, manteniendo `Ubicacion_ID` inmutable.
- Rechazar combinaciones físicas duplicadas.
- Desactivar ubicaciones únicamente si no tienen productos asociados.
- Impedir nuevas asignaciones a ubicaciones desactivadas.
- Mostrar claramente cuándo una ubicación no puede modificarse o desactivarse porque está utilizada.

Conservar las asociaciones existentes y exigir reasignación previa cuando corresponda.

No implementar eliminación definitiva, reasignaciones masivas ni modificaciones físicas de ubicaciones utilizadas.

## 5. Inventario y compatibilidad

Reutilizar las cuatro hojas oficiales:

- `Productos`
- `Categorías`
- `Ubicaciones`
- `Asignaciones`

Implementar únicamente las adaptaciones del esquema necesarias para los requisitos aprobados en `03_Especificaciones_Final.md`.

Preservar los datos e identificadores existentes, la integridad referencial y la compatibilidad con el inventario v0.

No regenerar ni sobrescribir el archivo maestro.

## 6. Persistencia en GitHub

Reutilizar el flujo existente de administración y publicación:

- Autenticación y autorización administrativa.
- Modificaciones locales controladas.
- Validación integral antes de publicar.
- Confirmación explícita.
- Control de concurrencia mediante SHA.
- Conservación de cambios ante errores.
- Actualización de las consultas una vez confirmada la publicación.

No desarrollar un segundo mecanismo de almacenamiento ni guardado.

Durante la ejecución autónoma, utilizar únicamente simulaciones para comprobar operaciones de escritura.

## 7. Interfaz

Integrar las operaciones en la administración existente de Streamlit.

Mantener una interfaz sencilla y coherente con FerreteríaMS.

No rediseñar la búsqueda pública, la navegación general ni la sección visual de Gemini.

## 8. Pruebas necesarias

Crear o adaptar solamente las pruebas relacionadas con las nuevas funcionalidades.

Comprobar:

- Creación y renombrado de categorías.
- Rechazo de categorías duplicadas.
- Creación y modificación permitida de ubicaciones.
- Bloqueo de cambios físicos sobre ubicaciones utilizadas.
- Rechazo de ubicaciones duplicadas.
- Desactivación segura de ubicaciones.
- Rechazo de asignaciones a ubicaciones inactivas.
- Preservación de relaciones y datos existentes.
- Publicación simulada mediante el mecanismo GitHub existente.

Verificar únicamente las integraciones directamente afectadas.

No repetir suites completas de v0 sin una justificación técnica concreta.

## 9. Restricciones

- No implementar todavía la desactivación o reactivación de productos; corresponde al Prompt 15.
- No integrar Gemini API; corresponde al segundo bloque.
- No añadir funcionalidades pospuestas o descartadas.
- No introducir nuevas dependencias salvo necesidad justificada.
- No modificar `inventario.xlsx` real.
- No realizar publicaciones HTTP PUT reales durante las pruebas.
- No acceder ni registrar secretos.
- No ejecutar commits, pushes ni despliegues.
- No cambiar documentos conceptuales ni especificaciones aprobadas.

Si surge una incompatibilidad crítica que requiera cambiar el alcance aprobado, informar antes de actuar.

## 10. Trazabilidad y resultados

Crear:

`05_Resultados/14_Resultado_Administracion_Catalogos.md`

Registrar los campos obligatorios de trazabilidad establecidos en `AGENTS.md`, incluyendo solicitud original, interpretación, acciones realizadas, archivos modificados, pruebas ejecutadas y resultados.

Mostrar al finalizar:

- Funcionalidades implementadas.
- Archivos modificados.
- Pruebas ejecutadas y resultado.
- Defectos bloqueantes, si existen.
- Resultado de `git status --short`.

Detenerse para revisión y aprobación.

## 11. Criterios de aceptación

El Prompt 14 se considerará satisfactorio cuando:

1. El administrador pueda crear y renombrar categorías válidas.
2. Pueda crear y editar ubicaciones según las restricciones aprobadas.
3. Se impidan duplicados y cambios que comprometan los productos asociados.
4. Las ubicaciones inactivas no puedan utilizarse para nuevas asignaciones.
5. Los datos anteriores permanezcan intactos.
6. El guardado simulado utilice la persistencia GitHub existente.
7. Las pruebas focalizadas correspondientes finalicen satisfactoriamente.

**No comenzar P15 sin autorización.**