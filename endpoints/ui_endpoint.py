import __init__
from flask import Flask, render_template, redirect, request, flash, url_for
from flasgger import Swagger
from utils import general_utils as g
from argparse import ArgumentParser

app = Flask(__name__, template_folder=g.root_path + 'templates')
swagger = Swagger(app)



@app.route('/index')
def index():
    return render_template('form.html')

@app.route("/form" , methods=['GET', 'POST'])
def form():
  gender             = request.form.get('genderOptions')
  married            = request.form.get('marriedOptions')
  dependents         = request.form.get('dependents')
  education_degree   = request.form.get('educationDegree')
  self_employed      = request.form.get('selfEmployedOptions')
  applicant_income   = request.form.get('applicantIncome')
  coapplicant_income = request.form.get('coapplicantIncome')
  loan_amount        = request.form.get('loanAmount')
  loan_amount_term   = request.form.get('loanAmountTerm')
  credit_history     = request.form.get('creditHistory')
  property_area_type = request.form.get('propertyAreaType')


  data = {
    "Gender":               gender,
    "Married":              married,
    "Dependents":           dependents,
    "Education Degree":     education_degree,
    "Self Employed":        self_employed,
    "Applicant's Income":   applicant_income,
    "Coapplicant's Income": coapplicant_income,
    "Loan Amount":          loan_amount,
    "Loan Amount Term":     loan_amount_term,
    "Credit History":       credit_history,
    "Property Area Type":   property_area_type
  }

@app.route('/')
def hello():
    """Root, please go somewhere else
    ---
    responses:
      200:
        description: why would you go here, go away
    """
    return redirect(f"apidocs", code=200)




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
