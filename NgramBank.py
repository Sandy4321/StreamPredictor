"""
Classes for Living N-grams. The repeating ones live. Rest die.

Todos:
unique vectors management.
"""

# constants
starting_ngram_strength = 100
feed_strength_gain = 100
max_length_ngram = 10
maturity_age = 300


class Ngram:
    def __init__(self, word):
        self.value = word
        self.length = len(self.value)
        self.strength = starting_ngram_strength * self.length
        self.age = 0
        self.matured = False

    def __repr__(self):
        return self.value + " strength=" + str(self.strength)

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

    def create_ngrams(self, char):
        """
        Creates the ngrams of all lengths by taking in the current char, inserting
        into the curent_stream queue, removing the oldest one.

        :param char:  string of length 1
        :return: List of ngrams with lengths 1 to max length
        """
        self.current_stream = [char] + self.current_stream[:-1]
        return [Ngram(''.join(self.current_stream[:i]))
                for i in range(1, 1 + len(self.current_stream))]

    def timestep(self, char):
        for ngram in self.create_ngrams(char):
            self.add_to_bank_string(ngram)
        self.check_maturation()
        self.decay()
        self.cull()

    def cull(self):
        cull_list = []
        for key, ngram in self.bank.iteritems():
            if ngram.strength < 0:
                cull_list.append(key)
        for cull_key in cull_list:
            self.bank.pop(cull_key)

    def check_maturation(self):
        for key, ngram in self.bank.iteritems():
            if ngram.age > maturity_age:
                ngram.matured = True
                print ngram.value + " matured."
                # if anything matured then mature and if limit exceeds, delete weakest mature.


class StreamPredictor:
    def train(self, input_stream):
        pass

    def predict(self, input_stream):
        pass
