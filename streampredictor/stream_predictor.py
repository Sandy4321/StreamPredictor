from streampredictor import file_manager
from streampredictor import pop
from streampredictor import pop_manager
from streampredictor import constants
from streampredictor import generator
import time


class StreamPredictor:
    def __init__(self, pm=None):
        if pm:
            self.pop_manager = pm  # type: pop_manager
        else:
            self.pop_manager = pop_manager.PopManager()  # type: pop_manager
        self.file_manager = file_manager.FileManager(self.pop_manager)
        self.generator = generator.Generator(self.pop_manager.pattern_collection, self.pop_manager.vocabulary)
        print(self.pop_manager.stats())

    def train(self, list_of_words, verbose=False):
        print('Started training with {0} words'.format(len(list_of_words)))
        self.pop_manager.add_words_to_vocabulary(list_of_words)
        previous_pop = self.pop_manager.pattern_collection[list_of_words[0]]
        remaining_sequence = list_of_words[1:]
        i = 1
        start_time = time.time()
        while remaining_sequence and len(remaining_sequence) > 0:
            next_pop, remaining_sequence = self.pop_manager.get_next_pop(remaining_sequence)
            if next_pop is None:
                break
            new_pop = pop.combine(previous_pop, next_pop)
            self.pop_manager.ingest(new_pop)
            if i % constants.occasional_step_count == 0:
                print('Occasional step at ', i)
                self.occasional_step(i, verbose)
            previous_pop = next_pop
            i += 1
        total_time_s = time.time() - start_time
        print('Finished training in {0} steps'.format(i))
        print('The rate of learning is {0} words/s'.format(i/total_time_s))

    def occasional_step(self, step_count, verbose):
        self.pop_manager.occasional_step(step_count, verbose)

    def generate(self, word_length, seed=None):
        """
        Returns the list of generated words.

        :type word_length: int
        :type seed: str
        :rtype: list[str]
        """
        generated_output = self.generator.generate_words(word_length, seed=seed)
        for word in generated_output:
            if word not in self.pop_manager.vocabulary:
                raise ValueError('Generated word not in vocabulary :' + word)
        return generated_output

    def calculate_perplexity(self, words, verbose=False):
        self.pop_manager.add_words_to_vocabulary(words, verbose)
        word_count = len(words)
        if verbose:
            print('Started calculating perplexity with word count = ' + str(word_count))
        log_running_perplexity = 0
        perplexity_list = []
        N = 1
        while N < word_count:
            N, log_running_perplexity = self.generator.perplexity_step(N, log_running_perplexity, perplexity_list,
                                                                       words[:N],
                                                                       words[N])
        final_log_perplexity = log_running_perplexity * (1 / float(N))
        final_perplexity = 2 ** final_log_perplexity
        if verbose:
            print('Final perplexity is ', final_perplexity)
        return perplexity_list
