from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from PySide6.QtCore import Signal
from lxml import etree as ET
from lxml.etree import XMLSyntaxError
import os, shutil, sys

class UploadWidget(QWidget):
    file_uploaded = Signal(str)

    def __init__(self):
        super().__init__()

        # Create a vertical layout
        self.layout = QVBoxLayout(self)

        # Create an upload button, connect its clicked signal to the upload_file method, and add it to the layout
        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_button)

    def upload_file(self):
        # Open a file dialog and get the selected file path
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open file', '.')
        if file_path:
            # Validate and process the file
            if not self.validate_and_process_file(file_path):
                return

            # Copy the file to the uploads folder
            project_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            uploads_folder = os.path.join(project_folder, 'uploads')
            os.makedirs(uploads_folder, exist_ok=True)
            file_name = os.path.basename(file_path)
            shutil.copy(file_path, os.path.join(uploads_folder, file_name))

            # Emit the file_uploaded signal with the file name
            self.file_uploaded.emit(file_name)

    def validate_and_process_file(self, file_path):
        # Check if the file is an XML file
        _, ext = os.path.splitext(file_path)
        if ext.lower() != '.xml':
            self.show_message("Invalid file selected", "Please select an XML file.")
            return False

        # Validate XML file to xsd schema
        try:
            schema_path = self.get_resource_path('backend/data/QTI 1_2 xsd schemas/imscp_v1p1.xsd')
            xmlschema_doc = ET.parse(schema_path)
            xmlschema = ET.XMLSchema(xmlschema_doc)
            xml_doc = ET.parse(file_path)
            xmlschema.validate(xml_doc)
        except XMLSyntaxError as e:
            self.show_message("XML Error", str(e))
            return False
        except Exception as e:
            self.show_message("Unexpected Error", str(e))
            return False

        # Check if the file contains items (questions)
        try:
            item_count = self.check_xml(file_path)
            self.show_message("XML Tag Count", f"Successfully found:\n\n{item_count} items in the XML file.")
        except Exception as e:
            self.show_message("XML Error", str(e))
            return False

        return True

    def check_xml(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        item_count = len(root.findall(".//item"))
        if item_count == 0:
            raise Exception("No 'item' tags found in the XML file.")
        return item_count

    def show_message(self, title, text):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec()

    def get_resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)