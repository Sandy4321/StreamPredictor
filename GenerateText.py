from PatternOfPatternsStream import PopManager


if __name__ == '__main__':
    pm = PopManager()
    pm.load('PatternStore/HarryPotter.tsv')
    seed =raw_input('Enter seed word for generation')
    print pm.generate_stream(100, seed=seed)
