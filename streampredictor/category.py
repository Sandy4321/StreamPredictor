from streampredictor import pop
import random


class Category:
    def __init__(self, name, strength, members):
        """
        :type name: str
        :type strength: int
        :type members: list[pop.Pop]
        """
        self.name = name
        self.strength = strength
        self.members = members

    def add_to_category(self, pop_list):
        """
        Add list of pops to members of category

        :type pop_list: list[pop.Pop]
        :rtype: None
        """
        for pop in pop_list:
            self.members.append(pop)
            pop.belongs_to_category.append(self)

    def get_sample(self):
        return random.choice(self.members).get_sample()
