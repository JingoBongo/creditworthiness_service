import __init__
from utils import general_utils as g
from argparse import ArgumentParser
from utils import constants as c
from utils.flask_child2 import FuseNode2
from utils import logger_utils as log

parser = ArgumentParser()
app = FuseNode2(__name__, arg_parser=parser)



# TODO make a way to generate template endpoints instead of keeping templates

@app.route('/')
def hello():
    """Root, please go somewhere else
    ---
    responses:
      200:
        description: why would you go here, go away
    """
    return 'system endpoint'

@app.route('/gegeg')
def gegeg():
    """Root, please go somewhere else
    ---
    responses:
      200:
        description: why would you go here, go away
    """
    return 'system endpoint'


if __name__ == "__main__":
    app.run()
