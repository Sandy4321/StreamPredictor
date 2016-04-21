"""
Pattern of patterns.

Sequence prediction by remembering pattern of patterns. When a new pattern is seen it is stored and combined with
existing patterns. Concrete example.
Suppose pattern A is seen, then pattern B is seen. New pattern AB is created from these.

Patterns decay over time, if not seen are culled. Patterns are fed if they are seen, and their components are fed
half of them. Kind of adaptive coding.
"""
import numpy as np

from Pop import Pop


# constants


class PopManager:
    def __init__(self):
        #  Constants
        self.occasional_step_period = 2000
        self.perplexity_count = 6000
        self.maximum_word_count = 40
        self.max_input_stream_length = 10 ** 7
        self.maximum_pattern_length = 40  # maximum pattern length
        self.required_repeats = 5  # if seen less than this many times, patterns won't survive on the long run.
        self.feed_ratio_parent_category = 0.5
        self.not_found_ratio = 0.9
        #  Fields
        self.patterns_collection = dict()
        self.feed_strength_gain = 10 ** 6
        self.previous_decay_time = 0
        self.vocabulary_count = 0

    def stats(self):
        return 'The perplexity count constant is ' + str(self.perplexity_count) + \
               '\nThe occasional step periods is ' + str(self.occasional_step_period) + \
               '\nThe not found raitio is' + str(self.not_found_ratio) + \
               '\nFeed strength gain is ' + str(self.feed_strength_gain)

    def __repr__(self):
        return 'Has ' + str(len(self.patterns_collection)) + ' few are ' + \
               '-'.join([i.__repr__() for i in self.patterns_collection.values()[:5]])

    def add_pop_string(self, string):
        if string in self.patterns_collection:
            raise Exception(string + 'is already present')
        self.patterns_collection[string] = Pop(string)

    def add_pop(self, pop):
        string = pop.unrolled_pattern
        if string in self.patterns_collection:
            raise Exception(string + 'is already present')
        self.patterns_collection[string] = pop

    def set_components_from_string(self, pop, first_string, second_string):
        if not first_string or not second_string:
            raise Exception("component cannot be empty")
        if first_string in self.patterns_collection:
            pop.first_component = self.patterns_collection[first_string]
        if second_string in self.patterns_collection:
            pop.second_component = self.patterns_collection[second_string]

    def setup_train(self, string):
        input_length = len(string)
        self.feed_strength_gain = 2 * input_length / self.required_repeats
        print 'Started training with string length ' + str(input_length)
        char_set = set(string)
        for char in char_set:
            self.patterns_collection[char] = Pop(char)
            self.patterns_collection[char].feed(self.feed_strength_gain)
        return input_length

    def train_token(self, words):
        word_count = self.add_words_to_patterns_collection(words)
        print 'Started training with word count = ' + str(word_count)
        previous_pop = self.patterns_collection.values()[0]
        i = 1
        while i < word_count:
            i, current_pop = self.train_token_step(i, previous_pop, words[i:i + self.maximum_word_count])
            previous_pop = current_pop
        self.refactor()
        self.cull(i)
        return self.patterns_collection

    def find_next_word(self, words_list):
        """
        Returns the longest pattern in the given word.
        :param long_word: a string
        :return: PoP(), longest pattern from start.
        """
        end = min(len(words_list), self.maximum_word_count)
        for j in range(end, 0, -1):  # how many chars to look ahead
            current_word = ''.join(words_list[:j])
            if current_word in self.patterns_collection:
                return self.patterns_collection[current_word], j
        new_pop = Pop(words_list[0])
        new_pop.feed(self.feed_strength_gain)
        self.patterns_collection[words_list[0]] = new_pop
        return new_pop, 1

    def calculate_perplexity(self, words, verbose=True):
        word_count = self.add_words_to_patterns_collection(words, verbose)
        if verbose:
            print 'Started calculating perplexity with word count = ' + str(word_count)
        log_running_perplexity = 0
        perplexity_list = []
        N = 1
        while N < word_count - 1:
            N, log_running_perplexity = self.perplexity_step(N, log_running_perplexity, perplexity_list, words[:N],
                                                             words[N])
        final_log_perplexity = log_running_perplexity * (1 / float(N))
        final_perplexity = 2 ** final_log_perplexity
        if verbose:
            print 'Final perplexity is ', final_perplexity
        return perplexity_list

    def train_token_and_perplexity(self, words):
        word_count = self.add_words_to_patterns_collection(words)
        print 'Started training and calculating perplexity with ', str(word_count), ' words.'
        previous_pop = self.patterns_collection.values()[0]
        perplexity_over_training = []
        training_time = []
        i = 1
        while i < word_count - self.maximum_pattern_length:
            i, current_pop = self.train_token_step(i, previous_pop, words[i:i + self.maximum_word_count])
            previous_pop = current_pop
            if i % self.occasional_step_period == 0:
                self.occasional_step(i, perplexity_over_training, training_time, words)
        self.occasional_step(i, perplexity_over_training, training_time, words)
        self.fix_first_child_parents()
        final_perplexity = perplexity_over_training[-1]
        print 'Final perplexity is ', final_perplexity, ' number of patterns is ', len(self.patterns_collection)
        return perplexity_over_training, training_time

    def decay(self, i):
        for key, pop in self.patterns_collection.iteritems():
            pop.decay(i)

    def occasional_step(self, i, perplexity_over_training, training_time, words):
        decay_amount = i - self.previous_decay_time
        training_time.append(i)
        self.decay(decay_amount)
        self.previous_decay_time = i
        self.cull(i)
        self.refactor()
        perplexity_over_training.append(
            self.calculate_perplexity(words[i:i + self.perplexity_count], verbose=False)[-1])

    def perplexity_step(self, N, log_running_perplexity, perplexity_list, previous_words, actual_next_word):
        next_words, probabilities = self.next_word_distribution(previous_words)
        chosen_prob = self.get_prediction_probability(actual_next_word, next_words, probabilities)
        log_running_perplexity -= np.log2(chosen_prob)
        perplexity_list.append(2 ** (log_running_perplexity * (1 / float(N))))
        print 'Current Perplexity = {0}\r'.format(perplexity_list[-1]),
        N += 1
        return N, log_running_perplexity

    def get_prediction_probability(self, actual_next_word, next_words, probabilities):
        word_count = len(next_words)
        remaining_words_in_vocabulary = self.vocabulary_count - word_count
        if actual_next_word in next_words:
            chosen_prob = (1 - self.not_found_ratio) * probabilities[next_words.index(actual_next_word)]
        else:
            chosen_prob = self.not_found_ratio / remaining_words_in_vocabulary
        return chosen_prob

    def train_token_step(self, index, previous_pop, next_words_list):
        """ A single step in training. Joins patterns, updates counter i"""
        current_pop, increment = self.find_next_word(next_words_list)
        self.join_pattern(previous_pop, current_pop, found_pattern_feed_ratio=1)
        index += increment
        if index % 1000 == 0 and index > self.feed_strength_gain:
            self.refactor()
        return index, current_pop

    def add_words_to_patterns_collection(self, words, verbose=True):
        word_count = len(words)
        unique_words = set(words)
        for word in unique_words:
            if word not in self.patterns_collection:
                self.patterns_collection[word] = Pop(word)
                self.patterns_collection[word].feed(self.feed_strength_gain)
                self.vocabulary_count += 1
        if verbose:
            print 'There are ', self.vocabulary_count, ' words in vocabulary.'
            print 'The first few words are ', ','.join(words[:10])
        return word_count

    def next_word_distribution(self, previous_words_list):
        start = max(0, len(previous_words_list) - self.maximum_word_count)
        for j in range(start, len(previous_words_list)):
            current_word = ''.join(previous_words_list[j:])
            if current_word in self.patterns_collection:
                current_pop = self.patterns_collection[current_word]
                words, probabilities = current_pop.get_next_smallest_distribution()
                return words, probabilities
        print 'Warning. Nothing after ', ''.join(previous_words_list)
        return previous_words_list[0], np.array([1])

    def join_pattern(self, first_pattern, second_pattern, found_pattern_feed_ratio):
        new_pattern = first_pattern.unrolled_pattern + second_pattern.unrolled_pattern
        if new_pattern not in self.patterns_collection:
            self.patterns_collection[new_pattern] = Pop(new_pattern)
            self.patterns_collection[new_pattern].set_components(first_pattern, second_pattern)
        self.patterns_collection[new_pattern].feed(self.feed_strength_gain * found_pattern_feed_ratio)
        # Category tasks
        if first_pattern.belongs_to_category is None and second_pattern.belongs_to_category is None:
            return
        first_category = first_pattern.belongs_to_category if first_pattern.belongs_to_category else first_pattern
        second_category = second_pattern.belongs_to_category if second_pattern.belongs_to_category else second_pattern
        self.join_pattern(first_category, second_category, found_pattern_feed_ratio * self.feed_ratio_parent_category)

    def find_next_pattern(self, long_word):
        """
        Returns the longest pattern in the given word.
        :param long_word: a string
        :return: PoP(), longest pattern from start.
        """
        for j in range(self.maximum_pattern_length, 0, -1):  # how many chars to look ahead
            current_word = long_word[:j]
            if current_word in self.patterns_collection:
                return self.patterns_collection[current_word]

    def cull(self, limit):
        cull_list = self.cull_child_and_mark_self(limit)
        for cull_key in cull_list:
            first_component = self.patterns_collection[cull_key].first_component
            if first_component:
                first_component.first_child_parents.remove(self.patterns_collection[cull_key])
            self.patterns_collection.pop(cull_key)

    def cull_child_and_mark_self(self, limit):
        cull_list = []
        for key, pop in self.patterns_collection.iteritems():
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

    def status(self):
        out_string = ''
        for key, pop in sorted(self.patterns_collection.iteritems(), key=lambda ng: ng[0]):
            out_string += pop.__repr__()
        out_string += 'Status of Pattern of patterns with ' + str(len(self.patterns_collection)) + ' pops \n'
        return out_string

    def predict_next_word(self, input_word):
        start = max(0, len(input_word) - self.maximum_pattern_length)
        for j in range(start, len(input_word)):
            current_word = input_word[j:]
            if current_word in self.patterns_collection:
                current_pop = self.patterns_collection[current_word]
                words, probabilities = current_pop.get_next_distribution()
                if current_pop.belongs_to_category:
                    category_words, category_probabilities = current_pop.belongs_to_category.get_next_distribution()
                    words = words + category_words
                    probabilities = np.hstack([0.5 * probabilities, 0.5 * category_probabilities])
                if len(words) < 1:
                    continue
                probabilities /= sum(probabilities)
                return np.random.choice(words, p=probabilities)
        print ' nothing after ', input_word
        return ''

    def refactor(self):
        for key, pop in self.patterns_collection.iteritems():
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

    def fix_first_child_parents(self):
        """
        Fixes mismatch between first_child_parents by going through each pattern and checking if pop is
        pop.first_child_parents.first component
        """
        print 'Fixing incorrect first_child_parents'
        for pop in self.patterns_collection.values():
            for parent_pop in pop.first_child_parents:
                if parent_pop.first_component:
                    if parent_pop.first_component is pop:
                        continue
                print 'Mismatch ', pop.__repr__(), ' and ', parent_pop.__repr__()
                pop.first_child_parents.remove(parent_pop)
