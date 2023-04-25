import pandas as pd

df = pd.DataFrame({'name': ['Web Server', 'Mail Server', 'SSH Server', 'RDP Server', 'Custom App', 'Game Server'],
                   'tcp-port': ['80', '443', '22:1024', '3389:3390', '8080:8081', '36000-59999:1024-65535 1024-65535:36000-59999'],
                   'comment': ['Public access', 'Internal only', 'Admin access', 'Remote desktop', 'Custom app port', 'Gaming port']})

print(df)

new_rows = []
for i, row in df.iterrows():
    ports = row['tcp-port'].split(' ')
    for port in ports:
        tcp_port, source_ports = port.split(':') if ':' in port else (port, '')
    
    new_row = row.copy()
    new_row['tcp-port'] = tcp_port
    new_row['source-port-start'] = source_ports
    new_rows.append(new_row)

new_df = pd.concat([df] + new_rows, ignore_index=True)

print(new_df)

