"""
Author: Abhishek Rao
"""
from streampredictor import category
from streampredictor import pop_manager
from streampredictor import constants
import logging


class Generalizer():
    """
    Responsible for generalizing patterns, finding categories etc. Checks the similarity of patterns.
    Where does it come from, where is it going. If two patterns have these same then they must be
    similar.
    """

    def __init__(self, pop_manager):
        """
        :type pop_manager: pop_manager.PopManager
        """
        self.pop_manager = pop_manager

    def generalize(self):
        """
        Ideally words that occur in same context should belong to same category.
        """
        print('Generalizing ..')
        pops_list = list(self.pop_manager.pattern_collection.values())
        for pop in pops_list:
            next_to_next = dict()
            for next_pop in pop.next_patterns():
                next_to_next[next_pop.unrolled_pattern] = next_pop.next_patterns()
            for next_key_a, next_list_a in next_to_next.items():
                for next_key_b, next_list_b in next_to_next.items():
                    if self.do_not_generalize(next_key_a, next_key_b):
                        continue
                    same_length = len(set(next_list_a).intersection(next_list_b))
                    passing_length = constants.generalize_intersection_ratio * min(len(next_list_a), len(next_list_b))
                    if same_length > passing_length and same_length > constants.generalize_common_required_count:
                        self.set_similarity(next_key_a, next_key_b)

    def do_not_generalize(self, first_string, second_string):
        if first_string == second_string:
            return True
        if len(''.join(e for e in first_string if e.isalnum())) < 3:
            return True
        if len(''.join(e for e in second_string if e.isalnum())) < 3:
            return True
        if self.pop_manager.pattern_collection[first_string].is_child(
                self.pop_manager.pattern_collection[second_string]) or \
                self.pop_manager.pattern_collection[second_string].is_child(
                    self.pop_manager.pattern_collection[first_string]):
            return True
        return False

    def set_similarity(self, first_pattern, second_pattern):
        if first_pattern == second_pattern:
            logging.info(first_pattern, ' and ', second_pattern, ' are same!')
            return
        first_pop = self.pop_manager.pattern_collection[first_pattern]
        second_pop = self.pop_manager.pattern_collection[second_pattern]
        if first_pop.has_common_child(second_pop):
            if first_pop.first_component and second_pop.first_component and second_pop.second_component \
                    and second_pop.second_component:
                self.set_similarity(first_pop.first_component.unrolled_pattern,
                                    second_pop.first_component.unrolled_pattern)
                self.set_similarity(first_pop.second_component.unrolled_pattern,
                                    second_pop.second_component.unrolled_pattern)
                return
        logging.info('Perhaps ', first_pattern, ' and ', second_pattern, ' are similar?')
        new_category_string = 'category {' + first_pattern + ':' + second_pattern + '}'
        if new_category_string not in self.pop_manager.pattern_collection:
            category_members = [self.pop_manager.pattern_collection[first_pattern],
                                self.pop_manager.pattern_collection[second_pattern]]
            new_category = category.Category(new_category_string, constants.new_category_strength, category_members)
            self.pop_manager.category_collection[new_category_string] = new_category
