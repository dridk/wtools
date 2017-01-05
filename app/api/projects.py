from flask import jsonify, request, g, abort, url_for, current_app 
from app.api import api
from app.exceptions import CustomError
import os
from app.utils import toJson
from variant_tools.project import Project
import uuid
import shutil

def project_to_item(project_dir):
	PATH = current_app.config['DATA_PATH']
	
	try:
		os.chdir(os.path.join(PATH,project_dir))
	except:
		raise CustomError("Cannot find projet")

	item = {}
	
	try:
		p = Project(verbosity='0') 
		item["name"]   = p.name
		item["build"]  = p.build 
		item["alt_build"]  = p.alt_build 
		item["annoDB"] = [i.name for i in p.annoDB]
		item["creation_date"] = p.creation_date
		item["dbName"] = p.db.dbName
		item["proj_file"] = p.proj_file
		item["id"] = project_dir
		item["variant_count"] = p.db.numOfRows("variant")
		p.close()
	except Exception as e:
		return None

	return item



#================================================================================
@api.route('/projects/')
def get_projects():
	output = []
	PATH = current_app.config['DATA_PATH']
	for d in os.listdir(PATH):
		item = project_to_item(d)
		if item is not None:
			output.append({"id":d, "name": item["name"]})

	return toJson(output)

#================================================================================
@api.route('/projects/', methods=['POST'])
def create_project():
	name   = request.json.get("name", "no_name")
	PATH   = current_app.config['DATA_PATH']
	FOLDER = str(uuid.uuid4())[:8]
	os.mkdir(os.path.join(PATH,FOLDER))
	os.chdir(os.path.join(PATH,FOLDER))

	p = Project(name = name, verbosity='0', mode='NEW_PROJ')
	p.close()

	return toJson({"id": FOLDER, "name": name})

#================================================================================
@api.route('/projects/<id>/')
def get_project(id):
	item = project_to_item(id)
	return toJson(item)
#================================================================================
@api.route('/projects/<id>/', methods=['DELETE'])
def delete_project(id):
	PATH   = current_app.config['DATA_PATH']
	# DELETING FILES IS DANGEROUS... CHECK IF IT IS THE GOOD FILE 
	if id in os.listdir(PATH):
		try:
			shutil.rmtree(os.path.join(PATH,id))
		except:
			raise CustomError("cannot remove project")

	return toJson({"id": id})