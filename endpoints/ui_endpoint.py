import __init__
from flask import Flask, render_template, redirect
from flasgger import Swagger
from utils import general_utils as g
from argparse import ArgumentParser

app = Flask(__name__, template_folder=g.root_path + 'templates')
swagger = Swagger(app)




@app.route('/form')
def init_form():
    """We have a form!
    ---
    responses:
      200:
        description: 99% caution
    """
    return render_template('form.html')


@app.route('/')
def hello():
    """Root, please go somewhere else
    ---
    responses:
      200:
        description: why would you go here, go away
    """
    return redirect(f"apidocs", code=200)




@app.errorhandler(404)
def handle_404(e):
    # handle all other routes here
    return 'Not Found, but we HANDLED IT'


@app.route(f"{g.LIFE_PING_ENDPOINT_CONTEXT}", methods=['PATCH'])
def life_ping():
    return '{"status":"alive"}'


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
    app.run(debug=g.debug, host=host, port=endpoint_port)
