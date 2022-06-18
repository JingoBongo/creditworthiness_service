import __init__
import os

db_name = 'main_db.db'
life_ping_endpoint_context = '/life_ping'
root_path = os.path.dirname(os.path.abspath(__file__)).replace('utils', '')
conf_path = os.path.normpath('.//resources//fuse.yaml')
sys_services_table_name = 'Sys_Services'
business_services_table_name = 'Business_Services'
schedulers_table_name = 'Schedulers'
harvested_routes_table_name = 'Harvested_Routes'
sql_engine_path = f"sqlite:///{root_path}resources\\{db_name}"
templates_folder_name = 'templates'
schedulers_folder_name = 'schedulers'
system_schedulers_folder_name = 'system_schedulers'
life_ping_schedule_name = 'life_ping_schedule'
life_ping_schedule_pyfile_name = 'life_ping_schedule.py'
route_harvester_schedule_name = 'route_harvester_schedule'
route_harvester_schedule_pyfile_name = 'route_harvester_schedule.py'
logs_folder_name = 'logs'
current_subprocess_logger = None
current_rotating_handler = None
current_console_handler = None













fuse_logo = '    ______     \n'\
'   / ____/_  __________ \n'\
'  / /_  / / / / ___/ _ \\\n'\
' / __/ / /_/ (__  )  __/\n'\
'/_/    \__,_/____/\___/ \n'\
'                        \n'
