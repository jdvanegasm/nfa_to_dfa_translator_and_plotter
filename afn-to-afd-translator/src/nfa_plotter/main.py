from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from nfa_plotter.gui import MainWindow


def run() -> None:
    """Punto de entrada principal de la aplicación."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())