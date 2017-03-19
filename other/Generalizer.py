"""
Author: Abhishek Rao
"""
from streampredictor import Pop


class Generalizer():
    """
    Responsible for generalizing patterns, finding categories etc. Checks the similarity of patterns.
    Where does it come from, where is it going. If two patterns have these same then they must be
    simlar.
    """

    def __init__(self, patterns_collection, feed_strength_gain):
        self.patterns_collection = patterns_collection
        self.generalize_intersection_ratio = 0.75
        self.generalize_common_required_count = 2
        self.feed_strength_gain = feed_strength_gain

    def do_not_generalize(self, first_string, second_string):
        if first_string == second_string:
            return True
        if len(''.join(e for e in first_string if e.isalnum())) < 3:
            return True
        if len(''.join(e for e in second_string if e.isalnum())) < 3:
            return True
        if self.patterns_collection[first_string].is_child(self.patterns_collection[second_string]) or \
                self.patterns_collection[second_string].is_child(self.patterns_collection[first_string]):
            return True
        return False

    def similarity_all(self):
        for key1, pop1 in self.patterns_collection.items():
            for key2, pop2 in self.patterns_collection.items():
                print('Similarity of ', pop1.unrolled_pattern, ' and ', pop2.unrolled_pattern, ' is ', pop1.similarity(
                    pop2))

    def generalize(self):
        print('Generalizing ..')
        pops_list = list(self.patterns_collection.values())
        for pop in pops_list:
            next_to_next = dict()
            for next_pop in pop.next_patterns():
                next_to_next[next_pop.unrolled_pattern] = next_pop.next_patterns()
            for next_key_a, next_list_a in next_to_next.items():
                for next_key_b, next_list_b in next_to_next.items():
                    if self.do_not_generalize(next_key_a, next_key_b):
                        continue
                    same_length = len(set(next_list_a).intersection(next_list_b))
                    passing_length = self.generalize_intersection_ratio * min(len(next_list_a), len(next_list_b))
                    if same_length > passing_length and same_length > self.generalize_common_required_count:
                        self.set_similarity(next_key_a, next_key_b)

    def set_similarity(self, first_pattern, second_pattern):
        if first_pattern == second_pattern:
            print(first_pattern, ' and ', second_pattern, ' are same!')
            return
        first_pop = self.patterns_collection[first_pattern]
        second_pop = self.patterns_collection[second_pattern]
        if first_pop.has_common_child(second_pop):
            if first_pop.first_component and second_pop.first_component and second_pop.second_component \
                    and second_pop.second_component:
                self.set_similarity(first_pop.first_component.unrolled_pattern,
                                    second_pop.first_component.unrolled_pattern)
                self.set_similarity(first_pop.second_component.unrolled_pattern,
                                    second_pop.second_component.unrolled_pattern)
                return
        print('Perhaps ', first_pattern, ' and ', second_pattern, ' are similar?')
        new_category_string = 'category with ' + first_pattern + ' and ' + second_pattern
        if new_category_string not in self.patterns_collection:
            new_category = Pop.Pop(new_category_string)
            self.patterns_collection[new_category_string] = new_category
            new_category.set_category(self.patterns_collection[first_pattern],
                                      self.patterns_collection[second_pattern])
        self.patterns_collection[new_category_string].feed(self.feed_strength_gain)
