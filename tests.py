from unittest import TestCase
import NgramBank


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
        self.assertFalse(bank_sample.in_bank(ngram_sample))
        bank_sample.add_to_bank_string('test')
        self.assertTrue(bank_sample.in_bank(ngram_sample))

    def add_to_bank_existing_increases_strength_test(self):
        bank_sample = NgramBank.BankNgram()
        bank_sample.add_to_bank_string('test')
        bank_sample.add_to_bank_string('test2')
        first_strength = bank_sample.bank['test2'].strength
        bank_sample.add_to_bank_string('test2')
        second_strength = bank_sample.bank['test2'].strength
        self.assertTrue(second_strength > first_strength)
