import pandas as pd
import re
from altr_df_alt import NameConvert as nc
from jinja2 import Template


# Define the function to apply to each item in the list
def apply_nc(lst):
    return [nc(dst) for dst in lst]

# Define a lambda function to check if each item in the list is present in the other dataframe columns
def check_names(lst):
    return all([item in dfadd['name'].values or item in dfgrp['name'].values for item in lst])

def check_service(lst):
    return all([item in dfsrv['name'].values for item in lst])

def add_zone_column(dfpol, intf_col_name, dfzone, default_value='unknown'):
    dfpol[intf_col_name] = dfpol[intf_col_name].apply(lambda lst: sorted(lst))
    dfpol.sort_values(intf_col_name, inplace=True)
    dfzone.sort_values('interface', inplace=True)
    zone_col_name = intf_col_name.replace('intf', 'zone')
    dfpol[zone_col_name] = dfpol[intf_col_name].apply(lambda intf_list: [dfzone.loc[dfzone['interface'] == intf, 'zone'].iloc[0] if len(dfzone.loc[dfzone['interface'] == intf, 'zone']) > 0 else default_value for intf in intf_list])
    dfpol = dfpol.groupby(level=0).agg({col: 'first' if col != intf_col_name else list for col in dfpol.columns})
    return dfpol

def cs(s):
    # Replace any spaces with underscores
    s = re.sub(r'\s+', '_', s)
    # Remove any special characters except underscore and period
    s = re.sub(r'[^\w._]+', '', s)
    return s

#Import csv of grp definitions into pandas df
dfpol = pd.read_csv('va1_pol.csv')
dfadd = pd.read_csv('va1_name_only.csv')
dfgrp = pd.read_csv('va1_grpname_only.csv')
dfsrv = pd.read_csv('va1_srvname_only.csv')
dfzone = pd.read_csv('va1_zone.csv')

dfpol['name'] = dfpol['name'].astype('string')
dfpol['name'] = dfpol.apply(lambda row: str(row['id']) if pd.isna(row['name']) else row['name'], axis=1)
dfpol['name'] = dfpol['name'].apply(cs)
dfpol['name'] = dfpol['name'].apply(lambda x: '"' + x + '"')

# Now put the src and dst addressess into lists since they are seperated by \n
dfpol['dstaddr'] = dfpol['dstaddr'].str.split('\n').tolist()
dfpol['srcaddr'] = dfpol['srcaddr'].str.split('\n').tolist()
dfpol['dstintf'] = dfpol['dstintf'].str.split('\n').tolist()
dfpol['srcintf'] = dfpol['srcintf'].str.split('\n').tolist()
dfpol['service'] = dfpol['service'].str.split('\n').tolist()

# Apply the function to the column of lists and create a new column with the result
dfpol['dstaddr'] = dfpol['dstaddr'].apply(lambda x: apply_nc(x) if isinstance(x, list) else [])
dfpol['srcaddr'] = dfpol['srcaddr'].apply(lambda x: apply_nc(x) if isinstance(x, list) else [])
dfpol['service'] = dfpol['service'].apply(lambda x: apply_nc(x) if isinstance(x, list) else [])

# This section checks for matches in the things we have already created and creates a column for it
dfpol['srcaddr_pass'] = dfpol['srcaddr'].apply(lambda x: check_names(x))
dfpol['dstaddr_pass'] = dfpol['dstaddr'].apply(lambda x: check_names(x))
dfpol['service_pass'] = dfpol['service'].apply(lambda x: check_service(x))

# Here we take care of the int to zone conversion. ARG!
dfpol = add_zone_column(dfpol, 'srcintf', dfzone, default_value='CACI-Trust')
dfpol = add_zone_column(dfpol, 'dstintf', dfzone, default_value='Internet')

# Now its much easier to check what devgroups these belong in
dfpol['src_devgroup'] = dfpol['srczone'].apply(lambda x: [dfzone.loc[dfzone['zone']==i, 'devgroup'].values[0] for i in x if i in dfzone['zone'].tolist()])
dfpol['dst_devgroup'] = dfpol['dstzone'].apply(lambda x: [dfzone.loc[dfzone['zone']==i, 'devgroup'].values[0] for i in x if i in dfzone['zone'].tolist()])


# Here we perform a match to figure out the devgroup
dfpol['devgroup'] = dfpol.apply(lambda x: x['src_devgroup'][0] if
        len(x['src_devgroup']) > 0 and x['src_devgroup'] == x['dst_devgroup']
        else 'Guest Firewall' if 'Guest Firewall' in x['src_devgroup'] or
        'Guest Firewall' in x['dst_devgroup'] else 'VA1_Guest' if 'VA1_Guest'
        in x['src_devgroup'] or 'VA1_Guest' in x['dst_devgroup'] else 'VA1_Edge_Vsys', axis=1)

dfpol['devgroup'] = dfpol['devgroup'].apply(cs)

# We also need to convert the action column to palo talk
dfpol['action'] = dfpol['action'].fillna('deny')
dfpol['action'] = dfpol['action'].replace({'accept': 'allow'})

# Loop through each row in the DataFrame
for i, row in dfpol.iterrows():
    # Loop through each column that contains lists
    for col in ["dstaddr", "srcaddr", "service"]:
        # Check if "all" is in the list
        if "all" in row[col]:
            # Replace "all" with "any"
            dfpol.at[i, col] = [x.replace("all", "any") for x in row[col]]
        elif "ALL" in row[col]:
            # Replace "all" with "any"
            dfpol.at[i, col] = [x.replace("ALL", "any") for x in row[col]]
        elif len(row[col]) == 0:
            # Replace "" with "any"
            dfpol.at[i, col] = ['any']
        
	    

# Now we sort them by the devgroup
dfdev = dfpol.groupby('devgroup')

# and create multiple datasets
dfdev_1 = dfdev.get_group('Global_Internet_Egress')
dfdev_2 = dfdev.get_group('VA1_Edge_Vsys')
#dfdev_3 = dfdev.get_group('Guest_Firewall')
#dfdev_4 = dfdev.get_group('VA3_Guest')

# Now lets sort them by the ID column to make sure they go in the right order
dfdev_1 = dfdev_1.sort_values('id')
dfdev_2 = dfdev_2.sort_values('id')
#dfdev_3 = dfdev_2.sort_values('id')
#dfdev_4 = dfdev_2.sort_values('id')


# Now lets reset the index
dfdev_1 = dfdev_1.apply(lambda x: x.reset_index(drop=True))
dfdev_2 = dfdev_2.apply(lambda x: x.reset_index(drop=True))
#dfdev_3 = dfdev_3.apply(lambda x: x.reset_index(drop=True))
#dfdev_4 = dfdev_4.apply(lambda x: x.reset_index(drop=True))

# open template
with open('secpol_xml.j2') as file:
    template = Template(file.read())
with open('secpol_start_xml.j2') as file:
    template_start = Template(file.read())
with open('secpol_end_xml.j2') as file:
    template_end = Template(file.read())

with open('config/va1_secpol_pass.xml', 'a') as f:
    f.write('<config>\n')
    f.write(' <devices>\n')
    f.write('   <entry name="localhost.localdomain">\n')
    for i, df in enumerate([dfdev_1, dfdev_2], start=1):
        dev_value = df.at[0, 'devgroup']
        start_config = template_start.render(devgroup=dev_value)
        f.write(start_config)
        f.write('\n')
        for index, row in df.iterrows():
            #if row['status'] == 'disable':
            if row['status'] == 'disable' or not all(row[['srcaddr_pass',
                'dstaddr_pass', 'service_pass']]):
                continue
            else:
        # Below we are assigning values to each of the values used in the template
        # per row
                secpol_config = template.render(
                    devgroup=row['devgroup'],
                    rule_name=row['name'],
                    srcip=row['srcaddr'],
                    dstip=row['dstaddr'],
                    srczone=row['srczone'],
                    dstzone=row['dstzone'],
                    action=row['action'],
                    services=row['service']
                )
            # Remove empty lines from the rendered output
                output_lines = [line for line in secpol_config.split('\n') if line.strip()]
                end_config = template_end.render()
            # Append the output to the output file
                f.write('\n'.join(output_lines))
                f.write('\n')
        f.write(end_config)

    f.write('    </entry>\n')
    f.write('  </devices>\n')
    f.write('</config>\n')
