import __init__
from flask import render_template, redirect, url_for
from flasgger import Swagger
from utils import general_utils as g
from utils import constants as c
from argparse import ArgumentParser

from utils.flask_child import FuseNode
parser = ArgumentParser()
app = FuseNode(__name__, template_folder=c.root_path + c.templates_folder_name, arg_parser=parser)



@app.route('/send_n')
def send_n():
    return 'aboba'

@app.route('/index')
def index():
    return 'Did you expect a default page or something?))'



@app.route('/snake')
def snake():
    """When pockets are empty.. at least you can play snakes
    ---
    responses:
      200:
        description: 99% caution
    """
    return render_template('snakes.html')


@app.route('/tetris')
def tetris():
    """This is becoming a common joke.. I like it
    ---
    responses:
      200:
        description: 99% caution
    """
    return render_template('tetris.html')

@app.route('/')
def hello():
    """Root, please go somewhere else
    ---
    responses:
      200:
        description: why would you go here, go away
    """
    return redirect(url_for('index'), code=200)


@app.route("/user/<string:str_variable>")
def endpoint_with_var(str_variable):
    """I have no idea why is this a title
        These are just notes as an example. We don't need most of this
        functionality, plus we aren't paid for this. So let's keep it
        simple as in hello_world endpoit, ey?
        ---
        parameters:
          - arg1: whatever, dude, this goes into business logic for now
            type: string
            required: true
            default: none, actually
        definitions:
          Job_id:
            type: String
        responses:
          200:
            description: A simple business logic unit with swagger
        """
    return 'elo hello fello\', %s' % str_variable


@app.errorhandler(404)
def handle_404(e):
    # handle all other routes here
    return 'This is not a thing. But you can see what is available at /apidocs'



if __name__ == "__main__":
    app.run()