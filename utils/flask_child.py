import os

from flasgger import Swagger

import __init__
from flask import Flask, app, Response
from utils import constants as c
from utils import general_utils as g
from utils import logger_utils
from utils import constants as c


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

def life_ping_handler():
    return '{"status":"alive"}'


def not_found_handler(e):
    return 'This is not a thing. But you can see what is available at /apidocs'

class FuseNode(Flask):
    def __init__(self, *args, **kwargs):
        parser = kwargs['arg_parser']
        kwargs = removekey(kwargs, 'arg_parser')
        super().__init__(*args, **kwargs)
        # adding 2 default thigs: life_ping route and 404 error handler
        self.add_url_rule(c.life_ping_endpoint_context, methods=['PATCH'], view_func=life_ping_handler)
        self.register_error_handler(404, not_found_handler)
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
        self.log = self.get_log()
        # app.run(debug=g.debug, host=host, port=endpoint_port)

    def run(self, *args, **kwargs):
        super().run(debug=self.debug, host=self.host, port=self.port)

    def get_log(self):
        name = self.name
        pid = os.getpid()
        logger_name = f"{name}-{pid}"
        log_path = f"{c.root_path}resources//{c.logs_folder_name}//{logger_name}"
        log = logger_utils.setup_logger(logger_name, log_path)
        c.current_subprocess_logger = log
        return log


