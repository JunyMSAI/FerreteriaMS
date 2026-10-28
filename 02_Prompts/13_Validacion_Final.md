# PROMPT 13 — Validación Final y Cierre de FerreteríaMS v0

**Proyecto:** FerreteríaMS v0  
**TASK_ID:** FERMS-V0-P13  
**TASK_TITLE:** Validación final y cierre de entrega  

---

## 1. Objetivo

Determinar si FerreteríaMS v0 está lista para su entrega, utilizando las evidencias existentes y verificando exclusivamente las funcionalidades pendientes o modificadas recientemente.

La prioridad es completar el cierre sin repetir pruebas, análisis o revisiones que ya fueron aprobados.

**No desarrollar nuevas funcionalidades.**

## 2. Documentos de referencia

Consultar únicamente lo necesario de:

- `GEMINI.md`
- `AGENTS.md`
- `01_Documentacion/02_Especificaciones_v0.md`
- `05_Resultados/11_Resultado_Integracion_Seguridad.md`
- `05_Resultados/12_Resultado_Despliegue_Streamlit_Cloud.md`
- Código y pruebas relacionados con la última corrección del formulario de edición.

Utilizar también la evidencia disponible del despliegue y las pruebas reales de Streamlit Cloud.

No reabrir decisiones conceptuales previamente aprobadas.

## 3. Estado funcional que debe comprobarse

Consolidar la evidencia disponible de las siguientes capacidades:

| Área | Comprobación requerida |
|---|---|
| Inicio de aplicación | Streamlit Cloud inicia correctamente |
| Búsqueda pública | Localiza productos por nombre |
| Localización | Presenta rack, columna, nivel y posición |
| Inventario | Lee el Excel oficial desde GitHub |
| Administración | Autenticación y protección de sesión |
| Crear producto | Permite utilizar categorías y ubicaciones existentes |
| Editar producto | Muestra los datos del producto seleccionado |
| Guardado | Publica cambios mediante GitHub Contents API |
| Persistencia | Los cambios quedan almacenados en el archivo maestro |
| Gemini | Permanece exclusivamente como «Próximamente» |

Distinguir explícitamente entre funcionalidades comprobadas en pruebas automatizadas, verificadas en Streamlit Cloud y todavía pendientes de confirmación.

No declarar una prueba real aprobada cuando únicamente existe evidencia simulada.

## 4. Validación focalizada de la última corrección

Revisar exclusivamente la sincronización del formulario de edición de productos en:

`03_Aplicacion/app.py`

Comprobar que:

1. Al seleccionar un producto diferente, aparecen sus datos correspondientes.
2. Los campos editables no conservan valores del producto anterior.
3. El código único permanece inmutable.
4. Los cambios escritos no se pierden durante la edición del mismo producto.
5. La corrección no afecta la confirmación de cambios locales.

Utilizar las pruebas existentes actualizadas. No repetir suites completas sin justificación técnica.

Si el inventario publicado contiene un único producto, utilizar pruebas automatizadas con dos productos simulados; no modificar el inventario real solo para realizar esta comprobación.

## 5. Persistencia real en GitHub

Comprobar mediante evidencia existente o lectura no destructiva:

- Que `03_Aplicacion/inventario.xlsx` existe en la rama `main`.
- Que el producto `TEST001`, utilizado en la prueba de evaluación, está almacenado en el archivo maestro.
- Que la búsqueda pública mostró el producto y su ubicación.
- Que la aplicación conserva controles administrativos, confirmación explícita y concurrencia mediante SHA.
- Que el token no aparece en archivos versionados ni en informes.

No modificar el inventario ni realizar nuevas operaciones HTTP PUT.

Si la evidencia existente no es suficiente para confirmar alguna condición, clasificarla como pendiente; no inventar resultados.

## 6. Seguridad y limitaciones

Confirmar solamente los aspectos afectados desde P11 y P12.

Registrar las limitaciones ya conocidas, especialmente:

- Catálogos de categorías y ubicaciones predefinidos en el Excel.
- Administración de esos catálogos desde la interfaz no incluida en v0.
- Borradores y sesiones sujetos a las características del almacenamiento temporal de Streamlit.
- Gemini API no integrada.
- Cualquier limitación funcional comprobada durante la evaluación.

No considerar como defectos de entrega las funcionalidades expresamente excluidas del alcance aprobado.

## 7. Política de verificación eficiente

Aplicar obligatoriamente:

- No repetir las 266 pruebas anteriores.
- No ejecutar auditorías generales.
- No refactorizar módulos estables.
- No modificar componentes ajenos a la última corrección.
- No realizar mejoras cosméticas.
- No crear funcionalidades nuevas.
- Ejecutar pruebas adicionales únicamente cuando exista un fallo real o un riesgo directamente relacionado con un cambio reciente.

Si aparece un fallo crítico, documentarlo y aplicar únicamente la corrección mínima autorizada por las instrucciones del proyecto.

Si requiere modificar requisitos aprobados o ampliar el alcance, solicitar autorización antes de actuar.

## 8. Informe final

Crear:

`05_Resultados/13_Resultado_Validacion_Final.md`

Incluir:

1. Resumen ejecutivo del estado de FerreteríaMS v0.
2. Tabla breve de funcionalidades y estado de aceptación.
3. Evidencias existentes reutilizadas.
4. Verificaciones nuevas efectivamente ejecutadas.
5. Defectos críticos pendientes, si existen.
6. Limitaciones aceptadas y funcionalidades futuras.
7. Relación de archivos modificados.
8. `git status --short`.
9. Conclusión: **APTA PARA ENTREGA**, **APTA CON LIMITACIONES DOCUMENTADAS** o **NO APTA POR BLOQUEOS CRÍTICOS**, con justificación.

Completar los campos obligatorios de trazabilidad: `TASK_ID`, `TASK_DATE`, `TASK_TIME`, `TASK_LEVEL`, `TASK_TITLE`, `USER_REQUEST_ORIGINAL`, `CODEX_UNDERSTANDING` y `CODEX_ACTIONS_TAKEN`.

Actualizar el historial de tareas únicamente si corresponde según `AGENTS.md`.

## 9. Restricciones

No está autorizado:

- Modificar `inventario.xlsx`.
- Realizar publicaciones mediante GitHub API.
- Mostrar, copiar o registrar secretos.
- Cambiar permisos del token.
- Ejecutar despliegues.
- Crear nuevas funcionalidades.
- Comenzar el desarrollo de futuras versiones.
- Ejecutar `git add`, `git commit`, `git push`, `git reset`, `git restore` o `git clean`.

## 10. Cierre

Al completar la verificación:

- Entregar el informe final.
- Identificar únicamente los bloqueos reales de entrega.
- Presentar recomendaciones mínimas, si fueran indispensables.
- Detenerse para aprobación del responsable.

No iniciar automáticamente `03_Especificaciones_Final.md`.

**Fin del Prompt 13, No comiences el Prompt 14.**