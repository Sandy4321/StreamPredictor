from unittest import TestCase
from . import NgramBank


class TestNgram(TestCase):
    def init_test(self):
        sample = NgramBank.Ngram('test')
        self.assertEqual(sample.age, 0)
        self.assertEqual(sample.length, 4)

    def age_test(self):
        sample = NgramBank.Ngram('test')
        old_age = sample.age
        old_strength = sample.strength
        sample.decay()
        self.assertEqual(sample.age, old_age + 1)
        self.assertEqual(sample.strength, old_strength - 1)


class TestBankNgram(TestCase):
    def add_to_bank_new_test(self):
        bank_sample = NgramBank.BankNgram()
        ngram_sample = NgramBank.Ngram('test')
        self.assertFalse(bank_sample.ngram_in_bank(ngram_sample))
        bank_sample.add_to_bank_string('test')
        self.assertTrue(bank_sample.ngram_in_bank(ngram_sample))

    def add_to_bank_existing_increases_strength_test(self):
        bank_sample = NgramBank.BankNgram()
        bank_sample.add_to_bank_string('test')
        bank_sample.add_to_bank_string('test2')
        first_strength = bank_sample.bank['test2'].strength
        bank_sample.add_to_bank_string('test2')
        second_strength = bank_sample.bank['test2'].strength
        self.assertTrue(second_strength > first_strength)

    def create_ngrams_test(self):
        bank_sample = NgramBank.BankNgram()
        bank_sample.current_stream = ['a','b','c']
        list_ngrams = bank_sample.create_ngrams_strings('d')
        strings = [i for i in list_ngrams]
        self.assertTrue('dab' in strings)
        self.assertTrue('da' in strings)
        self.assertTrue('d' in strings)

    def cull_test(self):
        bank_sample = NgramBank.BankNgram()
        bank_sample.add_to_bank_string('a')
        bank_sample.cull()
        self.assertTrue('a' in bank_sample.bank)
        for i in range(NgramBank.starting_ngram_strength):
            bank_sample.decay()
        bank_sample.cull()
        self.assertTrue('a' in bank_sample.bank)
        for i in range(1):
            bank_sample.decay()
        bank_sample.cull()
        self.assertFalse('a' in bank_sample.bank)

    def check_maturation_test(self):
        bank_sample = NgramBank.BankNgram()
        bank_sample.add_to_bank_string('a')
        bank_sample.check_maturation()
        self.assertFalse(bank_sample.bank['a'].matured)
        for i in range(NgramBank.maturity_age):
            bank_sample.decay()
        bank_sample.check_maturation()
        self.assertFalse(bank_sample.bank['a'].matured)
        bank_sample.decay()
        bank_sample.check_maturation()
        self.assertTrue(bank_sample.bank['a'].matured)

    def create_ngrams_short_long_test(self):
        bank_sample = NgramBank.BankNgram()
        bank_sample.current_stream = ['a','b','c']
        list_ngrams = bank_sample.create_ngrams_strings('d')
        self.assertEqual(4,len(bank_sample.current_stream))
        bank_sample.current_stream = list('01234')
        self.assertEqual(NgramBank.max_length_ngram, len(bank_sample.current_stream))
        list_ngrams = bank_sample.create_ngrams_strings('z')
        self.assertEqual(NgramBank.max_length_ngram, len(bank_sample.current_stream))




