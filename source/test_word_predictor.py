import os
from unittest import TestCase

import DataObtainer
from Pop import Pop
import WordPredictor

training_text = 'cat hat mat bat sat in the barn'


class TestPatternOfPatterns(TestCase):

    def test_train_runs(self):
        wp = WordPredictor.WordPredictor()
        wp.train(training_text)
        self.assertTrue(True)

    def test_generates_sample(self):
        wp = WordPredictor.WordPredictor()
        wp.train(training_text)
        sample_words = wp.generate(5)
        self.assertEqual(len(sample_words), 5)
