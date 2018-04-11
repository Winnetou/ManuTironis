# this one doesn't crawl the web, it just and only
# takes xml from
import os
import psycopg2
import uni_to_beta
import xml
import xmlrpc

connect_manu = psycopg2.connect("dbname=manu_tironis user=quellen password=quellen")
manu_cursor = connect_manu.cursor()


def get_raw_text():
    pass


def translate(raw_text):
    uni_to_beta.st(raw_text)
    pass


def get_trigrams(translated):
    """
    
    :param translated: str
    :return: 
    """
    tokens = translated.split()
    trigrams = []
    for index, word in enumerate(tokens[:-2]):
        trigram = " ".join(tokens[index], tokens[index + 1], tokens[index + 2])
        trigrams.append(trigram)
    # and now save /the planet:/ by calling bulk save
    # FIXME FINISH ME!!
    manu_cursor.executemany('insert into trigrams values (%s')


def main():
    for directory in os.listdir('here'):
        for subdir in directory:
            for file in subdir:
                if file.endswith("_gk.xml"):
                    xml = file.open.read()
                    raw_text = get_raw_text(xml)
                    translated = translate(raw_text)
                    get_trigrams(translated)
