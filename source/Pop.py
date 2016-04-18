from difflib import SequenceMatcher
import numpy as np

# Constants
decay_strength_loss = 1  # loss of strength per time step.
feed_ratio = [0.5, 0.25, 0.25]  # ratio of self feed to child components feed. First self, next two children.


class Pop:
    def __init__(self, chars):
        self.unrolled_pattern = chars  # The actual characters that make up current pattern.
        self.strength = 0
        self.first_component = None  # Children
        self.second_component = None
        self.first_child_parents = []
        self.belongs_to_category = None  # type Pop(), which category does this belong to?
        self.members_of_category = []  # Pop() List, who are the members of this category?

    def set_components(self, first_component, second_component):
        """
        Sets the children.
        """
        if not first_component or not second_component:
            raise Exception("component cannot be None")
        self.first_component = first_component
        first_component.first_child_parents.append(self)
        self.second_component = second_component

    def set_category(self, first_component, second_component):
        """
        Sets the member categories.
        """
        if not first_component or not second_component:
            raise Exception("component cannot be None")
        first_component.belongs_to_category = self
        second_component.belongs_to_category = self
        self.members_of_category.append(first_component)
        self.members_of_category.append(second_component)

    def get_sample(self):
        if len(self.members_of_category) < 1:
            return self.unrolled_pattern
        return np.random.choice(self.members_of_category).unrolled_pattern

    def feed(self, gain):
        self.strength += int(gain * feed_ratio[0])
        if gain > 2:
            if self.first_component:
                self.first_component.feed(int(gain * feed_ratio[1]))
            if self.second_component:
                self.second_component.feed(int(gain * feed_ratio[2]))

    def decay(self):
        self.strength -= decay_strength_loss

    def __repr__(self):
        out = self.unrolled_pattern + ': strength ' + str(self.strength)
        if self.first_component:
            out += '={ ' + self.first_component.unrolled_pattern + ': '
        if self.second_component:
            out += self.second_component.unrolled_pattern + '}'
        if self.belongs_to_category:
            out += ' # ' + self.belongs_to_category.unrolled_pattern
        return out

    def similarity(self, other_pop):
        if not (
                            self.first_component and self.second_component and other_pop.first_component and other_pop.second_component):
            return SequenceMatcher(None, self.unrolled_pattern, other_pop.unrolled_pattern).ratio()
        similarity1 = self.first_component.similarity(other_pop.first_component)
        similarity2 = self.second_component.similarity(other_pop.second_component)
        return (len(self.first_component.unrolled_pattern) * similarity1 + len(self.second_component.unrolled_pattern)
                * similarity2) / len(self.unrolled_pattern)

    def get_next_distribution(self):
        """ Gives the list of next predicted words and their associated probabilities.
        :return: List A, B. Where A is a list of strings, B is list of floats.
        """
        next_words = []
        strengths = []
        for parent_i in self.first_child_parents:
            if parent_i.second_component:
                next_pop = parent_i.second_component
                next_words.append(next_pop.get_sample())
                strengths.append(max(parent_i.strength, 0))
        total = sum(strengths)
        probabilities = np.array([float(i) / total for i in strengths])
        return next_words, probabilities

    def get_next_smallest_distribution(self):
        """
        Returns the smallest pattern that will come next.
        """
        next_words = []
        strengths = []
        for parent_i in self.first_child_parents:
            if parent_i.second_component:
                next_pop = parent_i.second_component
                while next_pop.first_component:
                    next_pop = next_pop.first_component
                next_words.append(next_pop.get_sample())
                strengths.append(max(parent_i.strength, 0))
        if len(next_words) == 0:
            if self.second_component:
                return self.second_component.get_next_smallest_distribution()
        total = sum(strengths)
        probabilities = np.array([float(i) / total for i in strengths])
        return next_words, probabilities

    def has_common_child(self, other_pop):
        if not (
                    self.first_component and self.second_component and other_pop.first_component and other_pop.second_component):
            return self.unrolled_pattern == other_pop.unrolled_pattern
        return self.first_component.has_common_child(other_pop.first_component) or \
               self.second_component.has_common_child(other_pop.second_component)

    def is_child(self, child):
        if child.unrolled_pattern == self.unrolled_pattern:
            return True
        if not self.second_component:
            return False
        return self.second_component.is_child(child) or self.first_component.is_child(child)

    def next_patterns(self):
        """ Gives the list of patterns that are likely to occur next. """
        if not self.first_child_parents:
            return []
        next_patterns = []
        for parent_i in self.first_child_parents:
            if parent_i.second_component:
                next_patterns.append(parent_i.second_component)
        return next_patterns
