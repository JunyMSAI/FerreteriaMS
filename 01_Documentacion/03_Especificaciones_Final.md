# Especificaciones de la Versión Final: FerreteríaMS

**Proyecto:** FerreteríaMS  
**Documento:** `01_Documentacion/03_Especificaciones_Final.md`
**Naturaleza:** Especificaciones **incrementales** respecto a `02_Especificaciones_v0.md`  
**Base de decisiones:** DEC-FINAL-001 a DEC-FINAL-034  
**Etapa anterior:** FerreteríaMS v0, P01–P13

> **Regla de alcance:** este documento establece únicamente los cambios pendientes aprobados para la versión final. Las funcionalidades, validaciones y controles de v0 siguen vigentes por referencia, salvo ampliación expresa indicada aquí. No constituye una reescritura de v0. Las propuestas de implementación que requieran resolver detalles técnicos deberán preservar este alcance, sin añadir funcionalidades.

## 1. Problema y usuario

### 1.1. Problema adicional que atiende la versión final

FerreteríaMS v0 permite localizar productos y administrar su información básica, pero para gestionar las **categorías y ubicaciones** es necesario editar el Excel maestro; además, el área de Gemini todavía no proporciona asesoría funcional. La versión final resolverá exclusivamente esas necesidades y permitirá **desactivar y reactivar productos** sin borrar sus datos.

### 1.2. Usuarios

- **Cliente:** continúa buscando y localizando productos sin autenticación; adicionalmente podrá realizar consultas escritas sobre ferretería, herramientas, materiales, mantenimiento, reparaciones y proyectos relacionados.
- **Administrador:** continúa utilizando la autenticación existente; adicionalmente podrá crear y editar categorías y ubicaciones, desactivar o reactivar productos y gestionar las relaciones necesarias sin editar manualmente el archivo maestro.

### 1.3. Alcance incremental aprobado

**Bloque 1 — Administración:** categorías, ubicaciones y estados de productos, con integridad referencial y reutilización de la persistencia GitHub.  
**Bloque 2 — Gemini:** chat de texto, bilingüe, contextual, seguro y acotado en consumo.  
**Datos de evaluación independientes:** inventario ficticio de 200 productos (DEC-FINAL-032), preparado para pruebas sin sustituir automáticamente el inventario oficial.

## 2. Qué hace el producto

### 2.1. Requisitos funcionales nuevos (RF-F)

Los identificadores `RF-F-###` son exclusivos de esta etapa; no sustituyen los requisitos `RF-###` de v0.

#### Administración de categorías y ubicaciones

**RF-F-001 — Crear categorías.** El administrador podrá incorporar una categoría con identificador único y nombre obligatorio en la hoja `Categorías`, usando la estructura existente. Los cambios serán temporales hasta su publicación confirmada.

**RF-F-002 — Editar categorías.** El administrador podrá modificar el nombre de una categoría. `Categoria_ID` permanecerá inmutable; los productos asociados seguirán enlazados por ese identificador y mostrarán el nuevo nombre sin reasignación (DEC-FINAL-026).

**RF-F-003 — Evitar categorías duplicadas.** No se permitirán nombres iguales tras normalizar espacios sobrantes, mayúsculas/minúsculas y acentos. Se comunicará el motivo del rechazo (DEC-FINAL-027).

**RF-F-004 — Crear ubicaciones.** El administrador podrá crear `Ubicacion_ID`, `Rack`, `Columna`, `Nivel` y `Posicion`, preservando los tipos de texto y las validaciones actuales.

**RF-F-005 — Editar ubicaciones libres.** Se podrá modificar la posición física (`Rack`, `Columna`, `Nivel`, `Posicion`) únicamente si la ubicación **no tiene ninguna asignación de productos**. `Ubicacion_ID` será inmutable. Si está asociada a productos, se bloqueará el cambio y se informará que primero deben reasignarse (DEC-FINAL-025).

**RF-F-006 — Evitar ubicaciones duplicadas.** Se rechazará una ubicación cuya combinación de rack, columna, nivel y posición ya exista, con mensaje comprensible, reutilizando la validación de unicidad del motor (DEC-FINAL-027).

**RF-F-007 — Desactivar ubicaciones.** Se permitirá desactivar una ubicación solo cuando **no tenga productos asociados**. Una ubicación desactivada no podrá asignarse a productos nuevos ni existentes. No se eliminarán filas para simular la desactivación (DEC-FINAL-004).

**RF-F-008 — Desactivar y reactivar productos.** El administrador podrá cambiar el estado activo/inactivo sin borrar el producto ni sus asignaciones. Los productos inactivos no aparecerán en búsquedas públicas ni se presentarán a Gemini como artículos registrados disponibles en el catálogo activo. La reactivación conservará sus datos y exigirá que cumplan las reglas vigentes de categoría y ubicaciones (DEC-FINAL-003).

**RF-F-009 — Coherencia de estados.** Las nuevas acciones no podrán dejar un producto activo con ubicación inválida o inactiva ni con referencias rotas. La desactivación de ubicaciones exigirá cero asignaciones, incluso de productos inactivos, mientras esos vínculos se conserven. Reutilizar las validaciones de v0 donde proceda.

**RF-F-010 — Persistencia de cambios.** Las operaciones de categorías, ubicaciones y estados de productos utilizarán el mismo flujo ya aprobado de cambios locales, confirmación del administrador, serialización del único `inventario.xlsx`, verificación de integridad, control de concurrencia SHA y publicación por GitHub Contents API (DEC-FINAL-024, DEC-FINAL-028 y DEC-FINAL-029). No se creará otra base de datos ni un segundo mecanismo de guardado.

**RF-F-011 — Conflictos y errores.** Si GitHub rechaza la publicación o existe conflicto SHA, se preservarán los cambios locales conforme a v0; la recarga que los descarte exigirá confirmación. No se implementará fusión automática ni cola avanzada de reintentos.

#### Gemini operativo para clientes

**RF-F-012 — Chat básico de texto.** El cliente podrá escribir preguntas y recibir respuestas en la sección Gemini existente, con seguimiento contextual durante la sesión y sin cuentas adicionales ni historial persistente (DEC-FINAL-002, 009 y 019).

**RF-F-013 — Asesoría útil y técnicamente pertinente.** Gemini atenderá consultas de ferretería, herramientas, materiales, mejoras del hogar, reparaciones, mantenimiento y proyectos relacionados. La pertinencia técnica y la seguridad de la solución tendrán prioridad sobre intentar recomendar productos del negocio.

**RF-F-014 — Consulta contextual del inventario.** La aplicación obtendrá productos relevantes mediante la lógica existente de consulta/búsqueda, evitando enviar el inventario completo en cada pregunta (DEC-FINAL-010). Los datos confirmados del catálogo se separarán de las recomendaciones generales.

**RF-F-015 — Productos registrados y no registrados.** Gemini podrá recomendar materiales o herramientas necesarios para una solución aunque no estén en el catálogo; indicará claramente su falta de confirmación en FerreteríaMS. Solo citará nombre, código y ubicación como **datos del catálogo** cuando estén confirmados en el inventario activo. No inventará códigos, ubicaciones, cantidades o disponibilidad física (DEC-FINAL-011 y 021).

**RF-F-016 — Producto seleccionado.** Al seleccionar un producto desde la búsqueda, el chat recibirá su referencia actual como contexto. Si se selecciona otro, la referencia se actualizará sin borrar la conversación, evitando atribuirle características del producto anterior (DEC-FINAL-017 y 020).

**RF-F-017 — Idioma.** El asistente responderá normalmente en el idioma utilizado por el cliente (español o inglés) y atenderá solicitudes de cambio de idioma en el chat. No será necesario un selector adicional (DEC-FINAL-013).

**RF-F-018 — Seguridad de asesoría.** Ante temas técnicos de riesgo, Gemini expresará incertidumbre cuando falten datos, incluirá precauciones proporcionadas y recomendará instrucciones del fabricante o profesionales cualificados cuando proceda; no afirmará certezas no documentadas (DEC-FINAL-012).

**RF-F-019 — Aviso permanente.** El área del chat mostrará un aviso fijo, visible y breve de que las respuestas provienen de inteligencia artificial y pueden contener errores; incluirá la recomendación de verificar información técnica y medidas de seguridad (DEC-FINAL-033).

**RF-F-020 — Alcance temático.** Gemini atenderá consultas relacionadas con ferretería o con proyectos donde sus productos y materiales sean pertinentes; si la pregunta es ajena (p. ej., pronóstico del tiempo), explicará cortésmente su especialización y redirigirá. No se incorporará otro clasificador de IA (DEC-FINAL-034).

**RF-F-021 — Contexto temporal limitado.** Se conservará en memoria de sesión una cantidad máxima configurable de mensajes recientes enviados al modelo. No habrá base de datos de conversaciones ni almacenamiento permanente (DEC-FINAL-022).

**RF-F-022 — Nueva conversación.** El botón «Nueva conversación» limpiará mensajes y contexto temporal, pero **no reiniciará** el contador de consultas consumidas dentro de la ventana de uso (DEC-FINAL-016).

**RF-F-023 — Límites de uso.** Se limitarán preguntas por ventana de sesión, tamaño de cada entrada e historial contextual. Al superar la cuota local se impedirán nuevas consultas hasta la siguiente ventana; el buscador seguirá disponible. Estos límites por sesión **no son garantía de cuota global** frente a múltiples usuarios (DEC-FINAL-015 y 023).

**RF-F-024 — Errores de Gemini.** Ante ausencia de clave, indisponibilidad, tiempo de espera, agotamiento de cuota o error de API, la aplicación mostrará mensaje claro y una opción de reintento manual cuando sea apropiado. No interrumpirá la búsqueda pública ni cambiará automáticamente a servicios de pago (DEC-FINAL-014 y 030).

**RF-F-025 — Conexión y secretos.** La llamada a Gemini API se realizará desde el servidor Python en Streamlit, usando una clave configurada en Streamlit Secrets. No se incorporará un backend adicional, ni se expondrán la clave y los secretos en navegador, repositorio o mensajes de error (DEC-FINAL-018 y 030).

## 3. Entradas y salidas

### 3.1. Entradas administrativas nuevas

- Categorías: identificador al crear; nombre al crear y renombrar.
- Ubicaciones: identificador al crear; rack, columna, nivel y posición al crear/editar; acción de desactivación cuando carezcan de asignaciones.
- Productos: selección de un producto y cambio activo/inactivo, preservando sus datos.
- Confirmación de publicación: se reutilizan los controles existentes.

### 3.2. Salidas administrativas

- Catálogos y estados actualizados en el espacio de trabajo; éxito persistente únicamente tras confirmación de GitHub.
- Mensajes claros ante duplicados, ubicación ocupada, referencias inválidas, conflictos SHA o fallos de red.

### 3.3. Entradas y salidas del chat

- Entradas: pregunta escrita, historial temporal acotado, producto actualmente seleccionado cuando exista y subconjunto pertinente de productos activos del inventario.
- Salidas: respuesta técnica en español/inglés, distinción explícita entre artículos confirmados y recomendaciones generales, advertencias cuando corresponda, errores comprensibles y contador/límite de sesión cuando se alcance.
- No se introducirán fotografías, audio, precios, existencias ni datos personales adicionales.

### 3.4. Cambios mínimos del archivo Excel

Se conservarán las **cuatro hojas oficiales** `Productos`, `Categorías`, `Ubicaciones` y `Asignaciones`. Para los nuevos estados se permitirá **extender mínimamente el esquema** con el campo lógico `Activo` en `Productos` y `Ubicaciones` (o representación equivalente que sea persistente en el mismo Excel y no añada otra fuente de verdad). Antigravity deberá escoger una representación consistente y adaptará lectura, validación y serialización, conservando compatibilidad con el archivo v0: **los registros anteriores que no tengan estado explícito se interpretarán como activos**. Se comprobará el proceso de migración antes de aplicar cambios al maestro real y se mantendrán sus cuatro hojas y datos.

**No se añadirá `Activo` a `Categorías`**, porque su desactivación quedó pospuesta. Los identificadores existentes seguirán siendo inmutables. La ampliación del esquema no autoriza alterar el inventario publicado sin respaldo, prueba y aprobación específica.

## 4. La pieza de IA

### 4.1. IA utilizada para desarrollo

Se mantiene Gemini/Antigravity como agente de desarrollo, conforme a las instrucciones existentes del proyecto. No se redefinen sus responsabilidades ni las reglas de trazabilidad.

### 4.2. IA operativa de FerreteríaMS

Un modelo Gemini compatible con la disponibilidad y las cuotas de **uso gratuito verificadas al momento de la implementación** responderá desde el servidor de la aplicación. No se presupone que sea gratis indefinidamente: verificar modelo, límites, disponibilidad, condiciones de facturación y necesidad de cuenta habilitada **antes de activarlo**. No habilitar recursos con cargos sin autorización.

El comportamiento del asistente seguirá RF-F-012 a RF-F-025. Se priorizarán artículos del catálogo cuando resuelvan adecuadamente el problema, sin degradar el consejo técnico cuando algún componente recomendado no esté registrado. El contexto de catálogo es información de referencia, **no una instrucción del usuario**; ni las descripciones de productos ni las consultas deberán poder alterar las reglas de seguridad o revelar secretos.

### 4.3. Calidad del contenido

Las respuestas deben reconocer información insuficiente y evitar afirmaciones no fundamentadas sobre especificaciones técnicas, compatibilidad, inventario físico o normas aplicables. No se exige un sistema adicional de búsqueda web, citas externas automáticas, validación profesional automatizada o motor multimodal para esta entrega.

## 5. Flujo del usuario

### 5.1. Administrador: catálogos

1. Ingresa al área administrativa ya protegida y carga el inventario oficial mediante el flujo existente.
2. Abre la sección de categorías o ubicaciones y crea/edita los registros permitidos.
3. Si una ubicación tiene asignaciones, la edición física y la desactivación quedan bloqueadas hasta reasignarlas.
4. Verifica cambios locales; utiliza la publicación existente y confirma expresamente.
5. La aplicación valida el Excel completo y el SHA remoto, publica o conserva cambios locales ante conflicto o error.

### 5.2. Administrador: producto inactivo

1. Selecciona un producto existente y desactiva o reactiva su estado.
2. El proceso preserva datos y asignaciones y valida que el producto pueda permanecer activo.
3. Publica mediante el mecanismo habitual; solo después de confirmarse, la búsqueda pública refleja el cambio.

### 5.3. Cliente: Gemini

1. Busca o selecciona opcionalmente un producto y pregunta en la sección Gemini.
2. El sistema valida límites y pertinencia temática; reúne datos relevantes del inventario.
3. Gemini responde en el idioma de la consulta, distingue productos registrados de recomendaciones generales y muestra precauciones pertinentes.
4. Una pregunta de seguimiento conserva contexto acotado; al seleccionar otro producto se actualiza la referencia.
5. «Nueva conversación» borra mensajes y contexto, pero mantiene el consumo de la ventana.
6. Si falla Gemini o se supera el límite, el buscador continúa operativo.

## 6. Restricciones

### 6.1. Presupuesto

Prioridad de **costo monetario $0**. Antes de configurar un servicio externo se confirmarán su nivel gratuito, límites, condiciones, posibles cargos y requisitos de habilitación. No se autoriza la activación automática de planes de pago.

### 6.2. Tecnologías

Mantener Streamlit + Python + pandas + archivo inventario `.xlsx` en GitHub. Reutilizar GitHub Contents API, secretos y autenticación ya existentes. Integrar Gemini desde Python del servidor mediante la biblioteca compatible elegida; no incorporar base de datos nueva, frontend independiente ni un segundo backend.

### 6.3. Seguridad

Reutilizar autorización administrativa, confirmación explícita, control SHA, saneamiento de errores y protección de secretos de v0. La ampliación del modelo de datos debe ser compatible y preservar registros existentes. La IA no modificará productos ni ejecutará funciones administrativas; utilizará datos del inventario en modo lectura.

### 6.4. Compatibilidad

Mantener búsqueda y administración según restricciones de dispositivos existentes; el chat público debe poder usarse en escritorio. Las fallas de Gemini no bloquearán la localización.

### 6.5. Consumo y privacidad

No almacenar conversaciones fuera de la memoria temporal de sesión. Definir parámetros de límite de preguntas, longitud de mensajes y ventana de uso como constantes configurables, con valores conservadores y documentados por Antigravity; no construir administración visual para dichos parámetros. Tener presente que Streamlit puede reiniciar el estado en memoria y que un límite por sesión no impide automáticamente abuso distribuido.

### 6.6. Integridad y persistencia

No perder datos de v0, no destruir asignaciones, mantener la unicidad y las cuatro hojas oficiales, y usar un único archivo maestro remoto. Prohibida la publicación automática del inventario ficticio de evaluación al maestro oficial.

### 6.7. Calidad y ejecución

Desarrollo en **dos bloques**: primero administración, después Gemini (DEC-FINAL-031). Pruebas nuevas y focalizadas de las funciones añadidas y sus dependencias inmediatas; no repetir sin causa técnica las suites ya aprobadas. No cambiar el código de funcionalidades estables para mejoras cosméticas o refactorizaciones generales.

## 7. Criterios de aceptación

Los identificadores `CA-F-###` son adicionales a los CA de v0. Las verificaciones pueden combinar escenarios para evitar redundancias.

| ID | Criterio verificable |
|---|---|
| CA-F-001 | Se crea una categoría válida y se publica mediante el mecanismo GitHub existente. |
| CA-F-002 | Se renombra una categoría utilizada sin modificar su ID y sus productos muestran el nuevo nombre. |
| CA-F-003 | Una categoría duplicada por nombre normalizado se rechaza con explicación clara. |
| CA-F-004 | Se crea una ubicación válida y se rechaza una combinación física duplicada. |
| CA-F-005 | No se puede modificar físicamente ni desactivar una ubicación con productos asociados; tras reasignarlos se permite la operación. |
| CA-F-006 | Una ubicación desactivada no se ofrece para asignar nuevos productos. |
| CA-F-007 | Desactivar un producto lo retira de la búsqueda pública y de las recomendaciones de catálogo activo; reactivarlo recupera sus datos y ubicaciones cuando sean válidos. |
| CA-F-008 | Todas las operaciones nuevas preservan integridad del Excel, controles SHA, confirmación y conservación de cambios locales ante fallos. |
| CA-F-009 | El inventario v0 se lee y migra sin pérdida de datos ni cambio involuntario de estados; las cuatro hojas se conservan. |
| CA-F-010 | Gemini acepta preguntas de ferretería en texto, permite seguimiento temporal y responde en español o inglés según la consulta. |
| CA-F-011 | Gemini usa productos pertinentes del catálogo y presenta código, nombre y ubicación solo cuando estén confirmados; también ofrece consejos técnicos útiles sobre materiales no registrados, identificándolos como no confirmados. |
| CA-F-012 | Al cambiar de producto seleccionado, Gemini usa el nuevo contexto conservando la conversación y sin mezclar datos. |
| CA-F-013 | «Nueva conversación» limpia el chat sin reiniciar el contador de uso. |
| CA-F-014 | Se aplica el límite de consultas/tamaño/contexto; al agotarse, Gemini bloquea nuevas preguntas durante la ventana, mientras la búsqueda sigue funcionando. |
| CA-F-015 | El aviso fijo de IA permanece visible y las consultas claramente ajenas a ferretería reciben una redirección cortés, sin confundir preguntas legítimas sobre proyectos. |
| CA-F-016 | Ante una consulta técnica con datos insuficientes o riesgo se comunica incertidumbre, precauciones y recomendación profesional pertinente. |
| CA-F-017 | Ausencia de API key, fallo de red o cuota agotada producen mensaje seguro y no interrumpen búsqueda ni navegación. |
| CA-F-018 | La clave Gemini se obtiene únicamente del servidor/Secrets y no aparece en repositorio, interfaz ni resultados de pruebas. |
| CA-F-019 | Se registra la verificación de las condiciones gratuitas aplicables antes de activar Gemini; no se habilita facturación sin aprobación. |
| CA-F-020 | La aplicación desplegada ejecuta un flujo mínimo de administración de catálogos y una consulta Gemini válida, sin regresión crítica en búsqueda o persistencia. |

### 7.1. Evidencia y estrategia de pruebas

Registrar para cada criterio **prueba, resultado, fecha y archivo/commit asociado** cuando aplique. Priorizar simulaciones y pruebas de integración focalizadas; las operaciones reales de escritura o cambios de Secrets requerirán aprobación específica, respaldo y validación dirigida. Una prueba simulada no equivale a una publicación real.

### 7.2. Inventario de evaluación (entregable auxiliar)

Preparar **por separado**, en una fase de pruebas autorizada, un archivo Excel de evaluación con **200 productos ficticios realistas** agrupados para proyectos de ferretería, con categorías, ubicaciones y asignaciones referencialmente válidas. Etiquetarlo claramente como conjunto de pruebas, conservarlo fuera de la ruta maestra de producción hasta autorización explícita, y validar búsqueda, ubicación y Gemini con escenarios representativos. Su contenido específico no constituye un nuevo requisito funcional de la aplicación ni requiere publicar datos ficticios en GitHub.

## 8. Fuera de alcance (por ahora)

### 8.1. Pospuesto para Future Enhancements (no bloquea la entrega)

- Desactivación/reactivación de categorías (DEC-FINAL-005).
- Eliminación definitiva de productos (DEC-FINAL-006).
- Fusión automática de conflictos GitHub (DEC-FINAL-029).
- Funcionalidades avanzadas de asesoría, control de consumo, recuperación o memoria, fuera del alcance básico aprobado.

### 8.2. Descartado del alcance (no bloquea la entrega)

- Auditoría detallada de cambios dentro de la aplicación; se conserva historial de commits GitHub (DEC-FINAL-007).
- Configuración del nombre y logotipo desde la administración (DEC-FINAL-008).
- Funcionalidades de voz o análisis de imágenes en Gemini para esta entrega (DEC-FINAL-019 aprobó texto únicamente).

### 8.3. Regla de cierre

Las opciones pospuestas o descartadas **no se consideran defectos pendientes ni impedimentos para declarar terminada la versión final**. Solo serán obligatorios los requisitos nuevos aprobados de este documento y los requisitos de v0 que sigan vigentes.

## 9. Despliegue

### 9.1. Entorno existente

Reutilizar el repositorio, la rama y la aplicación Streamlit Cloud ya operativos, sin recrearlos. Mantener el entorno Python 3.12 utilizado en el despliegue actual, sujeto a compatibilidad real de dependencias.

### 9.2. Orden de liberación

1. **Bloque 1:** administración de categorías/ubicaciones y estado de productos; validación focalizada y aprobación antes de integrar.
2. **Bloque 2:** Gemini de texto, Secrets y controles mínimos de seguridad/consumo; validación focalizada y aprobación.
3. **Aceptación final:** comprobar en despliegue únicamente los nuevos flujos y ausencia de regresiones críticas; cerrar la entrega según alcance aprobado.

### 9.3. Secretos y costos

La clave Gemini se configurará directamente en Streamlit Secrets cuando se autorice, sin mostrarla a Antigravity ni incorporarla al repositorio. Se verificará el uso gratuito aplicable antes de habilitar el chat. Si el servicio no puede activarse en las condiciones autorizadas, se documentará el bloqueo y se solicitará decisión del responsable; no se asumirá aprobación automática para usar servicios pagados.

### 9.4. Documentos y prompts posteriores

Solo **después de aprobar estas especificaciones** se identificarán los documentos existentes que deban actualizarse y se elaborarán los prompts secuenciales de Antigravity para los dos bloques. Mantener el proceso de aprobación, trazabilidad y commits, sin introducir tareas redundantes.

---

**Fin del documento, este documento no autoriza por sí mismo cambios de código, publicación de archivos sin mi autorización, modificaciones al inventario en Excel ni activación de servicios de pago.**