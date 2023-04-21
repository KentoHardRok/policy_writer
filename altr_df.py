import sys
import re

"""
This is just a simple function for converting strings to something the Palo
Alto will understand
"""

def NameConvert(input_string):
#Check if the input string is greater than 30 characters
    if len(input_string) > 30:
    # Keep only the last 30 characters
        input_string = '"' + input_string[-30:]
        # Replace any special characters except for '.' and '_' with an empty string
    output_string = ''.join(c for c in input_string if c.isalnum() or c == '.'
            or c == '_' or c == '"')
    output_string = re.sub(r'"(.*?)"', lambda x: '"' + x.group(1).replace('\n',
        '') + '"', output_string)
    output_string = output_string.replace(" ", "")
    return output_string


def main(wurd):
    if type(wurd) == str:
       print(NameConvert(wurd))

if __name__ == "__main__":
   main(sys.argv[1])

