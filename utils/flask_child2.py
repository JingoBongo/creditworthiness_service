import logging

import __init__
from sanic import Sanic, json, file
from sanic_openapi import swagger_blueprint

from utils import yaml_utils, logger_utils
from utils import constants as c
from utils.decorators.exceptions_catcher_decorator import catch_exceptions
from utils import logger_utils as log


async def life_ping_handler(request):
    return json({"status": "alive"})


async def favicon(request):
    return file(c.root_path + c.static_folder_name + '//favicon.ico')


async def handle_404(request, exception):
    return json({
        'issue': 'You clearly tried some unexpected context. How about you start with /apidocs? It is unique for every service/port'},
        status=404)


from sanic.handlers import ErrorHandler


class CustomErrorHandler(ErrorHandler):
    def default(self, request, exception):
        ''' handles errors that have no error handlers assigned '''
        # You custom error handling logic...
        return super().default(request, exception)


@catch_exceptions()
def attempt_to_set_arg_parser_variable_to_object(parser, arg_name, dest_obj):
    arg_val = getattr(parser.parse_args(), arg_name)
    # setattr(dest_obj, arg_name, arg_val)
    dest_obj[arg_name] = arg_val


@catch_exceptions()
def check_attribute_exists(dest_obj, attr_name):
    my_var_value = getattr(dest_obj, attr_name, None)
    return my_var_value


class FuseNode2(Sanic):
    def __init__(self, **kwargs):
        nme = None
        dict_basket = {}
        # if temp_arg_prs:= kwargs.get("arg_parser", None):
        #     temp_arg_prs.add_argument("-name")
        #     argggs = temp_arg_prs.parse_args()
        #     nme = argggs.get("-name", None)

        if parser := kwargs.pop("arg_parser", None):
            parser.add_argument(f"-local")
            parser.add_argument(f"-port")
            parser.add_argument(f"-debug")
            parser.add_argument(f"-fast")
            parser.add_argument(f"-name")

            attempt_to_set_arg_parser_variable_to_object(parser, 'local', dict_basket)
            attempt_to_set_arg_parser_variable_to_object(parser, 'port', dict_basket)
            attempt_to_set_arg_parser_variable_to_object(parser, 'debug', dict_basket)
            attempt_to_set_arg_parser_variable_to_object(parser, 'fast', dict_basket)
            attempt_to_set_arg_parser_variable_to_object(parser, 'name', dict_basket)


            # if check_attribute_exists(dict_basket, 'local'):
            if dict_basket.get('local', None):
                dict_basket['host'] = "127.0.0.1" if dict_basket['local'] == 'True' else yaml_utils.get_host_from_config()
            else:
                dict_basket['host'] = yaml_utils.get_host_from_config()
            dict_basket['host'] = "127.0.0.1" if dict_basket['local'] == 'True' else yaml_utils.get_host_from_config()

            # if check_attribute_exists(dict_basket, 'debug'):
            if dict_basket.get('debug', None):
                dict_basket['debug'] = bool(dict_basket['debug'])
            # if check_attribute_exists(dict_basket, 'fast'):
            if dict_basket.get('fast', None):
                dict_basket['fast'] == bool(dict_basket['fast'])
            if nmme:= dict_basket.get('name', None):
                nme = nmme

        super().__init__(nme or kwargs.get('name') or 'fallbackname')
        # self.static()
        for key,value in dict_basket.items():
            setattr(self.ctx, key, value)
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True
        })

        if not check_attribute_exists(self.ctx, 'port'):
            self.ctx.port = kwargs.get('port') or 5000
        if not check_attribute_exists(self.ctx, 'fast'):
            self.ctx.fast = False
        if not check_attribute_exists(self.ctx, 'host'):
            self.ctx.host = "127.0.0.1" if kwargs.get('local') == 'True' else yaml_utils.get_host_from_config()
        if not check_attribute_exists(self.ctx, 'debug'):
            self.ctx.debug = yaml_utils.get_debug_flag_from_config()
        if kwargs.get('swagger', False):
            self.blueprint(swagger_blueprint)
        self.ctx.port = int(self.ctx.port)

        # i want logger
        self.get_log()
        log.info(f"Started FuseNode {self.name} at {self.ctx.host}:{self.ctx.port}")
        # and default static and template folders

        # adding 3 default things: life_ping route and 404 error handler, and a favicon
        self.add_route(methods=['PATCH'], uri=c.life_ping_endpoint_context, handler=life_ping_handler)
        self.add_route(methods=c.all_request_method_types, uri='/favicon.ico', handler=favicon)

        # what does it even do? TODO: my own error handler
        self.error_handler = CustomErrorHandler()

    def get_log(self):
        name = self.name
        log = logger_utils.get_log(name)
        self.ctx.logger = log
        level = logging.DEBUG if self.ctx.debug else logging.INFO
        logging.getLogger('sanic.root').setLevel(level)
        logging.getLogger('sanic.root').addHandler(c.current_rotating_handler)
        logging.getLogger('sanic.root').addHandler(c.current_console_handler)
        logging.getLogger('sanic.error').setLevel(level)
        logging.getLogger('sanic.error').addHandler(c.current_rotating_handler)
        logging.getLogger('sanic.error').addHandler(c.current_console_handler)
        logging.getLogger('sanic.access').setLevel(level)
        logging.getLogger('sanic.access').addHandler(c.current_rotating_handler)
        logging.getLogger('sanic.access').addHandler(c.current_console_handler)
        return log


    def run(self, *args, **kwargs):
        if prt := kwargs.get('port', None):
            self.ctx.port = int(prt)
        if hst := kwargs.get('host', None):
            self.ctx.host = str(hst)
        if dbg := kwargs.get('debug', None):
            self.ctx.port = bool(dbg)
        if fst := kwargs.get('fast', None):
            self.ctx.fast = bool(fst)
        # Note to why i dont use it: i also need to cast variable type, but for later, maybe I will find a way
        # attempt_to_assign_variable_from_kwargs_if_exists('port', kwargs, self.ctx)
        # attempt_to_assign_variable_from_kwargs_if_exists('host', kwargs, self.ctx)
        # attempt_to_assign_variable_from_kwargs_if_exists('debug', kwargs, self.ctx)

        # TODO further (and upper 3 lines) needs further clarification.
        # for upper: there is probably a good way to do it without many ifs
        # for lower: access_log in async (high load) together with debug false (check) remove connection logs
        # but greatly improve performance. I suggest keeping the logs at least in mono workers, but for now it
        # only exists while debug
        super().run(debug=self.ctx.debug, host=self.ctx.host, port=self.ctx.port, fast=self.ctx.fast,
                    access_log=self.ctx.debug)


def attempt_to_assign_variable_from_kwargs_if_exists(var_name, kwargs, dest_obj):
    arg_val = getattr(kwargs, var_name, None)
    if arg_val:
        setattr(dest_obj, var_name, arg_val)
