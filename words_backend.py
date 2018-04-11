# here we talk to table words - get them, check they exists, etc
import psycopg2

conn = psycopg2.connect("dbname=manu_tironis user=quellen password=quellen")
cursor = conn.cursor()


def get_smlar_len_words(incorrect):
    """
    :return: all words of len close to len(incorrect).
    """
    ln = len(incorrect)
    cursor.execute('''SELECT word FROM words WHERE char_length(WORD)>%s AND char_length(WORD)<%s''', (ln - 1, ln + 1))
    c = cursor.fetchall()
    words = []
    for sublist in c:
        for element in sublist:
            words.append(element)
    return words


def word_exists_in_dictionary(word):
    try:
        query_str = '''select exists(select word from words where word='{}')'''.format(word)
        cursor.execute(query_str)
        res = cursor.fetchone()
        return res[0]
    except:
        conn.rollback()
        return False


def save_single_word(word):
    """
    Saves a word to the database
    if it is not there yet
    """
    word = clean(word)
    # FIXME
    # there must be a way to do that in smarter way on posgtres
    # maybe upsert ?
    # TODO - what shall we do about uppercase?

    try:
        exists_query = "SELECT EXISTS (SELECT word from words WHERE word = %s)"
        cursor.execute(exists_query, (word,))
        if cursor.fetchone()[0]:
            return
        insert_command = "INSERT INTO words (word) VALUES (%s)"
        cursor.execute(insert_command, (word,))
        conn.commit()
    except:
        conn.rollback()
        raise
