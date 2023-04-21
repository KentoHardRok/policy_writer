import re

input_str = 

pattern = r"\b((h|n)-((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?:\_(\d+))?)|\w+\b)"

matches = re.findall(pattern, input_str)

results = []

for match in matches:
    if match[1] in ["h"]:
        results.append(match[3])
    elif match[1] in ["n"]:
        results.append(match[3] + "/" + match[4])
    elif match[0] in ["all"]:
        results.append("any")
    else:
        results.append(match[0])

print(results)


def get_country_code(name):
    try: 
        country = pycountry.countries.search_fuzzy(name)[0]
        return country.alpha_2
    except LookupError:
        return None
