import pandas as pd
import re
from altr_df_alt import NameConvert as nc
from jinja2 import Template

#Import csv of grp definitions into pandas df
dfgrp = pd.read_csv('va1_grp.csv')
dfadd = pd.read_csv('va1_name_only.csv')

dfadd['name'] = dfadd['name'].apply(lambda x: '"' + x + '"')
dfgrp['name'] = dfgrp['name'].apply(lambda x: '"' + x + '"')

#format the name column
dfgrp['name'] = dfgrp.apply(lambda row: nc(row['name']) if
        pd.notna(row['name']) else row['name'], axis=1)

# define a function to extract the strings and return them as a list
#def extract_strings(string):
#    return re.findall(pattern, string)


# apply the function to the 'string' column
#dfgrp['member'] = dfgrp['member'].apply(extract_strings)

# ok now we try to convert each item of the datafrae list to the list save in
dfgrp['member'] = dfgrp['member'].apply(lambda x: [nc(name) for name
    in x])

dfgrp['member'] = dfgrp['member'].apply(lambda x: [item for item in
    x if item in dfadd['name'].values or item in dfgrp['name'].values])

# now we turn this column into something we can import to the template
dfgrp['member'] = dfgrp['member'].apply(lambda x: ' '.join(x))


# open template
with open('addgrp_temp.j2') as file:
    template = Template(file.read())

with open('va1_addgrp_config.txt', 'a') as f:
    for index, row in dfgrp.iterrows():
        # Below we are assigning values to each of the values used in the template
        # per row
            addgrp_config = template.render(
                group_name=row['name'],
                member=row['member']
            )
        # Remove empty lines from the rendered output
            output_lines = [line for line in addgrp_config.split('\n') if line.strip()]
        # Append the output to the output file
            f.write('\n'.join(output_lines))
            f.write('\n')

# dont forget to run sed -i '/\[[[:space:]]*\]/d' va1_addgrp_config.txt
