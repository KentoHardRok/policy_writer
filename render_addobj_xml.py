import pandas as pd
from subnet2cidr import mkcidr
from jinja2 import Template
from altr_df_alt import NameConvert as nc
import re

# This is where I read in the CSV file and save it to the Pandas DF
df = pd.read_csv('va3_add.csv')

# This next one liner converts the subnet column to a cidr notation
df['subnet'] = df.apply(lambda row: mkcidr(row['subnet']) if pd.notna(row['subnet']) else row['subnet'], axis=1)

# Next we tackle the empty type column and add the Type to the ipnetmask
mask = df['subnet'].notnull()
df.loc[mask, 'type'] = 'ipnetmask'

# same for comments with nothing there
no_comment = df['comment'].isnull()
df.loc[no_comment, 'comment'] = 'none'

# now for the edge case where there is a fwdn type address object with no value
# defined which is magically saved and used at all
df.loc[(df['type'] == 'fqdn') & (df['fqdn'].isnull()), 'fqdn'] = 'none'

df = df[~(df['fqdn'].str.startswith(('.', '*')) | df['fqdn'].str.endswith(('.', '*')))]

# filter the DataFrame based on the "visibility" column
dfprint = df.loc[(df['visibility'] != 'disabled') & (df['type'] != 'geography')
        & (df['fqdn'] != 'none')]

name_mask = df['name'].str.len() > 30

df['name'] = df['name'].apply(lambda x: re.sub('[^a-zA-Z0-9_.]+', '', x))
df['name'] = df['name'].str.replace(r'^[^a-zA-Z0-9]+', '', regex=True)
df.loc[name_mask, 'name'] = df.loc[name_mask, 'name'].str[-30:]

# Opening the template
with open('addobj_temp.j2') as file:
        template = Template(file.read())

with open('config/va3_addobj_config.txt', 'a') as f:
    for _, row in df[df['visibility'] != 'disabled'].iterrows():
        # Below we are assigning values to each of the values used in the template
        # per row
            address_config = template.render(
                name=row['name'],
                subnet=row['subnet'],
                comment=row['comment'],
                fqdn=row['fqdn'],
                start_ip=row['start-ip'],
                end_ip=row['end-ip'],
                obj_type=row['type'],
                dev_group='all_shared'
            )
        # Remove empty lines from the rendered output
            output_lines = [line for line in address_config.split('\n') if line.strip()]
        # Append the output to the output file
            f.write('\n'.join(output_lines))
            f.write('\n')
