import os

import utils.read_from_yaml as yaml_utils
from utils.decorators.db_decorators import sql_alchemy_db_func
import sqlite3

from utils.json_utils import read_from_json

cur_file_name = os.path.basename(__file__)
root_path = os.path.dirname(os.path.abspath(__file__)).replace('utils', '')
conf_path = f"{root_path}//resources//fuse.yaml"
config = yaml_utils.read_from_yaml(conf_path)
SYS_SERVICES_TABLE_NAME, BUSINESS_SERVICES_TABLE_NAME = config['sqlite']['init']['table_names']
engine_path = f"sqlite:///{root_path}resources\\main_db2.db"


def print_c(text):
    print(f"[{cur_file_name}] {str(text)}")

# TODO generic operations: drop, delete, insert, select

def process_one_column(column, kwargs):
    print(1)
    alc = kwargs['alc']
    generic_type = None
    column_name = column['name']
    if column['type'] == 'BigInteger':
        generic_type = alc.BigInteger
    elif column['type'] == 'Date':
        generic_type = alc.Date
    elif column['type'] == 'Boolean':
        generic_type = alc.Boolean
    elif column['type'] == 'DateTime':
        generic_type = alc.DateTime
    elif column['type'] == 'Enum':
        generic_type = alc.Enum
    elif column['type'] == 'Float':
        generic_type = alc.Float
    elif column['type'] == 'Integer':
        generic_type = alc.Integer
    elif column['type'] == 'Interval':
        generic_type = alc.Interval
    elif column['type'] == 'LargeBinary':
        generic_type = alc.LargeBinary
    elif column['type'] == 'MatchType':
        generic_type = alc.MatchType
    elif column['type'] == 'Numeric':
        generic_type = alc.Numeric
    elif column['type'] == 'PickleType':
        generic_type = alc.PickleType
    elif column['type'] == 'SchemaType':
        generic_type = alc.SchemaType
    elif column['type'] == 'SmallInteger':
        generic_type = alc.SmallInteger
    elif column['type'] == 'String':
        generic_type = alc.String
    elif column['type'] == 'Text':
        generic_type = alc.Text
    elif column['type'] == 'Time':
        generic_type = alc.Time
    elif column['type'] == 'Unicode':
        generic_type = alc.Unicode
    elif column['type'] == 'UnicodeText':
        generic_type = alc.UnicodeText
    else:
        generic_type = alc.String

    # check primary
    if 'primary_key' in column.keys():
        return alc.Column(column_name, generic_type, primary_key=bool(column['primary_key']))
    # check nullable
    if 'nullable' in column.keys():
        return alc.Column(column_name, generic_type, nullable=bool(column['nullable']))
    return alc.Column(column_name, generic_type)


@sql_alchemy_db_func()
def initial_table_creation(*args, **kwargs):
    # TODO IN PROGRESS
    tables_to_create = config['sqlite']['init']['tables']
    alc = kwargs['alc']
    for table in tables_to_create:
        schema_path = root_path + config['sqlite']['init']['tables'][table]['schema_path']
        schema = read_from_json(schema_path)
        if not alc.inspect(kwargs['engine']).dialect.has_table(kwargs['connection'], table):
            columns = [process_one_column(c, kwargs) for c in schema['columns']]
            temp_table = alc.Table(table, kwargs['metadata'], *columns)

    # tables_to_create = config['sqlite']['init']['table_names']
    # alc = kwargs['alc']
    # for table in tables_to_create:
    #     if not alc.inspect(kwargs['engine']).dialect.has_table(kwargs['connection'], table):
    #         temp_table = alc.Table(
    #             table, kwargs['metadata'],
    #             alc.Column('id', alc.Integer, primary_key=True),
    #             alc.Column('name', alc.String),
    #             alc.Column('port', alc.String),
    #             alc.Column('status', alc.String, nullable=True),
    #             alc.Column('pid', alc.Integer, nullable=False), )
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


def initial_db_creation():
    conn = sqlite3.connect(f"{root_path}resources\\main_db2.db")
    conn.close()