from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QRadioButton, QPushButton, QFileDialog, QMessageBox
import shutil, zipfile, os, sys

# TODO close window after export
class ExportWindow(QWidget):
    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Export Job')
        self.setGeometry(300, 300, 400, 200)  # Adjusted window size
        self.setFixedSize(400, 200)  # Fix window size

        layout = QVBoxLayout()

        self.label = QLabel('Choose export format:')
        layout.addWidget(self.label)

        self.radio_content_packaging = QRadioButton("IMS Content Packaging")
        self.radio_qti = QRadioButton("QTI Version 1.2 for SAKAI")
        layout.addWidget(self.radio_content_packaging)
        layout.addWidget(self.radio_qti)

        self.export_button = QPushButton('Export')
        self.export_button.clicked.connect(self.export)
        layout.addWidget(self.export_button)

        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.close)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def export(self):
        if self.radio_qti.isChecked():
            self.export_qti()
        elif self.radio_content_packaging.isChecked():
            self.export_content_packaging()

    def export_content_packaging(self):
        # take the file, copy it and rename it to exportAssessment.xml
        assessment_file_path = self.get_resource_path(f"uploads/{self.file_name}")
        destination_file_path = self.get_resource_path("backend/data/Content Packaging/exportAssessment.xml")
        shutil.copy(assessment_file_path, destination_file_path)

        # then take the imsmanifest.xml file and zip it with the exportAssessment.xml file
        imsmanifest_file_path = self.get_resource_path("backend/data/Content Packaging/imsmanifest.xml")
        with zipfile.ZipFile('export.zip', 'w') as z:
            z.write(destination_file_path, arcname='exportAssessment.xml')
            z.write(imsmanifest_file_path, arcname='imsmanifest.xml')

        # then ask where to save the zip file
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Zip Files (*.zip)")

        # Ensure the file name ends with .zip
        if save_path and not save_path.endswith('.zip'):
            save_path += '.zip'

        if save_path:
            shutil.move('export.zip', save_path)
            self.close()  # Close the window after export

    def export_qti(self):
        options = QFileDialog.Options()
        # Assuming self.file_name contains the desired predefined filename
        predefined_filename = self.file_name if self.file_name else "export.qti"
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", predefined_filename, "All Files (*);;Text Files (*.txt)", options=options)
        
        if file_name:
            source_file_path = self.get_resource_path(f"uploads/{self.file_name}")
            try:
                shutil.copy(source_file_path, file_name)
                QMessageBox.information(self, "Export Successful", f"File has been successfully exported to: {file_name}")
                self.close()  # Close the window after export
            except Exception as e:
                print(f"Error copying file: {e}")

    def get_resource_path(self, relative_path):
        """Get the absolute path to a resource, works for dev and for PyInstaller."""
        try:
            base_path = sys._MEIPASS  # PyInstaller creates a temp folder and stores the path in _MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")  # In development mode, base path is the current directory

        return os.path.join(base_path, relative_path)