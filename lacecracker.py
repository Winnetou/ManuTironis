#!/usr/bin/env python
#coding:utf-8
#

#set of functions for download and initial cracking of Lace texts
import pickle
#import re
from bs4 import BeautifulSoup
import requests
import os.path
#below to avoid UnicodeDecodeError 
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from pylev import classic_levenschtein
from fuzzywuzzy import fuzz
#glob_data = {'www':}

def give_link(number):
    beg = 'http://heml.mta.ca/lace/text/static/Texts/corpusscriptorum04nieb/2013-07-21-13-28_weidmann4_combined_hocr_output/corpusscriptorum04nieb_'
    num = str(number)#must be four chars, preceed by zeros if needed
    while len(num)<4:
        num = '0'+num
    link = beg+num+'.html'
    return link

def clean(word):
    '''
    If word ends with . or , 
    clean it
    '''
    word = word.strip()
    #badseeds = list(".,{}[]")
    #if 
    if word.endswith('.') or word.endswith(','):
        word = word[:-1]
    # if there is whitespace inside that word
    #FIXME
    return word

def is_correct(word):
    '''Checks if the word can be found
    in our dictionary
    returns True if yes
    '''    
    #dictionary
    if word in [ ".", ","]:
        return True
    pat = os.path.join(os.path.dirname(os.path.realpath('__file__')),'frequencies') #there must be a better way to do that
    f = open(pat)
    all_words = pickle.load(f)
    words = [unicode(w[0]) for w in all_words]

    if clean(word) in words:
        return True
    return False

def all_letters_latin(word):
    if all(letter.lower() in "qwertyuioplkjhgfdsazxcvbnm.," for letter in word):
        return True
    return False


def all_words_latin(words):
    '''take a line and check if it's all latin '''
    if not any(word.has_attr('lang') and word['lang']=="grc" for word in words)\
        and all(all_letters_latin(word.text) for word in words):
        return True
    return False


                
def make_header(line, header_data):
    '''Rather then crunching data from lousy ocr 
    use data provided by terrestrial inteleligence
    header_data is a dictionary
    contains offset - usually number of html document
    is by some offset higher or lower from page number
    and depending on work 
    page header maybe different on either even or odd number
    eg. CHRONICON and PASCHALE
    '''
    line_text = "".join(x.text for x in line.findAll('span', 'ocr_word'))
    for probab_title in header_data['titles']:
        print "make header:: ", line_text, probab_title, fuzz.ratio(line_text, probab_title)
    if fuzz.ratio(line_text, header_data['titles'][0])>fuzz.ratio(line_text, header_data['titles'][1]):
        best_title = header_data['titles'][0]
    else: 
        best_title = header_data['titles'][1]

    if header_data['page_number']>350: #that value must be different for every volume of Niebuhr
        header_data['page_number']=+1
    if header_data['page_number']%2==0:
        return '<p class="header"><span class="pagination">%s</span><span class="pagetitle">%s</span></p>' %(header_data['page_number'], best_title)
    else:
        return '<p class="header"><span class="pagetitle">%s</span><span class="pagination">%s</span></p>' %(best_title, header_data['page_number'])

def find_first_line(lines):
    '''Sometimes first line, which sould in Niebuhr's edition
    contain title of the work and page number
    is preceded by some junk
    like on page 277
    =therefore this function tries to find it '''
    score = []
    for index, line in enumerate(lines[:5]):
        tex = "".join(x.text for x in line.findAll('span', 'ocr_word'))
        score.append([index, line, fuzz.ratio(tex, "CHRONICON")+fuzz.ratio(tex, "PASCHALE")])
    #    if any(x in "".join(x.text for x in line.findAll('span', 'ocr_word')) for x in ["ASCHAL","CHR","HRO","ONIC","PASC"]):
    index, line = [ [x[0],x[1]] for x in score if x[2]==max([y[2] for y in score])][0]
    print "returning", index, line
    return line, index

def clean_text(text, x):
    '''Take html and clean it '''
    #TODO - something must be done with punctuation
    ret = []
    soup = BeautifulSoup(text)
    #span ocr_carea it the main content, it is divided into <p>
    # we need to keep <p> structure
    ocr_carea = soup.findAll('span','ocr_carea')
    if len(ocr_carea)>1:
        print "double ocr_carea"
        ocr_carea = [xo for xo in ocr_carea if len(xo) == max([len(y) for y in ocr_carea])][0]
    else:
        ocr_carea=ocr_carea[0]

    pis = ocr_carea.findAll('p')
    first_p_lines = pis[0].findAll('span','ocr_line')
    if len(first_p_lines)>1:
        print "double first_p_lines"
    header_data = {"page_number":x-16, 'titles':["CHRONICON","PASCHALE"]}
    likely_first_line, its_index = find_first_line(first_p_lines)
    first_p = make_header(likely_first_line,header_data)
    ret.append(first_p)
    for p in pis[1:]:
        lines = p.findAll('span','ocr_line')
        for line in lines:
            del line['bbox']
            del line['title']
            words = line.findAll('span', 'ocr_word')
            for word in words:
                del word['class']
                del word['title']
                del word['xml:lang']
                del word['data-lat-original']
                # correct only greek words:
                # skip latin and punctuation mark
                if word.has_attr('lang') and word['lang']=="grc"\
                    and not word.has_attr('corr'): # last condition: corr may have been added if the word was recognized as continued from the previous line
                    if is_correct(word.text):
                        word["corr"]=1
                    #here we deal with words continued in the next line of text
                    elif words[::-1].index(word)==0 and word.text.strip().endswith('-'): # if thats the last word in that line and continued in another
                        next_line_index = lines.index(line)+1 
                        try:
                            next_line = lines[next_line_index]
                            next_line_words = next_line.findAll('span', 'ocr_word')
                            first_word_next_line = next_line_words[0].text.strip()
                            joined_word = word.text.replace('-','').strip()+ first_word_next_line
                            #joined_word = clean(joined_word)
                            if is_correct(joined_word):
                                word["corr"]=1
                                next_line_words[0]['corr']=1
                        except IndexError:
                            #here we should find try find next page - if exists
                            # skipping first line
                            continue
                    else:
                        word["corr"]=0
            ret.append(p)
    full_text =  "\n".join([str(x) for x in ret])
    return full_text

def structure_text(text, data):
    '''This maybe applicable to Niebuhr's eidtion only
    Take page and divide it into four section:
    i. header (just use value provided, since we skipped first line in clean text function)
    ii. greek text
    iii. apparatus criticus
    iv. Latin translation
    but add metadata first
    '''
    htmlheader = '<div class="page" '
    for k in data.iterkeys():
        val = str(k)+'="'+ str(data[k])+'" '
        htmlheader = htmlheader + val
    htmlheader = htmlheader +'> '
    '''
    body = "<span></span>"
    soup = BeautifulSoup(text)
    lines = soup.findAll('span','ocr_line')
    # here, very simple logic: if most of the words are greek
    #its greek

    for index, item in enumerate(lines[:-1]):
        words  = item.findAll('span')
        next_line_words = lines[index+1].findAll('span')
        #if all(word.has_attr('lang') and word['lang']=="grc" for word in words) and all() 
        #TO JEST ZLE NIE JESTE DOBRZE OJ NIE NIE
    full_text = htmlheader + body+' </div>'
    '''
    full_text = htmlheader + text+' </div>'
    return full_text


def main(r=range(276,280)):
    '''Fetch a range of pages, clean them and save as a file '''

    print  '''Finish unfinished: 1.Divide page into header, greek text, apparatus criticus and Latin translation 2. Try better with word being continued in the nexte line;'''

    pat = os.path.join(os.path.dirname(os.path.realpath('__file__')),'result_2')
    try:
        os.remove(pat)
    except OSError:
        pass
    result_file = open(pat, 'a')
    
    for x in r:
        link = give_link(x)
        v = requests.get(link)
        print "Fetched ", x
        b=v._content
        k = clean_text(b, x)
        data = {
                "origin":link,
                "lacetitle": "Niebuhr, Barthold Georg, 1776-1831 et al. (1828). Corpus scriptorum historiae byzantinae. Editio emendatior et copiosior. consilio B.G. Niebuhrii 4",
                "title": "Chronicon Paschale" 
                }
            
        kon = structure_text(k, data)
        result_file.write(kon)
        result_file.flush()
    result_file.close()