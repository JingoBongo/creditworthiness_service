from flask import Flask
from flasgger import Swagger
from utils import general_utils as g
import os
from argparse import ArgumentParser

app = Flask(__name__)
swagger = Swagger(app)




@app.route('/')
def hello():
    """Root, please go somewhere else
    ---
    responses:
      200:
        description: why would you go here, go away
    """
    return 'system endpoint'


# experimental part
if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-port')
    parser.add_argument('-local')
    args = parser.parse_args()
    endpoint_port = args.port
    if bool(args.local):
        host = "127.0.0.1"
    else:
        host = g.host
    # endpoint_port = int(os.environ.get('PORT', endpoint_port))
    app.run(debug=g.debug, host=host, port=endpoint_port)