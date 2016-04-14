import numpy as np

from PopManager import PopManager
from FileManager import FileManager
from Generalizer import Generalizer
import MainFunctions


class StreamPredictor:
    def __init__(self, pm=None):
        if pm:
            self.pop_manager = pm
        else:
            self.pop_manager = PopManager()
        self.file_manager = FileManager(self.pop_manager)
        self.generalizer = Generalizer(self.pop_manager.patterns_collection, self.pop_manager.feed_strength_gain)

    def train(self, string, generalize=False):
        maximum_pattern_length = self.pop_manager.maximum_pattern_length
        input_length = self.pop_manager.setup_train(string)
        previous_pop = self.pop_manager.patterns_collection[string[0]]
        i = 1
        while i < input_length:
            current_pop = self.pop_manager.find_next_pattern(string[i:i + maximum_pattern_length])
            self.pop_manager.join_pattern(previous_pop, current_pop, found_pattern_feed_ratio=1)
            previous_pop = current_pop
            i += len(current_pop.unrolled_pattern)
            if i % 1000 == 0 and i > self.pop_manager.feed_strength_gain:
                # Refactor, adopt stronger children, as long as one's unrolled pattern is same.
                self.pop_manager.refactor()
                self.pop_manager.cull(0)
        self.pop_manager.refactor()
        if generalize:
            self.generalizer.generalize()
        self.pop_manager.cull(0)
        return self.pop_manager.patterns_collection

    def generate_stream(self, word_length, seed=None):
        print 'Generating stream with word count = ', word_length
        current_pop = np.random.choice(self.pop_manager.patterns_collection.values()) \
            if seed is None or '' else self.pop_manager.find_next_pattern(seed)
        current_word = current_pop.unrolled_pattern
        generated_output = current_word
        for i in range(word_length):
            next_word = self.pop_manager.predict_next_word(generated_output)
            if next_word == '':
                next_word = np.random.choice([pop.unrolled_pattern
                                              for key, pop in self.pop_manager.patterns_collection.iteritems()])
            generated_output += next_word
        return generated_output


if __name__ == '__main__':
    MainFunctions.sanity_check_run()
