import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# load the first XML document
tree1 = ET.parse('config/va1_addgrp.xml')
root1 = tree1.getroot()

# load the second XML document
tree2 = ET.parse('config/va3_addgrp.xml')
root2 = tree2.getroot()

# create a set to store the unique elements
unique_elements = set()

# iterate over the elements in the first document and add them to the set
for element in root1.iter():
    unique_elements.add(ET.tostring(element))

# iterate over the elements in the second document and add them to the set
for element in root2.iter():
    unique_elements.add(ET.tostring(element))

# create a new XML document with the unique elements
merged_root = ET.Element(root1.tag)

for element_string in unique_elements:
    element = ET.fromstring(element_string)
    merged_root.append(element)

merged_tree = ET.ElementTree(merged_root)

# write the merged document to a file
merged_tree.write('config/addgrp_merge.xml', encoding='UTF-8', xml_declaration=True)

# parse the XML document
doc = minidom.parse('config/addgrp_merge.xml')

# use the toprettyxml() method to create a formatted string
pretty_xml = doc.toprettyxml(indent='  ')

# write the formatted string to a file
with open('config/pretty_merge.xml', 'w') as f:
    f.write(pretty_xml)
