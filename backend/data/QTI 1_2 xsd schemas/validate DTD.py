import os
from lxml import etree

def validate_xml_with_dtd(xml_file, dtd_file):
    # Get the absolute path of the directory that the script is in
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Use the absolute path to open the DTD file
    dtd_file_path = os.path.join(script_dir, dtd_file)

    # Parse the DTD file
    with open(dtd_file_path, 'r') as dtd_fp:
        dtd = etree.DTD(dtd_fp)
    
    # Use the absolute path to open the XML file
    xml_file_path = os.path.join(script_dir, xml_file)

    # Parse the XML file
    xml_tree = etree.parse(xml_file_path)
    
    # Validate the XML file with the DTD
    is_valid = dtd.validate(xml_tree)
    
    if is_valid:
        print("The XML file is valid.")
    else:
        print("The XML file is not valid.")
        print(dtd.error_log)

# Example usage
xml_file = 'multiplechoice QTI1_2 .xml'
dtd_file = 'QTI Full DTD - ims_qtiasiv1p2.dtd'

validate_xml_with_dtd(xml_file, dtd_file)