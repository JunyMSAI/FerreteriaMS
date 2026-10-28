# FERMS-V0-P11 — Integración y seguridad para entrega urgente

**Proyecto:** FerreteríaMS v0   
**Prioridad:** ALTA — Entrega próxima  

## Objetivo

Verificar que FerreteríaMS v0 funcione correctamente como aplicación integrada y quede preparada para su despliegue en Streamlit Community Cloud.

**No desarrollar funcionalidades nuevas. Corregir únicamente errores críticos que impidan el funcionamiento, comprometan la seguridad o bloqueen el despliegue.**

## 1. Verificaciones iniciales

Leer `GEMINI.md`, `AGENTS.md`, las especificaciones oficiales y el informe P10.

Confirmar:

- Rama `main`.
- Commit base `ae1d44b`.
- Árbol de trabajo limpio.

Si existen cambios inesperados, detenerse.

## 2. Pruebas de integración

Verificar, priorizando pruebas ya existentes:

- Inicio de la aplicación Streamlit.
- Búsqueda pública y visualización de ubicaciones.
- Login administrativo con Argon2id.
- Bloqueos, expiración y renovación de sesiones.
- Creación y edición local de productos.
- Validación de categorías y ubicaciones.
- Serialización Excel y preservación de las cuatro hojas.
- Integración GitHub API con simulaciones.
- Control de conflictos SHA.
- Actualización de búsquedas después de una publicación simulada.
- Interfaz responsive y Gemini exclusivamente «Próximamente».

Ejecutar las pruebas existentes de P02–P10 secuencialmente, sin paralelismo.

No crear suites extensas nuevas salvo que sea imprescindible para comprobar un fallo crítico.

## 3. Seguridad obligatoria

Verificar:

- Ausencia de tokens, contraseñas y hashes incrustados en el código.
- Protección de secretos en errores, registros e interfaz.
- Reglas `.gitignore` para archivos sensibles.
- Autorización administrativa en operaciones de modificación.
- Bloqueo de inventarios demostrativos.
- Restricción de destino GitHub al repositorio y archivo oficiales.
- Prohibición de escrituras reales mientras `ESCRITURA_REAL_GITHUB_HABILITADA=False`.
- Separación segura entre transporte simulado y transporte real, comprobando que una función inyectada no pueda provocar una escritura no autorizada.
- No reutilizar automáticamente una solicitud de escritura cuyo resultado sea ambiguo.

**No utilizar tokens reales ni ejecutar escrituras HTTP reales.**

Si identificas una vulnerabilidad crítica, corrígela con el cambio mínimo posible y verifica que no introduzca regresiones.

## 4. Preparación para Streamlit Cloud

Comprobar sin desplegar:

- Archivo principal `03_Aplicacion/app.py`.
- Dependencias necesarias en `requirements.txt`.
- Compatibilidad de rutas y recursos.
- Lectura de configuración sensible mediante secretos o variables de entorno.
- Ausencia de dependencia obligatoria de archivos locales no incluidos.
- Estado de la compuerta de escritura real deshabilitada.

Registrar los requisitos pendientes para configurar Streamlit Cloud posteriormente.

## 5. Restricciones de tiempo y alcance

Evitar:

- Refactorizaciones.
- Cambios cosméticos.
- Cambios documentales menores heredados de P10.
- Nuevas funcionalidades.
- Repetición innecesaria de pruebas.
- Cambios en archivos protegidos sin autorización.

Si aparece un problema que requiere modificaciones importantes, informar antes de actuar.

## 6. Informe de resultados

Registrar el resultado en:

`05_Resultados/11_Resultado_Integracion_Seguridad.md`

El informe debe incluir los comandos ejecutados, resultados de pruebas, problemas críticos detectados, correcciones efectuadas, riesgos pendientes y estado de preparación para despliegue.

No declarar seguridad absoluta ni afirmar que se verificaron operaciones reales cuando solo se probaron simulaciones.

Al terminar, mostrar `git status --short`.

**No ejecutar git add, commit, push ni despliegue. No activar escrituras reales. Detenerse y esperar aprobación.**