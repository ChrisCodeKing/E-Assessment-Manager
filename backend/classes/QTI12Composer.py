from xml.etree import ElementTree as ET
import shutil, os, sys


class QTI12Composer:
    id_counter = 0

    def __init__(self, file_path, item=None):
        """Initialize the composer with an item and file path."""
        self.file_path = file_path
        self.item = item

    def compose_question(self, item_data):
        """Compose a question using the provided item data."""
        tree = ET.parse(self.file_path)
        root = tree.getroot()

        self.update_question(root, tree, item_data)
        self.update_answers(root, tree, item_data)
        self.update_solution(root, tree, item_data)

    def update_question(self, root, tree, item_data):
        """Update the question text for a given item."""
        for item in root.iter('item'):
            if item.attrib['ident'] == item_data['identifier']:
                question_element = item.find('.//presentation/flow/material/mattext')
                question_element.text = item_data['question']

        self._write_to_file(tree)

    def update_answers(self, root, tree, item_data):
        """Update the answer text for a given item."""
        for item in root.iter('item'):
            if item.attrib['ident'] == item_data['identifier']:
                for answer in item.find('.//presentation/flow/response_lid/'):
                    if 'ident' in answer.attrib:
                        new_answer = item_data['answers'][answer.attrib['ident']]
                        mattext = answer.find('.//material/mattext')
                        mattext.text = new_answer

        self._write_to_file(tree)

    def update_solution(self, root, tree, item_data):
        """Update the solution for a given item."""
        for item in root.iter('item'):
            if item.attrib['ident'] == item_data['identifier']:
                for respcondition in item.findall('.//respcondition'):
                    varequal = respcondition.find('.//conditionvar/varequal')
                    displayfeedback = respcondition.find('.//displayfeedback')
                    if varequal is not None and displayfeedback is not None:
                        identifier = varequal.text.strip()
                        if identifier in item_data['solutions']:
                            varequal.text = identifier
                            displayfeedback.attrib['linkrefid'] = item_data['solutions'][identifier]

        self._write_to_file(tree)

    def _write_to_file(self, tree):
        """Write the changes to the file."""
        tree.write(self.file_path)

    def generate_exam(self, data):
            """Generate an exam using the provided data."""
            # Ensure the source file exists
            source = self.file_path
            if not os.path.exists(source):
                raise FileNotFoundError(f"Source file not found: {source}")

            # Create the destination directory if it does not exist
            temp_dir = self.get_resource_path('backend/data/temp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Create a safe title for the destination file
            assessment_title = data['assessment title']
            safe_title = assessment_title.replace(' ', '_')
            destination = os.path.join(temp_dir, f'{safe_title}.xml')

            # Copy the source file to the destination
            shutil.copy(source, destination)

            # Update the file path to the new file
            self.file_path = destination

            # Parse the XML file
            tree_assessment = ET.parse(self.file_path)
            root_assessment = tree_assessment.getroot()

            # Update the assessment title
            self.update_assessment_title(root_assessment, tree_assessment, assessment_title)

            # Remove the assessment title from the data
            data.pop('assessment title')

            # Generate questions
            self.generate_questions(root_assessment, tree_assessment, data)

            return self.file_path


    def update_assessment_title(self, root_assessment, tree_assessment, title):
        """Update the title of the exam."""
        for assessment in root_assessment.iter('assessment'):
            assessment.attrib['ident'] = self.get_unique_id()
            assessment.attrib['title'] = title
        self._write_to_file(tree_assessment)

    def generate_questions(self, root_assessment, tree_assessment, data):
        """Generate questions for the exam."""
        for question_data in data.values():
            template_path = self.get_resource_path(self.select_template(question_data['title']))
            if template_path is not None:
                temp_filepath = self.generate_question_from_template(template_path, question_data)
                self.insert_question(root_assessment, tree_assessment, temp_filepath)
            else:
                print(f"Unsupported question type: {question_data['title']}")
    
        # self._write_to_file(tree_assessment)

    def select_template(self, question_type):
        templates = {
            'Multiple Choice': 'backend/data/multiple_choice.xml',
            'Multiple Correct': 'backend/data/multiple_correct.xml',
            'Multiple Correct Single Selection': 'backend/data/multiple_correct.xml',
            'True - False': 'backend/data/true_false.xml',
            'Essay Question': 'backend/data/essay_question.xml',
        }
        return templates.get(question_type, None)

    def find_parent(self, tree, child):
        """Find the parent of a given child element."""
        for parent in tree.iter():
            if child in list(parent):
                return parent
        return None  # In case the parent is not found

    def insert_question(self, root_assessment, tree_assessment, temp_filepath):
        print(temp_filepath)

        # Load the temporary question XML
        temp_tree = ET.parse(temp_filepath)
        temp_root = temp_tree.getroot()

        # Find the insertion point
        items = root_assessment.findall('.//item')
        if not items:  # If it's the first question
            # Find the <selection_ordering> tag to insert after
            selection_ordering = root_assessment.find('.//selection_ordering')
            if selection_ordering is not None:
                insertion_point = selection_ordering
            else:
                # Handle case where <selection_ordering> is not found
                print("Error: <selection_ordering> tag not found.")
                return
        else:  # If it's not the first question
            # Insert after the last <item> tag
            insertion_point = items[-1]

        # Find the parent of the insertion point
        parent = self.find_parent(tree_assessment, insertion_point)
        if parent is None:
            print("Error: Parent not found.")
            return

        # Insert the question
        index = list(parent).index(insertion_point) + 1
        parent.insert(index, temp_root)

        # Save the updated assessment document
        tree_assessment.write(self.file_path)

    def generate_question_from_template(self, template_path, question_data):
        # load the xml template 
        
        tree = ET.parse(template_path)
        root = tree.getroot()

        temp_filename = f"temp_question_{self.get_unique_id()}.xml"
        temp_filepath = self.get_resource_path(f"backend/data/temp/{temp_filename}")

        # update the identifier of the template 
        root.attrib['ident'] = question_data['identifier']
        tree.write(temp_filepath)

        # update the template with the question data
        self.update_question(root, tree, question_data)
        
        # update the answers
        self.update_answers(root, tree, question_data)

        # update the solution   
        self.update_solution(root, tree, question_data)

        tree.write(temp_filepath)

        return temp_filepath

    @staticmethod
    def get_unique_id():
        """Generate a unique identifier."""
        QTI12Composer.id_counter += 1
        return str(QTI12Composer.id_counter)
    
    def get_resource_path(self, relative_path):
        """ Get the absolute path to a resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores the path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)


