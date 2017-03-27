import sys

sys.path.insert(0, '../streampredictor/')
sys.path.insert(0, '../')
from streampredictor.stream_predictor import StreamPredictor

sp = StreamPredictor()
sp.occasional_step = 100

input_text = 'hello how are you hello who are you'
input_words = input_text.split(' ') * 1000
print(input_words[:20])
sp.train(input_words, verbose=True)
print('\n\nThe generated words are ')
print(sp.generate(20))
print('\nEnd of generated words\n')
sp.file_manager.save_tsv('../PatternStore/simple_generate.tsv')
print(sp.pop_manager.pattern_collection)
