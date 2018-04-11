# TODO FINISH THE FOLLOWING
# 1. cutting off punctuation marks - also, when word is in brackets or square brackets
import sqlalchemy as sa
from uuid import uuid4
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData
from datetime import datetime
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine('postgresql+psycopg2://quellen:quellen@localhost/manu_tironis')

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

# Base.metadata.create_all(engine) # <--- that command creates tables on the db
meta = MetaData(bind=engine)

Base = declarative_base(bind=engine, metadata=meta)


# ContentTypesList = ["greek", "english", "latin", "apparatus",]
# TODO - what shall be done with adjacent punctuation marks?
class Work(Base):
    """
    Represents a Work
    """
    __tablename__ = 'work'
    __table_args__ = (sa.schema.UniqueConstraint('author_standardized', 'title_standardized', name='author_title'),
                      )
    id = sa.Column(postgresql.UUID(as_uuid=True), primary_key=True)
    author_standardized = sa.Column(sa.String(256),
                                    nullable=False,
                                    doc="Standardized name of the author: eg Aristoteles Phil instaed of Aristotle")
    author_volume = sa.Column(sa.String(256),
                              nullable=False,
                              doc="Author as printed in the book")
    edition = sa.Column(sa.String(256),
                        nullable=False,
                        doc="Edition details: year, place, etc")
    editor = sa.Column(sa.String(128),
                       nullable=False,
                       doc="Name of the editor")
    ISBN = sa.Column(sa.String(128),
                     nullable=True,
                     doc="ISBN of the original edition")
    pages = relationship("Page", back_populates="work", order_by="Page.page_number")
    title_standardized = sa.Column(sa.String(512),
                                   nullable=False,
                                   doc="Title as usually cited eg. De anima instead of Libri xx de anima Aristotelis")
    title_volume = sa.Column(sa.String(512),
                             nullable=False,
                             doc="Title as printed in the book")


class Page(Base):
    """
    DONE
    """
    __tablename__ = 'page'
    id = sa.Column(postgresql.UUID(as_uuid=True), primary_key=True)
    number = sa.Column(sa.Integer,
                       doc="Page number - since we skip blank pages it is different from page_number")
    header = sa.Column(sa.String(1024),
                       nullable=True,
                       doc="Header of a page")
    page_number_on_top = sa.Column(sa.Boolean,
                                   nullable=True,
                                   doc="Does the site have its number on the top. False== it is on the bottom")
    page_number = sa.Column(sa.Integer,
                            doc="Ordinal number of the line of text on the page (to be displayed in html)")
    page_scan_url = sa.Column(sa.String(2048),
                              nullable=True,
                              doc="Url of the scan")
    external_page_scan_url = sa.Column(sa.String(2048),
                                       nullable=True,
                                       doc="If there is external url of the scan, we store it here")
    work_id = sa.Column(postgresql.UUID(as_uuid=True), sa.ForeignKey("work.id"))
    work = relationship("Work", back_populates="pages")
    lines = relationship("Line", back_populates="page", order_by="Line.number")

    @property
    def is_left(self):
        """
        :return: bool
        """
        if self.page_number % 2 == 0:
            return True
        return False

    @property
    def _header_with_markup(self):
        if self.header is None:
            return ""
        return '<span class="pagetitle">' + self.header + "</span>"

    @property
    def _pagenumber_with_markup(self):
        _page_number = str(self.page_number)
        if self.is_left:
            return '<span class="pagination left">' + _page_number + '</span>'
        return '<span class="pagination right">' + _page_number + '</span>'

    @property
    def _get_full_markedup_header(self):
        """ Gets header with or w/o page number"""
        begin, end = '<p class="header">', "</p>"
        if self.page_number_on_top:
            if self.is_left:
                return begin + self._pagenumber_with_markup + self._header_with_markup + end
            return begin + self._header_with_markup + self._pagenumber_with_markup + end
        return begin + self._header_with_markup + end

    @property
    def _get_full_markedup_footer(self):
        begin, end = '<p class="footer">', "</p>"
        return begin + self._pagenumber_with_markup + end

    @property
    def _get_full_markedup_content(self):
        """
        Iterates over lines of a page and joins them
        :return:
        """
        all_lines = [line.with_markup for line in self.lines]
        return " ".join(all_lines)

    @property
    def full_markedup(self):
        content = self._get_full_markedup_header + self._get_full_markedup_content
        # do we have to append a footer ?
        if not self.page_number_on_top:
            content += self._get_full_markedup_footer
        template = '<div id="{}" class="page"> {} </div>'
        full_page = template.format(self.id, content)
        return full_page

    def next_page(self):
        """ Check if next page exists, return it
        :rtype model.Page || None
        """
        # TODO TEST ME
        try:
            indexx = self.work.pages.index(self)
            pg = self.work.pages[indexx + 1]
            return pg
        except IndexError:
            return None

    def previous_page(self):
        """ Check if previous page exists, return it
        :rtype model.Page || None
        """
        indexx = self.work.pages.index(self)
        if indexx == 0:
            return None

        pg = self.work.pages[indexx - 1]
        return pg

    @property
    def is_first_in_work(self):
        return True if self.previous_page() is None else False

    @property
    def is_last_in_work(self):
        return True if self.next_page() is None else False

    @property
    def dictified(self):
        """ 
        :return: dict with all the data FE needs to have
        :rtype: dict
        """
        page_as_dickt = {
            "id": self.id,
            "title": self.work.title_volume,
            "pagenumber": self.page_number,
            "notepad": self.full_markedup,
            "image_url": self.page_scan_url,
        }
        next_page = self.next_page()
        previous_page = self.previous_page()
        if next_page is not None:
            page_as_dickt["next_page"] = next_page.page_number
        if previous_page:
            page_as_dickt["prev_page"] = previous_page.page_number
        return page_as_dickt


class Line(Base):
    """
    TODOs:
    1. Nice to have a method to tell if a token is first/last in line
    """
    __tablename__ = 'line'
    id = sa.Column(postgresql.UUID(as_uuid=True), primary_key=True)
    number = sa.Column(sa.Integer,
                       doc="Line number")
    content = sa.Column(
        sa.String(64), nullable=False, doc="Content type: greek, english, latin etc"
    )
    page_id = sa.Column(postgresql.UUID(as_uuid=True), sa.ForeignKey("page.id"))
    page = relationship("Page", back_populates="lines")

    tokens = relationship("Token", back_populates="line", order_by="Token.number")

    @property
    def is_first_on_page(self):
        return True if self.page.lines[0] == self else False

    @property
    def is_last_on_page(self):
        return True if self.page.lines[-1] == self else False

    @property
    def is_last_of_greek_text_on_page(self):
        """
        True if this is the last line of the greek body of text
        - either because later we have latin translation or
        apparatus, or because this is simply last line on the page
        :return: 
        """
        if self.is_last_on_page:
            return False
        self_index = self.page.lines.index(self)
        next_line = self.page.lines[self_index + 1]
        return True if next_line.content != "greek_text" else False

    @property
    def with_markup(self):
        line_tokens = [token for token in self.tokens if not token.deleted]
        sorted_line_tokens = sorted(line_tokens, key=lambda t: t.number)
        tokenz = []
        for t in sorted_line_tokens:
            tokenz.append(t.with_markup)
        tokenstring = " ".join(tokenz)
        template = '<span id="{}" number="{}" class="line {}"> {} </span>'
        full = template.format(self.id, self.number, self.content, tokenstring)
        return full

    def next_line(self):
        """ Check if next line exists, return it
        :rtype model.Line || None
        """
        indexx_plus_one = self.page.lines.index(self) + 1
        if any(line for line in self.page.lines if self.page.lines.index(line) == indexx_plus_one + 1):
            next_line = self.page.lines[indexx_plus_one]
            if next_line.content == self.content:
                return next_line

        next_page = self.page.next_page()
        if next_page:
            next_line = next_page.lines[0]
            if next_line.content == self.content:
                return next_line
        # if this is the last line ever return None. Though it is foolish
        return None


class Token(Base):
    __tablename__ = 'token'
    id = sa.Column(postgresql.UUID(as_uuid=True), primary_key=True)
    deleted = sa.Column(sa.Boolean,
                        nullable=False,
                        default=False,
                        doc="Boolean flag when set to TRUE means that word was deleted")
    number = sa.Column(sa.Integer,
                       doc="Token Number")
    line_id = sa.Column(postgresql.UUID(as_uuid=True), sa.ForeignKey('line.id'))
    line = relationship("Line", back_populates="tokens")
    token = sa.Column(sa.Unicode(256),
                      nullable=False,
                      doc="The word itself - even if not full and with punct marks")
    is_greek = sa.Column(sa.Boolean,
                         nullable=False,
                         default=False,
                         doc="Boolean flag when set to TRUE means that word is part of the greek text")
    is_greek_numeral = sa.Column(sa.Boolean,
                                 nullable=False,
                                 default=False,
                                 doc="TRUE means that word is a greek numeral")
    is_latin_numeral = sa.Column(sa.Boolean,
                                 nullable=False,
                                 default=False,
                                 doc="TRUE means that word is a latin numeral")
    is_arabic_numeral = sa.Column(sa.Boolean,
                                  nullable=False,
                                  default=False,
                                  doc="TRUE means that word is arabic numeral")
    is_side_pagination = sa.Column(sa.Boolean,
                                   nullable=False,
                                   default=False,
                                   doc="TRUE means that word is side pagination")
    is_greek_punctuation = sa.Column(sa.Boolean,
                                     nullable=False,
                                     default=False,
                                     doc="TRUE means that word is greek punctuation")
    is_latin_punctuation = sa.Column(sa.Boolean,
                                     nullable=False,
                                     default=False,
                                     doc="TRUE means that word is latin_punctuation")
    # FIXME - put constrain on the field below, it can be only 1 or 2
    half = sa.Column(sa.Integer,
                     nullable=True,
                     doc="Which halt of the word is it - 1 or 2")
    full = sa.Column(sa.String(1024),
                     nullable=True,
                     doc="The full word if the token is only a half")

    is_correct = sa.Column(sa.Boolean,
                           nullable=False,
                           default=False,
                           doc="Boolean flag when set to TRUE mean this is a correct reading of a token printed. It can be greek, latin numeral, punctuation")

    '''
    @property
    def cleaned_token(self):
        # TODO FINISH ME
        BADSEEDS = list(".,{}[](){}[]]().,;\"\'")

        def _it_is_punctuation(t):
            return True if all(el in BADSEEDS for el in t) else False

        def _cleaned(word):
            word = word.strip()
            while len(word) > 0 and word[-1] in BADSEEDS:
                word = word[:-1]
            while len(word) > 0 and word[0] in BADSEEDS:
                word = word[1:]
            return word

        def _it_is_in_brackets(word):
            if word[0] == '(' and word[-1] == ')':
                return True
            if word[0] == '[' and word[-1] == ']':

        # if it already is a punctuation mark and we know it
        if _it_is_punctuation(self.token):
            return self.token
        else:
            return _cleaned(self.token)
    '''

    @property
    def is_first_in_line(self):
        """This is needed to better tell which tokens are 
        side pagination and which are words """
        line_tokens = [token for token in self.line.tokens if not token.deleted]
        lowest = min(x.number for x in self.line.tokens)
        return True if self.number == lowest else False

    @property
    def is_last_in_line(self):
        """
        Token is last in line if its attr `number` is equal to the higest 
        :return: bool
        """
        line_tokens = [token for token in self.line.tokens if not token.deleted]
        highest = max(x.number for x in self.line.tokens)
        return True if self.number == highest else False

    @property
    def with_markup(self):
        markup_attrs = {'id': str(self.id), }
        if self.is_greek:
            markup_attrs['lang'] = 'grc'
            markup_attrs['corr'] = str(int(self.is_correct))
        if self.full is not None:
            markup_attrs['full'] = self.full
        if self.half is not None:
            markup_attrs['half'] = str(self.half)
        if self.is_side_pagination:
            if self.is_first_in_line:
                markup_attrs['class'] = "side_pagination left"
            elif self.is_last_in_line:
                markup_attrs['class'] = "side_pagination right"
        markup = ' '
        for key, val in markup_attrs.items():
            endcoded_key, endcoded_val = key, val
            pair = '{}="{}" '.format(endcoded_key, endcoded_val)
            markup += pair
        marked_up = "<span" + markup + ">" + self.token + "</span>"

        return marked_up

    def get_next_token(self):
        """
        This is helpful when you need to decide about:
        1. joining halves
        When it is a last token in non-last line, it returns token from 
        the next line.
        If this is the last token on the page in the main body of text
        then we look for next page
        :return: 
        """
        if not self.is_last_in_line:
            # simply get the next token
            indexx = self.line.tokens.index(self)
            next_token = self.line.tokens[indexx + 1]
            # FIXME !
            if next_token.is_side_pagination:
                raise ArmaggedonIsComing


        elif self.is_last_in_line:
            next_line = self.line.next_line()
            if next_line:
                next_token = next_line.tokens[0]
        return next_token


class Correction(Base):
    """
    DONE
    """
    __tablename__ = 'correction'

    id = sa.Column(postgresql.UUID(as_uuid=True), primary_key=True)
    # note - no foreign keys!
    token_affected = sa.Column(postgresql.UUID(as_uuid=True))
    date = sa.Column(sa.DateTime, default=datetime.now)
    before = sa.Column(sa.Unicode(256),
                       nullable=False,
                       doc="Token before it was corrected")
    after = sa.Column(sa.Unicode(256),
                      nullable=False,
                      doc="Token after it was corrected")
    source = sa.Column(sa.Unicode(256),
                       nullable=True,
                       doc="How the correction was made: man or machine?")
    rolled_back = sa.Column(sa.Boolean,
                            nullable=False,
                            default=False,
                            doc="TRUE means it was rolled back")


class ArmaggedonIsComing(Exception):
    """
    Tara ra dum dum pass
    """
    pass
