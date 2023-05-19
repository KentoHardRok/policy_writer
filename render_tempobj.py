import pandas as pd
import re
from jinja2 import Template

#Import csv of grp definitions into pandas df
dfobj = pd.read_csv('sort_missing_add.txt', names=['name'])

# open template
with open('addfakeobj_xml.j2') as file:
    template = Template(file.read())

with open('config/all_fake_obj.xml', 'a') as f:
    f.write('<config>\n')
    f.write('  <shared>\n')
    f.write('    <address>\n')
    for index, row in dfobj.iterrows():
        addgrp_config = template.render(
            service_name=row['name'],
        )
    # Remove empty lines from the rendered output
        output_lines = [line for line in addgrp_config.split('\n') if line.strip()]
    # Append the output to the output file
        f.write('\n'.join(output_lines))
        f.write('\n')

    f.write('    </address>\n')
    f.write('  </shared>\n')
    f.write('</config>\n')
