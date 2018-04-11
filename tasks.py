################################################
############                    ################
############     DEPRECATED     ################
############                    ################
################################################

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .model import Page, Token
from . import shallow_backend

engine = create_engine('postgresql+psycopg2://quellen:quellen@localhost/manu_tironis')
# create a Session
Session = sessionmaker(bind=engine)
session = Session()

from celery import Celery

logging.basicConfig(filename='db_access_logger.log', level=logging.DEBUG)
app = Celery('psql_manu_tironis', broker='amqp://guest@localhost//')


@app.task
def async_update_documents_notepad(doc_id, new_notepad):
    psql_manu_tironis.update_documents_notepad(doc_id, new_notepad)


@app.task
def update_really_all_texts(word):
    """
    Token was recognized as correct: we can set `is_correct` flag
    to True everywhere else
    :param word: 
    :return: 
    """
    session.query(Token).filter(Token.token == word).update({"is_correct": True})
    # second step: if property 'full' is there and equal to "word"
    session.query(Token).filter(Token.full == word).update({"is_correct": True})
    # session.find_and_update(Token).where(token.full == word)
    return


@app.task
def run_best_guess(correct_word, mistaken_word):
    """
    If the word was corrected (eg w0rd to word)
    it may a common OCR mistake
    in that case run all identical incorrect words
    and change their text to corrected
    but still keep'em as corr=0 in case the best guess
    is not really 100% correct
    This func is called by `update.save_corrected`
    :param doc_id:  ObjectId(page_id)
    """

    session.query(Token).filter(Token.token == mistaken_word).filter(Token.is_correct == False).update(
        {'token': correct_word})
    return
