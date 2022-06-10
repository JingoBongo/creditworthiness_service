from flasgger import Swagger

import __init__
from flask import Flask, app, Response
from utils import constants as c
from utils import general_utils as g


class EndpointAction(object):

    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        self.action()
        return self.response

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

class FuseNode(Flask):
    # app = None

    def __init__(self, *args, **kwargs):
        parser = kwargs['arg_parser']
        kwargs = removekey(kwargs, 'arg_parser')
        super().__init__(*args, **kwargs)
        # self = Flask(*args, **kwrds)
        self.add_url_rule('/life_ping', methods=['PATCH'], view_func=self.life_ping_handler)
        parser.add_argument('-port')
        parser.add_argument('-local')
        args = parser.parse_args()
        endpoint_port = args.port
        if args.local == "True":
            host = "127.0.0.1"
        else:
            host = g.host
        self.debug = g.debug
        self.host = host
        self.port = endpoint_port
        self.swagger = Swagger(self)
        # app.run(debug=g.debug, host=host, port=endpoint_port)

    def run(self, *args, **kwargs):
        super().run(debug=self.debug, host=self.host, port=self.port)


    def life_ping_handler(self):
        return '{"status":"alive"}'
