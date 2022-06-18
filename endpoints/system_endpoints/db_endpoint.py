import __init__
from argparse import ArgumentParser

from utils.flask_child import FuseNode
from utils import constants as c
from utils import logger_utils as log
from utils import db_utils

parser = ArgumentParser()
app = FuseNode(__name__, template_folder=c.root_path + c.templates_folder_name, arg_parser=parser)


@app.route('/select/<string:table_name>')
def select_from_table(table_name):
    """Select from given table, argument - table_name
        ---
    responses:
      200:
           description: 99% caution
        """
    try:
        return str(db_utils.select_from_table(table_name))
    except Exception as e:
        return {'msg': 'Something went horribly wrong while trying to select from ' + table_name,
                'status': 'error', 'exception': e}


@app.route('/clear/<string:table_name>')
def clear_table_from_contents(table_name):
    """Clear contents of a table, argument - table_name
        ---
    responses:
      200:
        description: 99% caution
        """
    try:
        db_utils.clear_table(table_name)
        return {'msg':'success','status':'ok'}
    except Exception as e:
        return {'msg': 'Something went horribly wrong while trying to clear ' + table_name,
                'status': 'error', 'exception': e}


if __name__ == "__main__":
    app.run()
