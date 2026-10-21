# FERMS-V0-P09 — Gestión administrativa de productos y ubicaciones

**Proyecto:** FerreteríaMS v0  
**Nivel:** Estándar con auditoría reforzada de integridad y seguridad  
**Commit base esperado:** `6cdda82`  


## 1. Objetivo

Implementar las funciones administrativas de gestión de productos y asignaciones de ubicaciones físicas dentro de la sección protegida **Productos** de FerreteríaMS v0.

La implementación debe permitir preparar, consultar, crear y editar registros de inventario en memoria, utilizando el esquema Excel aprobado y las protecciones de autenticación desarrolladas en los Prompts 07 y 08.

**Límite esencial:** el Prompt 09 NO debe guardar modificaciones en GitHub, crear el archivo maestro definitivo ni realizar escrituras remotas. La persistencia definitiva y el control de concurrencia mediante GitHub Contents API se implementarán exclusivamente en el Prompt 10.

## 2. Documentos obligatorios

Antes de modificar archivos, lee íntegramente:

1. `GEMINI.md`
2. `AGENTS.md`
3. `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`
4. `01_Documentacion/02_Especificaciones_v0.md`
5. `02_Prompts/08_Sesiones_Bloqueos_Borradores.md`
6. `05_Resultados/08_Resultado_Sesiones_Bloqueos_Borradores.md`

Inspecciona además los módulos existentes de inventario, búsqueda, lectura GitHub, autenticación y aplicación Streamlit, junto con las pruebas anteriores.

Las especificaciones oficiales y las decisiones conceptuales aprobadas tienen prioridad sobre cualquier interpretación del agente.

No introduzcas requisitos nuevos ni reabras decisiones aprobadas.

## 3. Verificación inicial obligatoria

Antes de implementar:

- Confirma rama `main` y commit base esperado.
- Confirma que la carpeta de trabajo esté limpia.
- Identifica las funciones existentes que pueden reutilizarse.
- Verifica el esquema exacto de las cuatro hojas de Excel.
- Identifica los requisitos funcionales RF y criterios de aceptación CA aplicables.
- Identifica restricciones documentadas que afecten la gestión administrativa.

Si aparecen cambios inesperados o una contradicción material con las especificaciones, detente y solicita autorización.

No hagas operaciones Git que alteren el repositorio.

## 4. Modelo de datos aprobado

Conserva exactamente las cuatro hojas:

### Productos

`Codigo_Producto, Nombre, Categoria_ID, Descripcion`

### Categorías

`Categoria_ID, Nombre_Categoria`

### Ubicaciones

`Ubicacion_ID, Rack, Columna, Nivel, Posicion`

### Asignaciones

`Codigo_Producto, Ubicacion_ID, Principal`

Reglas obligatorias:

- Conservar identificadores como texto, incluidos ceros iniciales.
- No cambiar nombres de hojas ni columnas.
- No incorporar cantidades, precios, ventas, inventario comercial ni campos adicionales.
- Mantener integridad referencial entre productos, categorías, ubicaciones y asignaciones.
- No permitir códigos duplicados.
- Cada producto debe tener al menos una ubicación válida y exactamente una ubicación principal.
- Evitar duplicar asignaciones entre un mismo producto y ubicación.
- Evitar coordenadas físicas duplicadas según las reglas de las especificaciones.
- Conservar el valor aprobado para distinguir asignación principal y secundaria.

Reutiliza las validaciones del motor de inventario existente en lugar de mantener dos interpretaciones incompatibles del esquema.

## 5. Interfaz administrativa

Implementa dentro de la sección protegida **Productos** una interfaz consistente con el diseño responsive existente, pero disponible para operaciones administrativas únicamente en el contexto de escritorio permitido.

### 5.1. Consulta administrativa

Permitir al administrador:

- Visualizar los productos del inventario cargado.
- Buscar y seleccionar un producto para mantenimiento.
- Consultar código, nombre, categoría, descripción y asignaciones físicas.
- Diferenciar ubicación principal de ubicaciones secundarias.
- Identificar claramente si existen modificaciones locales sin guardar.

No confundir los datos de trabajo administrativo con el inventario remoto confirmado en GitHub.

### 5.2. Creación de productos

Formulario para crear productos con:

- Código de producto.
- Nombre.
- Categoría existente.
- Descripción.
- Una o varias ubicaciones existentes.
- Selección explícita de una ubicación principal.

Validar todos los campos y relaciones antes de aceptar la operación.

No permitir crear un producto que carezca de ubicación principal válida.

### 5.3. Edición de productos

Permitir modificar los campos editables aprobados por las especificaciones.

**El código único del producto no debe poder modificarse una vez creado.**

Permitir editar las asignaciones físicas del producto, conservando las reglas de integridad.

Al cambiar la ubicación principal, garantizar que permanezca exactamente una asignación principal.

No efectuar modificaciones parciales si alguna validación falla.

### 5.4. Categorías y ubicaciones

Reutiliza el catálogo existente de categorías y ubicaciones para los formularios de producto.

Implementa únicamente las operaciones de mantenimiento sobre categorías y ubicaciones que estén expresamente previstas para esta etapa en las especificaciones oficiales y el plan aprobado.

No inventes reglas de eliminación, desactivación, reasignación o cambio de identificadores. Cuando una operación esté diferida a otra etapa, mantenla fuera del alcance e identifícala en el informe.

## 6. Motor de edición local

Implementa una capa administrativa separada y comprobable que permita aplicar cambios a una representación temporal del inventario.

Requisitos:

1. Partir de una copia de trabajo del inventario validado.
2. Aplicar las operaciones sobre una copia, nunca modificando inadvertidamente el inventario remoto original.
3. Validar el resultado integral de las cuatro hojas antes de aceptar cada modificación.
4. Rechazar la operación completa cuando exista cualquier inconsistencia.
5. Evitar estados parcialmente modificados.
6. Conservar las modificaciones locales válidas mientras dure la sesión administrativa.
7. Permitir distinguir entre datos originales y datos pendientes de guardar.
8. No convertir un borrador en cambio persistido.
9. No usar `pandas` como almacenamiento persistente autónomo: mantenerlo como motor de manipulación y validación de datos.

La implementación debe preparar una interfaz clara para la futura integración de escritura remota del Prompt 10.

## 7. Integración con autenticación y sesiones

Todas las operaciones de consulta administrativa restringida y modificación local deben exigir autorización efectiva mediante los mecanismos existentes de `autenticacion.py`.

Conservar:

- Autenticación Argon2id.
- Comprobantes criptográficos de un solo uso.
- Firmas HMAC.
- Cinco intentos fallidos.
- Bloqueos progresivos.
- Expiración por inactividad a los 15 minutos.
- Renovación explícita de sesión.
- Revocación de sesiones.
- Restricción administrativa de dispositivo.
- Aislamiento entre sesiones.

Antes de cualquier operación de mantenimiento, verificar autorización vigente en Python.

Registrar actividad administrativa solamente cuando corresponda a una interacción administrativa real.

Una actualización pasiva de Streamlit no debe renovar automáticamente la sesión.

No incorporar caminos alternativos que permitan modificar el inventario sin autorización.

## 8. Borradores administrativos

Integrar los formularios del Prompt 09 con las funciones de borradores existentes del Prompt 08.

Requisitos:

- Permitir conservar modificaciones locales no confirmadas.
- No guardar contraseñas, tokens, hashes ni secretos en borradores.
- Asociar el borrador a la cuenta y sesión autorizadas.
- Mantener la recuperación durante los 15 minutos adicionales tras la expiración de sesión, conforme al Prompt 08.
- Recuperar datos únicamente tras reautenticación válida.
- No revelar borradores a otras sesiones.
- Aplicar la política vigente de descarte al cerrar sesión voluntariamente.
- Diferenciar claramente **borrador temporal**, **cambios locales validados** y **datos persistidos en GitHub**.

Si la arquitectura actual de borradores requiere una adaptación para conservar correctamente formularios y ediciones del Prompt 09, realízala únicamente dentro del alcance aprobado, sin debilitar las garantías existentes.

## 9. Control de conflictos y preparación para el Prompt 10

El Prompt 09 debe preparar los datos necesarios para su posterior publicación, sin realizarla.

Cuando esté disponible, conservar como referencia el SHA del inventario remoto del que partió la edición.

No tratar ese SHA como una confirmación de escritura.

No implementar todavía:

- Solicitudes GitHub Contents API `PUT`.
- Creación definitiva de `inventario.xlsx`.
- Actualización de archivos remotos.
- Resolución remota de conflictos SHA.
- Commits automáticos del inventario.
- Reintentos de escritura remota.

Esas funcionalidades pertenecen al Prompt 10.

## 10. Estados, mensajes y prevención de pérdida de datos

La interfaz debe diferenciar:

- Inventario disponible para consulta y edición local.
- Inventario remoto inexistente.
- Error de conexión.
- Datos remotos inválidos.
- Error de validación administrativa.
- Modificación local válida.
- Cambios locales pendientes de guardar.
- Sesión administrativa expirada.
- Borrador temporal recuperable.

No mostrar mensajes como «Guardado en GitHub» o «Inventario actualizado» cuando solamente se modificó una copia temporal.

Evitar perder ediciones locales por un rerenderizado pasivo de Streamlit.

## 11. Seguridad e integridad

Verifica especialmente:

- Acceso administrativo no autorizado.
- Sesión vencida durante una edición.
- Intentos de cambiar el código de producto.
- Categorías inexistentes.
- Ubicaciones inexistentes.
- Ubicación principal ausente o duplicada.
- Asignaciones duplicadas.
- Productos duplicados.
- Modificaciones parciales ante errores.
- Datos de una sesión mezclados con los de otra.
- Borradores restaurados incorrectamente.
- Campos de texto con caracteres HTML o Markdown especiales.
- Datos presentados en la interfaz sin exposición accidental de información sensible.

La validación del servidor debe ser la autoridad final. No depender únicamente de controles visuales de Streamlit.

## 12. Pruebas obligatorias

Crea un archivo nuevo:

`04_Pruebas/test_09_gestion_administrativa_productos_ubicaciones.py`

Incluye pruebas unitarias y de integración que cubran, como mínimo:

1. Creación válida de un producto.
2. Rechazo de código duplicado.
3. Conservación de ceros iniciales.
4. Validación de nombre y descripción.
5. Rechazo de categoría inexistente.
6. Rechazo de ubicación inexistente.
7. Producto sin ubicación.
8. Producto sin ubicación principal.
9. Producto con dos ubicaciones principales.
10. Producto con ubicaciones secundarias.
11. Duplicación de asignaciones.
12. Edición válida de nombre.
13. Edición válida de descripción.
14. Edición válida de categoría.
15. Intento de modificar código inmutable.
16. Cambio válido de ubicación principal.
17. Eliminación local de una asignación secundaria cuando corresponda.
18. Rechazo de eliminación de la única asignación válida.
19. Integridad referencial.
20. Validación integral de las cuatro hojas.
21. Rechazo atómico de cambios inválidos.
22. Preservación del inventario original.
23. Conservación de cambios locales.
24. Detección de cambios pendientes.
25. Rechazo de operaciones sin login.
26. Rechazo tras expiración de sesión.
27. Restricción del contexto móvil.
28. Aislamiento de sesiones.
29. Creación y restauración de borrador.
30. Rechazo de borradores vencidos.
31. Conservación de la protección contra secretos.
32. Compatibilidad con la interfaz pública.
33. Ausencia de escritura remota.
34. Ausencia de creación del inventario maestro definitivo.
35. Comportamiento correcto cuando GitHub confirma que el inventario no existe.
36. Manejo de errores con mensajes claros.
37. Integración de formularios con `AppTest`.
38. Preservación del área visual Gemini «Próximamente».
39. Regresión de seguridad del Prompt 08.
40. Ausencia de credenciales reales en pruebas y resultados.

Las pruebas deben ser deterministas, utilizar datos sintéticos y no depender de acceso real a GitHub.

Para evitar repetir el congelamiento de Windows:

- Ejecuta primero las pruebas del Prompt 09.
- Ejecuta después las regresiones P02–P08 individualmente.
- Evita lanzar varias suites en paralelo.
- No introduzcas pruebas de estrés intensivas sin autorización.
- Reutiliza las técnicas de optimización criptográfica aprobadas en el Prompt 08, conservando pruebas reales de seguridad.
- Si detectas consumo excesivo o errores, detente y presenta un diagnóstico antes de continuar.

## 13. Archivos permitidos

Puedes crear:

- Un módulo administrativo específico en `03_Aplicacion/`, con nombre claro y responsabilidad delimitada.
- `04_Pruebas/test_09_gestion_administrativa_productos_ubicaciones.py`
- `05_Resultados/09_Resultado_Gestion_Administrativa_Productos_Ubicaciones.md`

Puedes modificar, si es necesario y está justificado:

- `03_Aplicacion/app.py`
- `03_Aplicacion/estilos.css`
- `03_Aplicacion/autenticacion.py`, exclusivamente para integración o ajustes imprescindibles de los borradores aprobados.

No modifiques sin solicitar autorización:

- `AGENTS.md`
- `GEMINI.md`
- Documentos conceptuales ni especificaciones oficiales.
- Prompts anteriores.
- Pruebas o informes de etapas anteriores.
- `requirements.txt`
- `03_Aplicacion/inventario.py`
- `03_Aplicacion/github_inventario.py`
- `03_Aplicacion/busqueda.py`

Si alguna modificación de un archivo protegido fuese imprescindible, justifícala y solicita autorización previamente.

## 14. Informe de resultados y trazabilidad

Genera:

`05_Resultados/09_Resultado_Gestion_Administrativa_Productos_Ubicaciones.md`

Debe incluir:

- TASK_ID, fecha y hora reales.
- Solicitud original íntegra del usuario.
- Interpretación del agente.
- Acciones realizadas.
- Documentos y requisitos consultados.
- Archivos creados y modificados.
- Arquitectura de la capa de edición temporal.
- Reglas de validación aplicadas.
- Protección administrativa.
- Integración con sesiones y borradores.
- Evidencia de pruebas y regresión.
- Comportamiento de la interfaz.
- Limitaciones conocidas.
- Funciones expresamente diferidas al Prompt 10.
- Estado final de Git.
- Referencias verificables a los RF y CA aplicables.

No inventes resultados ni declares probadas funciones no verificadas.

## 15. Restricciones finales

**Prohibido:**

- Ejecutar `git commit`, `git push`, `git merge`, `git reset`, `git restore` o `git clean`.
- Crear o modificar el archivo maestro definitivo `03_Aplicacion/inventario.xlsx`.
- Escribir a GitHub mediante API.
- Incorporar APIs de Gemini.
- Añadir funciones de comercio, ventas, precios o cantidades.
- Cambiar la arquitectura aprobada sin autorización.
- Ejecutar el Prompt 10 o etapas posteriores.
- Modificar requisitos oficiales para acomodar una implementación.

## 16. Entrega y condición de cierre

Al terminar:

1. Presenta el resumen de implementación.
2. Identifica exactamente los archivos afectados.
3. Presenta resultados de pruebas.
4. Explica las limitaciones restantes.
5. Confirma que no hubo escritura remota.
6. Confirma que no creaste el inventario maestro definitivo.
7. Presenta `git status --short`.
8. Detente y espera la revisión independiente y aprobación del usuario.

**No realizar commit ni push hasta recibir autorización expresa.**