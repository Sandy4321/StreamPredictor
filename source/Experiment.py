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

    def train_and_perplexity(self, string):
        words = nltk.word_tokenize(string)
        sp = StreamPredictor.StreamPredictor()
        perplexity_list = sp.pop_manager.train_token_and_perplexity(words)
        plt.plot(perplexity_list)
        plt.show()


if __name__ == '__main__':
    text = DataObtainer.get_clean_text_from_file('../data/pride.txt', 1000000)
    experiment = Experiment()
    experiment.perplexity_experiment_load(text)
    # experiment.perplexity_experiment(text)
    # experiment.train_and_perplexity(text)
