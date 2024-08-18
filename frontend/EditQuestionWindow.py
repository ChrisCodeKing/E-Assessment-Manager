from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QTextEdit, QApplication, QMessageBox, QCheckBox, QLineEdit, QHBoxLayout, QRadioButton
from PySide6.QtGui import QIcon
from backend.classes.QTI12Composer import QTI12Composer
import sys, os

class EditQuestionWindow(QMainWindow):
    def __init__(self, question_data, parent_window, file_path=None):
        super().__init__()
        self.question_data = question_data  # Data of the question being edited
        self.parent_window = parent_window  # Reference to the parent window
        self.file_path = file_path  # Path to the file where the question is stored
        self.initUI()  # Initialize the UI components

    def initUI(self):
        # Set window title and geometry
        self.setWindowTitle("Edit Question")
        self.setGeometry(300, 300, 400, 300)

        # Layout setup
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Displaying the question being edited
        self.question_label = QLabel("User is editing " + "<b>" + self.question_data["title"] + " - ID: " + self.question_data["identifier"] + "</b>")
        self.question_label.setWordWrap(True)
        self.layout.addWidget(self.question_label)

        # Setup for editing the question text
        self.question_title = QLabel("Question:")
        self.layout.addWidget(self.question_title)
        self.question_text_editor = QTextEdit()
        self.question_text_editor.setPlainText(str(self.question_data["question"]))
        self.layout.addWidget(self.question_text_editor)

        self.answer_widgets = {}

        # need to differentiate between question types 
        if self.question_data["title"] == 'Multiple Choice' or self.question_data["title"] == 'Multiple Correct' or self.question_data["title"] == 'Multiple Correct Single Selection':
            # Title and Text editor for answers
            self.answer_title = QLabel("Answers:")
            self.layout.addWidget(self.answer_title)
            for option in ['A', 'B', 'C', 'D']:
                # Create a new horizontal layout for each answer option
                answer_layout = QHBoxLayout()

                # Create the checkbox and line edit for this answer option
                checkbox = QCheckBox(option)
                line_edit = QLineEdit(self.question_data["answers"][option])

                # Check the checkbox if the option is correct
                if self.question_data["solutions"][option] == 'Correct':
                    checkbox.setChecked(True)

                # Add the checkbox and line edit to the horizontal layout
                answer_layout.addWidget(checkbox)
                answer_layout.addWidget(line_edit)

                # Add the horizontal layout to the main layout
                self.layout.addLayout(answer_layout)

                # Store the checkbox and line edit in a dictionary for later use
                self.answer_widgets[option] = (checkbox, line_edit)
        elif self.question_data["title"] == 'True - False':
            # Title and Text editor for answers
            self.answer_title = QLabel("Answers:")
            self.layout.addWidget(self.answer_title)
            for option in ['A', 'B']:
                # Create a new horizontal layout for each answer option
                answer_layout = QHBoxLayout()

                # Create the checkbox and line edit for this answer option
                checkbox = QRadioButton(option)
                line_edit = QLineEdit(self.question_data["answers"][option])

                # Check the radio button if the option is correct
                if self.question_data["solutions"][option] == 'Correct':
                    checkbox.setChecked(True)

                # Add the checkbox and line edit to the horizontal layout
                answer_layout.addWidget(checkbox)
                answer_layout.addWidget(line_edit)

                # Add the horizontal layout to the main layout
                self.layout.addLayout(answer_layout)

                # Store the checkbox and line edit in a dictionary for later use
                self.answer_widgets[option] = (checkbox, line_edit)
        elif self.question_data["title"] == 'Essay Question':
            # Create and fill in the answer and solution text editors with predefined text
            self.answer_text_editor = QTextEdit()

        # Save button setup
        self.save_button = QPushButton("Save")
        self.save_button.setIcon(QIcon(self.get_resource_path('frontend/assets/save.png')))
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(self.save_button)

        # Set central widget
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.centerWindow()  # Center the window on the screen

    def centerWindow(self):
        # Center the window on the screen
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().geometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def save_changes(self):
        try:
            # Confirmation dialog
            reply = QMessageBox.question(self, 'Save Changes', 'Do you want to save changes and close?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Collect the edited data from the UI
                new_question = self.question_text_editor.toPlainText()

                # Check if any field is empty and display a dialog if so
                missing_fields = []
                if not new_question.strip():
                    missing_fields.append("Question")

                if missing_fields:
                    missing_fields_str = ", ".join(missing_fields)
                    QMessageBox.warning(self, "Missing Information", f"Please fill in the following fields before saving: {missing_fields_str}")
                    return

                 # Proceed with saving if all fields are filled
                if self.question_data["title"] == 'Essay Question':
                    new_answers = {'A': ''}
                    new_solutions = {}
                else:
                    new_answers = {}
                    new_solutions = {}
                    for option, widgets in self.answer_widgets.items():
                        checkbox, line_edit = widgets
                        new_answers[option] = line_edit.text()
                        new_solutions[option] = 'Correct' if checkbox.isChecked() else 'InCorrect'
                
                new_data = {
                    'identifier': self.question_data["identifier"],
                    'title': self.question_data["title"],
                    'question': new_question,
                    'answers': new_answers,
                    'solutions': new_solutions
                }

                if self.file_path is not None:
                    self.composer = QTI12Composer(self.file_path)
                    self.composer.compose_question(new_data)
                    self.parent_window.refresh_view()
                else:
                    self.parent_window.update_exam_data(new_data)
                
                self.close()
        except Exception as e:
            # General error handling
            error_dialog = QMessageBox()
            error_dialog.setWindowTitle("Error")
            error_dialog.setText(f"An unexpected error occurred: {str(e)}")
            error_dialog.setIcon(QMessageBox.Warning)
            error_dialog.exec_()

    def edit_answer(self):
        # Replace the question label with the answer editor in the layout
        self.layout.replaceWidget(self.question_label, self.answer_edit)
        self.layout.update()

        # Update the save button's click event to save the answer
        self.save_button.clicked.disconnect()
        self.save_button.clicked.connect(self.save_answer)

    def get_resource_path(self, relative_path):
        """Get the absolute path to a resource, works for dev and for PyInstaller."""
        try:
            base_path = sys._MEIPASS  # PyInstaller creates a temp folder and stores the path in _MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")  # In development mode, base path is the current directory

        return os.path.join(base_path, relative_path)