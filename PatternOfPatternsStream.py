"""
Pattern of patterns.

Kind of adaptive coding.
"""

# constants
starting_strength = 1000
maxlen_word = 10
feed_strength_gain = 256
decay_strength_loss = 1
max_input_stream_length = 100000
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
        self.strength += gain * feed_ratio[0] * len(self.unrolled_pattern)
        if gain > 2:
            if self.first_component:
                self.first_component.feed(round(gain * feed_ratio[1]))
            if self.second_component:
                self.second_component.feed(round(gain * feed_ratio[2]))

    def decay(self):
        self.strength -= decay_strength_loss

    def __repr__(self):
        out = ""
        if self.first_component:
            out += '{' + self.first_component.unrolled_pattern + ':'
        if self.second_component:
            out +=  self.second_component.unrolled_pattern + '}'
        return self.unrolled_pattern + ': strength ' + str(self.strength) + out
        # ' components ' + \ # self.first_component.unrolled_pattern + ' and ' + self.second_component.unrolled_patternt


class PopManager:
    def __init__(self):
        self.patterns_collection = dict()
        for common_word in ['and', 'but', 'the', 'of', 'when', 'where', 'in', 'that', 'to', 'it']:
            self.patterns_collection[common_word] = Pop(common_word)

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

    def status(self):
        for key, ngram in sorted(self.patterns_collection.iteritems(), key=lambda ng: ng[1].strength):
            print ngram.__repr__()
        print 'Status of Pattern of patterns with ' + str(len(self.patterns_collection)) + ' pops \n'


if __name__ == '__main__':
    # test_string = 'abfacdabcadadabcdabcdafabcdabcdevabcdabcdadfaabcd;kjojafaabcd'
    with open('data/pride.txt', 'r') as myfile:
        data = myfile.read().replace('\n', '').replace(' ', '')
        data = data[:max_input_stream_length]
        data = ''.join(e for e in data if e.isalnum() or e is '_')
        pm = PopManager()
        pm.train(data)
        pm.status()
