import tensorflow as tf

try:
    from  DataObtainer import get_train_test_data
except:
    from .DataObtainer import get_train_test_data


def lstm_experiment():
    filename = '../data/ptb.test.txt'
    # get id sequence for train, test
    hidden_size = 100
    train_x, train_y, test_x, test_y, vocabulary_size = get_train_test_data(filename, 10 ** 3,
                                                                            embedding_size=hidden_size)

    lstm = LSTMSingleLayer(hidden_size=hidden_size, vocab_size=vocabulary_size)
    ph_x, ph_y = tf.plac
    lstm.train(train_x, train_y)
    # set up lstm model
    # train model
    # test perplexity on test


class LSTMSingleLayer():
    def __init__(self, hidden_size, vocab_size):
        self.hidden_size = hidden_size
        self.vocab_size = vocab_size
        self.model = tf.nn.rnn_cell.BasicLSTMCell(hidden_size, state_is_tuple=True)
        self.state = self.model.zero_state(batch_size=1, dtype=tf.float32)

    def train(self, X, Y):
        self.output = self.model(inputs=X, state=self.state)
        self.softmax_w = tf.get_variable(
            "softmax_w", [self.hidden_size, self.vocab_size], dtype=tf.float32)
        self.softmax_b = tf.get_variable("softmax_b", [self.vocab_size], dtype=tf.float32)
        logits = tf.matmul(self.output, self.softmax_w) + self.softmax_b
        loss = tf.nn.seq2seq.sequence_loss_by_example(
            [logits],
            [tf.reshape(Y, [-1])],
            [tf.ones(1, dtype=tf.float32)])
        self._cost = cost = tf.reduce_sum(loss)

    def test(self, X, Y):
        pass


if __name__ == '__main__':
    lstm_experiment()
