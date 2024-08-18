from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QPushButton, QLineEdit, QFrame, QComboBox, QRadioButton, QCheckBox, QButtonGroup, QScrollArea, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal
from .AddQuestionWindow import AddQuestionWindow
from .EditQuestionWindow import EditQuestionWindow
from backend.classes.QTI12Composer import QTI12Composer
import os, shutil, sys


class CreateTestWindow(QMainWindow):
    # Signal to emit the path of the created test
    emit_created = Signal(str)

    def __init__(self):
        super().__init__()

        self.index = 0  # Index for each question
        self.exam_data = {}  # Dictionary to store question data with an index for each question
        self.buttons = []  # List to store question button widgets

        # Supported question types and their corresponding render methods
        self.ITEM_TYPES = {
            'Multiple Choice': self.render_multiple_choice,
            'Multiple Correct': self.render_multiple_correct,
            'Multiple Correct Single Selection': self.render_multiple_correct,
            'True - False': self.render_true_false,
            'Essay Question': self.render_essay_question,
        }
        self.setup_ui()

    def setup_ui(self):
        """Sets up the main UI components of the CreateTestWindow."""
        self.setup_scroll_area()
        self.setup_main_widget()
        self.setup_header_layout()
        self.layout.addLayout(self.title_layout)
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.save_button)

    def setup_scroll_area(self):
        """Sets up the scroll area for displaying questions."""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)

        self.setWindowTitle("Create Test")
        self.setGeometry(300, 300, 700, 300)

    def setup_main_widget(self):
        """Initializes the main widget and layout."""
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

    def setup_header_layout(self):
        """Sets up the header layout with quiz title input and question type selection."""
        self.title_label = QLabel("Enter Quiz Title:")
        self.title_input = QLineEdit()

        self.add_question_button = QPushButton("Add Question")
        self.add_question_button.clicked.connect(self.add_question)

        self.question_type_dropdown = QComboBox()
        self.question_type_dropdown.addItems(list(self.ITEM_TYPES.keys()))

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_quiz)

        self.title_layout = QHBoxLayout()
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addWidget(self.title_input)
        self.title_layout.addWidget(self.question_type_dropdown)
        self.title_layout.addWidget(self.add_question_button)

    def add_question(self):
        """Opens a new window to add a question."""
        self.add_question_window = AddQuestionWindow(self.question_type_dropdown.currentText())
        self.add_question_window.data_saved.connect(self.retrieve_info)

    def render_question(self, question_data):
        """Renders the question title and question text."""
        title = QLabel(question_data['title'] + " - ID: "+ question_data['identifier'])
        question = QLabel(question_data['question'])

        # Make the title bold
        font = title.font()
        font.setBold(True)
        title.setFont(font)

        # Set fixed size for title and question
        title.setFixedHeight(20)
        question.setFixedHeight(20)

        self.scroll_layout.addWidget(title)
        self.scroll_layout.addWidget(question)

    def render_answers(self, question_data, button_type):
        """Renders the answer options for a question."""
        if button_type is QRadioButton:
            button_group = QButtonGroup(self.scroll_widget)
        for answer_key, answer_value in question_data['answers'].items():
            button = button_type(answer_value)
            button.setFixedHeight(20)    
            if question_data['solutions'][answer_key] == 'Correct':
                button.setChecked(True)
            button.setDisabled(True) # disable the selection
            self.scroll_layout.addWidget(button)
            if button_type is QRadioButton:
                button_group.addButton(button)

    def render_question_buttons(self, question_data):
        """Renders the edit and delete buttons for a question."""
        edit_button = QPushButton("Edit")
        edit_button.setIcon(QIcon(self.get_resource_path('frontend/assets/editing.png')))
        edit_button.setFixedSize(52, 24)
        edit_button.clicked.connect(lambda: self.open_edit_window(question_data))

        delete_button = QPushButton("Delete") 
        delete_button.setIcon(QIcon(self.get_resource_path('frontend/assets/delete.png')))
        delete_button.setFixedSize(60, 24)
        delete_button.clicked.connect(lambda: self.remove_question(question_data))
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch(1)

        # Wrap button_layout in a QWidget to set a fixed size
        button_layout_widget = QWidget()
        button_layout_widget.setLayout(button_layout)
        button_layout_widget.setFixedHeight(35)

        self.buttons.append(button_layout_widget)
        self.scroll_layout.addWidget(button_layout_widget)

        # Create a horizontal line separator and add it to the scroll_layout
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.scroll_layout.addWidget(separator)
    
    # Render methods for each question type
    def render_multiple_choice(self, question_data):
        self.render_question(question_data)
        self.render_answers(question_data, QCheckBox)
        self.render_question_buttons(question_data)

    def render_multiple_correct(self, question_data):
        self.render_question(question_data)
        self.render_answers(question_data, QCheckBox)
        self.render_question_buttons(question_data)

    def render_true_false(self, question_data):
        self.render_question(question_data)
        self.render_answers(question_data, QRadioButton)
        self.render_question_buttons(question_data)

    def render_essay_question(self, question_data):
        self.render_question(question_data)
        self.render_question_buttons(question_data)

    def retrieve_info(self):
        """Retrieves question info from the add question window and renders it."""
        info = self.add_question_window.get_info()

        # Add the question to the exam_data dict
        self.exam_data[self.index] = info
        self.index += 1

        question_data = self.exam_data[self.index - 1]
        render_method = self.ITEM_TYPES.get(question_data['title'])
        if render_method:
            render_method(question_data)

    def open_edit_window(self, question_data):
        """Opens a window to edit a question."""
        self.edit_window = EditQuestionWindow(question_data, self)
        self.edit_window.show()
        
    def remove_question(self, question_data):
        """Removes a question from the exam data."""
        # find the question with the unique identifier and remove it
        for key, value in list(self.exam_data.items()):  # Use list to create a copy of items for iteration
            if 'identifier' in value and value['identifier'] == question_data['identifier']:
                # print("found unique identifier")
                del self.exam_data[key]  # Remove the entry from the dictionary
                break  # Exit the loop as we found the item
        self.refresh_view()

    def refresh_view(self, is_edit=False):
        """Refreshes the view to reflect any changes in the question list."""
        if not is_edit:
            # Remove the buttons
            for button_widget in self.buttons:
                button_widget.setParent(None)
            self.buttons.clear()

        # Clear the scroll_layout
        for i in reversed(range(self.scroll_layout.count())): 
            layout_item = self.scroll_layout.itemAt(i)
            widget = layout_item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                # Handle the removal of layouts if any
                layout = layout_item.layout()
                if layout is not None:
                    self.remove_layout(layout)
    
        # Re-render all the questions
        for question_data in self.exam_data.values():
            render_method = self.ITEM_TYPES.get(question_data['title'])
            if render_method:
                render_method(question_data)
        
    def update_exam_data(self, new_data):
        """Updates the exam data with new data for a question."""
        for key, value in self.exam_data.items():
            if value['identifier'] == new_data['identifier']:
                self.exam_data[key] = new_data
                break
        self.refresh_view(True)

    def save_quiz(self):
        """Saves the quiz data to a file."""
        if self.title_input.text().strip():
            if self.exam_data:
                if QMessageBox.question(self, "Save Exam", "Are you done creating the exam? Do you want to save it?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    self.exam_data['assessment title'] = self.title_input.text()
                    data = self.exam_data

                    # file_path of the empty QTI file  
                    path = self.get_resource_path('backend/data/SAKAI_QTI_Blank.xml')
                    composer = QTI12Composer(path)
                    generated_file_path = composer.generate_exam(data)

                    uploads_folder = self.get_resource_path('uploads')
                    destination_path = os.path.join(uploads_folder, os.path.basename(generated_file_path))

                    shutil.copy(generated_file_path, destination_path)

                    # shorten the path for the user to only the filename
                    destination_path = os.path.basename(destination_path)

                    self.emit_created.emit(destination_path)

                    # close the window
                    self.close()
            else:
                QMessageBox.warning(self, "Input Required", "You need to add at least one question to the test.")
        else:
            QMessageBox.warning(self, "Input Required", "The assessment title needs to be filled.")

    def get_resource_path(self, relative_path):
        """Get the absolute path to a resource, works for dev and for PyInstaller."""
        try:
            base_path = sys._MEIPASS  # PyInstaller creates a temp folder and stores the path in _MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")  # In development mode, base path is the current directory

        return os.path.join(base_path, relative_path)