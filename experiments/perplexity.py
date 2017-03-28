import sys
import matplotlib.pyplot as plt

sys.path.insert(0, '../streampredictor/')
sys.path.insert(0, '../')
from streampredictor.stream_predictor import StreamPredictor
from streampredictor import data_fetcher

input_text_file = '../Data/ptb.train.txt'
max_input_length = 10 ** 7
with open(input_text_file, 'r') as f:
    words = f.read().split(' ')[:max_input_length]
sp = StreamPredictor()
test_length = -1000
sp.train(words[:test_length], verbose=True)
sp.file_manager.save_tsv('../PatternStore/ptb.train.tsv')
perplexity_list = sp.calculate_perplexity(words=words[test_length:], verbose=True)
plt.plot(perplexity_list)
plt.xlabel('Time')
plt.ylabel('Perplexity')
plt.title('Perplexity during training')
plt.show()
