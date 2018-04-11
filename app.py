from flask import Flask, request, jsonify, render_template, abort, Response

from . import shallow_backend
from . import suggest

app = Flask(__name__)
app.debug = True


# todo: 1. suggestions do not work
# todo: 2. adding corrections is still not implemeneted
# todo: 3. joining tokens across the lines has to be implemented
# todo: 4. commitable decorator

@app.route('/scriptorium')
def scriptorium():
    '''scriptorium page: returns titles of
    works being transcribed'''
    titles = shallow_backend.get_just_titles()
    return render_template("scriptorium.html", titles=titles)


# FIXME - for nice frienldy urls: /tiro/<author>/<title>/page
@app.route('/tiro/<title>/<int:pagenumber>')
def tiro(title, pagenumber):
    """shows single page"""
    page = shallow_backend.get_page(title, pagenumber)
    if not page:
        abort(404)
    return render_template("tiro.html", page=page)


# AJAX SECTION

@app.route("/suggest")
def suggest():
    """ Ajax - receive incorrect form, suggest correction"""
    incorrect = request.args.get('word')
    suggestions = suggest.smart_suggest(incorrect)
    return jsonify(suggestions)


@app.route("/update", methods=['POST'])
def update():
    '''
    Corrected version of the token provided manually by user
    Rename the function. 
    '''
    correct_form = request.form.get('correct_form')
    word_id = request.form.get('word_id')
    return shallow_backend.save_corrected(word_id, correct_form)


@app.route("/divide", methods=['POST'])
def divide():
    """
    Fixme: use PUT method
    :return: 
    """
    word_id = request.form.get('word_id'),
    word = request.form.get('word')
    return shallow_backend.divide_word(word_id, word)


@app.route("/join", methods=['POST'])
def join():
    """
    Fixme: use PUT method
    :return: 
    """
    word_id = request.form.get('word_id')
    word = request.form.get('word')
    return shallow_backend.join_word_with_next(word_id, word)


@app.route("/setcorrect", methods=['POST'])
def set_correct():
    '''
    User clicks: 'this word is correct' - we set corr to 1 
    '''
    word_id = request.form.get('word_id')
    return shallow_backend.set_correct(word_id)


@app.route("/setincorrect", methods=['POST'])
def setincorrect():
    ''' 
    User clicks: 'this word is not correct' - we set corr to 0
    '''
    word_id = request.form.get('word_id')
    return shallow_backend.set_incorrect(word_id)


@app.route("/setpagination", methods=['POST'])
def setpagination():
    '''
    '''
    word_id = request.form.get('word_id')
    return shallow_backend.set_pagination(word_id)


@app.route("/remove", methods=['POST'])
def remove():
    '''
    Remove token
    '''
    word_id = request.form.get('word_id')
    return shallow_backend.remove(word_id)


# ADMIN SECTION

@app.route("/corrections", methods=['GET'])
def get_corrections():
    '''
    Show all corrections  - only to logged in user
    '''
    time_from = request.args.get('time_from')
    time_to = request.args.get('time_to')
    source = request.args.get('source')
    corrections = shallow_backend.get_corrections(time_from=time_from,
                                                  time_to=time_to,
                                                  source=source)
    return render_template("corrections.html", corrections=corrections)


@app.route("/rollback", methods=['POST'])
def rollback():
    '''
    Rollback correction
    '''
    word_id = request.form.get('word_id')
    return shallow_backend.roll_back(word_id)


@app.errorhandler(404)
def page_not_found(error):
    ''' 404 '''
    return render_template("404.html"), 404
