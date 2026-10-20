# Especificaciones de la Versión 0: FerreteríaMS
 
**Documento:** `02_Especificaciones_v0.md` 
**Versión de la aplicación:** v0 
**Documento de referencia:** `01_Concepto_FerreteriaMS_Final.docx`  
**Enfoque:** Desarrollo de software asistido por inteligencia artificial  
**Presupuesto de servicios:** $0.00 durante la prueba de concepto

---

## 1. Problema y usuario

### 1.1. Problema que atiende la aplicación

Los clientes de una ferretería frecuentemente pierden tiempo buscando productos en racks, estanterías y diferentes áreas de la tienda.

Cuando desconocen la ubicación exacta de un artículo, necesitan recorrer los pasillos o solicitar ayuda a los empleados.

FerreteríaMS v0 atenderá este problema permitiendo que los clientes busquen productos por nombre y conozcan su ubicación física dentro de la tienda.

### 1.2. Usuarios

**Cliente de la ferretería**

- Puede consultar productos sin autenticarse.
- Puede utilizar la aplicación desde un navegador web en computadora o celular.
- Puede buscar productos y consultar su ubicación física.
- No puede modificar el inventario.

**Administrador de la ferretería**

- Debe autenticarse antes de administrar productos.
- Puede crear y editar productos.
- Puede asignar o retirar ubicaciones existentes.
- Puede identificar la ubicación principal de cada producto.
- El acceso administrativo se realizará exclusivamente desde la versión web para computadora, según el concepto aprobado.
- Inicialmente existirá una sola cuenta administrativa.

### 1.3. Alcance de la solución

FerreteríaMS v0 se concentrará en la búsqueda, localización y administración básica del inventario.

No controlará existencias físicas, cantidades, precios ni transacciones comerciales.

Encontrar un producto significa que está registrado en el inventario, no que necesariamente existan unidades disponibles para la venta.

### 1.4. Participación de la inteligencia artificial

Gemini será utilizado como agente de desarrollo para construir FerreteríaMS siguiendo los documentos, instrucciones y prompts aprobados.

Dentro de la aplicación v0, Gemini todavía no tendrá funcionamiento operativo.

La interfaz mostrará el espacio reservado para la futura asistencia mediante IA, identificado como «Próximamente».

---

## 2. Qué hace el producto

### 2.1. Definición de Requisito Funcional (RF)

**RF significa Requisito Funcional.**

Un Requisito Funcional describe una función, operación o comportamiento que la aplicación debe realizar.

Cada requisito se identifica mediante un código único para facilitar su seguimiento durante el desarrollo, las pruebas y la documentación.

Ejemplo:

**RF-001 — Búsqueda por nombre:** el cliente podrá buscar productos utilizando su nombre.

Los códigos RF permitirán relacionar las funcionalidades solicitadas con las tareas de programación y sus respectivos criterios de aceptación.

### 2.2. Búsqueda pública de productos

**RF-001 — Búsqueda por nombre**

El cliente podrá introducir el nombre de un producto en un campo de búsqueda y ejecutar la consulta mediante el botón Buscar.

La búsqueda será exclusivamente por nombre, no por marca ni por categoría.

**RF-002 — Coincidencias parciales**

La búsqueda admitirá coincidencias parciales entre el texto introducido y los nombres de productos registrados.

**RF-003 — Normalización del texto**

La búsqueda ignorará diferencias entre letras mayúsculas y minúsculas, así como diferencias de acentuación.

**RF-004 — Presentación de resultados**

La aplicación mostrará los productos registrados que correspondan al término buscado.

**RF-005 — Consulta de detalles**

El cliente podrá consultar los detalles de un producto encontrado, incluyendo su información descriptiva y ubicación.

**RF-006 — Localización física**

Para cada producto encontrado, la aplicación mostrará su ubicación mediante:

- Rack o estantería.
- Columna.
- Nivel.
- Posición.

**RF-007 — Ubicaciones múltiples**

Cuando un producto tenga varias ubicaciones, deberán distinguirse la ubicación principal y las ubicaciones secundarias.

**RF-008 — Producto no encontrado**

Cuando una búsqueda no encuentre coincidencias, la aplicación mostrará:

«No encontramos este producto en nuestro inventario».

Este mensaje indica únicamente que no se encontró en el inventario registrado; no afirma que la ferretería no lo venda.

**RF-009 — Acceso público**

Las búsquedas podrán realizarse sin necesidad de crear una cuenta o iniciar sesión.

**RF-010 — Diseño adaptable**

La interfaz de búsqueda y localización estará disponible para computadoras y dispositivos móviles.

**RF-035 — Orden de resultados**

Los productos cuyos nombres comiencen con el término buscado aparecerán antes que los productos cuyos nombres lo contengan en otra posición.

Dentro de cada grupo se utilizará un orden estable y reproducible.

**RF-036 — Paginación**

Se mostrarán hasta diez resultados por página, con controles para consultar las páginas siguientes y anteriores cuando corresponda.

**RF-037 — Búsqueda vacía**

Cuando el usuario intente buscar sin introducir un nombre, la aplicación solicitará que escriba un producto.

**RF-038 — Errores de consulta**

Cuando ocurra un error de conexión o lectura del inventario, la aplicación mostrará un mensaje de error con posibilidad de reintentar.

No se presentará un fallo técnico como si fuese una búsqueda legítima sin resultados.

### 2.3. Administración básica del inventario

**RF-011 — Acceso administrativo protegido**

El administrador deberá autenticarse antes de realizar modificaciones al inventario.

**RF-012 — Entrada al área administrativa**

Al intentar acceder a la pestaña Productos, la aplicación deberá presentar el mecanismo de Login/Logout establecido en el concepto.

**RF-013 — Restricción de administración móvil**

La interfaz móvil no permitirá acceder al área administrativa para modificar el inventario.

Esta restricción también deberá aplicarse a las operaciones de modificación, no solamente a la visibilidad de botones.

**RF-014 — Crear productos**

El administrador podrá registrar nuevos productos utilizando un formulario.

**RF-015 — Editar productos**

El administrador podrá modificar la información permitida de los productos existentes.

El código único de un producto existente no podrá modificarse.

**RF-016 — Seleccionar categorías**

El formulario permitirá asociar un producto con una categoría previamente registrada en el archivo Excel.

**RF-017 — Asignar ubicaciones**

El administrador podrá asignar a un producto una o varias ubicaciones previamente registradas.

**RF-018 — Retirar ubicaciones**

El administrador podrá retirar asociaciones de ubicaciones, siempre que la operación respete las reglas de integridad.

**RF-019 — Ubicación principal**

Cada producto deberá conservar exactamente una ubicación principal válida.

**RF-020 — Validaciones**

Antes de guardar modificaciones se comprobarán:

- Unicidad del código del producto.
- Cumplimiento de los campos obligatorios.
- Existencia y validez de las categorías y ubicaciones asociadas.
- Existencia de al menos una ubicación por producto.
- Existencia de exactamente una ubicación principal.
- Ausencia de asignaciones duplicadas.

**RF-021 — Catálogos predefinidos**

Las categorías y ubicaciones físicas estarán predefinidas en el archivo Excel.

La creación y edición de esos catálogos desde FerreteríaMS v0 no estará disponible.

### 2.4. Inventario y persistencia

**RF-022 — Archivo maestro**

La información del inventario estará almacenada en un único archivo llamado `inventario.xlsx`.

**RF-023 — Estructura del archivo**

El archivo contendrá cuatro hojas:

1. Productos.
2. Categorías.
3. Ubicaciones.
4. Asignaciones.

**RF-024 — Procesamiento**

La aplicación utilizará pandas para leer, consultar, procesar y transformar los datos del inventario.

Se podrán utilizar bibliotecas complementarias necesarias para trabajar con archivos `.xlsx`.

**RF-025 — Almacenamiento en GitHub**

El archivo maestro estará almacenado en GitHub.

**RF-026 — Guardado de modificaciones**

Las modificaciones realizadas por el administrador se guardarán mediante GitHub API.

**RF-027 — Conflictos de versiones**

La aplicación deberá detectar conflictos de versiones y evitar sobrescrituras silenciosas.

El guardado deberá comprobar que la versión sobre la cual se realizaron los cambios continúa siendo válida.

**RF-028 — Actualización de búsquedas**

Las búsquedas deberán consultar la versión vigente del inventario sin requerir un reinicio manual de Streamlit.

**RF-029 — Inicialización automática**

Si el archivo maestro todavía no existe en GitHub, la aplicación podrá generar automáticamente un inventario inicial de ejemplo.

**RF-030 — Protección del archivo existente**

La generación inicial no deberá sobrescribir un inventario existente.

**RF-031 — Datos de demostración**

Los datos utilizados como ejemplos deberán identificarse como demostrativos.

### 2.5. Interfaz Gemini v0

**RF-032 — Área visual de Gemini**

La aplicación tendrá una sección visual destinada a la futura asistencia mediante Gemini.

**RF-033 — Identificación del estado**

La sección mostrará claramente «Próximamente».

**RF-034 — Sin integración funcional**

FerreteríaMS v0 no realizará consultas operativas a Gemini API ni generará asesoría mediante el modelo.

---

## 3. Entradas y salidas

### 3.1. Operaciones del cliente

| Entrada | Salida esperada |
|---|---|
| Nombre de producto | Lista de coincidencias registradas |
| Nombre parcial | Productos cuyos nombres coincidan parcialmente |
| Nombre con diferencias de acentos o mayúsculas | Resultados normalizados |
| Selección de un producto | Información descriptiva y ubicación física |
| Producto con varias ubicaciones | Principal y secundarias diferenciadas |
| Búsqueda con más de diez coincidencias | Resultados paginados |
| Búsqueda sin coincidencias | Mensaje de producto no encontrado en el inventario |
| Campo de búsqueda vacío | Solicitud de introducir el nombre |
| Error técnico de consulta | Mensaje comprensible y opción de reintentar |

### 3.2. Operaciones del administrador

| Entrada | Salida esperada |
|---|---|
| Usuario y contraseña válidos | Acceso autorizado a administración |
| Credenciales incorrectas | Acceso denegado y aplicación de controles de seguridad |
| Datos válidos de un producto nuevo | Nuevo producto guardado |
| Cambios válidos en un producto | Actualización persistente |
| Selección de categoría | Asociación con categoría predefinida |
| Selección de ubicación | Asociación con ubicación existente |
| Cambio de ubicación principal | Actualización de la asignación principal |
| Datos inválidos | Mensaje de validación, sin guardar información inconsistente |
| Conflicto entre versiones | Aviso de conflicto y protección contra sobrescritura |

### 3.3. Estructura aprobada del archivo `inventario.xlsx`

El archivo contendrá exactamente las cuatro hojas definidas en el concepto.

#### Hoja 1 — Productos

| Columna | Tipo lógico | Descripción |
|---|---|---|
| Codigo_Producto | Texto | Identificador único e inmutable del producto |
| Nombre | Texto | Nombre utilizado en la búsqueda |
| Categoria_ID | Texto | Referencia a una categoría existente |
| Descripcion | Texto | Información descriptiva del producto |

**Reglas:**

- `Codigo_Producto` y `Nombre` son obligatorios.
- `Codigo_Producto` es único y no modificable después de su creación.
- `Categoria_ID` debe identificar una categoría válida.
- `Descripcion` puede estar vacía.
- Los códigos deben conservarse como texto para evitar pérdida de ceros iniciales.

#### Hoja 2 — Categorías

| Columna | Tipo lógico | Descripción |
|---|---|---|
| Categoria_ID | Texto | Identificador único de la categoría |
| Nombre_Categoria | Texto | Nombre descriptivo de la categoría |

**Reglas:**

- Cada categoría tendrá un identificador único.
- Los productos utilizarán `Categoria_ID` para relacionarse con esta hoja.
- En v0, las categorías se mantendrán predefinidas.

#### Hoja 3 — Ubicaciones

| Columna | Tipo lógico | Descripción |
|---|---|---|
| Ubicacion_ID | Texto | Identificador único de la ubicación |
| Rack | Texto | Rack o estantería |
| Columna | Texto | Columna física |
| Nivel | Texto | Nivel de la estantería |
| Posicion | Texto | Posición dentro del nivel |

**Reglas:**

- `Ubicacion_ID` debe ser único.
- La combinación `Rack + Columna + Nivel + Posicion` debe ser única.
- Las ubicaciones se mantendrán predefinidas durante v0.

#### Hoja 4 — Asignaciones

| Columna | Tipo lógico | Descripción |
|---|---|---|
| Codigo_Producto | Texto | Producto asociado |
| Ubicacion_ID | Texto | Ubicación física asociada |
| Principal | Texto | Identifica si es la ubicación principal: Sí o No |

**Reglas:**

- `Codigo_Producto` debe existir en Productos.
- `Ubicacion_ID` debe existir en Ubicaciones.
- No podrá repetirse una misma combinación de producto y ubicación.
- Cada producto tendrá como mínimo una ubicación.
- Cada producto tendrá exactamente una asignación marcada como principal.
- Las demás asignaciones se considerarán secundarias.
- Los valores del campo `Principal` se normalizarán al procesar el archivo, conservando únicamente dos estados lógicos: Sí y No.

### 3.4. Relaciones entre hojas

**Categorías → Productos**

Una categoría puede corresponder a varios productos. Cada producto referenciará una categoría válida.

**Productos → Asignaciones**

Un producto puede tener varias asignaciones de ubicación.

**Ubicaciones → Asignaciones**

Cada asignación deberá referenciar una ubicación registrada.

La hoja Asignaciones permitirá representar la relación entre productos y ubicaciones sin duplicar la información del producto.

### 3.5. Ejemplo demostrativo

**Productos**

| Codigo_Producto | Nombre | Categoria_ID | Descripcion |
|---|---|---|---|
| MAR001 | Martillo de uña | CAT01 | Martillo para carpintería |
| TOR001 | Tornillo galvanizado | CAT02 | Tornillo de uso general |

**Categorías**

| Categoria_ID | Nombre_Categoria |
|---|---|
| CAT01 | Herramientas |
| CAT02 | Tornillería |

**Ubicaciones**

| Ubicacion_ID | Rack | Columna | Nivel | Posicion |
|---|---|---|---|---|
| U001 | R01 | C01 | N02 | P03 |
| U002 | R02 | C03 | N01 | P02 |

**Asignaciones**

| Codigo_Producto | Ubicacion_ID | Principal |
|---|---|---|
| MAR001 | U001 | Sí |
| MAR001 | U002 | No |
| TOR001 | U002 | Sí |

Los datos anteriores son ficticios y solo ilustran la estructura aprobada.

No forman parte de un inventario real y no ordenan crear el archivo antes de la implementación.

---

## 4. La pieza de IA

### 4.1. Inteligencia artificial utilizada para el desarrollo

Gemini será el agente encargado de asistir en la construcción de FerreteríaMS.

Su trabajo se organizará mediante instrucciones y prompts relacionados con los requisitos aprobados.

Las tareas incluirán actividades de desarrollo, depuración, pruebas y documentación de resultados, bajo supervisión humana.

### 4.2. Inteligencia artificial dentro de FerreteríaMS v0

La versión v0 no incorporará una conexión funcional con Gemini API.

El área visual del asistente permanecerá identificada como «Próximamente».

Por tanto, v0 no deberá exigir una API key de Gemini para ejecutar la búsqueda o administrar el inventario.

### 4.3. Inteligencia artificial para la entrega final

La integración funcional de Gemini corresponde a `03_Especificaciones_Final.md`.

La futura integración permitirá:

- Información técnica sobre productos.
- Orientación sobre utilización, seguridad y almacenamiento.
- Asesoría interactiva sobre proyectos.
- Recomendaciones de herramientas y accesorios.
- Selección del idioma de respuesta.
- Priorización de los productos registrados en el inventario de la tienda.
- Advertencias sobre posibles errores de la inteligencia artificial.

Estas funcionalidades no deberán implementarse anticipadamente como parte de v0.

---

## 5. Flujo del usuario

### 5.1. Flujo del cliente

1. El cliente abre FerreteríaMS desde un navegador.
2. La aplicación presenta la pantalla pública principal.
3. El cliente introduce el nombre del producto.
4. Presiona Buscar.
5. La aplicación consulta el inventario registrado.
6. Se presentan los productos que coincidan con el término, priorizando aquellos cuyos nombres comienzan con él.
7. Se muestran hasta diez resultados por página.
8. El cliente selecciona el producto deseado.
9. La aplicación muestra su información y ubicación física.
10. Cuando corresponda, muestra las ubicaciones principal y secundarias.

Si no existen coincidencias, se mostrará el mensaje aprobado de producto no encontrado.

Si ocurre un error técnico, se informará del problema y se ofrecerá la posibilidad de reintentar.

### 5.2. Flujo del administrador

1. El administrador accede a FerreteríaMS desde la interfaz web para computadora.
2. Selecciona la pestaña Productos.
3. La aplicación presenta el acceso Login/Logout.
4. Introduce sus credenciales.
5. La aplicación verifica su autorización y las restricciones de seguridad.
6. Si la autenticación es correcta, se habilita la administración de productos.
7. El administrador crea o edita un producto.
8. Selecciona una categoría existente.
9. Selecciona una o varias ubicaciones existentes.
10. Identifica la ubicación principal.
11. Solicita guardar las modificaciones.
12. La aplicación valida los datos.
13. Se utiliza GitHub API para guardar la nueva versión del archivo maestro.
14. Se confirma el resultado únicamente después de verificar el guardado.
15. Las búsquedas públicas consultan posteriormente la información confirmada.

Si ocurre un conflicto de versiones o un fallo de conexión, la aplicación deberá proteger la información existente y comunicar el problema.

### 5.3. Flujo de seguridad administrativa

1. El administrador inicia sesión con sus credenciales.
2. Se aplican los controles de intentos fallidos y bloqueo temporal.
3. Durante una sesión válida, podrá administrar productos.
4. Después de trece minutos de inactividad se presentará una advertencia de próxima expiración.
5. El administrador podrá utilizar el botón «Continuar sesión» mientras la sesión siga siendo válida.
6. Al alcanzar quince minutos de inactividad, la sesión administrativa expirará.
7. Para continuar modificando el inventario, será necesario autenticarse nuevamente.
8. Si existían cambios sin guardar, se conservarán temporalmente durante quince minutos adicionales, según la política de seguridad aprobada.
9. Los cambios pendientes no se guardarán automáticamente ni se enviarán a GitHub sin una nueva confirmación válida.

### 5.4. Flujo desde celular

1. El cliente abre la aplicación desde el navegador móvil.
2. Se presenta una interfaz adaptable.
3. Puede buscar productos.
4. Puede consultar sus ubicaciones físicas.
5. No tendrá habilitada la administración del inventario.

La instalación como PWA no será un requisito de v0.

### 5.5. Flujo visual de Gemini

Durante v0, la sección Gemini se mostrará como una funcionalidad futura.

No permitirá iniciar conversaciones funcionales ni generar respuestas mediante Gemini API.

---

## 6. Restricciones

### 6.1. Presupuesto

El proyecto tendrá un presupuesto objetivo de servicios de $0.00 durante la prueba de concepto.

Se podrán utilizar herramientas gratuitas o servicios comerciales con niveles gratuitos adecuados.

Antes de activar los servicios se deberán comprobar las condiciones de uso, las cuotas y los límites correspondientes.

### 6.2. Tecnologías

La versión v0 utilizará las siguientes tecnologías principales:

- Python.
- Streamlit.
- pandas.
- Excel `.xlsx`.
- GitHub.
- GitHub API.
- Streamlit Community Cloud.

Las librerías complementarias deberán justificarse por las necesidades del proyecto.

Gemini API se reservará para la entrega final.

### 6.3. Seguridad

#### 6.3.1. Cuenta administrativa

Inicialmente existirá una única cuenta administrativa.

El acceso requerirá usuario y contraseña.

Las contraseñas deberán almacenarse mediante un mecanismo de hashing seguro, sin conservarlas en texto plano.

#### 6.3.2. Intentos fallidos

Después de cinco intentos fallidos consecutivos, se aplicará un bloqueo temporal.

Los bloqueos serán progresivos:

- Primer bloqueo: 5 minutos.
- Segundo bloqueo: 10 minutos.
- Tercer bloqueo: 20 minutos.
- Cuarto bloqueo y posteriores: 30 minutos.

La duración máxima de un bloqueo será de 30 minutos.

Después de una autenticación exitosa, se reiniciará el contador de intentos fallidos según la política aprobada.

#### 6.3.3. Sesiones administrativas

Las sesiones expirarán después de quince minutos de inactividad.

Se mostrará una advertencia dos minutos antes de la expiración.

La interfaz ofrecerá el botón «Continuar sesión» para renovar una sesión todavía válida.

Cuando expire, será necesario autenticarse nuevamente.

#### 6.3.4. Modificaciones no guardadas

Cuando la sesión expire mientras existan modificaciones pendientes, estas se conservarán temporalmente durante quince minutos adicionales.

La información pendiente solo podrá recuperarse tras una nueva autenticación válida.

La conservación temporal no representará un guardado confirmado en GitHub.

Una vez transcurrido ese plazo, la aplicación no estará obligada a conservar el borrador pendiente.

#### 6.3.5. Recuperación de credenciales

La recuperación de contraseña se realizará mediante un procedimiento administrativo seguro, externo a la interfaz pública.

No se incorporará un sistema público de recuperación de cuentas durante v0.

#### 6.3.6. Autorización y secretos

- Las operaciones administrativas requerirán autorización válida.
- La interfaz móvil no permitirá la modificación del inventario.
- La restricción de acceso administrativo no dependerá exclusivamente de ocultar elementos visuales.
- Las credenciales y tokens de GitHub deberán permanecer protegidos en el servidor.
- Los secretos no deberán exponerse al navegador ni incluirse directamente en el código fuente.
- Se utilizarán permisos mínimos necesarios para el acceso autorizado al archivo maestro.

### 6.4. Compatibilidad con dispositivos

La aplicación v0 será una aplicación web responsive.

Permitirá consultar productos desde navegadores compatibles en computadoras y celulares, utilizando conexión a internet.

La modificación administrativa del inventario estará restringida a la versión web para computadora.

**La instalación como Progressive Web App (PWA) se traslada a Mejoras Futuras**, conforme a la decisión de alcance aprobada posteriormente al documento de concepto.

En v0 no serán obligatorios:

- Instalación de la aplicación en el dispositivo.
- Funcionamiento sin conexión.
- Sincronización offline.
- Almacenamiento local permanente del inventario para búsquedas sin conexión.

Esta actualización no modifica físicamente el documento de concepto aprobado.

### 6.5. Restricciones del inventario

La versión v0 no administrará:

- Cantidades o existencias físicas.
- Precios.
- Carritos de compra.
- Transacciones comerciales.

La aplicación utilizará el inventario para identificar productos y sus ubicaciones.

No se mostrará información que haga parecer que FerreteríaMS es una tienda de venta en línea.

### 6.6. Integridad y persistencia

La aplicación deberá evitar guardar información inconsistente.

Las operaciones confirmadas deberán conservarse en GitHub.

Los errores y conflictos de versiones no deberán provocar sobrescrituras silenciosas.

El archivo deberá mantener las cuatro hojas aprobadas y sus relaciones después de cada modificación administrativa.

### 6.7. Estructura documental

El proyecto conservará la organización establecida en el concepto aprobado, incluyendo:

- `01_Documentacion/`
- `02_Prompts/`
- `03_Aplicacion/`
- `04_Pruebas/`
- `05_Resultados/`

Dentro de `01_Documentacion/`, la nomenclatura posterior aprobada será:

- `01_Concepto.md`
- `02_Especificaciones_v0.md`
- `03_Especificaciones_Final.md`

Los archivos `GEMINI.md`, `AGENTS.md`, `README.md`, `requirements.txt` y `.gitignore` conservarán sus nombres técnicos.

### 6.8. Calidad del software

El desarrollo deberá poder verificarse mediante pruebas y conservar trazabilidad entre requisitos, instrucciones, cambios y resultados.

Las imágenes conceptuales del documento aprobado servirán como guía visual.

El comportamiento funcional expresamente definido en el concepto y las decisiones posteriores aprobadas tendrán prioridad sobre cualquier detalle ilustrativo que no esté especificado.

---

## 7. Criterios de aceptación

### 7.1. Definición de Criterio de Aceptación (CA)

**CA significa Criterio de Aceptación.**

Un Criterio de Aceptación establece una condición verificable que debe cumplirse para considerar que una funcionalidad ha sido implementada correctamente.

Cada criterio se identifica mediante un código único y, cuando corresponda, se relaciona con uno o varios requisitos funcionales.

Ejemplo:

**CA-001 — Buscar un producto registrado:** al buscar un producto existente, la aplicación debe mostrarlo entre los resultados.

La relación entre ambos conceptos es:

- **RF:** define qué debe hacer la aplicación.
- **CA:** define cómo comprobar que lo hace correctamente.

Los códigos permitirán relacionar requisitos, pruebas, resultados y evidencias de implementación.

### 7.2. Búsqueda pública

| ID | RF relacionado | Prueba | Resultado esperado |
|---|---|---|---|
| CA-001 | RF-001, RF-004 | Buscar un producto registrado | Aparece entre las coincidencias |
| CA-002 | RF-002 | Buscar utilizando parte del nombre | Se encuentran coincidencias parciales |
| CA-003 | RF-003 | Utilizar mayúsculas o minúsculas diferentes | Se obtienen resultados equivalentes |
| CA-004 | RF-003 | Utilizar términos con o sin acentos | La búsqueda ignora la diferencia de acentuación |
| CA-005 | RF-007 | Consultar un producto con varias ubicaciones | Se muestran ubicaciones principal y secundarias |
| CA-006 | RF-008 | Buscar un producto no registrado | Se muestra el mensaje de ausencia del inventario |
| CA-007 | RF-009 | Buscar sin iniciar sesión | La búsqueda pública funciona |
| CA-008 | RF-010 | Consultar desde celular | La interfaz permite buscar y ver ubicaciones |
| CA-039 | RF-035 | Buscar productos con coincidencias al inicio y en el interior del nombre | Aparecen primero los que comienzan con el término |
| CA-040 | RF-036 | Buscar un término con más de diez resultados | Se muestran hasta diez resultados por página y funciona la navegación |
| CA-041 | RF-037 | Presionar Buscar sin introducir texto | La aplicación solicita introducir un nombre |
| CA-042 | RF-038 | Simular un fallo de conexión al consultar | Se presenta un error diferenciable de una búsqueda sin resultados y se permite reintentar |
| CA-043 | RF-001 | Intentar buscar por una opción de marca o categoría | No existen controles independientes de búsqueda por marca o categoría |

### 7.3. Administración

| ID | RF relacionado | Prueba | Resultado esperado |
|---|---|---|---|
| CA-009 | RF-011, RF-012 | Acceder a Productos sin autenticación | Se presenta Login/Logout antes de permitir modificaciones |
| CA-010 | RF-011 | Introducir credenciales válidas | Se autoriza el acceso |
| CA-011 | RF-011 | Introducir credenciales incorrectas | No se autoriza el acceso |
| CA-012 | RF-014 | Crear un producto con datos válidos | El producto se guarda correctamente |
| CA-013 | RF-015 | Editar un producto existente | Los cambios autorizados se conservan |
| CA-014 | RF-020 | Intentar utilizar un código duplicado | Se rechaza el guardado |
| CA-015 | RF-017 | Asignar una ubicación existente | Se registra la asociación |
| CA-016 | RF-017 | Asignar varias ubicaciones | Se conservan las relaciones válidas |
| CA-017 | RF-019 | Identificar una ubicación principal | El producto conserva exactamente una principal |
| CA-018 | RF-020 | Intentar guardar datos inválidos | Se impide guardar información inconsistente |
| CA-019 | RF-013 | Intentar administrar desde la interfaz móvil | No se habilita la modificación del inventario |
| CA-044 | RF-015 | Intentar modificar el código de un producto existente | El código permanece inmutable |
| CA-045 | RF-018, RF-019 | Intentar retirar la única ubicación de un producto | La operación se rechaza |
| CA-046 | RF-020 | Intentar asignar dos ubicaciones principales | La aplicación impide conservar dos principales |

### 7.4. Inventario y GitHub

| ID | RF relacionado | Prueba | Resultado esperado |
|---|---|---|---|
| CA-020 | RF-029 | No existe `inventario.xlsx` | La aplicación puede crear el archivo inicial de ejemplo |
| CA-021 | RF-030 | Ya existe `inventario.xlsx` | No se sobrescribe automáticamente |
| CA-022 | RF-023 | Leer el inventario | Se reconocen las cuatro hojas y sus columnas |
| CA-023 | RF-026 | Guardar una modificación | GitHub conserva el archivo actualizado |
| CA-024 | RF-028 | Consultar después de guardar | La búsqueda muestra los cambios confirmados sin reiniciar Streamlit |
| CA-025 | RF-027 | Detectar conflicto de versiones | Se evita sobrescribir silenciosamente |
| CA-026 | RF-026 | Ocurre un error de conexión durante el guardado | Se muestra un mensaje comprensible sin declarar éxito no confirmado |
| CA-047 | RF-020, RF-023 | Registrar un producto con categoría inexistente | Se rechaza el registro |
| CA-048 | RF-017, RF-023 | Registrar asignación con ubicación inexistente | Se rechaza la asociación |
| CA-049 | RF-023 | Duplicar una combinación Rack, Columna, Nivel y Posicion | La estructura se identifica como inválida |
| CA-050 | RF-023 | Duplicar una relación producto-ubicación | Se rechaza o se detecta la duplicación |
| CA-051 | RF-023 | Guardar cambios en Productos o Asignaciones | El archivo conserva sus cuatro hojas y la integridad de sus relaciones |

### 7.5. Seguridad

| ID | Prueba | Resultado esperado |
|---|---|---|
| CA-027 | Intentar modificar sin autorización | Operación denegada |
| CA-028 | Verificar exposición de secretos en la interfaz | No se muestran tokens o contraseñas |
| CA-029 | Verificar secretos en código y documentación pública | No existen credenciales publicadas |
| CA-030 | Probar controles administrativos de sesión | Se aplican las restricciones documentadas |
| CA-052 | Introducir cinco credenciales incorrectas consecutivas | Se aplica el bloqueo correspondiente |
| CA-053 | Repetir ciclos de fallos sujetos a bloqueo | Se respetan los períodos de 5, 10, 20 y 30 minutos |
| CA-054 | Mantener una sesión inactiva durante trece minutos | Se muestra una advertencia de expiración |
| CA-055 | Mantener una sesión inactiva durante quince minutos | La sesión expira y exige nueva autenticación |
| CA-056 | Seleccionar «Continuar sesión» mientras sigue vigente | Se renueva la sesión conforme a la política |
| CA-057 | Dejar expirar una sesión con cambios sin guardar | El borrador permanece recuperable durante el período temporal aprobado, tras reautenticación |
| CA-058 | Intentar modificar inventario desde una solicitud móvil no autorizada | La modificación es rechazada, aunque se intente eludir la interfaz |
| CA-059 | Inspeccionar configuración de credenciales | Las contraseñas no están almacenadas en texto plano |

### 7.6. Interfaz Gemini v0

| ID | RF relacionado | Prueba | Resultado esperado |
|---|---|---|---|
| CA-031 | RF-032, RF-033 | Abrir el área destinada a Gemini | Aparece identificada como «Próximamente» |
| CA-032 | RF-034 | Ejecutar FerreteríaMS v0 sin Gemini API key | La búsqueda y administración continúan funcionando |
| CA-033 | RF-034 | Comprobar llamadas funcionales a Gemini | La versión v0 no realiza llamadas operativas |

### 7.7. Despliegue y compatibilidad

| ID | Prueba | Resultado esperado |
|---|---|---|
| CA-034 | Ejecutar FerreteríaMS localmente | Se inicia la aplicación |
| CA-035 | Desplegar en Streamlit Community Cloud | La interfaz pública resulta accesible |
| CA-036 | Buscar productos en la aplicación desplegada | Se consultan correctamente los datos de GitHub |
| CA-037 | Guardar modificaciones autorizadas desde la aplicación desplegada | Los cambios confirmados persisten |
| CA-038 | Reiniciar la aplicación | El inventario confirmado permanece disponible en GitHub |
| CA-060 | Abrir la aplicación en un navegador móvil | La búsqueda y localización funcionan sin instalar una PWA |
| CA-061 | Ejecutar las funcionalidades principales sin mecanismos de instalación PWA | La aplicación funciona normalmente con conexión a internet |

### 7.8. Evidencia del SDLC

Para considerar completada la etapa v0, deberán conservarse evidencias de:

- Requisitos aprobados.
- Prompts enviados a Gemini.
- Archivos desarrollados o modificados.
- Pruebas realizadas.
- Resultados obtenidos.
- Errores y correcciones.
- Cambios registrados en GitHub.
- Despliegue y verificación de la aplicación.

---

## 8. Fuera de alcance (por ahora)

### 8.1. Funcionalidades reservadas para la entrega final

La versión v0 no incorporará Gemini funcionalmente.

Las siguientes capacidades estarán reservadas para la entrega final:

- Información técnica generada mediante Gemini.
- Asesoría interactiva sobre proyectos.
- Recomendaciones de herramientas y accesorios mediante IA.
- Selección del idioma de las respuestas de Gemini.
- Conversaciones con preguntas de seguimiento.
- Priorización del inventario de la ferretería por parte de Gemini.

Estas funcionalidades se desarrollarán en `03_Especificaciones_Final.md`.

### 8.2. Mejoras Futuras

La sección «Mejoras Futuras» del concepto aprobado identifica como ampliaciones opcionales:

- Nuevas modalidades de búsqueda.
- Mejoras adicionales de interfaz y administración.

Por decisión posterior de alcance, también se traslada a Mejoras Futuras:

- Instalación como Progressive Web App (PWA).

La futura implementación de PWA deberá evaluar, cuando corresponda, los requisitos de instalación, manifiesto y compatibilidad con los navegadores y la plataforma de despliegue.

El funcionamiento offline no queda aprobado como requisito.

### 8.3. Exclusiones generales

FerreteríaMS v0 no será un sistema comercial de ventas ni de control de existencias.

No incorporará:

- Control de cantidades.
- Precios.
- Carritos de compra.
- Facturación.
- Transacciones comerciales.
- Administración de categorías o ubicaciones desde la aplicación.
- Búsqueda pública independiente por marca o categoría.

---

## 9. Despliegue

### 9.1. Entorno de desarrollo

El proyecto será desarrollado utilizando Python y herramientas de desarrollo asistido por Gemini.

El código se almacenará y versionará mediante GitHub.

### 9.2. Plataforma

La aplicación utilizará Streamlit y estará desplegada en Streamlit Community Cloud.

La versión v0 será una aplicación web responsive que funcionará desde navegadores compatibles.

No requerirá instalación como PWA.

### 9.3. Archivo principal

El punto principal de ejecución será:

`03_Aplicacion/app.py`

La organización de carpetas y archivos seguirá la estructura aprobada en el documento de concepto y las actualizaciones documentales posteriores autorizadas.

### 9.4. Dependencias

Las dependencias Python se declararán en el archivo `requirements.txt` ubicado en la raíz del repositorio.

Se incluirán únicamente las necesarias para la versión que se esté construyendo.

La biblioteca `google-genai` no será necesaria para el funcionamiento de v0, porque la integración real de Gemini corresponde a la entrega final.

### 9.5. Inventario

El archivo maestro será:

`03_Aplicacion/inventario.xlsx`

Su contenido estará versionado en GitHub y será consultado y actualizado mediante los mecanismos aprobados.

Se utilizarán las cuatro hojas y los nombres de columnas definidos en la sección 3.

El inventario inicial de demostración solamente podrá generarse cuando el archivo maestro no exista todavía en GitHub.

Una vez creado, los reinicios y nuevos despliegues no deberán reemplazarlo automáticamente.

### 9.6. Secretos y credenciales

Las credenciales utilizadas para acceder a GitHub deberán mantenerse fuera del código fuente y de la interfaz pública.

Durante el despliegue se configurarán mediante mecanismos seguros compatibles con Streamlit Community Cloud.

Las credenciales del administrador también deberán protegerse según la política de seguridad aprobada.

### 9.7. Verificación del despliegue

Después de publicar la aplicación se comprobará:

- Acceso público desde navegador.
- Búsqueda por nombre, normalización y coincidencias parciales.
- Orden por relevancia y paginación.
- Consulta de ubicaciones físicas.
- Diseño responsive desde celular.
- Funcionamiento de la administración autorizada desde computadora.
- Controles de autenticación, bloqueo y sesión.
- Lectura y escritura del inventario en GitHub.
- Protección contra conflictos de versiones.
- Persistencia después de reinicios.
- Manejo adecuado de errores.
- Presentación de Gemini como «Próximamente».
- Funcionamiento sin requerir instalación PWA.

### 9.8. Desarrollo incremental

La construcción de FerreteríaMS se realizará mediante tareas pequeñas y verificables.

Gemini deberá seguir los documentos e instrucciones aprobados y conservar evidencia de su trabajo.

Cada tarea deberá indicar los requisitos afectados, sus criterios de aceptación y las pruebas ejecutadas.

La implementación de v0 se considerará completada solamente después de realizar las comprobaciones correspondientes.