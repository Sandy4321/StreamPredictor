"""
Contains collection of PoPs and has multi step predict.
Generalization
"""
import PatternOfPatternsStream


class CPoP:
    def __init__(self):
        self.my_pop_list = [] # collection of PoPs

    def has_pattern(self, pattern):
        return False

    def prediction_list(self):
