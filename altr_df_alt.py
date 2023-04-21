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
        input_string = input_string[-30:]
        if input_string.endswith('"') and not input_string.startswith('"'):
                    input_string = '"' + input_string
    # Build a regular expression pattern that matches any character that is not
    # a letter, digit, or allowed special character
    allowed_chars = '._" '
    pattern = r"[^a-zA-Z0-9" + re.escape(allowed_chars) + r"\s]"
    # Use the regular expression pattern to replace any matching
    # characters with an empty string
    output_string = re.sub(pattern, '', input_string)
    output_string = re.sub(r'\n', '', output_string)
    output_string = output_string.replace(" ", "")
    return output_string


def main(wurd):
    if type(wurd) == str:
       print(NameConvert(wurd))

if __name__ == "__main__":
   main(sys.argv[1])

