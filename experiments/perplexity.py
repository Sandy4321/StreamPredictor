import sys
import matplotlib.pyplot as plt

sys.path.insert(0, '../streampredictor/')
sys.path.insert(0, '../')
from streampredictor.stream_predictor import StreamPredictor

# Parameters
input_text_file = '../Data/ptb.train.txt'
output_filename = '../PatternStore/ptb.train.tsv'
train_length = 10 ** 5
test_length = 10**4

# Experiment
with open(input_text_file, 'r') as f:
    input_words = f.read().split(' ')[:train_length]
sp = StreamPredictor()
train_words = input_words[:train_length]
test_words = input_words[train_length:train_length+test_length]

sp.train(train_words, verbose=True)
sp.file_manager.save_tsv('%s' % output_filename)
perplexity_list = sp.calculate_perplexity(words=test_words, verbose=True)
plt.plot(perplexity_list)
plt.xlabel('Time')
plt.ylabel('Perplexity')
plt.title('Perplexity during training')
plt.show()
