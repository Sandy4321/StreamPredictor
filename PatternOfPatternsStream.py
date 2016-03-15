"""
Pattern of patterns.

Kind of adaptive coding.
"""

# constants
starting_strength = 100
maxlen_word = 10
feed_strength_gain = 64
decay_strength_loss = 1
max_input_stream_length = 5000
feed_ratio = [0.5, 0.25, 0.25]

class Pop:
    def __init__(self, first_component, second_component):
        if first_component or second_component:
            raise Exception("component cannot be None")
        self.first_component = first_component
        self.second_component = second_component
        self.unrolled_pattern = first_component.unrolled_pattern + second_component.unrolled_patternt
        self.strength = starting_strength
        print 'Created pop ' + self.unrolled_pattern

    def create_from_components(self):


    def feed(self, gain):
        self.strength +=gain *feed_ratio[0]
        if gain > 2:
            self.first_component.feed(floor(gain*feed_ratio[1]))
            self.second_component.feed(floor(gain*feed_ratio[2]))


    def decay(self):
        self.strength -= decay_strength_loss

    def __repr__(self):
        return self.unrolled_pattern + ' strength ' + str(self.strength) + ' components ' +\
               self.first_component.unrolled_pattern + ' and ' + self.second_component.unrolled_patternt


class PopManager:
    def __init__(self):
        self.patterns_collection = dict()

    def train(self, string):
        previous_word = string[0]
        char_set = set(string)
        for char in char_set:
            self.patterns_collection[char] = Pop(char, None)
        for i in range(1, len(string) - maxlen_word):
            for j in range(maxlen_word, 0, -1):
                current_word = string[i:i+j]
                if current_word in self.patterns_collection:
                    current_pop = self.patterns_collection[current_word]
                    self.patterns_collection[current_word].feed(feed_strength_gain)
                    i += j
                    new_pattern = previous_pop.unrolled_pattern + current_word
                    if new_pattern not in self.patterns_collection:
                        self.patterns_collection[new_pattern] = Pop(current_pop, previous_pop)
                    previous_pop = current_pop
                    break
            self.cull()
        return self.patterns_collection

    def cull(self):
        cull_list = []
        for key, ngram in self.patterns_collection.iteritems():
            ngram.decay()
            if ngram.strength < 0:
                cull_list.append(key)
        for cull_key in cull_list:
            print 'Culling ' + cull_key
            self.patterns_collection.pop(cull_key)

    def status(self):
        for key, ngram in sorted(self.patterns_collection.iteritems(), key=lambda ng: ng[1].strength):
            print ngram.__repr__()
        print 'Status of Pattern of patterns with' + str(len(self.patterns_collection)) + ' pops \n'




if __name__ == '__main__':
    # test_string = 'abfacdabcadadabcdabcdafabcdabcdevabcdabcdadfaabcd;kjojafaabcd'
    with open('data/pride_small.txt', 'r') as myfile:
        data = myfile.read().replace('\n', '').replace(' ', '')
        data = data[:max_input_stream_length]
        pm = PopManager()
        pm.train(data)
        pm.status()
