from streampredictor import FileManager
from streampredictor import Generalizer
from streampredictor import PopManager
from streampredictor import Pop
from streampredictor import constants
import random


class StreamPredictor:
    def __init__(self, pm=None):
        if pm:
            self.pop_manager = pm
        else:
            self.pop_manager = PopManager.PopManager()
        self.file_manager = FileManager.FileManager(self.pop_manager)
        self.generalizer = Generalizer.Generalizer(self.pop_manager.patterns_collection,
                                                   self.pop_manager.feed_strength_gain)
        print(self.pop_manager.stats())

    def train(self, sequence):
        self.pop_manager.setup(sequence)
        previous_pop = sequence[0]
        remaining_sequence = sequence[1:]
        i = 0
        while len(remaining_sequence) > 0:
            next_pop, remaining_sequence = self.pop_manager.get_next_pop(remaining_sequence)
            new_pop = Pop.combine(next_pop, previous_pop)
            self.pop_manager.ingest(new_pop)
            if i % constants.occasional_step_count == 0:
                self.occasional_step(i)

    def occasional_step(self, step_count):
        self.pop_manager.decay(constants.occasional_decay)
        self.pop_manager.cull(step_count)
        self.pop_manager.refactor()
