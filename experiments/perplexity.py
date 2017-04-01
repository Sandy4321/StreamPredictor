import sys
import matplotlib.pyplot as plt
import logging

sys.path.insert(0, '../streampredictor/')
sys.path.insert(0, '../')
from streampredictor.stream_predictor import StreamPredictor

# Parameters
input_text_file = '../Data/ptb.train.txt'
output_filename = '../PatternStore/ptb.train.tsv'
train_length = 10 ** 5
test_length = 10**4
logging.basicConfig(filename='../PatternStore/perplexity.log', level=logging.INFO)

# Experiment
with open(input_text_file, 'r') as f:
    input_words = f.read().split(' ')
input_words_length = len(input_words)
print('The file {0} has {1} words'.format(input_text_file, input_words_length))
if input_words_length < train_length + test_length:
    raise ValueError('The input words length {0} is less than train length {1} + test length {2}'
                     .format(input_words_length, train_length, test_length))
sp = StreamPredictor()
train_words = input_words[:train_length]
test_words = input_words[train_length:train_length+test_length]

sp.train(train_words)
sp.file_manager.save_tsv('%s' % output_filename)
perplexity_list = sp.calculate_perplexity(words=test_words)
plt.plot(perplexity_list)
plt.xlabel('Time')
plt.ylabel('Perplexity')
plt.title('Perplexity during training')
plt.show()
