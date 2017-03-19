import os
import time
import matplotlib.pyplot as plt
import nltk

from streampredictor import DataObtainer
from streampredictor import StreamPredictor
from streampredictor import Trainer

max_input_stream_length = 10000000
storage_file = '../PatternStore/OnlineTokens.pb'


def load_sp(storage_file):
    sp = StreamPredictor.StreamPredictor()
    if os.path.isfile(storage_file):
        sp.file_manager.load_tsv(storage_file)
        print('Loaded PopManager.PopManager from ', storage_file)
    else:
        print(' Created new PopManager.PopManager. Didnt find anything at ', storage_file)
    return sp


def default_trainer(storage_file):
    for iteration in range(100):
        start_time = time.time()
        print('Iteration number ' + str(iteration))
        text = DataObtainer.get_random_book_local('data/')
        text = DataObtainer.clean_text(text, max_input_stream_length)
        sp = load_sp(storage_file)
        sp.train_characters(text)
        sp.file_manager.save_tsv(storage_file)
        print(sp.generate_stream(200))
        total_time_mins = (time.time() - start_time) / 60
        rate_chars_min = round(len(text) / total_time_mins / 1000)
        print('Total time taken to run this is ', round(total_time_mins, ndigits=2), \
            ' mins. Rate = ', rate_chars_min, ' K chars/min')


def default_small_trainer(storage_file):
    start_time = time.time()
    text = DataObtainer.get_random_book_local('data/')
    text = DataObtainer.clean_text(text, 10000)
    sp = load_sp(storage_file)
    sp.train_characters(text)
    sp.generalizer.generalize()
    sp.file_manager.save_tsv(storage_file)
    print(sp.generate_stream(200))
    total_time_mins = (time.time() - start_time) / 60
    rate_chars_min = round(len(text) / total_time_mins / 1000)
    print('Total time taken to run this is ', round(total_time_mins, ndigits=2), \
        ' mins. Rate = ', rate_chars_min, ' K chars/min')


def online_trainer(storage_file):
    print('Starting online training')
    for iteration in range(100):
        start_time = time.time()
        print('Iteration number ' + str(iteration))
        text = DataObtainer.gutenberg_random_book()
        text = DataObtainer.clean_text(text, max_input_stream_length)
        sp = load_sp(storage_file)
        sp.train_characters(text)
        sp.file_manager.save_tsv(storage_file)
        print(sp.generate_stream(200))
        total_time_mins = (time.time() - start_time) / 60
        rate_chars_min = round(len(text) / total_time_mins / 1000)
        print('Total time taken to run this is ', round(total_time_mins, ndigits=2), \
            ' mins. Rate = ', rate_chars_min, ' K chars/min')


def sanity_check_run():
    sp = StreamPredictor.StreamPredictor()
    text = 'hahaha this is a sanity check, just checking some text'
    sp.train_characters(text)
    sp.train_characters(text)
    sp.train_characters(text)
    sp.train_characters(text)
    print(sp.generate_stream(5))
    print('Everything OK')


def perplexity_experiment(string):
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


def perplexity_experiment_load(string):
    words = nltk.word_tokenize(string)
    word_count = len(words)
    train_count = int(0.99 * word_count)
    test_words = words[train_count:]
    sp = StreamPredictor.StreamPredictor()
    sp.file_manager.load_pb_plain('../PatternStore/pride_token.txt')
    perplexity_list = sp.pop_manager.calculate_perplexity(test_words)
    plt.plot(perplexity_list)
    plt.show()


def train_and_perplexity(input_text_file):
    max_input_length = 10 ** 9
    words = DataObtainer.get_clean_words_from_file(input_text_file, max_input_length)
    sp = StreamPredictor.StreamPredictor()
    Trainer.train(words=words, streampredictor=sp)
    perplexity_list, iteration = sp.pop_manager.train_token_and_perplexity(words)
    plt.plot(iteration, perplexity_list)
    plt.xlabel('Time')
    plt.ylabel('Perplexity')
    plt.title('Perplexity during training')
    plt.show()


def generalize_token():
    sp = StreamPredictor.StreamPredictor()
    words = DataObtainer.get_clean_words_from_file('../Data/pride.txt', 10 ** 9)
    sp.pop_manager.train_token(words)
    sp.generalizer.generalize()
    sp.file_manager.save_pb_plain('../PatternStore/pride_generalized.txt')


def online_token_perplexity_trainer():
    print('Starting online training with tokens and perplexity calculation')
    sp = StreamPredictor.StreamPredictor()
    if os.path.isfile(storage_file):
        sp.file_manager.load_pb(storage_file)
        print('Loaded PopManager.PopManager from ', storage_file)
    else:
        print(' Created new PopManager.PopManager. Didnt find anything at ', storage_file)
    for iteration in range(10):
        start_time = time.time()
        print('Iteration number ' + str(iteration))
        words = DataObtainer.get_online_words(10 ** 10)
        perplexity_over_training, training_time = sp.pop_manager.train_token_and_perplexity(words)
        plt.plot(training_time, perplexity_over_training, 'd-')
        plt.show()
        sp.file_manager.save_pb(storage_file)
        total_time_mins = (time.time() - start_time) / 60
        rate_words_min = round(len(words) / total_time_mins / 1000)
        print('Total time taken to run this is ', round(total_time_mins, ndigits=2), \
            ' mins. Rate = ', rate_words_min, ' K words/min')


if __name__ == '__main__':
    # sanity_check_run()
    input_text_file = '../Data/ptb.test.txt'
    train_and_perplexity(input_text_file)
