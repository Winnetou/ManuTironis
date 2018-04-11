def all_letters_greek(word):
    """
    given word, check if all letters are greek
    :return: 
    """
    range_of_greek_letters = range(900, 988)
    for letter in word:
        if letter != ' ':
            if ord(letter) not in range_of_greek_letters:
                return False
    return True


def all_letters_latin(word):
    """
    given word, check if all letters are latin
    :return: 
    """
    range_of_latin_letters = range(0, 126)
    if any(ord(letter) not in range_of_latin_letters for letter in word):
        return False
    return True


def some_letters_non_greek(word):
    """
    True only if 1 or 2 letters are not greek and the string is longer > 4
    """
    if any(ord(l) not in range(900, 988) for l in word):
        return True
    return False
