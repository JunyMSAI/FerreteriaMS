# Informe de Resultados — FERMS-V0-P09: Gestión administrativa de productos y ubicaciones

## 1. Identificación de la tarea

| Campo | Valor |
| :--- | :--- |
| **Identificador de la tarea (`TASK_ID`)** | `FERMS-V0-P09` |
| **Título de la tarea** | Gestión administrativa de productos y ubicaciones |
| **Proyecto / Etapa** | FerreteríaMS v0 |
| **Fecha y hora de ejecución** | `2026-10-20 22:15:46 -04:00` |
| **Agente ejecutor** | Antigravity (Gemini) |
| **Rama activa verificada** | `main` |
| **Commit base de código funcional** | `6cdda82` (`FERMS-V0-P08: sesiones bloqueos y borradores administrativos`) |
| **Commit inmediato en `HEAD` al iniciar** | `204616d` (`Prompt "09_Gestion_Administrativa_Productos_Ubicaciones"` — añade únicamente `02_Prompts/09_Gestion_Administrativa_Productos_Ubicaciones.md` creado y autorizado por el usuario) |

---

## 2. Solicitud original íntegra del usuario

### 2.1. Instrucción de ejecución recibida en la conversación

```text
Ejecuta la tarea FERMS-V0-P09 — Gestión administrativa de productos y ubicaciones del proyecto FerreteríaMS v0.

Lee íntegramente:

02_Prompts/09_Gestion_Administrativa_Productos_Ubicaciones.md

Cumple exclusivamente las instrucciones aprobadas en ese documento.

Antes de comenzar, consulta GEMINI.md, AGENTS.md, el documento conceptual, las especificaciones oficiales, el Prompt 08 y su informe de resultados.

Verificación inicial de Git:

- Confirma que la rama activa sea main.
- Confirma que el commit base sea 6cdda82.
- El único archivo nuevo esperado antes de implementar es 02_Prompts/09_Gestion_Administrativa_Productos_Ubicaciones.md, creado y autorizado por el usuario.
- Si aparecen otros cambios inesperados, detente y solicita autorización.

Autorización de trabajo:

Autorizo únicamente las modificaciones locales permitidas en el Prompt 09.

Implementa la gestión administrativa de productos y ubicaciones, reutilizando el esquema oficial de inventario, los controles de autenticación y la gestión de borradores existentes.

Durante esta etapa, las modificaciones del inventario deben permanecer exclusivamente como cambios temporales validados, sin persistencia remota.

Restricciones obligatorias:

- No crees ni modifiques 03_Aplicacion/inventario.xlsx.
- No escribas a GitHub mediante API.
- No modifiques los documentos oficiales aprobados.
- No alteres los módulos protegidos sin solicitar autorización.
- No implementes Gemini operativo.
- No incorpores precios, cantidades ni ventas.
- No ejecutes operaciones Git de publicación.
- No avances al Prompt 10.

Ejecuta las pruebas del Prompt 09 y después las regresiones anteriores de manera individual y secuencial, evitando pruebas intensivas o procesos simultáneos que puedan sobrecargar la computadora.

Documenta la implementación y los resultados en:

05_Resultados/09_Resultado_Gestion_Administrativa_Productos_Ubicaciones.md

Al finalizar, proporciona un informe con los archivos modificados, las pruebas realizadas, los resultados obtenidos, las limitaciones y el estado de Git.

No ejecutes git commit, git push, git merge, despliegues ni operaciones destructivas.

Detente al terminar y espera mi revisión y autorización.
```

### 2.2. Contenido íntegro del prompt `02_Prompts/09_Gestion_Administrativa_Productos_Ubicaciones.md`

```markdown
# FERMS-V0-P09 — Gestión administrativa de productos y ubicaciones

**Proyecto:** FerreteríaMS v0  
**Nivel:** Estándar con auditoría reforzada de integridad y seguridad  
**Agente ejecutor:** Antigravity (Gemini) dentro de VS Code  
**Commit base esperado:** `6cdda82`  
**Rama esperada:** `main`

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
```

---

## 3. Interpretación del agente

El objetivo de la tarea **FERMS-V0-P09** es dotar a la sección protegida **Productos** de FerreteríaMS v0 de un motor administrativo de consulta, alta y edición de productos y asignaciones de ubicaciones físicas que opere **exclusivamente sobre copias de trabajo validadas en memoria**, sin persistencia remota en GitHub ni creación del archivo local definitivo `03_Aplicacion/inventario.xlsx`.

Puntos esenciales de diseño e integridad derivados de la solicitud y las especificaciones:

1. **Separación y atomicidad del motor de edición local (`03_Aplicacion/administracion_productos.py`):**
   - Toda sesión administrativa trabaja sobre su propia instancia aislada de `EspacioTrabajoAdminInventario`, que conserva una copia profunda e inmutable del inventario base (`inventario_original`), la copia mutable validada (`inventario_trabajo`) y el `sha_base_remoto` leído de GitHub como referencia para el futuro Prompt 10 (`confirmado_en_github=False`).
   - Antes de aceptar cualquier creación (`crear_producto_local`), edición (`editar_producto_local`), cambio de ubicación principal (`cambiar_ubicacion_principal_local`) o retiro de ubicación secundaria (`eliminar_asignacion_ubicacion_local`), las cuatro hojas (`Productos`, `Categorías`, `Ubicaciones`, `Asignaciones`) se clonan y se someten a `construir_inventario_datos()` de `inventario.py`. Si cualquier regla de esquema, formato o integridad referencial falla, la operación se rechaza por completo y `inventario_trabajo` permanece idéntico a su estado previo.
2. **Inmutabilidad del código de producto y catálogos predefinidos:**
   - Una vez registrado un producto, su `Codigo_Producto` es estrictamente inmutable (`RF-015`, `CA-044`): cualquier intento de enviar un `nuevo_codigo_producto` distinto al código original es rechazado con `CodigoErrorAdministrativo.CODIGO_PRODUCTO_INMUTABLE`.
   - En FerreteríaMS v0, los catálogos de `Categorías` y `Ubicaciones` están predefinidos en el archivo Excel (`RF-021`), por lo que se reutilizan para poblar los selectores de producto y se bloquea cualquier intento de crear, editar o eliminar categorías o ubicaciones mediante `rechazar_modificacion_catalogo_predefinido()`.
3. **Integración con seguridad administrativa, sesiones y borradores (Prompts 07 y 08):**
   - Cada operación administrativa exige autorización vigente en Python (`_exigir_sesion_admin_autorizada`), comprobando ausencia de bloqueo activo, contexto de escritorio (`ContextoDispositivo.ESCRITORIO`), validez de la sesión en `_SESIONES_ACTIVAS_SERVIDOR` y correspondencia exacta entre la sesión propietaria del `EspacioTrabajoAdminInventario` y la sesión actual.
   - Las lecturas pasivas para renderizar tablas o selectores (`registrar_actividad=False`) no renuevan automáticamente la sesión por inactividad; solo las acciones administrativas explícitas (`registrar_actividad=True`) actualizan la marca temporal.
   - Las operaciones locales validadas y los formularios en edición se sincronizan automáticamente con el subsistema de borradores de `autenticacion.py` (`guardar_borrador_admin`), permitiendo retener los cambios durante 15 minutos adicionales si la sesión expira por inactividad y reaplicarlos íntegramente tras la reautenticación (`restaurar_borrador_en_espacio_trabajo_admin`).

---

## 4. Documentos y requisitos consultados

### 4.1. Documentos oficiales leídos antes de implementar

1. `GEMINI.md`
2. `AGENTS.md`
3. `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`
4. `01_Documentacion/02_Especificaciones_v0.md`
5. `02_Prompts/08_Sesiones_Bloqueos_Borradores.md`
6. `05_Resultados/08_Resultado_Sesiones_Bloqueos_Borradores.md`
7. `02_Prompts/09_Gestion_Administrativa_Productos_Ubicaciones.md`

### 4.2. Requisitos funcionales (`RF`) relacionados

| Código RF | Descripción en `02_Especificaciones_v0.md` | Estado en Prompt 09 |
| :--- | :--- | :--- |
| `RF-011` | Protección del acceso administrativo mediante autenticación obligatoria. | Cumplido y preservado |
| `RF-012` | Uso de cuenta administrativa inicial configurada fuera del código fuente. | Cumplido y preservado |
| `RF-013` | Restricción de las funciones administrativas a la interfaz web para computadora. | Cumplido (verificación en UI y en cada función del motor local) |
| `RF-014` | Registro de productos nuevos con código único, nombre, categoría, descripción y al menos una ubicación física. | Cumplido en memoria de trabajo local |
| `RF-015` | Edición de productos existentes manteniendo inmutable el código único (`Codigo_Producto`). | Cumplido en memoria de trabajo local |
| `RF-016` | Asignación de ubicación principal a cada producto. | Cumplido en memoria de trabajo local |
| `RF-017` | Asignación de una o más ubicaciones secundarias adicionales a un producto. | Cumplido en memoria de trabajo local |
| `RF-018` | Cambio de ubicación principal y retiro de ubicaciones secundarias respetando integridad. | Cumplido en memoria de trabajo local |
| `RF-019` | Garantía de que todo producto mantenga al menos una ubicación válida y exactamente una principal. | Cumplido |
| `RF-020` | Validación de integridad antes de aceptar cualquier cambio administrativo. | Cumplido (validación atómica de las 4 hojas) |
| `RF-021` | Uso de categorías y ubicaciones predefinidas en el archivo Excel durante v0. | Cumplido (`rechazar_modificacion_catalogo_predefinido`) |
| `RF-022` | Estructura obligatoria de las cuatro hojas (`Productos`, `Categorías`, `Ubicaciones`, `Asignaciones`). | Cumplido |
| `RF-023` | Reglas de integridad referencial y unicidad entre hojas. | Cumplido |
| `RF-024` | Conservación de códigos e identificadores como texto incluyendo ceros iniciales. | Cumplido |
| `RF-027` | Preparación de referencia `sha_base_remoto` para detección futura de conflictos (persistencia diferida al Prompt 10). | Preparado en `EspacioTrabajoAdminInventario` y `PaquetePublicacionPendienteP10` |

### 4.3. Criterios de aceptación (`CA`) relacionados

| Código CA | Descripción resumida | Verificación en Prompt 09 |
| :--- | :--- | :--- |
| `CA-009`..`CA-011` | Control de acceso administrativo y validación de credenciales. | `test_28`, `test_39`, `test_40` y regresión `test_07` |
| `CA-012` (local) | Creación válida de producto con datos obligatorios y ubicación principal. | `test_02`, `test_03`, `test_40` |
| `CA-013` (local) | Edición válida de producto existente conservando integridad. | `test_14`, `test_15`, `test_16`, `test_40` |
| `CA-014` | Rechazo de código de producto duplicado. | `test_06` |
| `CA-015` | Asignación válida de ubicación principal. | `test_02`, `test_18` |
| `CA-016` | Asignación válida de ubicaciones secundarias. | `test_03`, `test_19` |
| `CA-017` | Cambio de ubicación principal manteniendo exactamente una principal. | `test_18` |
| `CA-018` | Preservación de los demás productos y relaciones al editar un registro. | `test_25`, `test_26` |
| `CA-019` / `CA-058` | Restricción de operaciones administrativas desde dispositivos móviles. | `test_31` y regresión `test_07`/`test_08` |
| `CA-022` | Conservación de las cuatro hojas y columnas exactas del esquema Excel. | `test_25` |
| `CA-027`..`CA-030` | Protección de rutas administrativas, ocultamiento de secretos y sesiones. | `test_28`..`test_39` |
| `CA-044` | Rechazo de cualquier intento de modificar `Codigo_Producto` en un producto existente. | `test_17` |
| `CA-045` | Retiro válido de ubicación secundaria y rechazo cuando es la única o la principal. | `test_20`, `test_21`, `test_22` |
| `CA-046` | Rechazo de producto sin ubicación o con cero / múltiples ubicaciones principales. | `test_10`, `test_11`, `test_12` |
| `CA-047` | Rechazo de categoría inexistente. | `test_08` |
| `CA-048` | Rechazo de ubicación inexistente. | `test_09` |
| `CA-049` / `CA-050` | Rechazo de coordenadas físicas duplicadas y asignaciones duplicadas `(Codigo_Producto, Ubicacion_ID)`. | `test_13`, `test_23` y regresión `test_02` |
| `CA-051` (local) | Rechazo atómico de operaciones inválidas sin alterar el estado previo. | `test_23`, `test_24`, `test_41`..`test_51` |
| `CA-055` / `CA-057` | Revocación tras expiración de sesión, retención de borrador por 15 min y restauración tras reautenticación. | `test_29`, `test_32`, `test_33`, `test_34`, `test_35`, `test_41`..`test_51` |

---

## 5. Acciones realizadas y archivos afectados

### 5.1. Archivos creados

1. `03_Aplicacion/administracion_productos.py`
   - Implementa el motor de edición administrativa local (`EspacioTrabajoAdminInventario`, `ResultadoCargaInventarioAdmin`, `ResultadoOperacionProductoAdmin`, `PaquetePublicacionPendienteP10`, `EstadoInventarioAdmin`, `CodigoErrorAdministrativo`, `ModoVistaAdmin`, `ErrorSincronizacionBorradorAdmin`).
   - Implementa las operaciones verificadas en servidor: `inicializar_espacio_trabajo_desde_inventario`, `cargar_inventario_administrativo_en_sesion`, `consultar_productos_administrativos`, `consultar_producto_administrativo_por_codigo`, `obtener_catalogo_categorias_admin`, `obtener_catalogo_ubicaciones_admin`, `rechazar_modificacion_catalogo_predefinido`, `crear_producto_local`, `editar_producto_local`, `cambiar_ubicacion_principal_local`, `eliminar_asignacion_ubicacion_local`, `descartar_cambios_locales_en_sesion`, `guardar_borrador_formulario_admin`, `restaurar_borrador_en_espacio_trabajo_admin` y `preparar_paquete_publicacion_futura_p10`.
2. `04_Pruebas/test_09_gestion_administrativa_productos_ubicaciones.py`
   - Implementa las 40 pruebas unitarias y de integración obligatorias de la Sección 12 del Prompt 09, más 7 pruebas de auditoría de atomicidad (`test_41` a `test_47`) y 4 pruebas de corrección final de integración UI, restauración segura de borradores y configuración predeterminada de GitHub (`test_48` a `test_51`, total: 51 pruebas).
3. `05_Resultados/09_Resultado_Gestion_Administrativa_Productos_Ubicaciones.md`
   - Documenta la trazabilidad completa, arquitectura, correcciones de auditoría de atomicidad, integración UI y configuración de GitHub, reglas de validación, resultados de pruebas y estado de Git.

### 5.2. Archivos modificados

1. `03_Aplicacion/app.py`
   - Integra el módulo `administracion_productos.py` dentro de la sección protegida `Productos`.
   - Añade las funciones de orquestación en sesión (`seleccionar_modo_vista_admin_en_sesion`, `ejecutar_carga_inventario_admin_en_sesion`, `ejecutar_creacion_producto_en_sesion`, `ejecutar_edicion_producto_en_sesion`, `ejecutar_cambio_ubicacion_principal_en_sesion`, `ejecutar_eliminacion_ubicacion_secundaria_en_sesion`, `ejecutar_descarte_cambios_locales_en_sesion`) y las subvistas administrativas de **Consulta**, **Crear producto** y **Editar producto y ubicaciones**, conservando intacta la vista inicial posterior al login requerida por las pruebas de regresión del Prompt 07.
   - Conecta `ejecutar_restauracion_borrador_en_sesion()` y el botón `btn_admin_restaurar_borrador` con el descargador del inventario remoto (`descargador_remoto`), garantiza el uso de `ConfiguracionRepositorioGitHub` y `CONFIGURACION_POR_DEFECTO` (evitando pasar `config=None` al lector real) y actualiza `CLAVE_MODO_VISTA_ADMIN` al restaurar un espacio de trabajo para presentar inmediatamente el espacio recuperado tras la expiración y reautenticación.

### 5.3. Archivos protegidos verificados sin modificaciones

No se modificó ninguno de los archivos protegidos:
- `AGENTS.md`, `GEMINI.md`
- `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`, `01_Documentacion/02_Especificaciones_v0.md`
- `02_Prompts/*`, `04_Pruebas/test_02..08`, `05_Resultados/02..08`
- `requirements.txt`
- `03_Aplicacion/inventario.py`, `03_Aplicacion/github_inventario.py`, `03_Aplicacion/busqueda.py`, `03_Aplicacion/autenticacion.py`, `03_Aplicacion/estilos.css`
- `03_Aplicacion/inventario.xlsx` (confirmado inexistente en disco).

---

## 6. Arquitectura de la capa de edición temporal, validación, seguridad y atomicidad

1. **Aislamiento en copia de trabajo (`EspacioTrabajoAdminInventario`):**
   - Al cargar el inventario remoto (o preparar una copia demostrativa en memoria cuando GitHub confirma que `inventario.xlsx` aún no existe), se crean dos copias profundas independientes mediante `clonar_inventario_datos()`: `inventario_original` (inmutable) e `inventario_trabajo` (mutable únicamente a través de transacciones validadas).
   - El `sha_base_remoto` leído de GitHub se almacena como metadato de referencia para el futuro control de concurrencia del Prompt 10, con `confirmado_en_github=False` en todas las estructuras de respuesta.
2. **Validación atómica de las cuatro hojas y sincronización transaccional de borradores (Corrección de Auditoría — Hallazgo 2):**
   - Toda operación de creación o edición (`crear_producto_local`, `editar_producto_local` y las operaciones derivadas `cambiar_ubicacion_principal_local` y `eliminar_asignacion_ubicacion_local`) valida primero la sesión de manera pasiva (`registrar_actividad=False`), construye DataFrames candidatos de `Productos`, `Categorías`, `Ubicaciones` y `Asignaciones` y ejecuta `construir_inventario_datos(hojas_candidatas)` de `inventario.py`.
   - Antes de mutar `espacio.inventario_trabajo`, `espacio.codigos_productos_creados`, `espacio.codigos_productos_editados` o `espacio.historial_operaciones_locales`, se construye un `espacio_candidato` aislado y se ejecuta `_sincronizar_borrador_automatico_en_sesion(estado, espacio_candidato, ...)`.
   - Solo si la validación y la sincronización del borrador tienen éxito se registra la actividad explícita de la sesión (`registrar_actividad=True`) y se publica el cambio en memoria; si `guardar_borrador_admin()` rechaza la sincronización (por ejemplo, por superar `MAX_TAMANO_BORRADOR_BYTES`, estructura inválida, expiración de sesión o cualquier excepción), se lanza `ErrorSincronizacionBorradorAdmin` sin haber modificado el inventario de trabajo, ni los códigos registrados, ni el historial de operaciones, ni el borrador previo en el servidor, ni haber renovado indebidamente `ultima_actividad_epoch`.
3. **Restauración atómica de borradores en espacio de preparación aislado (Corrección de Auditoría — Hallazgo 1):**
   - `restaurar_borrador_en_espacio_trabajo_admin()` valida primero la sesión de forma pasiva (`registrar_actividad=False`) y lee el borrador de forma no destructiva mediante `obtener_borrador_admin()` (sin consumir ni eliminar el borrador fuente ni reemplazar aún el estado de la sesión).
   - Verifica la titularidad del espacio activo y valida la coherencia de versión (`sha_base_remoto` explícito frente al SHA registrado en el borrador y al SHA del espacio activo), impidiendo mezclar inventarios de distintas versiones sin validación.
   - Si el borrador contiene `operaciones_locales`, construye un contenedor aislado `espacio_preparacion` en memoria local (sin tocar `estado[CLAVE_ESPACIO_TRABAJO_ADMIN]`) y reproduce todas las operaciones con `_sincronizar_borrador=False`, `_publicar_en_estado=False` y `_registrar_actividad=False` (sin efectos secundarios sobre el estado real, sobre el reloj de actividad de la sesión ni sobre el borrador fuente del servidor).
   - Solo cuando **todas** las operaciones y estructuras han sido validadas satisfactoriamente se invoca `restaurar_borrador_admin(..., eliminar_tras_restaurar=eliminar_tras_restaurar)` y se publica de forma atómica el espacio de trabajo validado y el formulario en `estado`. Si falla cualquier operación, tanto el espacio de trabajo anterior como el borrador fuente recuperable se conservan íntegramente.
4. **Integración completa UI ↔ Motor y configuración oficial GitHub en la restauración tras expiración de sesión:**
   - **Defecto detectado:** Cuando una sesión administrativa expiraba por inactividad, `app.py` limpiaba `st.session_state[CLAVE_ESPACIO_TRABAJO_ADMIN] = None`. Al reautenticarse y pulsar el botón «Restaurar borrador temporal» (`btn_admin_restaurar_borrador`), `ejecutar_restauracion_borrador_en_sesion()` invocaba `restaurar_borrador_en_espacio_trabajo_admin()` sin un inventario base ni espacio activo en sesión, provocando que la reconstrucción de `operaciones_locales` fallara por falta de inventario base y que la vista permaneciera en `ModoVistaAdmin.INICIAL`. Adicionalmente, el parámetro `config_github` en `ejecutar_restauracion_borrador_en_sesion()` tenía valor predeterminado `None`, lo cual podía transmitir `config=None` al lector real de GitHub.
   - **Corrección implementada:**
     1. En `restaurar_borrador_en_espacio_trabajo_admin()`, cuando el borrador contiene `operaciones_locales` y la sesión no dispone de espacio activo (por haber sido limpiado al expirar) ni se suministró `inventario_base` explícito:
        - Si el borrador proviene de un inventario remoto (`origen_remoto_confirmado=True` o `sha_borrador` presente), consulta de forma segura el inventario remoto en GitHub (`descargador_remoto` o `github_inventario.descargar_inventario_remoto`), **nunca sustituye silenciosamente un inventario remoto por uno demostrativo**, distingue `ErrorArchivoRemotoInexistente` (`EstadoInventarioAdmin.INVENTARIO_REMOTO_INEXISTENTE`), `ErrorDatosInventarioRemoto` (`EstadoInventarioAdmin.DATOS_REMOTOS_INVALIDOS`) y `ErrorGitHubInventario` (`EstadoInventarioAdmin.ERROR_CONEXION`), y verifica que el `sha_github` descargado coincida exactamente con el `sha_base_remoto` del borrador (`CodigoErrorAdministrativo.BORRADOR_INVALIDO_O_VENCIDO` en caso de conflicto de SHA).
        - Si ocurre cualquier error de red, inexistencia o conflicto de SHA, se preserva intacto el borrador fuente en el servidor y cualquier espacio de trabajo previo, sin renovar la marca de actividad de la sesión.
     2. En `03_Aplicacion/app.py`, `ejecutar_restauracion_borrador_en_sesion()` utiliza el tipo oficial `ConfiguracionRepositorioGitHub` y la instancia `CONFIGURACION_POR_DEFECTO` (`config_efectiva = config_github if config_github is not None else CONFIGURACION_POR_DEFECTO`), garantizando que nunca se pase `config=None` al descargador real cuando no se especifique configuración y conservando la inyección de configuraciones y descargadores simulados para pruebas. Asimismo, actualiza `CLAVE_MODO_VISTA_ADMIN` (al modo del `formulario_activo` si existía o a `ModoVistaAdmin.CONSULTA.value`) para presentar de inmediato en pantalla el banner de cambios locales pendientes y los productos recuperados.

---

## 7. Evidencia de pruebas ejecutadas (secuenciales e individuales)

Siguiendo las instrucciones de ejecución segura en Windows, primero se verificó la sintaxis estática con `py_compile`, luego se ejecutó la prueba nueva (`test_51`), la suite completa del Prompt 09 (51 pruebas: 40 originales + 11 de auditoría e integración UI/GitHub) y a continuación cada suite de regresión de los Prompts 02 a 08 de manera **individual y secuencial**:

| Orden | Comando ejecutado | Pruebas | Tiempo | Resultado |
| :---: | :--- | :---: | :---: | :---: |
| 0 | `python -m py_compile 03_Aplicacion/app.py 04_Pruebas/test_09_gestion_administrativa_productos_ubicaciones.py` | — | `0.15s` | **OK (exit 0)** |
| 1 | `python -m unittest 04_Pruebas/test_09_gestion_administrativa_productos_ubicaciones.py -v` | 51 | `2.619s` | **OK (51/51)** |
| 2 | `python -m unittest 04_Pruebas/test_02_motor_inventario.py -v` | 23 | `0.210s` | **OK (23/23)** |
| 3 | `python -m unittest 04_Pruebas/test_03_lectura_github.py -v` | 21 | `0.298s` | **OK (21/21)** |
| 4 | `python -m unittest 04_Pruebas/test_04_busqueda_publica.py -v` | 25 | `1.180s` | **OK (25/25)** |
| 5 | `python -m unittest 04_Pruebas/test_05_detalles_ubicaciones.py -v` | 23 | `2.953s` | **OK (23/23)** |
| 6 | `python -m unittest 04_Pruebas/test_06_interfaz_responsive_gemini.py -v` | 18 | `3.810s` | **OK (18/18)** |
| 7 | `python -m unittest 04_Pruebas/test_07_autenticacion_administrativa.py -v` | 22 | `1.766s` | **OK (22/22)** |
| 8 | `python -m unittest 04_Pruebas/test_08_sesiones_bloqueos_borradores.py -v` | 40 | `1.205s` | **OK (40/40)** |
| **Total** | **8 suites ejecutadas individual y secuencialmente** | **223** | **`14.041s`** | **OK (223/223)** |

### Detalle de las 11 pruebas adicionales de auditoría, integración UI y configuración GitHub (`test_41` a `test_51`)

1. `test_41_restauracion_operacion_valida_seguida_de_invalida_es_atomica`: Comprueba que al restaurar un borrador cuya primera operación es válida y la segunda es inválida, ninguna operación queda aplicada en el espacio de trabajo.
2. `test_42_conservacion_exacta_espacio_trabajo_anterior_cuando_falla_restauracion`: Comprueba que cuando falla la restauración de un borrador, el espacio de trabajo anterior en sesión (con sus creaciones, ediciones, historial e instancia) y el formulario previo permanecen idénticos.
3. `test_43_conservacion_borrador_fuente_cuando_falla_restauracion`: Comprueba que un fallo al restaurar (incluso con `eliminar_tras_restaurar=True`) no consume, no elimina ni sobrescribe el borrador fuente en el servidor.
4. `test_44_restauracion_correcta_multiples_operaciones_validas`: Comprueba la restauración completa y ordenada de múltiples creaciones y ediciones válidas tras expiración y reautenticación.
5. `test_45_rechazo_exceso_tamano_borrador_tras_crear_o_editar_revierte_cambios`: Comprueba que cuando `guardar_borrador_admin()` rechaza la sincronización por superar `MAX_TAMANO_BORRADOR_BYTES` tras crear o editar, el inventario de trabajo conserva su versión anterior, no quedan códigos ni operaciones falsamente registrados, no se emite mensaje de éxito y no se altera el borrador previo.
6. `test_46_excepcion_en_sincronizacion_nunca_deja_registros_parcialmente_aplicados`: Verifica en `crear_producto_local`, `editar_producto_local`, `cambiar_ubicacion_principal_local` y `eliminar_asignacion_ubicacion_local` que una excepción durante la sincronización del borrador jamás deja registros parcialmente aplicados.
7. `test_47_conservacion_aislamiento_entre_sesiones_y_sha_base_en_restauracion`: Verifica que la restauración rechaza mezclar borradores con un `sha_base_remoto` discrepante o pertenecientes a otra sesión, conservando intactos el SHA base y el borrador fuente.
8. `test_48_integracion_apptest_flujo_completo_expiracion_reautenticacion_y_boton_restaurar`: Ejecuta en `AppTest` el flujo real de interfaz: inicio de sesión → creación de producto `"0098"` → edición de `"MAR001"` → avance del reloj más allá de los 15 minutos → expiración y limpieza del espacio activo → reautenticación dentro de la ventana de 15 minutos adicionales → pulsación del botón real `btn_admin_restaurar_borrador` → reconstrucción del espacio de trabajo con su SHA original y presentación en pantalla de los productos recuperados.
9. `test_49_restauracion_sin_espacio_activo_distingue_errores_github_inexistente_y_conflicto_sha`: Verifica que cuando la sesión expiró y limpió el espacio activo, la consulta a GitHub para recuperar el inventario base distingue error de conexión (`ERROR_CONEXION`), inventario inexistente (`INVENTARIO_REMOTO_INEXISTENTE`, sin sustituir silenciosamente por el inventario demostrativo) y conflicto de SHA (`BORRADOR_INVALIDO_O_VENCIDO`), conservando el borrador fuente y reconstruyendo el espacio cuando el SHA coincide.
10. `test_50_operaciones_preparacion_y_fallos_no_renuevan_indebidamente_la_sesion`: Comprueba que las creaciones fallidas, ediciones fallidas y restauraciones fallidas en fase de preparación no avanzan `ultima_actividad_epoch` y que el servidor respeta la expiración autoritativa a los 15 minutos.
11. `test_51_configuracion_github_predeterminada_e_inyectada_en_ruta_restauracion`: Comprueba que `ejecutar_restauracion_borrador_en_sesion()` utiliza `ConfiguracionRepositorioGitHub` y `CONFIGURACION_POR_DEFECTO` por omisión (e incluso cuando se pasa `config_github=None`), garantizando que nunca se transmita `config=None` al lector real de GitHub, y conservando la inyección de configuraciones y descargadores simulados.

---

## 8. Limitaciones conocidas y funciones expresamente diferidas al Prompt 10

Conforme al alcance estricto del Prompt 09:

1. **Sin persistencia remota en GitHub durante esta etapa:** Las creaciones y ediciones de productos y ubicaciones se mantienen exclusivamente como cambios locales validados en memoria (`confirmado_en_github=False`).
2. **Funciones diferidas al Prompt 10:**
   - Escritura remota mediante GitHub Contents API (`PUT`).
   - Inicialización remota definitiva de `03_Aplicacion/inventario.xlsx` cuando no exista en el repositorio.
   - Detección y manejo de conflictos de concurrencia por discrepancia de SHA remoto al guardar.
   - Invalidación/refresco automático del inventario público tras confirmar un guardado remoto.
3. **Catálogos predefinidos en v0 (`RF-021`):** La creación, edición o eliminación directa de registros en las hojas `Categorías` y `Ubicaciones` no forma parte de FerreteríaMS v0 y es rechazada explícitamente.

---

## 9. Verificación de restricciones y estado final de Git

- **Confirmación de ausencia de escritura remota:** Verificado estática y dinámicamente (`test_37`) que ningún módulo de la aplicación contiene ni ejecuta métodos HTTP `PUT`, `POST`, `DELETE` o `PATCH`.
- **Confirmación de no creación de `03_Aplicacion/inventario.xlsx`:** Verificado (`test_38`) que `03_Aplicacion/inventario.xlsx` no existe en el árbol de trabajo local.
- **Estado de Git (`git status --short`):**

```text
 M 03_Aplicacion/app.py
?? 03_Aplicacion/administracion_productos.py
?? 04_Pruebas/test_09_gestion_administrativa_productos_ubicaciones.py
?? 05_Resultados/09_Resultado_Gestion_Administrativa_Productos_Ubicaciones.md
```

