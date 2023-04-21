import pandas as pd
from altr_df import NameConvert as nc
from jinja2 import Template

#Import csv of grp definitions into pandas df
dfgrp = pd.read_csv('va3_grp.csv')

# Drop rows where there are no memebers
# dfgrp.dropna(subset=['member'], inplace=True)

dfgrp['name'] = dfgrp.apply(lambda row: nc(row['name']) if
        pd.notna(row['name']) else row['name'], axis=1)

# Now we separate the individual items in the memeber column so they are list
# elements
dfgrp['member'] = dfgrp['member'].apply(lambda x: x.split('\n'))

# ok now we try to convert each item of the datafrae list to the list save in
dfgrp['member'] = dfgrp['member'].apply(lambda x: [nc(name) for name
    in x])

# now we turn this column into something we can import to the template
dfgrp['member'] = dfgrp['member'].apply(lambda x: ' '.join(x))

# open template
with open('addgrp_temp.j2') as file:
    template = Template(file.read())

with open('va3_addgrp_config.txt', 'a') as f:
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
