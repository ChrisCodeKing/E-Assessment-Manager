
import os
import xml.etree.ElementTree as ET

class QTI12Parser:
    """A class to parse QTI 1.2 files."""

    def __init__(self, file=None):
        """Initialize the parser with a file, or use a default file if none is provided."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.file = file or os.path.join(base_dir, 'ec_testquiz.xml')
        # print(f'Parsing file: {self.file}')
        self.tree = self._generate_tree()
        self.structure = self._generate_structure()

    def _generate_tree(self):
        """Parse the XML file and return the resulting tree."""
        try:
            return ET.parse(self.file)
        except Exception as e:
            print(f'Error: {e}')
            return None

    def _generate_structure(self):
        """Generate the structure of the QTI document."""
        try:
            root = self.tree.getroot()
            if root.tag == 'questestinterop':
                # print('Valid QTI root found')
                if len(root.findall('.//assessment/section/item')) > 0:
                    # print('Assessment -> Section -> Item - SAKAI QTI')
                    return self._find_items()
                elif len(root.findall('.//section/item')) > 0:
                    # print('Section -> Item')
                    return self._find_items()
                elif len(root.findall('.//item')) > 0:
                    # print('Item')
                    return self._find_items()
                else:
                    print('No valid QTI structure found')
        except Exception as e:
            print(f'Error: {e}')

    def _find_items(self):
        """Find all items in the QTI document and return a dictionary of their data."""
        # print('Finding items')
        item_data = {}
        for index, item in enumerate(self.tree.findall('.//item')):
            item_info = {
                'identifier': item.attrib['ident'],
                'title': item.attrib['title'],
                'question': self._find_question(item),
                'answers': self._find_answers(item),
            }
            item_info['solutions'] = self._find_solutions(item, item_info['answers'])
            item_data[index] = item_info
        return item_data

    @staticmethod
    def _find_question(item):
        """Find the question text for a given item."""
        questions = ""
        for question in item.findall('.//presentation/flow/material/mattext'):
            if question is not None and question.text is not None:
                text = question.text.replace('\n', ' ').strip()
                questions = ' '.join(text.split())
        return questions

    @staticmethod
    def _find_answers(item):
        """Find the answers for a given item."""
        answers = {}
        for answer in item.findall('.//response_label'):
            if 'ident' in answer.attrib:
                ident = answer.attrib['ident']
                mattext = answer.find('.//material/mattext')
                answer_text = mattext.text.strip() if mattext is not None and mattext.text is not None else ""
                answers[ident] = answer_text
        return answers
    
    @staticmethod
    def _find_solutions(item, answers):
        """Find the solutions for a given item."""
        solutions = {}
        for solution in item.findall('.//respcondition'):
            identifier = solution.find('.//conditionvar/varequal').text.strip()
            condition = solution.find('.//displayfeedback').attrib['linkrefid']
            if identifier in answers:
                solutions[identifier] = condition
        return solutions

    def get_structure(self):
        """Return the structure of the QTI document."""
        return self.structure
    

