#!/usr/bin/env python
#coding:utf-8

#this is a set of functions for download and initial cracking of Lace texts
import pickle
#import re
from bs4 import BeautifulSoup
import requests
import os.path
#below to avoid UnicodeDecodeError 
import sys
reload(sys)
sys.setdefaultencoding('utf8')
#from pylev import classic_levenschtein
from fuzzywuzzy import fuzz
import sqlite3

def clean(word):
    '''
    If word ends with . or , 
    clean it
    '''
    word = word.strip()
    #badseeds = list(".,{}[]")
    #if 
    if word[-1] in ".,][()[{}":
        word = word[:-1]
    return word

def is_correct(word):
    '''Checks if the word can be found
    in our dictionary
    returns True if yes
    '''    
    #dictionary
    if word in [ "ὑπ.", "ὑπ", "Ὀλυμπιάς","Ὀλυμπιάς."]:
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
    #for probab_title in header_data['titles']:
        #print "make header:: ", line_text, probab_title, fuzz.ratio(line_text, probab_title)
    if fuzz.ratio(line_text, header_data['titles'][0])>fuzz.ratio(line_text, header_data['titles'][1]):
        best_title = header_data['titles'][0]
    else: 
        best_title = header_data['titles'][1]
    #if header_data['page_number']>350: #that value must be different for every volume of Niebuhr
    #    header_data['page_number']=+1
    if header_data['page_number']%2!=0:
        return '<p class="header"> <span class="pagetitle">%s</span> <span class="pagination right">%s</span> </p>' %(best_title, header_data['page_number'])
    else:
        return '<p class="header"> <span class="pagination left">%s</span> <span class="pagetitle">%s</span> </p>' %(header_data['page_number'], best_title)
       

def find_first_line(lines):
    '''Sometimes first line, which sould in Niebuhr's edition
    contain title of the work and page number
    is preceded by some junk
    like on page 277
    =therefore this function tries to find it '''
    score = []
    for line in lines:
        tex = "".join(x.text for x in line.findAll('span', 'ocr_word'))
        score.append([line, fuzz.ratio(tex, "CHRONICON")+fuzz.ratio(tex, "PASCHALE")])
    #    if any(x in "".join(x.text for x in line.findAll('span', 'ocr_word')) for x in ["ASCHAL","CHR","HRO","ONIC","PASC"]):
    line = [ x[0] for x in score if x[1]==max([y[1] for y in score])][0]
    #print "returning", line
    return line




def is_marginalia(text):
 
    if text in ['5','10','15','20']:
        return True
    if any(w in '1234567890' for w in text) and all(w in '1234567890{}[]()' for w in text):
        return True
    return False

def clean_text(text, page_number):
    '''Take html and clean it '''
    ret = []
    #text = initial_clean(text)
    soup = BeautifulSoup(text)
    #here we make header
    ocr_carea = soup.find('body')
    #if len(ocr_carea)>1:
    #    #print "double ocr_carea"
    #    ocr_carea = [xo for xo in ocr_carea if len(xo) == max([len(y) for y in ocr_carea])][0]
    #else:
    #    ocr_carea=ocr_carea[0]
    pis = ocr_carea.findAll('p')
    if len(pis[0].contents)==0:
        pis = pis[1:]
    first_p_lines = ocr_carea.findAll('span','ocr_line')
    header_data = {"page_number":page_number, 'titles':["CHRONICON","PASCHALE"]}
    likely_first_line = find_first_line(first_p_lines)
    first_p = make_header(likely_first_line,header_data)
    #ret.append(first_p)
    #end of header creation 
    counter = 1
    for p in pis[1:]:
        lines = p.findAll('span','ocr_line')
        for line in lines:
            del line['title'] 
            words = line.findAll('span', 'ocr_word')
            for word in words:
                del word['title']
                del word['class']
                del word['xml:lang']
                del word['data-lat-original']
                del word['bbox']
                # correct only greek words:
                # skip latin and punctuation mark
                if word.has_attr('lang') and word['lang']=="grc"\
                    and not word.has_attr('corr'): # last condition: corr may have been added if the word was recognized as continued from the previous line
                    if is_correct(word.text):
                        word["corr"]=1
                    #here we deal with situation where two words separated by white space are contained in one 
                    elif " " in word.text:
                        two_words = word.text.split(" ")
                        #deal with things like "word ]" or "word )"
                        if any([wr in "{}[]]()().,;" for wr in two_words]):
                            new_word = word.text.replace(" ","")
                            if is_correct(new_word):
                                word["corr"]=1
                            else:
                                word["corr"]=0
                        elif any([is_correct(wr) for wr in two_words]):
                            #step one: two words inside the tag replaced with first
                            word.string = two_words[0]
                            if is_correct(two_words[0]):
                                word["corr"]=1
                            else:
                                word["corr"]=0
                            #now add new tag
                            new_node = soup.new_tag("span")
                            new_node["lang"]="grc"
                            new_node.string = two_words[1]
                            if is_correct(two_words[1]):
                                new_node["corr"]=1
                            else:
                                new_node["corr"]=0
                            
                            word.replace_with(new_node)
                            new_node.insert_before(word)
                        else:
                            word["corr"]=0
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
                                word["half"]=1
                                word["full"]=joined_word
                                next_line_words[0]['corr']=1
                                next_line_words[0]['half']=2
                        except IndexError:
                            continue
                    else:
                        word["corr"]=0
                else:
                    if is_marginalia(word.text):# here we check if is pagination
                        word["class"]="side_pagination"
        #final stage: we add ids to every word
        
        #lines = p.findAll('span','ocr_line')
        for line in lines: 
            words = line.findAll('span')
            for word in words:
                word["id"]=counter
                counter=counter+1
        ret.append(p)
    # now, structure the text, keeping paragraphs, mark what is: i. greek text iii. apparatus criticus iii. Latin translation
    indexx = 0
    for index_of_p, p in enumerate(ret):
        number_of_words = len(p.findAll('span'))
        number_of_greek_words = len([wo for wo in p.findAll('span') if wo.has_attr('lang') and wo['lang']=="grc"])
        if number_of_greek_words*2 >= number_of_words:# if 70% of words are greek
            indexx = index_of_p+1

    final_ret = [first_p]+ret[:indexx]+['</span> <span class="latin_text">']+ret[indexx:]
    full_text =  '<div class="page">'+str(final_ret[0])+'<span class="greek_text">' + " ".join([str(x) for x in final_ret[1:]])+'</span></div>'
    #second round: remove greek language attribute from all words
    soup = BeautifulSoup(full_text)
    latin_text = soup.find('span', "latin_text")
    for line in  latin_text.findAll('span', 'ocr_line'): #[x for x in latin_text.findAll('span') if x.has_attr('lang') and x['lang']=="grc"]:
        for word in line.findAll("span"):
            if word.has_attr('lang'):
                del  word["lang"]
            if word.has_attr('corr'):
                del word["corr"]

    final_text = str(soup)
    return final_text




def main(r=range(4326744,4326745)):
    '''Fetch a range of pages, clean them and save as a file '''
    result = []
    for x in r: 
        link = "http://heml.mta.ca/lace/sidebysideview2/"+str(x)
        print link
        whole_page = requests.get(link)._content
        soup = BeautifulSoup(whole_page)
        image = soup.find(attrs={'id':'page_image'})
        image_url = 'http://heml.mta.ca'+image['src']
        link_to_iframe = 'http://heml.mta.ca'+soup.find(attrs={'id':'page_right'}).findChild('iframe')['src']
        v = requests.get(link_to_iframe)
        page_number = x-4326429
        #print v._content
        cleaned = clean_text(v._content, page_number) 
        '''
        record = { "title":"Chronicon Paschale",\
        "pagenumber":page_number
        "image_url":image_url,\
        'text':cleaned,\
        'notepad':cleaned,\
        }
        '''
        #return
        record =["Chronicon Paschale",page_number,image_url,cleaned,cleaned]
        result.append(record)
    conn =sqlite3.connect('/Users/QTF/Desktop/ManuTironis/testbase')
    c = conn.cursor()
    conn.text_factory = str
    try:
        c.execute('create table pages (title text, pagenumber integer, image_url text, page text, notepad text)')
    except:
        pass
    conn.commit()
    c.executemany("insert into pages values (?,?,?,?,?)", result)
    conn.commit()
    c.close()
    conn.close()
    
    return #result 

if __name__== "__main__":
    main()
#remember baby: dictionary comes from all words already corrected
# that is: words appearing as correct
