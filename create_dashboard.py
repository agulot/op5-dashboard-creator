#!/usr/bin/python
import MySQLdb, sys
if len(sys.argv) <= 1:
        sys.exit("One argument required. Example: %s <hostgroup>" %(sys.argv[0]))
host_group = sys.argv[1]
connection = MySQLdb.connect(host= "localhost",
                  user="root",
                  passwd="",
                  db="merlin")
cursor = connection.cursor()
quoted_host_group='"'+host_group.lower()+'"'

def create_widgets (dashboard_id):
  lines=[]
  lines.append('netw_outages  | {"c":4,"p":0} | {}')
  lines.append('tac_scheduled | {"c":3,"p":0} | {}')
  lines.append('state_summary | {"c":4,"p":1} | {"refresh_interval":"60","filter_id":"'+str(service_filter)+'"}')
  lines.append('state_summary | {"c":3,"p":1} | {"refresh_interval":"60","filter_id":"'+str(host_filter)+'"}')
  lines.append('tablestat     | {"c":5,"p":2} | {"filter":"[services] host.groups >= \\"hg_temp1\\"","title":"HG_TEMP1 Service Stats","refresh_interval":"60"}')
  lines.append('tablestat     | {"c":5,"p":0} | {"filter":"[hosts] groups >= \\"hg_temp1\\"","title":"HG_TEMP1 Host Stats","refresh_interval":"60"}')
  lines.append('listview      | {"c":5,"p":1} | {"title":"Unacknowledged HG_TEMP1 Host Problems","query":"[hosts] groups >= \\"hg_temp1\\" and state != 0 and acknowledged = 0 and scheduled_downtime_depth = 0","columns":"select, state, icon_image_expanded, name, status, actions, \\"Host Group\\" = groups, duration, status_information, \\"Host Group\\" = groups,  \\"Contact Notified\\" = contacts, \\r\\n \\"Notifications Sent\\" = current_notification_number,    services_list_all, services_num_warning, services_num_critical, services_num_unknown, services_num_pending","limit":"20","order":"duration asc"}')
  lines.append('listview      | {"c":5,"p":3} | {"title":"Unacknowledged HG_TEMP1 Service Problems","query":"[services] host.groups >= \\"hg_temp1\\" and state != 0 and acknowledged = 0 and scheduled_downtime_depth = 0","columns":"select, host_state, host_name, \\"Host Groups\\" = groups, host_actions, select, state, description, status, actions, status_information, duration, \\"Contact Notified\\" = contacts, \\r\\n \\"Notifications Sent\\" = current_notification_number","limit":"100","order":"duration asc"}')
  for line in lines:
    name, position, template = line.split('|')
    lower_temp=template.replace("hg_temp1", host_group.lower())
    setting=lower_temp.replace("HG_TEMP1", host_group.upper())  
    cursor.execute("INSERT INTO dashboard_widgets (dashboard_id, name, position, setting) VALUES (%s, %s, %s, %s)",(dashboard_id, name.strip(), position.strip(), setting.strip()))
    connection.commit()
 

#### Test is host group "hosts" filter exists and create it if it does not
query="SELECT id FROM ninja_saved_filters WHERE LOWER(filter_name) LIKE LOWER('%"+host_group.lower()+" Host%')"
cursor.execute(query)

if not cursor.rowcount:
  print "Creating Host filter for "+host_group.lower()+"."
  filter_create="INSERT INTO ninja_saved_filters (filter_name, filter_table, filter, filter_description) VALUES ('"+host_group.upper()+" Hosts', 'hosts', '[hosts] groups >= "+quoted_host_group+"', '"+host_group.upper()+" Hosts')"
  cursor.execute(filter_create)
  connection.commit()
  host_filter=cursor.lastrowid
else:
  result = cursor.fetchall()
  for row in result:
    host_filter=str(row[0])
    print host_group.upper()+" Hosts filter already exists as id:"+host_filter+". Moving to Service filter."

#### Test is host group "services" filter exists and create it if it does not
query="SELECT id FROM ninja_saved_filters WHERE LOWER(filter_name) LIKE LOWER('%"+host_group.lower()+" Service%')"
cursor.execute(query)

if not cursor.rowcount:
  print "Creating Services filter for "+host_group.lower()+"."
  filter_create="INSERT INTO ninja_saved_filters (filter_name, filter_table, filter, filter_description) VALUES ('"+host_group.upper()+" Services', 'services', '[services] host.groups >= "+quoted_host_group+"', '"+host_group.upper()+" Services')"
  cursor.execute(filter_create)
  connection.commit()
  service_filter=cursor.lastrowid
else:
  result = cursor.fetchall()
  for row in result:
    service_filter=str(row[0]) 
    print host_group.upper()+" Services filter already exists as id:"+service_filter+". Moving to Dashboard creation."

#### Test if Dashboard already exists if not create it
query="SELECT id FROM dashboards WHERE name like '%"+host_group.upper()+" Datacenter%'"
cursor.execute(query)

if not cursor.rowcount:
  print "Dashboard not found. Creating ..."
  board_create="INSERT INTO dashboards (name, username, layout, read_perm) VALUES ('"+host_group.upper()+" Datacenter', 'administrator', '3,2,1', ',8,10,11,12,')"
  cursor.execute(board_create)
  connection.commit()
  dashboardid=cursor.lastrowid
  create_widgets(dashboardid) 
else:
  result = cursor.fetchall()
  for row in result:
    id=str(row[0])
    print host_group.upper()+" Datacenter Dashboard already exists."


