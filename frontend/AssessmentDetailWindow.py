from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QScrollArea, QLabel, QRadioButton, QCheckBox, QFrame, QButtonGroup, QPushButton, QLineEdit, QHBoxLayout, QMessageBox
from PySide6.QtGui import QIcon, QFontMetrics
from PySide6.QtCore import Qt
import os
from backend.classes.QTI12Parser import QTI12Parser
from frontend.EditQuestionWindow import EditQuestionWindow

class AssessmentDetailWindow (QMainWindow):
    def __init__(self, file_name):
        super().__init__()
        # Set window title to the file name
        self.setWindowTitle(file_name)

        # Compute file path relative to the script location
        script_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(script_dir)
        self.file_path = os.path.join(parent_dir, 'uploads', file_name)
        
        # Parse the exam file to get its structure
        self.parser = QTI12Parser(self.file_path)
        self.exam_data = self.parser.get_structure()
        
        # Setup the scroll area for displaying questions
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)

        # Create a new layout for the main window
        self.main_layout = QVBoxLayout()
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)

        # Add the scroll area and the save button to the main layout
        self.main_layout.addWidget(self.scroll_area)

        # Add a save button
        self.save_button = QPushButton('Save')
        self.main_layout.addWidget(self.save_button)

        # Connect the button's clicked signal to the save_and_close method
        self.save_button.clicked.connect(self.save_and_close)

        # Set the main widget as the central widget
        self.setCentralWidget(self.main_widget)
        
        # Render the questions and add an end-of-test label
        self.render_questions(self.exam_data)
        self.layout.addWidget(QLabel("End of Test - EOF"))

        # Set the width of the window
        self.resize(650, self.height()) 

    def save_and_close(self):
        # Create a message box that asks if the user wants to save
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setText("Do you want to save?")
        msg_box.setWindowTitle("Save")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Show the message box and get the user's response
        response = msg_box.exec_()

        # If the user clicked "Yes", save the data and close the window
        if response == QMessageBox.Yes:
            self.close()

    def render_question(self, question_data, current_question_number, total_questions):
        # Prepend "Question X of Y: " to the question title and use HTML for styling
        title_text = f"<b>Question {current_question_number} of {total_questions}:</b> {question_data['title']} - ID: {question_data['identifier']}"
        title = QLabel(title_text)
        title.setTextFormat(Qt.RichText)  # Ensure QLabel interprets the text as rich text
        question = QLabel(question_data['question'])
        
        self.layout.addWidget(title)
        self.layout.addWidget(question)

    def render_answers(self, question_data, button_type):
        # Display answers using the specified button type (Radio or Checkbox)
        if button_type is QRadioButton:
            button_group = QButtonGroup(self.scroll_widget)
        for answer_key, answer_value in question_data['answers'].items():
            button = button_type(answer_value)
            if question_data['solutions'][answer_key] == 'Correct':
                button.setChecked(True)
            button.setDisabled(True)  # Disable selection
            self.layout.addWidget(button)
            if button_type is QRadioButton:
                button_group.addButton(button)

    def render_edit_question(self, question_data):
        # Display an edit button for each question
        edit_button = QPushButton("Edit")
        edit_button.setIcon(QIcon('frontend/assets/editing.png'))
        edit_button.setFixedSize(52, 24)
        edit_button.clicked.connect(lambda: self.open_edit_window(question_data))
        self.layout.addWidget(edit_button)

    def open_edit_window(self, question_data):
        # Open a new window for editing the selected question
        self.edit_window = EditQuestionWindow(question_data, self, self.file_path)
        self.edit_window.show()

    def render_multiple_choice(self, question_data, current_question_number, total_questions):
        # Render a multiple-choice question
        self.render_question(question_data, current_question_number, total_questions)
        self.render_answers(question_data, QCheckBox)
        self.render_edit_question(question_data)

    def render_multiple_correct(self, question_data, current_question_number, total_questions):
        # Render a question with multiple correct answers
        self.render_question(question_data, current_question_number, total_questions)
        self.render_answers(question_data, QCheckBox)
        self.render_edit_question(question_data)

    def render_true_false(self, question_data, current_question_number, total_questions):
        # Render a true/false question
        self.render_question(question_data, current_question_number, total_questions)
        self.render_answers(question_data, QRadioButton)
        self.render_edit_question(question_data)

    def render_essay_question(self, question_data, current_question_number, total_questions):
        # Render an essay question
        self.render_question(question_data, current_question_number, total_questions)
        self.render_edit_question(question_data)

    def render_questions(self, exam_data):
        # Render questions based on their type
        ITEM_TYPES = {
            'Multiple Choice': self.render_multiple_choice,
            'Multiple Correct': self.render_multiple_correct,
            'Multiple Correct Single Selection': self.render_multiple_correct,
            'True - False': self.render_true_false,
            'Essay Question': self.render_essay_question,
        }

        total_questions = len(exam_data)
        current_question_number = 0
        
        for question_data in exam_data.values():
            current_question_number += 1
            render_method = ITEM_TYPES.get(question_data['title'])
            if render_method:
                render_method(question_data, current_question_number, total_questions)
                # Add a horizontal line after each question
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                self.layout.addWidget(line)

    def refresh_view(self):
        # Clear the current layout and re-render the questions
        for i in reversed(range(self.layout.count())): 
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Re-parse the file and update the exam data
        self.parser = QTI12Parser(self.file_path)
        self.exam_data = self.parser.get_structure()

        # Re-render the questions and add the end-of-test label
        self.render_questions(self.exam_data)
        self.layout.addWidget(QLabel("End of Test - EOF"))