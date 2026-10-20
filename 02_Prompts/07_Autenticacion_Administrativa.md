# PROMPT 07 — Autenticación administrativa de FerreteríaMS v0

**Proyecto:** FerreteríaMS v0  
**TASK_ID:** `FERMS-V0-P07`  
**Etapa:** Acceso administrativo seguro  
**Agente:** Antigravity dentro de VS Code  
**Repositorio:** `JunyMSAI/FerreteriaMS`  
**Rama:** `main`  
**Directorio:** `C:\Projects\FerreteriaMS`  
**Archivo:** `02_Prompts/07_Autenticacion_Administrativa.md`  

---

## 1. Objetivo general

Implementar la base segura de autenticación para la única cuenta administrativa de FerreteríaMS v0.

Esta etapa incorporará:

- Acceso a la sección administrativa desde la interfaz web de escritorio.
- Formulario de inicio de sesión.
- Verificación segura de credenciales.
- Almacenamiento seguro de la contraseña mediante hash.
- Estado básico de autenticación por sesión.
- Cierre de sesión.
- Protección del contenido administrativo.
- Manejo de credenciales inválidas y errores de configuración.

**No implementar todavía las reglas avanzadas de sesiones, bloqueos progresivos o conservación de borradores**, reservadas para el Prompt 08.

No incorporar todavía formularios para gestionar productos, categorías o ubicaciones.

---

## 2. Documentación obligatoria

Antes de implementar, lee íntegramente:

- `GEMINI.md`.
- `AGENTS.md`.
- `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`.
- `01_Documentacion/02_Especificaciones_v0.md`.
- `02_Prompts/05_Detalles_Ubicaciones.md`.
- `02_Prompts/06_Interfaz_Responsive_Gemini.md`.
- `05_Resultados/05_Resultado_Detalles_Ubicaciones.md`.
- `05_Resultados/06_Resultado_Interfaz_Responsive_Gemini.md`.
- Este Prompt 07.

Revisa la estructura existente de `03_Aplicacion/`, especialmente:

- `app.py`.
- `inventario.py`.
- `github_inventario.py`.
- `busqueda.py`.
- `estilos.css`.

Examina las imágenes conceptuales administrativas del documento Word, particularmente las relacionadas con la pestaña **Productos** y los controles **Login/Logout**.

Localiza los requisitos y criterios de aceptación oficiales relacionados con autenticación, seguridad, acceso administrativo y sesiones. Utiliza sus definiciones exactas, sin inventar equivalencias.

Verifica primero el estado Git y el commit base. Si existen modificaciones inesperadas de una tarea anterior, detente e informa.

---

## 3. Alcance y separación de responsabilidades

### Implementar en el Prompt 07

1. Una única cuenta administrativa.
2. Configuración segura de credenciales.
3. Verificación de contraseña mediante hash.
4. Formulario Login.
5. Función Logout.
6. Estado autenticado/no autenticado por sesión.
7. Protección de acceso a la sección administrativa.
8. Interfaz administrativa inicial, todavía sin operaciones de mantenimiento.
9. Pruebas unitarias y de integración de autenticación.

### Reservar para el Prompt 08

- Expiración de sesión después de 15 minutos de inactividad.
- Advertencia dos minutos antes de expirar.
- Botón para renovar sesión.
- Política de cinco intentos fallidos.
- Bloqueos progresivos de 5, 10, 20 y 30 minutos.
- Reinicio del contador después de autenticación exitosa.
- Conservación temporal de borradores después de expirar la sesión.
- Pruebas completas de temporización, expiración, bloqueo y renovación.

El Prompt 07 debe preparar una arquitectura compatible con esas reglas, pero **no debe ofrecer protección completa contra fuerza bruta o expiración de sesiones antes de que el Prompt 08 esté implementado y aprobado**.

---

## 4. Requisitos funcionales y criterios de aceptación

Consulta los requisitos oficiales relacionados con:

- Identificación del administrador.
- Inicio de sesión.
- Cierre de sesión.
- Restricción de acceso administrativo.
- Contraseña protegida.
- Una sola cuenta administrativa.
- Restricción de administración a la interfaz web de computadora.

Considera especialmente los RF comprendidos en el área administrativa del documento de especificaciones y los criterios CA-009, CA-010, CA-011, CA-019, CA-030 y CA-052 a CA-059, según sus definiciones exactas.

Distingue claramente:

- **Implementado en Prompt 07.**
- **Implementado parcialmente.**
- **Pendiente de Prompt 08.**
- **Pendiente de Prompt 09 o posterior.**

No declares completamente aprobados los criterios que dependan de los controles avanzados del Prompt 08.

---

## 5. Diseño del módulo de autenticación

Crear un módulo separado, con nombre sugerido:

`03_Aplicacion/autenticacion.py`

Este módulo deberá encargarse de:

- Obtener configuración administrativa del entorno seguro.
- Verificar que la configuración exista y sea válida.
- Comprobar credenciales.
- Crear y destruir el estado básico autenticado.
- Devolver resultados estructurados de autenticación.
- Evitar exposiciones de información sensible.

Evita mezclar toda la lógica de seguridad con el código visual de `app.py`.

Las funciones deben poder probarse sin iniciar Streamlit.

No utilizar GitHub como sistema de autenticación de administradores.

---

## 6. Cuenta administrativa y credenciales

### 6.1. Una cuenta administrativa

FerreteríaMS v0 contará exclusivamente con una cuenta administrativa.

No implementar:

- Registro público de usuarios.
- Creación de administradores adicionales.
- Administración de roles.
- Invitaciones a usuarios.
- Recuperación automática de contraseña por correo.
- Inicio de sesión mediante Google, GitHub u otros servicios externos.

### 6.2. Configuración de credenciales

El usuario administrativo deberá configurarse mediante secretos del servidor o variables de entorno.

Se permiten mecanismos compatibles con:

- Variables de entorno locales.
- `st.secrets` de Streamlit.
- Secrets de Streamlit Community Cloud, en etapas posteriores.

No crear contraseñas reales por defecto.

No almacenar credenciales en archivos incluidos en Git.

No añadir contraseñas reales a las pruebas ni a los informes.

### 6.3. Hash de contraseña

Utiliza un algoritmo moderno y adecuado para almacenar contraseñas, preferentemente **Argon2id** si existe una biblioteca mantenida y compatible con el entorno.

Si decides emplear otra alternativa, justifícala con relación a seguridad, compatibilidad, mantenibilidad y dependencias.

No utilizar SHA-256 simple, MD5, SHA-1 ni otro hash rápido como mecanismo directo de almacenamiento de contraseñas.

El almacenamiento debe incluir los parámetros y la sal adecuados para permitir una verificación segura.

La verificación no deberá comparar contraseñas directamente ni revelar sus valores.

### 6.4. Configuración ausente

Si las credenciales administrativas no están configuradas:

- El acceso administrativo permanece deshabilitado.
- La aplicación pública continúa funcionando.
- Se presenta un mensaje administrativo seguro.
- No se habilita una contraseña temporal conocida.
- No se crea automáticamente una cuenta insegura.

La configuración del administrador podrá realizarse manualmente en una etapa de preparación del entorno, sin publicar secretos.

---

## 7. Funciones básicas de autenticación

Implementa contratos claros para:

- Verificar si existe configuración administrativa válida.
- Verificar un usuario y contraseña.
- Registrar autenticación exitosa en el estado de sesión.
- Consultar si la sesión actual está autenticada.
- Cerrar sesión y borrar sus marcadores de autenticación.
- Rechazar intentos con datos incompletos.
- Gestionar excepciones sin exponer información sensible.

La verificación deberá ser resistente a comparaciones inseguras y comportarse de manera razonablemente uniforme ante credenciales incorrectas.

No mostrar información que permita distinguir públicamente si existe un usuario determinado.

Evitar mensajes que expongan detalles internos de la configuración de credenciales.

---

## 8. Integración con Streamlit

### 8.1. Área pública

La búsqueda pública deberá permanecer disponible sin iniciar sesión.

Conservar todas las funcionalidades desarrolladas:

- Búsqueda por nombre.
- Coincidencias parciales.
- Paginación.
- Detalles y ubicaciones.
- Interfaz responsive.
- Gemini «Próximamente».
- Manejo de errores.

### 8.2. Sección administrativa

Incorporar la estructura visual inicial correspondiente a **Productos**, de acuerdo con la navegación y los bocetos aprobados.

La interfaz administrativa podrá mostrar inicialmente:

- Formulario Login cuando no existe una sesión autenticada.
- Identificación de acceso administrativo una vez autenticado.
- Botón Logout.
- Mensaje informativo de que las funciones de mantenimiento se implementarán en etapas posteriores.

No mostrar formularios operativos de mantenimiento.

### 8.3. Protección efectiva

La autorización debe validarse en Python, no solamente ocultando botones o pestañas mediante CSS.

Cualquier futura operación administrativa deberá requerir una sesión administrativa válida.

No utilizar claves de sesión manipulables desde controles públicos como sustituto de la verificación de credenciales.

No exponer secretos en elementos de interfaz, URLs, archivos estáticos ni mensajes de error.

---

## 9. Administración exclusivamente desde computadora

El concepto aprobado establece que la administración se realizará exclusivamente desde la interfaz web de escritorio.

La sección pública seguirá disponible en teléfono y tableta.

Evalúa cómo cumplir esta restricción sin depender de controles meramente cosméticos.

Una regla CSS que oculte la pestaña administrativa en pantallas móviles no constituye protección de seguridad suficiente.

Si la versión de Streamlit y la arquitectura actual no permiten demostrar de forma fiable el tipo de dispositivo o imponer una restricción de servidor, documenta esta limitación y mantén la autenticación obligatoria para todas las operaciones administrativas.

No afirmes haber implementado una restricción segura de dispositivo si solo se ocultó la interfaz.

No agregar servicios externos, JavaScript personalizado ni mecanismos invasivos de identificación de dispositivos sin autorización.

La validación completa de acceso de escritorio puede quedar como criterio pendiente si requiere decisiones técnicas adicionales.

---

## 10. Preparación para el Prompt 08

Organiza la autenticación de forma modular para integrar posteriormente:

- Contadores de intentos fallidos.
- Bloqueos progresivos.
- Marca de tiempo de última actividad.
- Expiración por inactividad.
- Renovación de sesión.
- Advertencia previa a la expiración.
- Conservación temporal de borradores.

No activar estos mecanismos en el Prompt 07 ni afirmar que ya están completos.

Deja un contrato claro para que el Prompt 08 pueda incorporarlos sin reemplazar innecesariamente el módulo de autenticación.

No utilizar almacenamiento exclusivamente en `st.session_state` para implementar más adelante políticas que requieran controles compartidos entre sesiones; registra esta consideración técnica para la siguiente etapa.

---

## 11. Pruebas automatizadas

Crear:

`04_Pruebas/test_07_autenticacion_administrativa.py`

### 11.1. Pruebas de seguridad

Verificar:

1. Configuración administrativa válida.
2. Configuración inexistente.
3. Contraseña correcta.
4. Contraseña incorrecta.
5. Usuario incorrecto.
6. Usuario vacío.
7. Contraseña vacía.
8. Hash y verificación mediante el algoritmo seleccionado.
9. Ausencia de contraseñas en texto plano dentro del repositorio.
10. Ausencia de credenciales reales en mensajes de error.
11. Acceso administrativo denegado cuando no hay autenticación.
12. Cierre de sesión.
13. Aislamiento entre dos sesiones independientes.
14. Imposibilidad de convertir un marcador público de sesión en autorización administrativa sin verificación.

### 11.2. Pruebas de Streamlit

Utilizar `AppTest` cuando resulte adecuado.

Comprobar:

- La aplicación pública inicia sin credenciales administrativas.
- Se puede consultar el buscador sin iniciar sesión.
- El formulario Login aparece en la sección correspondiente.
- Credenciales incorrectas no conceden acceso.
- Una autenticación correcta habilita únicamente la sección administrativa inicial.
- Logout revoca el acceso.
- Gemini permanece no operativo.
- No existen formularios de administración de inventario activos.

### 11.3. Pruebas de regresión

Ejecutar:

`python -m unittest discover -s 04_Pruebas -p "test_*.py" -v`

Verificar que los Prompts 02 a 06 no presenten regresiones.

La referencia anterior es de 110 pruebas reportadas como aprobadas; utiliza el número real obtenido en la nueva ejecución.

### 11.4. Pruebas de límites

No declarar aprobadas las reglas avanzadas del Prompt 08.

Identifica expresamente que la aplicación no estará lista para administrar datos reales hasta integrar y validar las protecciones de sesión y bloqueo pendientes.

---

## 12. Archivos autorizados

Se permite crear o modificar localmente:

- `03_Aplicacion/autenticacion.py`.
- `03_Aplicacion/app.py`.
- `03_Aplicacion/estilos.css`, solo para adaptar visualmente el acceso administrativo.
- `04_Pruebas/test_07_autenticacion_administrativa.py`.
- `05_Resultados/07_Resultado_Autenticacion_Administrativa.md`.
- `requirements.txt`, si se necesita incorporar una biblioteca de hashing segura y se justifica.

Se permite añadir archivos auxiliares estrictamente necesarios para pruebas y configuración segura, pero no archivos que contengan secretos reales.

### Archivos protegidos

No modificar:

- `GEMINI.md`.
- `AGENTS.md`.
- `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`.
- `01_Documentacion/02_Especificaciones_v0.md`.
- `03_Aplicacion/inventario.py`.
- `03_Aplicacion/github_inventario.py`.
- `03_Aplicacion/busqueda.py`.
- `03_Aplicacion/inventario.xlsx`.
- Los prompts existentes.
- Las pruebas e informes de las tareas anteriores.
- `README.md`, salvo autorización adicional.

Si necesitas modificar un archivo protegido, explica el motivo y solicita permiso previamente.

---

## 13. Operaciones prohibidas

Durante esta tarea no está autorizado:

- Crear, modificar o eliminar el inventario maestro.
- Guardar datos mediante GitHub API.
- Implementar CRUD administrativo.
- Crear usuarios adicionales.
- Publicar contraseñas, hashes reales de producción o tokens.
- Configurar secretos reales sin intervención del usuario.
- Implementar las políticas completas del Prompt 08.
- Activar Gemini API.
- Añadir ventas, precios, cantidades o carrito.
- Crear una PWA instalable.
- Desplegar la aplicación.
- Ejecutar `git commit`, `git push` o `git merge`.
- Crear pull requests.
- Modificar documentos oficiales.
- Iniciar el Prompt 08 automáticamente.

---

## 14. Trazabilidad obligatoria

Cumple `AGENTS.md`.

Registrar:

- `TASK_ID`: FERMS-V0-P07.
- Fecha y hora reales.
- Solicitud original del usuario.
- Interpretación del agente.
- Acciones realizadas.
- Archivos modificados y creados.
- Algoritmo y dependencias de hashing seleccionados.
- Decisiones técnicas de autenticación.
- Requisitos y criterios relacionados.
- Pruebas ejecutadas.
- Limitaciones de protección aún pendientes.
- Evidencias disponibles.
- Commit base.
- Estado Git final.

Distinguir seguridad implementada de seguridad todavía pendiente.

No incluir contraseñas, hashes de producción ni tokens en la trazabilidad.

---

## 15. Informe de resultados

Crear:

`05_Resultados/07_Resultado_Autenticacion_Administrativa.md`

El informe deberá incluir:

### A. Objetivo y alcance

Funciones implementadas y responsabilidades reservadas para el Prompt 08.

### B. Arquitectura

Descripción del módulo de autenticación, contratos y separación frente a la interfaz pública.

### C. Credenciales y hashing

Algoritmo utilizado, dependencias, configuración segura y tratamiento de errores.

No incluir secretos reales.

### D. Interfaz administrativa

Descripción de Login, Logout y estado administrativo inicial.

### E. Pruebas

| Verificación | Resultado | Evidencia |
|---|---|---|
| Configuración segura | | |
| Hash y verificación | | |
| Login válido | | |
| Login inválido | | |
| Acceso sin autenticación | | |
| Logout | | |
| Aislamiento entre sesiones | | |
| Funcionamiento público sin login | | |
| Restricción de acceso desde escritorio | | |
| Ausencia de operaciones administrativas activas | | |
| Regresión Prompts 02–06 | | |

### F. Restricciones y pendientes

Distinguir los controles pendientes del Prompt 08 y las funciones de mantenimiento del Prompt 09.

### G. Evaluación

Utilizar:

- COMPLETADO.
- COMPLETADO CON OBSERVACIONES.
- INCOMPLETO.

Justificar el estado con evidencias.

---

## 16. Condiciones de finalización

La tarea podrá considerarse terminada cuando:

1. Exista un módulo de autenticación separado.
2. Se verifiquen contraseñas mediante un mecanismo seguro de hash.
3. No existan credenciales administrativas reales dentro del repositorio.
4. Funcione la autenticación básica.
5. Funcione el cierre de sesión.
6. El acceso administrativo permanezca protegido.
7. El buscador público continúe funcionando sin autenticación.
8. Se haya preparado la integración posterior de los controles del Prompt 08.
9. No se hayan implementado operaciones de modificación de inventario.
10. Se hayan ejecutado y documentado pruebas.
11. Se hayan identificado claramente las limitaciones de seguridad pendientes.
12. Los módulos y documentos protegidos permanezcan sin modificaciones.
13. Se entregue el informe completo y el estado final de Git.
14. El agente espere autorización para continuar.

**No ejecutar el Prompt 08.**