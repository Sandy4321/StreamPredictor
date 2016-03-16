"""
Pattern of patterns.

Kind of adaptive coding.
"""
import numpy as np

# constants
starting_strength = 1000
maxlen_word = 20
feed_strength_gain = 2048
decay_strength_loss = 1
max_input_stream_length = 1000000
feed_ratio = [0.6, 0.2, 0.2]


class Pop:
    def __init__(self, chars):
        self.unrolled_pattern = chars
        self.strength = starting_strength
        self.first_component = None
        self.second_component = None
        # print 'Created pop ' + self.unrolled_pattern

    def set_components(self, first_component, second_component):
        if not first_component or not second_component:
            raise Exception("component cannot be None")
        self.first_component = first_component
        self.second_component = second_component

    def feed(self, gain):
        self.strength += int(gain * feed_ratio[0] * len(self.unrolled_pattern))
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
        for common_word in ['and', 'but', 'the', 'of', 'when', 'where', 'in', 'that', 'to', 'it']:
            self.patterns_collection[common_word] = Pop(common_word)

    def set_components_from_string(self, pop, first_string, second_string):
        if not first_string or not second_string:
            raise Exception("component cannot be empty")
        if first_string in self.patterns_collection:
            pop.first_component = self.patterns_collection[first_string]
        if second_string in self.patterns_collection:
            pop.second_component = self.patterns_collection[second_string]

    def train(self, string):
        print 'Started training with string length ' + str(len(string))
        previous_word = string[0]
        char_set = set(string)
        for char in char_set:
            self.patterns_collection[char] = Pop(char)
        previous_pop = self.patterns_collection[previous_word]
        i = 1
        while i < len(string) - maxlen_word:
            for j in range(maxlen_word, 0, -1):
                current_word = string[i:i + j]
                if current_word in self.patterns_collection:
                    current_pop = self.patterns_collection[current_word]
                    self.patterns_collection[current_word].feed(feed_strength_gain)
                    i += j
                    new_pattern = previous_pop.unrolled_pattern + current_word
                    if new_pattern not in self.patterns_collection:
                        self.patterns_collection[new_pattern] = Pop(new_pattern)
                        self.patterns_collection[new_pattern].set_components(previous_pop, current_pop)
                    previous_pop = current_pop
                    break
            if i % 10 == 0 and i > starting_strength:
                self.cull()
            self.cull()
        return self.patterns_collection

    def cull(self):
        cull_list = []
        for key, ngram in self.patterns_collection.iteritems():
            ngram.decay()
            if ngram.strength < 0 and len(ngram.unrolled_pattern) > 1:
                cull_list.append(key)
        for cull_key in cull_list:
            # print 'Culling ' + cull_key
            self.patterns_collection.pop(cull_key)
            # Todo how ot remove components?

    def status(self):
        for key, ngram in sorted(self.patterns_collection.iteritems(), key=lambda ng: ng[1].strength):
            print ngram.__repr__()
        print 'Status of Pattern of patterns with ' + str(len(self.patterns_collection)) + ' pops \n'

    def save(self, filename):
        savestr = 'pattern, strength, component1, component2\n'
        for key, pop in sorted(self.patterns_collection.iteritems(), key=lambda ng: ng[1].strength):
            savestr += key + ',' + str(pop.strength) + ','
            if pop.first_component:
                savestr += pop.first_component.unrolled_pattern
            savestr += ','
            if pop.second_component:
                savestr += pop.second_component.unrolled_pattern
            savestr += '\n'
        with open(filename, mode='w') as file:
            file.write(savestr)
        print 'Saved file ' + filename

    def load(self, filename):
        with open(filename, mode='r') as file:
            all_lines = file.readlines()
            for lines in all_lines[1:]:
                elements = lines.split(',')
                key = elements[0]
                self.patterns_collection[key] = Pop(key)
                self.patterns_collection[key].strength = int(elements[1])
            for lines in all_lines[1:]:
                elements = lines.strip().split(',')
                key = elements[0]
                if elements[2] is not '' and elements[3] is not '':
                    self.set_components_from_string(self.patterns_collection[key], elements[2], elements[3])
        print 'Loaded file' + filename + ' with number of patterns = ' + str(len(self.patterns_collection))

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
        current_word = self.patterns_collection.values()[0] \
            if seed is None else seed
        for i in range(word_length):
            next_word = self.predict_next_word(current_word)
            if next_word == '':
                next_word = np.random.choice([pop.unrolled_pattern
                                              for key,pop in self.patterns_collection.iteritems()])
            generated_output += next_word
            current_word = next_word
        return generated_output

    def generate_default(self):
        self.load('patterns_of_pride.csv')
        output = self.generate_stream(100, 'The')
        print output


if __name__ == '__main__':
    test_string = 'abfacdabcadadabcdabcdafabcdabcdevabcdabcdadfaabcd;kjojafaabcd'
    with open('data/pride.txt', 'r') as myfile:
        data = myfile.read().replace('\n', '').replace(' ', '_')
        data = data[:max_input_stream_length]
        data = ''.join(e for e in data if e.isalnum() or e is '_')
    pm = PopManager()
    pm.train(data)
    pm.status()
    pm.save('patterns_of_pride.csv')
    pm.generate_default()
