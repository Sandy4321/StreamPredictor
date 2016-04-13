import numpy as np
import urllib2
import time
import os


def gutenberg_random_book():
    for i in range(100):
        book_number = np.random.randint(low=9, high=2000, size=1)[0]
        url = 'http://www.gutenberg.org/cache/epub/' + str(book_number) + '/pg' + str(book_number) + '.txt'
        response = urllib2.urlopen(url)
        text = response.read()
        if len(text) > 1000 and is_english(text):
            return text
        else:
            print 'Didnt get book, waiting for some time, seconds = ' + str(10 + book_number / 10)
            time.sleep(10 + book_number / 10)

def is_english(text):
    english_words = ['here', 'there', 'where', 'some', 'and', 'but']
    for word in english_words:
        if word not in text:
            return False
    return True

def get_random_book_local(folder):
    file = np.random.choice(os.listdir(folder))
    with open(folder + file) as opened_file:
        return opened_file.read()

def get_clean_text_from_file(file, max_input_stream_length):
    with open(file) as opened_file:
        text = opened_file.read()
        return clean_text(text, max_input_stream_length)

def clean_text(text, max_input_stream_length):
    text = text.replace('\n', ' ')
    max_length = min(max_input_stream_length, len(text))
    rotation = np.random.randint(low=0, high=max_length, size=1)
    text = text[rotation:max_length] + text[:rotation]
    # make sure to remove # for category separation
    text = ''.join(e for e in text if e.isalnum() or e in '.?", ')
    return text


if __name__ == '__main__':
    text = get_random_book_local('../data')
    print text
