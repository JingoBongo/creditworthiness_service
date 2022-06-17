import requests
from flask import url_for, redirect, make_response

import __init__
from utils import general_utils as g
from argparse import ArgumentParser
from utils import constants as c
from utils.flask_child import FuseNode

parser = ArgumentParser()
app = FuseNode(__name__, template_folder=c.root_path + c.templates_folder_name, arg_parser=parser)



@app.route('/')
def hello():
    """Root, please go somewhere else
    ---
    responses:
      200:
        description: why would you go here, go away
    """
    return 'system endpoint'

# @app.route('/provide/tetris')
@app.route('/provide/', defaults={'path': ''})
@app.route('/provide/<path:path>')
def test_provider(path):
    new_url = 'http://localhost:5000/'+path
    something = redirect(new_url)
    return something
if __name__ == "__main__":
    app.run()
