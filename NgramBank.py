"""
Classes for Living N-grams. The repeating ones live. Rest die.
"""

# constants
starting_ngram_strength = 100
feed_strength_gain = 100


class Ngram:
    def __init__(self, word):
        self.value = word
        self.length = len(self.value)
        self.strength = starting_ngram_strength
        self.age = 0
        self.matured = False

    def __repr__(self):
        return self.value + " strength=" + str(self.strength)

    def decay(self):
        self.age += 1
        self.strength -= 1

    def feed(self):
        self.strength += feed_strength_gain


class BankNgram:
    def __init__(self):
        self.bank = dict()

    def add_to_bank_string(self, new_string):
        """
        Adds a new ngram by adding the string.

        :param new_string: a string
        """
        if new_string in self.bank:
            self.bank[new_string].feed()
        else:
            self.bank[new_string] = Ngram(new_string)

    def in_bank(self, ngram):
        return ngram.value in self.bank

    def decay(self):
        for key, ngram in self.bank.iteritems():
            ngram.decay()






