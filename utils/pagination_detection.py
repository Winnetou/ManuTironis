#######################################
### FEW SCRIPTS TO BE RUN ONLY ONCE ###
#######################################

from model import Token, session


def pagination_detection():
    """
    Detect tokens that are side pagination
    :return: 
    """
    correct_number = {
        '5': '5', '10': '10', '1o': '10', '15': '15', '20': '20',
        '2o': '20', '30': '20', '3o': '20',
        '2O': '20', '1O': '10', 'O': '10', '2': '20',
        "2Ο": '20',
    }
    number_pagin = ('10', '1O', '1o', '15', '5', '20', '2O', '2o', '30', '3o', 'O', '2')
    wrong_ten = '1' + chr(927)
    wrong_twenty = '2' + chr(927)
    number_pagin = (wrong_ten, wrong_twenty, '10', '1O', '1o', '15', '5', '20', '2O', '2o', '30', '3o', 'O', '2')
    typisch = []

    # first round
    tkns = session.query(Token).filter(Token.deleted == False).filter(Token.number == 1).all()
    for tokn in tkns:
        if tokn.token in typisch:
            if tokn.line.line_number in [5, 10, 15, 20]:
                if tokn.line.page.is_odd:
                    pass
    return
