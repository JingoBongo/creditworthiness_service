import os

import utils.read_from_yaml as yaml_utils
from utils.decorators.db_decorators import sql_alchemy_db_func

cur_file_name = os.path.basename(__file__)
root_path = os.path.dirname(os.path.abspath(__file__)).replace('utils', '')
conf_path = f"{root_path}//resources//fuse.yaml"
config = yaml_utils.read_from_yaml(conf_path)
SYS_SERVICES_TABLE_NAME, BUSINESS_SERVICES_TABLE_NAME = config['sqlite']['init']['table_names']
engine_path = f"sqlite:///{root_path}resources\\main_db2.db"


def print_c(text):
    print(f"[{cur_file_name}] {str(text)}")


@sql_alchemy_db_func()
def initial_table_creation(*args, **kwargs):
    tables_to_create = config['sqlite']['init']['table_names']
    alc = kwargs['alc']
    for table in tables_to_create:
        if not alc.inspect(kwargs['engine']).dialect.has_table(kwargs['connection'], table):
            temp_table = alc.Table(
                table, kwargs['metadata'],
                alc.Column('id', alc.Integer, primary_key=True),
                alc.Column('name', alc.String),
                alc.Column('port', alc.String),
                alc.Column('status', alc.String, nullable=True),
                alc.Column('pid', alc.Integer, nullable=False), )
    kwargs['metadata'].create_all(kwargs['engine'])
    print_c("Initial table re-creation completed")


@sql_alchemy_db_func(required_args=['val_name', 'val_port', 'val_pid'])
def insert_into_sys_services(*args, **kwargs):
    val_port = kwargs['val_port']
    val_name = kwargs['val_name']
    val_pid = kwargs['val_pid']
    ins = kwargs['sys_services'].insert().values(name=val_name, port=val_port, pid=val_pid, status='alive')
    kwargs['engine'].execute(ins)
    print_c(f"Inserted into sys services table: {val_name}, {val_port}, {val_pid}, 'alive'")


@sql_alchemy_db_func(required_args=['table_name'])
def select_from_table(*args, **kwargs):
    try:
        alc = kwargs['alc']
        table = alc.Table(str(kwargs['table_name']), kwargs['metadata'], autoload=True, autoload_with=kwargs['engine'])
        query = alc.select([table])
        proxy = kwargs['connection'].execute(query)
        result_set = proxy.fetchall()
        return result_set
    except Exception as e:
        print_c('Something went horribly wrong while executing "insert_into_business_services_v2"')
        print_c(e)


@sql_alchemy_db_func(required_args=['val_name', 'val_port', 'val_pid'])
def insert_into_business_services(*args, **kwargs):
    val_port = kwargs['val_port']
    val_name = kwargs['val_name']
    val_pid = kwargs['val_pid']
    ins = kwargs['business_services'].insert().values(name=val_name, port=val_port, pid=val_pid, status='alive')
    kwargs['engine'].execute(ins)
    print_c(f"Inserted into business services table: {val_name}, {val_port}, {val_pid}, 'alive'")


@sql_alchemy_db_func()
def clear_system_tables(*args, **kwargs):
    d = kwargs['business_services'].delete()
    kwargs['engine'].execute(d)
    print_c("Cleared Sys_Services table")


@sql_alchemy_db_func()
def clear_business_tables(*args, **kwargs):
    d = kwargs['sys_services'].delete()
    kwargs['engine'].execute(d)
    print_c("Cleared Business_Services table")


@sql_alchemy_db_func(required_args=['val_pid'])
def delete_process_from_tables_by_pid(*args, **kwargs):
    alc = kwargs['alc']
    val_pid = kwargs['val_pid']
    pid_column = alc.Column('pid', alc.String)
    d = kwargs['business_services'].delete().where(pid_column == int(val_pid))
    d2 = kwargs['sys_services'].delete().where(pid_column == int(val_pid))
    kwargs['engine'].execute(d)
    kwargs['engine'].execute(d2)
    print_c(f"Deleted process by pid {val_pid} both from Sys and Business Tables")


@sql_alchemy_db_func(required_args=['val_pid', 'val_status'])
def change_service_status_by_pid(*args, **kwargs):
    val_pid = kwargs['val_pid']
    val_status = kwargs['val_status']
    alc = kwargs['alc']
    pid_column = alc.Column('pid', alc.String)
    q = kwargs['business_services'].update().where(pid_column == int(val_pid)).values(status=str(val_status))
    q2 = kwargs['business_services'].update().where(pid_column == int(val_pid)).values(status=str(val_status))
    kwargs['engine'].execute(q)
    kwargs['engine'].execute(q2)
    print_c(f"Updated process by pid {val_pid} with status {val_status}")
