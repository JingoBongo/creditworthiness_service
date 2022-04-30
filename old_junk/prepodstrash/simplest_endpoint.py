from b_logic_placeholder import do_the_thing_function
from flask import Flask
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)


@app.route('/hello_world')
def hello_world():
    """Everyone starts here. So did we.
    ---
    responses:
      200:
        description: start point
    """
    return 'Hello, World!'


@app.route('/')
def hello():
    """Root, please go somewhere else
    ---
    responses:
      200:
        description: why would you go here, go away
    """
    return 'try swagger at least, (apidocs)'


@app.route("/user/<string:job_id>")
def main(job_id):
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
    return do_the_thing_function(job_id)
