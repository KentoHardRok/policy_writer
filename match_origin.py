import pandas as pd

dflst = pd.read_csv('sort_missing_add.txt', names=['name'])
dfgroup = pd.read_csv('va3_grp.csv')

dflst['match'] = None

dfgroup['member'] = dfgroup['member'].str.split('\n').tolist()

# Function to find matches and update 'match' column
def find_matches(row):
    member_list = row['member']
    matches = dflst[dflst['name'].isin(member_list)]
    if not matches.empty:
        origin_values = row['origin']
        for match_index, match_row in matches.iterrows():
            match_row['match'] = origin_values[member_list.index(match_row['name'])]
            dflst.update(pd.DataFrame([match_row]))

# Apply the function to each row of dfgroup
dfgroup.apply(find_matches, axis=1)


dflst.to_csv('match_obj.csv', index=False)
