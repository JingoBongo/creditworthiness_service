import __init__
import subprocess


import socket

import time
import os
import requests
from flask import redirect, request, abort, render_template, Response

from utils import general_utils as g, os_utils
from argparse import ArgumentParser
from utils import constants as c
from utils.flask_child import FuseNode
from utils.root_finder_utils import find_valid_route
from utils.schedulers_utils import launch_route_harvester_scheduler_if_not_exists, route_harvester_job_body
from utils import logger_utils as log
from flask_sse import sse

parser = ArgumentParser()
app = FuseNode(__name__, arg_parser=parser)
app.register_blueprint(sse, url_prefix='/stream')

@app.route('/home')
@app.route('/home/<current>')
def manage(current=None):
    if current == 'services':
        template = 'services.html'
        title = 'Services'
    elif current == 'logs2':
        template = 'logs2.html'
        title = 'Logs 2'
    elif current == 'logs':
        log_files = os.listdir(c.logs_folder_full_path)
        return render_template('logs_main.html', log_files=log_files)
    elif current is None:
        template = 'gate_index.html'
        title = 'Fuse Management Hub'
    else:
        abort(404)

    return render_template(template, title=title, current=current)

@app.route('/stream-output')
def stream_output():
    # Run the journalctl command and stream the output to the client
    def generate_output():
        if os_utils.is_linux_running():
            cmd = ['journalctl', '-f', '-u', 'service_name']
            popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
            for stdout_line in iter(popen.stdout.readline, ""):
                yield 'data: {}\n\n'.format(stdout_line.decode('utf-8').rstrip())
            popen.stdout.close()
            return_code = popen.wait()
            if return_code:
                raise subprocess.CalledProcessError(return_code, cmd)


            # proc = subprocess.Popen(['journalctl', '-f', '-u', 'service_name'], stdout=subprocess.PIPE)
            # while True:
            #     line = proc.stdout.readline()
            #     if not line:
            #         break
            #     app.logger.info(f"Cmd output: {line}")
            #     yield 'data: {}\n\n'.format(line.decode('utf-8').rstrip())
        else:
            while True:
                time.sleep(1)
                app.logger.info('not a linux device')
                yield 'not a linux device' + '\n'

    return app.response_class(generate_output(), mimetype='text/plain')



@app.route('/logs')
def view_log_file():
    filename = request.args['filename']
    return render_template('log.html', filename=filename)


@app.route('/logs/<filename>/stream')
def stream_log_file(filename):
    def generate():
        last_pos = 0
        while True:
            with open(os.path.join(c.logs_folder_full_path, filename), 'r') as f:
                # Seek to the last position in the file that was read
                f.seek(last_pos)
                # Yield any new lines that have been added to the log file
                for line in f:
                    yield line
                last_pos = f.tell()
            time.sleep(2)

    return app.response_class(generate(), mimetype='text/plain')


@app.route('/todo_page')
def todo_page():
    return render_template('TODO_page.html')


# @admin.route('/manage') check out these later
# @admin.route('/manage/<current>')
# @login_required
@app.route('/run-cmd-command/<string:command>')
def cursed_call(command):
    """This... exists. I refuse to uncomment the code line until I think about security
        ---
        responses:
          200:
            description: why would you go here, go away
        """
    # g.run_cmd_command(command)
    return {"status": "done;;; I refuse to uncomment the code line until I think about security"}


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
        return {'msg': 'success', 'status': 'ok'}
    except Exception as e:
        return {'msg': 'exception', 'status': 'error', 'exception': e}


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
        rows1 = g.db.select_from_table_by_one_column(c.sys_services_table_name, 'name', result[0]['service_name'],
                                                     'String')
        rows2 = g.db.select_from_table_by_one_column(c.business_services_table_name, 'name', result[0]['service_name'],
                                                     'String')
        rows = rows2 + rows1
        for row in rows:
            #     TODO. here could be your load balancing logic or multi service handling, but here is a TODO :)
            #     TODO this includes selects from db as well
            port = row['port']
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            new_url = f"http://{ip_address}:{port}/{path}"
            esreq = requests.Request(method=request.method, url=new_url, headers=request.headers, data=request.data)
            resp = requests.Session().send(esreq.prepare())
            return (resp.text, resp.status_code, resp.headers.items())

        # return below should be unreachable in theory, but... still
        return {'msg': 'no such route. You want to start harvester? (/trigger-harvester)'}
    except Exception as e:
        app.logger.exception(e)
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


@app.route('/redir/<path:path>', methods=['GET', 'POST'])
def redir_request(path):
    """Redirect to service/route; is a bit slower and leads to directly accessing internal services
        ---
    responses:
      200:
           description: 99% caution
        """
    try:
        result = find_valid_route(path)
        if len(result) <= 0:
            return {'msg': 'no such route. You want to start harvester? (/trigger-harvester)'}
        if len(result) > 1:
            return {'msg': 'there are multiple matching routes, either try to avoid this during development'
                           ' or try to pick route by service_name or function_name from result list.',
                    'status': 'ambiguous result',
                    'possible resolution': 'remove duplicates and re-run harvester OR pick specific result from the list'}
        # pick service port by service name from result from db and go by path
        rows1 = g.db.select_from_table_by_one_column(c.sys_services_table_name, 'name', result[0]['service_name'],
                                                     'String')
        rows2 = g.db.select_from_table_by_one_column(c.business_services_table_name, 'name', result[0]['service_name'],
                                                     'String')
        rows = rows2 + rows1
        for row in rows:
            #     TODO. here could be your load balancing logic or multi service handling, but here is a TODO :)
            #     TODO this includes selects from db as well
            port = row['port']
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            new_url = f"http://{ip_address}:{port}/{path}"
            if request.method == 'POST':
                return redirect(new_url, code=307)

            return redirect(new_url)
        # return below should be unreachable in theory, but... still
        return {'msg': 'no such route. You want to start harvester? (/trigger-harvester)'}
    except Exception as e:
        app.logger.exception(e)
        return {'msg': 'error', 'exception': e}


if __name__ == "__main__":
    launch_route_harvester_scheduler_if_not_exists()
    app.run()
