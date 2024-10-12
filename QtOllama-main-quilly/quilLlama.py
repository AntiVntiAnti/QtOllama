import sys
import ollama

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSpinBox,
    QLineEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QStyleFactory,
    QMainWindow,
    QApplication,
    QTextEdit,
    QStatusBar,
    QMessageBox,
    QDialog,
    QProgressBar,
    QMenu,
    QToolButton,
    QFileDialog,)
from PyQt6.QtCore import QThread, pyqtSignal, QFileInfo, QTimer, Qt
from typing import Dict, Generator
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QCloseEvent, QAction, QFont

from utility.stats import StatsDialog

from ui.quillama_style import stylesheet
from ui.stats_dialog import HistoricalStatsDialog
from ui.wordcloud_dialog import WordCloudDialog  # assuming you save the dialog in a file named

import capabilities

# wordcloud_dialog.py
from ui.frameless_window import FramelessWindow
from utility.logger_setup import create_logger
logger = create_logger(__name__)


class MainWindow(FramelessWindow, QMainWindow):
    """
    MainWindow class represents the main application window for a chat-based interface.
    This class inherits from FramelessWindow and QMainWindow, providing a custom frameless window
    with various UI components and functionalities for interacting with an AI assistant.
    Attributes:
        menus (dict): A dictionary containing menu items and their corresponding actions.
        word_cloud_btn (QPushButton): Button to open the word cloud dialog.
        historical_stats_button (QPushButton): Button to view historical statistics.
        stats_button (QPushButton): Button to show statistics.
        stats_dialog (StatsDialog): Dialog to display statistics.
        assistant_response (str): The response from the AI assistant.
        thread (ResponseThread): Thread to handle AI responses.
        restart_button (QPushButton): Button to restart the chat.
        analytics_button (QPushButton): Button to show analytics.
        stop_button (QPushButton): Button to stop the chat.
        download_button (QPushButton): Button to download the chat as markdown.
        chat_display (QTextEdit): Text area to display chat messages.
        model_combo (QComboBox): Combo box to select the AI model.
        input_field (QLineEdit): Input field for user messages.
        send_button (QPushButton): Button to send user messages.
        word_cloud_dialog (WordCloudDialog): Dialog to display word cloud.
        historical_stats_dialog (HistoricalStatsDialog): Dialog to display historical statistics.
        context_length_spinner (QSpinBox): Spinner to set context length.
        selected_model (str): The currently selected AI model.
        messages (list): List of chat messages.
        context_length (int): The context length for the AI model.
        status_bar (QStatusBar): Status bar to display status messages.
        status_message (QLabel): Label to display status messages.
        progress_bar (QProgressBar): Progress bar to show progress.
        status_widget (QWidget): Widget to hold status bar components.
        status_layout (QHBoxLayout): Layout for the status widget.
        info_label (QLabel): Label to display information.
        toolbar (QToolBar): Toolbar for AI-related actions.
        dialogs (list): List of active dialogs.
        progress_dialog (QProgressDialog): Dialog to show progress.
        start_time (float): Start time for measuring elapsed time.
    Methods:
        __init__(): Initializes the MainWindow instance.
        init_ui(): Initializes the user interface components.
        create_menus(): Creates menus and submenus based on the provided dictionary.
        open_word_cloud(): Opens the word cloud dialog.
        view_historical_stats(): Opens the historical statistics dialog.
        update_context_length(value): Updates the context length.
        load_models(): Loads available AI models into the model combo box.
        model_changed(text): Handles changes to the selected AI model.
        send_message(): Sends a user message to the AI assistant.
        handle_response_chunk(chunk): Handles a chunk of the AI assistant's response.
        handle_response_finished(): Handles the completion of the AI assistant's response.
        handle_error(error_message): Handles errors in the response thread.
        display_message(role, content): Displays a chat message in the chat display.
        download_chat(): Downloads the chat history as a markdown file.
        show_statistics(): Shows the statistics dialog.
        update_info(): Updates the information label with text statistics.
        create_toolbars(): Creates toolbars for the application.
        update_status(status): Updates the status bar with the given status message.
        perform_ai_analysis(analysis_type): Performs AI analysis on the selected text or the last user message.
        get_last_user_message(): Returns the content of the last message sent by the user.
        get_active_window(): Returns the active editor window.
        handle_ai_result(analysis_type, result, error, settings): Handles the AI result by displaying a dialog.
        regenerate_analysis(analysis_type): Regenerates the analysis for the specified analysis type.
        show_analytics(): Shows analytics information about the chat.
        stop_chat(): Stops the chat and clears the chat display.
        restart_chat(): Restarts the chat by stopping and clearing the chat display.
    """
    def __init__(self):
        """
        Initializes the main window for the application.
        This constructor sets up the initial state of the main window, including:
        - Setting window flags to frameless.
        - Initializing various UI components to None.
        - Setting default values for certain attributes.
        - Calling methods to initialize the UI, load models, create menus, and create toolbars.
        Attributes:
            menus (None): Placeholder for menu components.
            word_cloud_btn (None): Placeholder for the word cloud button.
            historical_stats_button (None): Placeholder for the historical stats button.
            stats_button (None): Placeholder for the stats button.
            stats_dialog (None): Placeholder for the stats dialog.
            assistant_response (str): Stores the assistant's response, initialized as an empty string.
            thread (None): Placeholder for a thread object.
            restart_button (None): Placeholder for the restart button.
            analytics_button (None): Placeholder for the analytics button.
            stop_button (None): Placeholder for the stop button.
            download_button (None): Placeholder for the download button.
            chat_display (None): Placeholder for the chat display.
            model_combo (None): Placeholder for the model combo box.
            input_field (None): Placeholder for the input field.
            send_button (None): Placeholder for the send button.
            word_cloud_dialog (None): Placeholder for the word cloud dialog.
            historical_stats_dialog (None): Placeholder for the historical stats dialog.
            context_length_spinner (None): Placeholder for the context length spinner.
            selected_model (str): Stores the selected model, initialized as an empty string.
            messages (list): Stores messages, initialized as an empty list.
            context_length (int): Stores the context length, initialized to 8192.
        """
        super().__init__()
        self.menus = None
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        self.word_cloud_btn = None
        self.historical_stats_button = None
        self.stats_button = None
        self.stats_dialog = None
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
        self.word_cloud_dialog = None
        self.historical_stats_dialog = None
        self.context_length_spinner = None
        # self.create_toolbars()
        self.selected_model = ""
        self.messages = []
        self.context_length = 8192
        self.init_ui()
        self.load_models()
        self.create_menus()
        self.create_toolbars()
        
    def init_ui(self):
        """
        Initializes the user interface for the application.
        This method sets up the main widget and layout, including the following components:
        - Model selection and context length
        - Chat display
        - Input area
        - Various control buttons
        It also connects the appropriate signals to their respective slots and initializes
        the status bar and capabilities menu.
        Components:
        - main_widget: The main widget of the application.
        - main_layout: The main layout of the application.
        - top_layout: Layout for model selection and context length.
        - model_label: Label for model selection.
        - self.model_combo: ComboBox for selecting the model.
        - context_length_label: Label for context length.
        - self.chat_display: TextEdit for displaying chat messages.
        - input_layout: Layout for the input area.
        - self.input_field: LineEdit for user input.
        - self.send_button: Button to send messages.
        - button_layout: Layout for control buttons.
        - self.historical_stats_button: Button to view historical stats.
        - self.word_cloud_btn: Button to generate a word cloud.
        - self.download_button: Button to download chat as markdown.
        - self.analytics_button: Button to show analytics.
        - self.stop_button: Button to stop the chat.
        - self.restart_button: Button to restart the chat.
        - self.stats_button: Button to show statistics.
        - self.stats_dialog: Dialog for displaying statistics (initially None).
        - self.status_bar: Status bar of the application.
        - self.status_message: Label for status messages.
        - self.progress_bar: Progress bar for displaying progress.
        - self.status_widget: Widget for the status bar.
        - self.status_layout: Layout for the status widget.
        - self.info_label: Label for additional information.
        - capabilities_instance: Instance of the Capabilities class.
        - self.menus: Dictionary containing various analysis, generation, and transformation capabilities.
        """
        # ///////////////////////////////////////////////////////////////////
        # Create main widget and layout
        # ///////////////////////////////////////////////////////////////////
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # ///////////////////////////////////////////////////////////////////
        # Model selection and context length
        # ///////////////////////////////////////////////////////////////////
        top_layout = QHBoxLayout()
        model_label = QLabel("Select Model:")
        self.model_combo = QComboBox()
        context_length_label = QLabel("Context Length:")
        top_layout.addWidget(model_label)
        top_layout.addWidget(self.model_combo)
        
        # ///////////////////////////////////////////////////////////////////
        # Chat display
        # ///////////////////////////////////////////////////////////////////
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        
        # ///////////////////////////////////////////////////////////////////
        # Input area
        # ///////////////////////////////////////////////////////////////////
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("sender")
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        # ///////////////////////////////////////////////////////////////////
        # Buttons
        # ///////////////////////////////////////////////////////////////////
        button_layout = QHBoxLayout()
        self.historical_stats_button = QPushButton("View Historical Stats", self)
        self.word_cloud_btn = QPushButton("Word Cloud", self)
        self.download_button = QPushButton("Download Chat as Markdown")
        self.analytics_button = QPushButton("Show Analytics")
        self.stop_button = QPushButton("Stop Chat")
        self.restart_button = QPushButton("Restart Chat")
        self.stats_button = QPushButton("Statistics", self)
        self.stats_dialog = None
        self.status_bar = QStatusBar(self)
        self.status_message = QLabel(self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximumHeight(self.status_bar.fontMetrics().height())
        self.progress_bar.setVisible(False)
        self.status_widget = QWidget(self)
        self.status_layout = QHBoxLayout(self.status_widget)
        self.status_layout.addWidget(self.status_message)
        self.status_layout.addWidget(self.progress_bar)
        self.status_bar.addPermanentWidget(self.status_widget)
        self.info_label = QLabel(self)
        self.status_bar.addPermanentWidget(self.info_label)
        self.info_label = QLabel(self)
        self.status_bar.addPermanentWidget(self.info_label)
        self.setStatusBar(self.status_bar)
        # ///////////////////////////////////////////////////////////////////
        # Button Layout
        # ///////////////////////////////////////////////////////////////////
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.analytics_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.restart_button)
        button_layout.addWidget(self.stats_button)
        button_layout.addWidget(self.word_cloud_btn)
        button_layout.addWidget(self.historical_stats_button)
        
        # ///////////////////////////////////////////////////////////////////
        # Add layouts to main layout
        # ///////////////////////////////////////////////////////////////////
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.chat_display)
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # ///////////////////////////////////////////////////////////////////
        # Connect signals
        # ///////////////////////////////////////////////////////////////////
        self.stats_button.clicked.connect(self.show_statistics)
        self.send_button.clicked.connect(self.send_message)
        self.download_button.clicked.connect(self.download_chat)
        self.analytics_button.clicked.connect(self.show_analytics)
        self.stop_button.clicked.connect(self.stop_chat)
        self.restart_button.clicked.connect(self.restart_chat)
        self.input_field.returnPressed.connect(self.send_message)
        self.word_cloud_btn.clicked.connect(self.open_word_cloud)
        self.historical_stats_button.clicked.connect(self.view_historical_stats)
        
        capabilities_instance = capabilities.Capabilities()
        
        self.menus = {
            "Analyze": {
                "Prose": {
                    "Textual": capabilities_instance.get_prose_textual_analysis_types(),
                    "Semantic": capabilities_instance.get_prose_semantic_analysis_types(),
                    "Linguistic": capabilities_instance.get_prose_linguistic_analysis_types(),
                    "Cognitive": capabilities_instance.get_prose_cognitive_analysis_types(),
                    "Contextual": capabilities_instance.get_prose_contextual_analysis_types(),
                    "Stylistic": capabilities_instance.get_prose_stylistic_analysis_types(),
                    "Narrative": capabilities_instance.get_prose_narrative_analysis_types()
                },
                "Critical": capabilities_instance.get_critical_analysis_types(),
                "Psychoanalytical": capabilities_instance.get_psychoanalytical_analysis_types(),
                "Scientific": capabilities_instance.get_scientific_analysis_types(),
                "Philosophical": capabilities_instance.get_philosophical_analysis_types(),
                "Statistical": capabilities_instance.get_statistical_analysis_types(),
                "Opposition": capabilities_instance.get_opposition_analysis_types(),
                "Code": capabilities_instance.get_code_analysis_types(),
                "Prompt": capabilities_instance.get_prompt_analysis_types(),
                "Art Prompt": capabilities_instance.get_art_prompt_analysis_types(),
                "Poetry": capabilities_instance.get_poetry_analysis_types(),
            },
            "Generate": {
                
                "Prose": {
                    "Textual": capabilities_instance.get_prose_textual_generation_types(),
                    "Semantic": capabilities_instance.get_prose_semantic_generation_types(),
                    "Cognitive": capabilities_instance.get_prose_cognitive_generation_types(),
                    "Contextual": capabilities_instance.get_prose_contextual_generation_types(),
                    "Stylistic": capabilities_instance.get_prose_stylistic_generation_types(),
                    "Narrative": capabilities_instance.get_prose_narrative_generation_types(),
                },
                "Documentation": capabilities_instance.get_documentation_generation_types(),
                "Prompt": capabilities_instance.get_prompt_generation_types(),
                "Art Prompt": capabilities_instance.get_art_prompt_generation_types(),
                "Poetry": capabilities_instance.get_poetry_generation_types(),
                "Code": capabilities_instance.get_code_generation_types(),
            },
            "Transform": {
                "Prose": {
                    "Textual": capabilities_instance.get_prose_textual_transformation_types(),
                    "Semantic": capabilities_instance.get_prose_semantic_transformation_types(),
                    "Cognitive": capabilities_instance.get_prose_cognitive_transformation_types(),
                    "Contextual": capabilities_instance.get_prose_contextual_transformation_types(),
                    "Stylistic": capabilities_instance.get_prose_stylistic_transformation_types(),
                    "Narrative": capabilities_instance.get_prose_narrative_transformation_types(),
                },
                "Scaling": capabilities_instance.get_text_scaling_types(),
                "Enhancement": capabilities_instance.get_text_enhancement_types(),
                "Prompt": capabilities_instance.get_prompt_transformation_types(),
                "Art Prompt": capabilities_instance.get_art_prompt_transformation_types(),
                "Poetry": capabilities_instance.get_poetry_transformation_types(),
                "Code": capabilities_instance.get_code_transformation_types(),
            },
        }

    def create_menus(self):
        """
        Creates a hierarchical menu structure in the application's menu bar.

        The method iterates over the `self.menus` dictionary to dynamically
        generate menus and submenus. Each menu item is connected to the 
        `self.perform_ai_analysis` method, which is triggered when the menu 
        item is selected.

        The `self.menus` dictionary should have the following structure:
        {
            'Main Menu 1': {
            'Submenu 1': ['Option 1', 'Option 2'],
            'Submenu 2': {
                'Subsubmenu 1': ['Option 3', 'Option 4']
            }
            },
            'Main Menu 2': ['Option 5', 'Option 6']
        }

        The method supports nested submenus up to two levels deep.

        Args:
            None

        Returns:
            None
        """

        for main_menu_name, main_submenus in self.menus.items():
            main_menu = self.menuBar().addMenu(main_menu_name)
            for submenu_name, submenus in main_submenus.items():
                if isinstance(submenus, dict):
                    submenu = main_menu.addMenu(submenu_name)
                    for subsubmenu_name, options in submenus.items():
                        subsubmenu = submenu.addMenu(subsubmenu_name)
                        for option in options:
                            action = QAction(option, self)
                            action.triggered.connect(
                                lambda checked, o=option: self.perform_ai_analysis(o)
                            )
                            subsubmenu.addAction(action)
                else:
                    submenu = main_menu.addMenu(submenu_name)
                    for option in submenus:
                        action = QAction(option, self)
                        action.triggered.connect(
                            lambda checked, o=option: self.perform_ai_analysis(o)
                        )
                        submenu.addAction(action)
    
    # /////////////////////////////////////////////////////////////////////////////////////
    # WORD CLOUD
    # /////////////////////////////////////////////////////////////////////////////////////
    def open_word_cloud(self):
        """
        Opens the WordCloudDialog.

        This method initializes a WordCloudDialog with the current chat display
        and shows the dialog to the user.
        """
        self.word_cloud_dialog = WordCloudDialog(self.chat_display, self)
        self.word_cloud_dialog.show()
    
    # /////////////////////////////////////////////////////////////////////////////////////
    # HISTORICAL VIEW
    # /////////////////////////////////////////////////////////////////////////////////////
    def view_historical_stats(self):
        """
        Opens and displays the historical statistics dialog.

        This method initializes the HistoricalStatsDialog and shows it to the user.
        """
        self.historical_stats_dialog = HistoricalStatsDialog(self)
        self.historical_stats_dialog.show()
    
    # /////////////////////////////////////////////////////////////////////////////////////
    # SET CONTEXT LENGTH
    # /////////////////////////////////////////////////////////////////////////////////////
    def update_context_length(self, value):
        """
        Updates the context length with the given value.

        Args:
            value (int): The new context length to be set.

        Note:
            This method currently does not update the context length as the implementation is commented out.
            Ensure to check and set the parameter `num_ctx` to 4096 to verify if it is being sent as you change
            the context length. Refer to the API documentation for more details.

        Logs:
            Logs the updated context length.
        """                 
        pass
        # self.context_length = value
        # todo check /set parameter num_ctx 4096 to see if this is being sent as you change the
        #  context, I dont' believe it is. refer to the api docs.
        # logger.info(f"Context length updated to {self.context_length}")
    
    # /////////////////////////////////////////////////////////////////////////////////////
    # LOAD_MODELS
    # /////////////////////////////////////////////////////////////////////////////////////
    def load_models(self):
        """
        Loads available models from the Ollama API and populates the model combo box.

        This method retrieves a list of models from the Ollama API, extracts their names,
        and adds them to the model combo box. If models are successfully loaded, the first
        model is selected by default, and a signal is connected to handle model changes.
        Logs the loaded model names or an error message if the loading fails.

        Raises:
            Exception: If there is an error while loading models from the Ollama API.
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

    # /////////////////////////////////////////////////////////////////////////////////////
    # MODEL_CHANGED
    # /////////////////////////////////////////////////////////////////////////////////////
    def model_changed(self, text):
        """
        Handle the event when the model selection is changed.

        This method updates the selected model and logs the change.

        Parameters:
        text (str): The name of the newly selected model.
        """
        self.selected_model = text
        logger.info(f"Selected model changed to: {self.selected_model}")
    
    # /////////////////////////////////////////////////////////////////////////////////////
    # SEND_MESSAGE
    # /////////////////////////////////////////////////////////////////////////////////////
    def send_message(self):
        """
        Handles the event of sending a message from the user.

        This method retrieves the text from the input field, appends it to the messages list,
        displays the message in the chat display, and clears the input field. It then starts
        a new thread to get the assistant's response and connects the thread's signals to the
        appropriate handler methods.

        Attributes:
            prompt (str): The text input from the user.
            messages (list): The list of messages exchanged in the chat.
            assistant_response (str): The response from the assistant.
            thread (ResponseThread): The thread responsible for fetching the assistant's response.

        Signals:
            response_chunk_received: Emitted when a chunk of the assistant's response is received.
            response_finished: Emitted when the assistant's response is fully received.
            error_occurred: Emitted when an error occurs during the response fetching process.
        """
        prompt = self.input_field.text()
        if prompt:
            self.messages.append({"role": "user", "content": prompt})
            self.display_message("user", prompt)
            self.input_field.clear()
            logger.info(f"Sending message: {prompt}")
            self.assistant_response = ""
            self.chat_display.append("<b>Assistant:</b> ")
            # Start a thread to get the assistant's response
            self.thread = ResponseThread(self.selected_model, self.messages)
            self.thread.response_chunk_received.connect(self.handle_response_chunk)
            self.thread.response_finished.connect(self.handle_response_finished)
            self.thread.error_occurred.connect(self.handle_error)
            self.thread.start()
    
    def handle_response_chunk(self, chunk):
        """
        Handles a chunk of response from the assistant.

        This method appends the given chunk to the assistant's response,
        updates the chat display with the new chunk, and ensures that the
        cursor is visible in the chat display.

        Args:
            chunk (str): A piece of the response from the assistant.
        """
        self.assistant_response += chunk
        self.chat_display.insertPlainText(chunk)
        self.chat_display.ensureCursorVisible()
    
    def handle_response_finished(self):
        """
        Handles the completion of a response from the assistant.

        This method appends the assistant's response to the messages list with the role 
        set to "assistant" and logs that the response has finished.

        Attributes:
            self.assistant_response (str): The response content from the assistant.
        """
        self.messages.append({"role": "assistant", "content": self.assistant_response})
        logger.info("Response finished")
    
    def handle_error(self, error_message):
        """
        Handles errors by logging the error message and displaying a critical message box.

        Args:
            error_message (str): The error message to be logged and displayed.
        """
        logger.error(f"Error in response thread: {error_message}")
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")
    
    def display_message(self, role, content):
        """
        Appends a formatted message to the chat display based on the role.

        Parameters:
        role (str): The role of the message sender, either "user" or "assistant".
        content (str): The content of the message to be displayed.

        Returns:
        None
        """
        if role == "user":
            self.chat_display.append(f"<b>User:</b> {content}")
        else:
            self.chat_display.append(f"<b>Assistant:</b> {content}")
    
    def download_chat(self):
        """
        Prompts the user to save the chat messages to a file in various formats (PDF, TXT, MD, HTML).
        The method converts the chat messages into a markdown format and then allows the user to save
        the content in the chosen file format. If the user does not provide a valid extension, the 
        method defaults to saving the file as a .txt file.
        Supported file formats:
        - PDF: Saves the chat as a PDF document.
        - TXT: Saves the chat as a plain text file.
        - MD: Saves the chat as a markdown file.
        - HTML: Saves the chat as an HTML file.
        The method uses QFileDialog to prompt the user for the save location and file name.
        Raises:
            IOError: If there is an error writing to the file.
        """
        markdown_content = "\n\n".join(
            [f"**{msg['role']}**: {msg['content']}" for msg in self.messages]
        )
        options = "PDF Files (*.pdf);;Text Files (*.txt);;Markdown Files (*.md);;HTML Files (*.html)"
        filename, _ = QFileDialog.getSaveFileName(None, "Save File", "", options)
        
        if filename:
            file_extension = QFileInfo(filename).suffix().lower()
            
            if file_extension not in ["txt", "md", "html", "pdf"]:
                filename += ".txt"  # Default to .txt if no valid extension is provided
                file_extension = "txt"
            
            if file_extension == "pdf":
                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                printer.setOutputFileName(filename)
                self.chat_display.document().print(printer)
            elif file_extension in ["txt", "md"]:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(markdown_content)
            elif file_extension == "html":
                with open(filename, 'w', encoding='utf-8') as file:
                    html_content = markdown.markdown(markdown_content)
                    file.write(html_content)
    
    def show_statistics(self):
        """
        Toggles the visibility of the statistics dialog.

        If the statistics dialog is currently visible, it will be closed and set to None.
        If the statistics dialog is not visible, a new instance of StatsDialog will be created
        and displayed.

        Attributes:
            stats_dialog (StatsDialog): The dialog window displaying statistics.
            chat_display (QWidget): The widget displaying the chat content.
        """
        if self.stats_dialog is not None and self.stats_dialog.isVisible():
            self.stats_dialog.close()
            self.stats_dialog = None
        else:
            self.stats_dialog = StatsDialog(self.chat_display, self)
            self.stats_dialog.show()
    
    def update_info(self):
        """
        Updates the information label with various text statistics and interpretations.
        This method retrieves the text from the text editor, analyzes it using TextBlob and textstat,
        and updates the info label with the following information:
        - Number of characters
        - Number of words
        - Number of lines
        - Sentiment polarity and its interpretation
        - Sentiment subjectivity and its interpretation
        - Flesch reading ease score and its interpretation
        The interpretations are provided by the Interpretations class.
        Returns:
            None
        """
        text = self.text_editor.toPlainText()
        blob = TextBlob(text)
        
        sentiment_polarity = blob.sentiment.polarity
        sentiment = Interpretations.sentiment_polartiy_interpretation(sentiment_polarity)
        sentiment_subjectivity = blob.sentiment.subjectivity
        subjectivity = Interpretations.sentiment_subjectivity_interpretation(sentiment_subjectivity)
        flesch_reading_ease = textstat.flesch_reading_ease(text)
        reading_ease = Interpretations.flesch_reading_ease_interpretation(flesch_reading_ease)
        
        characters = len(text)
        words = len(text.split())
        lines = text.count("\n") + 1 if text else 0
        self.info_label.setText(
            f"Characters: {characters}, "
            f"Words: {words}, "
            f"Lines: {lines}, "
            f"Sentiment: {sentiment}, "
            f"Subjectivity: {subjectivity}, "
            f"Complexity: {reading_ease} ",
        )

    def create_toolbars(self):
        """
        Creates and configures the toolbars for the application.

        This method initializes a vertical toolbar and populates it with tool buttons
        based on the application's menu structure. Each tool button corresponds to a 
        main menu item and contains a dropdown menu with submenus and actions. The 
        actions trigger the `perform_ai_analysis` method with the respective option 
        when clicked.

        The toolbar is added to the left side of the main window.

        Attributes:
            toolbar (QToolBar): The main toolbar for the application.
        """

        self.toolbar = self.addToolBar('AI')
        self.toolbar.setOrientation(Qt.Orientation.Vertical)
        for main_menu_name, main_submenus in self.menus.items():
            tool_button = QToolButton(self)
            tool_button.setText(main_menu_name)
            tool_button.clicked.connect(tool_button.showMenu)

            menu = QMenu(self)
            for submenu_name, submenus in main_submenus.items():
                if isinstance(submenus, dict):
                    submenu = menu.addMenu(submenu_name)
                    for subsubmenu_name, options in submenus.items():
                        subsubmenu = submenu.addMenu(subsubmenu_name)
                        for option in options:
                            action = QAction(option, self)
                            action.triggered.connect(
                                lambda checked, o=option: self.perform_ai_analysis(o)
                            )
                            subsubmenu.addAction(action)
                else:
                    submenu = menu.addMenu(submenu_name)
                    for option in submenus:
                        action = QAction(option, self)
                        action.triggered.connect(
                            lambda checked, o=option: self.perform_ai_analysis(o)
                        )
                        submenu.addAction(action)

            tool_button.setMenu(menu)
            self.toolbar.addWidget(tool_button)

        # self.discuss_button = QAction("Conversation", self)
        # self.discuss_button.triggered.connect(self.discuss_with_ai)
        # self.toolbar.addAction(self.discuss_button)
        #
        # self.simulation_button = QAction("Simulation", self)
        # self.simulation_button.triggered.connect(self.start_simulation)
        # self.toolbar.addAction(self.simulation_button)

        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)
    
    def update_status(self, status):
        """
        Updates the status bar with the given status message.

        Parameters:
        - status (str): The status message to be displayed in the status bar.
        """
        self.status_bar.showMessage(status)
    
    def perform_ai_analysis(self, analysis_type):
        """
        Perform an AI analysis on the selected text or the last user message.
        This method checks if there is any selected text in the chat display. If there is, it uses the selected text;
        otherwise, it retrieves the last message sent by the user. It then creates a prompt for the AI assistant to 
        perform the specified type of analysis on the text. The prompt is added to the messages list, and the assistant's 
        response is handled in a separate thread.
        Args:
            analysis_type (str): The type of analysis to be performed on the text (e.g., sentiment analysis, summarization).
        Returns:
            None
        """

        # Check if there is selected text in the chat_display
        text_cursor = self.chat_display.textCursor()
        if text_cursor.hasSelection():
            text = text_cursor.selectedText()
        else:
            # No selection, get the last message from the user
            text = self.get_last_user_message()
            if not text:
                self.update_status("Please select text or send a message first.")
                return
        
        # Create the prompt
        prompt = f"Please perform a {analysis_type} on the following text: '{text}'"
        
        # Add the message to the messages list
        self.messages.append({"role": "user", "content": prompt})
        self.display_message("user", prompt)
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
    
    def get_last_user_message(self):
        """
        Retrieve the content of the last message sent by the user.

        This method iterates through the list of messages in reverse order and 
        returns the content of the first message found that has the role 'user'. 
        If no such message is found, it returns an empty string.

        Returns:
            str: The content of the last user message, or an empty string if no user message is found.
        """

        for msg in reversed(self.messages):
            if msg['role'] == 'user':
                return msg['content']
        return ""
    
    def get_active_window(self):
        """
        Retrieves the currently active QTextEdit widget from the active window.

        Returns:
            QTextEdit: The active QTextEdit widget if found, otherwise None.
        """

        active_window = QApplication.activeWindow()
        active_editor = (
            active_window.findChild(QTextEdit)
            if hasattr(active_window, "findChild")
            else None
        )
        return active_editor

    def handle_ai_result(self, analysis_type, result, error, settings):
        """
        Handles the AI result by displaying a dialog with the analysis type, result, elapsed time, and settings.
        If the result is not empty, a ResultDialog is created and shown.
        If there is an error, a QMessageBox with the error message is displayed.
        The progress dialog is hidden if it exists.

        Parameters:
        - analysis_type (str): The type of analysis.
        - result (any): The result of the analysis.
        - error (str): The error message, if any.
        - settings (dict): The settings for the analysis.

        Returns:
        - None
        """
        if result:
            elapsed_time = time.time() - self.start_time
            dialog = ResultDialog(analysis_type, result, elapsed_time, settings["operation_model"], self)
            dialog.regenerate.connect(lambda: self.regenerate_analysis(analysis_type))

            dialog.finished.connect(lambda: self.dialogs.remove(dialog))
            self.dialogs.append(dialog)
            dialog.show()

        elif error:
            QMessageBox.critical(self, "Error", error)

        if self.progress_dialog:
            self.progress_dialog.hide()
            self.progress_dialog = None

    def regenerate_analysis(self, analysis_type):
        """
        Regenerates the analysis for the specified analysis type.

        Parameters:
        - analysis_type (str): The type of analysis to regenerate.

        Returns:
        - None
        """
        self.perform_ai_analysis(analysis_type)
        
    def show_analytics(self):
        """
        Displays analytics information about the messages exchanged.

        This method calculates and shows the total number of messages, the number of user messages,
        the number of assistant messages, the estimated total number of tokens, and the current context length.
        The information is displayed in a message box.

        The following analytics are displayed:
        - Total messages: The total number of messages exchanged.
        - User messages: The number of messages sent by the user.
        - Assistant messages: The number of messages sent by the assistant.
        - Estimated total tokens: The total number of words in all messages.
        - Current context length: The current length of the context.

        A log entry is created to indicate that the analytics have been displayed.
        """
        user_messages = [msg['content'] for msg in self.messages if msg['role'] == 'user']
        assistant_messages = [msg['content'] for msg in self.messages if msg['role'] == 'assistant']
        total_messages = len(self.messages)
        total_tokens = sum(len(msg['content'].split()) for msg in self.messages)
        message = f"Total messages: {total_messages}\nUser messages: {len(user_messages)}\nAssistant messages: {len(assistant_messages)}\nEstimated total tokens: {total_tokens}\nCurrent context length: {self.context_length}"
        QMessageBox.information(self, "Analytics", message)
        logger.info("Analytics displayed")
    
    def stop_chat(self):
        """
        Stops the chat by terminating the running thread, clearing messages, and updating the chat display.

        This method performs the following actions:
        1. Checks if a thread is running and terminates it.
        2. Waits for the thread to finish.
        3. Clears the list of messages.
        4. Clears the chat display.
        5. Logs the action of stopping and clearing the chat.
        """
        if self.thread and self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()
        self.messages = []
        self.chat_display.clear()
        logger.info("Chat stopped and cleared")
    
    def restart_chat(self):
        """
        Restarts the chat session by first stopping the current chat and then logging the restart action.

        This method ensures that any ongoing chat session is properly terminated before initiating a new one.
        """
        self.stop_chat()
        logger.info("Chat restarted")


class ResponseThread(QThread):
    """
    ResponseThread is a QThread subclass that handles generating responses using a specified model and emits signals during the process.
    Attributes:
        response_chunk_received (pyqtSignal): Signal emitted when a chunk of the response is received.
        response_finished (pyqtSignal): Signal emitted when the entire response is received.
        error_occurred (pyqtSignal): Signal emitted when an error occurs during the response generation.
    Args:
        model_name (str): The name of the model to be used for generating responses.
        messages (list): A list of messages to be processed by the model.
    Methods:
        run(): Executes the response generation process, emitting signals for each chunk received, the final response, and any errors encountered.
    """
    response_chunk_received = pyqtSignal(str)
    response_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, model_name, messages):
        """
        Initializes the instance of the class.

        Args:
            model_name (str): The name of the model.
            messages (list): A list of messages to be copied.

        """
        super().__init__()
        self.model_name = model_name
        self.messages = messages.copy()
    
    def run(self):
        """
        Executes the ollama_generator to process messages and emit responses.

        This method runs the ollama_generator with the specified model name and messages.
        It collects the response chunks and emits signals for each chunk received and 
        when the entire response is finished. If an exception occurs during the process,
        it logs the error and emits an error signal.

        Emits:
            response_chunk_received (str): Signal emitted for each chunk of the response.
            response_finished (str): Signal emitted when the entire response is finished.
            error_occurred (Exception): Signal emitted if an error occurs.

        Raises:
            Exception: If an error occurs during the execution of the generator.
        """
        response = ""
        try:
            for chunk in ollama_generator(self.model_name, self.messages):
                response += chunk
                self.response_chunk_received.emit(chunk)
            self.response_finished.emit(response)
        except Exception as e:
            logger.error(f"Error in response thread: {e}")
            self.error_occurred.emit(e)
    
        
def ollama_generator(model_name: str, messages: Dict) -> Generator:
    """
    Generates a stream of messages from the Ollama chat model.

    Args:
        model_name (str): The name of the chat model to use.
        messages (Dict): A dictionary containing the messages to send to the model.

    Yields:
        str: The content of each message chunk from the stream.

    Raises:
        Exception: If an error occurs during the generation process, it logs the error and raises the exception.
    """
    try:
        stream = ollama.chat(
            model=model_name, messages=messages, stream=True
        )
        for chunk in stream:
            yield chunk['message']['content']
    except Exception as e:
        logger.error(f"Error in ollama_generator: {str(e)}")
        raise

        
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setStyleSheet(stylesheet)
        window = MainWindow()
        try:
            window.setStyle(QStyleFactory.create("Fusion"))
        except Exception as e:
            logger.error(f"{e}")
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Critical error: {str(e)}")
        print(f"An error occurred: {str(e)}")
