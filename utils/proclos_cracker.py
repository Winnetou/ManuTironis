import requests
import uuid
from bs4 import BeautifulSoup, Tag
from sqlalchemy.orm import sessionmaker

from model import Page, Line, Token, Work

from sqlalchemy import create_engine

import psycopg2
import words_backend

engine = create_engine('postgresql+psycopg2://quellen:quellen@localhost/manu_tironis')
Session = sessionmaker(bind=engine)
session = Session()

connect_manu = psycopg2.connect("dbname=manu_tironis user=quellen password=quellen")
manu_cursor = connect_manu.cursor()


def is_correct(word):
    return words_backend.word_exists_in_dictionary(word)


def is_just_a_number(line):
    """
    :param line: Tag instance
    :return:
    """
    if line.text.isdigit():
        return True
    return False


def is_header_to_be_ignored(line):
    if len(line.text.split()) == 1:
        return True
    return False


def clean_text_with_new_model(text, header_text, record, the_work):
    """ """
    if record["ordinal_number"] == 1:
        header_text = ""
    page_data = {
        "id": uuid.uuid4(),
        "number": record["ordinal_number"],
        "header": header_text,
        "page_number_on_top": True,
        "page_number": record["pagenumber"],
        "external_page_scan_url": record["lace_image_url"],
        "page_scan_url": record["image_url"],
        "work": the_work
    }
    page = Page(**page_data)
    session.add(page)

    soup = BeautifulSoup(text, 'html.parser')
    # here we make header
    ocr_carea = soup.find('body')
    all_lines = ocr_carea.findAll('span', {"class": "ocr_line"})
    # In most cases, two first lines contain header and page number
    if is_just_a_number(all_lines[0]):
        all_lines = all_lines[1:]
    if is_header_to_be_ignored(all_lines[0]):
        all_lines = all_lines[1:]
    # second round: sometimes in greek text there are words
    # that were ocred with latin chars
    # they have netiher corr=0 nor lang=grc
    # add it here
    line_counter = 0
    for single_line in all_lines:
        line_counter += 1
        content = "greek"
        line_data = {
            "id": uuid.uuid4(),
            "page": page,
            "number": line_counter,
            "content": content
        }
        line_model = Line(**line_data)
        session.add(line_model)
        words = single_line.text.split()
        number_counter = 0
        for word in words:
            number_counter += 1
            is_first = True if words.index(word) == 0 else False
            is_last = True if words[::-1].index(word) == 0 else False
            token_vals = {
                "id": uuid.uuid4(),
                'number': number_counter,
                'line': line_model,
                'token': word,
                'is_greek': True,
                'is_side_pagination': is_side_pagination(word, is_first, is_last),
                'is_greek_punctuation': False,
                'is_latin_punctuation': False,
                'is_correct': is_correct(word),
            }
            a_token = Token(**token_vals)
            session.add(a_token)
            print("JUST added {}".format(a_token.token))

    session.commit()


def is_side_pagination(word, is_first, is_last):
    number_pagin = ('5', '10', '1O', '1o', '15', '5', '20', '2O', '2o', '25', '25', '25',
                    '30', '3o', 'O', '2')
    if is_first or is_last:
        if word in number_pagin:
            return True
    return False


def main(start=11530379,
         finish=11530381,
         skip_pages=[],
         first_page_number=1,
         ):
    '''Fetch a range of pages, clean them and save as a file
    :param start: number in url in lace where we shall start reading ocr
    :param finish see ^^
    :param skip_pages - some pages are empty, we can skip them
    :param first_page_number first number ofl page in print
    we shall start here: http://heml.mta.ca/lace/sidebysideview2/11530379 
    '''
    main_link = "http://heml.mta.ca/lace/sidebysideview2/"
    page_number = first_page_number
    the_work = get_work_or_create()
    # the_work = session.query(Work).filter(Work.author_standardized=='Proclus').one_or_none()
    ordinal_number = 0
    for x in [p for p in range(start, finish) if p not in skip_pages]:
        link = main_link + str(x)
        # whole_page = requests.get(link)._content
        whole_page = get_url_content(link)
        soup = BeautifulSoup(whole_page, "html.parser")
        image = soup.find(attrs={'id': 'page_image'})
        lace_image_url = 'http://heml.mta.ca' + image['src']
        ordinal_number += 1
        record = {
            "lace_image_url": lace_image_url,
            "image_url": lace_image_url,
            "pagenumber": page_number,
            "ordinal_number": ordinal_number
        }
        link_to_iframe = 'http://heml.mta.ca' + \
                         soup.find(attrs={'id': 'page_right'}).findChild('iframe')['src']
        text = get_url_content(link_to_iframe)
        header_text = get_header_text(page_number)
        clean_text_with_new_model(text, header_text, record, the_work)
        page_number += 1  # george the first!
    return


def get_header_text(page_number):
    if page_number % 2 == 0:
        # is is even
        return 'PROKLOU'
    return 'EIS TEN POLITEIAN'


def get_url_content(link_to_iframe):
    v = requests.get(link_to_iframe)
    t = v._content
    return t


def get_work_or_create():
    the_work = session.query(Work).filter(Work.author_standardized == 'Proclus').one_or_none()
    if the_work is None:
        vals = {
            'id': uuid.uuid4(),
            'title_volume': "In Platonis Rem publicam commentarii",
            'title_standardized': "In Platonis Rem publicam commentarii",
            'author_volume': "Proclus",
            'author_standardized': "Proclus",
            'edition': "1899",
            'editor': "Kroll, Wilhelm",
            "ISBN": "000000000"
        }
        try:
            werk = Work(**vals)
            session.add(werk)
            session.commit()
        except:
            raise
    return the_work


if __name__ == "__main__":
    main(12806686, 12807245)
