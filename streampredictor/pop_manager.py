"""
Pattern of patterns.

Sequence prediction by remembering pattern of patterns. When a new pattern is seen it is stored and combined with
existing patterns. Concrete example.
Suppose pattern A is seen, then pattern B is seen. New pattern AB is created from these.

Patterns decay over time, if not seen are culled. Patterns are fed if they are seen, and their components are fed
half of them. Kind of adaptive coding.
"""
import numpy as np

from streampredictor.pop import Pop
from streampredictor import constants


class PopManager:
    def __init__(self):
        #  Constants
        self.occasional_step_period = 2000
        self.perplexity_count = 6000  # the length of words used to calculate perplexity
        self.maximum_word_count = 40
        self.max_input_stream_length = 10 ** 7
        self.maximum_pattern_length = 40  # maximum pattern length
        self.required_repeats = 5  # if seen less than this many times, patterns won't survive on the long run.
        self.feed_ratio_parent_category = 0.5
        self.not_found_ratio = 0.9
        self.feed_strength_gain = 10 ** 6
        #  Fields
        self.patterns_collection = dict()
        self.vocabulary_count = 0

    def stats(self):
        return '\n============= Stream Predictor Hyper parameters ===================' + \
               '\nThe perplexity count constant is ' + str(self.perplexity_count) + \
               '\nThe occasional step periods is ' + str(self.occasional_step_period) + \
               '\nThe not found raitio is' + str(self.not_found_ratio) + \
               '\nFeed strength gain is ' + str(self.feed_strength_gain) + \
               '\n============= End Stream Predictor Hyper parameters ==================='

    def __repr__(self):
        return 'Has ' + str(len(self.patterns_collection)) + ' few are ' + \
               '-'.join([i.__repr__() for i in list(self.patterns_collection.values())[:5]])

    def get(self, key):
        """
        Gets the pop with the name key

        :type key: str
        :rtype: Pop
        """
        return self.patterns_collection[key]

    def add_pop(self, pop):
        string = pop.unrolled_pattern
        if string in self.patterns_collection:
            raise Exception(string + 'is already present')
        self.patterns_collection[string] = pop
        self.vocabulary_count += 1

    def get_next_pop(self, remaining_sequence):
        """
        Returns the longest pattern in the given word.

        :type remaining_sequence: list[str]
        :rtype: Pop, list[Pop]
        """
        end = min(len(remaining_sequence), self.maximum_word_count)
        for j in range(end, 0, -1):  # how many chars to look ahead
            current_word = ''.join(remaining_sequence[:j])
            if current_word in self.patterns_collection:
                return self.patterns_collection[current_word], remaining_sequence[j:]
        return None, None

    def ingest(self, new_pop):
        """
        add and strengthen the new pop

        :type new_pop: Pop
        :rtype:None
        """
        if new_pop.unrolled_pattern not in self.patterns_collection:
            self.patterns_collection[new_pop.unrolled_pattern] = new_pop
        self.patterns_collection[new_pop.unrolled_pattern].feed(
            self.feed_strength_gain * constants.found_pattern_feed_ratio)

    def occasional_step(self, step_count):
        self.decay(constants.occasional_decay)
        self.cull(step_count)
        self.refactor()

    def decay(self, i):
        for key, pop in self.patterns_collection.items():
            pop.decay(i)

    def cull(self, limit):
        cull_list = self.cull_child_and_mark_self(limit)
        for cull_key in cull_list:
            first_component = self.patterns_collection[cull_key].first_component
            if first_component:
                first_component.first_child_parents.remove(self.patterns_collection[cull_key])
            self.patterns_collection.pop(cull_key)

    def cull_child_and_mark_self(self, limit):
        cull_list = []
        for key, pop in self.patterns_collection.items():
            if pop.first_component:
                if pop.first_component.strength < limit:
                    pop.first_component.first_child_parents.remove(pop)
                    pop.first_component = None
            if pop.second_component:
                if pop.second_component.strength < limit:
                    pop.second_component = None
            if pop.strength < limit and len(pop.unrolled_pattern) > 1:
                cull_list.append(key)
        return cull_list

    def refactor(self):
        for key, pop in self.patterns_collection.items():
            if pop.first_component and pop.second_component:
                current_components_strength = pop.first_component.strength + pop.second_component.strength
            else:
                current_components_strength = 0
            for i in range(1, len(key) - 1):
                new_first_component = key[:i]
                new_second_component = key[i:]
                if new_first_component in self.patterns_collection:
                    if new_second_component in self.patterns_collection:
                        refactored_components_strength = self.patterns_collection[new_first_component].strength + \
                                                         self.patterns_collection[new_second_component].strength
                        if refactored_components_strength > current_components_strength:
                            self.change_components_string(new_first_component, new_second_component, pop)

    def change_components_string(self, first_string, second_string, pop):
        if first_string not in self.patterns_collection or second_string not in self.patterns_collection:
            raise ValueError('One of these is not in pattern collection {', first_string, ' : ', second_string, '}')
        if pop.first_component:
            old_pop = pop.first_component
            if pop in old_pop.first_child_parents:
                old_pop.first_child_parents.remove(pop)
        pop.set_components(self.patterns_collection[first_string],
                           self.patterns_collection[second_string])

    def add_words_to_vocabulary(self, words, verbose=True):
        """
        Find the vocabulary and add that vocabulary to pattern collection.

        :type words: list of str
        :rtype: None
        """
        unique_words = set(words)
        for word in unique_words:
            if word not in self.patterns_collection:
                self.add_pop(Pop(word))
                self.patterns_collection[word].feed(self.feed_strength_gain)
        if verbose:
            print('There are ', self.vocabulary_count, ' words in vocabulary.')
            print('The first few words are ', ','.join(words[:10]))

    def status(self):
        out_string = ''
        for key, pop in sorted(iter(self.patterns_collection.items()), key=lambda ng: ng[0]):
            out_string += pop.__repr__()
        out_string += 'Status of Pattern of patterns with ' + str(len(self.patterns_collection)) + ' pops \n'
        return out_string

    ############## end of clean code ########################

    def perplexity_step(self, N, log_running_perplexity, perplexity_list, previous_words, actual_next_word):
        next_words, probabilities = self.next_word_distribution(previous_words)
        chosen_prob = self.get_prediction_probability(actual_next_word, next_words, probabilities)
        log_running_perplexity -= np.log2(chosen_prob)
        perplexity_list.append(2 ** (log_running_perplexity * (1 / float(N))))
        print('Current Perplexity = {0}\r'.format(perplexity_list[-1]), end=' ')
        N += 1
        return N, log_running_perplexity

    def calculate_perplexity(self, words, verbose=True):
        self.add_words_to_vocabulary(words, verbose)
        word_count = len(words)
        if verbose:
            print('Started calculating perplexity with word count = ' + str(word_count))
        log_running_perplexity = 0
        perplexity_list = []
        N = 1
        while N < word_count:
            N, log_running_perplexity = self.perplexity_step(N, log_running_perplexity, perplexity_list, words[:N],
                                                             words[N])
        final_log_perplexity = log_running_perplexity * (1 / float(N))
        final_perplexity = 2 ** final_log_perplexity
        if verbose:
            print('Final perplexity is ', final_perplexity)
        return perplexity_list

    # def train_token_and_perplexity(self, words):
    #     self.add_words_to_patterns_collection(words)
    #     word_count = len(words)
    #     print('Started training and calculating perplexity with ', str(word_count), ' words.')
    #     previous_pop = list(self.patterns_collection.values())[0]
    #     perplexity_over_training = []
    #     training_time = []
    #     i = 1
    #     while i < word_count - self.maximum_pattern_length:
    #         i, current_pop = self.train_token_step(i, previous_pop, words[i:i + self.maximum_word_count])
    #         previous_pop = current_pop
    #         if i % self.occasional_step_period == 0:
    #             self.occasional_step(i, perplexity_over_training, training_time, words)
    #     self.occasional_step(i, perplexity_over_training, training_time, words)
    #     self.fix_first_child_parents()
    #     final_perplexity = perplexity_over_training[-1]
    #     print('Final perplexity is ', final_perplexity, ' number of patterns is ', len(self.patterns_collection))
    #     return perplexity_over_training, training_time



    def get_prediction_probability(self, actual_next_word, predicted_words, probabilities):
        if actual_next_word not in self.patterns_collection:
            raise ValueError('The actual next word is not present in vocabulary. Preprocess to handle unknown words')
        word_count = len(predicted_words)
        remaining_words_in_vocabulary = self.vocabulary_count - word_count
        if remaining_words_in_vocabulary < 0:
            raise ValueError('The given predicted word count {0} is  greater than vocabulary word count {1}'
                             .format(word_count, self.vocabulary_count))
        if actual_next_word in predicted_words:
            chosen_prob = (1 - self.not_found_ratio) * probabilities[predicted_words.index(actual_next_word)]
        else:
            chosen_prob = self.not_found_ratio / remaining_words_in_vocabulary
        return chosen_prob

    def generate_words(self, word_length, seed=None):
        print('Generating words with word count = ', word_length)
        current_pop = np.random.choice(list(self.patterns_collection.values())) \
            if seed is None or '' else self.find_next_pattern(seed)
        current_word = current_pop.unrolled_pattern
        generated_output = [current_word]
        printable_output = self.patterns_collection[current_word].print_components()
        for i in range(word_length - 1):
            next_word = self.choose_next_word_word_list(generated_output)
            if next_word == '':
                next_word = np.random.choice([pop.unrolled_pattern
                                              for key, pop in self.patterns_collection.items()])
            generated_output.append(next_word)
            printable_output += self.patterns_collection[next_word].print_components()
        return printable_output

    def next_word_distribution(self, previous_words_list):
        start = max(0, len(previous_words_list) - self.maximum_word_count)
        for j in range(start, len(previous_words_list)):
            current_word = ''.join(previous_words_list[j:])
            if current_word in self.patterns_collection:
                current_pop = self.patterns_collection[current_word]
                words, probabilities = current_pop.get_next_smallest_distribution()
                return words, probabilities
        print('Warning. Nothing after ', ''.join(previous_words_list))
        return previous_words_list[0], np.array([1])

        # def join_pattern(self, first_pattern, second_pattern, found_pattern_feed_ratio):
        #     new_pattern = first_pattern.unrolled_pattern + second_pattern.unrolled_pattern
        #     if new_pattern not in self.patterns_collection:
        #         self.patterns_collection[new_pattern] = Pop(new_pattern)
        #         self.patterns_collection[new_pattern].set_components(first_pattern, second_pattern)
        #     self.patterns_collection[new_pattern].feed(self.feed_strength_gain * found_pattern_feed_ratio)
        # Category tasks
        # if first_pattern.belongs_to_category is None and second_pattern.belongs_to_category is None:
        #     return
        # first_category = first_pattern.belongs_to_category if first_pattern.belongs_to_category else first_pattern
        # second_category = second_pattern.belongs_to_category if second_pattern.belongs_to_category else second_pattern
        # self.join_pattern(first_category, second_category, found_pattern_feed_ratio * self.feed_ratio_parent_category)

    def choose_next_word_word_list(self, input_word, Verbose=False):
        start = max(0, len(input_word) - self.maximum_pattern_length)
        for j in range(start, len(input_word)):
            current_word = ''.join(input_word[j:])
            if current_word in self.patterns_collection:
                current_pop = self.patterns_collection[current_word]
                words, probabilities = current_pop.get_next_words_distribution()
                if current_pop.belongs_to_category:
                    category_words, category_probabilities = current_pop.belongs_to_category.get_next_words_distribution()
                    words = words + category_words
                    probabilities = np.hstack([0.5 * probabilities, 0.5 * category_probabilities])
                if len(words) < 1:
                    continue
                probabilities /= sum(probabilities)
                return np.random.choice(words, p=probabilities)
        if Verbose:
            print(' nothing after ', input_word)
        return ''

    def fix_first_child_parents(self, verbose=False):
        """
        Fixes mismatch between first_child_parents by going through each pattern and checking if pop is
        pop.first_child_parents.first component
        """
        print('Fixing incorrect first_child_parents')
        for pop in list(self.patterns_collection.values()):
            for parent_pop in pop.first_child_parents:
                if parent_pop.first_component:
                    if parent_pop.first_component is pop:
                        continue
                if verbose:
                    print('Mismatch ', pop.__repr__(), ' and ', parent_pop.__repr__())
                pop.first_child_parents.remove(parent_pop)