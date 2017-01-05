from flask import jsonify, request, g, abort, url_for, current_app 
from . import api


@api.route('/projects')
def get_projects():
    return jsonify(["yes","yo", current_app.config['DATA_PATH']])


