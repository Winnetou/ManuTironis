from .. import suggest
from unittest import TestCase, mock
import re


@mock.patch('suggest.words_backend._get_smlar_len_words')
class SuggestTest(TestCase):
    def setUp(self, mocked_words):
        super(SuggestTest, self).setUp()
        self.mocked_words = ['καθότι', 'θρόνος', '', '', '', '', '', ]
        mocked_words.return_value = self.mocked_words

    def test_replace_non_greek_with_dot(self):
        '''          
        '''
        incorrect = 'θρό^ος'

    # @mock.patch('suggest.re')
    def test_find_by_re_substitution(self,
                                     mocked_words, mocked_re):
        '''
        Don't mock re, just check it returns θρόνος
        '''
        # mocked_re.match.return_value

    def test_get_similar_by_levens(self, mocked_words):
        '''
        '''

    def test_translate_latin_chars(self, mocked_words):
        '''
        '''
        incorrect = 'tovTo'
        corrected = suggest.translate_latin_chars(incorrect)
        expected = "?"
        self.assertEqual(corrected, expected)
