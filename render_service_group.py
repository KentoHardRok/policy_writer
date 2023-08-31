import pandas as pd
import re
from altr_df_alt import NameConvert as nc
from jinja2 import Template

def apply_nc(lst):
    return [nc(dst) for dst in lst]


# define a function to split the Num column
def split_num(x):
    if pd.isna(x) or x == '' or x == 'nan':
        return pd.Series([None, None])
    elif len(x) == 0:
        return pd.Series([[], []])
    else:
        left = []
        right = []
        for item in x.split(' '):
            if ':' in item:
                left.append(item.split(':')[0])
                right.append(item.split(':')[1])
            else:
                left.append(item)
                right.append('')
        return pd.Series([left, right])

#Import csv of grp definitions into pandas df
dfsrv = pd.read_csv('~/aws_serv.csv')

dfsrv['name'] = dfsrv['name'].apply(lambda x: '"' + x + '"')

#format the name column
dfsrv['name'] = dfsrv.apply(lambda row: nc(row['name']) if
        pd.notna(row['name']) else row['name'], axis=1)

dfsrv['name'].to_csv('aws_srvname_only.csv', index=False)

# convert member to list of members
dfsrv['member'] = dfsrv['member'].str.split('|').tolist()

# Apply name function to the member list
dfsrv['member'] = dfsrv['member'].apply(lambda x: apply_nc(x) if isinstance(x, list) else [])

# open template
with open('addsrvgroup_xml.j2') as Gfile:
    template_grp = Template(Gfile.read())

with open('config/aws_srvgrp_config.xml', 'a') as f:
    f.write('<config>\n')
    f.write('  <shared>\n')
    f.write('    <service-group>\n')
    for index, row in dfsrv.iterrows():
        # Below we are assigning values to each of the values used in the template
        # per row
            addgrp_config = template_grp.render(
                service_name=row['name'],
                members = row['member']
            )
        # Remove empty lines from the rendered output
            output_lines = [line for line in addgrp_config.split('\n') if line.strip()]
        # Append the output to the output file
            f.write('\n'.join(output_lines))
            f.write('\n')

    f.write('    </service-group>\n')
    f.write('  </shared>\n')
    f.write('</config>\n')
