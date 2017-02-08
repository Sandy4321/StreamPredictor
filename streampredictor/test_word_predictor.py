from unittest import TestCase

from . import WordPredictor
from . import DataObtainer

training_text = 'cat hat mat bat sat in the barn'
words = training_text.split(' ')


class TestPatternOfPatterns(TestCase):

    def test_train_runs(self):
        wp = WordPredictor.WordPredictor()
        wp.train(words)
        self.assertTrue(True)

    def test_generates_sample(self):
        wp = WordPredictor.WordPredictor()
        wp.train(words)
        generated_text = wp.generate(5)
        self.assertGreater(len(generated_text.split(' ')), 5)


class TestDataObtainer(TestCase):
    def test_convert_word_2_id(self):
        test_words = ['aaa', 'bbb', 'ccc', 'aaa']
        seq, word2id, id2word = DataObtainer.convert_words_to_id(test_words)
        self.assertEqual([0,1,2,0], seq)
        for word in test_words:
            self.assertEqual(word, id2word[word2id[word]])