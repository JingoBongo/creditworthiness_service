import logging
import os

from flasgger import Swagger
from flask.logging import default_handler

import __init__
from flask import Flask, app, Response
from utils import constants as c
from utils import general_utils as g
from utils import logger_utils
from utils import constants as c
from utils import config_utils


class EndpointAction(object):

    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        self.action()
        return self.response


def remove_key(d, key):
    r = dict(d)
    del r[key]
    return r


def life_ping_handler():
    return '{"status":"alive"}'


def not_found_handler(e):
    return '{"kak_kakati": "This is not a thing. But you can see what is available at /apidocs"}'


class FuseNode(Flask):
    def __init__(self, *args, **kwargs):
        try:
            parser = kwargs.pop("arg_parser")
            super().__init__(*args, **kwargs)
            # adding 2 default thigs: life_ping route and 404 error handler
            self.add_url_rule(c.life_ping_endpoint_context, methods=['PATCH'], view_func=life_ping_handler)
            self.register_error_handler(404, not_found_handler)
            parser.add_argument('-port')
            parser.add_argument('-local')
            args = parser.parse_args()
            endpoint_port = args.port
            host = "127.0.0.1" if args.local == 'True' else config_utils.getHostFromConfig()
            self.debug = config_utils.getDebugFlagFromConfig()
            self.host = host
            self.port = endpoint_port
            self.swagger = Swagger(self)
            self.get_log()
            self.logger.info(f"Started FuseNode {self.name} at {host}:{endpoint_port}")
            # app.run(debug=g.debug, host=host, port=endpoint_port)
        except Exception as e:
            print(f"Something went wrong while launching fuse node")
            print(e)
            self.logger.info(f"Something went wrong while launching fuse node")
            self.logger.info(e)

    def run(self, *args, **kwargs):
        if 'port' in kwargs.keys():
            self.port = kwargs['port']
        super().run(debug=self.debug, host=self.host, port=self.port)

    def get_log(self):
        name = self.name
        log = logger_utils.get_log(name)

        # // test part
        # TODO: this worked to collect request logs, but not perfectly. probably needs refactoring
        w_log = logging.getLogger('werkzeug')
        # TODO: why is level = DEBUG here? investigate. we have level from configs now
        w_log.setLevel(logging.DEBUG)
        w_log.addHandler(c.current_rotating_handler)

        # w_log.addHandler(c.current_console_handler)
        self.logger = log
        return log
