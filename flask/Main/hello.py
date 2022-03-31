from flask import Flask
# from flask_restplus import Namespace, Resource, fields

app = Flask(__name__)


@app.route('/basic_api/hello_world')
def hello_world():
    return 'Hello, World!'


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route("/<string:job_id>")
def main(job_id):
    return f"Welcome!. This is Flask Test Part 1 {job_id}"

