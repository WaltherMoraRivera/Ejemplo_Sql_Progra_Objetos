"""E2E UI flow test: menu → select table → back → select another table, etc."""
from pathlib import Path
import sys
import os

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from PyQt6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.infrastructure.database.oracle_connection import OracleConnection


def test_ui_flow():
    """Test a complete UI flow without DB access."""
    # Prevent OracleConnection from attempting a real DB connection
    OracleConnection.from_settings = staticmethod(lambda p: None)

    app = QApplication([])
    mw = MainWindow(Path("config/settings.json"))
    mw.show()
    app.processEvents()

    results = {}
    step = 0

    # Step 1: Initial menu state
    step += 1
    results[f"step{step}_initial_title"] = mw.windowTitle()
    results[f"step{step}_initial_entity"] = mw._entity
    results[f"step{step}_actions_visible"] = mw._refresh_action.isVisible()

    # Step 2: Select PELÍCULAS
    step += 1
    try:
        mw._set_entity("pelicula")
        app.processEvents()
        results[f"step{step}_after_pelicula_title"] = mw.windowTitle()
        results[f"step{step}_after_pelicula_entity"] = mw._entity
        results[f"step{step}_actions_visible"] = mw._refresh_action.isVisible()
        results[f"step{step}_table_visible"] = mw._table.isVisible()
    except Exception as exc:
        results[f"step{step}_exception"] = str(exc)

    # Step 3: Back to menu
    step += 1
    try:
        mw._back_to_menu()
        app.processEvents()
        results[f"step{step}_after_back_title"] = mw.windowTitle()
        results[f"step{step}_after_back_entity"] = mw._entity
        results[f"step{step}_actions_visible"] = mw._refresh_action.isVisible()
        results[f"step{step}_table_visible"] = mw._table.isVisible()
    except Exception as exc:
        results[f"step{step}_exception"] = str(exc)

    # Step 4: Select ASISTENTES (should not crash)
    step += 1
    try:
        mw._set_entity("asistente")
        app.processEvents()
        results[f"step{step}_after_asistente_title"] = mw.windowTitle()
        results[f"step{step}_after_asistente_entity"] = mw._entity
        results[f"step{step}_actions_visible"] = mw._refresh_action.isVisible()
        results[f"step{step}_table_visible"] = mw._table.isVisible()
    except Exception as exc:
        results[f"step{step}_exception"] = str(exc)

    # Step 5: Back to menu again
    step += 1
    try:
        mw._back_to_menu()
        app.processEvents()
        results[f"step{step}_after_back2_title"] = mw.windowTitle()
        results[f"step{step}_after_back2_entity"] = mw._entity
        results[f"step{step}_actions_visible"] = mw._refresh_action.isVisible()
    except Exception as exc:
        results[f"step{step}_exception"] = str(exc)

    # Step 6: Select CIUDADES
    step += 1
    try:
        mw._set_entity("ciudad")
        app.processEvents()
        results[f"step{step}_after_ciudad_title"] = mw.windowTitle()
        results[f"step{step}_after_ciudad_entity"] = mw._entity
        results[f"step{step}_actions_visible"] = mw._refresh_action.isVisible()
    except Exception as exc:
        results[f"step{step}_exception"] = str(exc)

    # Step 7: Back to menu for final check
    step += 1
    try:
        mw._back_to_menu()
        app.processEvents()
        results[f"step{step}_final_title"] = mw.windowTitle()
        results[f"step{step}_final_entity"] = mw._entity
        results[f"step{step}_final_actions_visible"] = mw._refresh_action.isVisible()
    except Exception as exc:
        results[f"step{step}_exception"] = str(exc)

    # Print results
    for k, v in sorted(results.items()):
        print(f"{k}: {v}")

    # Check for success
    has_exceptions = any("exception" in k for k in results.keys())
    if has_exceptions:
        print("\n❌ E2E UI Flow Test FAILED: One or more exceptions occurred.")
        return False
    else:
        print("\n✅ E2E UI Flow Test PASSED: All transitions completed without errors.")
        return True


if __name__ == "__main__":
    success = test_ui_flow()
    sys.exit(0 if success else 1)
