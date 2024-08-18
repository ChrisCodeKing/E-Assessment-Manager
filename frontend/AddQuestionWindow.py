from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QTextEdit, QWidget, QPushButton, QApplication, QMessageBox, QCheckBox, QLineEdit, QHBoxLayout, QRadioButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal

import json, sys, os 

class AddQuestionWindow(QMainWindow):
    id_counter = 0
    data_saved = Signal(dict)

    def __init__(self, question_type):
        super().__init__()
        self.question_type = question_type
        self.data = {}
        self.initUI()
        self.show()
        
    def initUI(self):
        self.setWindowTitle("Add Question")
        self.setGeometry(300, 300, 400, 300)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.question_label = QLabel("User is adding a new question of type: " + "<b>" + self.question_type + "</b>")
        self.question_label.setWordWrap(True)
        self.layout.addWidget(self.question_label)

        # Title and Text editor for question
        self.question_title = QLabel("Question:")
        self.layout.addWidget(self.question_title)
        self.question_text_editor = QTextEdit()
        self.layout.addWidget(self.question_text_editor)

        self.answer_widgets = {}

        # need to differentiate between question types 
        if self.question_type == 'Multiple Choice' or self.question_type == 'Multiple Correct' or self.question_type == 'Multiple Correct Single Selection':
            # Title and Text editor for answers
            self.answer_title = QLabel("Answers:")
            self.layout.addWidget(self.answer_title)
            for option in ['A', 'B', 'C', 'D']:
                # Create a new horizontal layout for each answer option
                answer_layout = QHBoxLayout()

                # Create the checkbox and line edit for this answer option
                checkbox = QCheckBox(option)
                line_edit = QLineEdit('Answer here')

                # Add the checkbox and line edit to the horizontal layout
                answer_layout.addWidget(checkbox)
                answer_layout.addWidget(line_edit)

                # Add the horizontal layout to the main layout
                self.layout.addLayout(answer_layout)

                # Store the checkbox and line edit in a dictionary for later use
                self.answer_widgets[option] = (checkbox, line_edit)
        elif self.question_type == 'True - False':
            # Title and Text editor for answers
            self.answer_title = QLabel("Answers:")
            self.layout.addWidget(self.answer_title)
            for option in ['A', 'B']:
                # Create a new horizontal layout for each answer option
                answer_layout = QHBoxLayout()

                # Create the checkbox and line edit for this answer option
                checkbox = QRadioButton(option)
                line_edit = QLineEdit("True" if option == 'A' else "False")

                # Add the checkbox and line edit to the horizontal layout
                answer_layout.addWidget(checkbox)
                answer_layout.addWidget(line_edit)

                # Add the horizontal layout to the main layout
                self.layout.addLayout(answer_layout)

                # Store the checkbox and line edit in a dictionary for later use
                self.answer_widgets[option] = (checkbox, line_edit)
        elif self.question_type == 'Essay Question':
            # Create and fill in the answer and solution text editors with predefined text
            self.answer_text_editor = QTextEdit(self.get_predefined_text('answer'))
            self.solution_text_editor = QTextEdit(self.get_predefined_text('solution'))

        # Create a central widget, set the layout to this widget, and set this widget as the central widget of the QMainWindow
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

        self.save_button = QPushButton("Save")
        self.save_button.setIcon(QIcon(self.get_resource_path('frontend/assets/save.png')))
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(self.save_button)


        # print(f"Question type: {self.question_type}")
        self.centerWindow()

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().geometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def save_changes(self):
        try:
             # Confirmation dialog
            reply = QMessageBox.question(self, 'Save Changes', 'Do you want to save changes?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                question = self.question_text_editor.toPlainText()
                answers = {}
                solutions = {}
                for option, (checkbox, line_edit) in self.answer_widgets.items():
                    answers[option] = line_edit.text()
                    solutions[option] = "Correct" if checkbox.isChecked() else "InCorrect"

                answer_json = json.dumps(answers)
                solution_json = json.dumps(solutions)
                if self.question_type == 'Essay Question':
                    answer_json = self.answer_text_editor.toPlainText()
                    solution_json = self.solution_text_editor.toPlainText()


                # Check if any field is empty and display a dialog if so
                missing_fields = []
                if not question.strip():
                    missing_fields.append("Question")
                if not answer_json.strip():
                    missing_fields.append("Answers")
                if not solution_json.strip():
                    missing_fields.append("Solutions")

                if missing_fields:
                    missing_fields_str = ", ".join(missing_fields)
                    QMessageBox.warning(self, "Missing Information", f"Please fill in the following fields before saving: {missing_fields_str}")
                    return

                # Proceed with saving if all fields are filled
                answers = json.loads(answer_json.replace("'", '"'))
                solutions = json.loads(solution_json.replace("'", '"'))

                self.data = {
                    'identifier': self.generate_ID(),
                    'title': self.question_type,
                    'question': question,
                    'answers': answers,
                    'solutions': solutions
                }
                # Optionally, close the window after saving
                self.data_saved.emit(self.data)
                self.close()
        except json.JSONDecodeError as e:
            error_dialog = QMessageBox()
            error_dialog.setWindowTitle("JSON Format Error")
            detailed_error_msg = f"Error parsing JSON: {e.msg}. Please ensure your data is in the correct format.\n\n"
            detailed_error_msg += "Example format for answers:\n"
            detailed_error_msg += '{"A": "Answer here", "B": "Answer here", "C": "Answer here", "D": "Answer here"}\n\n'
            detailed_error_msg += "Example format for solutions:\n"
            detailed_error_msg += '{"A": "Correct", "B": "Incorrect", "C": "Incorrect", "D": "Incorrect"}\n\n'
            detailed_error_msg += f"Error at line {e.lineno}, column {e.colno}. Please review your input."
            error_dialog.setText(detailed_error_msg)
            error_dialog.setIcon(QMessageBox.Warning)
            error_dialog.exec_()
        except Exception as e:
            # General error handling
            error_dialog = QMessageBox()
            error_dialog.setWindowTitle("Error")
            error_dialog.setText(f"An unexpected error occurred: {str(e)}")
            error_dialog.setIcon(QMessageBox.Warning)
            error_dialog.exec_()

    def generate_ID(self):
        AddQuestionWindow.id_counter += 1
        return str(AddQuestionWindow.id_counter)
    
    def get_info(self):
        return self.data

    def get_predefined_text(self, text_type):
        predefined_texts = {
            'Multiple Choice' :{
                'answer' : '{ "A": "Answer here", "B": "Answer here", "C": "Answer here", "D": "Answer here" }',
                'solution' : '{ "A": "InCorrect", "B": "InCorrect", "C": "InCorrect", "D": "InCorrect" }'
            },
            'Multiple Correct' :{
                'answer' : '{ "A": "Answer here", "B": "Answer here", "C": "Answer here", "D": "Answer here" }',
                'solution' : '{ "A": "InCorrect", "B": "InCorrect", "C": "InCorrect", "D": "InCorrect" }'
            },
            'Multiple Correct Single Selection' : {
                'answer' : '{ "A": "Answer here", "B": "Answer here", "C": "Answer here", "D": "Answer here" }',
                'solution' : '{ "A": "InCorrect", "B": "InCorrect", "C": "InCorrect", "D": "InCorrect" }'
            },
            'True - False' : {
                'answer' : '{ "A": "True", "B": "False" }',
                'solution' : '{ "A": "Correct", "B": "InCorrect" }'
            },
            'Essay Question' : {
                'answer' : '{ "A": ""}',
                'solution' : '{ "A": ""}'
            }
        }

        return predefined_texts.get(self.question_type, {}).get(text_type, 'Default predefined text')
    
    def get_resource_path(self, relative_path):
        """Get the absolute path to a resource, works for dev and for PyInstaller."""
        try:
            base_path = sys._MEIPASS  # PyInstaller creates a temp folder and stores the path in _MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")  # In development mode, base path is the current directory

        return os.path.join(base_path, relative_path)