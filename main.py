from PySide6.QtWidgets import QApplication
from frontend.main_view import MainWindow

import sys


# Create an instance of QApplication
app = QApplication([])

# Create an instance of MainWindow
window = MainWindow()
# Display the main window
window.show()

# Start the application's event loop and exit the script with the status code returned by the event loop
sys.exit(app.exec())