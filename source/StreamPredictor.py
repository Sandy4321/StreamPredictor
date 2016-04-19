import numpy as np
import time
import os
import matplotlib.pyplot as plt

import FileManager
import Generalizer
import PopManager
import DataObtainer

storage_file = '../PatternStore/OnlineTokens.pb'


class StreamPredictor:
    def __init__(self, pm=None):
        if pm:
            self.pop_manager = pm
        else:
            self.pop_manager = PopManager.PopManager()
        self.file_manager = FileManager.FileManager(self.pop_manager)
        self.generalizer = Generalizer.Generalizer(self.pop_manager.patterns_collection,
                                                   self.pop_manager.feed_strength_gain)
        print self.pop_manager.stats()

    def train(self, string, generalize=False):
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

    @staticmethod
    def online_token_perplexity_trainer():
        print 'Starting online training with tokens and perplexity calculation'
        sp = StreamPredictor()
        if os.path.isfile(storage_file):
            sp.file_manager.load_pb(storage_file)
            print 'Loaded PopManager.PopManager from ', storage_file
        else:
            print ' Created new PopManager.PopManager. Didnt find anything at ', storage_file
        for iteration in range(10):
            start_time = time.time()
            print 'Iteration number ' + str(iteration)
            words = DataObtainer.get_online_words(10 ** 10)
            perplexity_over_training, training_time = sp.pop_manager.train_token_and_perplexity(words)
            plt.plot(training_time, perplexity_over_training,'d-')
            plt.show()
            sp.file_manager.save_pb(storage_file)
            total_time_mins = (time.time() - start_time) / 60
            rate_words_min = round(len(words) / total_time_mins / 1000)
            print 'Total time taken to run this is ', round(total_time_mins, ndigits=2), \
                ' mins. Rate = ', rate_words_min, ' K words/min'


if __name__ == '__main__':
    StreamPredictor.online_token_perplexity_trainer()
