import unittest
import auxilia


class AuxiliaTest(unittest.TestCase):
    def setUp(self):
        super(AuxiliaTest, self).setUp()
        self.pure_greek_word = 'προυπισχνουμένων'
        self.pure_latin_word = 'mentula'
        self.mixed_word = 'μeνtula'

    def test_all_letters_greek(self):
        result = auxilia.all_letters_greek(
            self.pure_greek_word)
        self.assertTrue(result)

    def test_all_letters_greek_false(self):
        result = auxilia.all_letters_greek(
            self.mixed_word
        )
        self.assertFalse(result)

    def test_all_letters_latin(self):
        result = auxilia.all_letters_latin(
            self.pure_latin_word)
        self.assertTrue(result)

    def test_all_letters_latin_false(self):
        result = auxilia.all_letters_latin(
            self.mixed_word)
        self.assertFalse(result)

    def test_some_letters_non_greek(self):
        result = auxilia.some_letters_non_greek(
            self.mixed_word)
        self.assertTrue(result)

    def test_some_letters_non_greek_false(self):
        result = auxilia.some_letters_non_greek(
            self.pure_greek_word)
        self.assertFalse(result)
