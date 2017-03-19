from streampredictor import FileManager
from streampredictor import Pop
from streampredictor import PopManager
from streampredictor import constants


class StreamPredictor:
    def __init__(self, pm=None):
        if pm:
            self.pop_manager = pm
        else:
            self.pop_manager = PopManager.PopManager()
        self.file_manager = FileManager.FileManager(self.pop_manager)
        print(self.pop_manager.stats())

    def train(self, list_of_words):
        self.pop_manager.setup(list_of_words)
        previous_pop = self.pop_manager.patterns_collection[list_of_words[0]]
        remaining_sequence = list_of_words[1:]
        i = 0
        while len(remaining_sequence) > 0:
            next_pop, remaining_sequence = self.pop_manager.get_next_pop(remaining_sequence)
            new_pop = Pop.combine(next_pop, previous_pop)
            self.pop_manager.ingest(new_pop)
            if i % constants.occasional_step_count == 0:
                self.occasional_step(i)

    def occasional_step(self, step_count):
        self.pop_manager.occasional_step(step_count)

    def generate(self, word_length, seed=None):
        return self.pop_manager.generate_words(word_length, seed=None)

    def calculate_perplexity(self, words):
        return self.pop_manager.calculate_perplexity(words=words, verbose=False)
