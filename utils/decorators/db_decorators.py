import os



import utils.constants as c
from utils import logger_utils as log

db_name = c.db_name
cur_file_name = os.path.basename(__file__)
SYS_SERVICES_TABLE_NAME = c.sys_services_table_name
BUSINESS_SERVICES_TABLE_NAME = c.business_services_table_name
SCHEDULERS_TABLE_NAME = c.schedulers_table_name
HARVESTED_ROUTES_TABLE_NAME = c.harvested_routes_table_name
TASKMASTER_TASK_NAMES_TABLE_NAME = c.taskmaster_tasks_types_table_name
ALL_PROCESSES_TABLE_NAME = c.all_processes_table_name
TASKS_TABLE_NAME = c.tasks_table_name
BUSY_PORTS_TABLE_NAME = c.busy_ports_table_name
root_path = c.root_path
engine_path = c.sql_engine_path


# def print_c(text):
#     print(f"[{cur_file_name}] {str(text)}")


def sql_alchemy_db_func(required_args=None):
    def upper(func):
        def inner(*args, **kwargs):
            if required_args:
                # TODO: if not is instance => raise error, then run the code without else
                if isinstance(required_args, list):
                    if not len(args) == len(required_args):
                        raise Exception(
                            f"Amount of arguments provided for function {func.__name__} is {len(args)}, "
                            f"but {len(required_args)} was declared to be needed")
                    ind = 0
                    for arg in required_args:
                        kwargs[arg] = args[ind]
                        ind += 1
                else:
                    raise ValueError(f"decorator needs a list of strings as a 'required_arguments' kwarg")
            import sqlalchemy as alc
            from sqlalchemy.orm import sessionmaker



            kwargs['alc'] = alc
            kwargs['engine'] = kwargs['alc'].create_engine(engine_path)
            kwargs['session'] = sessionmaker(kwargs['engine'])()
            kwargs['connection'] = kwargs['engine'].connect()
            kwargs['metadata'] = kwargs['alc'].MetaData()
            # TODO. on second thought code lines below are needed mostly for system stuff only, maybe have
            # separate decorators for system and business?..
            # like, most probably schedulers, sys services, harvested routes and tasks are needed just for me
            # try:
            #     kwargs['sys_services'] = kwargs['alc'].Table(SYS_SERVICES_TABLE_NAME, kwargs['metadata'],
            #                                                  autoload=True,
            #                                                  autoload_with=kwargs['engine'])
            #     kwargs['business_services'] = kwargs['alc'].Table(BUSINESS_SERVICES_TABLE_NAME, kwargs['metadata'],
            #                                                       autoload=True,
            #                                                       autoload_with=kwargs['engine'])
            #     kwargs['schedulers'] = kwargs['alc'].Table(SCHEDULERS_TABLE_NAME, kwargs['metadata'],
            #                                                autoload=True,
            #                                                autoload_with=kwargs['engine'])
            #     kwargs['harvested_routes'] = kwargs['alc'].Table(HARVESTED_ROUTES_TABLE_NAME, kwargs['metadata'],
            #                                                      autoload=True,
            #                                                      autoload_with=kwargs['engine'])
            #     kwargs['taskmaster_tasks'] = kwargs['alc'].Table(TASKMASTER_TASK_NAMES_TABLE_NAME, kwargs['metadata'],
            #                                                      autoload=True,
            #                                                      autoload_with=kwargs['engine'])
            #     kwargs['all_processes'] = kwargs['alc'].Table(ALL_PROCESSES_TABLE_NAME, kwargs['metadata'],
            #                                                   autoload=True,
            #                                                   autoload_with=kwargs['engine'])
            #     kwargs['tasks'] = kwargs['alc'].Table(TASKS_TABLE_NAME, kwargs['metadata'],
            #                                           autoload=True,
            #                                           autoload_with=kwargs['engine'])
            #     kwargs['busy_ports'] = kwargs['alc'].Table(BUSY_PORTS_TABLE_NAME, kwargs['metadata'],
            #                                                autoload=True,
            #                                                autoload_with=kwargs['engine'])
            # #     TODO: refactor it in a separate method so user can get Table instance without having to look
            # # into here
            # except Exception as e:
            #     log.exception(f"Exception in db_utils decorator (get all sys tables part)")
            #     log.exception(e)
                # print_c(e)
            result = func(**kwargs)
            kwargs['connection'].connection.commit()
            kwargs['connection'].connection.close()
            # print_c("query executed, connection closed")
            log.debug(f"{func.__name__} query executed, connection closed")
            return result

        return inner

    return upper
