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
@api.route('/projects/<projet_id>/select/', methods= ['POST'])
def select(projet_id):

	#  http GET :5000/api/projects/projet1/select/ fields:='["chr","pos", "ref", "alt", "name2"]'
	if request.json is None:
		raise CustomError("No fields in body")

	if "fields" not in request.json:
		raise CustomError("No fields in body")



	fields = request.json["fields"]

	print(fields)

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



#================================================================================
@api.route('/projects/<projet_id>/tables/')
def get_tables(projet_id):
	PATH  = current_app.config['DATA_PATH']
	os.chdir(os.path.join(PATH, projet_id))
	p = Project(verbosity='0') 
	results = []
	for name in p.getVariantTables():
		item = {}
		item["name"] = name
		item["description"] = p.descriptionOfTable("variant")[0]
		item["created"] = p.descriptionOfTable("variant")[1]
		item["cmd"] = p.descriptionOfTable("variant")[2]
		item["count"] = p.db.numOfRows("variant")

		results.append(item)

	p.close()
	return toJson(results)

#================================================================================
@api.route('/projects/<projet_id>/tables/<name>/')
def get_table(projet_id, name):
	PATH  = current_app.config['DATA_PATH']
	os.chdir(os.path.join(PATH, projet_id))
	p = Project(verbosity='0') 

	if name not in p.getVariantTables():
		raise CustomError("Cannot find table "+name)

	item = {}
	item["name"] = name
	item["description"] = p.descriptionOfTable("variant")[0]
	item["created"] = p.descriptionOfTable("variant")[1]
	item["cmd"] = p.descriptionOfTable("variant")[2]
	item["count"] = p.db.numOfRows("variant")
	p.close()

	return toJson(item)

#================================================================================
@api.route('/projects/<projet_id>/annotations/')
def get_annotations(projet_id):
	PATH  = current_app.config['DATA_PATH']
	os.chdir(os.path.join(PATH, projet_id))
	p = Project(verbosity='0') 	
	results = []
	index = 0
	for db in p.annoDB:
		item = {}
		item["id"] = index
		item["name"] = db.name 
		item["description"] = db.description
		item["type"] = db.anno_type 
		item["dir"] = db.dir 
		item["filename"] = db.filename
		item["fieldsCount"] = len(db.fields)
		item["version"] = db.version
		results.append(item)
		index+=1

	return toJson(item)
#================================================================================
@api.route('/projects/<projet_id>/annotations/<int:index>/')
def get_annotation(projet_id, index):
	PATH  = current_app.config['DATA_PATH']
	os.chdir(os.path.join(PATH, projet_id))
	p = Project(verbosity='0') 	
	
	if index < 0 or index >= len(p.annoDB):
		raise CustomError("Not a valid ID")

	db = p.annoDB[index]
	item = {}
	item["id"] = index
	item["name"] = db.name 
	item["description"] = db.description
	item["type"] = db.anno_type 
	item["dir"] = db.dir 
	item["filename"] = db.filename
	item["fieldsCount"] = len(db.fields)
	item["version"] = db.version
	fields = []
	for f in db.fields:
		f_item = {}
		f_item["id"] = f.index 
		f_item["name"] = f.name
		f_item["type"] = f.type
		f_item["comment"] = f.comment
		fields.append(f_item)
	item["fields"] = fields 
	return toJson(item)

#================================================================================
@api.route('/projects/<projet_id>/fields/')
def get_fields(projet_id):
	PATH  = current_app.config['DATA_PATH']
	os.chdir(os.path.join(PATH, projet_id))
	p = Project(verbosity='0') 	

	results = []

	item = {}
	item["name"] = "variant"
	fields = []
	for i in p.db.fieldsOfTable("variant"):
		if i[0] not in ("variant_id","bin"):
			f_item = {}
			f_item["name"] = str(i[0])
			f_item["full_name"] =  str(i[0])
			f_item["type"] = "variant."+str(i[0])
			f_item["comment"] = p.descriptionOfField(str(i[0]))
			fields.append(f_item)
	item["fields"] = fields 
	results.append(item)


	for db in p.annoDB:	
		item = {}
		item["name"] = db.name 
		fields = []
		for f in db.fields:
			f_item = {}
			f_item["name"] = f.name
			f_item["full_name"] = db.name +"."+f.name
			f_item["type"] = f.type
			f_item["comment"] = f.comment
			fields.append(f_item)
		item["fields"] = fields 
		results.append(item)



	return toJson(results)
