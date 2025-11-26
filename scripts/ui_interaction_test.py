from pathlib import Path
import sys
import os

# Ensure repository root is on sys.path so `app` package can be imported
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from PyQt6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.infrastructure.database.oracle_connection import OracleConnection


def main():
    # Prevent OracleConnection from attempting a real DB connection during this UI test
    OracleConnection.from_settings = staticmethod(lambda p: None)

    app = QApplication([])
    mw = MainWindow(Path("config/settings.json"))
    # Show the window so visibility checks reflect actual widget state
    mw.show()
    app.processEvents()

    results = {}

    # Initial state: toolbar actions and back button should be hidden
    results["initial_refresh_visible"] = mw._refresh_action.isVisible()
    results["initial_new_visible"] = mw._new_action.isVisible()
    results["initial_delete_visible"] = mw._delete_action.isVisible()
    results["initial_back_visible"] = mw._back_button.isVisible()

    # Simulate selecting 'pelicula'
    try:
        mw._set_entity("pelicula")
        app.processEvents()
        results["after_select_refresh_visible"] = mw._refresh_action.isVisible()
        results["after_select_new_visible"] = mw._new_action.isVisible()
        results["after_select_delete_visible"] = mw._delete_action.isVisible()
        results["after_select_back_visible"] = mw._back_button.isVisible()
        results["title_after_select"] = mw.windowTitle()
    except Exception as exc:
        results["select_exception"] = str(exc)

    # Simulate clicking back
    try:
        mw._back_to_menu()
        app.processEvents()
        results["after_back_refresh_visible"] = mw._refresh_action.isVisible()
        results["after_back_new_visible"] = mw._new_action.isVisible()
        results["after_back_delete_visible"] = mw._delete_action.isVisible()
        results["after_back_back_visible"] = mw._back_button.isVisible()
        results["title_after_back"] = mw.windowTitle()
    except Exception as exc:
        results["back_exception"] = str(exc)

    # Print a concise report
    for k, v in results.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
