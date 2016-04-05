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
    2. same category, must split into sub patterns. e.g. if ABXC and ABYC are found to be similar then only X
    is similar to Y
"""
import os
import time
from difflib import SequenceMatcher
import numpy as np

import DataObtainer

# constants
max_input_stream_length = 10000000
maxlen_word = 40  # maximum pattern length
required_repeats = 5  # if seen less than this many times, patterns won't survive on the long run.
decay_strength_loss = 1  # loss of strength per time step.
feed_ratio = [0.5, 0.25, 0.25]  # ratio of self feed to child components feed. First self, next two children.
feed_ratio_parent_category = 0.5
generalize_intersection_ratio = 0.75
generalize_common_required_count = 3


class Pop:
    def __init__(self, chars):
        self.unrolled_pattern = chars  # The actual characters that make up current pattern.
        self.strength = 0
        self.first_component = None  # Children
        self.second_component = None
        self.first_child_parents = []
        self.belongs_to_category = None  # type Pop(), which category does this belong to?
        self.members_of_category = []  # Pop() List, who are the members of this category?

    def set_components(self, first_component, second_component):
        """
        Sets the children.
        """
        if not first_component or not second_component:
            raise Exception("component cannot be None")
        self.first_component = first_component
        first_component.first_child_parents.append(self)
        self.second_component = second_component

    def set_category(self, first_component, second_component):
        """
        Sets the member categories.
        """
        if not first_component or not second_component:
            raise Exception("component cannot be None")
        first_component.belongs_to_category = self
        second_component.belongs_to_category = self
        self.members_of_category.append(first_component)
        self.members_of_category.append(second_component)

    def feed(self, gain):
        self.strength += int(gain * feed_ratio[0])
        if gain > 2:
            if self.first_component:
                self.first_component.feed(int(gain * feed_ratio[1]))
            if self.second_component:
                self.second_component.feed(int(gain * feed_ratio[2]))

    def decay(self):
        self.strength -= decay_strength_loss

    def is_child(self, child):
        if child.unrolled_pattern == self.unrolled_pattern:
            return True
        if not self.second_component:
            return False
        return self.second_component.is_child(child) and self.first_component.is_child(child)

    def __repr__(self):
        out = self.unrolled_pattern + ': strength ' + str(self.strength)
        if self.first_component:
            out += '={ ' + self.first_component.unrolled_pattern + ': '
        if self.second_component:
            out += self.second_component.unrolled_pattern + '}'
        if self.belongs_to_category:
            out += ' # ' + self.belongs_to_category.unrolled_pattern
        return out

    def similarity(self, other_pop):
        if not (
                    self.first_component and self.second_component and other_pop.first_component and other_pop.second_component):
            return SequenceMatcher(None, self.unrolled_pattern, other_pop.unrolled_pattern).ratio()
        similarity1 = self.first_component.similarity(other_pop.first_component)
        similarity2 = self.second_component.similarity(other_pop.second_component)
        return (len(self.first_component.unrolled_pattern) * similarity1 + len(self.second_component.unrolled_pattern)
                * similarity2) / len(self.unrolled_pattern)

    def get_next_distribution(self):
        """ Gives the list of next predicted words and their associated probabilities.
        :return: List A, B. Where A is a list of strings, B is list of floats.
        """
        next_words = []
        strengths = []
        for parent_i in self.first_child_parents:
            if parent_i.second_component:
                next_words.append(parent_i.second_component.unrolled_pattern)
                strengths.append(max(parent_i.strength, 0))
        total = sum(strengths)
        probabilities = [float(i) / total for i in strengths]
        return next_words, probabilities

    def has_common_child(self, other_pop):
        if not (
                    self.first_component and self.second_component and other_pop.first_component and other_pop.second_component):
            return self.unrolled_pattern == other_pop.unrolled_pattern
        return self.first_component.has_common_child(other_pop.first_component) or \
               self.second_component.has_common_child(other_pop.second_component)

    def next_patterns(self):
        """ Gives the list of patterns that are likely to occur next. """
        if not self.first_child_parents:
            return []
        next_patterns = []
        for parent_i in self.first_child_parents:
            if parent_i.second_component:
                next_patterns.append(parent_i.second_component)
        return next_patterns


class PopManager:
    def __init__(self):
        self.patterns_collection = dict()
        self.feed_strength_gain = 10000

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

    def train(self, string, generalize=False):
        input_length = self.setup_train(string)
        previous_pop = self.patterns_collection[string[0]]
        i = 1
        while i < input_length - maxlen_word:
            current_pop = self.find_next_pattern(string[i:i + maxlen_word])
            self.join_pattern(previous_pop, current_pop, found_pattern_feed_ratio=1)
            previous_pop = current_pop
            i += len(current_pop.unrolled_pattern)
            if i % 1000 == 0 and i > self.feed_strength_gain:
                # Refactor, adopt stronger children, as long as one's unrolled pattern is same.
                self.refactor()
                self.cull(0)
        self.refactor()
        if generalize:
            self.generalize()
        self.cull(0)
        return self.patterns_collection

    def setup_train(self, string):
        input_length = len(string)
        self.feed_strength_gain = 2 * input_length / required_repeats
        print 'Started training with string length ' + str(input_length)
        char_set = set(string)
        for char in char_set:
            self.patterns_collection[char] = Pop(char)
            self.patterns_collection[char].feed(self.feed_strength_gain)
        return input_length

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
        self.join_pattern(first_category, second_category, found_pattern_feed_ratio * feed_ratio_parent_category)

    def find_next_pattern(self, long_word):
        """
        Returns the longest pattern in the given word.
        :param long_word: a string
        :return: PoP(), longest pattern from start.
        """
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

    def status(self):
        out_string = ''
        for key, pop in sorted(self.patterns_collection.iteritems(), key=lambda ng: ng[1].strength):
            out_string += pop.__repr__()
        out_string += 'Status of Pattern of patterns with ' + str(len(self.patterns_collection)) + ' pops \n'
        return out_string

    def save_tsv(self, filename):
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

    # def save(self, filename):
    #     """ Pickle thyself. """
    #     pickle.dump(self, gzip.open(filename, 'w'))
    #     print 'Pattern Of Patterns saved to ', filename
    #
    # @staticmethod
    # def load(filename):
    #     return pickle.load(gzip.open(filename, 'r'))

    def load_tsv(self, filename):
        limit = None  # doesn't work for now, some patterns will have first parent child which is not loaded
        with open(filename, mode='r') as file:
            all_lines = file.readlines()
            total_lines = len(all_lines)
            if limit:
                start_line = max(0, total_lines - limit)
                lines_to_read = all_lines[1 + start_line:]
            else:
                lines_to_read = all_lines[1:]
            for lines in lines_to_read:
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

    def predict_next_word(self, input_word):
        for j in range(len(input_word)):
            current_word = input_word[j:]
            if current_word in self.patterns_collection:
                current_pop = self.patterns_collection[current_word]
                if len(current_pop.first_child_parents) < 1:
                    continue
                words, probabilities = current_pop.get_next_distribution()
                if len(words) < 1:
                    raise Exception(' predict_next_word ' + current_word)
                return np.random.choice(words, p=probabilities)
        return ''

    def generate_stream(self, word_length, seed=None):
        current_pop = np.random.choice(self.patterns_collection.values()) \
            if seed is None or '' else self.find_next_pattern(seed)
        current_word = current_pop.unrolled_pattern
        generated_output = current_word
        for i in range(word_length):
            next_word = self.predict_next_word(generated_output)
            if next_word == '':
                next_word = np.random.choice([pop.unrolled_pattern
                                              for key, pop in self.patterns_collection.iteritems()])
            generated_output += next_word
            current_word = next_word
        return generated_output

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

    def similarity_all(self):
        for key1, pop1 in self.patterns_collection.iteritems():
            for key2, pop2 in self.patterns_collection.iteritems():
                print 'Similarity of ', pop1.unrolled_pattern, ' and ', pop2.unrolled_pattern, ' is ', pop1.similarity(
                    pop2)

    def fix_first_child_parents(self):
        print 'Fixing incorrect first_child_parents'
        for pop in self.patterns_collection.values():
            for parent_pop in pop.first_child_parents:
                if parent_pop.first_component:
                    if parent_pop.first_component is pop:
                        continue
                print 'Mismatch ', pop.__repr__(), ' and ', parent_pop.__repr__()
                pop.first_child_parents.remove(parent_pop)

    def do_not_generalize(self, first_string, second_string):
        if first_string == second_string:
            return True
        if len(''.join(e for e in first_string if e.isalnum())) < 3:
            return True
        if len(''.join(e for e in second_string if e.isalnum())) < 3:
            return True
        if self.patterns_collection[first_string].is_child(self.patterns_collection[second_string]) or \
                self.patterns_collection[second_string].is_child(self.patterns_collection[first_string]):
            return True
        return False

    def generalize(self):
        print 'Generalizing ..'
        pops_list = self.patterns_collection.values()
        for pop in pops_list:
            next_to_next = dict()
            for next_pop in pop.next_patterns():
                next_to_next[next_pop.unrolled_pattern] = next_pop.next_patterns()
            for next_key_a, next_list_a in next_to_next.iteritems():
                for next_key_b, next_list_b in next_to_next.iteritems():
                    if self.do_not_generalize(next_key_a, next_key_b):
                        continue
                    same_length = len(set(next_list_a).intersection(next_list_b))
                    passing_length = generalize_intersection_ratio * min(len(next_list_a), len(next_list_b))
                    if same_length > passing_length and same_length > generalize_common_required_count:
                        self.set_similarity(next_key_a, next_key_b)

    def set_similarity(self, first_pattern, second_pattern):
        if first_pattern == second_pattern:
            print first_pattern, ' and ', second_pattern, ' are same!'
            return
        first_pop = self.patterns_collection[first_pattern]
        second_pop = self.patterns_collection[second_pattern]
        if first_pop.has_common_child(second_pop):
            if first_pop.first_component and second_pop.first_component and second_pop.second_component \
                    and second_pop.second_component:
                self.set_similarity(first_pop.first_component.unrolled_pattern,
                                    second_pop.first_component.unrolled_pattern)
                self.set_similarity(first_pop.second_component.unrolled_pattern,
                                    second_pop.second_component.unrolled_pattern)
                return
        print 'Perhaps ', first_pattern, ' and ', second_pattern, ' are similar?'
        new_category_string = 'category with ' + first_pattern + ' and ' + second_pattern
        if new_category_string not in self.patterns_collection:
            new_category = Pop(new_category_string)
            self.patterns_collection[new_category_string] = new_category
            new_category.set_category(self.patterns_collection[first_pattern],
                                      self.patterns_collection[second_pattern])
        self.patterns_collection[new_category_string].feed(self.feed_strength_gain)


class StreamCounter:
    """
    Used to analyze few variables of Pop Manager.
    """

    def __init__(self):
        self.time = []
        self.pop_count = []
        self.prediction_gain = []

    def update(self, time, popcount, prediction_gain):
        self.time.append(time)
        self.pop_count.append(popcount)
        self.prediction_gain.append(prediction_gain)


def load_pm(storage_file):
    if os.path.isfile(storage_file):
        pm = PopManager()
        pm.load_tsv(storage_file)
        print 'Loaded PopManager from ', storage_file
    else:
        pm = PopManager()
        print ' Created new PopManager. Didnt find anything at ', storage_file
    return pm


def default_trainer(storage_file):
    for iteration in range(100):
        start_time = time.time()
        print 'Iteration number ' + str(iteration)
        text = DataObtainer.get_random_book_local('data/')
        text = DataObtainer.clean_text(text, max_input_stream_length)
        pm = load_pm(storage_file)
        pm.train(text)
        pm.save_tsv(storage_file)
        print pm.generate_stream(200)
        total_time_mins = (time.time() - start_time) / 60
        rate_chars_min = round(len(text) / total_time_mins / 1000)
        print 'Total time taken to run this is ', round(total_time_mins, ndigits=2), \
            ' mins. Rate = ', rate_chars_min, ' K chars/min'


def default_small_trainer(storage_file):
    start_time = time.time()
    text = DataObtainer.get_random_book_local('data/')
    text = DataObtainer.clean_text(text, 10000)
    pm = load_pm(storage_file)
    pm.train(text)
    pm.generalize()
    pm.save_tsv(storage_file)
    print pm.generate_stream(200)
    total_time_mins = (time.time() - start_time) / 60
    rate_chars_min = round(len(text) / total_time_mins / 1000)
    print 'Total time taken to run this is ', round(total_time_mins, ndigits=2), \
        ' mins. Rate = ', rate_chars_min, ' K chars/min'


def online_trainer(storage_file):
    print 'Starting online training'
    for iteration in range(100):
        start_time = time.time()
        print 'Iteration number ' + str(iteration)
        text = DataObtainer.gutenberg_random_book()
        text = DataObtainer.clean_text(text, max_input_stream_length)
        pm = load_pm(storage_file)
        pm.train(text)
        pm.save_tsv(storage_file)
        print pm.generate_stream(200)
        total_time_mins = (time.time() - start_time) / 60
        rate_chars_min = round(len(text) / total_time_mins / 1000)
        print 'Total time taken to run this is ', round(total_time_mins, ndigits=2), \
            ' mins. Rate = ', rate_chars_min, ' K chars/min'


def sanity_check_run():
    pm = PopManager()
    text = 'hahaha this is a sanity check, just checking some text'
    pm.train(text)
    pm.train(text)
    pm.train(text)
    pm.train(text)
    print pm.generate_stream(5)
    print 'Everything OK'


if __name__ == '__main__':
    sanity_check_run()
