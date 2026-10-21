# Informe de Resultados — Prompt 11: Integración, Seguridad y Preparación para Despliegue en Streamlit Community Cloud

**Proyecto:** FerreteríaMS  
**Etapa:** FerreteríaMS v0  
**Identificador de la tarea:** `FERMS-V0-P11`  
**Fecha de ejecución:** 21 de octubre de 2026  
**Título de la tarea:** Integración y seguridad para entrega urgente y preparación para despliegue en Streamlit Community Cloud  
**Documento prompt de origen:** `02_Prompts/11_Integracion_Seguridad.md`  
**Rama de trabajo:** `main`  
**Commit funcional base (P10):** `ae1d44b` (`Prompt 10 completado`)  
**Commit documental actual (P11):** `3e46aa5` (`prompt "11_Integracion_Seguridad" incluido`)  
**Agente de desarrollo:** Gemini  

---

## 1. Solicitud / Prompt Original

### 1.1. Instrucción de ejecución recibida del usuario (conservada íntegramente sin alteraciones)

```markdown
**FERMS-V0-P11 — AUTORIZACIÓN DE EJECUCIÓN**

Proyecto: FerreteríaMS v0.

Ejecuta exclusivamente el documento oficial:

`02_Prompts/11_Integracion_Seguridad.md`

Antes de comenzar:

1. Lee `GEMINI.md`, `AGENTS.md`, las especificaciones oficiales y el informe P10.
2. Confirma que estás en la rama `main`, que el documento P11 está registrado en el commit actual y que el árbol de trabajo está limpio.
3. Si encuentras modificaciones inesperadas, detente.

**Prioridad: entrega urgente.**

Realiza primero las verificaciones de integración y seguridad utilizando las pruebas existentes P02–P10. Evita refactorizaciones, mejoras cosméticas o funcionalidades nuevas.

Corrige únicamente defectos críticos comprobados que afecten la funcionalidad, seguridad o despliegue.

**Restricciones obligatorias:**
- No utilizar credenciales reales durante las pruebas.
- No activar escrituras reales de GitHub.
- No crear ni modificar `03_Aplicacion/inventario.xlsx`.
- No desplegar en Streamlit Cloud.
- No ejecutar `git add`, `git commit` ni `git push`.
- No iniciar P12.

Documenta los resultados en:

`05_Resultados/11_Resultado_Integracion_Seguridad.md`

Al finalizar, presenta el resultado de las pruebas, los riesgos pendientes y `git status --short`.

Detente y espera mi revisión y autorización.
```

### 1.2. Referencia al documento oficial del Prompt 11

El texto íntegro del prompt se conserva sin alteraciones en `02_Prompts/11_Integracion_Seguridad.md` (commit `3e46aa5`).

---

## 2. Interpretación del Agente

1. **Verificaciones iniciales de gobernanza y estado del repositorio:**
   - Se leyeron íntegramente `GEMINI.md`, `AGENTS.md`, `01_Documentacion/02_Especificaciones_v0.md`, `05_Resultados/10_Resultado_Persistencia_Inventario_GitHub.md` y `02_Prompts/11_Integracion_Seguridad.md`.
   - Se verificó que la rama activa es `main`, que el commit actual `3e46aa5` registra `02_Prompts/11_Integracion_Seguridad.md` y desciende directamente del commit base `ae1d44b` (`git merge-base --is-ancestor ae1d44b HEAD` con código de salida `0`), que el árbol de trabajo se encontraba completamente limpio al iniciar y que `03_Aplicacion/inventario.xlsx` no existe localmente.

2. **Alcance de verificación e integración (sin funcionalidades nuevas ni refactorizaciones):**
   - Ejecutar secuencialmente y sin paralelismo las 9 suites existentes (`P02` a `P10`) para comprobar la integración de extremo a extremo en simulación: inicio de la aplicación Streamlit, búsqueda pública y visualización de ubicaciones, autenticación administrativa con Argon2id, bloqueos progresivos, expiración/renovación de sesión y borradores, creación/edición local de productos y ubicaciones, serialización y *round-trip* de las 4 hojas Excel, persistencia simulada hacia GitHub Contents API, detección de conflictos `SHA`, actualización de búsquedas sin reiniciar Streamlit e interfaz responsive con sección Gemini exclusivamente «Próximamente».
   - Auditar los controles obligatorios de seguridad, aplicando únicamente endurecimientos críticos mínimos sobre `03_Aplicacion/persistencia_github.py` para garantizar la separación entre transporte real y ejecutores simulados sin modificar globalmente funciones de red, la marca de despacho por instancia y revocación automática de confirmación ante resultados de escritura ambiguos, y la resolución autónoma de `sys.path`.
   - Comprobar sin desplegar la preparación técnica para Streamlit Community Cloud y documentar la configuración pendiente.

---

## 3. Comandos Ejecutados y Resultados de Pruebas de Integración (P02–P10)

### 3.1. Comandos de verificación inicial de Git y entorno

```powershell
git branch --show-current
git log -n 3 --oneline
git status --short
git show --stat 3e46aa5
git merge-base --is-ancestor ae1d44b HEAD
```

- **Rama activa:** `main`
- **Historial reciente:**
  - `3e46aa5 prompt "11_Integracion_Seguridad" incluido`
  - `ae1d44b Prompt 10 completado`
  - `8ac0b7e promt "10_Persistencia_Inventario_GitHub" incluido`
- **Árbol de trabajo inicial:** limpio (sin archivos modificados ni sin seguimiento).

### 3.2. Ejecución secuencial de las suites existentes P02–P10

Comando ejecutado secuencialmente (sin paralelismo):

```powershell
python -m unittest 04_Pruebas/test_02_motor_inventario.py
python -m unittest 04_Pruebas/test_03_lectura_github.py
python -m unittest 04_Pruebas/test_04_busqueda_publica.py
python -m unittest 04_Pruebas/test_05_detalles_ubicaciones.py
python -m unittest 04_Pruebas/test_06_interfaz_responsive_gemini.py
python -m unittest 04_Pruebas/test_07_autenticacion_administrativa.py
python -m unittest 04_Pruebas/test_08_sesiones_bloqueos_borradores.py
python -m unittest 04_Pruebas/test_09_gestion_administrativa_productos_ubicaciones.py
python -m unittest 04_Pruebas/test_10_persistencia_inventario_github.py
```

| Etapa / Suite | Archivo de prueba | Casos ejecutados | Tiempo | Resultado | Cobertura de integración verificada |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **P02** | `04_Pruebas/test_02_motor_inventario.py` | 23 | 0.329s | **OK** | Esquema de 4 hojas (`Productos`, `Categorías`, `Ubicaciones`, `Asignaciones`), integridad referencial, preservación de códigos con ceros iniciales como texto, ubicación principal única. |
| **P03** | `04_Pruebas/test_03_lectura_github.py` | 21 | 0.448s | **OK** | Lectura simulada desde GitHub API, validación HTTPS y de dominios permitidos, extracción de `sha_github`, diferenciación entre inexistencia (`404`) y fallos técnicos. |
| **P04** | `04_Pruebas/test_04_busqueda_publica.py` | 25 | 1.822s | **OK** | Búsqueda pública exclusivamente por nombre, coincidencias parciales, normalización sin acentos ni distinción de mayúsculas, orden por relevancia, paginación de 10 resultados, búsqueda vacía y manejo de errores con reintento. |
| **P05** | `04_Pruebas/test_05_detalles_ubicaciones.py` | 23 | 5.685s | **OK** | Consulta de detalle de producto, visualización de `Rack`, `Columna`, `Nivel` y `Posición`, distinción entre ubicación principal y secundarias, retorno a resultados conservando página. |
| **P06** | `04_Pruebas/test_06_interfaz_responsive_gemini.py` | 18 | 8.474s | **OK** | Inicio de `03_Aplicacion/app.py`, adaptación responsive en computadora y móvil, sección visual de Gemini identificada exclusivamente como «Próximamente» sin exigir API key ni realizar llamadas a Gemini API. |
| **P07** | `04_Pruebas/test_07_autenticacion_administrativa.py` | 22 | 2.128s | **OK** | Login administrativo protegido en pestaña `Productos`, verificación de contraseñas con Argon2id (`argon2-cffi`), rechazo de texto plano y hashes débiles, restricción de acceso desde móvil. |
| **P08** | `04_Pruebas/test_08_sesiones_bloqueos_borradores.py` | 40 | 1.621s | **OK** | Cinco intentos fallidos consecutivos, bloqueos progresivos de 5, 10, 20 y 30 min, advertencia a los 13 min, expiración a los 15 min de inactividad, renovación con «Continuar sesión» y conservación temporal de borradores por 15 min adicionales. |
| **P09** | `04_Pruebas/test_09_gestion_administrativa_productos_ubicaciones.py` | 51 | 2.867s | **OK** | Creación y edición local de productos, inmutabilidad de `Codigo_Producto`, validación de categorías y ubicaciones predefinidas, cambio de ubicación principal y retiro de secundarias. |
| **P10** | `04_Pruebas/test_10_persistencia_inventario_github.py` | 43 | 6.831s | **OK** | Serialización `.xlsx` en memoria y *round-trip*, solicitudes `PUT` simuladas a GitHub Contents API, control de concurrencia por `SHA`, actualización de búsqueda pública sin reiniciar Streamlit, bloqueo de datos demostrativos y compuerta de escritura real deshabilitada. |
| **TOTAL** | **9 suites ejecutadas secuencialmente** | **266** | **30.205s** | **100% OK** | **Integración completa verificada en entorno simulado** |

---

## 4. Verificación de Seguridad Obligatoria, Defectos Críticos Corregidos y Archivos Afectados

### 4.1. Controles de seguridad verificados

1. **Ausencia de tokens, contraseñas y hashes incrustados en el código:**
   - Inspeccionados todos los módulos de `03_Aplicacion/` (`inventario.py`, `github_inventario.py`, `busqueda.py`, `autenticacion.py`, `administracion_productos.py`, `persistencia_github.py`, `app.py`) y archivos seguidos por Git (`git ls-files`). No existen tokens reales (`ghp_`, `github_pat_`, `gho_`, `ghs_`, `ghu_`), contraseñas reales ni hashes Argon2id reales incrustados.
2. **Protección de secretos en errores, registros e interfaz:**
   - `ocultar_secretos_en_texto`, `ocultar_secretos_autenticacion` y `sanitizar_texto_persistencia` redactan tokens, encabezados `Authorization`, contraseñas y hashes `$argon2id$` tanto en excepciones como en representaciones `__repr__` y `__str__` de objetos de estado y configuración.
3. **Reglas `.gitignore` para archivos sensibles:**
   - Verificado que `.gitignore` excluye `.streamlit/secrets.toml`, `.env`, `.env.*`, `*.env`, `*.pem`, `*.key`, `secrets.json`, `secrets.yaml` y `secrets.yml`. Ninguno de estos archivos existe en el repositorio versionado.
4. **Autorización administrativa en operaciones de modificación:**
   - Todas las funciones de modificación local (`crear_producto_local`, `editar_producto_local`, `cambiar_ubicacion_principal_local`, `eliminar_asignacion_ubicacion_local`) y remota (`publicar_cambios_administrativos_github`, `recargar_inventario_remoto_tras_conflicto`) verifican en servidor el contexto de escritorio (`ContextoDispositivo.ESCRITORIO`), la ausencia de bloqueo temporal activo, la vigencia de la sesión administrativa y la propiedad de la sesión sobre el espacio de trabajo.
5. **Bloqueo de inventarios demostrativos:**
   - `verificar_inventario_autorizado_para_publicacion` y `contiene_datos_demostrativos` rechazan cualquier intento de publicar o inicializar el archivo maestro con datos marcados como `[DEMOSTRATIVO]` / `(Demostrativo)` o con `es_copia_demostrativa=True`, y la interfaz oculta los controles de publicación en GitHub cuando se utiliza la copia demostrativa en memoria.
6. **Restricción de destino GitHub al repositorio y archivo oficiales:**
   - `validar_destino_escritura_github` y `ejecutar_solicitud_put_github` restringen estrictamente el destino al propietario `JunyMSAI`, repositorio `FerreteriaMS`, rama `main`, ruta `03_Aplicacion/inventario.xlsx` y endpoint `https://api.github.com/repos/JunyMSAI/FerreteriaMS/contents/03_Aplicacion/inventario.xlsx`.
7. **Prohibición de escrituras reales mientras `ESCRITURA_REAL_GITHUB_HABILITADA=False`:**
   - Confirmado que `ESCRITURA_REAL_GITHUB_HABILITADA: bool = False` en `03_Aplicacion/persistencia_github.py` bloquea incondicionalmente cualquier solicitud HTTP `PUT` real en `ejecutar_solicitud_put_github`.

### 4.2. Problemas críticos de seguridad/despliegue detectados y corregidos con cambio mínimo

Durante la auditoría del Prompt 11 sobre `03_Aplicacion/persistencia_github.py` se identificaron y corrigieron tres puntos críticos con el cambio mínimo indispensable:

1. **Separación entre transporte HTTP real y ejecutores simulados sin modificar globalmente módulos de red (`03_Aplicacion/persistencia_github.py`):**
   - *Problema detectado:* `_verificar_transporte_escritura_autorizado` comprobaba únicamente el envoltorio externo de `ejecutor_http_put`, sin desenvolver instancias de `functools.partial` ni funciones decoradas con `__wrapped__` que referenciaran a `ejecutar_solicitud_put_github` o a funciones de `urllib.request`, `http.client` o `socket` mientras `ESCRITURA_REAL_GITHUB_HABILITADA` era `False`. Asimismo, `ejecutar_solicitud_put_github` no verificaba por sí misma que la URL coincidiera exactamente con `validar_destino_escritura_github(CONFIGURACION_POR_DEFECTO)`.
   - *Corrección aplicada:* Se añadió desenvolvimiento recursivo de `functools.partial` y `__wrapped__` en `_desenvolver_ejecutor_candidato` dentro de `_verificar_transporte_escritura_autorizado` y se reforzó `ejecutar_solicitud_put_github` para exigir `ESCRITURA_REAL_GITHUB_HABILITADA=True` y coincidencia exacta con `validar_destino_escritura_github(CONFIGURACION_POR_DEFECTO)`, manteniendo el transporte real separado de los ejecutores simulados de pruebas sin aplicar *monkeypatching* global sobre `urllib.request`, `http.client` o `socket` (evitando así interferencias con sesiones concurrentes de Streamlit y sin afirmar aislamiento universal frente a código arbitrario).
2. **Prevención de reenvío de una misma solicitud `PUT` y revocación de confirmación tras resultados ambiguos (`03_Aplicacion/persistencia_github.py`):**
   - *Problema detectado:* Cuando el paso de escritura (`PUT` o `interpretar_respuesta_put_github`) fallaba con un resultado ambiguo (p. ej. *timeout*, caída de red, error `5xx` o respuesta `200`/`201` truncada sin `sha`), la bandera `CLAVE_CONFIRMACION_GUARDADO_GITHUB` en el estado de sesión no se revocaba automáticamente, y una instancia de `SolicitudPutContentsGitHub` no quedaba marcada como ya despachada.
   - *Corrección aplicada:* Se incorporó el atributo de estado interno `_despachada: bool` en cada instancia de `SolicitudPutContentsGitHub` junto con `_registrar_despacho_unico_solicitud_put` (sin utilizar colecciones globales basadas en `id()`, evitando crecimiento indefinido en memoria o falsos positivos por reutilización de direcciones de objetos recolectados), se conservó el control de huella en `estado` (`CLAVE_HUELLA_ULTIMA_PUBLICACION_ADMIN`) y la comprobación previa de `SHA`, y se añadió la revocación automática de `estado[CLAVE_CONFIRMACION_GUARDADO_GITHUB] = False` (y `chk_admin_confirmar_publicacion_github = False`) cuando falla el paso de escritura, exigiendo nueva confirmación administrativa y nueva verificación remota de `SHA` antes de cualquier reintento.
3. **Resolución autónoma de ruta de importación en `03_Aplicacion/persistencia_github.py`:**
   - *Problema detectado:* A diferencia de `app.py`, `administracion_productos.py`, `busqueda.py` y `github_inventario.py`, el módulo `persistencia_github.py` no añadía `Path(__file__).resolve().parent` a `sys.path` antes de importar módulos hermanos de `03_Aplicacion/`, lo que podía causar `ModuleNotFoundError` si se importaba antes que `app.py` desde la raíz del proyecto.
   - *Corrección aplicada:* Se añadió la inserción estándar de `_DIRECTORIO_ACTUAL` en `sys.path` al inicio de `03_Aplicacion/persistencia_github.py`.

### 4.3. Archivos creados o modificados en esta tarea

- **Modificados:**
  - `03_Aplicacion/persistencia_github.py` (separación segura entre transporte real y simulado sin *monkeypatching* global, marca por instancia `_despachada` en `SolicitudPutContentsGitHub` y revocación de confirmación ante resultados ambiguos, validación estricta de URL oficial en `ejecutar_solicitud_put_github` y ajuste de `sys.path`).
  - `04_Pruebas/test_10_persistencia_inventario_github.py` (ampliación de `test_41_rechazo_intentos_anular_compuerta_escritura_real_github` para verificar el bloqueo de envoltorios `functools.partial`/`__wrapped__`, la marca de despacho por instancia sin depender de `id()` y la revocación de confirmación ante resultados ambiguos).
- **Creados:**
  - `05_Resultados/11_Resultado_Integracion_Seguridad.md` (presente informe).
- **Archivos que NO fueron creados ni modificados:**
  - `03_Aplicacion/inventario.xlsx` (confirmado inexistente).
  - Resto de módulos de `03_Aplicacion/`, `requirements.txt`, `.gitignore` y documentación oficial.

---

## 5. Preparación para Despliegue en Streamlit Community Cloud

### 5.1. Comprobaciones realizadas (sin ejecutar despliegue)

| Elemento de despliegue | Estado comprobado | Detalle técnico |
| :--- | :---: | :--- |
| **Archivo principal** | Listo | `03_Aplicacion/app.py` existe, define `renderizar_aplicacion()` bajo `if __name__ == "__main__":` y configura `st.set_page_config`. |
| **Dependencias (`requirements.txt`)** | Listo | Incluye únicamente las 4 bibliotecas externas requeridas por v0: `streamlit>=1.30.0`, `pandas>=2.0.0`, `openpyxl>=3.1.0`, `argon2-cffi>=23.1.0`. No incluye `google-genai`. |
| **Compatibilidad de rutas y recursos** | Listo | Uso exclusivo de `pathlib.Path(__file__).resolve().parent` para `sys.path` y para cargar `03_Aplicacion/estilos.css` con degradación segura si el archivo no estuviera presente. |
| **Lectura de secretos y variables de entorno** | Listo | `autenticacion.py` y `github_inventario.py` / `persistencia_github.py` leen credenciales desde `st.secrets` o variables de entorno sin depender de archivos locales `.env` o `.streamlit/secrets.toml` en el repositorio. |
| **Ausencia de dependencia de archivos locales no incluidos** | Listo | La aplicación opera íntegramente en memoria (`io.BytesIO`) contra GitHub API y no requiere que `03_Aplicacion/inventario.xlsx` exista en el sistema de archivos local del contenedor. |
| **Compuerta de escritura real en GitHub** | Deshabilitada (`False`) | `ESCRITURA_REAL_GITHUB_HABILITADA = False` en `03_Aplicacion/persistencia_github.py`. |

### 5.2. Requisitos pendientes para configurar en Streamlit Community Cloud cuando se autorice el despliegue

1. **Configuración de Secrets en el panel de Streamlit Community Cloud (`App settings -> Secrets`):**
   - `FERRETERIAMS_ADMIN_USER`: nombre de usuario de la cuenta administrativa única.
   - `FERRETERIAMS_ADMIN_PASSWORD_HASH`: hash Argon2id (`$argon2id$v=19$...`) de la contraseña administrativa (generado fuera de línea con `generar_hash_contrasena`).
   - `FERRETERIAMS_GITHUB_TOKEN` (o `GITHUB_TOKEN`): Fine-grained Personal Access Token de GitHub restringido exclusivamente al repositorio `JunyMSAI/FerreteriaMS` con permiso `Contents: Read and write` (mínimo privilegio).
2. **Habilitación autorizada de escrituras reales e inicialización del inventario maestro:**
   - Mientras `ESCRITURA_REAL_GITHUB_HABILITADA` permanezca en `False` en `03_Aplicacion/persistencia_github.py`, cualquier escritura HTTP `PUT` real hacia GitHub está bloqueada por diseño. Su cambio a `True` y la inicialización oficial de `03_Aplicacion/inventario.xlsx` en la rama `main` requieren autorización expresa en la etapa correspondiente.

---

## 6. Riesgos y Limitaciones Pendientes

1. **Operaciones reales de red contra GitHub Contents API no ejecutadas en esta etapa:**
   - Cumpliendo las restricciones obligatorias del Prompt 11, todas las verificaciones de lectura y escritura contra GitHub se ejecutaron mediante simulaciones y mocks deterministas, sin tokens reales ni tráfico HTTP real. La validación del token real y de la escritura HTTP `PUT` contra `https://api.github.com/repos/JunyMSAI/FerreteriaMS/contents/03_Aplicacion/inventario.xlsx` queda pendiente para la etapa autorizada de activación y despliegue.
2. **Inexistencia actual de `03_Aplicacion/inventario.xlsx` en el repositorio remoto:**
   - Hasta que se autorice e inicialice el archivo maestro oficial en GitHub, la búsqueda pública en producción informará el estado controlado `INVENTARIO_NO_INICIALIZADO`.
3. **Estado de bloqueos y borradores en memoria del proceso de Streamlit:**
   - Conforme a la arquitectura sin base de datos aprobada para FerreteríaMS v0, el control de bloqueos progresivos, sesiones activas y borradores temporales de 15 minutos reside en la memoria del proceso del servidor de Streamlit (`threading.RLock`), por lo que se reinicia si el contenedor de Streamlit Community Cloud se reinicia por completo.
4. **Límite de tamaño de GitHub Contents API:**
   - La actualización de archivos mediante contenido Base64 en `PUT /repos/{owner}/{repo}/contents/{path}` está sujeta al límite de 1 MB de GitHub Contents API, suficiente para el alcance de FerreteríaMS v0.

---

## 7. Requisitos (RF) y Criterios de Aceptación (CA) Verificados en Integración

- **Requisitos funcionales verificados en simulación:** `RF-001` a `RF-038`.
- **Criterios de aceptación comprobados en pruebas locales e integradas simuladas:** `CA-001` a `CA-034`, `CA-039` a `CA-061`.
- **Criterios de aceptación sujetos a la activación y despliegue real en Streamlit Community Cloud y GitHub:** `CA-035`, `CA-036`, `CA-037`, `CA-038` (y la confirmación en red real de `CA-020`, `CA-023`, `CA-024`).

---

## 8. Estado Final del Repositorio (`git status --short`)

```text
 M 03_Aplicacion/persistencia_github.py
 M 04_Pruebas/test_10_persistencia_inventario_github.py
?? 05_Resultados/11_Resultado_Integracion_Seguridad.md
```

- No se ejecutaron `git add`, `git commit`, `git push` ni despliegues.
- No se creó ni modificó `03_Aplicacion/inventario.xlsx`.
- `ESCRITURA_REAL_GITHUB_HABILITADA` permanece en `False`.

