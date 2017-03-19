import nltk
import urllib.request, urllib.error, urllib.parse
import time
import os
import random


def gutenberg_random_book():
    for i in range(100):
        book_number = random.randint(9, 2000)
        url = 'http://www.gutenberg.org/cache/epub/' + str(book_number) + '/pg' + str(book_number) + '.txt'
        response = urllib.request.urlopen(url)
        text = response.read()
        if len(text) > 1000 and is_english(text):
            print(('Got book from ', url))
            return text
        else:
            print(('Didnt get book, waiting for some time, seconds = ' + str(10 + book_number / 10)))
            time.sleep(10 + book_number / 10)


def is_english(text):
    english_words = ['here', 'there', 'where', 'some', 'and', 'but']
    for word in english_words:
        if word not in text:
            return False
    return True


def get_random_book_local(folder):
    file = random.choice(os.listdir(folder))
    with open(folder + file) as opened_file:
        return opened_file.read()


def get_clean_text_from_file(file, max_input_stream_length):
    with open(file) as opened_file:
        text = opened_file.read()
        return clean_text(text, max_input_stream_length)


def get_clean_words_from_file(file, max_input_length):
    with open(file) as opened_file:
        text = opened_file.read()
        clean_words = nltk.word_tokenize(clean_text(text))[:max_input_length]
        print('Cleaned words, some of the first few are ',clean_words[:5])
        return clean_words


def get_words_from_ptb(file, max_input_length):
    with open(file) as opened_file:
        text = opened_file.read().replace('\n', '')
        return text.split(' ')[:max_input_length]


def clean_text(text, max_input_length=10 ** 10000):
    text = text.replace('\n', ' ')
    max_length = min(max_input_length, len(text))
    rotation = random.randint(0, max_length)
    text = text[rotation:max_length] + text[:rotation]
    # make sure to remove # for category separation
    text = ''.join(e for e in text if e.isalnum() or e in '.?", <>')
    return text


def get_online_words(max_input_length):
    text = gutenberg_random_book()
    words = nltk.word_tokenize(clean_text(text, max_input_length))
    return words


def convert_words_to_id(words):
    """
    Converts words list to id list and returns id sequence, word2id and id2word dictionary.
    """
    unique_words = sorted(list(set(words)))
    print('Vocabulary size is ', len(unique_words))
    id2word = dict((id, word) for id, word in enumerate(unique_words))
    word2id = dict((i, j) for j, i in id2word.items())
    id_sequence = [word2id[word] for word in words]
    return id_sequence, word2id, id2word


def split_train_test(sequence):
    train_test_ratio = 0.7
    N = len(sequence)
    print('Total length of input sequence', N)
    train_length = int(train_test_ratio * N)
    return sequence[:train_length], sequence[train_length:]


def get_train_test_id_sequence_from_ptb_file(filename, max_words_limit):
    words = get_words_from_ptb(filename, max_input_length=max_words_limit)
    N = len(words)
    print('There are {0} words first few are {1}'.format(N, words[:10]))
    id_sequence, word2id, id2word = convert_words_to_id(words)
    train, test = split_train_test(id_sequence)
    print('There are {0} ids in train, first few are '.format(len(train)), train[:10])
    return train, test, len(word2id), word2id, id2word


def get_embedding_matrix(vocabulary_size, embedding_size):
    import tensorflow as tf
    with tf.device("/cpu:0"):
        embedding = tf.get_variable(
            "embedding", [vocabulary_size, embedding_size], dtype=tf.float32)
        return embedding


def convert_sequence_to_embedd_vectors(sequence, embedding):
    import tensorflow as tf
    embed_vectors = tf.nn.embedding_lookup(embedding, sequence)
    print('The embed vectors shape is ', embed_vectors.get_shape())
    return embed_vectors


def get_train_test_vectors_from_ptb_file(filename, max_words_limit, embedding_size):
    train_seq, test_seq, vocabulary_size, word2id, id2word = get_train_test_id_sequence_from_ptb_file(filename, max_words_limit)
    embedding = get_embedding_matrix(vocabulary_size=vocabulary_size, embedding_size=embedding_size)
    train_vectors = convert_sequence_to_embedd_vectors(sequence=train_seq, embedding=embedding)
    test_vectors = convert_sequence_to_embedd_vectors(sequence=test_seq, embedding=embedding)
    return train_vectors, test_vectors, vocabulary_size, train_seq, test_seq, word2id, id2word


def get_train_test_data(filename, max_words_limit, embedding_size):
    train_vectors, test_vectors, vocabulary_size, train_seq, test_seq, word2id, id2word = \
        get_train_test_vectors_from_ptb_file(filename, max_words_limit, embedding_size)
    train_x, train_y = create_targets(train_vectors)
    train_x_seq, train_y_seq = create_targets(train_seq)
    test_x, test_y = create_targets(test_vectors)
    test_x_seq, test_y_seq = create_targets(test_seq)
    return train_x, train_y, test_x, test_y, vocabulary_size, train_x_seq, train_y_seq, test_x_seq, test_y_seq, word2id, id2word


def create_targets(X):
    """ Create shifted to right version for predicting next word"""
    return X[:-1], X[1:]


if __name__ == '__main__':
    words = get_words_from_ptb('../data/ptb.test.txt', max_input_length=100)
    print(words)
    seq, word2id, id2word = convert_words_to_id(words)
    print(seq)
