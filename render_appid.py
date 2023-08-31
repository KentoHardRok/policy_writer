import pandas as pd
import re
from altr_df_alt import NameConvert as nc
from jinja2 import Template

#Import csv of grp definitions into pandas df
dfsrv = pd.read_csv('~/aws_serv.csv')

dfsrv['name'] = dfsrv['name'].apply(lambda x: '"' + x + '"')

#format the name column
dfsrv['name'] = dfsrv.apply(lambda row: nc(row['name']) if
        pd.notna(row['name']) else row['name'], axis=1)

dfsrv['name'].to_csv('aws_appid_obj.csv', index=False)

dfsrv = dfsrv[pd.notna(dfsrv['protocol'])]

dfsrv['name'].to_csv('aws_appidname_only.csv', index=False)

# open template
with open('addappid_xml.j2') as file:
    template = Template(file.read())

with open('config/aws_appid.xml', 'a') as f:
    f.write('<config>\n')
    f.write('  <shared>\n')
    f.write('    <service>\n')
    for index, row in dfsrv.iterrows():
        addgrp_config = template.render(
            service_name=row['name'],
        )
    # Remove empty lines from the rendered output
        output_lines = [line for line in addgrp_config.split('\n') if line.strip()]
    # Append the output to the output file
        f.write('\n'.join(output_lines))
        f.write('\n')

    f.write('    </service>\n')
    f.write('  </shared>\n')
    f.write('</config>\n')
