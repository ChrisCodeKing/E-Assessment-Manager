from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox
from PySide6.QtCore import Signal
from backend.classes.JobsModel import JobsModel
from .AssessmentDetailWindow import AssessmentDetailWindow 
from .ExportWindow import ExportWindow
import os

class AssessmentOverviewWidget(QWidget):
    # Signal to notify when a file is uploaded
    file_uploaded = Signal(str)

    def __init__(self, upload_widget, parent=None):
        super().__init__(parent)
        self.model = JobsModel()  # Model to manage job data

        # Layout setup
        self.layout = QVBoxLayout(self)
        self.title = QLabel("Assessment Overview")  # Title label
        self.layout.addWidget(self.title)

        # Table setup
        self.table = QTableWidget(0, 4)  # Initialize table with 0 rows and 5 columns
        self.table.setHorizontalHeaderLabels(["File Name", "View/Edit", "Remove", "Export"])
        self.layout.addWidget(self.table)

        # Adjust column resizing    
        self.adjust_column_resizing()

        self.populate_table()  # Populate table with jobs

        # Connect the file_uploaded signal from the upload widget to the add_job method
        upload_widget.file_uploaded.connect(self.add_job)

        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)

    def adjust_column_resizing(self):
        # Set the "File Name" column to stretch
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Set the button columns to resize to their contents or a fixed size
        for column in range(1, 4):  # Assuming columns 1, 2, and 3 are for buttons
            self.table.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeToContents)

    def populate_table(self):
        # Load jobs from the uploads folder and populate the table
        project_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        uploads_folder = os.path.join(project_folder, 'uploads')
        self.model.load_jobs(uploads_folder)
        for i, file_name in enumerate(self.model.jobs, start=1):
            self.add_job(file_name)

    def add_job(self, file_name):
        # Add a job to the table
        row = self.table.rowCount()
        self.table.insertRow(row)
        # self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.table.setItem(row, 0, QTableWidgetItem(file_name))

        # Define button size
        button_width = 100

        # Add View/Edit button
        view_button = QPushButton("View/Edit")
        view_button.setFixedWidth(button_width)
        view_button.clicked.connect(lambda: self.view_job(row + 1, file_name))
        self.table.setCellWidget(row, 1, view_button)

        # Add Remove button
        remove_button = QPushButton("Remove")
        remove_button.setFixedWidth(button_width)
        remove_button.clicked.connect(lambda: self.remove_job(row, file_name))
        self.table.setCellWidget(row, 2, remove_button)

        # Add Export button
        export_button = QPushButton("Export")
        export_button.setFixedWidth(button_width)
        export_button.clicked.connect(lambda: self.export_job(row + 1, file_name))
        self.table.setCellWidget(row, 3, export_button)

    def view_job(self, test_number, file_name):
        # Open the job view window
        self.job_view_window = AssessmentDetailWindow (file_name)
        self.job_view_window.show()

    def remove_job(self, row, file_name):
        # Remove a job from the table and delete the file
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'uploads', file_name)

        msg_box = QMessageBox()
        msg_box.setText("Are you sure you want to delete this file?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        result = msg_box.exec()
        
        if result == QMessageBox.Yes and os.path.exists(file_path):
            try:
                os.remove(file_path)
                QMessageBox.information(self, "Success", "File deleted successfully")
                self.table.removeRow(row)
                # refresh the table

                    
            except FileNotFoundError:
                QMessageBox.critical(self, "Error", "The file does not exist.")
            except PermissionError:
                QMessageBox.critical(self, "Error", "You do not have permission to delete this file.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            

    def export_job(self, test_number, file_name):
        # Placeholder for job export functionality
        print(f"Exporting job {test_number} with file '{file_name}'")
        self.export_window = ExportWindow(file_name)
        self.export_window.show()

    def on_cell_double_clicked(self, row, column):
        # Check if the double-clicked column is the "File Name" column
        if column == 0:
            # Retrieve the filename from the cell
            file_name = self.table.item(row, 0).text()
            # Call the view_job method to open the file
            self.view_job(row + 1, file_name)