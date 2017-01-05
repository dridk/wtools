from flask import jsonify, request, g, abort, url_for, current_app 
from app.api import api
from app.exceptions import CustomError
import os
from app.utils import toJson
from variant_tools.project import Project

@api.route('/projects')
def get_projects():
	output = []
	PATH = current_app.config['DATA_PATH']
	for d in os.listdir(PATH):
		os.chdir(os.path.join(PATH,d))
		try:
			p = Project()
		except ValueError as err:
			pass
		else:
			item = {}
			item["name"]   = p.name
			item["build"]  = p.build 
			item["alt_build"]  = p.alt_build 
			item["annoDB"] = [i.name for i in p.annoDB]
			item["creation_date"] = p.creation_date
			item["dbName"] = p.db.dbName
			item["proj_file"] = p.proj_file
			item["variant_count"] = p.db.numOfRows("variant")

			output.append(item)

	return toJson(output)



