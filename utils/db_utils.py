import os
import utils.read_from_yaml as yaml_utils
from utils.decorators.db_decorators import use_db_main_variables_decorator

cur_file_name = os.path.basename(__file__)
SYS_SERVICES_TABLE_NAME = 'Sys_Services'
BUSINESS_SERVICES_TABLE_NAME = 'Business_Services'
root_path = os.path.dirname(os.path.abspath(__file__)).replace('utils', '')
conf_path = f"{root_path}\\resources\\fuse.yaml"
config = yaml_utils.read_from_yaml(conf_path)
engine_path = f"sqlite:///{root_path}resources\\main_db2.db"


def print_c(text):
    print(f"[{cur_file_name}] {str(text)}")


@use_db_main_variables_decorator(engine_path=engine_path, SYS_SERVICES_TABLE_NAME=SYS_SERVICES_TABLE_NAME,
                                 BUSINESS_SERVICES_TABLE_NAME=BUSINESS_SERVICES_TABLE_NAME)
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
                alc.Column('pid', alc.Integer, nullable=False), )
    kwargs['metadata'].create_all(kwargs['engine'])
    print_c("Initial table re-creation completed")


# def insert_into_sys_services_v2(name, port, pid):
#     try:
#         engine, connection, metadata, sys_services, business_services = generate_engine_conn_meta_systable_bustable()
#         query = alc.select([sys_services])
#         proxy = connection.execute(query)
#         result_set = proxy.fetchall()
#         return result_set
#     except Exception as e:
#         print_c('Something went horribly wrong while executing "insert_into_sys_services_v2"')
#         print_c(e)

@use_db_main_variables_decorator(engine_path=engine_path, SYS_SERVICES_TABLE_NAME=SYS_SERVICES_TABLE_NAME,
                                 BUSINESS_SERVICES_TABLE_NAME=BUSINESS_SERVICES_TABLE_NAME,
                                 required_args=['table_name'])
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


@use_db_main_variables_decorator(engine_path=engine_path, SYS_SERVICES_TABLE_NAME=SYS_SERVICES_TABLE_NAME,
                                 BUSINESS_SERVICES_TABLE_NAME=BUSINESS_SERVICES_TABLE_NAME,
                                 required_args=['val_name', 'val_port', 'val_pid'])
def insert_into_sys_services(*args, **kwargs):
    val_port = kwargs['val_port']
    val_name = kwargs['val_name']
    val_pid = kwargs['val_pid']
    ins = kwargs['sys_services'].insert().values(name=val_name, port=val_port, pid=val_pid)
    kwargs['engine'].execute(ins)
    print_c(f"Inserted into sys services table: {val_name}, {val_port}, {val_pid}")


@use_db_main_variables_decorator(engine_path=engine_path, SYS_SERVICES_TABLE_NAME=SYS_SERVICES_TABLE_NAME,
                                 BUSINESS_SERVICES_TABLE_NAME=BUSINESS_SERVICES_TABLE_NAME,
                                 required_args=['val_name', 'val_port', 'val_pid'])
def insert_into_business_services(*args, **kwargs):
    val_port = kwargs['val_port']
    val_name = kwargs['val_name']
    val_pid = kwargs['val_pid']
    ins = kwargs['business_services'].insert().values(name=val_name, port=val_port, pid=val_pid)
    kwargs['engine'].execute(ins)
    print_c(f"Inserted into business services table: {val_name}, {val_port}, {val_pid}")


@use_db_main_variables_decorator(engine_path=engine_path, SYS_SERVICES_TABLE_NAME=SYS_SERVICES_TABLE_NAME,
                                 BUSINESS_SERVICES_TABLE_NAME=BUSINESS_SERVICES_TABLE_NAME)
def clear_system_tables(*args, **kwargs):
    d = kwargs['business_services'].delete()
    kwargs['engine'].execute(d)
    print_c("Cleared Sys_Services table")


@use_db_main_variables_decorator(engine_path=engine_path, SYS_SERVICES_TABLE_NAME=SYS_SERVICES_TABLE_NAME,
                                 BUSINESS_SERVICES_TABLE_NAME=BUSINESS_SERVICES_TABLE_NAME)
def clear_business_tables(*args, **kwargs):
    d = kwargs['sys_services'].delete()
    kwargs['engine'].execute(d)
    print_c("Cleared Business_Services table")
