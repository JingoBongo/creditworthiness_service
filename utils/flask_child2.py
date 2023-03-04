# from sanic_openapi import swagger_blueprint
from sanic import Sanic, json, file
from sanic.handlers import ErrorHandler
from sanic_openapi import swagger_blueprint

import __init__
from utils import yaml_utils
from utils import constants as c
from utils.decorators.exceptions_catcher_decorator import catch_exceptions


# from sanic import Sanic, json, file
# import logging
# from flasgger import Swagger
#
# from flask import Flask, Response, url_for, send_from_directory
#
# import utils.yaml_utils
# from utils import logger_utils
#
#
#
#
# async def life_ping_handler(request):
#     return await json({"status": "alive"})
#
#
# # def favicon_handler():
# #     return send_from_directory(c.root_path + c.static_folder_name, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
#
# async def favicon(request):
#     return await file(c.root_path + c.static_folder_name + '//favicon.ico')
#
#
#
#
# async def handle_404(request, exception):
#     return await json({
#                     'issue': 'You clearly tried some unexpected context. How about you start with /apidocs? It is unique for every service/port'},
#                 status=404)
#
#
# class FuseNode2:
#
#
#     def __init__(self, *args, template_folder=c.root_path + c.templates_folder_name,
#                  static_folder=c.root_path + c.static_folder_name, **kwargs):
#         try:
#             parser = kwargs.pop("arg_parser")
#             self.app = Sanic(args[0])
#             self.name = args[0]
#             self.app.config.update(static_dir=static_folder, template_dir=template_folder,
#                                debug=utils.yaml_utils.get_debug_flag_from_config())
#
#             # adding 3 default things: life_ping route and 404 error handler, and a favicon
#             self.app.router.add(methods=['PATCH'], uri=c.life_ping_endpoint_context, handler=life_ping_handler)
#             self.app.router.add(methods=c.all_request_method_types, uri='/favicon.ico', handler=favicon)
#             self.app.error_handler.add(404, handle_404)
#
#             parser.add_argument('-port')
#             parser.add_argument('-local')
#             args = parser.parse_args()
#             endpoint_port =args.port if args.port else 5000
#             host = "127.0.0.1" if args.local == 'True' else utils.yaml_utils.get_host_from_config()
#             self.debug = utils.yaml_utils.get_debug_flag_from_config()
#             self.host = host
#             self.port = endpoint_port
#             # self.swagger = Swagger(self)
#             self.app.blueprint(swagger_blueprint)
#             self.get_log()
#             self.logger.info(f"Started FuseNode {self.name} at {host}:{endpoint_port}")
#         except Exception as e:
#             print(f"Something went wrong while launching fuse node")
#             print(e)
#             self.logger.info(f"Something went wrong while launching fuse node")
#             self.logger.info(e)
#
#     def run(self, *args, **kwargs):
#         if 'port' in kwargs.keys():
#             self.port = kwargs['port']
#         # super().run(debug=self.debug, host=self.ctx.host, port=self.ctx.port)
#         self.app.run()
#         # self.app.run(debug=self.debug, host=self.host, port=self.port)
#
#     def get_log(self):
#         name = self.name
#         log = logger_utils.get_log(name)
#         self.logger = log
#         level = logging.DEBUG if self.debug else logging.INFO
#         logging.getLogger('sanic.error').setLevel(level)
#         logging.getLogger('sanic.error').addHandler(c.current_rotating_handler)
#         logging.getLogger('sanic.error').addHandler(c.current_console_handler)
#         # code above fixes werkzeug logs, but also floods the logs
#         return log
async def life_ping_handler(request):
    return await json({"status": "alive"})


async def favicon(request):
    return await file(c.root_path + c.static_folder_name + '//favicon.ico')


async def handle_404(request, exception):
    return await json({
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
    setattr(dest_obj, arg_name, arg_val)

@catch_exceptions()
def check_attribute_exists(dest_obj, attr_name):
    my_var_value = getattr(dest_obj, attr_name, None)
    return my_var_value


class FuseNode2(Sanic):
    def __init__(self, **kwargs):
        super().__init__(kwargs.get('name') or 'fallbackname')
        if parser:= kwargs.pop("arg_parser", None):
            parser.add_argument(f"-local")
            parser.add_argument(f"-port")
            parser.add_argument(f"-debug")
            parser.add_argument(f"-fast")
            attempt_to_set_arg_parser_variable_to_object(parser, 'local', self.ctx)
            attempt_to_set_arg_parser_variable_to_object(parser, 'port', self.ctx)
            attempt_to_set_arg_parser_variable_to_object(parser, 'debug', self.ctx)
            attempt_to_set_arg_parser_variable_to_object(parser, 'fast', self.ctx)

            self.ctx.host = "127.0.0.1" if self.ctx.local == 'True' else yaml_utils.get_host_from_config()

            if check_attribute_exists(self.ctx, 'local'):
                self.ctx.host = "127.0.0.1" if self.ctx.local == 'True' else yaml_utils.get_host_from_config()
            else:
                self.ctx.host = yaml_utils.get_host_from_config()

            if check_attribute_exists(self.ctx, 'debug'):
                self.ctx.debug = bool(self.ctx.debug)
            if check_attribute_exists(self.ctx, 'fast'):
                self.ctx.fast == bool(self.ctx.fast)


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

        # adding 3 default things: life_ping route and 404 error handler, and a favicon
        self.add_route(methods=['PATCH'], uri=c.life_ping_endpoint_context, handler=life_ping_handler)
        self.add_route(methods=c.all_request_method_types, uri='/favicon.ico', handler=favicon)

        # self.router.add(methods=['PATCH'], uri=c.life_ping_endpoint_context, handler=life_ping_handler)
        # self.error_handler.add(404, handle_404)
        # self.error_handler(ErrorHandler(handle_404))

        # what does it even do? TODO: my own error handler
        self.error_handler = CustomErrorHandler()

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
        super().run(debug=self.ctx.debug, host=self.ctx.host, port=self.ctx.port, fast=self.ctx.fast)

def attempt_to_assign_variable_from_kwargs_if_exists(var_name, kwargs, dest_obj):
    arg_val = getattr(kwargs, var_name, None)
    if arg_val:
        setattr(dest_obj, var_name, arg_val)