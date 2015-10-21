 #!/usr/bin/env python
 #coding:utf-8

from flask import Flask
#from flask import Blueprint
from flask import render_template, request, jsonify
import sqlite3
from manes import give_suggestions

#app = Blueprint('blueprint', __name__, 
#    template_folder='templates')
app = Flask(__name__)

def get_cursor():
    conn =sqlite3.connect('/Users/QTF/Desktop/ManuTironis/testbase')
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
    record = {'image_url': rec[0], 'notepad':rec[1]}
    #must be record id
    # and we need to return prev page and next page as weel
    record['prev_page'] = "#"
    record['next_page'] = "#"
    return render_template("edituiboot.html",record = record)
    
@app.route("/suggest")
def suggest():
    #Ajax - receive incorrect form, suggest correction''
    word = request.args.get('word')
    suggestions = give_suggestions(word)
    benc = {}
    for t in suggestions:
        benc[t] = t
    return jsonify(benc)
    #return jsonify(suggestions)
 

@app.route("/update", methods=['POST'])
def update():

    page_id = request.values.get('page_id')
    word_id = request.values.get('word_id')
    correct_form = request.values.get('correct_form')

    #validation - do it now, before messing with the db
    #if any(len(x)==0 for x in [record_id, word_id, correct_form]):
    #    return jsonify({'result':"FAIL"})
    #do_the_update(record_id, word_id, correct_form)
    if True: #update_was_successful:
        return jsonify({'result':"OK"})
    else:
        return jsonify({'result':"FAIL"})

## MOVE IT LATER TO ANOTHER SPACE
from bs4 import BeautifulSoup

def do_the_update(record_id, word_id, correct_form):
    #Here we handle saving that new word to the db
    #1. update the record by changing this one word 
    #for mongo
    record_to_update = collection.find_one({"Oid":record_id})
    #for now
    record_to_update = c.execute("select notepad from pages where id=?", (record_id))[0]
    #now, make the soup
    soup = BeautifulSoup(text)
    word_to_be_upd = soup.find("span",attrs={"id":word_id})
    word_to_be_upd.text = correct_form # is it right? FIXME if not
    #2. add that change to version history
    #3. add the word and it's prev version to the db
    if update_was_successful:
        return "OK"
    else:
        return "FAIL"

def major_drama(*args):
    '''Something really creepy happened. 
    Log the circumstances and 
    let the chef know about it '''
    pass
if __name__== "__main__":
    app.run()