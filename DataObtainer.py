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
        if len(text) > 1000:
            return text
        else:
            print 'Didnt get book, waiting for some time, seconds = ' + str(10 + book_number / 10)
            time.sleep(10 + book_number / 10)


def get_random_book_local():
    file = np.random.choice(os.listdir('data/'))
    with open('data/' + file) as opened_file:
        return opened_file.read()


def clean_text(text, max_input_stream_length):
    text= text.replace('\n', ' ')
    max_length = min(max_input_stream_length, len(text))
    rotation = np.random.randint(low=0, high=max_length, size=1)
    text = text[rotation:max_length] + text[:rotation]
    text = ''.join(e for e in text if e.isalnum() or e in '.?", ')
    return text


if __name__ == '__main__':
    text = get_random_book_local()
    print text
