from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea
import markdown, os, sys

class HelpWindow(QDialog):
    def __init__(self, markdown_file_path):
        super().__init__()
        self.setWindowTitle("Help")
        self.setGeometry(300, 300, 600, 600)

        # Read Markdown content from file
        with open(self.get_resource_path(markdown_file_path), 'r') as md_file:
            markdown_content = md_file.read()

        # Convert Markdown to HTML
        html_content = markdown.markdown(markdown_content)

        layout = QVBoxLayout()

        # Create QLabel for HTML content
        self.help_text = QLabel()
        self.help_text.setText(html_content)
        self.help_text.setWordWrap(True)

        # Create a QScrollArea and set its widget to be the QLabel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # Make the scroll area resizable
        scroll_area.setWidget(self.help_text)  # Set the QLabel as the scroll area's widget

        layout.addWidget(scroll_area)  # Add the scroll area to the layout

        self.setLayout(layout)

    def get_resource_path(self, relative_path):
        """ Get the absolute path to a resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores the path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
