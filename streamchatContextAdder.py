import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QComboBox, QFileDialog, QMessageBox, QSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QFileInfo, QByteArray
import ollama
from typing import Dict, Generator
from PyQt6.QtGui import QTextDocument, QTextDocumentWriter
from PyQt6.QtPrintSupport import QPrinter
from logger_setup import create_logger
logger = create_logger(__name__)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.assistant_response = ""
        self.thread = None
        self.restart_button = None
        self.analytics_button = None
        self.stop_button = None
        self.download_button = None
        self.chat_display = None
        self.model_combo = None
        self.input_field = None
        self.send_button = None
        self.context_length_spinner = None
        self.setWindowTitle("Chat Application")

        self.selected_model = ""
        self.messages = []
        self.context_length = 4096

        self.init_ui()
        self.load_models()

    def init_ui(self):
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Model selection and context length
        top_layout = QHBoxLayout()
        model_label = QLabel("Select Model:")
        self.model_combo = QComboBox()
        context_length_label = QLabel("Context Length:")
        self.context_length_spinner = QSpinBox()
        self.context_length_spinner.setRange(1024, 12000)
        self.context_length_spinner.setSingleStep(1024)
        self.context_length_spinner.setValue(4096)
        self.context_length_spinner.valueChanged.connect(self.update_context_length)
        top_layout.addWidget(model_label)
        top_layout.addWidget(self.model_combo)
        top_layout.addWidget(context_length_label)
        top_layout.addWidget(self.context_length_spinner)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.send_button = QPushButton("Send")
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        # Buttons
        button_layout = QHBoxLayout()
        self.download_button = QPushButton("Download Chat as Markdown")
        self.analytics_button = QPushButton("Show Analytics")
        self.stop_button = QPushButton("Stop Chat")
        self.restart_button = QPushButton("Restart Chat")
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.analytics_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.restart_button)

        # Add layouts to main layout
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.chat_display)
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Connect signals
        self.send_button.clicked.connect(self.send_message)
        self.download_button.clicked.connect(self.download_chat)
        self.analytics_button.clicked.connect(self.show_analytics)
        self.stop_button.clicked.connect(self.stop_chat)
        self.restart_button.clicked.connect(self.restart_chat)
        self.input_field.returnPressed.connect(self.send_message)

    def update_context_length(self, value):
        self.context_length = value
        logging.info(f"Context length updated to {self.context_length}")

    def load_models(self):
        try:
            models = ollama.list()["models"]
            model_names = [model["name"] for model in models]
            self.model_combo.addItems(model_names)
            if model_names:
                self.selected_model = model_names[0]
                self.model_combo.currentTextChanged.connect(self.model_changed)
            logging.info(f"Loaded models: {model_names}")
        except Exception as e:
            logging.error(f"Error loading models: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load models: {str(e)}")

    def model_changed(self, text):
        self.selected_model = text
        logging.info(f"Selected model changed to: {self.selected_model}")

    def send_message(self):
        prompt = self.input_field.text()
        if prompt:
            self.messages.append({"role": "user", "content": prompt})
            self.display_message("user", prompt)
            self.input_field.clear()
            logging.info(f"Sending message: {prompt}")
            self.assistant_response = ""
            self.chat_display.append("<b>Assistant:</b> ")

            # Trim messages to fit within context length
            self.trim_messages()

            # Start a thread to get the assistant's response
            self.thread = ResponseThread(self.selected_model, self.messages)
            self.thread.response_chunk_received.connect(self.handle_response_chunk)
            self.thread.response_finished.connect(self.handle_response_finished)
            self.thread.error_occurred.connect(self.handle_error)
            self.thread.start()

    def trim_messages(self):
        total_length = sum(len(msg["content"]) for msg in self.messages)
        while total_length > self.context_length and len(self.messages) > 1:
            removed_message = self.messages.pop(0)
            total_length -= len(removed_message["content"])
        logging.info(f"Trimmed messages to fit context length. Current message count: {len(self.messages)}")

    def handle_response_chunk(self, chunk):
        self.assistant_response += chunk
        self.chat_display.insertPlainText(chunk)
        self.chat_display.ensureCursorVisible()

    def handle_response_finished(self, response):
        self.messages.append({"role": "assistant", "content": self.assistant_response})
        logging.info("Response finished")

    def handle_error(self, error_message):
        logging.error(f"Error in response thread: {error_message}")
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")

    def display_message(self, role, content):
        if role == "user":
            self.chat_display.append(f"<b>User:</b> {content}")
        else:
            self.chat_display.append(f"<b>Assistant:</b> {content}")

    def download_chat(self):
        markdown_content = "\n\n".join(
            [f"**{msg['role']}**: {msg['content']}" for msg in self.messages]
        )
        options = "PDF Files (*.pdf);;Text Files (*.txt);;Markdown Files (*.md);;HTML Files (*.html)"
        filename, _ = QFileDialog.getSaveFileName(None, "Save File", "", options)
        
        if filename:
            file_extension = QFileInfo(filename).suffix().lower()
            
            if file_extension not in ["txt", "md", "html", "pdf"]:
                filename += ".txt"  # Default to .txt if no valid extension is provided
            
            if file_extension == "pdf":
                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                printer.setOutputFileName(filename)
                self.chat_display.document().print(printer)
            else:
                with open(filename, 'w', encoding='utf-REFACTOR NOTES 8-30') as file:
                    if file_extension == "html":
                        file.write(self.current_text_edit.toHtml())
                    elif file_extension == "txt":
                        file.write(self.current_text_edit.toPlainText())
                    elif file_extension == "md":
                        file.write(self.current_text_edit.toMarkdown())
   
    
        
        
    def show_analytics(self):
        user_messages = [msg['content'] for msg in self.messages if msg['role'] == 'user']
        assistant_messages = [msg['content'] for msg in self.messages if msg['role'] == 'assistant']
        total_messages = len(self.messages)
        total_tokens = sum(len(msg['content'].split()) for msg in self.messages)
        message = f"Total messages: {total_messages}\nUser messages: {len(user_messages)}\nAssistant messages: {len(assistant_messages)}\nEstimated total tokens: {total_tokens}\nCurrent context length: {self.context_length}"
        QMessageBox.information(self, "Analytics", message)
        logging.info("Analytics displayed")

    def stop_chat(self):
        if self.thread and self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()
        self.messages = []
        self.chat_display.clear()
        logging.info("Chat stopped and cleared")

    def restart_chat(self):
        self.stop_chat()
        logging.info("Chat restarted")
        
        
class ResponseThread(QThread):
    response_chunk_received = pyqtSignal(str)
    response_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self,
                 model_name,
                 messages):
        super().__init__()
        self.model_name = model_name
        self.messages = messages.copy()
    
    def run(self):
        response = ""
        try:
            for chunk in ollama_generator(self.model_name, self.messages):
                response += chunk
                self.response_chunk_received.emit(chunk)
            self.response_finished.emit(response)
        except Exception as e:
            logging.error(f"Error in response thread: {str(e)}")
            self.error_occurred.emit(str(e))


def ollama_generator(model_name: str,
                     messages: Dict) -> Generator:
    try:
        stream = ollama.chat(
            model=model_name, messages=messages, stream=True
        )
        for chunk in stream:
            yield chunk['message']['content']
    except Exception as e:
        logging.error(f"Error in ollama_generator: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.critical(f"Critical error: {str(e)}")
        print(f"An error occurred: {str(e)}")
