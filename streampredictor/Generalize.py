from . import DataObtainer
from .StreamPredictor import StreamPredictor


def fruit_generalization():
    print('hello')
    sp = StreamPredictor()
    sp.pop_manager.add_pop_string('apple')
    sp.pop_manager.add_pop_string('banana')
    text = DataObtainer.get_clean_text_from_file('data/Experimental/case.txt', 100000)
    sp.train_characters(text)
    sp.pop_manager.refactor()
    # sp.generalize()
    # sp.train(text)
    # sp.generalize()
    # sp.train(text)
    # sp.generalize()
    print([i.belongs_to_category.__repr__() for i in list(sp.pop_manager.patterns_collection.values()) if
           i.belongs_to_category is not None])
    sp.pop_manager.save_pb_plain('PatternStore/fruit_experiment.txt')
    sp.pop_manager.load_pb_plain('PatternStore/fruit_experiment.txt')


def simple_generation(generation_length=100):
    sp = StreamPredictor()
    sp.pop_manager.load_pb_plain('PatternStore/fruit_experiment_synthetic.txt')
    out = sp.generate_stream(generation_length)
    return out


def cat_dog_generalization():
    sp = StreamPredictor()
    sp.pop_manager.load_pb_plain('PatternStore/cat_dog_0.txt')
    sp.pop_manager.generalize()
    sp.pop_manager.save_pb_plain('PatternStore/cat_dog_gen.txt')


def cat_dog_generation():
    cat_dog_text = simple_generation(999)
    sp = StreamPredictor()
    sp.pop_manager.add_pop_string('cat')
    sp.pop_manager.add_pop_string('dog')
    sp.pop_manager.add_pop_string(' ate food. ')
    sp.pop_manager.add_pop_string('The ')
    for i in range(3):
        sp.train_characters(cat_dog_text)
        sp.pop_manager.save_pb_plain('PatternStore/cat_dog_' + str(i) + '.txt')
        generated = sp.generate_stream(100)
        print(generated)


def cat_dog_train_category():
    cat_dog_text = simple_generation(999)
    sp = StreamPredictor()
    sp.pop_manager.load_pb_plain('PatternStore/cat_dog_gen.txt')
    sp.train_characters(cat_dog_text)
    sp.pop_manager.save_pb_plain('PatternStore/cat_dog_gen2.txt')


if __name__ == '__main__':
    cat_dog_train_category()
