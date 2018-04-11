import logging

from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .model import Token, ArmaggedonIsComing, Correction

logging.basicConfig(filename='db_access_logger.log', level=logging.DEBUG)
app = Celery('psql_manu_tironis', broker='amqp://guest@localhost//')

engine = create_engine('postgresql+psycopg2://quellen:quellen@localhost/manu_tironis')
# create a Session
Session = sessionmaker(bind=engine)
session = Session()


@app.task
def add_correction(data):
    """
    :return: 
    """
    cor = Correction(**data)
    session.add(cor)
    session.commit()


@app.task
def set_correct_to_many(word_id):
    """
    Saves a word to the database
    if it is not there yet
    """
    try:
        tokn = session.query(Token).get(Token.id == word_id)
        word = tokn.token
        # TODO - what shall we do about uppercase?
        session.query(Token).filter(Token.token == word).update({'is_correct': True})
        session.query(Token).filter(Token.full == word).update({'is_correct': True})
        session.commit()
        _upsert_word(word)
    except:
        session.rollback()
    return


''' 

def _upsert_word(word):
    """
    :param word: 
    :return: 
    """
    import psycopg2
    connect_manu = psycopg2.connect("dbname=manu_tironis user=quellen password=quellen")
    manu_cursor = connect_manu.cursor()
    try:
        insert_command = "INSERT INTO words (word) VALUES (%s)"
        manu_cursor.execute(insert_command, (word,))
        connect_manu.commit()
    except:
        connect_manu.rollback()
    return

'''


@app.task
def run_best_guess(word_id, old_token, new_token):
    """
    Saves a word to the database
    if it is not there yet
    """
    # , we take all tokens with the same old_token
    # and for every token corrected we add CORRECTION
    all_to_be_corrected = session.query(Token).filter(Token.token == old_token) \
        .filter(Token.is_correct == False).all()
    # FIXME we need to also find the words with FULL and with CLEANED TOKEN equal to new_token
    for tokn in all_to_be_corrected:
        try:
            corc_data = {
                'token_affected': tokn.id,
                'before': old_token,
                'after': new_token,
                'source': 'best_guess'
            }
            add_correction(**corc_data)
            tokn.token = new_token
            tokn.is_correct = True
            session.commit()
        except:
            session.rollback()
            continue

    return


@app.task
def rollback_token(word_id, token_before, token_after):
    """
    :param word_id: token id 
    :param before: version before
    :param after: version after
    :return: 
    """
    tokn = session.query(Token).get(word_id)
    if tokn.token != token_after:
        raise ArmaggedonIsComing
    tokn.token = token_before
    tokn.is_correct = False
    return
