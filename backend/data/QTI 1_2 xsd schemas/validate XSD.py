import os
from lxml import etree

def validate_xml_with_xsd(xml_file, xsd_file):
    # Parse the XSD file
    with open(xsd_file, 'r') as xsd_fp:
        xsd_doc = etree.parse(xsd_fp)
        xsd = etree.XMLSchema(xsd_doc)
    
    # Parse the XML file
    xml_doc = etree.parse(xml_file)
    
    # Validate the XML file with the XSD
    is_valid = xsd.validate(xml_doc)
    
    if is_valid:
        print("The XML file is valid according to the XSD.")
    else:
        print("The XML file is not valid according to the XSD.")
        print(xsd.error_log)

# Example usage
dir_path = os.path.dirname(os.path.realpath(__file__))
xml_file = os.path.join(dir_path, 'multiplechoice QTI1_2 .xml')
xsd_file = os.path.join(dir_path, 'ims_qtiresv1p2.xsd')

validate_xml_with_xsd(xml_file, xsd_file)