import xml.etree.ElementTree as ET

# parse the XML file
tree = ET.parse('config/va1_addgrp.xml')
root = tree.getroot()

# iterate over the child elements of the root
for child in root.findall('./config/shared/entry/*'):
    # iterate over the grandchildren of the child element
    for grandchild in child.findall('./*'):
        # check if the grandchild is called 'member'
        if grandchild.tag == 'member':
            # do something if there is a grandchild called 'member'
            print("Found 'member' in element:", child.tag)

# write the updated XML to a file
tree.write('config/va1_output.xml')

