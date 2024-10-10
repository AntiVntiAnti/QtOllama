import textstat as textstat
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QDialog, \
    QTextEdit, \
    QVBoxLayout, \
    QTableWidget, \
    QTableWidgetItem, \
    QHeaderView
from nltk import word_tokenize
from textblob import TextBlob

from interpretations import Interpretations


class StatsDialog(QDialog):
    """
    A dialog window that displays real-time text statistics for a given QTextEdit widget.

    Attributes:
        text_edit_widget (QTextEdit): The QTextEdit widget whose text is analyzed.
        table (QTableWidget): The table widget displaying the statistics.
        timer (QTimer): Timer to update statistics at regular intervals.

    Methods:
        __init__(text_edit_widget: QTextEdit, parent=None):
            Initializes the StatsDialog with the given QTextEdit widget and parent.

        update_statistics():
            Updates the statistics based on the current text in the QTextEdit widget.
    """
    
    def __init__(self,
                 text_edit_widget: QTextEdit,
                 parent=None):
        """
        Initializes the statistics window for real-time text analysis.

        Args:
            text_edit_widget (QTextEdit): The text edit widget to analyze.
            parent (optional): The parent widget. Defaults to None.

        Attributes:
            text_edit_widget (QTextEdit): The text edit widget to analyze.
            table (QTableWidget): The table widget displaying statistics.
            timer (QTimer): The timer for updating statistics every second.
        """
        super().__init__(parent)
        self.text_edit_widget = text_edit_widget
        
        self.setWindowTitle("Real-Time Text Statistics")
        self.resize(600, 600)
        layout = QVBoxLayout()
        
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Statistic", "Raw Value", "Interpretation"])
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_statistics)
        self.timer.start(1000)
    
    def update_statistics(self):
        """
        Updates the statistics of the text in the text_edit_widget and displays them in the table.

        This method performs the following operations:
        - Tokenizes the text and calculates total and unique tokens.
        - Computes lexical diversity.
        - Counts characters, words, sentences, syllables, lines, and paragraphs.
        - Calculates various readability scores including Flesch Reading Ease, Flesch-Kincaid Grade Level, SMOG Index, Gunning Fog Index, Automated Readability Index, Dale-Chall Readability Score, Linsear Write Formula, and Coleman-Liau Index.
        - Estimates reading time.
        - Analyzes sentiment polarity and subjectivity using TextBlob.
        - Interprets readability scores and sentiment analysis results.
        - Populates the table with the calculated statistics and their interpretations.

        The table is updated with the following statistics:
        - Characters
        - Words
        - Unique words
        - Difficult Words
        - Syllables
        - Sentences
        - Lines
        - Paragraphs
        - Total tokens
        - Unique tokens
        - Lexical diversity
        - Sentiment Polarity
        - Sentiment Subjectivity
        - Flesch Reading Ease
        - Flesch-Kincaid Grade Level
        - Smog Index
        - Gunning Fog
        - Automated Readability Index
        - Dale-Chall Readability Score
        - Linsear Write Formula
        - Coleman-Liau Index
        - Estimated Reading Time (minutes)
        """
        text = self.text_edit_widget.toPlainText()
        
        tokens = word_tokenize(text)
        total_tokens = len(tokens)
        unique_tokens = len(set(tokens))
        lexical_diversity = unique_tokens / total_tokens if total_tokens > 0 else 0
        
        characters = len(text)
        words = textstat.lexicon_count(text)
        sentences = textstat.sentence_count(text)
        syllables = textstat.syllable_count(text)
        lines = text.count("\n") + 1 if text else 0
        flesch_reading_ease = textstat.flesch_reading_ease(text)
        reading_ease_interpretation = Interpretations.flesch_reading_ease_interpretation(
            flesch_reading_ease)
        flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
        flesch_kincaid_grade_interpretation = Interpretations.flesch_kincaid_grade_interpretation(
            flesch_kincaid_grade)
        smog_index = textstat.smog_index(text)
        gunning_fog = textstat.gunning_fog(text)
        gunning_fog_interpretation = Interpretations.gunning_fog_index_interpretation(gunning_fog)
        automated_readability_index = textstat.automated_readability_index(text)
        dale_chall_readability_score = textstat.dale_chall_readability_score(text)
        difficult_words = textstat.difficult_words(text)
        linsear_write_formula = textstat.linsear_write_formula(text)
        coleman_liau_index = textstat.coleman_liau_index(text)
        coleman_liau_index_interpretation = Interpretations.coleman_liau_index_interpretation(
            coleman_liau_index)
        reading_time = textstat.reading_time(text, ms_per_char=2)
        blob = TextBlob(text)
        sentiment_polarity = round(blob.sentiment.polarity, 2)
        sentiment_polarity_interpretation = Interpretations.sentiment_polartiy_interpretation(
            sentiment_polarity)
        sentiment_subjectivity = round(blob.sentiment.subjectivity, 2)
        sentiment_subjectivity_interpretation = Interpretations.sentiment_subjectivity_interpretation(
            sentiment_subjectivity)
        unique_words = len(set(word_tokenize(text)))
        number_of_paragraphs = text.count("\n\n")
        
        stats = [
            ("Characters", characters, ""),
            ("Words", words, ""),
            ("Unique words", unique_words, ""),
            ("Difficult Words", difficult_words, ""),
            ("Syllables", syllables, ""),
            ("Sentences", sentences, ""),
            ("Lines", lines, ""),
            ("Paragraphs", number_of_paragraphs, ""),
            ("Total tokens", total_tokens, ""),
            ("Unique tokens", unique_tokens, ""),
            ("Lexical diversity", lexical_diversity, ""),
            ("Sentiment Polarity", sentiment_polarity, sentiment_polarity_interpretation),
            ("Sentiment Subjectivity", sentiment_subjectivity,
             sentiment_subjectivity_interpretation),
            ("Flesch Reading Ease", flesch_reading_ease, reading_ease_interpretation),
            ("Flesch-Kincaid Grade Level", flesch_kincaid_grade,
             flesch_kincaid_grade_interpretation),
            ("Smog Index", smog_index, ""),
            ("Gunning Fog", gunning_fog, gunning_fog_interpretation),
            ("Automated Readability Index", automated_readability_index, ""),
            ("Dale-Chall Readability Score", dale_chall_readability_score, ""),
            ("Linsear Write Formula", linsear_write_formula, ""),
            ("Coleman-Liau Index", coleman_liau_index, coleman_liau_index_interpretation),
            ("Estimated Reading Time (minutes)", reading_time, ""),
        ]
        
        self.table.setRowCount(len(stats))
        for i, (stat_name, raw_value, interpretation) in enumerate(stats):
            self.table.setItem(i, 0, QTableWidgetItem(stat_name))
            self.table.setItem(i, 1, QTableWidgetItem(str(raw_value)))
            self.table.setItem(i, 2, QTableWidgetItem(interpretation))
        
        self.table.horizontalHeader().setSectionResizeMode(0,
                                                           QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1,
                                                           QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
