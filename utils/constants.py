import __init__
import os

fuse_instance_name = 'Fuse'
db_name = 'main_db.db'
life_ping_endpoint_context = '/life_ping'
root_path = os.path.dirname(os.path.abspath(__file__)).replace('utils', '')
conf_path = os.path.normpath('.//resources//fuse.yaml')
resources_path = os.path.normpath('.//resources')
temporary_files_folder_path = root_path + os.path.normpath('.//resources//temporary_files//')
sys_services_table_name = 'Sys_Services'
business_services_table_name = 'Business_Services'
schedulers_table_name = 'Schedulers'
taskmaster_tasks_table_name = 'Taskmaster_Tasks'
harvested_routes_table_name = 'Harvested_Routes'
all_processes_table_name = 'All_Processes'
sql_engine_path = f"sqlite:///{root_path}resources\\{db_name}"
templates_folder_name = 'templates'
schedulers_folder_name = 'schedulers'
system_schedulers_folder_name = 'system_schedulers'
life_ping_schedule_name = 'life_ping_schedule'
taskmaster_schedule_name = 'taskmaster_schedule'
taskmaster_schedule_pyfile_name = 'taskmaster_schedule.py'
life_ping_schedule_pyfile_name = 'life_ping_schedule.py'
route_harvester_schedule_name = 'route_harvester_schedule'
route_harvester_schedule_pyfile_name = 'route_harvester_schedule.py'
logs_folder_name = 'logs'
tasks_status_new = 'new'
tasks_status_in_progress = 'in_progress'
tasks_status_errored = 'errored'
tasks_status_completed = 'completed'
tasks_status_does_not_exist_locally = 'does_not_exist_locally'
tasks_name_delimiter = '____'
tasks_init_requires_file_name = 'init_requires.pickle'
tasks_global_provides_file_name = 'provides.pickle'
tasks_step_provides_file_name = 'step_provides.pickle'
on_start_unique_fuse_id = None
on_start_unique_fuse_id_name = "on_start_unique_fuse_id"
current_subprocess_logger = None
current_rotating_handler = None
current_console_handler = None













fuse_logo = '    ______     \n'\
'   / ____/_  __________ \n'\
'  / /_  / / / / ___/ _ \\\n'\
' / __/ / /_/ (__  )  __/\n'\
'/_/    \__,_/____/\___/ \n'\
'                        \n'
