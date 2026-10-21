# FERMS-V0-P10 — Persistencia segura del inventario mediante GitHub API

**Proyecto:** FerreteríaMS v0  
**Nivel:** Auditoría reforzada — persistencia, seguridad y concurrencia  
**Último commit funcional aprobado:** `97f91ce` — FERMS-V0-P09  

---

## 1. Objetivo

Implementar la persistencia del archivo maestro de inventario de FerreteríaMS v0 mediante la API oficial de GitHub, conectando el motor de edición administrativa temporal del Prompt 09 con el almacenamiento definitivo aprobado para el MVP.

La implementación debe permitir:

1. Preparar el contenido de un archivo Excel válido a partir del inventario administrativo.
2. Crear el archivo maestro en GitHub cuando su ausencia haya sido confirmada.
3. Actualizar un archivo maestro existente utilizando su SHA como mecanismo de control de concurrencia.
4. Proteger contra pérdida de datos, sobrescrituras accidentales, duplicados y publicaciones parciales.
5. Actualizar el estado administrativo solamente cuando GitHub haya confirmado satisfactoriamente la escritura.
6. Permitir que la búsqueda pública consulte posteriormente el inventario persistido.
7. Mantener la trazabilidad mediante el historial de commits de GitHub.

**Límite de autorización:** implementar y probar la capacidad de escritura no significa estar autorizado a modificar el inventario real del repositorio durante esta tarea.

Las pruebas deberán utilizar simulaciones o mocks. Cualquier escritura real exigirá una autorización posterior, explícita e independiente del usuario.

## 2. Documentos y código obligatorio

Leer y respetar:

- `GEMINI.md`
- `AGENTS.md`
- `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`
- `01_Documentacion/02_Especificaciones_v0.md`
- `02_Prompts/09_Gestion_Administrativa_Productos_Ubicaciones.md`
- `05_Resultados/09_Resultado_Gestion_Administrativa_Productos_Ubicaciones.md`

Inspeccionar además los módulos y pruebas de los Prompts 02 a 09, especialmente:

- `03_Aplicacion/inventario.py`
- `03_Aplicacion/github_inventario.py`
- `03_Aplicacion/administracion_productos.py`
- `03_Aplicacion/autenticacion.py`
- `03_Aplicacion/app.py`

Las decisiones conceptuales y especificaciones aprobadas son las fuentes de autoridad.

No modificar requisitos para acomodar la implementación.

## 3. Verificación inicial

Antes de comenzar:

1. Confirmar que el repositorio local pertenece a FerreteríaMS.
2. Confirmar la rama `main`.
3. Confirmar que el commit `97f91ce` está presente como último punto funcional aprobado del Prompt 09.
4. Reconocer que el usuario puede haber creado posteriormente un commit documental con el propio Prompt 10; por tanto, no exigir que `HEAD` sea literalmente `97f91ce`.
5. Confirmar que no existen modificaciones inesperadas en el área de trabajo.
6. Inspeccionar cómo se representa y valida actualmente el inventario.
7. Inspeccionar cómo se obtiene el SHA mediante GitHub API.
8. Identificar los requisitos funcionales y criterios de aceptación aplicables.
9. Identificar los archivos y componentes que serán estrictamente necesarios.

Si existe una contradicción relevante con el alcance aprobado, detenerse y solicitar autorización.

No modificar el repositorio mediante operaciones destructivas de Git.

## 4. Arquitectura oficial de almacenamiento

Mantener la arquitectura del MVP:

- **GitHub:** archivo maestro y control de versiones.
- **Excel (`.xlsx`):** estructura persistente del inventario.
- **Pandas:** procesamiento, transformación y validación de datos.
- **Streamlit:** interfaz pública y administrativa.
- **GitHub Contents API:** lectura y escritura autorizada de la versión del archivo maestro.

No introducir una base de datos SQL, Supabase, servicios adicionales ni almacenamiento alternativo.

El archivo oficial es:

`03_Aplicacion/inventario.xlsx`

**Importante:** esta ruta identifica el archivo dentro del repositorio de GitHub. No obliga a crear una copia persistente del archivo en el disco local.

Preferir generación y serialización del Excel en memoria mediante `BytesIO`, conservando el esquema y las dependencias ya aprobadas.

## 5. Esquema obligatorio del Excel

El archivo maestro debe conservar exactamente estas cuatro hojas, con sus encabezados y orden:

**Productos**

`Codigo_Producto, Nombre, Categoria_ID, Descripcion`

**Categorías**

`Categoria_ID, Nombre_Categoria`

**Ubicaciones**

`Ubicacion_ID, Rack, Columna, Nivel, Posicion`

**Asignaciones**

`Codigo_Producto, Ubicacion_ID, Principal`

Reglas esenciales:

- Identificadores tratados como texto, conservando ceros iniciales.
- Código de producto único e inmutable después de su creación.
- Categorías y ubicaciones referenciadas deben existir.
- Cada producto debe conservar al menos una ubicación y exactamente una principal.
- No duplicar asignaciones de producto y ubicación.
- No duplicar las coordenadas físicas según las reglas oficiales.
- No crear columnas o pestañas adicionales.
- Conservar la representación oficial de la marca `Principal`.
- No incluir cantidades, precios, ventas ni funcionalidades comerciales.

Antes de cualquier escritura, ejecutar una validación integral del inventario utilizando el motor existente de `inventario.py`.

## 6. Serialización del archivo Excel

Implementar una función comprobable para convertir el inventario validado en bytes de un archivo `.xlsx`.

Debe:

1. Recibir una estructura `InventarioDatos` válida.
2. Clonar o proteger los datos de entrada.
3. Crear el Excel en memoria.
4. Conservar exactamente las cuatro hojas.
5. Conservar el orden de las columnas.
6. Preservar códigos e identificadores como cadenas de texto.
7. Evitar conversiones silenciosas de identificadores a números o fechas.
8. Volver a leer los bytes producidos con el mecanismo oficial existente.
9. Comprobar que el archivo serializado conserva la información y cumple las validaciones.
10. Rechazar cualquier error antes de intentar publicar.

No crear un archivo temporal persistente sin justificación y autorización.

La serialización no debe mutar el inventario original ni el espacio de trabajo del administrador.

## 7. Credenciales y permisos para GitHub API

Usar exclusivamente el mecanismo seguro de configuración admitido por el proyecto.

Requisitos:

- No almacenar tokens o contraseñas en el código fuente.
- No registrar secretos en logs, excepciones, informes o respuestas de interfaz.
- Utilizar credenciales de mínimo privilegio.
- Limitar la escritura al repositorio, rama y ruta oficiales.
- No permitir que campos de la interfaz pública modifiquen propietario, repositorio, rama o ruta.
- No permitir que una solicitud administrativa manipule archivos arbitrarios del repositorio.
- No realizar escritura si las credenciales son inexistentes, inválidas o insuficientes.
- No introducir un token real en las pruebas automatizadas.

Inspeccionar primero las decisiones oficiales relativas a secretos y permisos. Si hace falta configurar una credencial nueva, documentar su necesidad, nombre y permisos mínimos, pero no solicitar que el usuario la comparta en el chat ni incorporarla al repositorio.

## 8. Escritura mediante GitHub Contents API

Implementar una capa de persistencia separada y comprobable.

La API de GitHub deberá utilizarse de acuerdo con su contrato oficial para crear o actualizar un archivo mediante Contents API.

Operación prevista: actualización del contenido del archivo del repositorio en la rama autorizada, con contenido Base64 y mensaje de commit apropiado.

Requisitos:

1. Validar el inventario completo antes de construir la solicitud.
2. Comprobar la sesión administrativa vigente.
3. Comprobar la autorización de escritura.
4. Obtener o verificar el estado remoto inmediatamente antes de publicar.
5. Distinguir claramente creación de archivo y actualización.
6. Utilizar el SHA correcto cuando se modifica un archivo existente.
7. No reenviar escrituras a ciegas después de errores de red.
8. Verificar la respuesta de GitHub antes de declarar éxito.
9. No marcar como persistidos cambios que GitHub no haya confirmado.
10. Conservar la capacidad de recuperar el inventario original y el historial de GitHub.
11. Impedir que se publique una estructura distinta del archivo Excel aprobado.

La existencia previa del archivo debe verificarse contra el estado remoto de GitHub, no solamente contra el disco local.

## 9. Creación inicial del inventario remoto

Si GitHub confirma de forma inequívoca que `03_Aplicacion/inventario.xlsx` no existe:

1. Presentar el estado de archivo maestro no inicializado.
2. Preparar el contenido inicial utilizando el inventario validado y la fuente autorizada conforme a los documentos oficiales.
3. No tratar como prueba de inexistencia un error de red, autorización, lectura o servidor.
4. Solicitar confirmación administrativa explícita para iniciar la creación.
5. Realizar una nueva verificación remota inmediatamente antes de publicar.
6. Si el archivo aparece entre ambas verificaciones, abortar la creación.
7. Utilizar una operación de creación sin SHA existente cuando corresponda al contrato de la API.
8. Confirmar la creación únicamente mediante una respuesta satisfactoria de GitHub.

**Restricción crítica para esta ejecución del Prompt 10:**

Aunque el código pueda implementar este flujo, no está autorizado a efectuar ahora una creación real en el repositorio del usuario.

La inicialización verdadera de `inventario.xlsx` se realizará únicamente en una etapa de activación posterior expresamente autorizada.

No publicar silenciosamente los productos demostrativos usados para pruebas como si fueran inventario real.

## 10. Actualización y protección frente a conflictos SHA

Cuando el archivo maestro ya exista:

1. Identificar el SHA remoto correspondiente al inventario base del espacio de trabajo.
2. Comprobar el SHA remoto actual inmediatamente antes de guardar.
3. Si el SHA cambió, rechazar la escritura.
4. Conservar intactas las modificaciones locales pendientes.
5. Informar que existe un conflicto entre la versión editada y la versión actual del inventario en GitHub.
6. Ofrecer una forma segura de volver a cargar la versión remota, sin reemplazar silenciosamente el trabajo pendiente.
7. No combinar automáticamente inventarios divergentes.
8. No sobrescribir la versión más reciente de otro proceso o administrador.
9. No sustituir el SHA base por el SHA nuevo hasta recibir confirmación válida del guardado.

Examinar también las condiciones de error de concurrencia reconocidas por GitHub y evitar su interpretación como éxito.

Una respuesta de conflicto o una solicitud de resultado incierto nunca debe provocar un reintento de escritura automático que pueda sobrescribir información.

## 11. Integración con el motor administrativo del Prompt 09

Reutilizar `EspacioTrabajoAdminInventario` y `PaquetePublicacionPendienteP10`.

No duplicar la lógica de creación o edición de productos.

La operación de publicación debe trabajar con una copia validada del inventario temporal.

Antes de guardar:

- Verificar la autorización administrativa en servidor.
- Confirmar que el espacio de trabajo pertenece a la sesión actual.
- Confirmar que existen cambios pendientes o una inicialización legítima.
- Obtener el inventario preparado y validado.
- Confirmar que la operación corresponde a la rama y ruta aprobadas.
- Verificar el SHA.

Después de una publicación confirmada:

- Actualizar la representación del inventario original.
- Actualizar la copia de trabajo.
- Actualizar el SHA base a la versión confirmada.
- Marcar los cambios como persistidos.
- Limpiar las marcas de productos creados y editados cuando proceda.
- Descartar los borradores de esos cambios ya confirmados.
- Conservar una estructura de estado consistente.
- Evitar que un fallo de actualización de la interfaz provoque una escritura duplicada.

Si una escritura falla o queda incierta:

- No descartar modificaciones locales.
- No eliminar el borrador.
- No declarar éxito.
- Permitir comprobar posteriormente el estado de GitHub antes de decidir cómo continuar.

## 12. Interfaz administrativa de guardado

Incorporar a la sección protegida **Productos** los controles mínimos necesarios.

La interfaz debe diferenciar:

- Cambios locales pendientes.
- Inventario remoto no inicializado.
- Inventario preparado y validado para guardar.
- Confirmación administrativa requerida.
- Guardado en curso.
- Guardado remoto confirmado.
- Conflicto de versión SHA.
- Error de autorización.
- Error de conexión.
- Resultado remoto incierto.

El control de confirmación debe exigir una acción consciente del administrador.

No guardar automáticamente en cada pulsación, cambio de campo o rerenderizado de Streamlit.

No guardar desde la interfaz pública.

Antes de permitir el guardado, mostrar claramente que se modificará el archivo maestro de GitHub.

Evitar publicaciones duplicadas por doble clic, reejecución de Streamlit o repetición accidental de una acción.

No presentar mensajes de confirmación hasta recibir evidencia válida de la operación remota.

## 13. Historial de cambios y auditoría

El MVP utiliza el historial de commits y versiones de GitHub como mecanismo de trazabilidad, conforme a la decisión de arquitectura simplificada.

Cada publicación debe generar un mensaje de commit claro y comprensible, por ejemplo:

`FERMS-V0: actualizar inventario de productos y ubicaciones`

No añadir un sistema paralelo de auditoría detallada por campo.

No afirmar que el historial de commits equivale a una auditoría campo por campo.

No realizar commits locales de Git como sustituto de la operación de guardado mediante GitHub API.

Conservar la trazabilidad de qué tarea implementó las funciones y qué operación produjo la actualización del archivo maestro.

## 14. Integración con la búsqueda pública

Después de un guardado remoto confirmado:

1. La próxima consulta pública nueva debe leer la versión vigente del inventario.
2. La paginación de una búsqueda ya iniciada debe mantener la consistencia de sus resultados conforme a las especificaciones.
3. No reutilizar indefinidamente un inventario obsoleto.
4. No modificar el esquema ni las reglas de búsqueda pública.
5. No habilitar acceso administrativo al visitante público.
6. No necesitar un reinicio manual del servidor para que una nueva consulta vea una actualización remota confirmada, salvo limitaciones documentadas que deban resolverse antes de aceptar la etapa.

Verificar mediante pruebas que una actualización confirmada se refleja en una consulta nueva.

## 15. Seguridad, atomicidad y manejo de errores

Examinar especialmente:

- Sesión ausente o vencida.
- Bloqueo administrativo activo.
- Contexto de dispositivo no permitido.
- Token ausente o inválido.
- Token sin permisos de escritura.
- Ruta remota inesperada.
- Rama equivocada.
- Archivo inexistente.
- Errores de conexión.
- Errores de autenticación y autorización de GitHub.
- Archivo Excel inválido.
- Categorías o ubicaciones inexistentes.
- Productos y asignaciones duplicados.
- Conflictos SHA.
- Doble publicación.
- Error durante la serialización.
- Respuesta remota ambigua.
- Fallo después de una escritura confirmada.
- Conservación de borradores ante errores.

No permitir operaciones parciales ni sobrescrituras silenciosas.

En todos los casos, la validación de servidor tendrá prioridad sobre las restricciones visuales.

## 16. Pruebas automatizadas

Crear:

`04_Pruebas/test_10_persistencia_inventario_github.py`

Utilizar inventarios sintéticos, relojes controlados y clientes HTTP simulados.

Cubrir al menos:

1. Serialización válida del inventario Excel.
2. Conservación de las cuatro hojas.
3. Conservación de nombres y orden de columnas.
4. Preservación de ceros iniciales.
5. Lectura y validación del Excel serializado.
6. Rechazo de inventario inválido antes de publicar.
7. Creación simulada cuando GitHub confirma archivo inexistente.
8. Rechazo de inicialización ante errores de conexión.
9. Rechazo de inicialización cuando el archivo aparece concurrentemente.
10. Actualización simulada con SHA correcto.
11. Rechazo con SHA diferente.
12. Preservación de cambios locales tras conflicto.
13. Rechazo de sesión administrativa vencida.
14. Rechazo de usuarios no autenticados.
15. Rechazo de contexto móvil cuando corresponda.
16. Rechazo de escritura con configuración no autorizada.
17. Manejo de credenciales inválidas o ausentes.
18. Ausencia de secretos en logs y errores.
19. Protección frente a doble clic o publicaciones repetidas.
20. Fallo HTTP sin confirmación.
21. Resultado de red incierto sin éxito falso.
22. Reintentos seguros solamente cuando puedan demostrarse.
23. Actualización del SHA tras éxito confirmado.
24. Limpieza de borradores después de éxito.
25. Preservación de borradores después de fallo.
26. Preservación de datos originales ante serialización fallida.
27. Confirmación explícita desde interfaz administrativa.
28. Rechazo de guardado desde interfaz pública.
29. Recuperación correcta después de una publicación confirmada.
30. Búsqueda pública nueva que muestra los datos actualizados.
31. Conservación del comportamiento de paginación.
32. Registro de mensaje de commit adecuado.
33. Ausencia de modificaciones de otros archivos del repositorio.
34. Prueba de integración `AppTest` del flujo de guardado simulado.
35. Verificación de que las pruebas no ejecutan escrituras reales.
36. Compatibilidad con los contratos P02–P09.
37. Manejo seguro de excepciones en el proceso de confirmación.
38. Comportamiento cuando el servidor reinicia o el estado temporal se pierde.
39. Preservación de seguridad y restricciones del Prompt 08.
40. Restauración correcta del estado del Prompt 09 tras guardar.

Añadir otras pruebas si el análisis revela riesgos importantes.

La cantidad mínima no sustituye la necesidad de cobertura útil y verificable.

**Todas las pruebas de escritura deben usar mocks: está prohibido ejecutar solicitudes reales que modifiquen GitHub durante la validación.**

## 17. Ejecución de pruebas sin sobrecargar Windows

Conservar la estrategia aprobada:

1. Comprobar sintaxis con `py_compile`.
2. Ejecutar únicamente las pruebas nuevas de P10.
3. Ejecutar las regresiones P02–P09 individualmente y de forma secuencial.
4. No ejecutar suites simultáneas.
5. No realizar pruebas de estrés intensivas.
6. Detenerse si aparece consumo excesivo, congelamiento o resultados inconsistentes.
7. No usar credenciales reales durante pruebas de escritura.
8. No lanzar despliegues.

Presentar números exactos de pruebas y resultados comprobados.

## 18. Archivos permitidos

Se permite crear:

- Un módulo especializado de escritura o persistencia GitHub en `03_Aplicacion/`, si resulta apropiado para separar responsabilidades.
- `04_Pruebas/test_10_persistencia_inventario_github.py`
- `05_Resultados/10_Resultado_Persistencia_Inventario_GitHub.md`

Se permite modificar, cuando esté justificado:

- `03_Aplicacion/app.py`
- `03_Aplicacion/administracion_productos.py`
- `03_Aplicacion/github_inventario.py`, solamente si la extensión de la capa GitHub aprobada es más adecuada que otro módulo.
- `03_Aplicacion/inventario.py`, exclusivamente para serialización y validación Excel si fuese imprescindible.

No modificar sin autorización adicional:

- `GEMINI.md`
- `AGENTS.md`
- Documentos conceptuales y especificaciones oficiales.
- Prompts anteriores.
- Informes y pruebas anteriores.
- `autenticacion.py`
- `busqueda.py`
- `requirements.txt`
- Archivos de despliegue o configuraciones ajenas al alcance.

**No crear ni modificar `03_Aplicacion/inventario.xlsx` en el directorio local o remoto durante la ejecución actual.**

Si una dependencia adicional o modificación de archivo protegido resulta imprescindible, solicitar autorización antes de proceder.

## 19. Informe de resultados y trazabilidad

Crear:

`05_Resultados/10_Resultado_Persistencia_Inventario_GitHub.md`

El informe debe contener:

- `TASK_ID`
- Fecha y hora reales.
- Título de tarea.
- Nivel de auditoría.
- Solicitud original íntegra.
- Comprensión del agente.
- Acciones realmente realizadas.
- Documentos y especificaciones consultados.
- Requisitos RF y criterios CA relacionados.
- Arquitectura de persistencia.
- Contratos de lectura y escritura de GitHub.
- Estrategia de serialización Excel.
- Modelo de control de conflictos SHA.
- Controles de autorización y confirmación.
- Manejo de errores.
- Evidencia de pruebas y regresiones.
- Archivos creados y modificados.
- Restricciones respetadas.
- Limitaciones y riesgos residuales.
- Funciones pendientes de activación.
- Estado final de Git.
- Confirmación expresa de que no se escribieron datos reales en GitHub.

Distinguir claramente entre funcionalidad implementada, funcionalidad probada mediante simulación y funcionalidad todavía no activada contra GitHub real.

No declarar comprobaciones inexistentes.

## 20. Restricciones finales

Durante esta ejecución está prohibido:

- Publicar el archivo maestro real.
- Ejecutar escrituras reales a GitHub Contents API.
- Crear o modificar `03_Aplicacion/inventario.xlsx`.
- Introducir secretos en el repositorio.
- Ejecutar `git commit`, `git push`, `git merge`, `git reset`, `git restore` o `git clean`.
- Modificar documentos oficiales aprobados.
- Añadir una base de datos distinta de la arquitectura aprobada.
- Implementar Gemini operativo.
- Incorporar ventas, pagos, precios o cantidades.
- Ejecutar despliegues.
- Comenzar el Prompt 11.
- Activar automáticamente las funciones de escritura real al terminar las pruebas.

Una autorización futura para activar operaciones reales deberá ser explícita y posterior a la revisión independiente.

## 21. Entrega y condición de cierre

Al finalizar:

1. Presentar resumen de implementación.
2. Enumerar exactamente los archivos afectados.
3. Presentar pruebas y resultados reales.
4. Mostrar cómo se protege el SHA.
5. Explicar cómo se bloquean operaciones de escritura no autorizadas.
6. Confirmar que la funcionalidad de escritura fue probada exclusivamente mediante simulaciones.
7. Confirmar que `inventario.xlsx` no fue creado ni modificado.
8. Presentar `git status --short`.
9. Identificar cualquier decisión pendiente de autorización del usuario.
10. Detenerse para revisión independiente.

**No ejecutar commit ni push. No activar todavía la escritura real del inventario.**