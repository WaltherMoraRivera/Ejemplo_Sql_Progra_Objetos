"""UI test: compare repository data vs MainWindow table model.

Prints repository rows, model rows, and any differences.
"""
from pathlib import Path
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from app.infrastructure.database.oracle_connection import OracleConnection
from app.infrastructure.repositories.asistente_repository import AsistenteRepository
from app.ui.main_window import MainWindow


def dump_repo(conn_settings: Path):
    conn = OracleConnection.from_settings(conn_settings)
    repo = AsistenteRepository(conn)
    items = repo.get_all()
    print(f"Repository returned {len(items)} asistentes:")
    for a in items:
        print(f" - DB: id={a.id} nombre={a.nombre!r} correo={a.correo!r} telefono={a.telefono!r}")
    return items


def dump_model(window: MainWindow):
    model = window.centralWidget().model()
    rows = model.rowCount()
    print(f"Model reports {rows} rows")
    displayed = []
    for r in range(rows):
        def _unwrap(val):
            # model.data may return a QVariant wrapper; try to get the Python value
            try:
                if hasattr(val, "value"):
                    return val.value()
                if hasattr(val, "toPyObject"):
                    return val.toPyObject()
            except Exception:
                pass
            return val

        nombre = _unwrap(model.data(model.index(r, 1), Qt.ItemDataRole.DisplayRole))
        correo = _unwrap(model.data(model.index(r, 2), Qt.ItemDataRole.DisplayRole))
        telefono = _unwrap(model.data(model.index(r, 3), Qt.ItemDataRole.DisplayRole))
        print(f" - VIEW: row={r} nombre={nombre} correo={correo} telefono={telefono}")
        displayed.append((str(nombre), str(correo), str(telefono)))
    return displayed


def main():
    settings = Path("config/settings.json")
    print("Using settings:", settings.resolve())

    repo_items = dump_repo(settings)

    app = QApplication(sys.argv)
    window = MainWindow(settings)
    # Ensure model is loaded
    window._viewmodel.load_asistentes()

    displayed = dump_model(window)

    # Compare counts
    repo_tuples = [(str(a.nombre), str(a.correo), str(a.telefono)) for a in repo_items]
    if len(repo_tuples) != len(displayed):
        print("[DIFF] Count mismatch: repo vs view", len(repo_tuples), len(displayed))
    else:
        print("Counts match.")

    # Find mismatches per-row by id matching if possible
    id_to_repo = {a.id: a for a in repo_items}
    # try match by name/email
    mismatches = []
    for r in range(len(displayed)):
        view = displayed[r]
        # try find repo entry with same name
        matches = [a for a in repo_items if (str(a.nombre), str(a.correo), str(a.telefono)) == view]
        if not matches:
            mismatches.append((r, view))
    if mismatches:
        print(f"Found {len(mismatches)} mismatched view rows:")
        for m in mismatches:
            print(" - row", m[0], "->", m[1])
    else:
        print("No mismatches found between repo and view rows.")

    print("UI test finished.")

if __name__ == '__main__':
    main()
