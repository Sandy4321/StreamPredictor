import numpy as np
from streampredictor import constants
from streampredictor import pop


class Generator():
    def __init__(self, pattern_collection):
        """
        Generates words from pattern collection

        :type pattern_collection:dict[str,pop.Pop]
        """
        self.pattern_collection = pattern_collection

    def generate_words(self, word_length, seed=None):
        """
        Returns the list of generated words.

        :type word_length: int
        :type seed: str
        :rtype: list[str]
        """
        print('Generating words with word count = ', word_length)
        if (seed is None) or (seed is ''):
            current_word = self.get_random_word()
        else:
            current_word = seed
        generated_output = [current_word]
        for i in range(word_length - 1):
            next_word = self.choose_next_word(generated_output)
            if next_word == '':
                next_word = self.get_random_word()
            generated_output.append(next_word)
        return generated_output

    def choose_next_word(self, previous_list_of_words):
        """
        Get the next word given previous list of words.

        :type previous_list_of_words:list[str]
        :rtype: str
        """
        current_pop = self.longest_pop(previous_list_of_words)
        words, probabilities = current_pop.get_next_words_distribution()
        if current_pop.belongs_to_category:
            category_words, category_probabilities = current_pop.belongs_to_category.get_next_words_distribution()
            words = words + category_words
            probabilities = np.hstack([0.5 * probabilities, 0.5 * category_probabilities])
        probabilities /= sum(probabilities)
        return np.random.choice(words, p=probabilities)

    def longest_pop(self, list_of_words):
        """
        Get the longest pop in the given list of words ending in the last word.

        :type list_of_words:list[str]
        :rtype: pop.Pop
        """
        end = len(list_of_words)
        start = max(0, end - constants.maximum_pattern_length)
        for j in range(start, end - 1):
            current_word = ''.join(list_of_words[j:])
            if current_word in self.pattern_collection:
                current_pop = self.pattern_collection[current_word]
                words, probabilities = current_pop.get_next_words_distribution()
                if len(words) < 1:
                    continue
                return current_pop
        return self.pattern_collection[list_of_words[-1]]

    def get_random_word(self):
        """
        Returns a random string from pattern collection

        :rtype: str
        """
        return np.random.choice(list(self.pattern_collection.values()))
