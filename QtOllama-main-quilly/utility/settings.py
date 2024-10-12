import json
import os

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QLabel, QLineEdit, QHBoxLayout, QRadioButton, QPushButton, \
    QFontDialog


def load_settings():
    """
    Loads the available models from the Ollama service and populates the model combo box with the model names.
    Sets the first model as the selected model and connects the combo box's currentTextChanged signal to the model_changed method.
    Logs the loaded models or an error if the loading fails.

    Raises:
        Exception: If there is an error loading the models, it logs the error and shows a critical message box.

    """
    try:
        models = ollama.list()["models"]
        model_names = [model["name"] for model in models]
        self.model_combo.addItems(model_names)
        if model_names:
            self.selected_model = model_names[0]
            self.model_combo.currentTextChanged.connect(self.model_changed)
        logger.info(f"Loaded models: {model_names}")
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        QMessageBox.critical(self, "Error", f"Failed to load models: {str(e)}")

class SettingsDialog(QDialog):
    """
    A dialog window for updating application settings.

    Signals:
        updated: Emitted when settings are updated.

    Methods:
        __init__(parent=None):
            Initializes the settings dialog.
        
        choose_font():
            Opens a font dialog to choose a font and updates the font fields.
        
        load_settings():
            Loads the settings from a persistent storage.
    """
    updated = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(500, 200)  # specify dialog size

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)



        self.load_settings()

    def choose_font(self):
        current_font = self.font_field.text() or "Helvetica"
        current_font_size = int(self.font_size_field.text() or 14)
        current_font = QFont(current_font, current_font_size)
        font, valid = QFontDialog.getFont(current_font, self, "Choose Font")
        if valid:
            self.font_field.setText(font.family())
            self.font_size_field.setText(str(font.pointSize()))


    def load_settings(self):
        settings = load_settings()
