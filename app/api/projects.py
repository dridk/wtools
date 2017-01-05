from flask import jsonify, request, g, abort, url_for, current_app,send_file
from app.api import api
from app.exceptions import CustomError
import os
from app.utils import toJson
from variant_tools.project import Project
from variant_tools import variant 
import sys
import uuid
import shutil
import argparse
import tempfile
from io import StringIO,BytesIO

def project_to_item(project_dir):
	PATH = current_app.config['DATA_PATH']

	test = os.path.join(PATH,project_dir)
	print(test)

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
	for d in [p for p in os.listdir(PATH) if os.path.isdir(os.path.join(PATH,p))]:
		
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
@api.route('/projects/<projet_id>/', methods=['DELETE'])
def delete_project(projet_id):
	PATH   = current_app.config['DATA_PATH']
	# DELETING FILES IS DANGEROUS... CHECK IF IT IS THE GOOD FILE 
	if projet_id in os.listdir(PATH):
		try:
			shutil.rmtree(os.path.join(PATH,projet_id))
		except:
			raise CustomError("cannot remove project")

	return toJson({"id": projet_id})

#================================================================================
@api.route('/projects/<projet_id>/select/')
def select(projet_id):

	#  http GET :5000/api/projects/projet1/select/ fields:='["chr","pos", "ref", "alt", "name2"]'

	if request.json is None:
		raise CustomError("No fields in body")

	if "fields" not in request.json:
		raise CustomError("No fields in body")

	fields = request.json["fields"]

	PATH  = current_app.config['DATA_PATH']
	os.chdir(os.path.join(PATH, projet_id))

	parser  = argparse.ArgumentParser()
	variant.selectArguments(parser)
	variant.generalOutputArguments(parser)
	parser.add_argument('-v', '--verbosity', choices=['0', '1', '2', '3'])


	req = ['variant','-o'] + fields
	print(req)

	args = parser.parse_args(req)


	old_stdout = sys.stdout 
	result =  StringIO()
	sys.stdout = result
	variant.select(args)
	sys.stdout = old_stdout
	result.seek(0)
	data = str.encode(result.getvalue())

	return send_file(BytesIO(data),
                     attachment_filename="select.csv",
                     as_attachment=True)






