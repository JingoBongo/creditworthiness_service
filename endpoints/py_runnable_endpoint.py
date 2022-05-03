from flask import Flask
from flasgger import Swagger
from utils import general_utils as g
import os
from argparse import ArgumentParser

app = Flask(__name__)
swagger = Swagger(app)


@app.route('/end2')
def hello_world():
    """Everyone starts here. So did we.
    ---
    responses:
      200:
        description: start point
    """
    return 'end2!'


# experimental part
if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-port')
    parser.add_argument('-local')
    args = parser.parse_args()
    endpoint_port = args.port

    # endpoint_port = int(os.environ.get('PORT', endpoint_port))
    app.run(debug=g.debug, host='0.0.0.0', port=endpoint_port)