# Here we translate old DB to new one
import psycopg2
import psycopg2.extras
import uuid

from bs4 import BeautifulSoup, Tag
from model import Work, Page, Token, Line

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CreateSchema

Base = declarative_base()

# an Engine, which the Session will use for connection
# resources
engine = create_engine('postgresql+psycopg2://quellen:quellen@localhost/manu_tironis')

# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()

# Base.metadata.create_all(engine) # <--- that command creates tables on the db

connect_manu = psycopg2.connect("dbname=manu_tironis user=quellen password=quellen")
c = connect_manu.cursor()
dict_cur = connect_manu.cursor(cursor_factory=psycopg2.extras.DictCursor)


def clean_token(token):
    """
    :param token: string
    :return: string
    """
    bad_seeds = ["", ""]
    token = token.strip()
    while token[-1] in bad_seeds and len(token) > 1:
        token = token[:-1]


def is_greek_numeral(token):
    return False


def is_latin_numeral(token):
    return False


def is_arabic_numeral(token):
    if all(w in list("1234567890") for w in token):
        return True
    return False


def is_greek_punctuation(token):
    return False


def is_latin_punctuation(token):
    if token in list(",.<>?)(:!?_-"):
        return True
    return False


def make_homer():
    vals = {
        'id': uuid.uuid4(),
        'title_volume': "Homeri Ilias. ",
        'title_standardized': "Ilias",
        'author_volume': "Homerus",
        'author_standardized': "Homerus",
        'edition': "1828",
        'editor': "Hovanietz, Mieszko",
        "ISBN": "321458"
    }
    try:
        werk = Work(**vals)
        session.add(werk)
        session.commit()
    except:
        raise


def create_work_if_doesnt_exist():
    """
    :return:
    """
    # Niebuhr, Barthold Georg, 1776-1831 et al. (1828).
    # Corpus scriptorum historiae byzantinae. Editio emendatior et copiosior. consilio B.G. Niebuhrii 4
    vals = {
        'id': uuid.uuid4(),
        'title_volume': "Corpus scriptorum historiae byzantinae. Editio emendatior et copiosior. consilio B.G. Niebuhrii 4",
        'title_standardized': "Chronicon Paschale",
        'author_volume': "Anon.",
        'author_standardized': "Anon.",
        'edition': "1828",
        'editor': "Niebuhr, Barthold Georg",
        "ISBN": "123454321"
    }

    try:
        werk = Work(**vals)
        session.add(werk)
        session.commit()
    except Exception as e:
        session.rollback()
        werk = session.query(Work).filter_by(author_standardized="Anon.", title_standardized="Chronicon Paschale").one()

    return werk


def start_all():
    from sqlalchemy import MetaData
    meta = MetaData(bind=engine)
    Base = declarative_base(bind=engine, metadata=meta)
    Base.metadata.create_all(engine)
    # FIXME - GOd knows why, but that all above has to executed
    # from the shell to persist.  Once you move to prod, do it there
    # as well, babe.
    return


def main():
    # the_work = session.query(Work).first()
    the_work = create_work_if_doesnt_exist()
    c.execute('''SELECT id FROM lace_texts ORDER BY pagenumber::int''')
    pages_IDs = c.fetchall()

    for ord, page_id in enumerate(pages_IDs):
        dict_cur.execute('''SELECT * from lace_texts where id = %s''', page_id)
        record = dict_cur.fetchone()
        page_as_soup = BeautifulSoup(record['notepad'], 'html.parser')
        header_elem = page_as_soup.find("span", {"class": "pagetitle"})
        header_text = header_elem.text
        page_data = {
            "id": uuid.uuid4(),
            "number": ord,
            "header": header_text,
            "page_number_on_top": True,
            "page_number": record["pagenumber"],
            "external_page_scan_url": record["lace_image_url"],
            "page_scan_url": record["image_url"],
            "work": the_work,
        }
        print("page: number {}, pagenumber : {}".format(ord, record['pagenumber']))
        page = Page(**page_data)
        session.add(page)
        lines = page_as_soup.find_all("span", {"class": "ocr_line"})
        word_number = 0
        for line_number, line in enumerate(lines):
            # HERE WE CREATE A LINE INSTANCE
            content = str(line.parent['class'][0])
            line_data = {
                "id": uuid.uuid4(),
                "page": page,
                "number": line_number,
                "content": content
            }
            line_mod = Line(**line_data)
            session.add(line_mod)
            # and now we add Line to Page
            # page.children.append(line)
            words = line.find_all("span")
            number = 0
            for word in words:
                number += 1
                if word.string is None:
                    continue
                # HERE WE CREATE A TOKEN INSTANCE
                word_number += 1
                is_side_pagination = False
                if word.has_attr('class'):
                    if 'side_pagination' in word['class']:
                        is_side_pagination = True
                is_greek = True if word.has_attr('lang') and word['lang'] == 'grc' else False
                is_correct = True if word.has_attr('corr') and word['corr'] == '1' else False
                full_version, half = None, None
                if word.has_attr('full'):
                    full_version = word['full']
                if word.has_attr('half'):
                    half = word['half']
                token_text = word.string
                token_vals = {
                    "id": uuid.uuid4(),
                    'number': number,
                    'line': line_mod,
                    'token': token_text,
                    'is_greek': is_greek,
                    'is_greek_numeral': is_greek_numeral(token_text),
                    'is_latin_numeral': is_latin_numeral(token_text),
                    'is_arabic_numeral': is_arabic_numeral(token_text),
                    'is_side_pagination': is_side_pagination,
                    'is_greek_punctuation': is_greek_punctuation(token_text),
                    'is_latin_punctuation': is_latin_punctuation(token_text),
                    'half': half,
                    'full': full_version,
                    'is_correct': is_correct
                }
                a_token = Token(**token_vals)
                session.add(a_token)
                # line.children.append(token)
        # aaand here we  commit
        session.commit()


def _is_correct(word):
    token_text = word.string
    if word.has_attr('corr') and word['corr'] == '1':
        return True
    else:
        if is_exists_in_db(token_text):
            return True
    return False


def is_exists_in_db(token_text):
    FIXME!  # final test:
    # make sure that :func: model/get_page
    # returns the exact same thing
    # that is already on the db
    if __name__ == '__main__':
        main()
