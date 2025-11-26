"""E2E UI flow test including the new FUNCION entity."""
from pathlib import Path
import sys

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from PyQt6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.infrastructure.database.oracle_connection import OracleConnection


def test_ui_flow_with_funcion():
    """Test UI flow including FUNCION entity selection."""
    # Prevent OracleConnection from attempting a real DB connection
    OracleConnection.from_settings = staticmethod(lambda p: None)

    app = QApplication([])
    mw = MainWindow(Path("config/settings.json"))
    mw.show()
    app.processEvents()

    results = {}
    step = 0

    # Step 1: Verify initial menu shows 5 buttons (including FUNCIONES)
    step += 1
    results[f"step{step}_title"] = mw.windowTitle()
    results[f"step{step}_entity"] = mw._entity

    # Step 2: Select FUNCIONES
    step += 1
    try:
        mw._set_entity("funcion")
        app.processEvents()
        results[f"step{step}_title"] = mw.windowTitle()
        results[f"step{step}_entity"] = mw._entity
        results[f"step{step}_actions_visible"] = mw._refresh_action.isVisible()
        results[f"step{step}_table_visible"] = mw._table.isVisible()
    except Exception as exc:
        results[f"step{step}_exception"] = str(exc)

    # Step 3: Back to menu
    step += 1
    try:
        mw._back_to_menu()
        app.processEvents()
        results[f"step{step}_title"] = mw.windowTitle()
        results[f"step{step}_entity"] = mw._entity
        results[f"step{step}_actions_visible"] = mw._refresh_action.isVisible()
    except Exception as exc:
        results[f"step{step}_exception"] = str(exc)

    # Step 4: Select PELICULA, then back, then FUNCION again (to verify reusability)
    step += 1
    try:
        mw._set_entity("pelicula")
        app.processEvents()
        results[f"step{step}_after_pelicula"] = mw.windowTitle()
    except Exception as exc:
        results[f"step{step}_exception"] = str(exc)

    step += 1
    try:
        mw._back_to_menu()
        app.processEvents()
        results[f"step{step}_back_to_menu"] = mw.windowTitle()
    except Exception as exc:
        results[f"step{step}_exception"] = str(exc)

    step += 1
    try:
        mw._set_entity("funcion")
        app.processEvents()
        results[f"step{step}_funcion_again_title"] = mw.windowTitle()
        results[f"step{step}_funcion_again_entity"] = mw._entity
    except Exception as exc:
        results[f"step{step}_exception"] = str(exc)

    # Print results
    for k, v in sorted(results.items()):
        print(f"{k}: {v}")

    # Check for success
    has_exceptions = any("exception" in k for k in results.keys())
    if has_exceptions:
        print("\n❌ E2E UI Flow Test with FUNCION FAILED: One or more exceptions occurred.")
        return False
    else:
        print("\n✅ E2E UI Flow Test with FUNCION PASSED: All transitions completed without errors.")
        return True


if __name__ == "__main__":
    success = test_ui_flow_with_funcion()
    sys.exit(0 if success else 1)
