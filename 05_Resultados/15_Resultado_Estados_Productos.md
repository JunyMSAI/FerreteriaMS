# Resultado de Ejecución — FERMS-FINAL-P15: Estados activo/inactivo de productos

- **Identificador de la tarea:** `FERMS-FINAL-P15`
- **Fecha de ejecución:** 2026-10-22
- **Título de la tarea:** Estados activo/inactivo de productos, visibilidad en búsqueda y cierre del Bloque 1
- **Etapa / Bloque:** FerreteríaMS — Versión Final · Bloque 1 (Cierre)
- **Agente de desarrollo:** Gemini (Antigravity)

---

## 1. Prompt o solicitud original

Ejecución autorizada del documento oficial `02_Prompts/15_Estados_Productos.md`:

> **FERMS-FINAL-P15 — AUTORIZACIÓN DE EJECUCIÓN**
>
> Ejecuta exclusivamente el documento oficial:
> `02_Prompts/15_Estados_Productos.md`
>
> **Prioridad:** completar el Bloque 1 con calidad, rapidez y sin tareas redundantes.
>
> Antes de comenzar, consulta `GEMINI.md`, `AGENTS.md`, `03_Especificaciones_Final.md` y los resultados de P14.
>
> **Instrucciones:**
> 1. Implementar únicamente la desactivación y reactivación de productos.
> 2. Conservar todos los datos y ubicaciones de los productos inactivos.
> 3. Excluirlos de la búsqueda y el detalle público, sin afectar los productos activos.
> 4. Reutilizar el motor Excel, la administración y la persistencia GitHub existentes.
> 5. Mantener compatibilidad con inventarios anteriores.
> 6. Ejecutar solamente pruebas focalizadas sobre el nuevo comportamiento y las integraciones directamente afectadas.
>
> **Restricciones:**
> - No reconstruir funcionalidades de v0 o P14.
> - No integrar Gemini API todavía.
> - No modificar `inventario.xlsx` real.
> - No realizar operaciones HTTP PUT reales ni utilizar credenciales reales.
> - No desarrollar funcionalidades adicionales.
> - No realizar auditorías extensas.
> - No ejecutar commit, push ni despliegue.

---

## 2. Interpretación del agente

El objetivo de `FERMS-FINAL-P15` es cerrar el **Bloque 1** de la versión final incorporando el estado lógico `Activo` (`"Sí"` / `"No"`) en la hoja `Productos`, permitiendo al administrador desactivar y reactivar productos con confirmación explícita en sesión de escritorio autenticada, conservando íntegros sus datos (`Codigo_Producto` inmutable con ceros iniciales, `Nombre`, `Categoria_ID`, `Descripcion`) y sus filas en `Asignaciones`, excluyendo los productos inactivos de la búsqueda pública, del detalle público y del catálogo activo preparado para futuras consultas de Gemini (Bloque 2), y manteniendo retrocompatibilidad con archivos Excel `v0` sin columna `Activo` en `Productos`.

---

## 3. Acciones realizadas

1. **Esquema y validación retrocompatible en `03_Aplicacion/inventario.py`:**
   - Se actualizó `ESQUEMA_HOJAS[HOJA_PRODUCTOS]` a `("Codigo_Producto", "Nombre", "Categoria_ID", "Descripcion", "Activo")` y se registró `HOJA_PRODUCTOS: frozenset({"Activo"})` en `COLUMNAS_OPCIONALES_RETROCOMPATIBLES` para que inventarios `v0` sin columna `Activo` en `Productos` se carguen automáticamente asignando `Activo = "Sí"`.
   - En `validar_inventario` y `construir_inventario_datos`, se normaliza y valida el campo `Activo` de cada fila de `Productos` mediante `normalizar_valor_activo` (admitiendo únicamente estados lógicos `"Sí"` y `"No"`, y rechazando valores inválidos con `CodigoErrorInventario.VALOR_ACTIVO_INVALIDO`).
   - Se actualizó `obtener_productos_estructurados(inventario, *, incluir_inactivos: bool = True)` para exponer `"activo"` y `"es_activo"` en cada diccionario de producto, se incorporó `obtener_productos_activos_estructurados(inventario)` y se añadió el parámetro `incluir_inactivos: bool = True` en `obtener_producto_por_codigo`.

2. **Exclusión de productos inactivos en `03_Aplicacion/busqueda.py`:**
   - Se actualizó `extraer_catalogo_productos(origen_datos, *, solo_activos: bool = True)` para excluir por defecto los productos con `Activo = "No"` en todos los tipos de origen soportados (`InventarioDatos`, `Mapping`, `DataFrame`, `Iterable`), manteniendo retrocompatibilidad con registros sin columna `Activo`.
   - Se incorporó `obtener_catalogo_productos_activos(origen_datos)` para la consulta pública y como punto de acceso limpio al catálogo activo para el futuro Bloque 2.
   - Se actualizó `consultar_detalle_producto` para invocar `obtener_producto_por_codigo(..., incluir_inactivos=False)`, devolviendo `EstadoDetalleProducto.PRODUCTO_NO_DISPONIBLE` cuando se solicita el detalle público de un producto inactivo.

3. **Operaciones administrativas de desactivación/reactivación y borradores en `03_Aplicacion/administracion_productos.py`:**
   - Se añadieron los códigos de error `PRODUCTO_YA_INACTIVO`, `PRODUCTO_YA_ACTIVO`, `CONFIRMACION_CAMBIO_ESTADO_REQUERIDA` y `VALOR_ACTIVO_PRODUCTO_INVALIDO`.
   - Se aseguró que `crear_producto_local` registre explícitamente `"Activo": "Sí"` y que `editar_producto_local` conserve el estado `Activo` vigente del producto editado.
   - Se implementaron `desactivar_producto_local`, `reactivar_producto_local` y `cambiar_estado_producto_local`, exigiendo sesión administrativa válida en escritorio y confirmación explícita, conservando todos los datos y ubicaciones del producto al desactivar, y verificando al reactivar que su categoría exista, tenga al menos una ubicación activa asignada, exactamente una ubicación principal y ninguna asignación rota o duplicada.
   - Se enriqueció `consultar_productos_administrativos` con los indicadores `activo`, `es_activo`, `activo_texto`, `estado_producto_texto`, `permite_desactivar`, `permite_reactivar`, `es_desactivado_local` y `es_reactivado_local`.
   - Se integró la reproducción de operaciones `DESACTIVAR_PRODUCTO` y `REACTIVAR_PRODUCTO` en `restaurar_borrador_en_espacio_trabajo_admin`.
   - Las ubicaciones asociadas a productos inactivos conservan sus filas en `Asignaciones`, permaneciendo protegidas contra edición física y desactivación (`UBICACION_CON_PRODUCTOS_ASOCIADOS`).

4. **Integración en interfaz administrativa en `03_Aplicacion/app.py`:**
   - Se añadieron las funciones de sesión `ejecutar_desactivacion_producto_en_sesion`, `ejecutar_reactivacion_producto_en_sesion` y `ejecutar_cambio_estado_producto_en_sesion`.
   - Se actualizaron `_renderizar_vista_consulta_admin` y `_renderizar_formulario_editar_producto_admin` para mostrar claramente el estado de cada producto (`🟢 Activo` / `🔴 Inactivo`) y permitir desactivarlo o reactivarlo previa casilla de confirmación explícita.

5. **Pruebas focalizadas en `04_Pruebas/test_15_estados_productos.py`:**
   - Se creó y ejecutó la suite focalizada `04_Pruebas/test_15_estados_productos.py` verificando los escenarios definidos en la Sección 8 del prompt junto con la suite `04_Pruebas/test_14_administracion_catalogos.py`.

---

## 4. Archivos creados o modificados

### Archivos modificados
- `03_Aplicacion/inventario.py`
- `03_Aplicacion/busqueda.py`
- `03_Aplicacion/administracion_productos.py`
- `03_Aplicacion/app.py`

### Archivos creados
- `04_Pruebas/test_15_estados_productos.py`
- `05_Resultados/15_Resultado_Estados_Productos.md`

### Archivos verificados sin modificaciones
- `03_Aplicacion/inventario.xlsx` (intacto en disco, verificado mediante hash SHA-256 y `git status --short`).

---

## 5. Requisitos y criterios de aceptación relacionados

### Requisitos funcionales Versión Final (`03_Especificaciones_Final.md`)
- `RF-F-008`: Desactivación y reactivación de productos en la hoja `Productos` mediante el campo lógico `Activo`, conservando todos sus datos y ubicaciones asignadas, excluyéndolos de la búsqueda pública y manteniéndolos visibles en la administración.
- `RF-F-009`: Validación de integridad al reactivar productos (categoría existente, al menos una ubicación existente y activa, y exactamente una ubicación principal).
- `RF-F-010`: Conservación de las cuatro hojas oficiales (`Productos`, `Categorías`, `Ubicaciones`, `Asignaciones`) y persistencia en GitHub con control de versión SHA.
- `RF-F-011`: Compatibilidad retroactiva con archivos `inventario.xlsx` de `v0` sin columna `Activo` en `Productos` y `Ubicaciones` (interpretados automáticamente como `"Sí"`).

### Criterios de aceptación Versión Final (`03_Especificaciones_Final.md`)
- `CA-F-007`: Desactivación de productos con exclusión inmediata de la búsqueda y detalle público, conservación íntegra de datos y ubicaciones, visibilidad administrativa y reactivación validada.
- `CA-F-008`: Guardado y serialización de las cuatro hojas oficiales en `inventario.xlsx` con verificación round-trip y control SHA simulado.
- `CA-F-009`: Carga retrocompatible de inventarios anteriores sin estado explícito en `Productos` o `Ubicaciones` asumiendo estado activo (`"Sí"`).

### Requisitos y criterios heredados de `v0` preservados
- `RF-001` a `RF-009`, `RF-013`, `RF-015` a `RF-020`, `RF-024`, `RF-025`, `RF-027`, `RF-030` y criterios `CA-001` a `CA-007`, `CA-014` a `CA-019`, `CA-022`, `CA-044` a `CA-050`.

---

## 6. Pruebas ejecutadas y resultados

Comando ejecutado:

```bash
python -m unittest 04_Pruebas/test_15_estados_productos.py 04_Pruebas/test_14_administracion_catalogos.py -v
```

Resultado: **22 pruebas ejecutadas — 22 exitosas (`OK`) en 1.798 s.**

### Detalle de pruebas focalizadas en `04_Pruebas/test_15_estados_productos.py` (9 pruebas)
1. `test_01_compatibilidad_retroactiva_inventario_v0_y_validacion_activo`: Carga inventario `v0` sin columna `Activo` en `Productos`, asigna `Activo = "Sí"` por defecto, comprueba alta de nuevo producto con `Activo = "Sí"` y rechaza valores inválidos en `Activo` (`CA-F-009`). **OK**
2. `test_02_desactivacion_producto_conserva_datos_y_asignaciones`: Desactiva el producto `"0010"` (conservando ceros iniciales, nombre, categoría, descripción, ubicación principal y secundaria) y rechaza desactivar de nuevo un producto ya inactivo (`CA-F-007`). **OK**
3. `test_03_exclusion_productos_inactivos_busqueda_detalle_y_catalogo_activo`: Verifica que el producto inactivo `"0010"` no aparece en `buscar_productos_por_nombre`, `ejecutar_busqueda_productos`, `consultar_detalle_producto` (`PRODUCTO_NO_DISPONIBLE`) ni en `obtener_catalogo_productos_activos`, mientras los productos activos siguen disponibles normalmente (`RF-F-008`, `CA-F-007`). **OK**
4. `test_04_reactivacion_producto_valido_y_rechazo_ante_inconsistencias`: Reactiva un producto válido comprobando su retorno inmediato a la búsqueda y al detalle público; verifica rechazo cuando ya está activo, cuando carece de ubicación principal, cuando tiene una ubicación inactiva o cuando carece de asignaciones (`RF-F-009`, `CA-F-007`). **OK**
5. `test_05_visibilidad_administrativa_activos_e_inactivos`: Comprueba que `consultar_productos_administrativos` incluye productos activos e inactivos con sus indicadores de estado y permite editar un producto inactivo preservando su condición de inactivo (`CA-F-007`). **OK**
6. `test_06_proteccion_ubicaciones_asociadas_a_productos_inactivos`: Verifica que una ubicación asociada a un producto inactivo sigue bloqueada frente a edición física y desactivación (`UBICACION_CON_PRODUCTOS_ASOCIADOS`) (`CA-F-005`, `CA-F-006`, `CA-F-007`). **OK**
7. `test_07_persistencia_simulada_roundtrip_y_borradores`: Verifica restauración de borradores con operaciones `DESACTIVAR_PRODUCTO` y `REACTIVAR_PRODUCTO`, publicación simulada mediante GitHub Contents API con control SHA y verificación round-trip de las 4 hojas Excel con columna `Activo` en `Productos` y `Ubicaciones` (`CA-F-008`, `CA-F-009`). **OK**
8. `test_08_seguridad_administrativa_y_confirmacion_cambio_estado`: Verifica que el cambio de estado exige confirmación explícita, sesión autenticada y dispositivo de escritorio (`RF-013`). **OK**
9. `test_09_inmutabilidad_archivo_inventario_xlsx_en_disco`: Verifica mediante hash SHA-256 que `03_Aplicacion/inventario.xlsx` permanece intacto en disco. **OK**

### Regresión focalizada del Bloque 1 en `04_Pruebas/test_14_administracion_catalogos.py` (13 pruebas)
- Todas las 13 pruebas de administración de categorías, ubicaciones, retrocompatibilidad, borradores y publicación simulada de `P14` pasaron sin regresiones (`OK`).

---

## 7. Estado de `git status --short`

```text
 M 03_Aplicacion/administracion_productos.py
 M 03_Aplicacion/app.py
 M 03_Aplicacion/busqueda.py
 M 03_Aplicacion/inventario.py
?? 04_Pruebas/test_15_estados_productos.py
?? 05_Resultados/15_Resultado_Estados_Productos.md
```

---

## 8. Errores, limitaciones o asuntos pendientes

- **Errores o regresiones:** Ninguno.
- **Archivo maestro `03_Aplicacion/inventario.xlsx`:** Intacto (sin modificar).
- **Operaciones remotas reales / commits / despliegues:** No realizados, cumpliendo estrictamente las restricciones de la tarea.
- **Estado del Bloque 1:** Completado en su totalidad (`CA-F-001` a `CA-F-009`). Listo para revisión y aprobación antes de iniciar el Bloque 2.
- **Referencia al commit:** Pendiente de autorización del usuario.

