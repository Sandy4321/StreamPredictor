import tensorflow as tf
import time
import numpy as np

try:
    from  DataObtainer import get_train_test_data
except:
    from .DataObtainer import get_train_test_data

max_grad_norm = 5
init_scale = 0.1
max_epochs = 2


def lstm_experiment():
    filename = '../data/ptb.test.txt'
    # get id sequence for train, test
    hidden_size = 100
    batch_size = 1
    train_x, train_y, test_x, test_y, vocabulary_size, train_x_seq, train_y_seq, test_x_seq, test_y_seq \
        = get_train_test_data(filename, 10 ** 3, embedding_size=hidden_size)

    # set up lstm model
    lstm = LSTMSingleLayer(hidden_size=hidden_size, vocab_size=vocabulary_size, batch_size=batch_size)
    # train model
    train_loss = lstm.train(train_x, train_y_seq)
    print(train_loss)
    # test perplexity on test


class LSTMSingleLayer():
    def __init__(self, hidden_size, vocab_size, batch_size):
        self.hidden_size = hidden_size
        self.batch_size = batch_size
        self.vocab_size = vocab_size
        self.model = tf.nn.rnn_cell.BasicLSTMCell(hidden_size, state_is_tuple=True)
        self.state = self.model.zero_state(batch_size=1, dtype=tf.float32)
        self.ph_x = tf.placeholder(dtype=tf.float32, shape=[batch_size, hidden_size], name="X")
        self.ph_y = tf.placeholder(dtype=tf.int32, shape=[batch_size], name="Y")

        self.output, self.state = self.model(inputs=self.ph_x, state=self.state)
        self.softmax_w = tf.get_variable(
            "softmax_w", [self.hidden_size, self.vocab_size], dtype=tf.float32)
        self.softmax_b = tf.get_variable("softmax_b", [self.vocab_size], dtype=tf.float32)
        logits = tf.matmul(self.output, self.softmax_w) + self.softmax_b
        loss = tf.nn.seq2seq.sequence_loss_by_example(
            [logits],
            [self.ph_y],
            [tf.ones(self.ph_y.get_shape(), dtype=tf.float32)])
        self.cost = cost = tf.reduce_sum(loss)

        self._lr = tf.Variable(0.0, trainable=False)
        tvars = tf.trainable_variables()
        grads, _ = tf.clip_by_global_norm(tf.gradients(cost, tvars),
                                          max_grad_norm)
        optimizer = tf.train.GradientDescentOptimizer(self._lr)
        self._train_op = optimizer.apply_gradients(
            zip(grads, tvars),
            global_step=tf.contrib.framework.get_or_create_global_step())

        self._new_lr = tf.placeholder(
            tf.float32, shape=[], name="new_learning_rate")
        self._lr_update = tf.assign(self._lr, self._new_lr)

    def train(self, X, Y):
        initializer = tf.random_uniform_initializer(-init_scale, init_scale)
        with tf.name_scope("Train"):
            with tf.variable_scope("Model", reuse=None, initializer=initializer):
                tf.scalar_summary("Training Loss", self.cost)
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            epoch_perplexities = []
            for epoch in range(max_epochs):
                print('Epoch number ', epoch)
                epoch_perplexities.append(self.run_epoch(session=sess, X=X, Y=Y))
        return epoch_perplexities

    def run_epoch(self, session, X, Y):
        start_time = time.time()
        current_state = session.run(self.model.zero_state(self.batch_size, dtype=np.float32))
        costs = 0.0
        iters = 0
        fetches = {
            "cost": self.cost,
            "state": self.state,
            "eval_op": self._train_op
        }
        epoch_size = int(X.get_shape()[0])
        print('Epoch size is ', epoch_size)

        for step in range(epoch_size):
            step_x = session.run(X[step])
            step_y = Y[step]
            feed_dict = {self.ph_x: step_x.reshape([self.batch_size, -1]),
                         self.ph_y: np.array(step_y).reshape([self.batch_size], ),
                         self.state: current_state}
            vals = session.run(fetches, feed_dict)
            cost = vals["cost"]
            current_state = vals["state"]
            costs += cost
            iters += self.batch_size
            if step % (epoch_size // 10) == 10:
                print("Completion %.3f perplexity: %.3f speed: %.0f wps" %
                      (step * 1.0 / epoch_size, np.exp(costs / iters),
                       iters * self.batch_size / (time.time() - start_time)))
        return np.exp(costs / iters)

    def test(self, X, Y):
        pass


if __name__ == '__main__':
    lstm_experiment()
