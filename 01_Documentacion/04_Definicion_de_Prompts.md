# Definición y propósito de los prompts de FerreteríaMS

**Proyecto:** FerreteríaMS  
**Documento:** `01_Documentacion/04_Definicion_de_Prompts.md`  
**Cobertura:** Prompts aprobados P01–P19

## Índice informativo de consulta rápida.

## 1. Propósito del documento

Describir de manera breve para qué se creó cada prompt aprobado, qué necesidad o parte del proyecto atendió. Este índice facilita localizar la instrucción pertinente sin tener que leer inicialmente todos los prompts.

## 2. Definición de cada prompt

Prompts: Objetivo y necesidad atendida

- **P01 — Verificación inicial:** [01_Verificacion_Inicial.md](../02_Prompts/01_Verificacion_Inicial.md),
    Revisar, en modo solo lectura, las instrucciones del agente y los documentos de concepto y especificaciones antes de comenzar el desarrollo.
- **P02 — Motor de inventario:** [02_Motor_Inventario.md](../02_Prompts/02_Motor_Inventario.md),
    Preparar dependencias y construir el motor para leer y validar el inventario Excel de cuatro hojas, con reglas de integridad y protección de datos existentes.
- **P03 — Lectura desde GitHub:** [03_Lectura_GitHub.md](../02_Prompts/03_Lectura_GitHub.md),
    Conectar la aplicación con GitHub API para consultar, descargar y validar el archivo del inventario creado en Excel, incluyendo control de versión e incidencias de acceso.
- **P04 — Búsqueda pública:** [04_Busqueda_Publica.md](../02_Prompts/04_Busqueda_Publica.md),
    Construir la búsqueda de productos por nombre con coincidencias parciales, normalización de texto, relevancia y pagina en Streamlit.
- **P05 — Detalles y ubicaciones:** [05_Detalles_Ubicaciones.md](../02_Prompts/05_Detalles_Ubicaciones.md),
    Permitir seleccionar un resultado y consultar la información del producto, su ubicación principal y otras ubicaciones asignadas.
- **P06 — Interfaz responsive y Gemini «Próximamente»:** [06_Interfaz_Responsive_Gemini.md](../02_Prompts/06_Interfaz_Responsive_Gemini.md),
    Mejorar la presentación en computadora he incorporar un espacio visual reservado para Gemini, todavía sin conexión funcional.
- **P07 — Autenticación administrativa:** [07_Autenticacion_Administrativa.md](../02_Prompts/07_Autenticacion_Administrativa.md),
    Establecer el acceso protegido del administrador, con credenciales seguras y separación entre funciones públicas y administrativas. Inicio de sesión administrativo y protección básica de las funciones restringidas.
- **P08 — Sesiones, bloqueos y borradores:** [08_Sesiones_Bloqueos_Borradores.md](../02_Prompts/08_Sesiones_Bloqueos_Borradores.md),
    Reforzar la seguridad administrativa mediante intentos fallidos, bloqueos progresivos, expiración, renovación de sesión y manejo de cambios pendientes.
- **P09 — Gestión administrativa:** [09_Gestion_Administrativa_Productos_Ubicaciones.md](../02_Prompts/09_Gestion_Administrativa_Productos_Ubicaciones.md),
    Crear la interfaz y lógica para consultar, crear y editar productos y sus relaciones con categorías y ubicaciones. 
- **P10 — Persistencia en GitHub:** [10_Persistencia_Inventario_GitHub.md](../02_Prompts/10_Persistencia_Inventario_GitHub.md),
    Permitir guardar de forma controlada el inventario en Excel mediante GitHub API, con confirmación, manejo de credenciales.
- **P11 — Integración y seguridad:** [11_Integracion_Seguridad.md](../02_Prompts/11_Integracion_Seguridad.md),
    Comprobar la integración entre módulos, atender riesgos de seguridad relevantes y preparar la entrega.
- **P12 — Despliegue en Streamlit Cloud:** [12_Despliegue_Streamlit_Cloud.md](../02_Prompts/12_Despliegue_Streamlit_Cloud.md),
    Completar los ajustes mínimos de funcionamiento y habilitar el despliegue real, incluyendo navegación, inventario y preparación del guardado mediante GitHub.
- **P13 — Validación final de v0:** [13_Validacion_Final.md](../02_Prompts/13_Validacion_Final.md),
    Verificar de manera focalizada las funciones principales, la persistencia real y las condiciones de seguridad para cerrar la primera versión.
- **P14 — Administración de catálogos:** [14_Administracion_Catalogos.md](../02_Prompts/14_Administracion_Catalogos.md),
    Ampliar la administración para crear y editar categorías y ubicaciones, evitar duplicados y proteger asignaciones existentes.
- **P15 — Estados de productos:** [15_Estados_Productos.md](../02_Prompts/15_Estados_Productos.md),
    Incorporar la desactivación y reactivación de productos sin borrar sus datos, excluyendo los inactivos de la búsqueda pública y del catálogo activo usado por Gemini.
- **P16 — Integración funcional de Gemini:** [16_Integracion_Gemini.md](../02_Prompts/16_Integracion_Gemini.md),
    Desarrollar el asistente de texto para asesoría de ferretería, con contexto del inventario, restricciones temáticas, advertencias y límites de consumo.
- **P17 — Activación y validación de Gemini:** [17_Activacion_Validacion_Gemini.md](../02_Prompts/17_Activacion_Validacion_Gemini.md),
    Preparar la conexión real con Google Gemini API, configurar la clave de manera segura y verificar compatibilidad, disponibilidad y manejo de errores.
- **P18 — Página independiente de Gemini:** [18_Pagina_Independiente_Gemini.md](../02_Prompts/18_Pagina_Independiente_Gemini.md),
    Separar el chat de la búsqueda pública y trasladarlo a una sección propia.
- **P19 — Página Acerca de FerreteriaMS:** [19_Pagina_Acerca_de_FerreteriaMS.md](../02_Prompts/19_Pagina_Acerca_de_FerreteriaMS.md),
    Crear la página informativa relacionada a la FerreteriaMS.       