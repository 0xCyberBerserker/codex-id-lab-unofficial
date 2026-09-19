"""Disposable palette-native Qt window for isolated AT-SPI acceptance tests."""

import json
import os
import sys

from PySide6.QtCore import QCoreApplication, QTimer, QTranslator
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QVBoxLayout, QWidget


class FixtureTranslator(QTranslator):
    def __init__(self, language):
        super().__init__()
        self.messages = {
            "es": {"Accessibility fixture": "Prueba de accesibilidad", "Fixture input": "Entrada de prueba"},
            "ca": {"Accessibility fixture": "Prova d'accessibilitat", "Fixture input": "Entrada de prova"},
        }.get(language, {})

    def translate(self, context, source, disambiguation=None, n=-1):
        return self.messages.get(source, source)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("codex-lab-accessibility-fixture")
    translator = FixtureTranslator(sys.argv[1] if len(sys.argv) > 1 else "en")
    app.installTranslator(translator)
    text = lambda source: QCoreApplication.translate("Fixture", source)
    window = QWidget()
    window.setWindowTitle(text("Accessibility fixture"))
    window.setObjectName("labAccessibilityFixture")
    layout = QVBoxLayout(window)
    label = QLabel(text("Fixture input"))
    editor = QLineEdit("lab-fixture-only")
    editor.setObjectName("labFixtureInput")
    editor.setAccessibleName(text("Fixture input"))
    label.setBuddy(editor)
    layout.addWidget(label)
    layout.addWidget(editor)
    window.resize(420, 120)
    window.show()
    editor.setFocus()
    app.processEvents()
    print(json.dumps({"pid": os.getpid(), "title": window.windowTitle(),
                      "inputLabel": editor.accessibleName()}), flush=True)
    QTimer.singleShot(20000, app.quit)
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
