from PatternOfPatternsStream import PopManager


if __name__ == '__main__':
    pm = PopManager()
    pm.load('PatternStore/HarryPotter.tsv')
    print pm.generate_stream(100)
