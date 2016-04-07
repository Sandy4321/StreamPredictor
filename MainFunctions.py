import PopManager
import os
import DataObtainer
import time

max_input_stream_length = 10000000

def load_pm(storage_file):
    if os.path.isfile(storage_file):
        pm = PopManager.PopManager()
        pm.load_tsv(storage_file)
        print 'Loaded PopManager.PopManager from ', storage_file
    else:
        pm = PopManager.PopManager()
        print ' Created new PopManager.PopManager. Didnt find anything at ', storage_file
    return pm


def default_trainer(storage_file):
    for iteration in range(100):
        start_time = time.time()
        print 'Iteration number ' + str(iteration)
        text = DataObtainer.get_random_book_local('data/')
        text = DataObtainer.clean_text(text, max_input_stream_length)
        pm = load_pm(storage_file)
        pm.train(text)
        pm.save_tsv(storage_file)
        print pm.generate_stream(200)
        total_time_mins = (time.time() - start_time) / 60
        rate_chars_min = round(len(text) / total_time_mins / 1000)
        print 'Total time taken to run this is ', round(total_time_mins, ndigits=2), \
            ' mins. Rate = ', rate_chars_min, ' K chars/min'


def default_small_trainer(storage_file):
    start_time = time.time()
    text = DataObtainer.get_random_book_local('data/')
    text = DataObtainer.clean_text(text, 10000)
    pm = load_pm(storage_file)
    pm.train(text)
    pm.generalize()
    pm.save_tsv(storage_file)
    print pm.generate_stream(200)
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
        pm = load_pm(storage_file)
        pm.train(text)
        pm.save_tsv(storage_file)
        print pm.generate_stream(200)
        total_time_mins = (time.time() - start_time) / 60
        rate_chars_min = round(len(text) / total_time_mins / 1000)
        print 'Total time taken to run this is ', round(total_time_mins, ndigits=2), \
            ' mins. Rate = ', rate_chars_min, ' K chars/min'


def sanity_check_run():
    pm = PopManager.PopManager()
    text = 'hahaha this is a sanity check, just checking some text'
    pm.train(text)
    pm.train(text)
    pm.train(text)
    pm.train(text)
    print pm.generate_stream(5)
    print 'Everything OK'

