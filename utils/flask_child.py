import __init__

import logging
from flasgger import Swagger

from flask import Flask, Response, url_for, send_from_directory

import utils.yaml_utils
from utils import logger_utils
from utils import constants as c


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

def favicon_handler():
    return send_from_directory(c.root_path + c.static_folder_name,'favicon.ico', mimetype='image/vnd.microsoft.icon')


def not_found_handler(e):
    return '{"kak_to_throw_like_a_monke": "This is not a thing. But you can see what is available at /apidocs"}'


class FuseNode(Flask):
    def __init__(self, *args, template_folder=c.root_path + c.templates_folder_name, static_folder=c.root_path + c.static_folder_name, **kwargs):
        try:
            parser = kwargs.pop("arg_parser")
            super().__init__(*args, template_folder=template_folder, static_folder=static_folder, **kwargs)
            # adding 3 default things: life_ping route and 404 error handler, and a favicon
            self.add_url_rule(c.life_ping_endpoint_context, methods=['PATCH'], view_func=life_ping_handler)
            self.add_url_rule('/favicon.ico', view_func=favicon_handler)
            self.register_error_handler(404, not_found_handler)
            parser.add_argument('-port')
            parser.add_argument('-local')
            args = parser.parse_args()
            endpoint_port = args.port
            host = "127.0.0.1" if args.local == 'True' else utils.yaml_utils.get_host_from_config()
            self.debug = utils.yaml_utils.get_debug_flag_from_config()
            self.host = host
            self.port = endpoint_port
            self.swagger = Swagger(self)
            self.get_log()
            self.logger.info(f"Started FuseNode {self.name} at {host}:{endpoint_port}")
        except Exception as e:
            print(f"Something went wrong while launching fuse node")
            print(e)
            self.logger.info(f"Something went wrong while launching fuse node")
            self.logger.info(e)

    def run(self, *args, **kwargs):
        if 'port' in kwargs.keys():
            self.port = kwargs['port']
        super().run(*args, debug=self.debug, host=self.host, port=self.port, **kwargs)

    def get_log(self):
        name = self.name
        log = logger_utils.get_log(name)
        self.logger = log
        level = logging.DEBUG if self.debug else logging.INFO
        logging.getLogger('werkzeug').setLevel(level)
        logging.getLogger('werkzeug').addHandler(c.current_rotating_handler)
        logging.getLogger('werkzeug').addHandler(c.current_console_handler)
        # code above fixes werkzeug logs, but also floods the logs
        return log
