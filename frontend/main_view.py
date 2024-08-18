from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QWidget, QPushButton, QHBoxLayout, QSizePolicy
from frontend.UploadWidget import UploadWidget
from frontend.AssessmentOverviewWidget import AssessmentOverviewWidget
from frontend.CreateTestWindow import CreateTestWindow
from frontend.HelpWindow import HelpWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set the window title
        self.setWindowTitle("QTI Test Manager")
        # Central widget setup
        self.central_widget = QWidget()  # Create a QWidget to set as the central widget
        self.setCentralWidget(self.central_widget)  # Set the created widget as the central widget
        
        # Main layout setup
        self.layout = QVBoxLayout(self.central_widget)  # Create a QVBoxLayout for the central widget
        self.layout.setSpacing(10)  # Set the spacing between the widgets in the layout
        # Title label setup
        self.title = QLabel("Import Quiz or Create Quiz from Scratch")  # Create a title label
        self.layout.addWidget(self.title)  # Add the title label to the layout
        # Top bar layout setup
        self.top_bar_layout = QHBoxLayout()  # Create a QHBoxLayout for the top bar
        button_size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Define a common size policy for all buttons
        
        # Upload widget setup
        self.upload_widget = UploadWidget()  # Create the UploadWidget
        self.upload_widget.setSizePolicy(button_size_policy)  # Set size policy for the UploadWidget
        self.top_bar_layout.addWidget(self.upload_widget)  # Add the UploadWidget to the horizontal layout
        
        # Create test button setup
        self.create_test_button = QPushButton("Create Test")  # Create a button for creating a new test
        self.create_test_button.setSizePolicy(button_size_policy)  # Set size policy for the button
        self.create_test_button.clicked.connect(self.create_test)  # Connect button click to create_test method
        self.top_bar_layout.addWidget(self.create_test_button)  # Add the button to the horizontal layout
        
        # Help button setup
        self.help_button = QPushButton("Help")  # Create a button for help
        self.help_button.setSizePolicy(button_size_policy)  # Set size policy for the button
        self.help_button.clicked.connect(self.show_help)  # Connect button click to show_help method
        self.top_bar_layout.addWidget(self.help_button)  # Add the button to the horizontal layout
        
        self.top_bar_layout.addStretch(1)  # Add a stretchable space to the horizontal layout to push everything to the left
        
        # Add the top bar layout to the main layout
        self.layout.addLayout(self.top_bar_layout)
        # Jobs widget setup
        self.jobs_widget = AssessmentOverviewWidget(self.upload_widget)  # Create the JobsWidget
        self.layout.addWidget(self.jobs_widget)  # Add the JobsWidget to the layout
        # Window geometry setup
        self.setGeometry(100, 100, 800, 600)  # Set window size

    def create_test(self):
        # Method to handle creation of a new test
        self.create_test_window = CreateTestWindow()  # Create an instance of CreateTestWindow
        self.create_test_window.emit_created.connect(self.jobs_widget.add_job)  # Connect signal to add_job method of jobs_widget
        self.create_test_window.show()  # Show the create test window

    def show_help(self):
        if not hasattr(self, 'help_window') or not self.help_window.isVisible():
            self.help_window = HelpWindow('backend/data/help_content.md')
        self.help_window.show()