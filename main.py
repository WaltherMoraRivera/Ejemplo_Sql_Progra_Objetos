"""Entry point for the PyQt6 MVVM application."""
from __future__ import annotations
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from app.ui.main_window import MainWindow


def main() -> int:
    """Run the desktop application."""

    app = QApplication(sys.argv)
    settings_path = Path(__file__).parent / "config" / "settings.json"
    window = MainWindow(settings_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

