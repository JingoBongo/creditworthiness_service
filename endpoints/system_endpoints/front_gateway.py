import requests
from flask import url_for, redirect, make_response, request

import __init__
from utils import general_utils as g, db_utils
from argparse import ArgumentParser
from utils import constants as c
from utils.flask_child import FuseNode
from utils.schedulers_utils import launch_route_harvester_scheduler_if_not_exists, route_harvester_job_body
from utils import logger_utils as log

parser = ArgumentParser()
app = FuseNode(__name__, template_folder=c.root_path + c.templates_folder_name, arg_parser=parser)



@app.route('/trigger-harvester')
def hello():
    """Root, please go somewhere else
    ---
    responses:
      200:
        description: why would you go here, go away
    """
    try:
        route_harvester_job_body()
        return {'msg':'success', 'status':'ok'}
    except Exception as e:
        return {'msg':'exception', 'status':'error', 'exception':e}

# @app.route('/provide/tetris')
# @app.route('/provide/', defaults={'path': ''})
# @app.route('/provide/<path:path>')
@app.route('/provide/<path:path>')
def test_provider(path):
    """Actual resending user's request to service/route; is a lot slower but user is not directly accessing internal services
        ---
    responses:
      200:
           description: 99% caution
        """
    # we have path that is expected from redirected service. therefore we
    # need a way to harvest routes from endpoints.
    # therefore schedulers w/ 5 or 10 minutes interval for it
    # then, if requested path is not in scheduler's list, harvest again
    # then, if requested path is not in scheduler's list, return error in json
    # get port from service with such route
    # table_name', 'column_name', 'column_value', 'column_type'
    try:
        row = db_utils.select_from_table_by_one_column(c.harvested_routes_table_name, 'route', '/'+path, 'String')
        res = g.db_utils.select_from_table(c.sys_services_table_name) + g.db_utils.select_from_table(
        c.business_services_table_name)
        # TODO, move this DB join stuff in harvesting function, here it reduces performance, same for redirect

        if len(row)==0:
            return {'msg': 'no such route. You want to start harvester? (/trigger-harvester)'}
        for roww in res:
            if roww['name'] == row[0]['service_name']:
                res2 = roww['port']
                new_url = f"http://localhost:{res2}/{path}"
                # something = redirect(new_url)
                # something = requests.request(request, url=new_url)
                esreq = requests.Request(method=request.method, url=new_url,
                                         headers=request.headers, data=request.data)
                resp = requests.Session().send(esreq.prepare())
                return (resp.text, resp.status_code, resp.headers.items())

                # return something
        return {'msg': 'no such route. You want to start harvester? (/trigger-harvester)'}
    except Exception as e:
        log.exception(e)
        return {'msg':'error', 'exception':e}

@app.route('/redir/<path:path>')
def redir_request(path):
    """Redirect to service/route; is a bit slower and leads to directly accessing internal services
        ---
    responses:
      200:
           description: 99% caution
        """
    # we have path that is expected from redirected service. therefore we
    # need a way to harvest routes from endpoints.
    # therefore schedulers w/ 5 or 10 minutes interval for it
    # then, if requested path is not in scheduler's list, harvest again
    # then, if requested path is not in scheduler's list, return error in json
    # get port from service with such route
    # table_name', 'column_name', 'column_value', 'column_type'
    try:
        row = db_utils.select_from_table_by_one_column(c.harvested_routes_table_name, 'route', '/'+path, 'String')
        res = g.db_utils.select_from_table(c.sys_services_table_name) + g.db_utils.select_from_table(
        c.business_services_table_name)

        if len(row)==0:
            return {'msg': 'no such route. You want to start harvester? (/trigger-harvester)'}
        for roww in res:
            if roww['name'] == row[0]['service_name']:
                res2 = roww['port']
                new_url = f"http://localhost:{res2}/{path}"
                something = redirect(new_url)
                return something
        return {'msg': 'no such route. You want to start harvester? (/trigger-harvester)'}
    except Exception as e:
        log.exception(e)
        return {'msg':'error', 'exception':e}



if __name__ == "__main__":
    launch_route_harvester_scheduler_if_not_exists()
    app.run()
