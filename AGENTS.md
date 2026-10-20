# AGENTS: FerreteríaMS

**Documento:** `AGENTS.md` 
**Etapa activa:** FerreteríaMS v0  
**Agente de desarrollo:** Gemini

---

## 1. Qué es este proyecto

FerreteríaMS es una aplicación web que permite a los clientes de una ferretería buscar productos por nombre y consultar su ubicación física dentro de la tienda.

La ubicación se expresa mediante rack o estantería, columna, nivel y posición.

La primera versión, denominada **FerreteríaMS v0**, incorporará:

- Búsqueda pública de productos.
- Consulta de ubicación principal y ubicaciones secundarias.
- Administración básica del inventario mediante acceso protegido.
- Almacenamiento persistente de los datos en un archivo Excel versionado en GitHub.
- Una sección visual de Gemini identificada como «Próximamente».

La versión v0 no incorporará ventas, precios, cantidades, control de existencias, carritos de compra ni transacciones comerciales.

La entrega final del proyecto incorporará Gemini como asistente de inteligencia artificial para ofrecer información técnica y asesoría interactiva sobre productos y proyectos.

**Gemini tiene dos funciones distintas en este proyecto:**

1. Actuar como agente de programación durante el desarrollo.
2. Integrarse posteriormente como asistente funcional dentro de la aplicación, exclusivamente cuando se trabaje en la entrega final.

La segunda función no forma parte de FerreteríaMS v0.

### Documentos de referencia

Antes de desarrollar cualquier funcionalidad, el agente deberá consultar:

1. `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`: concepto general aprobado del proyecto.
2. `01_Documentacion/02_Especificaciones_v0.md`: requisitos y criterios de aceptación aprobados para v0.
3. `AGENTS.md`: reglas permanentes del agente.
4. El prompt correspondiente a la tarea solicitada.

El documento `03_Especificaciones_Final.md` será utilizado cuando se autorice expresamente el desarrollo de la entrega final.

Las decisiones posteriores aprobadas y documentadas deberán respetarse sin modificar silenciosamente los documentos originales.

Si existen contradicciones, dudas o requisitos insuficientemente definidos, el agente deberá identificarlos y solicitar aclaración antes de ejecutar cambios que puedan afectar el alcance.

---

## 2. Cómo está hecho

### 2.1. Tecnologías principales

FerreteríaMS v0 utilizará:

- **Python:** lenguaje principal.
- **Streamlit:** interfaz web.
- **pandas:** lectura, procesamiento y consulta del inventario.
- **Excel `.xlsx`:** almacenamiento estructurado del inventario.
- **GitHub:** repositorio y control de versiones.
- **GitHub API:** actualización del archivo maestro.
- **Streamlit Community Cloud:** plataforma de despliegue.

Se podrán incorporar librerías complementarias cuando sean necesarias, gratuitas y compatibles con el alcance aprobado.

Toda dependencia añadida deberá quedar registrada en `requirements.txt`.

No deberá integrarse Gemini API como funcionalidad operativa de v0.

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

El documento `03_Especificaciones_Final.md` se preparará en una etapa posterior.

El archivo `inventario.xlsx` solo podrá generarse automáticamente si el archivo maestro todavía no existe en GitHub.

### 2.3. Inventario

El archivo maestro `inventario.xlsx` contendrá exactamente cuatro hojas:

**Productos:** `Codigo_Producto`, `Nombre`, `Categoria_ID`, `Descripcion`.

**Categorías:** `Categoria_ID`, `Nombre_Categoria`.

**Ubicaciones:** `Ubicacion_ID`, `Rack`, `Columna`, `Nivel`, `Posicion`.

**Asignaciones:** `Codigo_Producto`, `Ubicacion_ID`, `Principal`.

El agente deberá respetar los nombres de columnas, las relaciones y las validaciones definidas en la sección 3 de `02_Especificaciones_v0.md`.

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

El agente deberá implementar únicamente las funcionalidades incluidas en la etapa autorizada.

No deberá agregar funcionalidades nuevas por iniciativa propia, aunque considere que podrían mejorar la aplicación.

Cuando identifique una mejora, podrá recomendarla, explicando su utilidad, pero deberá esperar autorización antes de implementarla.

### 3.2. Seguir los requisitos y criterios de aceptación

Cada tarea deberá identificar, cuando corresponda:

- Requisitos funcionales afectados, identificados mediante códigos `RF`.
- Criterios de aceptación correspondientes, identificados mediante códigos `CA`.
- Archivos que será necesario crear o modificar.
- Pruebas necesarias para verificar el resultado.

El agente no deberá sustituir un requisito aprobado por una interpretación propia.

### 3.3. Realizar cambios pequeños y verificables

El desarrollo se dividirá en tareas organizadas y secuenciales.

Cada tarea deberá tener un objetivo definido.

El agente deberá evitar modificaciones innecesarias en archivos o funcionalidades que no estén relacionados con la tarea.

Al finalizar deberá explicar qué cambió, por qué y cómo verificó el resultado.

### 3.4. Proteger las credenciales y los secretos

Las contraseñas, API keys y tokens deberán permanecer protegidos.

Está prohibido incluir secretos reales en:

- Código fuente.
- Archivos versionados.
- Documentación pública.
- Prompts.
- Resultados y registros de pruebas.

Deberán utilizarse mecanismos seguros de configuración, como los Secrets de Streamlit cuando corresponda.

Las contraseñas administrativas deberán protegerse mediante hashing seguro.

Los tokens de GitHub tendrán únicamente los permisos necesarios.

### 3.5. Preservar la seguridad administrativa

El agente deberá implementar los controles definidos en `02_Especificaciones_v0.md`, incluyendo:

- Una cuenta administrativa inicial.
- Cinco intentos fallidos consecutivos antes de aplicar bloqueo.
- Bloqueos progresivos de 5, 10, 20 y 30 minutos.
- Expiración de sesión después de quince minutos de inactividad.
- Advertencia dos minutos antes de la expiración.
- Renovación mediante «Continuar sesión».
- Protección temporal de cambios no guardados y reautenticación.
- Restricción de la administración a la interfaz web para computadora.

No deberá depender exclusivamente de ocultar botones o pestañas para impedir operaciones no autorizadas.

### 3.6. Preservar los datos

Antes de modificar el inventario, el agente deberá comprobar las reglas de integridad aplicables.

No podrá eliminar o sobrescribir información confirmada sin que la operación esté autorizada.

Las modificaciones administrativas deberán conservar correctamente los datos existentes que no hayan sido objeto del cambio.

Si ocurre un conflicto de versiones, no deberá sobrescribir silenciosamente el archivo maestro.

### 3.7. Mantener una interfaz sencilla

La interfaz deberá seguir las imágenes conceptuales aprobadas, respetando los requisitos funcionales.

El cliente podrá buscar exclusivamente por nombre de producto.

La interfaz no deberá presentar FerreteríaMS como una tienda de venta en línea.

No deberá incorporar carritos de compra, precios, cantidades ni controles comerciales.

La interfaz pública deberá funcionar en computadora y celular.

La instalación PWA no es un requisito de v0.

### 3.8. Manejar los errores

Las operaciones que puedan fallar deberán incorporar mecanismos apropiados de manejo de errores.

Los mensajes deberán ser comprensibles para el usuario.

Un fallo de conexión o lectura no deberá mostrarse como una búsqueda sin resultados.

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
- Requisitos RF relacionados.
- Criterios CA relacionados.
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

Antes de realizar acciones que publiquen o integren cambios, como `push`, `merge` o despliegue, el agente deberá contar con la autorización correspondiente.

No deberá realizar operaciones destructivas sobre el repositorio o el inventario sin autorización expresa.

---

## 4. Cómo comprobar que funciona

### 4.1. Verificación general

Antes de declarar una tarea terminada, Gemini deberá verificar que:

1. El código correspondiente puede ejecutarse o, si no es posible, explicar el impedimento.
2. El resultado cumple los RF y CA aplicables.
3. No se introdujeron cambios fuera de alcance.
4. No se afectaron funcionalidades previamente aprobadas.
5. No se expusieron credenciales.
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

El agente deberá comprobar, entre otros casos:

- Búsqueda por nombre completo.
- Búsqueda por nombre parcial.
- Coincidencias sin distinción de acentos y mayúsculas.
- Orden por relevancia.
- Diez resultados por página.
- Consulta de ubicación principal y secundarias.
- Búsqueda sin coincidencias.
- Búsqueda vacía.
- Error de conexión con opción de reintentar.

### 4.4. Pruebas administrativas

El agente deberá comprobar:

- Autenticación válida e inválida.
- Bloqueos progresivos.
- Expiración y renovación de sesión.
- Recuperación temporal de cambios no guardados.
- Creación y edición de productos.
- Inmutabilidad de códigos existentes.
- Asignación y retiro de ubicaciones.
- Mantenimiento de exactamente una ubicación principal.
- Rechazo de modificaciones no autorizadas.
- Restricción administrativa desde dispositivos móviles.

### 4.5. Pruebas de inventario y persistencia

El agente deberá comprobar:

- Lectura de las cuatro hojas Excel.
- Validez de las relaciones entre hojas.
- Rechazo de códigos duplicados.
- Rechazo de categorías o ubicaciones inexistentes.
- Rechazo de asignaciones duplicadas.
- Inicialización únicamente cuando no exista inventario maestro.
- Protección del inventario existente.
- Guardado mediante GitHub API.
- Detección de conflictos de versiones.
- Actualización de búsquedas sin reiniciar Streamlit.
- Persistencia después de reinicios.

### 4.6. Pruebas de la sección Gemini

Durante v0 se verificará que:

- El área aparezca como «Próximamente».
- No se requiera Gemini API key para operar la aplicación.
- No se realicen consultas funcionales a Gemini API.

### 4.7. Evidencia de resultados

El agente deberá registrar:

- Pruebas ejecutadas.
- Resultados obtenidos.
- Criterios CA que se han comprobado.
- Pruebas pendientes o no ejecutadas.
- Errores encontrados.
- Correcciones realizadas.
- Limitaciones conocidas.

No deberá afirmar que una prueba fue ejecutada correctamente si no existe evidencia de su ejecución.

La aprobación final de una funcionalidad corresponderá a la revisión humana de los resultados.

---

## 5. Qué no hacer

Gemini y cualquier otro agente que participe en el desarrollo de FerreteríaMS deberán respetar las siguientes prohibiciones:

1. No modificar el concepto ni las especificaciones aprobadas sin autorización.
2. No desarrollar funcionalidades de la entrega final durante la construcción de v0.
3. No incorporar Gemini API funcional durante v0.
4. No agregar ventas, facturación, precios, cantidades, carritos de compra ni control de existencias.
5. No introducir búsqueda pública independiente por marca o categoría.
6. No agregar administración móvil del inventario.
7. No implementar instalación PWA como requisito de v0.
8. No modificar la arquitectura aprobada sin solicitar autorización.
9. No sobrescribir ni recrear automáticamente un inventario que ya exista en GitHub.
10. No modificar códigos únicos de productos existentes.
11. No permitir que un producto conserve ubicaciones inválidas o más de una ubicación principal.
12. No almacenar contraseñas en texto plano ni publicar secretos.
13. No eliminar archivos, datos o documentación aprobada sin autorización.
14. No realizar `push`, `merge`, despliegues ni operaciones destructivas sin autorización.
15. No afirmar que las pruebas pasaron cuando no fueron ejecutadas.
16. No modificar archivos ajenos a una tarea sin necesidad justificada.
17. No ocultar errores, conflictos de versiones ni limitaciones técnicas.
18. No añadir complejidad innecesaria o funcionalidades que no correspondan a la etapa autorizada.

Si una instrucción recibida contradice las restricciones del proyecto, el agente deberá detener la operación afectada, explicar la contradicción y solicitar una decisión antes de continuar.