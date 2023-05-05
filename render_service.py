import pandas as pd
import re
from altr_df_alt import NameConvert as nc
from jinja2 import Template

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
dfsrv = pd.read_csv('va3_serv.csv')

dfsrv['name'] = dfsrv['name'].apply(lambda x: '"' + x + '"')

#format the name column
dfsrv['name'] = dfsrv.apply(lambda row: nc(row['name']) if
        pd.notna(row['name']) else row['name'], axis=1)

# This changes the column type to string. easier to work with
dfsrv['tcp-portrange'] = dfsrv['tcp-portrange'].astype(str)

# split the tcp-portrange column into two columns
dfsrv[['tcp-dst', 'tcp-src']] = dfsrv['tcp-portrange'].apply(split_num)

# split the udp-portrange column into two columns
dfsrv[['udp-dst', 'udp-src']] = dfsrv['udp-portrange'].apply(split_num)

# Here I am putting everything into a list
#dfsrv[['tcp-dst', 'tcp-src', 'udp-dst', 'udp-src']] = dfsrv[['tcp-dst', 'tcp-src', 'udp-dst', 'udp-src']].apply(lambda x: x.split(' '))


dfsrv['name'].to_csv('va3_srvname_only.csv', index=False)

# open template
with open('addsrv_xml.j2') as file:
    template = Template(file.read())

# open template
with open('addsrvgroup_xml.j2') as Gfile:
    template_grp = Template(Gfile.read())

with open('config/va3_addsrv_config.xml', 'a') as f:
    f.write('<config>\n')
    f.write('  <shared>\n')
    f.write('    <service>\n')
    for index, row in dfsrv.iterrows():
        # Below we are assigning values to each of the values used in the template
        # per row
            addgrp_config = template.render(
                service_name=row['name'],
		tcp_dst = row['tcp-dst'],
		tcp_src = row['tcp-src'],
		udp_dst = row['udp-dst'],
                udp_src = row['udp-src']
            )
        # Remove empty lines from the rendered output
            output_lines = [line for line in addgrp_config.split('\n') if line.strip()]
        # Append the output to the output file
            f.write('\n'.join(output_lines))
            f.write('\n')

    f.write('    </service>\n')
    f.write('  </shared>\n')
    f.write('</config>\n')

with open('config/va3_addsrvgrp_config.xml', 'a') as f:
    f.write('<config>\n')
    f.write('  <shared>\n')
    f.write('    <service-group>\n')
    for index, row in dfsrv.iterrows():
        # Below we are assigning values to each of the values used in the template
        # per row
            addgrp_config = template_grp.render(
                service_name=row['name'],
		tcp_dst = row['tcp-dst'],
		tcp_src = row['tcp-src'],
		udp_dst = row['udp-dst'],
                udp_src = row['udp-src']
            )
        # Remove empty lines from the rendered output
            output_lines = [line for line in addgrp_config.split('\n') if line.strip()]
        # Append the output to the output file
            f.write('\n'.join(output_lines))
            f.write('\n')

    f.write('    </service-group>\n')
    f.write('  </shared>\n')
    f.write('</config>\n')
