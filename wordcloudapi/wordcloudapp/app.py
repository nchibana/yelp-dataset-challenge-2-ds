from flask import Flask, jsonify, request
import requests
from flask_cors import CORS, cross_origin
from .timeseries import timeseries
from .dashboard import jsondata


def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route('/')
    @app.route('/index')
    @app.route('/api', methods=['POST'])
    def make_predict():
        data = request.get_json(force=True)
        predict_request = data['business_id']
        result = timeseries(predict_request)
        return result

    @app.route('/dashboard', methods=['POST'])
    def get_data():
        user_input = request.get_json(force=True)
        info_request = user_input['business_id']
        output = jsondata(info_request)
        return output

    return app