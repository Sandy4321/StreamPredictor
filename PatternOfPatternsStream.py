"""
Pattern of patterns.

Sequence prediction by remembering pattern of patterns. When a new pattern is seen it is stored and combined with
existing patterns. Concrete example.
Suppose pattern A is seen, then pattern B is seen. New pattern AB is created from these.

Patterns decay over time, if not seen are culled. Patterns are fed if they are seen, and their components are fed
half of them. Kind of adaptive coding.

Todos:
1. Graphs - done
2. Multi step look ahead
3. Single character prediction
4. Measure of prediction , avg prediction rate
5. Measure of interesting, find interesting stuff to learn.
6. Crawl web.
7. Binary search in find next pattern()

Idea:
    1. (done) Refactoring: See if instead of current components, new components which are stronger can be set.
    e.g. if pattern is ABCD = {ABC:D} but AB and CD are stronger then set ABCD = {AB:CD}
"""
import os
import time

import math
import matplotlib.pyplot as plt
import numpy as np
import DataObtainer

# constants
max_input_stream_length = 1000000
maxlen_word = 40  # maximum pattern length
required_repeats = 5  # if seen less than this many times, patterns won't survive on the long run.
decay_strength_loss = 1  # loss of strength per time step.
feed_ratio = [0.5, 0.25, 0.25]  # ratio of self feed to child components feed. First self, next two children.


class Pop:
    def __init__(self, chars):
        self.unrolled_pattern = chars  # The actual characters that make up current pattern.
        self.strength = 0
        self.first_component = None  # Children
        self.second_component = None
        self.first_child_parents = []

    def set_components(self, first_component, second_component):
        """
        Sets the children.
        """
        if not first_component or not second_component:
            raise Exception("component cannot be None")
        self.first_component = first_component
        first_component.first_child_parents.append(self)
        self.second_component = second_component

    def feed(self, gain):
        self.strength += int(gain * feed_ratio[0])
        if gain > 2:
            if self.first_component:
                self.first_component.feed(int(gain * feed_ratio[1]))
            if self.second_component:
                self.second_component.feed(int(gain * feed_ratio[2]))

    def decay(self):
        self.strength -= decay_strength_loss

    def __repr__(self):
        out = ""
        if self.first_component:
            out += '{' + self.first_component.unrolled_pattern + ':'
        if self.second_component:
            out += self.second_component.unrolled_pattern + '}'
        return self.unrolled_pattern + ': strength ' + str(self.strength) + out
        # ' components ' + \ # self.first_component.unrolled_pattern + ' and ' + self.second_component.unrolled_patternt


class PopManager:
    def __init__(self):
        self.patterns_collection = dict()

    def set_components_from_string(self, pop, first_string, second_string):
        if not first_string or not second_string:
            raise Exception("component cannot be empty")
        if first_string in self.patterns_collection:
            pop.first_component = self.patterns_collection[first_string]
        if second_string in self.patterns_collection:
            pop.second_component = self.patterns_collection[second_string]

    def train(self, string):
        input_length = len(string)
        feed_strength_gain = 2 * input_length / required_repeats
        print 'Started training with string length ' + str(input_length)
        char_set = set(string)
        for char in char_set:
            self.patterns_collection[char] = Pop(char)
            self.patterns_collection[char].feed(feed_strength_gain)
        previous_pop = self.patterns_collection[string[0]]
        i = 1
        while i < input_length - maxlen_word:
            current_pop = self.find_next_pattern(string[i:i + maxlen_word])
            current_word = current_pop.unrolled_pattern
            if current_word in self.patterns_collection:
                new_pattern = previous_pop.unrolled_pattern + current_word
                if new_pattern not in self.patterns_collection:
                    self.patterns_collection[new_pattern] = Pop(new_pattern)
                    self.patterns_collection[new_pattern].feed(feed_strength_gain)
                    self.patterns_collection[new_pattern].set_components(previous_pop, current_pop)
                else:
                    self.patterns_collection[new_pattern].feed(feed_strength_gain)
                previous_pop = current_pop
                i += len(current_word)
            if i % 10 == 0 and i > feed_strength_gain:  # Every now and then cull weak patterns
                self.cull(0)
            if i % 100 == 0 and i > feed_strength_gain:  # Refactor, adopt stronger children, as long as one's
                # unrolled pattern is same.
                self.refactor()
        self.cull(0)
        return self.patterns_collection

    def find_next_pattern(self, long_word):
        """
        Returns the longest pattern in the given word.
        :param long_word: a string
        :return: PoP(), longest pattern from start.
        """
        current_pattern = self.patterns_collection[long_word[0]]
        for j in range(maxlen_word, 0, -1):  # how many chars to look ahead
            current_word = long_word[:j]
            if current_word in self.patterns_collection:
                return self.patterns_collection[current_word]

    def cull(self, limit):
        cull_list = self.cull_child_and_mark_self(limit)
        for cull_key in cull_list:
            self.patterns_collection.pop(cull_key)

    def cull_child_and_mark_self(self, limit):
        cull_list = []
        for key, pop in self.patterns_collection.iteritems():
            pop.decay()
            if pop.first_component:
                if pop.first_component.strength < limit:
                    pop.first_component = None
            if pop.second_component:
                if pop.second_component.strength < limit:
                    pop.second_component = None
            if pop.strength < limit and len(pop.unrolled_pattern) > 1:
                cull_list.append(key)
        return cull_list

    def status(self, show_plot=False):
        out_string = ''
        for key, pop in sorted(self.patterns_collection.iteritems(), key=lambda ng: ng[1].strength):
            out_string += pop.__repr__()
        out_string += 'Status of Pattern of patterns with ' + str(len(self.patterns_collection)) + ' pops \n'
        if show_plot:
            strengths = [pop.strength for i, pop in self.patterns_collection.iteritems()]
            lengths = [len(pop.unrolled_pattern) for i, pop in self.patterns_collection.iteritems()]
            plt.scatter(x=lengths, y=strengths)
            plt.title('Strengths vs Lengths (x axis)')
            plt.show()
        return out_string

    def save(self, filename):
        save_string = 'pattern, strength, component1, component2, parents\n'
        for key, pop in sorted(self.patterns_collection.iteritems(), key=lambda ng: ng[1].strength):
            save_string += key + '\t' + str(pop.strength) + '\t'
            if pop.first_component:
                save_string += pop.first_component.unrolled_pattern
            save_string += '\t'
            if pop.second_component:
                save_string += pop.second_component.unrolled_pattern
            save_string += '\t'
            for parent_i in pop.first_child_parents:
                save_string += parent_i.unrolled_pattern
                save_string += '\t'
            save_string += '\n'
        with open(filename, mode='w') as file:
            file.write(save_string)
        print 'Saved file ' + filename

    def load(self, filename):
        with open(filename, mode='r') as file:
            all_lines = file.readlines()
            for lines in all_lines[1:]:
                elements = lines.split('\t')
                key = elements[0]
                self.patterns_collection[key] = Pop(key)
                self.patterns_collection[key].strength = int(elements[1])
            for lines in all_lines[1:]:
                elements = lines.strip('\n').split('\t')
                key = elements[0]
                if elements[2] is not '' and elements[3] is not '':
                    self.set_components_from_string(self.patterns_collection[key], elements[2], elements[3])
                if elements[4] != '':
                    for parent_i in elements[4:]:
                        if parent_i != '' and parent_i in self.patterns_collection:
                            self.patterns_collection[key].first_child_parents.append(self.patterns_collection[parent_i])
        print 'Loaded file ' + filename + ' with number of patterns = ' + str(len(self.patterns_collection))

    def predict_next_word(self, current_word):
        predictor_pops = []
        for key, pop in self.patterns_collection.iteritems():
            if pop.first_component and pop.second_component:
                if pop.first_component.unrolled_pattern == current_word:
                    predictor_pops.append((pop.strength, pop.second_component.unrolled_pattern))
        if len(predictor_pops) == 0:
            return ''
        strengths = [i[0] for i in predictor_pops]
        total = sum(strengths)
        words = [i[1] for i in predictor_pops]
        probabilities = [float(i) / total for i in strengths]
        return np.random.choice(words, p=probabilities)

    def generate_stream(self, word_length, seed=None):
        generated_output = ""
        current_word = np.random.choice(self.patterns_collection.values()) \
            if seed is None else seed
        for i in range(word_length):
            next_word = self.predict_next_word(current_word)
            if next_word == '':
                next_word = np.random.choice([pop.unrolled_pattern
                                              for key, pop in self.patterns_collection.iteritems()])
            generated_output += next_word
            current_word = next_word
        return generated_output

    def refactor(self, verbose=False):
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
                            if pop.first_component and pop.second_component:
                                old_first_component = pop.first_component.unrolled_pattern
                                old_second_component = pop.second_component.unrolled_pattern
                            else:
                                old_first_component, old_second_component = "", ""
                            pop.set_components(self.patterns_collection[new_first_component],
                                               self.patterns_collection[new_second_component])
                            if verbose:
                                print 'Refactored ' + pop.unrolled_pattern + ' from {' + old_first_component + ':' \
                                      + old_second_component + '} into {' + new_first_component + ':' + \
                                      new_second_component + '}'


class StreamCounter:
    """
    Used to analyze and plot few variables of Pop Manager.
    """

    def __init__(self):
        self.time = []
        self.pop_count = []
        self.prediction_gain = []

    def update(self, time, popcount, prediction_gain):
        self.time.append(time)
        self.pop_count.append(popcount)
        self.prediction_gain.append(prediction_gain)

    def plot(self):
        plt.figure()
        plt.plot(self.time, self.pop_count)
        plt.ylabel('Count of pops')
        plt.figure()
        plt.plot(self.time, self.prediction_gain)
        plt.ylabel('prediction gain')
        plt.show()


def default_trainer(storage_file):
    for iteration in range(100):
        start_time = time.time()
        print 'Iteration number ' + str(iteration)
        text = DataObtainer.get_random_book_local()
        text = DataObtainer.clean_text(text, max_input_stream_length)
        pm = PopManager()
        if os.path.isfile(storage_file):
            pm.load(storage_file)
        pm.train(text)
        pm.save(storage_file)
        print pm.generate_stream(200)
        total_time_mins = (time.time() - start_time) / 60
        rate_chars_min = len(text) / total_time_mins
        print 'Total time taken to run this is ', round(total_time_mins, ndigits=2), ' mins. Rate = ', rate_chars_min


def online_trainer(storage_file):
    for iteration in range(100):
        start_time = time.time()
        print 'Iteration number ' + str(iteration)
        text = DataObtainer.gutenberg_random_book()
        text = DataObtainer.clean_text(text, max_input_stream_length)
        pm = PopManager()
        if os.path.isfile(storage_file):
            pm.load(storage_file)
        pm.train(text)
        pm.save(storage_file)
        print pm.generate_stream(200)
        total_time_mins = (time.time() - start_time) / 60
        rate_chars_min = len(text) / total_time_mins
        print 'Total time taken to run this is ', round(total_time_mins, ndigits=2), ' mins. Rate = ', rate_chars_min


if __name__ == '__main__':
    pattern_file = 'PatternStore/parent.tsv'
    default_trainer(pattern_file)
