import os

db_name = 'main_db.db'
cur_file_name = os.path.basename(__file__)
SYS_SERVICES_TABLE_NAME = 'Sys_Services'
BUSINESS_SERVICES_TABLE_NAME = 'Business_Services'
SCHEDULERS_TABLE_NAME = 'Schedulers'
root_path = os.path.dirname(os.path.abspath(__file__)).replace('utils\\decorators', '')
engine_path = f"sqlite:///{root_path}resources\\{db_name}"


def print_c(text):
    print(f"[{cur_file_name}] {str(text)}")


def sql_alchemy_db_func(required_args=None):
    def upper(func):
        def inner(*args, **kwargs):
            if required_args:
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
            try:
                kwargs['sys_services'] = kwargs['alc'].Table(SYS_SERVICES_TABLE_NAME, kwargs['metadata'],
                                                             autoload=True,
                                                             autoload_with=kwargs['engine'])
                kwargs['business_services'] = kwargs['alc'].Table(BUSINESS_SERVICES_TABLE_NAME, kwargs['metadata'],
                                                                  autoload=True,
                                                                  autoload_with=kwargs['engine'])
                kwargs['schedulers'] = kwargs['alc'].Table(SCHEDULERS_TABLE_NAME, kwargs['metadata'],
                                                                  autoload=True,
                                                                  autoload_with=kwargs['engine'])
            except Exception as e:
                print_c(e)
            result = func(**kwargs)
            kwargs['connection'].connection.commit()
            kwargs['connection'].connection.close()
            print_c("query executed, connection closed")
            return result

        return inner

    return upper
