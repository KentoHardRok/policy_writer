import pandas as pd
from jinja2 import Template
from altr_df_alt import NameConvert as nc
import re

# This is where I read in the CSV file and save it to the Pandas DF
df = pd.read_csv('va3_add.csv')

df['name'] = df.apply(lambda row: nc(row['name']) if pd.notna(row['name']) else row['name'], axis=1)
df['name'] = df['name'].str.replace(r'^\W+', '', regex=True)

df = df.drop_duplicates(subset=['fqdn'])
# This breaks up everything into only the fqdn objects
dfgrp = df.groupby('type')
dfqdn = dfgrp.get_group('fqdn')


# same for comments with nothing there
no_comment = df['comment'].isnull()
dfqdn.loc[no_comment, 'comment'] = 'none'

# This only picks the lines which are wildcards
dfqdn = dfqdn[(dfqdn['fqdn'].str.startswith(('.', '*')) | dfqdn['fqdn'].str.endswith(('.', '*')))]

dfqdn['fqdn'] = dfqdn['fqdn'].str.split('\n').tolist()

dfqdn['name'].to_csv('va3_customurlname_only.csv', index=False)

# Opening the template
with open('custom_url_xml.j2') as file:
        template = Template(file.read())

with open('config/va3_customurl_config.xml', 'a') as f:
    f.write('<config>\n')
    f.write('  <shared>\n')
    f.write('    <profiles>\n')
    f.write('      <custom-url-category>\n')
    for _, row in dfqdn[dfqdn['visibility'] != 'disabled'].iterrows():
        # Below we are assigning values to each of the values used in the template
        # per row
            address_config = template.render(
                name=row['name'],
                members=row['fqdn']
            )
        # Remove empty lines from the rendered output
            output_lines = [line for line in address_config.split('\n') if line.strip()]
        # Append the output to the output file
            f.write('\n'.join(output_lines))
            f.write('\n')
    f.write('      </custom-url-category>\n')
    f.write('    </profiles>\n')
    f.write('  </shared>\n')
    f.write('</config>\n')

