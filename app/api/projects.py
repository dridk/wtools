from flask import jsonify, request, g, abort, url_for, current_app 
from app.api import api
from app.exceptions import CustomError


@api.route('/projects')
def get_projects():
	raise CustomError("sorry ")
    # return jsonify(["yes","yo", current_app.config['DATA_PATH']])


