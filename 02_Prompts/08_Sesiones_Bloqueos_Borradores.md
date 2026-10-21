# PROMPT 08 — Gestión avanzada de sesiones, bloqueos y borradores

**Proyecto:** FerreteríaMS v0  
**TASK_ID:** `FERMS-V0-P08`  
**Etapa:** Seguridad administrativa avanzada  
**Agente:** Antigravity dentro de VS Code  
**Repositorio:** `JunyMSAI/FerreteriaMS`  
**Rama:** `main`  
**Directorio local:** `C:\Projects\FerreteriaMS`  
**Archivo:** `02_Prompts/08_Sesiones_Bloqueos_Borradores.md` 

---

## 1. Objetivo general

Completar los mecanismos avanzados de seguridad administrativa de FerreteríaMS v0 sobre el módulo de autenticación implementado y corregido durante el Prompt 07.

Desarrollar, integrar y probar:

1. Control de intentos fallidos consecutivos.
2. Bloqueos temporales progresivos.
3. Expiración administrativa por inactividad.
4. Advertencia previa a la expiración.
5. Renovación explícita de sesión.
6. Conservación y recuperación temporal de borradores no guardados.
7. Revocación efectiva de sesiones expiradas.
8. Limpieza y límites de los registros de seguridad del servidor.

La cuenta administrativa sigue siendo única.

**No implementar en esta etapa formularios CRUD ni escrituras sobre el inventario maestro.**

---

## 2. Lectura y verificación previa

Leer íntegramente:

- `GEMINI.md`.
- `AGENTS.md`.
- `01_Documentacion/01_Concepto_FerreteriaMS_Final.docx`.
- `01_Documentacion/02_Especificaciones_v0.md`.
- `02_Prompts/07_Autenticacion_Administrativa.md`.
- `05_Resultados/07_Resultado_Autenticacion_Administrativa.md`.
- Este Prompt 08.

Revisar las implementaciones y pruebas existentes:

- `03_Aplicacion/autenticacion.py`.
- `03_Aplicacion/app.py`.
- `03_Aplicacion/estilos.css`.
- `04_Pruebas/test_07_autenticacion_administrativa.py`.
- Los módulos y pruebas de los Prompts 02 a 06.

Verificar que el repositorio esté limpio y registrar el commit base.

Si existen modificaciones inesperadas pendientes, detenerse y solicitar indicaciones.

No modificar las especificaciones oficiales.

### Revisión obligatoria de seguridad existente

Antes de diseñar las ampliaciones, comprender especialmente:

- Verificación Argon2id.
- `ComprobanteVerificacionCredenciales`.
- Comprobantes criptográficos de un solo uso.
- `_COMPROBANTES_VERIFICACION_SERVIDOR`.
- `_SESIONES_ACTIVAS_SERVIDOR`.
- `EstadoSesionAdmin`.
- Firma HMAC.
- `iniciar_sesion_admin()`.
- `registrar_autenticacion_en_sesion()`.
- `esta_autenticado_en_sesion()`.
- `requerir_autorizacion_admin()`.
- `cerrar_sesion_admin()`.

No eliminar ni debilitar los controles corregidos durante el Prompt 07.

---

## 3. Requisitos oficiales

Identificar y verificar en `02_Especificaciones_v0.md` los requisitos y criterios exactos que regulan:

- Cinco intentos consecutivos fallidos.
- Bloqueos progresivos de 5/10/20/30 minutos.
- Máximo de 30 minutos.
- Reinicio del contador tras autenticación exitosa.
- Sesión de 15 minutos.
- Aviso dos minutos antes de la expiración.
- Renovación mediante botón.
- Retención de borradores por 15 minutos adicionales.
- Restricción administrativa a computadoras.
- Seguridad del acceso administrativo.

Consultar especialmente `CA-030`, `CA-052`, `CA-053`, `CA-054`, `CA-055`, `CA-056`, `CA-057`, `CA-058` y `CA-059`, según las definiciones exactas del documento.

No reinterpretar los criterios ni modificar sus valores.

Cuando una condición técnica no esté completamente determinada por la documentación, distinguirla como una decisión de implementación y justificarla.

---

## 4. Política de intentos fallidos

### 4.1. Regla general

Aplicar bloqueo cuando se acumulen **cinco intentos de autenticación fallidos consecutivos**.

Los intentos fallidos comprenden credenciales incorrectas, conforme a la definición y reglas oficiales.

No registrar contraseñas introducidas ni exponer hashes en mensajes de error.

### 4.2. Bloqueo progresivo

Implementar la siguiente progresión:

| Bloqueo consecutivo | Duración |
|---|---|
| Primero | 5 minutos |
| Segundo | 10 minutos |
| Tercero | 20 minutos |
| Cuarto y posteriores | 30 minutos |

El tiempo máximo será de 30 minutos.

Al finalizar un bloqueo, se permitirá una nueva serie de intentos conforme a la progresión aprobada.

No reiniciar silenciosamente el nivel de progresión si el administrador continúa fallando después de cumplir un bloqueo.

### 4.3. Inicio exitoso

Tras autenticación satisfactoria:

- Reiniciar el contador de intentos fallidos consecutivos.
- Reiniciar la progresión de bloqueos según las especificaciones aprobadas.
- Registrar una sesión autenticada válida.
- No revelar información sensible en el mensaje de éxito.

### 4.4. Acceso durante bloqueo

Durante un bloqueo activo:

- Denegar cualquier intento de autenticación, incluso con contraseña correcta.
- No emitir comprobantes nuevos.
- No crear sesiones administrativas.
- Mostrar un aviso comprensible con la condición de bloqueo.
- No permitir que otra pestaña o sesión evite el bloqueo.
- Aplicar la comprobación antes de realizar operaciones costosas de verificación de contraseña cuando sea seguro hacerlo.

No utilizar el navegador como autoridad para calcular el fin del bloqueo.

---

## 5. Estado compartido de seguridad

La política de bloqueo debe ser compartida entre las sesiones relevantes del servidor.

No guardar el contador de intentos fallidos únicamente en `st.session_state`.

Revisar el almacenamiento existente en memoria del proceso y determinar si puede satisfacer las condiciones del MVP en el entorno previsto.

### Condiciones obligatorias

- Un intento fallido desde una sesión debe afectar a las demás sesiones del administrador.
- Abrir una nueva pestaña no debe reiniciar el bloqueo.
- Las actualizaciones del contador deben realizarse de manera consistente ante operaciones concurrentes.
- Las consultas y cambios del estado deben estar protegidos frente a condiciones de carrera.
- No se debe aceptar un contador aportado por el cliente como autoridad.

### Limitaciones del despliegue

Reconocer expresamente que un diccionario global de Python solo comparte datos dentro del mismo proceso.

No afirmar persistencia entre reinicios o múltiples procesos si no existe un mecanismo que realmente la garantice.

Si para cumplir el requisito en el despliegue final fuera imprescindible adoptar almacenamiento adicional o modificar la arquitectura, documentar la limitación y solicitar autorización antes de incorporar un servicio o dependencia.

No introducir SQLite, Redis, Supabase ni otro servicio de almacenamiento de seguridad sin autorización previa.

---

## 6. Expiración por inactividad

### 6.1. Duración

Una sesión administrativa debe expirar después de **15 minutos de inactividad**.

La autoridad temporal debe estar en el servidor.

El cliente no debe poder prolongar una sesión alterando valores en `st.session_state`.

### 6.2. Registro de actividad

Definir claramente qué eventos constituyen actividad administrativa legítima.

Evitar actualizar automáticamente la última actividad ante:

- Recargas pasivas.
- Re-renderizados sin interacción.
- Comprobaciones periódicas de estado.
- Solicitudes automatizadas destinadas únicamente a actualizar la interfaz.

No permitir que un mecanismo de actualización visual mantenga una sesión indefinidamente activa.

### 6.3. Revocación

Cuando la sesión expire:

- Invalidar el token administrativo en el registro del servidor.
- Rechazar las operaciones administrativas protegidas.
- Limpiar el estado de autenticación de la sesión.
- Volver a solicitar credenciales.
- Mantener el acceso público disponible.

No limitarse a ocultar visualmente el panel administrativo.

---

## 7. Advertencia previa

Mostrar una advertencia **dos minutos antes** de que expire la sesión por inactividad.

Esto corresponde al minuto 13 de una sesión sin nueva actividad.

El aviso debe:

- Informar claramente que la sesión está próxima a expirar.
- Permitir comprender cuánto tiempo queda aproximadamente.
- Presentar la opción de renovar la sesión.
- No exponer secretos.
- Ser accesible mediante teclado.
- No bloquear permanentemente la navegación pública.

### Consideración específica de Streamlit

Investigar y verificar qué comportamiento real ofrece la versión instalada de Streamlit para actualizar la interfaz cuando el usuario no interactúa.

No declarar que la advertencia aparece automáticamente al minuto 13 si solo se evaluó la condición durante un re-renderizado provocado manualmente.

Si una actualización automática requiere una capacidad compatible con Streamlit, evaluar primero soluciones nativas y mantenidas.

No incorporar JavaScript personalizado ni dependencias adicionales sin justificar y solicitar autorización cuando resulte necesario.

Si no es posible garantizar un aviso automático con los mecanismos autorizados, registrar el requisito como parcialmente implementado y explicar exactamente qué queda pendiente.

---

## 8. Renovación de sesión

Implementar un botón identificado como:

**Continuar sesión**

Su finalidad es renovar la sesión antes de que expire.

### Reglas

- Debe estar disponible únicamente cuando exista autorización válida y no expirada.
- La renovación debe registrarse en el servidor.
- No debe aceptar marcas temporales proporcionadas por el cliente.
- Debe comprobar que la sesión no haya sido revocada.
- Debe respetar la política de autenticación existente.
- Debe mantener la sesión administrativa sin crear permisos adicionales.
- Debe conservar el aislamiento entre sesiones.

Una sesión ya expirada no puede renovarse simplemente pulsando el botón: debe volver a autenticarse.

---

## 9. Conservación temporal de borradores

### 9.1. Objetivo

Preparar un mecanismo que conserve temporalmente los datos de un formulario administrativo que todavía no se hayan guardado cuando expire la sesión.

La documentación aprobada exige **15 minutos adicionales de retención temporal**.

### 9.2. Alcance en el Prompt 08

Los formularios CRUD todavía no existirán hasta el Prompt 09.

Por tanto, implementar un mecanismo genérico, independiente de formularios concretos, que pueda:

- Registrar un borrador en memoria temporal.
- Asociarlo a la sesión y cuenta administrativa correspondientes.
- Conservándolo al expirar una sesión, sin mantener autorización.
- Consultarlo únicamente tras una nueva autenticación válida.
- Restaurarlo durante la ventana temporal permitida.
- Descartarlo cuando venza la retención.
- Eliminarlo de forma segura cuando corresponda.

Probarlo mediante datos sintéticos.

**No crear formularios de productos ni modificar inventario.xlsx.**

### 9.3. Seguridad

Evitar:

- Restaurar borradores a otra cuenta o sesión no autorizada.
- Mantener el borrador indefinidamente.
- Confundir un borrador con datos guardados.
- Conceder autorización administrativa por existir un borrador.
- Almacenar contraseñas, tokens o secretos dentro de los borradores.
- Recuperar borradores durante una sesión bloqueada o no autenticada.

Determinar y documentar el comportamiento de los borradores ante Logout voluntario, de acuerdo con el concepto aprobado o, cuando no esté especificado, como decisión técnica explícita.

### 9.4. Persistencia

El mecanismo puede utilizar almacenamiento temporal del servidor adecuado para el alcance actual, pero debe documentar qué sucede ante reinicios y múltiples procesos.

No prometer persistencia frente a un reinicio del servidor si no existe realmente.

---

## 10. Limpieza de registros y consumo de memoria

Implementar mantenimiento controlado de los registros de seguridad existentes.

Como mínimo:

- Limpiar comprobantes de verificación expirados.
- Impedir reutilizar comprobantes ya consumidos.
- Limpiar sesiones expiradas o revocadas.
- Depurar borradores vencidos.
- Gestionar el estado de bloqueos finalizados.
- Evitar crecimiento ilimitado de estructuras temporales.
- Definir límites razonables y verificables para registros efímeros.

Evitar que la limpieza de registros elimine accidentalmente un bloqueo activo o permita eludir el nivel progresivo de bloqueo.

Documentar las garantías reales de concurrencia dentro del proceso.

---

## 11. Integración con la interfaz administrativa

Modificar la interfaz de `Productos` solo en lo necesario para integrar:

- Estado de sesión válido.
- Mensaje de bloqueo.
- Aviso de próxima expiración.
- Botón «Continuar sesión».
- Redirección al formulario Login cuando expire la sesión.
- Mensajes adecuados de reautenticación y recuperación de borradores.

Mantener intacta la experiencia pública de búsqueda.

No crear todavía formularios de mantenimiento.

Gemini seguirá identificado como «Próximamente», sin llamadas a IA.

Las políticas de sesión deben comprobarse en Python y no depender exclusivamente de CSS o de controles visuales.

---

## 12. Pruebas automatizadas

Crear:

`04_Pruebas/test_08_sesiones_bloqueos_borradores.py`

### Pruebas de bloqueo

Cubrir:

1. Primer intento fallido.
2. Cuatro intentos fallidos sin bloqueo.
3. Quinto intento y primer bloqueo de cinco minutos.
4. Segundo bloqueo de diez minutos.
5. Tercer bloqueo de veinte minutos.
6. Cuarto bloqueo de treinta minutos.
7. Bloqueos posteriores sin exceder treinta minutos.
8. Contraseña correcta durante bloqueo activo.
9. Finalización del bloqueo.
10. Reinicio de contadores después de login exitoso.
11. Intentos distribuidos entre dos sesiones.
12. Protección ante intentos concurrentes.
13. Ausencia de emisión de comprobantes durante bloqueo.

### Pruebas de sesión

Cubrir:

14. Sesión recién autenticada.
15. Actividad administrativa legítima.
16. Inactividad inferior a quince minutos.
17. Advertencia al minuto trece.
18. Expiración al minuto quince.
19. Revocación real del token expirado.
20. Rechazo de operaciones después de expirar.
21. Renovación antes de la expiración.
22. Rechazo de renovación después de expirar.
23. Separación entre sesiones independientes.
24. Comportamiento ante re-renderizados pasivos.

### Pruebas de borradores

Cubrir:

25. Guardar un borrador temporal.
26. Retenerlo después de expirar la sesión.
27. Reautenticarse y restaurarlo durante la ventana permitida.
28. Rechazar recuperación sin autenticación.
29. Rechazar recuperación desde una cuenta o contexto no autorizado.
30. Expirar y eliminar borradores después de quince minutos adicionales.
31. Manejo de Logout voluntario.
32. Aislamiento de borradores entre sesiones.

### Pruebas de integración y robustez

Cubrir:

33. Limpieza de registros expirados.
34. Comprobantes de un solo uso del Prompt 07.
35. Uso de Argon2id sin degradación.
36. Rechazo de marcadores de sesión falsificados.
37. Aplicación pública disponible durante bloqueo administrativo.
38. No implementación de CRUD o escritura remota.
39. Gemini visual no operativo.
40. Compatibilidad de las pruebas existentes.

Utilizar relojes simulados o inyectables para probar temporizaciones sin esperar minutos reales.

No depender de cambios en el reloj del sistema operativo.

### Regresión completa

Ejecutar:

`python -m unittest discover -s 04_Pruebas -p "test_*.py" -v`

El último resultado reportado para los Prompts 02–07 fue de **132 pruebas aprobadas**.

Ese total es una referencia y no debe sustituir la cantidad real obtenida al finalizar el Prompt 08.

---

## 13. Verificaciones reales de Streamlit

Ejecutar localmente:

`streamlit run 03_Aplicacion/app.py`

Comprobar los mecanismos que puedan verificarse realmente.

Distinguir estrictamente:

- **Prueba unitaria con tiempo simulado.**
- **Prueba de integración con AppTest.**
- **Verificación real de Streamlit en navegador.**
- **Comportamiento pendiente de comprobar con tiempo real y navegador abierto.**

No afirmar haber demostrado una advertencia automática tras trece minutos reales si únicamente se simularon valores temporales.

No crear credenciales administrativas de producción.

---

## 14. Archivos autorizados

Se permite crear o modificar localmente:

- `03_Aplicacion/autenticacion.py`.
- `03_Aplicacion/app.py`.
- `03_Aplicacion/estilos.css`, si es necesario.
- Un módulo auxiliar para sesiones o borradores, si está técnicamente justificado.
- `04_Pruebas/test_08_sesiones_bloqueos_borradores.py`.
- `05_Resultados/08_Resultado_Sesiones_Bloqueos_Borradores.md`.

Si una dependencia adicional fuese imprescindible, justificarla y solicitar autorización antes de modificar `requirements.txt`.

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
- Prompts anteriores.
- Pruebas e informes de Prompts 02–07.
- `README.md`.
- `requirements.txt`, sin autorización adicional.

No cambiar la arquitectura aprobada sin solicitar autorización.

---

## 15. Restricciones expresas

Queda prohibido:

- Crear o modificar el inventario maestro.
- Incorporar CRUD administrativo.
- Realizar escrituras mediante GitHub API.
- Crear usuarios administrativos adicionales.
- Añadir roles no aprobados.
- Implementar Gemini API funcional.
- Crear transacciones comerciales.
- Introducir servicios de almacenamiento externos sin autorización.
- Publicar credenciales o hashes de producción.
- Ejecutar commits o push.
- Ejecutar merge o crear pull requests.
- Realizar despliegues.
- Modificar las especificaciones o el concepto.
- Comenzar el Prompt 09 automáticamente.

---

## 16. Trazabilidad obligatoria

Cumplir íntegramente `AGENTS.md`.

Registrar:

- `TASK_ID`: FERMS-V0-P08.
- Fecha y hora reales.
- Nivel de tarea.
- Solicitud original íntegra o referencia verificable.
- Interpretación del agente.
- Acciones realizadas.
- Archivos creados y modificados.
- Decisiones técnicas de temporización.
- Estrategia de almacenamiento temporal.
- Gestión de concurrencia.
- Limitaciones en reinicios y múltiples procesos.
- Requisitos y criterios relacionados.
- Pruebas y evidencias.
- Estado del repositorio al finalizar.
- Commit base.
- Aspectos pendientes.

No incluir secretos ni tokens reales.

---

## 17. Informe de resultados

Crear:

`05_Resultados/08_Resultado_Sesiones_Bloqueos_Borradores.md`

Con los apartados:

### A. Objetivo y alcance

Alcance implementado y restricciones respetadas.

### B. Arquitectura de seguridad

Registros, sesiones, concurrencia y revocación.

### C. Bloqueos

Tabla de progresión con evidencias.

### D. Inactividad y renovación

Expiración, advertencias y comportamiento del botón.

### E. Borradores

Creación, retención, restauración y eliminación.

### F. Pruebas

| Verificación | Resultado | Evidencia |
|---|---|---|
| Cinco intentos fallidos | | |
| Primer bloqueo: 5 min | | |
| Segundo bloqueo: 10 min | | |
| Tercer bloqueo: 20 min | | |
| Cuarto bloqueo: 30 min | | |
| Expiración de sesión | | |
| Advertencia al minuto 13 | | |
| Renovación de sesión | | |
| Borrador retenido | | |
| Borrador restaurado | | |
| Borrador eliminado tras caducidad | | |
| Aislamiento de sesiones | | |
| Concurrencia | | |
| Regresión de Prompts 02–07 | | |

### G. Limitaciones y pendientes

Diferenciar pruebas simuladas, integradas, reales y pendientes.

### H. Evaluación final

Elegir:

- COMPLETADO.
- COMPLETADO CON OBSERVACIONES.
- INCOMPLETO.

Justificar el resultado según las evidencias.

---

## 18. Condiciones de finalización

La tarea se considerará terminada cuando:

1. Se apliquen cinco intentos consecutivos fallidos.
2. Se respeten bloqueos progresivos de 5, 10, 20 y 30 minutos.
3. Se aplique un máximo de 30 minutos.
4. Un login exitoso reinicie los contadores según el concepto aprobado.
5. Los bloqueos no puedan eludirse abriendo otra sesión dentro de las garantías documentadas.
6. La sesión expire a los 15 minutos de inactividad.
7. Los tokens expirados queden revocados.
8. Exista un mecanismo de advertencia previa conforme a las capacidades realmente verificadas.
9. «Continuar sesión» renueve únicamente sesiones válidas.
10. Los borradores tengan retención temporal limitada.
11. No se debilite Argon2id ni la verificación criptográfica del Prompt 07.
12. La búsqueda pública siga disponible.
13. Se ejecuten las pruebas del Prompt 08 y la regresión completa.
14. Se documenten las limitaciones reales del almacenamiento y despliegue.
15. No se modifique ningún archivo protegido sin autorización.
16. No se ejecuten commits, push ni despliegues.
17. Se entregue el informe de trazabilidad y el agente espere revisión.

**No ejecutar el Prompt 09.**