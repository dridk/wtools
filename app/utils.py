from flask import jsonify 

def toJson(data):
    if isinstance(data,list):
        return jsonify({"success":True, "results":data, "total": len(data)})
    else:
        return jsonify({"success":True, "results":data})


