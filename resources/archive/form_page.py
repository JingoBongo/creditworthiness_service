# import __init__
# import json
# import os
# import requests
# from fuse import print_c
# from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify
# from flasgger import Swagger
# from utils import general_utils as g
# from argparse import ArgumentParser
# import re
# # from ml_model_endpoint import ml_endpoint
#
# # IMPORTANT NOTE. I REFUSE TO FIX THIS FILE UNTILL I REFACTOR IT COMPLETELY AND MAKE IT WORK
#
# app = Flask(__name__, template_folder=g.root_path + 'templates')
# app.secret_key = "631113d3-5487-450f-a43d-8b90db71c20d"
# swagger = Swagger(app)
#
# # app.register_blueprint(ml_endpoint)
#
# root_path = g.root_path
# config = g.config
#
# SYS_SERVICES_TABLE_NAME = g.SYS_SERVICES_TABLE_NAME
# BUSINESS_SERVICES_TABLE_NAME = g.BUSINESS_SERVICES_TABLE_NAME
#
# data_hash_path = os.path.normpath("resources//user_data.json")
#
#
# @app.route('/send_n')
# def send_n():
#     return 'aboba'
#
#
# @app.route('/index')
# def index():
#     return render_template('form.html')
#
# @app.route("/form" , methods=['GET', 'POST'])
# def form():
#   gender             = request.form.get('genderOptions')
#   married            = request.form.get('marriedOptions')
#   dependents         = request.form.get('dependents')
#   education_degree   = request.form.get('educationDegree')
#   self_employed      = request.form.get('selfEmployedOptions')
#   applicant_income   = int(request.form.get('applicantIncome'))
#   coapplicant_income = int(request.form.get('coapplicantIncome'))
#   loan_amount        = int(request.form.get('loanAmount'))
#   loan_amount_term   = int(request.form.get('loanAmountTerm'))
#   credit_history     = int(request.form.get('creditHistory'))
#   property_area_type = request.form.get('propertyAreaType')
#
#
#   user_data = {
#     "Gender":            [gender],
#     "Married":           [married],
#     "Dependents":        [dependents],
#     "Education":         [education_degree],
#     "ApplicantIncome":   [applicant_income],
#     "CoapplicantIncome": [coapplicant_income],
#     "LoanAmount":        [loan_amount],
#     "Loan_Amount_Term":  [loan_amount_term],
#     "Credit_History":    [credit_history],
#     "Property_Area":     [property_area_type]
#   }
#
#   with open(data_hash_path, 'w') as j:
#     json.dump(user_data, j, indent=2)
#     print_c("New json file is created from the form data")
#
#   headers = {"Content-Type": "application/json; charset=utf-8"}
#   services = db_utils.select_from_table(
#         BUSINESS_SERVICES_TABLE_NAME)
#   port = ""
#
#   for i in services:
#     service = {"name": i['name'], "port": i['port']}
#     print(service)
#     if "model_endpoint" in service["name"]:
#       port = service["port"]
#       print(port)
#
#   response = requests.post(f"http://localhost:{port}/processPerson", headers=headers, json=user_data)
#
#   print('response from server:',response.status_code)
#   print('RESPONSE DATA:',response.json)
#   return redirect(f"http://localhost:{port}/processPerson")
#
# @app.route('/snake')
# def snake():
#     """When pockets are empty.. at least you can play snakes
#     ---
#     responses:
#       200:
#         description: 99% caution
#     """
#     return render_template('snakes.html')
#
#
# @app.route('/tetris')
# def tetris():
#     """This is becoming a common joke.. I like it
#     ---
#     responses:
#       200:
#         description: 99% caution
#     """
#     return render_template('tetris.html')
#
# @app.route('/')
# def hello():
#     """Root, please go somewhere else
#     ---
#     responses:
#       200:
#         description: why would you go here, go away
#     """
#     return redirect(url_for('index'), code=200)
#
#
# @app.route("/user/<string:str_variable>")
# def endpoint_with_var(str_variable):
#     """I have no idea why is this a title
#         These are just notes as an example. We don't need most of this
#         functionality, plus we aren't paid for this. So let's keep it
#         simple as in hello_world endpoit, ey?
#         ---
#         parameters:
#           - arg1: whatever, dude, this goes into business logic for now
#             type: string
#             required: true
#             default: none, actually
#         definitions:
#           Job_id:
#             type: String
#         responses:
#           200:
#             description: A simple business logic unit with swagger
#         """
#     return 'elo hello fello\', %s' % str_variable
#
#
# @app.errorhandler(404)
# def handle_404(e):
#     # handle all other routes here
#     return 'Not Found, but we HANDLED IT'
#
#
# @app.route(f"{g.LIFE_PING_ENDPOINT_CONTEXT}", methods=['PATCH'])
# def life_ping():
#     return '{"status":"alive"}'
#
# if __name__ == "__main__":
#     parser = ArgumentParser()
#     parser.add_argument('-port')
#     parser.add_argument('-local')
#     args = parser.parse_args()
#     endpoint_port = args.port
#     if args.local == "True":
#         host = "127.0.0.1"
#     else:
#         host = g.host
#     app.run(debug=g.debug, host=host, port=endpoint_port)
