from flask import Flask, render_template, redirect
from flasgger import Swagger
from utils import general_utils as g
from argparse import ArgumentParser

app = Flask(__name__, template_folder=g.root_path + 'templates')
swagger = Swagger(app)


@app.route('/snake')
def hello_world():
    """When pockets are empty.. at least you can play snakes
    ---
    responses:
      200:
        description: 99% caution
    """
    return render_template('snakes.html')


@app.route('/')
def hello():
    """Root, please go somewhere else
    ---
    responses:
      200:
        description: why would you go here, go away
    """
    return redirect(f"apidocs", code=200)


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
    return 'Not Found, but we HANDLED IT'


@app.route(f"{g.LIFE_PING_ENDPOINT_CONTEXT}", methods=['PATCH'])
def life_ping():
    return '{"status":"alive"}'


# experimental part
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-port')
    parser.add_argument('-local')
    args = parser.parse_args()
    endpoint_port = args.port
    if args.local == "True":
        host = "127.0.0.1"
    else:
        host = g.host
    # endpoint_port = int(os.environ.get('PORT', endpoint_port))
    app.run(debug=g.debug, host=host, port=endpoint_port)
