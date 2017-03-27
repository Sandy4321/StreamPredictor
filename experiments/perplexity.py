import sys
import matplotlib.pyplot as plt

sys.path.insert(0, '../streampredictor/')
sys.path.insert(0, '../')
from streampredictor.stream_predictor import StreamPredictor
from streampredictor import data_fetcher

input_text_file = '../Data/ptb.test.txt'
max_input_length = 10 ** 4
words = data_fetcher.get_clean_words_from_file(input_text_file, max_input_length)
sp = StreamPredictor()
test_length = -1000
sp.train(words[:test_length])
sp.file_manager.save_tsv('../PatternStore/ptb.tsv')
perplexity_list = sp.calculate_perplexity(words=words[test_length:], verbose=True)
plt.plot(perplexity_list)
plt.xlabel('Time')
plt.ylabel('Perplexity')
plt.title('Perplexity during training')
plt.show()
