 #coding:utf-8

from flask import Flask
#from flask import Blueprint
from flask import render_template, request, jsonify

#from .manes import *

#app = Blueprint('blueprint', __name__, 
#    template_folder='templates')
app = Flask(__name__)

@app.route("/")
def index_view():
    return render_template("index.html")


if __name__== "__main__":
	app.run()