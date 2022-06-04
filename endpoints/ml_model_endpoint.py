import __init__
from flask import Flask, render_template, redirect, request
from flasgger import Swagger
from utils import general_utils as g
from argparse import ArgumentParser

import pandas as pd
import numpy as np
import pickle
# import scikit-learn==1.0.2

app = Flask(__name__, template_folder=g.root_path + 'templates')
swagger = Swagger(app)

scaler = pickle.load(open("resources/pickles/standard_scaler.pkl", 'rb'))
one_hot_encoder = pickle.load(open("resources/pickles/one_hot_encoder.pkl", 'rb'))
model = pickle.load(open("resources/pickles/bag_log_clf.pkl", 'rb'))

print("MODELS: " + str(scaler) + str(one_hot_encoder) + str(model))
numerical_columns = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term"]
categorical_columns = ["Gender", "Married", "Dependents", "Credit_History", "Education",
                       "Property_Area"]
X = ['ApplicantIncome', 'CoapplicantIncome', 'LoanAmount', 'Loan_Amount_Term', 'Gender_Female',
     'Gender_Male', 'Married_No', 'Married_Yes', 'Dependents_0', 'Dependents_1', 'Dependents_2', 'Dependents_3+', 'Credit_History_No', 'Credit_History_Yes',
     'Education_Graduate', 'Education_Not Graduate', 'Property_Area_Rural', 'Property_Area_Semiurban', 'Property_Area_Urban']



@app.route('/processPerson', methods=["POST", "GET"])
def processPerson():
    try:
        json_record = dict(request.json)

        record = pd.DataFrame(json_record, columns=numerical_columns + categorical_columns)
        record["Credit_History"] = record["Credit_History"].replace({0: "No", 1: "Yes"})

        encoded_categories_df = pd.DataFrame(one_hot_encoder.transform(record[categorical_columns]),
                                             columns=one_hot_encoder.get_feature_names_out())
        record = pd.concat([record, encoded_categories_df], axis=1)
        record.drop(columns=categorical_columns, inplace=True)

        record[numerical_columns] = scaler.transform(record[numerical_columns])

        prediction = model.predict_proba(np.array(record.loc[0]).reshape(1, -1))
        print(prediction[0][1])
        return str(prediction[0][1])
    except:
        return "nema json"


@app.errorhandler(404)
def handle_404(e):
    # handle all other routes here
    return 'Not Found, but we HANDLED IT'


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
    app.run(debug=g.debug, host=host, port=endpoint_port)
