#coding:utf-8
#set of functions for initial text preparation

def find_apparatus(page):
    '''Start from the bottom line
    and check where greek text ends
    and apparatus criticus starts
    '''
    return line_number


def join_word():
    '''
    Whenever a word on the end of a line
    is continued in another line
    try to join it and check
    '''
    # first, attempt to find all lines ending with -
    for line in page[:-1]: #we do not get to the final line, because its continued on another page
        line = line.strip()
        if line.endswith('-'):
            last_word = line.split()[-1]
            next_line = page[page.inex(line)+1].strip()
            first_word = next_line.split()[0]

def add_unknown_word(word):
    '''
    Here we add new word to the set 
    of accepted forms
    '''
    accepted_words = 
    if word in accepted_words:
        return
    accepted_words.add(word)


def add_correction(incorrect_ocr, correct_form, corpus, classifier):
    """
    : Corrupted form was corrected by the user
    : check if the same incorrect form can be found in that work
    : if that's the case, 
    : save both forms - the corrected as 'suggested'
    : also, information about OCR classifier used and the corpus
    : may be of importance
    """
    #TODO
    #first check if it is already there
    pass

#XXXX Here set of functions to work with text

def is_corrupted(word):
    '''
    Here we try to guess
    if the word is OCR-ed correctly
    or incorrectly
    '''
    if any(letter in 'qwertyuioplkjhgfdsazxcvbnm0987654321()[]{}<>,.?!@#$%^&*w' for letter in word.lower()):
        return True
    if word not in lexicon:
        return True
    return False

def maybe_its_a_numeral(word):
    """
    This function 
    is to help with greek numerals
    They wont be inlcuded in the dictionary
    """
    pass

def is_proper_name(word):
    '''
    For text processing purposes in the future we want to know
    which words represent proper names
    to add html attribute proper="1" or "0" 
    '''
    all_proper_names = FIXME
    if word in all_proper_names:
        return True
    return False

def try_regular_expression(word):
    ''' 
    Let's say we have corrupted word
    where one greek letter was mistaken for a latin letter
    eg. Fασιλεῦ
    then replace that latin letter with wildcard in re: "."
    and using regular expressions
    find matches in the lexicon
    this should be faster and more reliable than Levenshtein
    '''
    similar_words=[]
    for letter in word:
        if letter.lower() in 'qwertyuioplkjhgfdsazxcvbnm0987654321,.;[]()_-?/\\|':
            word.replace(letter, ".{1}")
            # FINISH ME FIX ME TODO
            # itert 


    return similar_words

def find_similar_trigram(trigram, text):
    '''We have: word_1 corrupted_word_2 word_3
    find  a trigram where
    word_1 word_2 word_3
    and word_2 has as small 
    lev distance to corrupted_word_2
    as possible'''
    proposed = []

    for element in get_trigrams(text):
        if element.split(' ')[0] == trigram.split(' ')[0] and element.split(' ')[2] == trigram.split(' ')[2]:
        #here we check levenstein distance between middle word in the trigram
            if lev_distance(element.split(' ')[1], trigram.split(' ')[1]) > 0.8:
                proposed.append(element)
    return proposed


    
def get_trigrams(text):
    """
    Get a text, which is only partially cleaned
    find all trigrams - only with clean words 
    """
    trigrams = []
    # FIRST, words will be a list of all words with tags
    # use BeautifulSoup for that 
    words = 
    # item is 
    for index, word in enumerate(words):
        if word["corr"]==1 and words[index+1]["corr"]==1 and words[index+2]["corr"]==1:
            trigram = word.text+" "+words[index+1].text+' '+words[index+2].text
            trigrams.append(trigram)
    return trigrams




def lev_distance():
    ''' Levenshtein distance '''
    pass

