import __init__

from utils.config_utils import get_config
from utils.decorators.db_decorators import sql_alchemy_db_func
import sqlite3
from utils import constants as c
from utils import logger_utils as log

# meh, takes x times less lines, still a bit ugly
from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Float, Integer, Interval, Date, LargeBinary, Numeric
from sqlalchemy import PickleType, SmallInteger, String, Text, Time, Unicode, UnicodeText, Table

from utils.json_utils import read_from_json

alc_dictionary = {'BigInteger': BigInteger,
                  'Date': Date,
                  'Boolean': Boolean,
                  'DateTime': DateTime,
                  'Enum': Enum,
                  'Float': Float,
                  'Integer': Integer,
                  'Interval': Interval,
                  'LargeBinary': LargeBinary,
                  'MatchType': Date,
                  'Numeric': Numeric,
                  'PickleType': PickleType,
                  'SmallInteger': SmallInteger,
                  'String': String,
                  'Text': Text,
                  'Time': Time,
                  'Unicode': Unicode,
                  'UnicodeText': UnicodeText}


def return_column_type_by_name(column: str, kwargs):
    alc = kwargs['alc']
    return alc_dictionary.get(column, alc.String)


def process_one_column(column, kwargs):
    alc = kwargs['alc']
    column_name = column['name']
    generic_type = return_column_type_by_name(column['type'], kwargs)

    # TODO. sqlalchemy doesnt accept dict as kwargs, therefore for now it is a dumb if-chain
    if 'nullable' in column.keys() and 'primary_key' in column.keys():
        return alc.Column(column_name, generic_type, primary_key=bool(column['primary_key']),
                          nullable=bool(column['nullable']))

    # check primary
    if 'primary_key' in column.keys():
        return alc.Column(column_name, generic_type, primary_key=bool(column['primary_key']))

    # check nullable
    if 'nullable' in column.keys():
        return alc.Column(column_name, generic_type, nullable=bool(column['nullable']))
    return alc.Column(column_name, generic_type)


@sql_alchemy_db_func()
def initial_table_creation(*args, **kwargs):
    try:
        config = get_config()
        tables_to_create = config['sqlite']['init']['tables']
    except:
        log.warn(f"It seems there are no tables to re-create on init")
        return
    alc = kwargs['alc']
    for table in tables_to_create:
        schema_path = c.root_path + config['sqlite']['init']['tables'][table]['schema_path']
        schema = read_from_json(schema_path)
        if not alc.inspect(kwargs['engine']).dialect.has_table(kwargs['connection'], table):
            columns = [process_one_column(cc, kwargs) for cc in schema['columns']]
            temp_table = alc.Table(table, kwargs['metadata'], *columns)
    kwargs['metadata'].create_all(kwargs['engine'])
    log.info("Initial table re-creation completed")


def get_table(kwargs, table_name: str):
    return kwargs['alc'].Table(table_name, kwargs['metadata'],
                               autoload=True,
                               autoload_with=kwargs['engine'])


def upsert_tasks_table(task_name, task_unique_name, on_start_unique_fuse_id, status, task_folder_path):
    delete_task_from_tasks_table_by_unique_task_name(task_unique_name)
    dict_values = {'task_name': task_name, 'task_unique_name': task_unique_name,
                   'on_start_unique_fuse_id': on_start_unique_fuse_id, 'status': status,
                   'task_folder_path': task_folder_path}
    insert_into_table(c.tasks_table_name, dict_values)
    log.debug(f"Upserted task {task_unique_name} with values '{dict_values}' in {c.tasks_table_name}")


@sql_alchemy_db_func(required_args=['val_name', 'val_path', 'val_port', 'val_pid'])
def insert_into_sys_services(*args, **kwargs):
    val_port = kwargs['val_port']
    val_name = kwargs['val_name']
    val_pid = kwargs['val_pid']
    val_path = kwargs['val_path']
    ins = get_table(kwargs, c.sys_services_table_name).insert().values(name=val_name, path=val_path, port=val_port,
                                                                       pid=val_pid,
                                                                       status='alive')
    kwargs['engine'].execute(ins)
    log.debug(
        f"Inserted into {c.sys_services_table_name} table: {val_name}, {val_path}, {val_port}, {val_pid}, 'alive'")


@sql_alchemy_db_func(required_args=['val_name', 'val_path', 'val_pid'])
def insert_into_schedulers(*args, **kwargs):
    val_name = kwargs['val_name']
    val_pid = kwargs['val_pid']
    val_path = kwargs['val_path']
    ins = get_table(kwargs, c.schedulers_table_name).insert().values(name=val_name, path=val_path, pid=val_pid)
    kwargs['engine'].execute(ins)
    log.debug(f"Inserted into {c.schedulers_table_name} table: {val_name}, {val_path}, {val_pid}, 'alive'")


@sql_alchemy_db_func(required_args=['table_name'])
def select_from_table(*args, **kwargs):
    try:
        alc = kwargs['alc']
        table = get_table(kwargs, str(kwargs['table_name']))
        query = alc.select([table])
        proxy = kwargs['connection'].execute(query)
        result_set = proxy.fetchall()
        return result_set
    except Exception as e:
        log.exception('Something went horribly wrong while executing "insert_into_business_services_v2"')
        log.exception(e)


@sql_alchemy_db_func(required_args=['val_name', 'val_path', 'val_port', 'val_pid'])
def insert_into_business_services(*args, **kwargs):
    val_port = kwargs['val_port']
    val_name = kwargs['val_name']
    val_pid = kwargs['val_pid']
    val_path = kwargs['val_path']
    ins = get_table(kwargs, c.business_services_table_name).insert().values(name=val_name, path=val_path, port=val_port,
                                                                            pid=val_pid,
                                                                            status='alive')
    kwargs['engine'].execute(ins)
    log.debug(
        f"Inserted into {c.business_services_table_name} table: {val_name}, {val_path}, {val_port}, {val_pid}, 'alive'")


@sql_alchemy_db_func()
def clear_system_services_table(*args, **kwargs):
    d = get_table(kwargs, c.sys_services_table_name).delete()
    kwargs['engine'].execute(d)
    log.debug(f"Cleared {c.sys_services_table_name} table")


@sql_alchemy_db_func()
def clear_business_services_table(*args, **kwargs):
    d = get_table(kwargs, c.business_services_table_name).delete()
    kwargs['engine'].execute(d)
    log.debug(f"Cleared {c.business_services_table_name} table")


@sql_alchemy_db_func()
def clear_schedulers_table(*args, **kwargs):
    d = get_table(kwargs, c.schedulers_table_name).delete()
    kwargs['engine'].execute(d)
    log.debug(f"Cleared {c.schedulers_table_name} table")


@sql_alchemy_db_func()
def clear_tasks_table(*args, **kwargs):
    d = get_table(kwargs, c.taskmaster_tasks_types_table_name).delete()
    kwargs['engine'].execute(d)
    log.debug(f"Cleared {c.taskmaster_tasks_types_table_name} table")


# Be aware that this function requires a dictionary of insert values
# where key = column_name and value is inserted value
@sql_alchemy_db_func(required_args=['table_name', 'values_dict'])
def insert_into_table(*args, **kwargs):
    try:
        table_name = kwargs['table_name']
        values = kwargs['values_dict']
        table = get_table(kwargs, table_name)
        ins = table.insert().values(**values)
        kwargs['engine'].execute(ins)
        log.debug(f"Inserted into {table_name} table: '{kwargs['values_dict']}'")
    except Exception as e:
        log.exception(
            f"Something went horribly wrong while trying to insert values '{kwargs['values_dict']}' into table {kwargs['table_name']}")
        log.exception(e)


# TODO, test this
@sql_alchemy_db_func(required_args=['table_name'])
def clear_table(*args, **kwargs):
    try:
        table_name = kwargs['table_name']
        table = get_table(kwargs, table_name)
        d = table.delete()
        kwargs['engine'].execute(d)
        log.debug(f"Cleared {table_name} table")
    except Exception as e:
        log.exception(
            f"Something went wrong while trying to delete (clear?) table '{kwargs['table_name']}'. Maybe such tables doesn't exist?")
        log.exception(e)


@sql_alchemy_db_func(required_args=['table_name'])
def drop_table(*args, **kwargs):
    try:
        # TODO: revisit this method. it kinda works but looks weird
        table_name = kwargs['table_name']
        table = get_table(kwargs, table_name)
        table = kwargs['metadata'].tables.get(table)
        if table is not None:
            kwargs['metadata'].drop_all(kwargs['engine'], [table], checkfirst=True)
            log.debug(f"Dropped {table_name} table")
        else:
            log.warn(f"Are you sure table {table_name} exists? It doesn't seem so")
    except Exception as e:
        log.exception(
            f"Something went wrong while trying to drop table '{kwargs['table_name']}'. Maybe such tables doesn't exist?")
        log.exception(e)


@sql_alchemy_db_func(required_args=['val_pid'])
def delete_process_from_tables_by_pid(*args, **kwargs):
    alc = kwargs['alc']
    val_pid = kwargs['val_pid']
    pid_column = alc.Column('pid', alc.String)
    int_val_pid = int(val_pid)
    d = get_table(kwargs, c.business_services_table_name).delete().where(pid_column == int_val_pid)
    d2 = get_table(kwargs, c.sys_services_table_name).delete().where(pid_column == int_val_pid)
    d3 = get_table(kwargs, c.all_processes_table_name).delete().where(pid_column == int_val_pid)
    d4 = get_table(kwargs, c.schedulers_table_name).delete().where(pid_column == int_val_pid)
    kwargs['engine'].execute(d)
    kwargs['engine'].execute(d2)
    kwargs['engine'].execute(d3)
    kwargs['engine'].execute(d4)
    log.debug(f"Deleted process by pid {val_pid} both from Sys and Business Tables (+ schedulers + all processes)")


@sql_alchemy_db_func(required_args=['val_port'])
def delete_port_from_busy_ports_by_port(*args, **kwargs):
    alc = kwargs['alc']
    val_port = kwargs['val_port']
    port_column = alc.Column('port', alc.String)
    d = get_table(kwargs, c.business_services_table_name).delete().where(port_column == val_port)
    kwargs['engine'].execute(d)
    log.debug(f"Deleted port {val_port} ({type(val_port)}) from {c.busy_ports_table_name}")


@sql_alchemy_db_func(required_args=['val_key'])
def delete_value_by_key_from_common_strings_table(*args, **kwargs):
    alc = kwargs['alc']
    val_key = kwargs['val_key']
    key_column = alc.Column('key', alc.String)
    common_strings_table: Table = get_table(kwargs, c.common_strings_table_name)
    d = common_strings_table.delete().where(key_column == val_key)
    kwargs['engine'].execute(d)
    log.debug(f"Deleted key-value pair {val_key}  from {c.common_strings_table_name}")


@sql_alchemy_db_func(required_args=['val_table_name', 'val_column_name', 'val_column_type', 'val_column_value'])
def delete_rows_from_table_by_column(*args, **kwargs):
    alc = kwargs['alc']
    val_column_name = kwargs['val_column_name']
    val_column_type = kwargs['val_column_type']
    val_column_value = kwargs['val_column_value']
    val_table_name = kwargs['val_table_name']
    table: Table = get_table(kwargs, val_table_name)
    column = alc.Column(val_column_name, return_column_type_by_name(val_column_type))
    d = table.delete().where(column == val_column_value)
    kwargs['engine'].execute(d)
    log.debug(f"Deleted row by column/value {val_column_name}/{val_column_value} from {val_table_name}")


# TODO: test this as this is jenky af   <<<< finish it first
# In fact, I am not even sure I tried it once.. or even finished it
@sql_alchemy_db_func(
    required_args=['val_table_name', 'val_select_column_name', 'val_select_column_type', 'val_select_column_value',
                   'val_column_name', 'val_column_type', 'val_column_value'])
def update_rows_from_table_by_column(*args, **kwargs):
    alc = kwargs['alc']

    val_select_column_name = kwargs['val_select_column_name']
    val_select_column_type = kwargs['val_select_column_type']
    val_select_column_value = kwargs['val_select_column_value']

    val_column_name = kwargs['val_column_name']
    val_column_value = kwargs['val_column_value']

    val_column_type = kwargs['val_column_type']

    val_table_name = kwargs['val_table_name']
    ttable: Table = get_table(kwargs, val_table_name)
    select_column = alc.Column(val_select_column_name, return_column_type_by_name(val_select_column_type))
    # ccolumn = alc.Column(val_select_column_name, return_column_type_by_name(val_select_column_type))
    # tbl.c[column_name_here]
    # d = table.update(getattr(table.columns, val_select_column_name).values().where(select_column == val_select_column_value)
    stmt = ttable.update().where(ttable.c[val_select_column_name] == val_column_value).values(
        {val_column_name: val_column_value})

    # stmt = ttable.update().where(ttable.c[val_select_column_name] == val_column_value).values({
    # getattr(ttable.c[val_column_name] : val_column_name)})

    kwargs['engine'].execute(stmt)
    # print_c(f"Deleted process by pid {val_pid} both from Sys and Business Tables")
    # log.info(f"Deleted row by column/value {val_column_name}/{val_column_value} from {val_table_name}")


@sql_alchemy_db_func(required_args=['val_task_unique_name'])
def delete_task_from_tasks_table_by_unique_task_name(*args, **kwargs):
    alc = kwargs['alc']
    val_task_unique_name = kwargs['val_task_unique_name']
    unique_task_name_column = alc.Column('task_unique_name', alc.String)
    tasks_table: Table = get_table(kwargs, c.tasks_table_name)
    d = tasks_table.delete().where(unique_task_name_column == val_task_unique_name)
    kwargs['engine'].execute(d)
    log.debug(f"Deleted task {val_task_unique_name}  from {c.tasks_table_name}")


def upsert_key_value_pair_from_common_strings_table(key: str, value: str):
    # this select.. I suppose I will need it one day. If not and 1 month goes from this day, delete (11m/3d/2022)
    # record = select_from_table_by_one_column(c.common_strings_table_name, 'key', key, 'String')
    delete_value_by_key_from_common_strings_table(key)
    insert_into_table(c.common_strings_table_name, {'key': key, 'value': value})
    log.debug(f"Upserted {key} : {value} pair into {c.common_strings_table_name}.")


@sql_alchemy_db_func(required_args=['route'])
def delete_route_from_harvested_routes_by_route(*args, **kwargs):
    alc = kwargs['alc']
    val_route = kwargs['route']
    route_column = alc.Column('route', alc.String)
    d = get_table(kwargs, c.harvested_routes_table_name).delete().where(route_column == str(val_route))
    kwargs['engine'].execute(d)
    log.debug(f"Deleted routes '{val_route}' from {c.harvested_routes_table_name} table")


@sql_alchemy_db_func(required_args=['task_name'])
def delete_task_from_taskmaster_tasks_by_task_name(*args, **kwargs):
    alc = kwargs['alc']
    val_task_name = kwargs['task_name']
    task_name_column = alc.Column('task_name', alc.String)
    taskmaster_task_types_table: Table = get_table(c.taskmaster_tasks_types_table_name)
    d = taskmaster_task_types_table.delete().where(task_name_column == str(val_task_name))
    kwargs['engine'].execute(d)
    log.debug(f"Deleted task '{val_task_name}' from {c.taskmaster_tasks_types_table_name} table")


@sql_alchemy_db_func(required_args=['val_pid'])
def get_service_port_by_pid(*args, **kwargs):
    try:
        alc = kwargs['alc']
        val_pid = kwargs['val_pid']
        pid_column = alc.Column('pid', alc.String)
        port_column = alc.Column('port', alc.String)
        d = get_table(kwargs, c.business_services_table_name).select(port_column).where(pid_column == int(val_pid))
        d2 = get_table(kwargs, c.sys_services_table_name).select(port_column).where(pid_column == int(val_pid))
        prox1 = kwargs['engine'].execute(d)
        prox2 = kwargs['engine'].execute(d2)
        result1 = prox1.fetchall()
        result2 = prox2.fetchall()
        result1 = result1 + result2
        if len(result1) > 1:
            log.warn(f"While getting port by pid {val_pid} we got {len(result1)} results, not one")
        return result1[0]['port']
    except Exception as e:
        log.exception(e)
        return None


@sql_alchemy_db_func(required_args=['table_name', 'column_name', 'column_value', 'column_type'])
def select_from_table_by_one_column(*args, **kwargs):
    try:
        alc = kwargs['alc']
        table_name = kwargs['table_name']
        column_name = kwargs['column_name']
        column_value = kwargs['column_value']
        generic_column = alc.Column(column_name, return_column_type_by_name(kwargs['column_type'], kwargs))

        table = get_table(kwargs, table_name)

        query = alc.select([table]).where(generic_column == column_value)
        proxy = kwargs['connection'].execute(query)
        result_set = proxy.fetchall()
        return result_set
    except Exception as e:
        log.exception('Something went horribly wrong while executing select from table by one column')
        log.exception(e)


@sql_alchemy_db_func(required_args=['val_pid', 'val_status'])
def change_service_status_by_pid(*args, **kwargs):
    val_pid = kwargs['val_pid']
    val_status = kwargs['val_status']
    alc = kwargs['alc']
    pid_column = alc.Column('pid', alc.String)
    q = get_table(kwargs, c.sys_services_table_name).update().where(pid_column == int(val_pid)).values(
        status=str(val_status))
    q2 = get_table(kwargs, c.business_services_table_name).update().where(pid_column == int(val_pid)).values(
        status=str(val_status))
    kwargs['engine'].execute(q)
    kwargs['engine'].execute(q2)
    log.debug(f"Updated service by pid {val_pid} with status {val_status}")


def initial_db_creation():
    conn = sqlite3.connect(f"{c.root_path}resources\\{c.db_name}")
    conn.close()
    log.info(f"Database {c.db_name} exists or was created.")
