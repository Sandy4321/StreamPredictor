from PopManager import PopManager
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

def simple_generation(generation_length=100):
    pm = PopManager()
    pm.load_pb_plain('PatternStore/fruit_experiment_synthetic.txt')
    out = pm.generate_stream(generation_length)
    return out

def cat_dog_generalization():
    pm = PopManager()
    pm.load_pb_plain('PatternStore/cat_dog_0.txt')
    pm.generalize()
    pm.save_pb_plain('PatternStore/cat_dog_gen.txt')


def cat_dog_generation():
    cat_dog_text = simple_generation(999)
    pm = PopManager()
    pm.add_pop_string('cat')
    pm.add_pop_string('dog')
    pm.add_pop_string(' ate food. ')
    pm.add_pop_string('The ')
    for i in range(3):
        pm.train(cat_dog_text)
        pm.save_pb_plain('PatternStore/cat_dog_' + str(i) + '.txt')
        generated = pm.generate_stream(100)
        print generated

def cat_dog_train_category():
    cat_dog_text = simple_generation(999)
    pm = PopManager()
    pm.load_pb_plain('PatternStore/cat_dog_gen.txt')
    pm.train(cat_dog_text)
    pm.save_pb_plain('PatternStore/cat_dog_gen2.txt')


if __name__ == '__main__':
    cat_dog_train_category()
