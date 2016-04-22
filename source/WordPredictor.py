import numpy as np

import FileManager
import Generalizer
import PopManager


class WordPredictor:
    """
    Creates language model by training on given words and then generating sample words or
    calculating perplexity for test words.
    """
    def __init__(self, pm=None):
        if pm:
            self.pop_manager = pm
        else:
            self.pop_manager = PopManager.PopManager()
        self.file_manager = FileManager.FileManager(self.pop_manager)
        self.generalizer = Generalizer.Generalizer(self.pop_manager.patterns_collection,
                                                   self.pop_manager.feed_strength_gain)
        print self.pop_manager.stats()

    def train(self, training_words):
        self.pop_manager.train_token(training_words)

    def generate(self, sample_length):
        self.pop_manager.generate_words(sample_length)
