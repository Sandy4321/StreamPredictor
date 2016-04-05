from PatternOfPatternsStream import Pop, PopManager
import DataObtainer


def fruit_generalization():
    print 'hello'
    pm = PopManager()
    pm.add_pop_string('apple')
    pm.add_pop_string('banana')
    text = DataObtainer.get_clean_text_from_file('data/Experimental/case.txt', 100000)
    pm.train(text)
    pm.refactor()
    # pm.generalize()
    # pm.train(text)
    # pm.generalize()
    # pm.train(text)
    # pm.generalize()
    print [i.belongs_to_category.__repr__() for i in pm.patterns_collection.values() if
           i.belongs_to_category is not None]
    pm.save_pb_plain('PatternStore/fruit_experiment.txt')
    pm.load_pb_plain('PatternStore/fruit_experiment.txt')

def simple_generation():
    pm = PopManager()
    pm.load_pb_plain('PatternStore/fruit_experiment_synthetic.txt')
    out = pm.generate_stream(100)
    print out

if __name__ == '__main__':
    # pm = PopManager()
    # pm.load_tsv('PatternStore/General_53MB.tsv')
    # pm.generalize()
    # print [i.belongs_to_category.__repr__() + '\n' for i in pm.patterns_collection.values() if
    #        i.belongs_to_category is not None]
    # pm.save_tsv('PatternStore/General_generalized.tsv')
    simple_generation()

