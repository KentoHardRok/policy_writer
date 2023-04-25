import re
import sys

def serv():
    """
    First is to outline what we need to convert to get these services correct.
    It seems the special characters we need to convert are as follows:
    - : to ,
    - /s to ,
    - :
