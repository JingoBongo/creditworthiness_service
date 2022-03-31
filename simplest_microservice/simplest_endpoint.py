from b_logic_placeholder import do_the_thing_function
from flask import Flask, jsonify
# from flask_swagger import swagger
from flasgger import Swagger

# from flask_restplus import Namespace, Resource, fields

app = Flask(__name__)
swagger = Swagger(app)


@app.route('/hello_world')
def hello_world():
    return 'Hello, World!'


@app.route('/')
def hello():
    return 'try swagger at least, (apidocs)'


@app.route("/user/<string:job_id>")
def main(job_id):
    """I have no idea why is this a title
        These are just notes as an example. And as a note, I don't care about
        most of it's functionality, it will be enough just putting a name&comment above each endpoint
        just for BRIEF explanation. We are not getting paid here after all.
        But I didn't find time to understand how to make proper examples and etc here. I don't care,
        we can just delete everything below next line.
        ---
        parameters:
          - arg1: whatever, dude, this goes into business logic for now
            type: string
            required: true
            default: none, actually
        definitions:
          Job_id:
            type: String
        responses:
          200:
            description: A simple business logic unit with swagger
            schema:
              $ref: '{job_id}'
            examples:
              job_id: {"job_id": 'botan'}
        """
    return do_the_thing_function(job_id)


# @app.route("/spec")
# def spec():
#     swag = swagger(app)
#     swag['info']['version'] = "1.0"
#     swag['info']['title'] = "Simplest API"
#     return jsonify(swag)