from doctest import OutputChecker
from pathlib import Path
from time import time
from subprocess import Popen, PIPE
from flask import Flask, jsonify, request
from marshmallow import Schema, fields, validate, ValidationError

app = Flask(__name__)

class PredictionRequest(Schema):
    layer_path = fields.Str(validate=validate.Length(min=1))
    model = fields.Str(validate=validate.Length(min=1))
    folder = fields.Str(validate=validate.Length(min=1))

@app.route('/')
def mock():
    from time import sleep
    sleep(20)
    return jsonify('Hello World')

@app.route('/predict', methods=['POST'])
def run_predict():
    data = request.get_json()
    schema = PredictionRequest()
    try:
        result = schema.load(data)
    except ValidationError as err:
        print("Invalid request body")
        return jsonify({"error": "Invalid request body"}), 400

    #Create folder to store output in volume ./appdata
    try:
        model = "./appdata/" + result['model'] + ".zip"
        #Here do the prediction CLI call
        args = "python -m rastervision.pipeline.cli predict {} {} {}".format(model, result['layer_path'], result['folder']).split(" ")
        p = Popen(args)
        p.wait()
        if p.returncode != 0:
            raise Exception("Error occured in rastervision during prediction task")
    except Exception as e:
        print("Error occured during prediction task: ", e)
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Successfully completed prediction"}), 200

# main driver function
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)