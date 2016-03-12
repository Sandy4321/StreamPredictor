"""
Classes for Living N-grams. The repeating ones live. Rest die.

Todos:
unique vectors management.
"""

# constants
import operator
import numpy as np
import keras

starting_ngram_strength = 100
feed_strength_gain = 100
maturation_strength_gain = 1000
max_length_ngram = 7
maturity_age = 2000
unique_vector_length = 1400
max_input_stream_length = 5000


class Ngram:
    def __init__(self, word):
        self.value = word
        self.length = len(self.value)
        self.strength = starting_ngram_strength * self.length
        self.age = 0
        self.matured = False
        self.maturation_number = None

    def __repr__(self):
        return self.value[::-1] + ': strength=' + str(self.strength) \
               + ' age=' + str(self.age) + '\n'

    def decay(self):
        self.age += 1
        self.strength -= 1

    def feed(self):
        self.strength += feed_strength_gain * self.length

    def kick(self):
        self.strength -= feed_strength_gain * self.length


class BankNgram:
    def __init__(self, savefilename):
        self.bank = dict()
        self.current_stream = []
        self.vacancy_indicator = [0] * unique_vector_length
        self.savefilename = savefilename

    def add_to_bank_string(self, new_string):
        """
        Adds a new ngram by adding the string.

        :param new_string: a string
        """
        if new_string in self.bank:
            self.bank[new_string].feed()
            prefix = new_string[:-1]
            if prefix in self.bank:
                self.bank[prefix].kick()
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
            # print 'Culling ' + cull_key
            if self.bank[cull_key].matured:
                print 'Mature ngram being killed. Name = ' + self.bank[cull_key].__repr__()
                self.vacancy_indicator[self.bank[cull_key].maturation_number] = 0
            self.bank.pop(cull_key)

    def cull_immature(self):
        cull_list = []
        for key, ngram in self.bank.iteritems():
            if not ngram.matured:
                cull_list.append(key)
        print 'Culling immature. Count = ' + str(len(cull_list))
        for cull_key in cull_list:
            self.bank.pop(cull_key)

    def check_maturation(self):
        for key, ngram in self.bank.iteritems():
            if ngram.matured:
                continue
            if ngram.age > maturity_age:
                try:
                    ngram.maturation_number = self.vacancy_indicator.index(0)
                    ngram.matured = True
                    ngram.strength += maturation_strength_gain * ngram.length
                    self.vacancy_indicator[ngram.maturation_number] = 1
                    print ngram.value[::-1] + " matured with maturation number " + str(ngram.maturation_number)
                except ValueError:
                    print 'No more space in vacancy indicator.'
                # if anything matured then mature and if limit exceeds, delete weakest mature.
                prefix = ngram.value[:-1]
                if prefix in self.bank:
                    self.bank[prefix].strength -= self.bank[prefix].length * maturation_strength_gain

    def status(self):
        print 'Status of ngram bank with ' + str(len(self.bank)) + ' ngrams \n'
        for key, ngram in sorted(self.bank.iteritems(), key=lambda ng: ng[1].strength):
            print ngram.__repr__()
        print 'Status of ngram bank with ' + str(len(self.bank)) + ' ngrams \n'

    def emit_features(self, string):
        vectors_list = []
        for char in list(string):
            feature_for_char = np.zeros([unique_vector_length, 1])
            strings_list = self.create_ngrams_strings(char)
            for string_ngram in strings_list:
                if string_ngram in self.bank:
                    feature_for_char[self.bank[string_ngram].maturation_number, 0] = 1
            vectors_list.append(feature_for_char)
        return np.hstack(vectors_list)

    def save(self):
        savestr = 'token, strength, age'
        for key, ngram in self.bank.iteritems():
            savestr += key + ',' + str(ngram.strength) + ',' + str(ngram.age) + '\n'
        with open(self.savefilename, mode='w') as file:
            file.write(savestr)
        print 'Saved file ' + self.savefilename

    def load(self):
        with open(self.savefilename, mode='r') as file:
            all_lines = file.readlines()
            for lines in all_lines[1:]:
                elements = lines.split(sep=',')
                key = elements[0]
                self.bank[key] = Ngram(key)
                self.bank[key].length = len(key)
                self.bank[key].strength = int(elements[1])
                self.bank[key].age = int(elements[2])
        print 'Loaded file'


class StreamPredictor:
    def __init__(self):
        self.n_gram_bank = BankNgram('FirstBank.csv')

    def train(self, input_stream):
        print 'Started training with stream length ' + str(len(input_stream))
        for char in list(input_stream):
            self.n_gram_bank.timestep(char)
        self.n_gram_bank.cull_immature()
        self.n_gram_bank.save()
        features = self.n_gram_bank.emit_features(input_stream)
        print 'Obtained features of shape ' + str(features.shape)

    def predict(self, input_stream):
        pass


if __name__ == '__main__':
    sp = StreamPredictor()
    with open('data/pride_small.txt', 'r') as myfile:
        data = myfile.read().replace('\n', '').replace(' ', '')
        data = data[:max_input_stream_length]
        sp.train(data)
    sp.n_gram_bank.status()
