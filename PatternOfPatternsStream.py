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

Idea:
Refactoring: See if instead of current components, new components which are stronger can be set.
e.g. if pattern is ABCD = {ABC:D} but AB and CD are stronger then set ABCD = {AB:CD}
"""
import os
import time
import matplotlib.pyplot as plt
import numpy as np
import DataObtainer

# constants
max_input_stream_length = 1000000
starting_strength = 1000
maxlen_word = 20  # maximum pattern length
required_repeats = 5  # if seen less than this many times, patterns won't survive on the long run.
decay_strength_loss = 1  # loss of strength per time step.
feed_ratio = [0.5, 0.25, 0.25]  # ratio of self feed to child components feed. First self, next two children.


class Pop:
    def __init__(self, chars):
        self.unrolled_pattern = chars  # The actual characters that make up current pattern.
        self.strength = starting_strength
        self.first_component = None  # Children
        self.second_component = None

    def set_components(self, first_component, second_component):
        """
        Sets the children.
        """
        if not first_component or not second_component:
            raise Exception("component cannot be None")
        self.first_component = first_component
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
        previous_pop = self.patterns_collection[string[0]]
        i = 1
        while i < input_length - maxlen_word:
            for j in range(maxlen_word, 0, -1):  # how many chars to look ahead
                current_word = string[i:i + j]
                if current_word in self.patterns_collection:
                    current_pop = self.patterns_collection[current_word]
                    new_pattern = previous_pop.unrolled_pattern + current_word
                    if new_pattern not in self.patterns_collection:
                        self.patterns_collection[new_pattern] = Pop(new_pattern)
                        self.patterns_collection[new_pattern].set_components(previous_pop, current_pop)
                    else:
                        self.patterns_collection[new_pattern].feed(feed_strength_gain)
                    previous_pop = current_pop
                    i += j
                    break
            if i % 10 == 0 and i > starting_strength:  # Every now and then cull weak patterns
                self.cull(0)
        self.cull(0)
        return self.patterns_collection

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

    def status(self, show_strength):
        if show_strength:
            for key, pop in sorted(self.patterns_collection.iteritems(), key=lambda ng: ng[1].strength):
                print pop.__repr__()
            print 'Status of Pattern of patterns with ' + str(len(self.patterns_collection)) + ' pops \n'
        strengths = [pop.strength for i, pop in self.patterns_collection.iteritems()]
        lengths = [len(pop.unrolled_pattern) for i, pop in self.patterns_collection.iteritems()]
        plt.scatter(x=lengths, y=strengths)
        plt.title('Strengths vs Lengths (x axis)')
        plt.show()

    def save(self, filename):
        save_string = 'pattern, strength, component1, component2\n'
        for key, pop in sorted(self.patterns_collection.iteritems(), key=lambda ng: ng[1].strength):
            save_string += key + '\t' + str(pop.strength) + '\t'
            if pop.first_component:
                save_string += pop.first_component.unrolled_pattern
            save_string += '\t'
            if pop.second_component:
                save_string += pop.second_component.unrolled_pattern
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
    for iteration in range(2):
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
        print 'Total time taken to run this is ', round((time.time() - start_time) / 60, ndigits=2), ' mins'


if __name__ == '__main__':
    default_trainer('PatternStore/first_pattern.tsv')
