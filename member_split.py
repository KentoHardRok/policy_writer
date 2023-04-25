import pandas as pd
import sys

# create a sample dataframe
df = pd.read_csv('va1_grp.csv')

# function to split long member strings and add new rows recursively
def split_member_strings(df):
    # split long strings in the member column and create new rows with the remaining members
    split_df = df.member.str.split(',', expand=True)
    split_df = split_df.stack().reset_index(level=1, drop=True).rename('member')

    # merge the new rows with the original dataframe and add a new row for each group of rows
    merged_df = pd.merge(df, split_df, left_index=True, right_index=True, how='outer')
    new_rows = merged_df[merged_df.member.str.len() > 100].copy()
    new_rows.member = new_rows.member.str[100:]
    merged_df = pd.concat([merged_df, new_rows], ignore_index=True)

    # copy all other columns from original dataframe to the newly created rows
    other_cols = [col for col in df.columns if col != 'member']
    for col in other_cols:
        merged_df.loc[merged_df.member.isin(new_rows.member), col] = new_rows[col].values

    # check if there are still any long member strings and recursively split and add new rows
    if any(merged_df.member.str.len() > 100):
        return split_member_strings(merged_df)
    else:
        return merged_df

# call the split_member_strings function to split long member strings and add new rows
merged_df = split_member_strings(df)

# group the dataframe by the original index and join the members back into strings
grouped_df = merged_df.groupby(merged_df.index).agg(
    {col: 'first' if col == 'member' else ','.join for col in merged_df.columns}
)

# check the result
#print(grouped_df)

dfprint.to_csv('va1_grp_div.csv')

