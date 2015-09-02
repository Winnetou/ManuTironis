 #coding:utf-8

from flask import Flask
#from flask import Blueprint
from flask import render_template, request, jsonify
import sqlite3
#from .manes import *

#app = Blueprint('blueprint', __name__, 
#    template_folder='templates')
app = Flask(__name__)

def get_cursor():
    conn =sqlite3.connect('/Users/QTF/Desktop/ManuTironis/testbase2')
    c = conn.cursor()
    return c


@app.route("/")
def main():
    c = get_cursor()
    all_texts = [ w for w in c.execute("select title, pagenumber from pages ORDER BY pagenumber ASC limit 1") ]
    return render_template("edit.html", all_texts = all_texts)


@app.route("/edit/<text>/<pagenumber>")
def edit(text, pagenumber):
    print text, pagenumber
    c = get_cursor()
    rec = [p for p in c.execute("select image_url, notepad from pages where title=? and pagenumber = ?",(text,pagenumber))][0]
    print rec
    record = {'image_url': rec[0], 'notepad':rec[1]}
    #must be record id
    print record
    return render_template("edituiboot.html",record = record)
    return render_template("editui.html",record = record)
 
''' 
@app.route("/update", methods=['POST'])
def update():
    #Ajax - the most important functionality of updating the record

    record_id = request.form['record_id']
    word_id = request.form['word_id']
    correct_form = request.form['correct_form']
    do_the_update(record_id, word_id, correct_form)
    if update_was_successful:
        return jsonify("OK")
    else:
        return jsonify("FAIL")

@app.route("/suggest/<word>", methods=['GET'])
def suggest(word):
    #Ajax - receive incorrect form, suggest correction''

    suggestions = db.get(word)
    return jsonify(suggestions)
#


def do_the_update(record_id, word_id):
    #Here we handle saving that new word to the db
    #1. update the record by changing this one word 
    #2. add that change to version history
    pass
'''

if __name__== "__main__":
    app.run()