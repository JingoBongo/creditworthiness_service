import os

import utils.constants as c
from utils import logger_utils as log


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
            kwargs['engine'] = kwargs['alc'].create_engine(c.sql_engine_path)
            kwargs['session'] = sessionmaker(kwargs['engine'])()
            kwargs['connection'] = kwargs['engine'].connect()
            kwargs['metadata'] = kwargs['alc'].MetaData()

            result = func(**kwargs)
            kwargs['connection'].connection.commit()
            kwargs['connection'].connection.close()
            log.debug(f"{func.__name__} query executed, connection closed")
            return result

        return inner

    return upper
