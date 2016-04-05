"""
A class that operates using natural language.

Each sentence will be decomposed into known operators and then operated to create new operator out of given sentence.
Realizes my dream of having data and operator in same space, much better than visuals.
"""


class LanguageOperator:
    def __init__(self, description):
        self.description = description
        self.property = dict()

    def previous_next(self, previous, next):
        pass



class LanguageManager:
    def __init__(self):
        self.collection = dict()
        is_operator = 'is'
        self.collection[is_operator] = LanguageOperator(is_operator)
