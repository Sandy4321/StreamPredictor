from unittest import TestCase

from . import WordPredictor

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
