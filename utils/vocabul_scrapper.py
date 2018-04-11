#!/usr/bin/env python
# -*- coding: utf-8 -*-

# in nomine Patri
import requests
import psycopg2

from bs4 import BeautifulSoup, Tag

BADSEEDS = list('''?!//\\.,{}|[](){}[]]().,:;\"“”〈〈〉〉¹²⁴''')
BADSEEDS.append('\xb7')
BADSEEDS.append("'")

connect_manu = psycopg2.connect("dbname=manu_tironis user=quellen password=quellen")
manu_cursor = connect_manu.cursor()


def deamon_run():
    """
    Visit heml every week and scrap new words
    
    :return: 
    """
    # check latest
    # get page number of the last page
    # FIXME
    pass


def run_lola_run(alpha, omega):
    """
    :param int: alpha: beginning url
    :param int: omega: end url
    :return:
    """

    main_link = "http://heml.mta.ca/lace/sidebysideview2/"
    sublink = 'http://heml.mta.ca'
    for x in [p for p in range(alpha, omega)]:
        try:

            link = main_link + str(x)
            whole_page = requests.get(link)._content
            soup0 = BeautifulSoup(whole_page, "html.parser")
            iframe = soup0.find('iframe')
            iframe_link = iframe['src']
            full_link = sublink + iframe_link
            ze_page = requests.get(full_link)._content
            soup = BeautifulSoup(ze_page, "html.parser")
            words = soup.findAll('span', {'class': 'ocr_word'})

            for word in words:
                if word.has_attr('data-spellcheck-mode') and word['data-spellcheck-mode'] == "True":
                    if word.has_attr('data-selected-form'):
                        word_itself = word['data-selected-form']
                        if seems_to_be_greek(word_itself):
                            if is_fishy(word_itself):
                                continue
                            if is_polluted(word_itself):
                                word_itself = clean(word_itself)
                            if is_fishy(word_itself):
                                continue
                            if not check_if_exists(word_itself):
                                save_it(word_itself)
        except Exception as e:
            print("something went wrong: {}".format(e))
            raise e


def seems_to_be_greek(word):
    range_of_greek_letters = range(900, 988)
    for letter in word:
        if letter != ' ':
            if ord(letter) not in range_of_greek_letters:
                return False
    return True


def is_polluted(word):
    if any(letter in BADSEEDS for letter in word):
        return True
    return False


def is_fishy(word):
    alph = list('1234567890-qwertyuioplkjhgfdsazxcvbnm')
    if any(letter in alph for letter in word):
        return True
    if len(word) < 4:
        return True
    return False


def clean(word):
    '''
    If word ends with . or ,
    clean it
    '''
    word = word.strip()
    while len(word) > 0 and word[-1] in BADSEEDS:
        word = word[:-1]
    while len(word) > 0 and word[0] in BADSEEDS:
        word = word[1:]
    return word


def check_if_exists(word):
    try:
        query_str = '''select exists(select word from words where word='{}')'''.format(word)
        manu_cursor.execute(query_str)
        res = manu_cursor.fetchone()
        return res[0]
    except Exception as e:
        # "something went wrong: {}".format(e)
        connect_manu.rollback()
    return True


def save_it(word):
    """
    :param word:
    :return:
    """
    try:
        manu_cursor.execute("INSERT INTO words VALUES (%s)", (word,))
        connect_manu.commit()
        print('commited: {}'.format(word))
    except psycopg2.IntegrityError:
        print("INTEGRITY ERROR")
        connect_manu.rollback()
    except Exception as e:
        print("something went wrong: {}".format(e))
        connect_manu.rollback()


if __name__ == "__main__":
    run_lola_run(12806686, 12807245)
