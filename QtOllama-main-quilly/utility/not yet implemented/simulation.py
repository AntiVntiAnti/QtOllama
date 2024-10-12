import logging
import time
import traceback

import openai
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QDialog,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QStatusBar,
    QProgressBar,
    QLabel,
    QVBoxLayout,
    QCheckBox,
    QGroupBox,
    QGridLayout,
    QMessageBox,
)

from settings import load_settings


class SimWorker(QThread):
    """
    SimWorker is a QThread subclass that handles asynchronous communication with the OpenAI API.

    Signals:
        new_message (str, bool, float): Emitted when a HammerAI-lama-3_1-storm-latest message chunk is received.
        complete_message (str, float): Emitted when a complete message is received.
        error (str): Emitted when an error occurs.

    Attributes:
        messages (list): A list of messages to be sent to the OpenAI API.

    Methods:
        __init__(messages: list):
            Initializes the SimWorker with a list of messages.
        
        run():
            Executes the thread, sending messages to the OpenAI API and emitting signals based on the responses.
    """
    new_message = pyqtSignal(str, bool, float)
    complete_message = pyqtSignal(str, float)
    error = pyqtSignal(str)

    def __init__(self, messages: list):
        """
        Initializes the simulation thread with a list of messages.

        Args:
            messages (list): A list of messages to be processed by the simulation.
        """
        QThread.__init__(self)
        self.messages = messages

    def run(self):
        start_time = time.time()

        try:
            settings = load_settings()
            openai.api_key = settings["api_key"]
            logging.debug("OpenAI Request: {}".format(self.messages))

            responses = openai.ChatCompletion.create(
                model=settings["conversation_model"],
                messages=self.messages,
                temperature=0.6,
                stream=True,
            )

            first_chunk = True
            result = ""

            for response in responses:
                choice = response.get("choices", [{}])[0]
                delta = choice.get("delta", {})
                content = delta.get("content")

                if content:
                    result += content
                    self.new_message.emit(content, first_chunk, start_time)
                    if first_chunk:
                        first_chunk = False

                finish_reason = choice.get("finish_reason")
                if finish_reason:
                    self.complete_message.emit(result, start_time)
                    result = ""
                    first_chunk = True
        except Exception as e:
            self.error.emit(
                f"Error on sim worker: {e}, Trace: {traceback.format_exc()}"
            )


logging.basicConfig(level=logging.DEBUG)


class SimulationDialog(QDialog):
    """
    SimulationDialog is a custom QDialog that facilitates a turn-based, role-playing simulation with a language model.

    Attributes:
        messages (list): A list to store messages.
        ai_response_edit (QTextEdit): A text edit widget to display AI responses.
        user_input_edit (QLineEdit): A line edit widget for user input.
        send_button (QPushButton): A button to send user input.
        input_layout (QHBoxLayout): A horizontal layout for user input and send button.
        status_bar (QStatusBar): A status bar to display progress and status messages.
        progress_bar (QProgressBar): A progress bar to show simulation progress.
        status_message (QLabel): A label to display status messages.
        layout (QVBoxLayout): A vertical layout for the dialog.
        conversation_history (list): A list to store the conversation history.
        text_editor (QTextEdit): A text editor widget to get initial content for the simulation.
        sim_worker (SimWorker): A worker thread to process the simulation.

    Methods:
        __init__(self, text_editor, parent=None): Initializes the SimulationDialog.
        get_editor_contents(self): Returns the contents of the text editor.
        initialize_simulation(self): Initializes the simulation parameters dialog.
        on_start_simulation_clicked(self): Handles the start simulation button click.
        process_sim_worker(self): Processes the simulation worker thread.
        handle_dialog_finished(self, result): Handles the dialog finished event.
        handle_worker_error(self, error_message): Handles errors from the worker thread.
        send_user_input(self, user_text=None): Sends user input to the simulation.
        update_ai_response(self, ai_response, is_complete_message, start_time): Updates the AI response in the text edit.
        update_conversation_history(self, full_response, start_time): Updates the conversation history with the AI response.
    """
    def __init__(self, text_editor, parent=None):
        """
        Initializes the simulation window for interacting with the LLM.

        Args:
            text_editor (QTextEdit): The text editor instance used for displaying and editing text.
            parent (QWidget, optional): The parent widget of this window. Defaults to None.

        Attributes:
            messages (list): A list to store messages exchanged during the simulation.
            ai_response_edit (QTextEdit): A read-only text edit widget to display AI responses.
            user_input_edit (QLineEdit): A line edit widget for user input.
            send_button (QPushButton): A button to send user input.
            input_layout (QHBoxLayout): A horizontal layout to arrange user input widgets.
            status_bar (QStatusBar): A status bar to display status messages and progress.
            progress_bar (QProgressBar): A progress bar to indicate ongoing processes.
            status_message (QLabel): A label to display status messages.
            layout (QVBoxLayout): A vertical layout to arrange the main components of the window.
            conversation_history (list): A list to store the history of the conversation.
            text_editor (QTextEdit): The text editor instance used for displaying and editing text.
        """
        super().__init__(parent)
        self.messages = []
        self.setWindowTitle("Simulation with LLM")

        self.ai_response_edit = QTextEdit(self)
        self.ai_response_edit.setReadOnly(True)
        self.ai_response_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.ai_response_edit.setStyleSheet(
            "QTextEdit {background-color: #003366; color: #ffffff;}"
        )

        self.user_input_edit = QLineEdit(self)
        self.user_input_edit.setStyleSheet(
            "QLineEdit {background-color: #003366; color: #ffffff;}"
        )
        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_user_input)
        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.user_input_edit)
        self.input_layout.addWidget(self.send_button)

        self.status_bar = QStatusBar(self)
        self.progress_bar = QProgressBar(self)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.progress_bar.setRange(0, 0)

        self.status_message = QLabel(self)
        self.status_bar.addPermanentWidget(self.status_message)
        self.status_bar.setSizeGripEnabled(False)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.ai_response_edit)
        self.layout.addLayout(self.input_layout)
        self.layout.addWidget(self.status_bar)

        self.setLayout(self.layout)

        self.resize(600, 400)

        self.conversation_history = []

        self.text_editor = text_editor
        self.initialize_simulation()

    def get_editor_contents(self):
        """
        Retrieves the current contents of the text editor.

        Returns:
            str: The current text within the text editor.
        """
        return self.text_editor.toPlainText()

    def initialize_simulation(self):
        """
        Initializes the simulation dialog for setting up simulation parameters.

        This method creates a dialog window with various input fields for the user to specify
        parameters for the simulation, including character, location, year, and scenario notes.
        It also includes an option to include text editor contents in the simulation.

        The dialog contains the following input fields:
        - Character: A required field where the user specifies who they want to be in the simulation.
        - Location: An optional field where the user specifies where the simulation takes place.
        - Year: An optional field where the user specifies the year of the simulation.
        - Scenario Notes: An optional field for any additional scenario notes.
        - Include Text Editor Contents: A checkbox to include the contents of the text editor.

        If the dialog is accepted, the method retrieves the input values, constructs a system message
        and an initial user message, and updates the conversation history with these messages. It then
        calls the `process_sim_worker` method to start the simulation.

        The dialog is styled with a specific color scheme for the input fields.

        Returns:
            None
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Simulation Parameters")

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        groupBox = QGroupBox("Simulation Parameters")
        layout.addWidget(groupBox)

        grid = QGridLayout()
        groupBox.setLayout(grid)

        self.character_label = QLabel("Who do you want to be in the simulation?")
        self.character_edit = QLineEdit()
        self.character_edit.setStyleSheet(
            "QLineEdit {background-color: #003366; color: #ffffff;}"
        )
        self.character_edit.setPlaceholderText("Required")
        grid.addWidget(self.character_label, 0, 0)
        grid.addWidget(self.character_edit, 0, 1)

        location_label = QLabel("Where do you want the simulation to take place?")
        location_edit = QLineEdit()
        location_edit.setStyleSheet("QLineEdit {background-color: #003366; color: #ffffff;}")
        location_edit.setPlaceholderText("Optional")
        grid.addWidget(location_label, 1, 0)
        grid.addWidget(location_edit, 1, 1)

        year_label = QLabel("In what year should the simulation take place?")
        year_edit = QLineEdit()
        year_edit.setStyleSheet("QLineEdit {background-color: #003366; color: #ffffff;}")
        year_edit.setPlaceholderText("Optional")
        grid.addWidget(year_label, 2, 0)
        grid.addWidget(year_edit, 2, 1)

        scenario_label = QLabel("Include any scenario notes?")
        scenario_edit = QTextEdit()
        scenario_edit.setStyleSheet("QTextEdit {background-color: #003366; color: #ffffff;}")
        scenario_edit.setPlaceholderText("Optional")
        grid.addWidget(scenario_label, 3, 0)
        grid.addWidget(scenario_edit, 3, 1)

        include_editor_checkbox = QCheckBox("Include text editor contents")
        include_editor_checkbox.setDisabled(not self.get_editor_contents().strip())
        grid.addWidget(include_editor_checkbox, 4, 0)

        button = QPushButton("Begin Simulation")
        layout.addWidget(button)
        button.clicked.connect(dialog.accept)

        dialog.finished.connect(self.handle_dialog_finished)


        if dialog.exec():

            character = self.character_edit.text()

            location = (
                location_edit.text()
                if location_edit.text().strip()
                else "undisclosed location"
            )
            year = (
                int(year_edit.text())
                if year_edit.text().strip()
                else "unspecified time"
            )

            scenario_notes = (
                scenario_edit.toPlainText() if scenario_edit.toPlainText().strip() else None
            )

            include_editor_contents = include_editor_checkbox.isChecked()


            self.setWindowTitle(f"Simulation: {character}—{location}—{year}")

            system_message = """Function as a turn-based, role-playing simulation. Remember, this is a game of interaction, 
                                and after every turn, the simulation will pause allowing the user to interact. The simulation 
                                will never break out of the scenario."""

            if scenario_notes is not None:
                system_message += (
                    f"\n\nAdditional simulation scenario notes: {scenario_notes}"
                )

            if include_editor_contents:
                editor_contents = self.get_editor_contents()
                system_message += f"\n\nAdditional information: {editor_contents}"

            initial_user_message = f"\n\nIn this simulation, I am {character.strip()}, currently in {location.strip()}, and the year is {str(year)}. Begin the simulation."


            self.conversation_history.extend(
                [
                    {
                        "role": "system",
                        "content": system_message,
                    },
                    {"role": "user", "content": initial_user_message},
                ]
            )
            self.process_sim_worker()

    def on_start_simulation_clicked(self):
        """
        Slot function to handle the event when the "Start Simulation" button is clicked.

        This function checks if the character name field is empty. If it is, it displays
        an error message prompting the user to provide a character name and prevents
        the simulation from starting.

        Returns:
            None
        """
        if not self.character_edit.text().strip():
            msg = QMessageBox(QMessageBox.Icon.Critical, "Missing Required Field", "Please provide a character name.")
            msg.exec()
            return
            dialog.accept()
        button.clicked.connect(on_start_simulation_clicked)


    def process_sim_worker(self):
        """
        Initializes and starts the simulation worker thread, connecting necessary signals
        for handling HammerAI-lama-3_1-storm-latest messages, completion, and errors. If a simulation worker already
        exists, it is properly terminated and disconnected before creating a HammerAI-lama-3_1-storm-latest one.

        Attributes:
            sim_worker (SimWorker): The worker thread responsible for processing the simulation.
            conversation_history (list): The history of the conversation to be processed by the worker.

        Methods:
            update_ai_response: Slot to handle HammerAI-lama-3_1-storm-latest messages from the worker.
            update_conversation_history: Slot to handle the completion of the worker's task.
            handle_worker_error: Slot to handle any errors that occur in the worker.
        """
        self.progress_bar.show()
        if hasattr(self, "sim_worker"):
            self.sim_worker.quit()
            self.sim_worker.new_message.disconnect()
            self.sim_worker.error.disconnect()
            self.sim_worker.complete_message.disconnect()

        self.sim_worker = SimWorker(self.conversation_history)
        self.sim_worker.new_message.connect(self.update_ai_response)
        self.sim_worker.complete_message.connect(self.update_conversation_history)
        self.sim_worker.error.connect(self.handle_worker_error)
        self.sim_worker.start()

    @pyqtSlot(int)
    def handle_dialog_finished(self, result):
        """
        Handles the event when a dialog is finished.

        Parameters:
        result (QDialog.DialogCode): The result code of the dialog, indicating whether it was accepted or rejected.

        If the dialog was rejected, the method will close the current window.
        """
        if result == QDialog.DialogCode.Rejected:
            self.close()

    @pyqtSlot(str)
    def handle_worker_error(self, error_message):
        """
        Handles errors encountered by a worker.

        Args:
            error_message (str): The error message to be printed and logged.

        Side Effects:
            Prints the error message to the console.
            Updates the status message to indicate an error has occurred.
        """
        print(error_message)
        self.status_message.setText("An error occurred. Please view logs.")

    def send_user_input(self, user_text=None):
        """
        Handles the user input, appends it to the conversation history, updates the UI, 
        and triggers the processing of the simulation worker.

        Parameters:
        user_text (str, optional): The text input from the user. If not provided, 
                       it defaults to the text from the user_input_edit widget.

        Returns:
        None
        """
        user_text = user_text or self.user_input_edit.text()
        if user_text.strip():
            new_message = {"role": "user", "content": user_text}
            self.conversation_history.append(new_message)
            self.ai_response_edit.append("\n👤 " + user_text)
            self.user_input_edit.clear()
            self.process_sim_worker()

    def update_ai_response(self, ai_response, is_complete_message, start_time):
        """
        Updates the AI response in the text editor.

        Parameters:
        ai_response (str): The response generated by the AI.
        is_complete_message (bool): Flag indicating if the message is complete.
        start_time (float): The start time of the response generation.

        Returns:
        None
        """
        if ai_response.strip() != "":
            if is_complete_message:
                ai_response = "\n\n🌐 " + ai_response
            self.ai_response_edit.insertPlainText(ai_response)
            self.ai_response_edit.moveCursor(QTextCursor.MoveOperation.End)
            self.ai_response_edit.ensureCursorVisible()

    @pyqtSlot(str, float)
    def update_conversation_history(self, full_response, start_time):
        """
        Updates the conversation history with a HammerAI-lama-3_1-storm-latest message from the assistant and performs UI updates.

        Args:
            full_response (str): The full response content from the assistant.
            start_time (datetime): The start time of the conversation or response generation.

        Returns:
            None
        """
        new_message = {"role": "assistant", "content": full_response.strip()}
        self.conversation_history.append(new_message)
        self.ai_response_edit.ensureCursorVisible()

        self.progress_bar.hide()
