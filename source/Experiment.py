import nltk
import matplotlib.pyplot as plt
import StreamPredictor
import DataObtainer


class Experiment:
    def perplexity_experiment(self, string):
        words = nltk.word_tokenize(string)
        word_count = len(words)
        train_count = int(0.99 * word_count)
        train_words = words[:train_count]
        test_words = words[train_count:]
        sp = StreamPredictor.StreamPredictor()
        sp.pop_manager.train_token(train_words)
        sp.file_manager.save_pb_plain('../PatternStore/pride_token2.txt')
        perplexity_list = sp.pop_manager.calculate_perplexity(test_words)
        plt.plot(perplexity_list)
        plt.show()

    def perplexity_experiment_load(self, string):
        words = nltk.word_tokenize(string)
        word_count = len(words)
        train_count = int(0.99 * word_count)
        test_words = words[train_count:]
        sp = StreamPredictor.StreamPredictor()
        sp.file_manager.load_pb_plain('../PatternStore/pride_token.txt')
        perplexity_list = sp.pop_manager.calculate_perplexity(test_words)
        plt.plot(perplexity_list)
        plt.show()

    @staticmethod
    def train_and_perplexity():
        words = DataObtainer.get_clean_words_from_file('../Data/pride.txt', 10**9)
        sp = StreamPredictor.StreamPredictor()
        perplexity_list, x_list = sp.pop_manager.train_token_and_perplexity(words)
        plt.plot(x_list, perplexity_list)
        plt.show()

    @staticmethod
    def generalize_token():
        sp = StreamPredictor.StreamPredictor()
        words = DataObtainer.get_clean_words_from_file('../Data/pride.txt', 10**9)
        sp.pop_manager.train_token(words)
        sp.generalizer.generalize()
        sp.file_manager.save_pb_plain('../PatternStore/pride_generalized.txt')


if __name__ == '__main__':
    # experiment.perplexity_experiment(text)
    # experiment.perplexity_experiment(text)
    Experiment.train_and_perplexity()
    # Experiment.generalize_token()
