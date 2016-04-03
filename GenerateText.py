from PatternOfPatternsStream import PopManager


if __name__ == '__main__':
    pm = PopManager()
    pm.load_tsv('PatternStore/General.tsv')
    print pm.generate_stream(1000)
