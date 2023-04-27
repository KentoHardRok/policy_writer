import pandas as pd
import re
from altr_df_alt import NameConvert as nc
from jinja2 import Template

#Import csv of grp definitions into pandas df
dfgrp = pd.read_csv('va1_grp.csv')
dfadd = pd.read_csv('va1_name_only.csv')

dfadd['name'] = dfadd['name'].apply(lambda x: '"' + x + '"')
dfgrp['name'] = dfgrp['name'].apply(lambda x: '"' + x + '"')

#format the name column
dfgrp['name'] = dfgrp.apply(lambda row: nc(row['name']) if
        pd.notna(row['name']) else row['name'], axis=1)

#dfgrp['name'] = dfgrp['name'].replace(' ', '', regex=True)

# define a regular expression pattern to match the strings between quotespattern = r'"[^"]*"'


# define a function to extract the strings and return them as a list
def extract_strings(string):
    return re.findall(pattern, string)


# apply the function to the 'string' column
dfgrp['member'] = dfgrp['member'].apply(extract_strings)

# ok now we try to convert each item of the datafrae list to the list save in
dfgrp['member'] = dfgrp['member'].apply(lambda x: [nc(name) for name
    in x])

dfgrp['member'] = dfgrp['member'].apply(lambda x: [item for item in
    x if item in dfadd['name'].values or item in dfgrp['name'].values])

##################################new##############################################
# function to split long member strings and add new rows recursively
#def split_member_strings(df):
#    # split long strings in the member column and create new rows with the remaining members
#    split_df = df.member.str.split(',', expand=True)
#    split_df = split_df.stack().reset_index(level=1, drop=True).rename('member')
#
#    # merge the new rows with the original dataframe and add a new row for each group of rows
#    merged_df = pd.merge(df, split_df, left_index=True, right_index=True, how='outer')
#    new_rows = merged_df[merged_df['member'].str.len() > 100].copy()
#    new_rows.member = new_rows.member.str[100:]
#    merged_df = pd.concat([merged_df, new_rows], ignore_index=True)
#
#    # copy all other columns from original dataframe to the newly created rows
#    other_cols = [col for col in df.columns if col != 'member']
#    for col in other_cols:
#        merged_df.loc[merged_df.member.isin(new_rows.member), col] = new_rows[col].values
#
#    # check if there are still any long member strings and recursively split and add new rows
#    if any(merged_df.member.str.len() > 100):
#        return split_member_strings(merged_df)
#    else:
#        return merged_df

# call the split_member_strings function to split long member strings and add new rows
# merged_df = split_member_strings(dfgrp)

# group the dataframe by the original index and join the members back into strings
#dfgrp = merged_df.groupby(merged_df.index).agg(
#    {col: 'first' if col == 'member' else ','.join for col in merged_df.columns}
#)
#########################################################new#########################

# now we turn this column into something we can import to the template
dfgrp['member'] = dfgrp['member'].apply(lambda x: ' '.join(x))


# open template
with open('addgrp_temp.j2') as file:
    template = Template(file.read())

with open('va1_addgrp_config.txt', 'a') as f:
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

# dont forget to run sed -i '/\[[[:space:]]*\]/d' va1_addgrp_config.txt
