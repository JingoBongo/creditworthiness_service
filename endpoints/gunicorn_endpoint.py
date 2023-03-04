"""MODULE_METADATA_START
MDL_STANDALONE: True
MDL_MODULE_NAME: gunicorn copycat
MDL_MONO: True
MDL_LOCAL: False
MDL_ROLE: BUSINESS
MDL_AUTHOR: mpakaboy@gmail.com
MDL_REPOSITORY: AUTHOR/REPO_NAME
MDL_VERSION: 1
MDL_LAST_VERSION_DATE: 1/1/1111
MDL_DESCRIPTION: GENERAL DATA ABOUT PACKAGE, POSSIBLY REQUIRED
ARBITRARY SOFT
"""
from argparse import ArgumentParser

from sanic_openapi import swagger_blueprint
from sanic_openapi.openapi2 import doc

import __init__
from sanic import Sanic, json
from sanic.response import text

from utils import constants
from utils.flask_child2 import FuseNode2
from sanic_jinja2 import SanicJinja2

parser = ArgumentParser()
app = FuseNode2(arg_parser=parser)
jinja = SanicJinja2(app, pkg_name="main")


@doc.summary("Get a greeting")
@doc.produces({'message': str})
@doc.consumes({'name': str}, location="path", required=True)
@app.route('/hello/<name>')
async def hello(request, name):
    return json({'message': f'Hello, {name}!'})



@app.route('/html')
async def htmlhtml(request):
    return jinja.render("TODO_page.html", request)



if __name__ == "__main__":
    app.run()