# get lines pertaining to appar crit
# later we will feed the AI with it
from ..model import Line, Page
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
from sqlalchemy import create_engine,

engine = create_engine('postgresql+psycopg2://quellen:quellen@localhost/manu_tironis')

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

all_pages = session.query(Page).all()
for page in all_pages:
    for line in page.lines:
        if line.is_last_of_greek_text_on_page:
            next_line = line.next_line()
            greek = ' '.join([t.token for t in line.tokens])
            apparatus = ' '.join([t.token for t in next_line.tokens])
