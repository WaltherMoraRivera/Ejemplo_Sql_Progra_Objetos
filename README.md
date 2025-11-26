# Gestor de Festival de Cine - PyQt6

Aplicación de escritorio basada en PyQt6 para gestionar múltiples entidades de una base de datos de Festival de Cine (Oracle Autonomous Database). La aplicación soporta operaciones CRUD (crear, leer, actualizar, eliminar) para **Asistentes**, **Ciudades**, **Sedes**, **Películas**, **Funciones**, **Asistencias** y **Jurados**.

El proyecto sigue una arquitectura **MVVM** (Modelo–Vista–VistaModelo) con separación clara entre:
- **Domain Models**: clases de dominio con datos e identidad.
- **Repositories**: acceso a datos y mapeo de procedimientos almacenados Oracle.
- **ViewModels**: orquestación de lógica y emisión de señales PyQt6.
- **UI**: interfaz gráfica, tablas, diálogos, delegados.

## Requisitos previos

- Python 3.11+
- Dependencias (ver `requirements.txt`):
  - PyQt6==6.7.0
  - oracledb==2.0.1
- Wallet de Oracle Autonomous Database configurado.

### Configuración de Oracle Autonomous Database

1. **Wallet**: Descomprime tu wallet en `Wallet/` o ajusta la ruta en `config/settings.json`.
   - Archivos esperados: `tnsnames.ora`, `cwallet.sso`, `sqlnet.ora`, `ojdbc.properties`.

2. **Credenciales**: Actualiza `config/settings.json`:
   ```json
   {
     "user": "tu_usuario",
     "password": "tu_contraseña",
     "dsn": "alias_dsn_en_tnsnames",
     "wallet_dir": "./Wallet",
     "wallet_password": "contraseña_wallet_si_aplica"
   }
   ```

3. **Validación**: `OracleConnection` busca el wallet en rutas relativas y valida su existencia. Si no existe, lanza `FileNotFoundError` con detalles.

## Estructura del Proyecto

```
.
├── main.py                           # Punto de entrada
├── config/
│   └── settings.json                 # Credenciales y configuración Oracle
├── app/
│   ├── domain/
│   │   └── models/
│   │       ├── asistente.py          # Modelo de Asistente
│   │       ├── ciudad.py             # Modelo de Ciudad
│   │       ├── sede.py               # Modelo de Sede
│   │       ├── pelicula.py           # Modelo de Película
│   │       ├── funcion.py            # Modelo de Función
│   │       ├── asistencia.py         # Modelo de Asistencia
│   │       └── jurado.py             # Modelo de Jurado
│   ├── infrastructure/
│   │   ├── database/
│   │   │   └── oracle_connection.py  # Factoría de conexiones
│   │   └── repositories/
│   │       ├── asistente_repository.py
│   │       ├── ciudad_repository.py
│   │       ├── sede_repository.py
│   │       ├── pelicula_repository.py
│   │       ├── funcion_repository.py
│   │       ├── asistencia_repository.py
│   │       └── jurado_repository.py
│   ├── viewmodels/
│   │   ├── asistente_viewmodel.py
│   │   ├── ciudad_viewmodel.py
│   │   ├── sede_viewmodel.py
│   │   ├── pelicula_viewmodel.py
│   │   ├── funcion_viewmodel.py
│   │   ├── asistencia_viewmodel.py
│   │   └── jurado_viewmodel.py
│   └── ui/
│       ├── main_window.py            # Ventana principal con menú de selección
│       ├── asistente_table_model.py
│       ├── ciudad_table_model.py
│       ├── sede_table_model.py
│       ├── pelicula_table_model.py
│       ├── funcion_table_model.py
│       ├── asistencia_table_model.py
│       ├── jurado_table_model.py
│       ├── dialogs.py                # Diálogos de CRUD para todas las entidades
│       └── delegates.py              # Delegados personalizados (botones, etc.)
└── scripts/
    ├── e2e_test_pelicula.py          # Test E2E para Película
    ├── ui_interaction_test.py        # Test E2E de flujo UI (sin BD)
    ├── e2e_ui_flow_test.py           # Test E2E completo del flujo menu→tabla→back
    ├── e2e_ui_flow_with_funcion.py   # Test E2E con FUNCION
    ├── e2e_ui_flow_with_asistencia.py # Test E2E con ASISTENCIA
    └── e2e_ui_flow_with_jurado.py    # Test E2E con JURADO
```

## Entidades Soportadas

### 1. **Asistente**
- Campos: `id`, `nombre`, `correo`, `telefono`, `edad`, `ciudad_residencia`, `tipo_asistente`.
- Tabla: `ASISTENTE`
- Repositorio: `AsistenteRepository`

### 2. **Ciudad**
- Campos: `id`, `nombre`, `region`, `pais`, `observaciones`.
- Tabla: `CIUDAD`
- Repositorio: `CiudadRepository`

### 3. **Sede**
- Campos: `id`, `nombre`, `direccion`, `capacidad_maxima`, `tipo_sede`, `id_ciudad`, `estado`.
- Tabla: `SEDE`
- Repositorio: `SedeRepository`

### 4. **Película**
- Campos: `id`, `titulo`, `pais_origen`, `director`, `duracion_minutos`, `genero`, `clasificacion`, `sinopsis`.
- Tabla: `PELICULA`
- Repositorio: `PeliculaRepository`

### 5. **Función**
- Campos: `id`, `fecha`, `hora`, `precio_entrada`, `estado_funcion`, `observaciones`, `id_sede`.
- Tabla: `FUNCION`
- Repositorio: `FuncionRepository`
- Estados: `Programada`, `En curso`, `Finalizada`, `Cancelada`.

### 6. **Asistencia**
- Campos: `id_funcion` (FK), `id_asistente` (FK), `entradas`, `fecha_compra`, `metodo_pago`, `comentarios`.
- Tabla: `ASISTENCIA` (clave primaria compuesta: id_funcion + id_asistente)
- Repositorio: `AsistenciaRepository`
- Métodos de Pago: `Efectivo`, `Tarjeta`, `Transferencia`.

### 7. **Jurado**
- Campos: `id`, `nombre`, `correo`, `especialidad`, `pais_origen`, `experiencia_anos`, `tipo_jurado`, `biografia`.
- Tabla: `JURADO`
- Repositorio: `JuradoRepository`
- Tipos: `Invitado`, `Permanente`, `Honorario`.

## Flujo de la Aplicación

### Inicio y Selección de Tabla

1. Al ejecutar `main.py`, se crea `MainWindow` y se muestra un **menú de selección** con siete botones:
   - **ASISTENTES**
   - **CIUDADES**
   - **SEDES**
   - **PELÍCULAS**
   - **FUNCIONES**
   - **ASISTENCIAS**
   - **JURADOS**

2. El usuario selecciona una tabla y se carga dinámicamente:
   - Se crea `OracleConnection` con `settings.json`.
   - Se instancia el `Repository` y `ViewModel` correspondientes.
   - Se carga el `TableModel` y la vista de tabla.

### Toolbar y Controles

- **Recargar**: recarga los datos desde la BD (visible solo cuando una tabla está seleccionada).
- **Nuevo**: abre un diálogo de formulario para crear un nuevo registro.
- **Eliminar**: elimina los registros seleccionados (previamente marcados con checkbox).
- **Volver al Menú** (derecha): regresa al menú inicial para cambiar de tabla.

**Nota**: Los botones de **Recargar**, **Nuevo** y **Eliminar** solo son visibles cuando una tabla está seleccionada. Al volver al menú se ocultan automáticamente.

### CRUD por Tabla

#### Leer (listar registros)

1. `ViewModel.load_<entidad>()` invoca `Repository.get_all()`.
2. El repositorio ejecuta la consulta (SELECT directo o procedimiento almacenado).
3. Se mapean las filas a instancias del modelo.
4. Se emite la señal `<entidad>s_changed` con la lista.
5. `TableModel.update_<entidad>s()` actualiza la tabla y mantiene selecciones previas.

#### Crear (insert)

1. Botón **Nuevo** → Abre `<Entidad>FormDialog` con validaciones específicas de cada entidad.
2. Al aceptar, se crea la instancia del modelo sin `id`.
3. `ViewModel.add_<entidad>()` → `Repository.add()` ejecuta INSERT o procedimiento almacenado.
4. Se recarga la tabla y se limpian selecciones.

#### Eliminar

1. Se marcan filas con checkbox (en la primera columna).
2. Botón **Eliminar** → reúne IDs y pide confirmación.
3. `ViewModel.delete_<entidad>s()` → `Repository.delete_many()` elimina cada registro.
4. Se recarga la tabla.

#### Ver Detalle

- Última columna muestra botón "Detalle".
- Abre `<Entidad>DetailDialog` con los datos del registro (solo lectura o editable según configuración).

### Gestión del Layout y Límpieza

- La ventana usa un **layout persistente** para evitar problemas con eliminación de widgets.
- Al cambiar de tabla o volver al menú, solo se remueven los widgets del layout; el `QTableView` se preserva y reutiliza.
- Esto garantiza que transiciones menu → tabla → back → tabla funcionan sin errores.

## Ejecución

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar la aplicación

```bash
python main.py
```

Se abrirá la ventana "Gestor de Festival de Cine" mostrando el menú inicial. Selecciona una tabla y usa los botones de toolbar para CRUD.

## Testing

### Pruebas E2E

El proyecto incluye scripts de prueba E2E en `scripts/`:

1. **`ui_interaction_test.py`**: Verifica el flujo de selección UI sin acceso a BD.
   ```bash
   python scripts/ui_interaction_test.py
   ```

2. **`e2e_ui_flow_with_funcion.py`**: Simula un flujo completo incluyendo la nueva entidad FUNCION (menú → FUNCION → back → otra tabla → back → FUNCION).
   ```bash
   python scripts/e2e_ui_flow_with_funcion.py
   ```

3. **`e2e_ui_flow_with_asistencia.py`**: Simula un flujo completo incluyendo la nueva entidad ASISTENCIA (menú → ASISTENCIA → back → FUNCION → back → ASISTENCIA).
   ```bash
   python scripts/e2e_ui_flow_with_asistencia.py
   ```

4. **`e2e_ui_flow_with_jurado.py`**: Simula un flujo completo incluyendo la nueva entidad JURADO (menú → JURADO → back → ASISTENCIA → back → JURADO).
   ```bash
   python scripts/e2e_ui_flow_with_jurado.py
   ```

## Notas Técnicas

### Arquitectura MVVM

- **Domain Model**: clase de datos simple (dataclass-like, con identificador).
- **Repository**: singleton por entidad; encapsula SQL/procedimientos y mapeo.
- **ViewModel**: emisor de señales (PyQt6); sin UI, independiente de la biblioteca gráfica.
- **TableModel (QAbstractTableModel)**: adaptador entre datos en memoria y tabla visual.
- **MainWindow**: orquestador; maneja selección de entidad, navegación y transiciones.

### Selección con Checkbox

- Independiente de la selección de filas del QTableView.
- Guardada en `TableModel._selected_ids`.
- Se emite `dataChanged` al limpiar selecciones para refrescar visualmente.

### Conversión Lazy de Modelos

- Los repositorios traen datos como tuplas/diccionarios de Oracle.
- Se convierten a instancias del modelo solo cuando es necesario (ej. detalle, edición).

### Gestión de Conexiones

- `OracleConnection` usa thin client de `oracledb`.
- Cada instancia abre una conexión; se recomienda usar un pool para producción.
- Las conexiones se cierran al salir (posible mejoría: usar context managers).

## Cambios Recientes (v2.0)

### Migración de Esquema
- **Antes**: Gestión de Clientes con tabla única `CLIENTE`.
- **Ahora**: Gestor de Festival de Cine con soporte para 5 entidades (`ASISTENTE`, `CIUDAD`, `SEDE`, `PELICULA`, `FUNCION`).

### Menú de Selección Dinámico
- **Antes**: La app abría directamente en la tabla de clientes.
- **Ahora**: Presenta un menú inicial (TABLAS DISPONIBLES) con botones para elegir entidad (incluyendo FUNCIONES).

### Toolbar Dinámico
- **Antes**: Acciones visibles siempre.
- **Ahora**: Acciones (`Recargar`, `Nuevo`, `Eliminar`) se ocultan en el menú y se muestran solo cuando una tabla está activa.

### Botón "Volver al Menú"
- Permite navegar de vuelta al menú sin cerrar la app.
- Ubicado en la esquina superior derecha del toolbar.

### Gestión Mejorada de Layout
- **Problema anterior**: Cambiar de tabla tras volver al menú causaba errores de Qt (`QTableView has been deleted`).
- **Solución**: Layout persistente y reutilización de instancias de widget en lugar de eliminación/recreación.

### Nueva Entidad: FUNCION (v2.1)
- Soporte completo para la tabla `FUNCION` con:
  - Modelo: `app/domain/models/funcion.py`
  - Repositorio: `app/infrastructure/repositories/funcion_repository.py`
  - ViewModel: `app/viewmodels/funcion_viewmodel.py`
  - Table Model: `app/ui/funcion_table_model.py`
  - Diálogos: `FuncionFormDialog` y `FuncionDetailDialog` en `app/ui/dialogs.py`
- Integración completa en menú de selección y flujo CRUD.
- Test E2E para verificar navegación y reutilización de widgets.

### Nueva Entidad: ASISTENCIA (v2.2)
- Soporte completo para la tabla `ASISTENCIA` (relación muchos-a-muchos entre FUNCION y ASISTENTE) con:
  - Modelo: `app/domain/models/asistencia.py`
  - Repositorio: `app/infrastructure/repositories/asistencia_repository.py`
  - ViewModel: `app/viewmodels/asistencia_viewmodel.py`
  - Table Model: `app/ui/asistencia_table_model.py`
  - Diálogos: `AsistenciaFormDialog` y `AsistenciaDetailDialog` en `app/ui/dialogs.py`
- Integración completa en menú de selección (botón ASISTENCIAS en row 2, col 1).
- Test E2E para verificar navegación y reutilización de widgets entre múltiples transiciones.
- Manejo de claves primarias compuestas (id_funcion, id_asistente).

### Nueva Entidad: JURADO (v2.3)
- Soporte completo para la tabla `JURADO` con:
  - Modelo: `app/domain/models/jurado.py`
  - Repositorio: `app/infrastructure/repositories/jurado_repository.py`
  - ViewModel: `app/viewmodels/jurado_viewmodel.py`
  - Table Model: `app/ui/jurado_table_model.py`
  - Diálogos: `JuradoFormDialog` y `JuradoDetailDialog` en `app/ui/dialogs.py`
- Integración completa en menú de selección (botón JURADOS en row 3, col 0).
- Test E2E para verificar navegación y reutilización de widgets entre múltiples transiciones.
- Campos completos: nombre, correo, especialidad, país origen, experiencia, tipo, biografía.

### Testing Ampliado
- Se añadieron scripts E2E que validan:
  - Flujos UI sin acceso a BD.
  - Cambios de tabla y navegación sin errores (incluyendo FUNCION, ASISTENCIA y JURADO).
  - CRUD para entidades específicas (Película, Función, Asistencia, Jurado, etc.).
  - Reutilización correcta de widgets QTableView tras múltiples transiciones (menu → tabla → back → tabla → back → tabla).
