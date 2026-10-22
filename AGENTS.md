# AGENTS: FerreteríaMS

**Documento:** `AGENTS.md`
**Etapa activa:** FerreteríaMS — Versión Final
**Agente de desarrollo:** Gemini (Antigravity)

---

## 1. Qué es este proyecto

FerreteríaMS es una aplicación web que permite a los clientes de una ferretería buscar productos por nombre y consultar su ubicación física dentro de la tienda.

La ubicación se expresa mediante rack o estantería, columna, nivel y posición.

La base desarrollada en **FerreteríaMS v0** ya incorpora:

- Búsqueda pública de productos.
- Consulta de ubicación principal y ubicaciones secundarias.
- Administración básica del inventario mediante acceso protegido.
- Almacenamiento persistente de los datos en un archivo Excel versionado en GitHub.

La etapa activa, **FerreteríaMS — Versión Final**, amplía exclusivamente las funcionalidades incrementales aprobadas en `01_Documentacion/03_Especificaciones_Final.md`, organizadas en dos bloques:

1. **Bloque 1:** Administración de categorías, ubicaciones y estados de productos (activo/inactivo).
2. **Bloque 2:** Integración de Gemini con el inventario como asistente de texto bilingüe, contextual, seguro y acotado en consumo.

FerreteríaMS no incorpora ventas, precios, cantidades, control de existencias, carritos de compra ni transacciones comerciales.

**Gemini tiene dos funciones distintas en este proyecto:**

1. Actuar como agente de programación durante el desarrollo (Gemini / Antigravity).
2. Integrarse en el **Bloque 2** de la versión final como asistente funcional dentro de la aplicación, siguiendo estrictamente `01_Documentacion/03_Especificaciones_Final.md`.

### Documentos de referencia

Antes de desarrollar cualquier funcionalidad, el agente deberá consultar:

1. `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`: concepto general aprobado del proyecto.
2. `01_Documentacion/02_Especificaciones_v0.md`: requisitos (`RF`) y criterios de aceptación (`CA`) vigentes de las funcionalidades ya desarrolladas en v0.
3. `01_Documentacion/03_Especificaciones_Final.md`: requisitos incrementales (`RF-F`), criterios de aceptación (`CA-F`), restricciones y alcance aprobados para la versión final.
4. `AGENTS.md`: reglas permanentes del agente.
5. El prompt correspondiente a la tarea solicitada.

Las decisiones posteriores aprobadas y documentadas deberán respetarse sin modificar silenciosamente los documentos originales.

Si existen contradicciones, dudas o requisitos insuficientemente definidos, el agente deberá identificarlos y solicitar aclaración antes de ejecutar cambios que puedan afectar el alcance.

---

## 2. Cómo está hecho

### 2.1. Tecnologías principales

FerreteríaMS utilizará:

- **Python:** lenguaje principal.
- **Streamlit:** interfaz web.
- **pandas:** lectura, procesamiento y consulta del inventario.
- **Excel `.xlsx`:** almacenamiento estructurado del inventario.
- **GitHub:** repositorio y control de versiones.
- **GitHub API:** actualización del archivo maestro.
- **Streamlit Community Cloud:** plataforma de despliegue.
- **Gemini API:** asistente de texto desde el servidor Python en el Bloque 2, utilizando una librería compatible y clave en Streamlit Secrets, previa verificación de condiciones de uso gratuito y sin activar recursos de pago sin autorización.

Se podrán incorporar librerías complementarias cuando sean necesarias, gratuitas y compatibles con el alcance aprobado.

Toda dependencia añadida deberá quedar registrada en `requirements.txt`.

### 2.2. Organización del proyecto

La estructura documental y de desarrollo será:

```text
FerreteriaMS/
├── 01_Documentacion/
│   ├── 01_Concepto_FerreteriaMS_Final.docx
│   ├── 02_Especificaciones_v0.md
│   └── 03_Especificaciones_Final.md
├── 02_Prompts/
├── 03_Aplicacion/
│   ├── app.py
│   └── inventario.xlsx
├── 04_Pruebas/
├── 05_Resultados/
├── GEMINI.md
├── AGENTS.md
├── README.md
├── requirements.txt
└── .gitignore
```

La estructura indica la ubicación prevista de los archivos, no autoriza crear todos ellos anticipadamente.

El archivo `inventario.xlsx` solo podrá generarse automáticamente si el archivo maestro todavía no existe en GitHub. El inventario ficticio de evaluación de 200 productos (cuando se autorice su fase de pruebas) se preparará por separado y no deberá publicarse automáticamente en la ruta maestra de producción.

### 2.3. Inventario

El archivo maestro `inventario.xlsx` contendrá exactamente cuatro hojas oficiales:

**Productos:** `Codigo_Producto`, `Nombre`, `Categoria_ID`, `Descripcion` (y el campo lógico `Activo` en la versión final).

**Categorías:** `Categoria_ID`, `Nombre_Categoria` (sin campo `Activo`, cuya desactivación está pospuesta).

**Ubicaciones:** `Ubicacion_ID`, `Rack`, `Columna`, `Nivel`, `Posicion` (y el campo lógico `Activo` en la versión final).

**Asignaciones:** `Codigo_Producto`, `Ubicacion_ID`, `Principal`.

El agente deberá respetar los nombres de columnas, las relaciones y las validaciones definidas en la sección 3 de `02_Especificaciones_v0.md` y en la sección 3.4 de `03_Especificaciones_Final.md`, garantizando compatibilidad retroactiva con el archivo v0 (los registros previos sin estado explícito se interpretarán como activos).

El inventario no registrará precios, cantidades ni existencias físicas.

### 2.4. Persistencia

GitHub será la fuente persistente del inventario.

La aplicación deberá:

- Leer la versión vigente del archivo maestro.
- Guardar las modificaciones autorizadas mediante GitHub API.
- Detectar conflictos de versiones.
- Evitar sobrescrituras silenciosas.
- Conservar las cuatro hojas y la integridad de sus relaciones.
- Permitir consultar los cambios confirmados sin reiniciar manualmente Streamlit.

---

## 3. Reglas

### 3.1. Respetar el alcance aprobado

El agente deberá implementar únicamente las funcionalidades incluidas en la etapa autorizada, limitándose al alcance incremental aprobado en `01_Documentacion/03_Especificaciones_Final.md`.

La implementación de la versión final se organizará en dos bloques secuenciales:

1. **Bloque 1:** Administración de categorías, ubicaciones y estados de productos.
2. **Bloque 2:** Integración de Gemini con el inventario.

Las funcionalidades ya terminadas y aprobadas en v0 no deberán reconstruirse, refactorizarse ni modificarse sin necesidad técnica justificada.

Las funcionalidades pospuestas o descartadas en `01_Documentacion/03_Especificaciones_Final.md` (desactivación de categorías, eliminación definitiva de productos, fusión automática de conflictos en GitHub, auditoría detallada en la aplicación, configuración administrativa de nombre/logotipo, y capacidades de voz o imágenes en Gemini) quedan fuera del alcance de esta entrega y no deberán implementarse.

No deberá agregar funcionalidades nuevas por iniciativa propia, aunque considere que podrían mejorar la aplicación.

Cuando identifique una mejora, podrá recomendarla, explicando su utilidad, pero deberá esperar autorización antes de implementarla.

### 3.2. Seguir los requisitos y criterios de aceptación

Cada tarea deberá identificar, cuando corresponda:

- Requisitos funcionales afectados, identificados mediante códigos `RF` (v0) y `RF-F` (versión final).
- Criterios de aceptación correspondientes, identificados mediante códigos `CA` (v0) y `CA-F` (versión final).
- Archivos que será necesario crear o modificar.
- Pruebas focalizadas necesarias para verificar el resultado.

El agente no deberá sustituir un requisito aprobado por una interpretación propia.

### 3.3. Realizar cambios pequeños y verificables

El desarrollo se dividirá en tareas organizadas y secuenciales dentro del bloque autorizado.

Cada tarea deberá tener un objetivo definido.

El agente deberá evitar modificaciones innecesarias en archivos o funcionalidades estables de v0 que no estén relacionados con la tarea.

Al finalizar deberá explicar qué cambió, por qué y cómo verificó el resultado.

### 3.4. Proteger las credenciales y los secretos

Las contraseñas, API keys y tokens deberán permanecer protegidos.

Está prohibido incluir secretos reales en:

- Código fuente.
- Archivos versionados.
- Documentación pública.
- Prompts.
- Resultados y registros de pruebas.

Deberán utilizarse mecanismos seguros de configuración, como los Secrets de Streamlit cuando corresponda (incluyendo la clave de Gemini API desde el servidor).

Las contraseñas administrativas deberán protegerse mediante hashing seguro.

Los tokens de GitHub tendrán únicamente los permisos necesarios.

### 3.5. Preservar la seguridad administrativa

El agente deberá implementar y conservar los controles definidos en `02_Especificaciones_v0.md`, incluyendo:

- Una cuenta administrativa inicial.
- Cinco intentos fallidos consecutivos antes de aplicar bloqueo.
- Bloqueos progresivos de 5, 10, 20 y 30 minutos.
- Expiración de sesión después de quince minutos de inactividad.
- Advertencia dos minutos antes de la expiración.
- Renovación mediante «Continuar sesión».
- Protección temporal de cambios no guardados y reautenticación.
- Restricción de la administración a la interfaz web para computadora.

No deberá depender exclusivamente de ocultar botones o pestañas para impedir operaciones no autorizadas. El asistente Gemini operará exclusivamente en modo lectura sobre el inventario activo y nunca ejecutará funciones administrativas.

### 3.6. Preservar los datos

Antes de modificar el inventario, el agente deberá comprobar las reglas de integridad aplicables.

No podrá eliminar o sobrescribir información confirmada sin que la operación esté autorizada.

Las modificaciones administrativas deberán conservar correctamente los datos existentes que no hayan sido objeto del cambio.

Si ocurre un conflicto de versiones, no deberá sobrescribir silenciosamente el archivo maestro.

### 3.7. Mantener una interfaz sencilla

La interfaz deberá seguir las imágenes conceptuales aprobadas, respetando los requisitos funcionales.

El cliente podrá buscar exclusivamente por nombre de producto y, en el Bloque 2, realizar consultas de texto en la sección Gemini.

La interfaz no deberá presentar FerreteríaMS como una tienda de venta en línea.

No deberá incorporar carritos de compra, precios, cantidades ni controles comerciales.

La interfaz pública deberá funcionar en computadora y celular.

La instalación PWA no es un requisito de esta entrega.

### 3.8. Manejar los errores

Las operaciones que puedan fallar deberán incorporar mecanismos apropiados de manejo de errores.

Los mensajes deberán ser comprensibles para el usuario.

Un fallo de conexión o lectura no deberá mostrarse como una búsqueda sin resultados. Los errores, agotamiento de cuota o ausencia de clave en Gemini API no deberán interrumpir el funcionamiento del buscador público.

Un guardado no deberá declararse exitoso antes de confirmarse.

### 3.9. Mantener las dependencias

Cuando se añada o modifique una dependencia Python, deberá actualizarse `requirements.txt`.

No deberán añadirse librerías innecesarias.

Las dependencias deberán ser compatibles con las condiciones económicas y tecnológicas aprobadas.

### 3.10. Trazabilidad obligatoria

El desarrollo deberá permitir identificar cada tarea desde el prompt que la originó hasta su resultado.

Para cada tarea se registrará, como mínimo:

- Identificador de la tarea.
- Fecha de ejecución.
- Título de la tarea.
- Prompt o solicitud original.
- Interpretación del agente.
- Acciones realizadas.
- Archivos creados o modificados.
- Requisitos RF / RF-F relacionados.
- Criterios CA / CA-F relacionados.
- Pruebas ejecutadas y resultados.
- Errores, limitaciones o asuntos pendientes.
- Referencia al commit, cuando exista.

El prompt original deberá conservarse sin alteraciones.

La interpretación del agente y las acciones realizadas deberán registrarse por separado.

### 3.11. Organización de prompts y resultados

Los prompts de desarrollo estarán organizados en `02_Prompts/`, utilizando numeración consecutiva.

Las pruebas y verificaciones estarán organizadas en `04_Pruebas/`.

Los informes, resultados y evidencias del agente estarán organizados en `05_Resultados/`.

Los nombres de archivos podrán utilizar el formato `NN_Nombre` siempre que no interfiera con requisitos técnicos.

El agente no deberá alterar la estructura de carpetas aprobada sin autorización.

### 3.12. Control de cambios

Las modificaciones a requisitos, arquitectura, almacenamiento, seguridad o alcance necesitarán aprobación previa.

El agente podrá identificar problemas y proponer soluciones alternativas, pero no decidir unilateralmente cambios funcionales importantes.

El documento de concepto y las especificaciones aprobadas no deberán modificarse automáticamente durante la programación.

### 3.13. Control de versiones y autorización

Los cambios de código deberán gestionarse mediante GitHub.

Antes de realizar acciones que registren, publiquen o integren cambios, como `commit`, `push`, `merge` o despliegue, el agente deberá contar con la autorización correspondiente.

No deberá realizar operaciones destructivas sobre el repositorio o el inventario sin autorización expresa.

---

## 4. Cómo comprobar que funciona

### 4.1. Verificación general

Antes de declarar una tarea terminada, el agente deberá ejecutar **pruebas focalizadas sobre las funcionalidades nuevas o directamente afectadas** (evitando repetir innecesariamente suites de v0 sobre módulos no intervenidos) y verificar que:

1. El código correspondiente puede ejecutarse o, si no es posible, explicar el impedimento.
2. El resultado cumple los `RF`/`RF-F` y `CA`/`CA-F` aplicables.
3. No se introdujeron cambios fuera de alcance.
4. No se afectaron ni reconstruyeron funcionalidades previamente aprobadas en v0.
5. No se expusieron credenciales ni secretos.
6. Se actualizaron las dependencias, cuando corresponda.
7. Quedó registrada la evidencia de lo realizado.

### 4.2. Ejecución local

La aplicación Streamlit tendrá como archivo principal:

`03_Aplicacion/app.py`

La ejecución local deberá verificarse con el entorno Python y las dependencias correspondientes.

Como referencia, desde la raíz del proyecto:

```bash
python -m pip install -r requirements.txt
streamlit run 03_Aplicacion/app.py
```

Estos comandos se utilizarán cuando la aplicación y las dependencias hayan sido creadas y configuradas.

### 4.3. Pruebas de búsqueda

El agente deberá preservar y comprobar, cuando la tarea afecte la búsqueda:

- Búsqueda por nombre completo y parcial.
- Coincidencias sin distinción de acentos y mayúsculas.
- Orden por relevancia y diez resultados por página.
- Consulta de ubicación principal y secundarias.
- Exclusión de productos desactivados (`Activo` inactivo) de la búsqueda pública.
- Búsqueda sin coincidencias, búsqueda vacía y error de conexión con opción de reintentar.

### 4.4. Pruebas administrativas

El agente deberá comprobar de forma focalizada en las tareas correspondientes:

- Controles de autenticación, bloqueos progresivos, expiración/renovación de sesión, recuperación temporal de borradores y restricción móvil definidos en v0.
- Creación y edición de productos e inmutabilidad de códigos e identificadores existentes (`Codigo_Producto`, `Categoria_ID`, `Ubicacion_ID`).
- Creación y renombrado de categorías, rechazando duplicados normalizados (`CA-F-001` a `CA-F-003`).
- Creación de ubicaciones, rechazo de combinaciones físicas duplicadas, y edición o desactivación únicamente de ubicaciones sin productos asociados (`CA-F-004` a `CA-F-006`).
- Desactivación y reactivación de productos preservando sus datos, asignaciones y reglas de integridad (`CA-F-007`).

### 4.5. Pruebas de inventario y persistencia

El agente deberá comprobar:

- Lectura, migración compatible y preservación de las cuatro hojas Excel (`CA-F-008`, `CA-F-009`).
- Validez de las relaciones entre hojas, unicidad de códigos/combinaciones físicas y mantenimiento de exactamente una ubicación principal activa por producto activo.
- Protección del inventario maestro existente y prohibición de publicar automáticamente el inventario ficticio de evaluación (200 productos).
- Guardado mediante GitHub API, control de concurrencia SHA, detección de conflictos y actualización de consultas sin reiniciar Streamlit.

### 4.6. Pruebas de la sección Gemini (Bloque 2)

Durante el desarrollo y verificación del Bloque 2 se comprobará de forma focalizada que:

- El chat acepte consultas de texto sobre ferretería, mantenga seguimiento temporal de sesión y responda en español o inglés según la consulta (`CA-F-010`).
- Utilice productos activos pertinentes del catálogo (citando código, nombre y ubicación solo cuando estén confirmados) y distinga explícitamente recomendaciones generales no confirmadas (`CA-F-011`).
- Actualice el contexto al cambiar de producto seleccionado sin mezclar datos (`CA-F-012`).
- El botón «Nueva conversación» limpie el historial sin reiniciar el contador de uso de la ventana (`CA-F-013`).
- Aplique límites de consultas, longitud y contexto por sesión sin afectar el buscador público (`CA-F-014`).
- Muestre el aviso fijo de IA, redirija cortésmente consultas ajenas a ferretería y comunique precauciones ante riesgos técnicos (`CA-F-015`, `CA-F-016`).
- Maneje de forma segura la ausencia de API key, fallos de red o agotamiento de cuota sin interrumpir la búsqueda (`CA-F-017`).
- Obtenga la clave exclusivamente desde el servidor/Secrets, sin exponerla, y verifique previamente las condiciones de capa gratuita sin activar facturación (`CA-F-018`, `CA-F-019`).

### 4.7. Evidencia de resultados

El agente deberá registrar:

- Pruebas ejecutadas.
- Resultados obtenidos.
- Criterios `CA` / `CA-F` que se han comprobado.
- Pruebas pendientes o no ejecutadas.
- Errores encontrados.
- Correcciones realizadas.
- Limitaciones conocidas.

No deberá afirmar que una prueba fue ejecutada correctamente si no existe evidencia de su ejecución.

La aprobación final de una funcionalidad corresponderá a la revisión humana de los resultados.

---

## 5. Qué no hacer

Gemini y cualquier otro agente que participe en el desarrollo de FerreteríaMS deberán respetar las siguientes prohibiciones:

1. No modificar el concepto ni las especificaciones aprobadas (`02_Especificaciones_v0.md` y `03_Especificaciones_Final.md`) sin autorización.
2. No reconstruir ni modificar sin necesidad técnica las funcionalidades ya terminadas en v0.
3. No implementar funcionalidades pospuestas o descartadas en `03_Especificaciones_Final.md` (desactivación de categorías, eliminación definitiva de productos, fusión automática de conflictos GitHub, auditoría detallada en la aplicación, configuración de nombre/logotipo, ni voz o imágenes en Gemini).
4. No agregar ventas, facturación, precios, cantidades, carritos de compra ni control de existencias.
5. No introducir búsqueda pública independiente por marca o categoría.
6. No agregar administración móvil del inventario ni permitir que Gemini ejecute modificaciones administrativas.
7. No implementar instalación PWA ni activar servicios o planes de pago sin autorización expresa.
8. No modificar la arquitectura aprobada ni añadir bases de datos o backends adicionales sin solicitar autorización.
9. No sobrescribir ni recrear automáticamente un inventario que ya exista en GitHub, ni publicar el inventario ficticio de evaluación en la ruta maestra oficial.
10. No modificar identificadores únicos existentes (`Codigo_Producto`, `Categoria_ID`, `Ubicacion_ID`).
11. No permitir que un producto activo conserve ubicaciones inválidas/inactivas o más de una ubicación principal, ni editar físicamente o desactivar ubicaciones con productos asociados.
12. No almacenar contraseñas en texto plano ni publicar secretos o claves de API.
13. No eliminar archivos, datos o documentación aprobada sin autorización.
14. No realizar `commit`, `push`, `merge`, despliegues ni operaciones destructivas sin autorización.
15. No afirmar que las pruebas pasaron cuando no fueron ejecutadas.
16. No modificar archivos ajenos a una tarea sin necesidad justificada.
17. No ocultar errores, conflictos de versiones ni limitaciones técnicas.
18. No añadir complejidad innecesaria o funcionalidades que no correspondan al bloque autorizado.

Si una instrucción recibida contradice las restricciones del proyecto, el agente deberá detener la operación afectada, explicar la contradicción y solicitar una decisión antes de continuar.