import unittest
from unittest import mock


@mock.patch('app.shallow_backend')
class AppTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_scriptorium(self, patched_be):
        """ """
        patched_be.get_just_titles.return_value =
        pass

    def test_tiro(self, patched_be):
        """ """
        patched_be.get_page.return_value =
        pass

    @mock.patch('app.suggest')
    def test_suggest(self, _, patched_suggest):
        """ """
        sugg = {'bam': 'bam', "pam": 'pam'}
        patched_suggest.smart_suggest.return_value = sugg
        pass

    def test_update(self, patched_be):
        """ """
        patched_be.save_corrected.return_value =

    @mock.patch('app.')
    def test_divide(self, patched_be):
        """ """
        patched_be.divide_word.return_value =

        pass

    def test_join(self, patched_be):
        """ """
        patched_be.join_word_with_next.return_value =

    def test_set_correct(self, patched_be):
        """ """
        patched_be.set_correct.return_value =

    def test_setincorrect(self, patched_be):
        """ """
        patched_be.set_incorrect.return_value =

    def test_setpagination(self, patched_be):
        """ """
        patched_be.set_pagination.return_value =

    def test_remove(self, patched_be):
        """ """
        patched_be.remove.return_value =

    @mock.patch('app.')
    def test_get_corrections(self, patched_be):
        """ """
        patched_be.get_corrections.return_value =

    @mock.patch('app.')
    def test_rollback(self, patched_be):
        """ """
        patched_be.roll_back.return_value =
