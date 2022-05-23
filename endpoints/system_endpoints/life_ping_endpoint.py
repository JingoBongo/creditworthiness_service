from flask import Flask
from flasgger import Swagger
from utils import general_utils as g
from argparse import ArgumentParser

app = Flask(__name__)
swagger = Swagger(app)


@app.route(f"{g.LIFE_PING_ENDPOINT_CONTEXT}", methods=['PATCH'])
def life_ping():
    return '{"status":"alive"}'



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-port')
    parser.add_argument('-local')
    args = parser.parse_args()
    endpoint_port = args.port
    if args.local == "True":
        host = "127.0.0.1"
    else:
        host = g.host

    process_name = "life_ping_schedule"
    process_full_path = f"{g.root_path}\\utils\\life_ping_schedule.py"
    local_process = g.custom_subprocess.CustomNamedProcess([g.sys.executable,
                                                            process_full_path],
                                                           name=process_name)
    g.launched_subprocesses.append(
        g.custom_subprocess.CustomProcessListElement(process_full_path,
                                                     999999999,
                                                     process_name,
                                                     local_process.pid,
                                                     local_process))

    app.run(debug=g.debug, host=host, port=endpoint_port)
