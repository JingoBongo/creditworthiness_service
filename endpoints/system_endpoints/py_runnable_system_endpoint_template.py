import __init__

from flask import Flask
from flasgger import Swagger
from utils import general_utils as g
from argparse import ArgumentParser

app = Flask(__name__)
swagger = Swagger(app)



@app.route(f"{g.LIFE_PING_ENDPOINT_CONTEXT}", methods=['PATCH'])
def life_ping():
    return '{"status":"alive"}'



@app.route('/')
def hello():
    """Root, please go somewhere else
    ---
    responses:
      200:
        description: why would you go here, go away
    """
    return 'system endpoint'



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