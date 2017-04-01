import logging
import random
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, '../streampredictor/')
sys.path.insert(0, '../')
from streampredictor.stream_predictor import StreamPredictor


# Experiment
def perplexity_experiment(input_text_file, train_length, test_length, output_filename):
    with open(input_text_file, 'r') as f:
        input_words = f.read().replace('\n', '').replace('  ', ' ').split(' ')
    input_words_length = len(input_words)
    print('The file {0} has {1} words'.format(input_text_file, input_words_length))
    if input_words_length < train_length + test_length:
        raise ValueError('The input words length {0} is less than train length {1} + test length {2}'
                         .format(input_words_length, train_length, test_length))
    random_rotation = random.randint(0, input_words_length)
    input_words = input_words[random_rotation:] + input_words[:random_rotation]
    train_words = input_words[:train_length]
    test_words = input_words[train_length:train_length + test_length]
    sp = StreamPredictor()
    perplexity_list = sp.train_and_test(train_words, test_words)
    sp.file_manager.save(output_filename, output_filename + 'category.tsv')
    return sp, perplexity_list


if __name__ == '__main__':
    # Parameters
    input_text_file = '../Data/ptb.train.txt'
    output_filename = '../PatternStore/ptb.train.tsv'
    train_length = 8 * 10 ** 5
    test_length = 8 * 10 ** 3
    logging.basicConfig(filename='../PatternStore/perplexity.log', level=logging.INFO)

    # Experiment
    sp, perplexity_list = perplexity_experiment(input_text_file, train_length, test_length, output_filename)
    plt.plot(perplexity_list)
    plt.xlabel('Time')
    plt.ylabel('Perplexity')
    plt.title('Perplexity during training')
    plt.show()
