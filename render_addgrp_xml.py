import pandas as pd
import re
from altr_df_alt import NameConvert as nc
from jinja2 import Template

# define a regular expression pattern to match the strings between quotes
pattern = r'"[^"]*"'


# define a function to extract the strings and return them as a list
def extract_strings(string):
    return re.findall(pattern, string)


#Import csv of grp definitions into pandas df
dfgrp = pd.read_csv('va3_grp.csv')
dfadd = pd.read_csv('va3_name_only.csv')

dfadd['name'] = dfadd['name'].apply(lambda x: '"' + x + '"')
dfgrp['name'] = dfgrp['name'].apply(lambda x: '"' + x + '"')

dfgrp['origin'] = dfgrp['member'].copy()
dfgrp['origin'] = dfgrp['origin'].str.split('\n').tolist()

#format the name column
dfgrp['name'] = dfgrp.apply(lambda row: nc(row['name']) if
        pd.notna(row['name']) else row['name'], axis=1)

# apply the function to the 'string' column
dfgrp['member'] = dfgrp['member'].apply(extract_strings)

dfgrp[['member', 'origin']].to_csv('origin_names.csv', index=False)

# ok now we try to convert each item of the datafrae list to the list save in
dfgrp['member'] = dfgrp['member'].apply(lambda x: [nc(name) for name
    in x])

# This is meant to delete anything that is not present in add objlist or
# a group name
dfgrp['member'] = dfgrp['member'].apply(lambda x: [item for item in
    x if item in dfadd['name'].values or item in dfgrp['name'].values])

# now lets make sure there are no duplicates in these lists
dfgrp['member'] = dfgrp['member'].apply(lambda x: list(set(x)))

# here we strip the " from the members only
dfgrp['member'] = dfgrp['member'].apply(lambda x: x.strip('"') if isinstance(x, str) else x)

dfgrp['name'] = dfgrp['name'].str.replace(r'^"[^a-zA-Z0-9]+', '"', regex=True)


# open template
with open('addgrp_xml.j2') as file:
    template = Template(file.read())

with open('config/va3_addgrp.xml', 'a') as f:
    f.write('<config>\n')
    f.write('  <shared>\n')
    f.write('    <address-group>\n')
    for index, row in dfgrp.iterrows():
    # Below we are assigning values to each of the values used in the template
    # per row
        addgrp_config = template.render(
            group_name=row['name'],
            members=row['member']
        )
    # Remove empty lines from the rendered output
        output_lines = [line for line in addgrp_config.split('\n') if line.strip()]
    # Append the output to the output file
        f.write('\n'.join(output_lines))
        f.write('\n')

    f.write('    </address-group>\n')
    f.write('  </shared>\n')
    f.write('</config>\n')
