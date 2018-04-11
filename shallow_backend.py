# in nomine Patris et Filii et Spiritu Sancto
import uuid
import psycopg2

from . import deep_backend

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .model import Work, Page, Token, Correction, ArmaggedonIsComing

from Levenshtein import ratio

engine = create_engine('postgresql+psycopg2://quellen:quellen@localhost/manu_tironis')
# create a Session
Session = sessionmaker(bind=engine)
session = Session()


def get_page(title, pagenumber, page_id=None):
    """
    Page does not exists.
    :param page_number:
    :return: string (being the html)
    """

    if page_id is None:
        p = session.query(Page).join(Page.work).filter(Work.title_standardized == title).filter(
            Page.page_number == pagenumber).one_or_none()
    else:
        p = session.query(Page).get(page_id)
    return p.dictified if p else p


def get_just_titles():
    """
    Return distinct list of titles.
    Called by app.quellen.scriptorium
    :return: 
    """
    # FIXME - that cannot go to production
    # we have to query page with mininum oage number
    # distinct for every work.
    works = session.query(Work).distinct().all()
    titles_pages = []
    for work in works:
        if len(work.pages) > 0:
            pagenumber = work.pages[0].page_number
            titles_pages.append({'title': work.title_standardized, 'pagenumber': pagenumber})
    return titles_pages


def join_word_with_next(word_id, word):
    """
    Take a token, join with the next one
    :param word_id: uuid of the token
    :param word: in case 
    :return: string
    """
    # There must be a better way to delete a token.
    # right now, it messes up the numeration
    # and we use a hack to make it less messy
    token = session.query(Token).get(word_id)
    if token.is_last_in_line:
        return join_tokens_across_lines(word_id)
    next_token = token.get_next_token()
    try:
        joined_token = token.token + next_token.token
        # if word was provided and it is different from
        # joined tokens
        if word and joined_token != word:
            token.token = word
        else:
            token.token = joined_token
        next_token.deleted = True
        next_token.number = next_token.number * -1
        all_tokens_with_higher_number = session.query(Token) \
            .filter(Token.line_id == token.line_id) \
            .filter(Token.number > token.number).all()
        for token in all_tokens_with_higher_number:
            token.number -= 1
        session.commit()
        add_correction(token)
        add_correction(next_token)
        return token.with_markup
    except:
        session.rollback()
        raise


def join_tokens_across_lines(word_id):
    """
    The words we join are across two lines
    Hyphen shall be added to word 1, half=1, 
    to word two: full and half=2
    :param word_id: 
    :return: 
    """
    the_token = session.query(Token).get(word_id)
    next_token = the_token.get_next_token(word_id)
    if the_token.line_id != next_token.line_id:
        raise ArmaggedonIsComing
    try:
        if not the_token.token.endswith("-"):
            full_token = the_token.token + next_token.token
            the_token.token += '-'
        else:
            full_token = the_token.token[:-1] + next_token.token
        the_token.full = next_token.full = full_token
        the_token.half = 1
        next_token.half = 2
        add_correction(token)
        add_correction(next_token)

        session.commit()
    except:
        session.rollback()
    return
    # FIXME FINISH ME! TESTME


def divide_word(word_id, word):
    divided_words = word.split(" ")
    if not len(divided_words) > 1:
        return
    try:
        first_part = divided_words[0]
        token_to_be_divided = session.query(Token).get(word_id)
        token_to_be_divided.token = first_part
        # now we need to reorder the tokens to add another one
        all_tokens_with_higher_number = session.query(Token).filter(Token.line_id == token_to_be_divided.line_id) \
            .filter(Token.number > token_to_be_divided.number).all()
        # if token was divided into 3 parts, then the next token number
        # shall start with number+len(divided_words)-1
        increment = len(divided_words) - 1
        for token in all_tokens_with_higher_number:
            token.number += increment
        # and now we can add new token
        res = [token_to_be_divided]
        counter = 1
        for next_part in divided_words[1:]:
            new_token_data = {
                'id': uuid.uuid4(),
                'token': next_part,
                'line': token_to_be_divided.line,
                'number': token_to_be_divided.number + counter,
                'is_correct': False,  # is_correct(next_part)
                'is_greek': True
            }
            counter += 1
            t = Token(**new_token_data)
            res.append(t)
            session.add(t)
        session.commit()
        add_correction(token)
        add_correction(next_token)
        return " ".join([t.with_markup for t in res])
    except:
        session.rollback()
        raise


def set_correct(word_id):
    """
    UI says token is incorrect, user changes it to correct
    :param word_id: 
    :return: 
    """
    token = session.query(Token).get(word_id)
    token.is_correct = True
    session.commit()
    add_correction(token)
    # deep_backend.set_correct_to_many(word_id)
    return token.with_markup


def set_incorrect(word_id):
    token = session.query(Token).get(word_id)
    token.is_correct = False
    session.commit()
    add_correction(token)
    return token.with_markup


def set_pagination(word_id):
    # import pdb
    # pdb.set_trace()
    token = session.query(Token).get(word_id)
    token.is_greek = False
    token.is_side_pagination = True
    session.commit()
    add_correction(token)
    return token.with_markup


def save_corrected(word_id, new_token):
    """
    Saves new, corrected version of a token
    :return: 
    """
    new_token = new_token.strip()

    assert len(new_token.split(" ")) == 1
    if len(new_token.split(" ")) > 1:
        # we have split -- call new func
        divide_word(word_id, new_token)
        # FIXME -   that func has to return saved str
        token = session.query(Token).get(word_id)
    old_token = token.token
    deep_backend.run_best_guess(word_id, old_token, new_token)
    token.token = new_token
    token.is_correct = True
    session.commit()
    add_correction(token)
    return token.with_markup


def remove(word_id):
    """
    Changes flag  `deleted` from True to Falsch
    :param word_id: 
    :return: 
    """

    token = session.query(Token).get(word_id)
    token.number = token.number * -1
    token.deleted = True
    session.commit()
    add_correction(token)
    return ""


'''
def commitable(func):
    def wrapper():
        try:
            func(*args, **kwargs)
            session.commit()
            return
        except:
            session.rollback()
            raise
    return wrapper
'''


def add_correction(token_id, old_version, new_version):
    try:
        vals = {
            'id': uuid.uuid4(),
            'token_affected': token_id,
            'before': old_version,
            'after': new_version,
            'source': 'user'
        }
        c = Correction(**vals)
        session.add(c)
        session.commit(c)
    except:
        log.error()
        # let's keep it somewhere else
        # do not throw up
        pass


def get_corrections(time_from=None, time_to=None, source=None):
    """
    :return: 
    """
    corrections = session.query(Correction).filter(Correction.rolled_back == False)
    if time_from is not None:
        corrections.filter(Correction.date > time_from)
    if time_to is not None:
        corrections.filter(Correction.date < time_to)
    if source is not None:
        corrections.filter(Correction.source == source)
    return corrections.all()


def roll_back(correction_id):
    """
    take a correction id, roll back the change to the Token
    :param correction_id: 
    :return: 
    """
    try:
        corr = session.query(Correction).get(correction_id)
        word_id, before, after = corr.token_affected, corr.before, corr.after
        deep_backend.rollback_token(word_id, before, after)
        corr.rolled_back = True
        session.commit()
    except:
        session.rollback()
    return
