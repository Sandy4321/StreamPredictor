import StreamPredictor
import os
import DataObtainer
import time

max_input_stream_length = 10000000


def load_sp(storage_file):
    sp = StreamPredictor.StreamPredictor()
    if os.path.isfile(storage_file):
        sp.file_manager.load_tsv(storage_file)
        print 'Loaded PopManager.PopManager from ', storage_file
    else:
        print ' Created new PopManager.PopManager. Didnt find anything at ', storage_file
    return sp


def default_trainer(storage_file):
    for iteration in range(100):
        start_time = time.time()
        print 'Iteration number ' + str(iteration)
        text = DataObtainer.get_random_book_local('data/')
        text = DataObtainer.clean_text(text, max_input_stream_length)
        sp = load_sp(storage_file)
        sp.train(text)
        sp.file_manager.save_tsv(storage_file)
        print sp.generate_stream(200)
        total_time_mins = (time.time() - start_time) / 60
        rate_chars_min = round(len(text) / total_time_mins / 1000)
        print 'Total time taken to run this is ', round(total_time_mins, ndigits=2), \
            ' mins. Rate = ', rate_chars_min, ' K chars/min'


def default_small_trainer(storage_file):
    start_time = time.time()
    text = DataObtainer.get_random_book_local('data/')
    text = DataObtainer.clean_text(text, 10000)
    sp = load_sp(storage_file)
    sp.train(text)
    sp.generalizer.generalize()
    sp.file_manager.save_tsv(storage_file)
    print sp.generate_stream(200)
    total_time_mins = (time.time() - start_time) / 60
    rate_chars_min = round(len(text) / total_time_mins / 1000)
    print 'Total time taken to run this is ', round(total_time_mins, ndigits=2), \
        ' mins. Rate = ', rate_chars_min, ' K chars/min'


def online_trainer(storage_file):
    print 'Starting online training'
    for iteration in range(100):
        start_time = time.time()
        print 'Iteration number ' + str(iteration)
        text = DataObtainer.gutenberg_random_book()
        text = DataObtainer.clean_text(text, max_input_stream_length)
        sp = load_sp(storage_file)
        sp.train(text)
        sp.file_manager.save_tsv(storage_file)
        print sp.generate_stream(200)
        total_time_mins = (time.time() - start_time) / 60
        rate_chars_min = round(len(text) / total_time_mins / 1000)
        print 'Total time taken to run this is ', round(total_time_mins, ndigits=2), \
            ' mins. Rate = ', rate_chars_min, ' K chars/min'


def sanity_check_run():
    sp = StreamPredictor.StreamPredictor()
    text = 'hahaha this is a sanity check, just checking some text'
    sp.train(text)
    sp.train(text)
    sp.train(text)
    sp.train(text)
    print sp.generate_stream(5)
    print 'Everything OK'
