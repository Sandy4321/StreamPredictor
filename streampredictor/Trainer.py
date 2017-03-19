def train(words, streampredictor):
    return streampredictor.pop_manager.train_token_and_perplexity(words)
