# PROMPT 03 — Lectura del inventario desde GitHub API

**Proyecto:** FerreteríaMS v0  
**Identificador:** `FERMS-V0-P03`  
**Etapa:** Integración de lectura del inventario remoto  
**Agente:** Antigravity en VS Code  
**Repositorio:** `JunyMSAI/FerreteriaMS`  
**Rama:** `main`  
**Directorio local:** `C:\Projects\FerreteriaMS`  
**Archivo del prompt:** `02_Prompts/03_Lectura_GitHub.md`  

---

## 1. Objetivo de la tarea

Desarrollar y verificar un mecanismo seguro para consultar el archivo maestro `03_Aplicacion/inventario.xlsx` almacenado en el repositorio de GitHub.

La integración deberá:

1. Verificar si existe el archivo maestro remoto.
2. Distinguir su inexistencia de los errores de consulta.
3. Descargar su contenido cuando exista.
4. Obtener e identificar la versión del archivo mediante su SHA de GitHub.
5. Utilizar el motor Excel implementado en `03_Aplicacion/inventario.py` para validar los datos descargados.
6. Comunicar errores de forma estructurada y comprensible.
7. Preparar una interfaz reutilizable para las siguientes tareas.

Esta tarea implementará exclusivamente operaciones de **lectura de GitHub API**.

No deberá crear, actualizar, reemplazar ni eliminar archivos remotos.

---

## 2. Documentación obligatoria

Antes de trabajar, consulta íntegramente:

- `GEMINI.md`
- `AGENTS.md`
- `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`
- `01_Documentacion/02_Especificaciones_v0.md`
- `02_Prompts/02_Motor_Inventario.md`
- `05_Resultados/02_Resultado_Motor_Inventario.md`
- Este Prompt 03.

Consulta también el código existente:

- `03_Aplicacion/inventario.py`
- `04_Pruebas/test_02_motor_inventario.py`

Utiliza exclusivamente las versiones existentes en el repositorio.

No reconstruyas el motor Excel, ni sustituyas documentos aprobados por versiones anteriores.

### Dependencia del Prompt 02

El motor Excel de FERMS-V0-P02 ya dispone de:

- Lectura y validación de las cuatro hojas.
- Validaciones de estructura e integridad.
- Identificadores de error.
- Conversión de datos en estructuras de consulta.
- Estados `EXISTE`, `NO_EXISTE` y `DESCONOCIDO_ERROR`.
- Preparación segura de inicialización.

Antes de integrar, verifica sus interfaces y el resultado de las pruebas.

Reutiliza estos componentes en lugar de duplicar sus responsabilidades.

---

## 3. Requisitos funcionales y criterios de aceptación

### Requisitos relacionados

- **RF-022:** inventario maestro `inventario.xlsx`.
- **RF-023:** estructura de cuatro hojas.
- **RF-024:** procesamiento mediante pandas.
- **RF-025:** almacenamiento del maestro en GitHub.
- **RF-027:** base para el control posterior de conflictos de versiones.
- **RF-028:** lectura de la versión vigente sin reinicio manual.
- **RF-029:** inicialización solamente si no existe el archivo.
- **RF-030:** protección contra sobrescritura.
- **RF-038:** manejo de errores de consulta.

### Criterios relacionados

- **CA-022:** lectura de las cuatro hojas aprobadas.
- **CA-024:** consulta de cambios confirmados, pendiente de verificación completa con la interfaz.
- **CA-025:** obtención de información para detectar conflictos; comprobación de escritura reservada para el Prompt 10.
- **CA-036:** lectura desde la aplicación desplegada, pendiente de despliegue.
- **CA-042:** diferenciación de fallos de consulta.
- **CA-020 y CA-021:** solo verificación de los estados necesarios para inicialización segura; la creación real del archivo permanece pendiente.

No marques como completamente aprobados los criterios que dependan de funcionalidades todavía no implementadas.

---

## 4. Configuración del repositorio remoto

La integración utilizará estos parámetros:

| Parámetro | Valor |
|---|---|
| Plataforma | GitHub |
| Propietario | `JunyMSAI` |
| Repositorio | `FerreteriaMS` |
| Rama | `main` |
| Ruta del inventario | `03_Aplicacion/inventario.xlsx` |

Los parámetros podrán declararse mediante configuración centralizada para facilitar su reutilización.

No introduzcas URLs innecesariamente dispersas por el código.

La aplicación deberá poder comprobar la versión vigente del archivo remoto cuando se realice una nueva consulta.

No debe depender indefinidamente de una copia almacenada en caché.

---

## 5. Construcción del módulo GitHub API

### 5.1. Organización del código

Crea un módulo específico para la lectura del inventario desde GitHub dentro de `03_Aplicacion/`.

Puedes utilizar un nombre como:

`03_Aplicacion/github_inventario.py`

El módulo deberá separar:

- Solicitudes HTTP.
- Interpretación de respuestas de GitHub.
- Consulta de existencia del archivo.
- Obtención del contenido y su identificador SHA.
- Integración con el motor Excel.
- Tratamiento de errores.

No dupliques las validaciones ya implementadas en `inventario.py`.

No modifiques su lógica salvo que detectes una incompatibilidad imprescindible. Si ello requiere cambios fuera de los archivos autorizados, solicita autorización previamente.

### 5.2. Consulta de existencia

Implementa una función que consulte si el archivo maestro existe en la rama configurada.

Deberá devolver un estado compatible con:

- `EXISTE`
- `NO_EXISTE`
- `DESCONOCIDO_ERROR`

Un `404` podrá interpretarse como inexistencia solamente cuando la respuesta y el contexto permitan determinar con seguridad que el repositorio y la referencia son accesibles y que el archivo solicitado realmente no existe.

Si el repositorio es privado, faltan permisos, la rama no existe o el estado no puede determinarse, no debe declararse automáticamente `NO_EXISTE`.

Los errores de autorización, conexión, cuota, servidor y respuestas inesperadas deberán tratarse de forma diferenciada.

### 5.3. Descarga del archivo

Cuando el archivo exista:

1. Solicita el contenido mediante GitHub API.
2. Obtén su identificador SHA.
3. Descarga el contenido binario completo.
4. Verifica que la respuesta corresponda al archivo esperado.
5. Entrega sus bytes al motor `inventario.py`.
6. Valida la estructura y las relaciones de las cuatro hojas.
7. Devuelve los datos estructurados junto con la versión remota identificada.

No guardes una copia del archivo maestro automáticamente en el repositorio local.

No modifiques los datos descargados para ocultar inconsistencias.

### 5.4. Identificación de versión

El resultado de una lectura exitosa deberá permitir identificar:

- Repositorio consultado.
- Rama consultada.
- Ruta del archivo.
- SHA de GitHub correspondiente al archivo.
- Contenido validado del inventario.

Distingue el SHA del archivo remoto de cualquier hash calculado localmente.

Esta información deberá servir posteriormente para implementar el control de concurrencia y conflictos de versiones del Prompt 10.

No implementes todavía operaciones de escritura.

### 5.5. Validación del contenido

Utiliza:

`cargar_inventario_excel()`

y las estructuras existentes de `inventario.py`.

Si el archivo descargado tiene hojas faltantes, adicionales o datos inconsistentes, comunica el error correspondiente.

No sustituyas silenciosamente el archivo remoto por el inventario demostrativo.

Si un archivo existe pero está corrupto, ello **no autoriza a generar otro inventario**.

---

## 6. Seguridad y credenciales

El repositorio es actualmente público, por lo que las consultas públicas de lectura podrán realizarse sin un token si las condiciones de GitHub API lo permiten.

Sin embargo, la implementación deberá estar preparada para utilizar una credencial mediante mecanismos seguros cuando resulte necesaria.

### Reglas obligatorias

- Nunca incluir tokens reales directamente en el código.
- Nunca introducir credenciales en archivos Markdown.
- Nunca mostrar tokens en errores, trazas o informes.
- Nunca publicar secretos en GitHub.
- Utilizar permisos mínimos.
- No crear ni modificar tokens durante esta tarea.
- No solicitar al usuario que pegue secretos en la conversación.
- No incluir una dependencia obligatoria de Gemini API.

Si una consulta no puede realizarse por falta de autenticación, comunícalo y deja la prueba como pendiente.

La ausencia de token no debe provocar una operación de escritura ni una modificación del repositorio.

---

## 7. Manejo de errores

Implementa respuestas o excepciones diferenciables para los siguientes escenarios:

1. Archivo remoto confirmado como inexistente.
2. Repositorio inaccesible.
3. Rama inexistente o inaccesible.
4. Acceso denegado.
5. Credencial inválida o insuficiente.
6. Límite de solicitudes de GitHub API.
7. Error temporal del servidor.
8. Tiempo de espera agotado.
9. Conexión de red fallida.
10. Respuesta de API con formato inesperado.
11. Contenido binario inválido.
12. Archivo Excel corrupto.
13. Inventario que incumple el esquema aprobado.

Cuando una consulta falle, no utilices silenciosamente información potencialmente desactualizada como si fuera la versión vigente.

La futura interfaz deberá poder distinguir entre:

- Producto no encontrado.
- Inventario todavía no inicializado.
- Error al consultar el inventario.
- Datos remotos inválidos.

Un error de GitHub API no deberá presentarse como si la búsqueda no tuviera coincidencias.

---

## 8. Integración con la inicialización segura

El motor del Prompt 02 contiene:

`preparar_inicializacion_segura(...)`

Comprueba que el resultado de la consulta remota pueda utilizarse con esa función.

### Estados esperados

**EXISTE:** no se permite inicialización automática.

**NO_EXISTE:** permite preparar los datos iniciales en memoria, conforme a las reglas aprobadas.

**DESCONOCIDO_ERROR:** bloquea la inicialización.

Durante este Prompt 03 no deberás crear realmente el archivo en GitHub.

No ejecutes escrituras remotas ni siquiera como prueba.

La inicialización definitiva deberá mantenerse pendiente de autorización e integración posterior.

---

## 9. Pruebas automatizadas

Crea una suite de pruebas independiente para esta tarea dentro de `04_Pruebas/`, utilizando un nombre compatible con `unittest`, por ejemplo:

`test_03_lectura_github.py`

### 9.1. Pruebas de consulta

Comprueba:

- Repositorio y rama configurados correctamente.
- Archivo existente.
- Archivo inexistente confirmado.
- Error de autenticación.
- Error de permisos.
- Error de conexión.
- Timeout.
- Error de servidor.
- Límite de solicitudes.
- Respuesta inesperada de GitHub API.

### 9.2. Pruebas de descarga

Comprueba:

- Obtención correcta del SHA.
- Descarga completa de bytes.
- Lectura del Excel descargado mediante el motor existente.
- Identificación de las cuatro hojas.
- Conservación de códigos como texto.
- Detección de un Excel inválido.
- Ausencia de escrituras en disco.

### 9.3. Pruebas de inicialización segura

Comprueba que:

- Un estado `EXISTE` impide inicialización.
- Un estado `DESCONOCIDO_ERROR` impide inicialización.
- Un estado `NO_EXISTE` permite preparar los bytes iniciales en memoria.
- Los fallos de API nunca se traducen automáticamente en confirmación de inexistencia.

### 9.4. Simulación de respuestas

Utiliza respuestas simuladas, mocks o técnicas equivalentes para las pruebas automatizadas.

Las pruebas deberán ser reproducibles y no depender de credenciales reales.

No modifiques el repositorio remoto durante las pruebas.

### 9.5. Prueba real de solo lectura

Cuando sea posible y esté autorizado, realiza una consulta real de solo lectura al repositorio GitHub para verificar la conectividad y el estado del archivo maestro.

No declares que el archivo existe o no existe basándote exclusivamente en una simulación.

Si la consulta real no puede completarse, registra:

**NO VERIFICADO — Consulta remota real pendiente.**

No utilices permisos de escritura para superar un problema de lectura.

### 9.6. Regresión

Ejecuta nuevamente las pruebas del Prompt 02 junto con las nuevas pruebas del Prompt 03.

Las pruebas anteriores deberán continuar funcionando.

Distingue las pruebas que pasaron, fallaron o no pudieron ejecutarse.

---

## 10. Archivos autorizados

Se autoriza crear o modificar localmente:

- Un módulo nuevo de lectura GitHub API en `03_Aplicacion/`.
- `requirements.txt`, únicamente si se incorpora una dependencia realmente necesaria.
- Una suite de pruebas nueva en `04_Pruebas/`.
- Archivos auxiliares estrictamente necesarios para las pruebas.
- Un informe de resultados en `05_Resultados/`.

El módulo `inventario.py` deberá reutilizarse sin modificarlo, salvo autorización adicional.

### Archivos protegidos

No modificar:

- `GEMINI.md`
- `AGENTS.md`
- `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`
- `01_Documentacion/02_Especificaciones_v0.md`
- `03_Aplicacion/app.py`
- `03_Aplicacion/inventario.py`
- `README.md`
- Los archivos existentes en `02_Prompts/`
- El inventario maestro definitivo `03_Aplicacion/inventario.xlsx`

No crear `03_Especificaciones_Final.md`.

---

## 11. Operaciones autorizadas y prohibidas

### Autorizadas

- Lectura de archivos del proyecto.
- Desarrollo local del módulo GitHub API.
- Lecturas HTTP de GitHub API.
- Pruebas automatizadas con mocks.
- Pruebas de conectividad exclusivamente de lectura.
- Revisión del estado local de Git.
- Registro local de resultados y evidencias.

### Prohibidas

- Crear, actualizar o eliminar archivos en GitHub.
- Subir `inventario.xlsx`.
- Ejecutar métodos de escritura contra GitHub API.
- Modificar documentos

**No comiences el Prompt 04.**