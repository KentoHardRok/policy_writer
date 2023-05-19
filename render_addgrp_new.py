import pandas as pd
import re
from altr_df_alt import NameConvert as nc
from jinja2 import Template

def apply_nc(lst):
    return [nc(dst) for dst in lst]

"mirror.atl.genesisadaptive.com"
#Import csv of grp definitions into pandas df
dfgrp = pd.read_csv('va1_grp.csv')


#format the name column
dfgrp['name'] = dfgrp.apply(lambda row: nc(row['name']) if
        pd.notna(row['name']) else row['name'], axis=1)

dfgrp['origin'] = dfgrp['member'].copy()

dfgrp['origin'] = dfgrp['origin'].str.split('\n').tolist()

dfgrp['member'] = dfgrp['member'].str.replace(r'(?<!")\n(?!"\s*)', '', regex=True)

dfgrp['member'] = dfgrp['member'].str.split('\n').tolist()

dfgrp['member'] = dfgrp['member'].apply(lambda lst: [item.replace('"', '') for item in lst])

dfgrp['member'] = dfgrp['member'].apply(lambda x: apply_nc(x) if isinstance(x, list) else [])

dfgrp['member'] = dfgrp['member'].apply(lambda lst: [re.sub(r'^\W', '', word) for word in lst])

dfgrp['name'] = dfgrp['name'].apply(lambda x: '"' + x + '"')

# open template
with open('addgrp_xml.j2') as file:
    template = Template(file.read())

with open('config/va1_addgrp_new.xml', 'a') as f:
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
