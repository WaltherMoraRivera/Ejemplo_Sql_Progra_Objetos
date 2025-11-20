# Gestión de Clientes PyQt6

Aplicación de escritorio basada en PyQt6 que consume procedimientos almacenados de Oracle Autonomous Database para listar, crear y eliminar clientes. El proyecto sigue una estructura **MVVM** (Modelo–Vista–VistaModelo) y separa la interfaz, la lógica de presentación y el acceso a datos.

## Requisitos previos

- Python 3.11+
- Dependencias del proyecto (instalar con `pip install -r requirements.txt`).
- Wallet de Oracle Autonomous Database configurado.

### Configurar Oracle Autonomous Database

1. Descomprime tu wallet en `config/wallet` (archivos `tnsnames.ora`, `cwallet.sso`, etc.).
2. Ajusta las credenciales en `config/settings.json` (`user`, `password`, `dsn`, `wallet_dir`, `wallet_password` si aplica).
3. El alias `dsn` debe existir en `tnsnames.ora`.

`OracleConnection` resuelve rutas relativas a `config/` o a la raíz del proyecto y valida que el directorio del wallet exista. Si no lo encuentra, se lanza un `FileNotFoundError` con un mensaje aclaratorio.

## Estructura principal

- `main.py`: punto de entrada; crea `QApplication`, carga la configuración y abre `MainWindow`.
- `app/domain/models/cliente.py`: modelo de dominio `Cliente` usado en todas las capas.
- `app/infrastructure/database/oracle_connection.py`: factoría de conexiones a Oracle.
- `app/infrastructure/repositories/cliente_repository.py`: capa de repositorio que encapsula los procedimientos almacenados (`SP_GET_CLIENTES`, `SP_GET_CLIENTE_BY_ID`, `SP_INSERT_CLIENTE`, `SP_UPDATE_CLIENTE`, `SP_DELETE_CLIENTE`).
- `app/viewmodels/cliente_viewmodel.py`: lógica de presentación que orquesta el flujo de datos entre la UI y el repositorio.
- `app/ui/*`: componentes de interfaz (`MainWindow`, tabla, diálogos, delegados).

## Flujo de datos y responsabilidades

### Carga inicial y refresco

1. `MainWindow` crea `OracleConnection` con `settings.json` y construye `ClienteRepository` y `ClienteViewModel`.
2. Al inicializar la ventana se invoca `ClienteViewModel.load_clientes()`, que llama a `ClienteRepository.get_all()`.
3. `get_all()` ejecuta `SP_GET_CLIENTES` y mapea cada fila a `Cliente`; el resultado viaja al `ViewModel` y se emite la señal `clientes_changed`.
4. `ClienteTableModel.update_clientes()` recibe la lista y refresca la tabla, manteniendo los checkboxes seleccionados que aún existan.

### Crear (insert) un cliente

1. Botón **Nuevo** abre `ClienteFormDialog`, que valida campos (RUT numérico, DV de un carácter, email con regex, etc.).
2. Al aceptar, se arma un `Cliente` sin `id` con los datos del formulario.
3. `ClienteViewModel.add_cliente()` invoca `ClienteRepository.add(cliente)`, que llama a `SP_INSERT_CLIENTE` y hace `commit` de la transacción. El procedimiento devuelve el nuevo `id`.
4. Tras insertar, el `ViewModel` vuelve a cargar la lista (`load_clientes`) y la tabla se actualiza; también se limpian las selecciones de checkboxes.

### Eliminar clientes (uno o varios)

1. La primera columna de la tabla (`ClienteTableModel.SELECT_COLUMN`) muestra un checkbox por fila. El modelo guarda los IDs seleccionados en `_selected_ids` cuando el usuario marca una casilla.
2. El botón **Eliminar** en `MainWindow` llama a `_handle_delete_selected`, que reúne los IDs mediante `ClienteTableModel.get_selected_ids()`.
3. Tras confirmar, `ClienteViewModel.delete_clientes()` ejecuta `ClienteRepository.delete_many()`. Este método recorre los IDs y llama al procedimiento `SP_DELETE_CLIENTE` por cada uno, haciendo `commit` al final.
4. Si la operación es exitosa, se recarga la tabla y se limpian las selecciones.

### Ver detalle

- La última columna usa `DetailButtonDelegate`, que dibuja un botón "Detalle" en cada fila. Al hacer clic, `MainWindow` abre `ClienteDetailDialog` con todos los datos del `Cliente` correspondiente.

## Selección con checkboxes

- La selección es independiente del `QTableView` y se maneja en `ClienteTableModel.setData()` con el rol `CheckStateRole`.
- Solo se pueden marcar filas que tengan `id` (evita seleccionar registros todavía no persistidos).
- `clear_selection()` emite `dataChanged` para actualizar visualmente los checkboxes al limpiar.

## Ejecución

```bash
python main.py
```

Al iniciar se mostrará la ventana "Gestión de Clientes" con acciones **Recargar**, **Nuevo** y **Eliminar**, más los botones de detalle por fila.

