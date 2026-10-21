# PROMPT 02 — Preparación del entorno y motor de inventario Excel

**Proyecto:** FerreteríaMS  
**Identificador:** `FERMS-V0-P02`  
**Etapa:** Desarrollo de FerreteríaMS v0 

---

## 1. Objetivo general

Implementar y verificar la base de procesamiento del inventario de FerreteríaMS v0, comenzando por los archivos de configuración `requirements.txt` y `.gitignore`.

Después, construir el motor Python encargado de leer, validar y procesar la estructura aprobada de `inventario.xlsx`.

El trabajo debe respetar la documentación oficial y mantenerse separado de las funcionalidades de búsqueda pública, administración visual, autenticación y despliegue, reservadas para tareas posteriores.

**Esta tarea autoriza modificaciones locales únicamente dentro del alcance expresamente definido. No autoriza publicar cambios en GitHub.**

## 2. Documentación obligatoria

Antes de realizar modificaciones, consulta:

1. `GEMINI.md`
2. `AGENTS.md`
3. `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`
4. `01_Documentacion/02_Especificaciones_v0.md`
5. `02_Prompts/01_Verificacion_Inicial.md`
6. Este Prompt 02

Utiliza las versiones que existen actualmente en el repositorio.

No reconstruyas ni sustituyas los documentos aprobados utilizando borradores o versiones anteriores.

Si no puedes consultar correctamente alguno de los documentos obligatorios, informa del problema antes de continuar.

### Resultado previo

La auditoría `FERMS-V0-P01` identificó:

- Documentación principal disponible.
- Repositorio local conectado con GitHub.
- Entorno Python con Streamlit, pandas y openpyxl instalados.
- Ausencia inicial de `requirements.txt` y `.gitignore`.
- `03_Aplicacion/app.py` con la plantilla académica original.
- `inventario.xlsx` todavía pendiente de creación controlada.

Verifica nuevamente los hechos que puedan haber cambiado desde aquella auditoría.

## 3. Requisitos y criterios relacionados

### Requisitos funcionales

- **RF-020:** validaciones del inventario.
- **RF-022:** archivo maestro `inventario.xlsx`.
- **RF-023:** cuatro hojas y estructura del archivo.
- **RF-024:** procesamiento mediante pandas.
- **RF-025:** almacenamiento del maestro en GitHub.
- **RF-029:** inicialización automática cuando no exista el maestro.
- **RF-030:** protección contra sobrescritura de un inventario existente.
- **RF-031:** identificación de los datos demostrativos.

### Criterios de aceptación

- **CA-020:** inicialización cuando no existe el archivo maestro.
- **CA-021:** protección del inventario existente.
- **CA-022:** reconocimiento de las cuatro hojas y sus columnas.
- **CA-047:** rechazo de categorías inexistentes.
- **CA-048:** rechazo de ubicaciones inexistentes.
- **CA-049:** detección de ubicaciones físicas duplicadas.
- **CA-050:** detección de asignaciones duplicadas.

Los criterios **CA-020 y CA-021 requerirán verificación integrada adicional** cuando esté disponible la conexión de lectura de GitHub y el mecanismo completo de inicialización.

El criterio **CA-051**, relacionado con la conservación de la integridad después del guardado, se comprobará integralmente en la tarea de persistencia mediante GitHub API.

No declares estos criterios integrados como aprobados anticipadamente.

---

## 4. Etapa A — Preparar requirements.txt y .gitignore

### 4.1. Archivo requirements.txt

Verifica si existe `requirements.txt` en la raíz del proyecto.

Si no existe, créalo.

Incluye las dependencias Python necesarias para la versión v0 que estén justificadas por el proyecto.

Considera:

- Streamlit para la aplicación.
- pandas para el procesamiento del inventario.
- openpyxl para trabajar con archivos `.xlsx`.
- Otras dependencias únicamente si resultan necesarias para el código autorizado.

No agregues `google-genai`, porque Gemini API no será funcional dentro de FerreteríaMS v0.

Si utilizas una biblioteca estándar de Python, no la incorpores como dependencia externa.

No copies automáticamente el contenido de la plantilla de `requirements.txt` del profesor, ya que contiene una dependencia para Gemini operativo que no corresponde a v0.

Documenta cualquier dependencia adicional y justifica su necesidad.

### 4.2. Archivo .gitignore

Verifica si existe `.gitignore` en la raíz del repositorio.

Si no existe, créalo.

Debe contemplar, como mínimo:

- Entornos virtuales de Python.
- Directorios `__pycache__`.
- Archivos Python compilados.
- Archivos temporales de pruebas.
- Cachés habituales de herramientas Python.
- Configuraciones locales que contengan credenciales.
- `.streamlit/secrets.toml`.
- Archivos `.env` que contengan secretos.

No excluyas los documentos oficiales aprobados, los archivos de aplicación necesarios ni `requirements.txt`.

No excluyas globalmente todos los archivos `.xlsx`, porque `inventario.xlsx` será el archivo maestro versionado de FerreteríaMS.

### 4.3. Verificación de seguridad

Comprueba que no se hayan incluido credenciales reales ni secretos en los archivos nuevos.

No crees tokens ni claves de API.

No modifiques la configuración privada de GitHub ni de Streamlit Cloud.

### 4.4. Resultado de la etapa A

Entrega una explicación de:

- Archivos creados o actualizados.
- Dependencias incorporadas.
- Exclusiones configuradas.
- Comprobaciones realizadas.
- Problemas encontrados.

---

## 5. Etapa B — Construir el motor del inventario Excel

### 5.1. Alcance

Construye un módulo Python dedicado al procesamiento del inventario.

El módulo deberá permitir:

1. Leer un archivo Excel existente.
2. Reconocer sus cuatro hojas.
3. Verificar los nombres de columnas aprobados.
4. Preservar los códigos como texto.
5. Validar productos, categorías, ubicaciones y asignaciones.
6. Detectar relaciones inválidas.
7. Preparar datos estructurados para las futuras funcionalidades de búsqueda.
8. Crear en memoria un inventario demostrativo válido para pruebas.

Utiliza pandas y las bibliotecas complementarias necesarias para trabajar con `.xlsx`.

Puedes proponer un nombre técnico para el módulo, por ejemplo `inventario.py`, dentro de `03_Aplicacion/`.

Si la implementación necesita módulos auxiliares, explica por qué son necesarios y limita su creación al motor del inventario.

**No modifiques todavía `03_Aplicacion/app.py`.**

Su adaptación a FerreteríaMS está prevista para tareas posteriores.

### 5.2. Hojas y columnas obligatorias

El archivo deberá manejar exactamente las siguientes hojas.

#### Productos

| Columna | Tipo lógico |
|---|---|
| Codigo_Producto | Texto |
| Nombre | Texto |
| Categoria_ID | Texto |
| Descripcion | Texto |

#### Categorías

| Columna | Tipo lógico |
|---|---|
| Categoria_ID | Texto |
| Nombre_Categoria | Texto |

#### Ubicaciones

| Columna | Tipo lógico |
|---|---|
| Ubicacion_ID | Texto |
| Rack | Texto |
| Columna | Texto |
| Nivel | Texto |
| Posicion | Texto |

#### Asignaciones

| Columna | Tipo lógico |
|---|---|
| Codigo_Producto | Texto |
| Ubicacion_ID | Texto |
| Principal | Texto |

Conserva exactamente estos nombres.

No añadas columnas destinadas a precios, cantidades, inventario físico o transacciones.

### 5.3. Validaciones obligatorias

Implementa, como mínimo, las siguientes verificaciones.

**Productos**

- `Codigo_Producto` obligatorio y único.
- `Nombre` obligatorio.
- `Categoria_ID` debe referenciar una categoría válida.
- `Descripcion` puede estar vacía.
- Los códigos deben conservarse como texto, incluidos sus posibles ceros iniciales.

**Categorías**

- `Categoria_ID` obligatorio y único.
- `Nombre_Categoria` obligatorio.
- No pueden existir categorías duplicadas por identificador.

**Ubicaciones**

- `Ubicacion_ID` obligatorio y único.
- Los campos `Rack`, `Columna`, `Nivel` y `Posicion` son necesarios para identificar la ubicación.
- La combinación de estos cuatro campos debe ser única.

**Asignaciones**

- Cada `Codigo_Producto` debe existir en Productos.
- Cada `Ubicacion_ID` debe existir en Ubicaciones.
- No puede repetirse una relación entre el mismo producto y la misma ubicación.
- Cada producto debe tener al menos una asignación.
- Cada producto debe tener exactamente una ubicación principal.
- Las ubicaciones secundarias deben identificarse correctamente.

El campo `Principal` deberá representar de forma consistente los estados lógicos Sí y No.

La normalización de valores de entrada no deberá aceptar silenciosamente estados ambiguos o inválidos.

### 5.4. Manejo de errores

El motor deberá diferenciar entre:

- Archivo inexistente.
- Archivo corrupto o ilegible.
- Hoja obligatoria faltante.
- Columnas obligatorias faltantes.
- Valores obligatorios ausentes.
- Identificadores duplicados.
- Referencias a categorías inexistentes.
- Referencias a ubicaciones inexistentes.
- Productos sin asignaciones.
- Productos con más de una ubicación principal.
- Ubicaciones físicas duplicadas.

Cuando se detecte información inválida, el motor deberá comunicar el problema de manera identificable.

No deberá modificar automáticamente el archivo para ocultar errores estructurales o de integridad.

No sobrescribas un archivo existente durante una operación de validación.

---

## 6. Etapa C — Preparación de la inicialización segura

### 6.1. Regla fundamental

El concepto y las especificaciones establecen que `inventario.xlsx` solamente podrá generarse automáticamente si todavía no existe el archivo maestro en GitHub.

Esta regla deberá respetarse desde el diseño del motor.

### 6.2. Separación de responsabilidades

Durante el Prompt 02:

- Podrás desarrollar una función que construya en memoria un inventario demostrativo válido.
- Podrás preparar la serialización del inventario a formato `.xlsx`.
- Podrás probar las funciones con archivos temporales aislados.
- Podrás preparar una interfaz de funciones que posteriormente permita conectar la inicialización a GitHub.

**No debes crear automáticamente `03_Aplicacion/inventario.xlsx` como consecuencia de ejecutar pruebas o importar un módulo.**

No debes subir un inventario demostrativo al repositorio remoto.

### 6.3. Condición de creación remota

La futura integración deberá comprobar expresamente si el archivo maestro existe en GitHub.

Solamente cuando se confirme que no existe podrá proponerse o ejecutarse la creación inicial, conforme al flujo autorizado de la aplicación.

Un error de conexión, falta de permisos o resultado desconocido **no equivale a la confirmación de que el archivo no existe**.

Si no se puede determinar su existencia con seguridad, la inicialización deberá detenerse y comunicar el problema.

### 6.4. Alcance de este prompt

No implementes todavía la conexión de lectura o escritura de GitHub API, reservada para los Prompts 03 y 10.

Puedes diseñar una interfaz mínima para que el motor sea utilizado posteriormente por esas funcionalidades, pero sin introducir una integración remota prematura.

---

## 7. Etapa D — Pruebas del motor

Crea pruebas locales verificables dentro de `04_Pruebas/`, utilizando nombres compatibles con las herramientas de prueba elegidas.

Las pruebas deberán ejecutarse sobre datos ficticios y archivos temporales aislados.

### 7.1. Casos válidos

Comprueba:

- Lectura de las cuatro hojas.
- Reconocimiento correcto de los encabezados.
- Conservación de identificadores como texto.
- Lectura de productos asociados con categorías existentes.
- Lectura de ubicaciones válidas.
- Producto con una ubicación principal.
- Producto con ubicación principal y ubicaciones secundarias.
- Generación de un inventario demostrativo válido en memoria.
- Serialización y posterior lectura de un archivo temporal válido.

### 7.2. Casos inválidos

Comprueba:

- Productos con códigos duplicados.
- Productos sin nombre.
- Categorías inexistentes.
- Categorías duplicadas por identificador.
- Ubicaciones duplicadas por identificador.
- Combinaciones físicas duplicadas.
- Asignaciones a productos inexistentes.
- Asignaciones a ubicaciones inexistentes.
- Asignaciones duplicadas.
- Productos sin ubicación.
- Productos con dos ubicaciones principales.
- Valores inválidos del campo Principal.
- Archivos con hojas o columnas faltantes.
- Archivos corruptos.

### 7.3. Protección de datos

Realiza pruebas que demuestren que:

- La validación no sobrescribe el archivo de entrada.
- La generación demostrativa no sobrescribe archivos maestros existentes.
- Importar el módulo del inventario no genera archivos automáticamente.
- Las pruebas no introducen cambios en el repositorio remoto.

### 7.4. Evidencias

Registra cuáles pruebas fueron ejecutadas y sus resultados.

Distingue claramente entre:

- APROBADO.
- FALLIDO.
- NO EJECUTADO.
- PENDIENTE DE INTEGRACIÓN.

No declares aprobados CA que dependan de GitHub API si la integración todavía no existe.

---

## 8. Archivos autorizados para esta tarea

Puedes crear o modificar localmente, dentro del alcance del Prompt 02:

- `requirements.txt`
- `.gitignore`
- Un módulo Python del motor Excel dentro de `03_Aplicacion/`.
- Los módulos auxiliares estrictamente necesarios para ese motor.
- Pruebas relacionadas con el motor dentro de `04_Pruebas/`.
- Un informe de resultados correspondiente a esta tarea dentro de `05_Resultados/`.

Utiliza nombres de archivos claros y consistentes con la estructura aprobada.

### Archivos protegidos

No modifiques:

- `GEMINI.md`.
- `AGENTS.md`.
- `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`.
- `01_Documentacion/02_Especificaciones_v0.md`.
- `03_Aplicacion/app.py`.
- `README.md`.
- `02_Prompts/01_Verificacion_Inicial.md`.
- `02_Prompts/02_Motor_Inventario.md`.

No crees todavía `03_Especificaciones_Final.md`.

No crees todavía el archivo maestro definitivo `03_Aplicacion/inventario.xlsx`.

Si encuentras una necesidad de modificar algún archivo protegido, detén esa operación y solicita autorización.

---

## 9. Operaciones permitidas y prohibidas

### Permitidas

- Leer documentación y código existente.
- Crear los archivos locales expresamente autorizados.
- Instalar dependencias necesarias en el entorno local, siempre que no impliquen costes ni cambios fuera del proyecto.
- Ejecutar pruebas locales.
- Inspeccionar resultados y errores.
- Crear el informe de resultados autorizado.
- Consultar el estado local de Git.

### Prohibidas

- Modificar documentos aprobados.
- Modificar `app.py`.
- Crear el inventario maestro definitivo sin comprobar su inexistencia en GitHub.
- Escribir o eliminar información del repositorio remoto.
- Ejecutar `git push`.
- Ejecutar `git merge`.
- Realizar despliegues.
- Crear pull requests.
- Ejecutar operaciones destructivas sobre archivos existentes.
- Utilizar credenciales reales dentro de código, prompts o informes.
- Incorporar Gemini API operativa a FerreteríaMS v0.
- Comenzar el Prompt 03 automáticamente.

No realices `git commit` durante esta tarea sin una autorización específica posterior.

Si una acción requiere ampliar estas autorizaciones, solicita aprobación antes de realizarla.

---

## 10. Trazabilidad obligatoria

Al ejecutar esta tarea deberás conservar la trazabilidad definida en `AGENTS.md`.

El informe incluirá:

- Identificador `FERMS-V0-P02`.
- Fecha y hora reales de ejecución.
- Título de la tarea.
- Solicitud original íntegra o referencia exacta al archivo de prompt preservado sin cambios.
- Interpretación del agente.
- Acciones realizadas.
- Archivos creados o modificados.
- Dependencias añadidas.
- RF examinados e implementados.
- CA probados.
- Pruebas ejecutadas y resultados.
- Errores o limitaciones.
- Asuntos pendientes.
- Estado de Git.
- Referencia a commit, si existe.

El agente deberá diferenciar explícitamente qué contenido pertenece a la solicitud del usuario y qué decisiones técnicas tomó para implementar el trabajo.

No inventes resultados ni declares pruebas ejecutadas sin evidencia.

El informe de resultados deberá almacenarse en `05_Resultados/` utilizando un nombre identificable, por ejemplo `02_Resultado_Motor_Inventario.md`.

El prompt original deberá permanecer intacto.

---

## 11. Informe final de Antigravity

Presenta un resumen comprensible con estas partes:

### A. Preparación del entorno

Indica:

- Estado de `requirements.txt`.
- Estado de `.gitignore`.
- Dependencias necesarias y justificación.
- Problemas de seguridad o configuración detectados.

### B. Implementación del motor Excel

Describe:

- Módulos creados.
- Funciones principales.
- Hojas procesadas.
- Validaciones aplicadas.
- Manejo de errores.
- Decisiones técnicas relevantes.

### C. Pruebas

Presenta una tabla:

| Prueba | RF/CA relacionado | Resultado | Evidencia |
|---|---|---|---|
| Lectura de cuatro hojas | RF-023 / CA-022 | | |
| Código duplicado | RF-020 | | |
| Categoría inexistente | RF-020 / CA-047 | | |
| Ubicación inexistente | RF-020 / CA-048 | | |
| Ubicación física duplicada | RF-023 / CA-049 | | |
| Asignación duplicada | RF-023 / CA-050 | | |
| Generación demostrativa | RF-029 / CA-020 parcial | | |
| Protección del archivo existente | RF-030 / CA-021 parcial | | |

Añade las demás pruebas ejecutadas.

### D. Restricciones respetadas

Confirma expresamente:

- Documentos aprobados sin cambios.
- `app.py` original sin cambios.
- `inventario.xlsx` maestro no creado ni reemplazado.
- Repositorio remoto sin cambios.
- Ausencia de secretos expuestos.
- Ningún commit, push, merge o despliegue realizado.

### E. Problemas y recomendaciones

Indica qué quedó pendiente para el Prompt 03 y cuáles son los prerrequisitos de integración con GitHub.

### F. Evaluación final

Utiliza uno de estos estados:

- **COMPLETADO:** se implementó y verificó todo el alcance autorizado.
- **COMPLETADO CON OBSERVACIONES:** existe funcionalidad implementada, pero hay asuntos no bloqueantes.
- **INCOMPLETO:** quedaron pendientes elementos obligatorios del Prompt 02.

Justifica la clasificación mediante pruebas y evidencia.

---

## 12. Condición de finalización

El Prompt 02 solamente podrá considerarse terminado cuando:

1. `requirements.txt` esté creado y verificado.
2. `.gitignore` esté creado y verificado.
3. Exista un motor Excel funcional para procesar la estructura aprobada.
4. Las validaciones obligatorias estén implementadas.
5. Se hayan ejecutado pruebas locales.
6. Se hayan documentado sus resultados.
7. No se haya creado ni sobrescrito el archivo maestro definitivo.
8. No se hayan modificado archivos protegidos.
9. El repositorio remoto permanezca sin alteraciones.
10. Se entregue el informe de resultados y el agente espere autorización para continuar.

**No comiences el Prompt 03.**