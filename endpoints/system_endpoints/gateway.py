import __init__
import requests
from flask import url_for, redirect, make_response, request

from utils import general_utils as g
from argparse import ArgumentParser
from utils import constants as c
from utils.flask_child import FuseNode
from utils.root_finder_utils import find_valid_route
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


@app.route('/provide/<path:path>')
def test_provider(path):
    """Actual resending user's request to service/route; is a lot slower but user is not directly accessing internal services
        ---
    responses:
      200:
           description: 99% caution
        """
    try:
        result = find_valid_route(path)
        if len(result) < 0:
            return {'msg': 'no such route. You want to start harvester? (/trigger-harvester)'}
        if len(result) > 1:
            return {'msg': 'there are multiple matching routes, either try to avoid this during development'
                           'or try to pick route by service_name or function_name from result list.',
                    'status': 'ambiguous result',
                    'possible resolution': 'remove duplicates and re-run harvester OR pick specific result from the list'}
        # pick service port by service name from result from db and go by path
        rows1 = g.db.select_from_table_by_one_column(c.sys_services_table_name, 'name', result[0]['service_name'], 'String')
        rows2 = g.db.select_from_table_by_one_column(c.business_services_table_name, 'name', result[0]['service_name'], 'String')
        rows = rows2 + rows1
        for row in rows:
            #     TODO. here could be your load balancing logic or multi service handling, but here is a TODO :)
            #     TODO this includes selects from db as well
            port = row['port']
            new_url = f"http://localhost:{port}/{path}"
            esreq = requests.Request(method=request.method, url=new_url, headers=request.headers, data=request.data)
            resp = requests.Session().send(esreq.prepare())
            return (resp.text, resp.status_code, resp.headers.items())

        # return below should be unreachable in theory, but... still
        return {'msg': 'no such route. You want to start harvester? (/trigger-harvester)'}
    except Exception as e:
        log.exception(e)
        return {'msg': 'error', 'exception': e}


@app.route('/find/<path:path>')
def find_possible_routes(path):
    """Find similar routes from db, returns list of all matching routes. Should be used as
        first step of getting right route. It is still needed to compare result len in case of duplicates or 0 result
        ---
    responses:
      200:
           description: 99% caution
        """
    return str(find_valid_route(path))

@app.route('/redir/<path:path>')
def redir_request(path):
    """Redirect to service/route; is a bit slower and leads to directly accessing internal services
        ---
    responses:
      200:
           description: 99% caution
        """
    try:
        result = find_valid_route(path)
        if len(result)<=0:
            return {'msg': 'no such route. You want to start harvester? (/trigger-harvester)'}
        if len(result)>1:
            return {'msg': 'there are multiple matching routes, either try to avoid this during development'
                           'or try to pick route by service_name or function_name from result list.',
                            'status':'ambiguous result',
                            'possible resolution':'remove duplicates and re-run harvester OR pick specific result from the list'}
        # pick service port by service name from result from db and go by path
        rows1 = g.db.select_from_table_by_one_column(c.sys_services_table_name, 'name', result[0]['service_name'], 'String')
        rows2 = g.db.select_from_table_by_one_column(c.business_services_table_name, 'name', result[0]['service_name'], 'String')
        rows = rows2 + rows1
        for row in rows:
        #     TODO. here could be your load balancing logic or multi service handling, but here is a TODO :)
        #     TODO this includes selects from db as well
            port = row['port']
            new_url = f"http://localhost:{port}/{path}"
            something = redirect(new_url)
            return something
        # return below should be unreachable in theory, but... still
        return {'msg': 'no such route. You want to start harvester? (/trigger-harvester)'}
    except Exception as e:
        log.exception(e)
        return {'msg':'error', 'exception':e}



if __name__ == "__main__":
    launch_route_harvester_scheduler_if_not_exists()
    app.run()
