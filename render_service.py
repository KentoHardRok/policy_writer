import pandas as pd
import re
from altr_df_alt import NameConvert as nc
from jinja2 import Template

#Import csv of grp definitions into pandas df
dfsrv = pd.read_csv('va1_srv.csv')

dfsrv['name'] = dfsrv['name'].apply(lambda x: '"' + x + '"')

#format the name column
dfsrv['name'] = dfsrv.apply(lambda row: nc(row['name']) if
        pd.notna(row['name']) else row['name'], axis=1)

new_rows = []
for i, row in df.iterrows():
    ports = row['tcp-port'].split(' ')
    for port in ports:
        tcp_port, source_ports = port.split(':') if ':' in port else (port, '')
        source_ports = source_ports.split('-') if '-' in source_ports else [source_ports, source_ports]
        new_row = row.copy()
        new_row['tcp-port'] = tcp_port
        new_row['source-port-start'] = source_ports[0]
        new_row['source-port-end'] = source_ports[1]
        new_rows.append(new_row)

new_df = pd.concat([df] + new_rows, ignore_index=True)
new_df = new_df.drop(columns=['tcp-port'])

# ok now we try to convert each item of the datafrae list to the list save in
dfsrv['member'] = dfsrv['member'].apply(lambda x: [nc(name) for name
    in x])

dfsrv['member'] = dfsrv['member'].apply(lambda x: [item for item in
    x if item in dfadd['name'].values or item in dfsrv['name'].values])

# now we turn this column into something we can import to the template
dfsrv['member'] = dfsrv['member'].apply(lambda x: ' '.join(x))


# open template
with open('addgrp_temp.j2') as file:
    template = Template(file.read())

with open('va1_addgrp_config.txt', 'a') as f:
    for index, row in dfsrv.iterrows():
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
