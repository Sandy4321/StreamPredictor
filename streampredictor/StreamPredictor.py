from . import FileManager
from . import Generalizer
from . import PopManager
import random


class StreamPredictor:
    def __init__(self, pm=None):
        if pm:
            self.pop_manager = pm
        else:
            self.pop_manager = PopManager.PopManager()
        self.file_manager = FileManager.FileManager(self.pop_manager)
        self.generalizer = Generalizer.Generalizer(self.pop_manager.patterns_collection,
                                                   self.pop_manager.feed_strength_gain)
        print(self.pop_manager.stats())

    def train_characters(self, string, generalize=False):
        maximum_pattern_length = self.pop_manager.maximum_pattern_length
        input_length = self.pop_manager.setup_train(string)
        previous_pop = self.pop_manager.patterns_collection[string[0]]
        i = 1
        while i < input_length:
            current_pop = self.pop_manager.find_next_pattern(string[i:i + maximum_pattern_length])
            self.pop_manager.join_pattern(previous_pop, current_pop, found_pattern_feed_ratio=1)
            previous_pop = current_pop
            self.pop_manager.cull(0)
            i += len(current_pop.unrolled_pattern)
            if i % 1000 == 0 and i > self.pop_manager.feed_strength_gain:
                # Refactor, adopt stronger children, as long as one's unrolled pattern is same.
                self.pop_manager.refactor()
        self.pop_manager.refactor()
        if generalize:
            self.generalizer.generalize()
        self.pop_manager.cull(0)
        return self.pop_manager.patterns_collection

    def generate_stream(self, word_length, seed=None):
        print('Generating stream with word count = ', word_length)
        current_pop = random.choice(list(self.pop_manager.patterns_collection.values())) \
            if seed is None or '' else self.pop_manager.find_next_pattern(seed)
        current_word = current_pop.unrolled_pattern
        generated_output = current_word
        for i in range(word_length):
            next_word = self.pop_manager.choose_next_word_string(generated_output)
            if next_word == '':
                next_word = random.choice([pop.unrolled_pattern
                                              for key, pop in self.pop_manager.patterns_collection.items()])
            generated_output += next_word
        return generated_output
