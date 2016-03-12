"""
Classes for Living N-grams. The repeating ones live. Rest die.

Todos:
unique vectors management.
"""

# constants
import operator

starting_ngram_strength = 100
feed_strength_gain = 100
max_length_ngram = 5
maturity_age = 3000


class Ngram:
    def __init__(self, word):
        self.value = word
        self.length = len(self.value)
        self.strength = starting_ngram_strength * self.length
        self.age = 0
        self.matured = False

    def __repr__(self):
        return self.value[::-1] + ' strength=' + str(self.strength) \
               + ' age=' + str(self.age) + '\n'

    def decay(self):
        self.age += 1
        self.strength -= 1

    def feed(self):
        self.strength += feed_strength_gain * self.length


class BankNgram:
    def __init__(self):
        self.bank = dict()
        self.current_stream = []

    def add_to_bank_string(self, new_string):
        """
        Adds a new ngram by adding the string.

        :param new_string: a string
        """
        if new_string in self.bank:
            self.bank[new_string].feed()
        else:
            self.bank[new_string] = Ngram(new_string)

    def ngram_in_bank(self, ngram):
        return ngram.value in self.bank

    def decay(self):
        for key, ngram in self.bank.iteritems():
            ngram.decay()

    def create_ngrams_strings(self, char):
        """
        Creates the strings of all lengths by taking in the current char, inserting
        into the current_stream queue, removing the oldest one.

        :param char:  string of length 1
        :return: List of strings with lengths 1 to max length
        """
        if len(self.current_stream) < max_length_ngram:
            self.current_stream = [char] + self.current_stream
        else:
            self.current_stream = [char] + self.current_stream[:-1]
        return [''.join(self.current_stream[:i])
                for i in range(1, 1 + len(self.current_stream))]

    def timestep(self, char):
        for string in self.create_ngrams_strings(char):
            self.add_to_bank_string(string)
        self.check_maturation()
        self.decay()
        self.cull()

    def cull(self):
        cull_list = []
        for key, ngram in self.bank.iteritems():
            if ngram.strength < 0:
                cull_list.append(key)
        for cull_key in cull_list:
            print 'Culling ' + cull_key
            self.bank.pop(cull_key)

    def check_maturation(self):
        for key, ngram in self.bank.iteritems():
            if ngram.matured:
                continue
            if ngram.age > maturity_age:
                ngram.matured = True
                print ngram.value[::-1] + " matured."
                # if anything matured then mature and if limit exceeds, delete weakest mature.

    def status(self):
        print 'Status of ngram bank with ' + str(len(self.bank)) + ' ngrams \n'
        for key, ngram in sorted(self.bank.iteritems(), key= lambda ng: ng[1].strength):
            print ngram.__repr__()
        print 'Status of ngram bank with ' + str(len(self.bank)) + ' ngrams \n'


class StreamPredictor:
    def __init__(self):
        self.n_gram_bank = BankNgram()

    def train(self, input_stream):
        print 'Started training with stream length ' + str(len(input_stream))
        for char in list(input_stream):
            self.n_gram_bank.timestep(char)

    def predict(self, input_stream):
        pass

if __name__ == '__main__':
    sp = StreamPredictor()
    with open('data/pride_small.txt', 'r') as myfile:
        data=myfile.read().replace('\n', '').replace(' ', '')
        data = data[:10000]
        sp.train(data)
    sp.n_gram_bank.status()

