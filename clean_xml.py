import xml.etree.ElementTree as ET

# Parse the XML document
tree = ET.parse('config/va3_customurl_config.xml')
root = tree.getroot()

# Create a set to store unique elements
unique_elements = set()

# Iterate through all elements in the XML document
for element in root.iter():
    # Convert the element to a string
    element_str = ET.tostring(element)

    # Check if the element string is already in the set
    if element_str in unique_elements:
        # Remove the duplicate element from its parent
        element.getparent().remove(element)
    else:
        # Add the element string to the set
        unique_elements.add(element_str)

# Save the modified XML document
tree.write('config/va3_customurl_config_clean.xml')

