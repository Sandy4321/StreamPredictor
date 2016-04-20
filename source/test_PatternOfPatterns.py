import os
from unittest import TestCase

import DataObtainer
from Pop import Pop
from StreamPredictor import StreamPredictor

test_pb = '../PatternStore/test.pb'
test_pb_plain = '../PatternStore/test.txt'
training_text = 'cat hat mat bat sat in the barn'


class TestPatternOfPatterns(TestCase):
    def get_sample(self):
        sample = StreamPredictor()
        sample.train(training_text)
        return sample

    def test_save(self):
        sample = self.get_sample()
        sample.file_manager.save_tsv(test_pb)
        self.assertTrue(os.path.isfile(test_pb))

    def test_load(self):
        self.test_save()
        empty_sample = StreamPredictor()
        self.assertFalse(len(empty_sample.pop_manager.patterns_collection) > 10)
        empty_sample.file_manager.load_tsv(test_pb)
        self.assertTrue(len(empty_sample.pop_manager.patterns_collection) > 10)

    def test_save_pb(self):
        sample = self.get_sample()
        sample.file_manager.save_pb(test_pb)
        self.assertTrue(os.path.isfile(test_pb))

    def test_save_pb_plain(self):
        sample = self.get_sample()
        sample.file_manager.save_pb_plain(test_pb_plain)
        self.assertTrue(os.path.isfile(test_pb_plain))

    def test_load_pb(self):
        self.test_save_pb()
        empty_sample = StreamPredictor()
        self.assertFalse(len(empty_sample.pop_manager.patterns_collection) > 10)
        empty_sample.file_manager.load_pb(test_pb)
        self.assertTrue(len(empty_sample.pop_manager.patterns_collection) > 10)

    def test_load_pb_plain(self):
        self.test_save_pb_plain()
        empty_sample = StreamPredictor()
        self.assertFalse(len(empty_sample.pop_manager.patterns_collection) > 10)
        empty_sample.file_manager.load_pb_plain(test_pb_plain)
        self.assertTrue(len(empty_sample.pop_manager.patterns_collection) > 10)

    def test_train_increases_patterns(self):
        sample = self.get_sample()
        pattern_count = len(sample.pop_manager.patterns_collection)
        sample.train(training_text)
        self.assertGreater(len(sample.pop_manager.patterns_collection), pattern_count)

    def test_save_load_equal(self):
        sample = self.get_sample()
        sample.pop_manager.patterns_collection['karma'] = Pop('karma')
        first_string = sample.pop_manager.status()
        sample.file_manager.save_pb(test_pb)
        second = StreamPredictor()
        second.file_manager.load_pb(test_pb)
        second_string = second.pop_manager.status()
        self.assertEqual(first_string, second_string)

    def test_find_next_pattern(self):
        sample = self.get_sample()
        small_pattern = 'somew'
        big_pattern = small_pattern + ' some random text'
        sample.pop_manager.patterns_collection[small_pattern] = Pop(small_pattern)
        found_pattern = sample.pop_manager.find_next_pattern(big_pattern)
        self.assertEqual(found_pattern.unrolled_pattern, small_pattern)
        small_pattern = 'somewhat'
        big_pattern = small_pattern + ' some random text'
        sample.pop_manager.patterns_collection[small_pattern] = Pop(small_pattern)
        found_pattern = sample.pop_manager.find_next_pattern(big_pattern)
        self.assertEqual(found_pattern.unrolled_pattern, small_pattern)
        small_pattern = 'somewhatapa'
        big_pattern = small_pattern + ' some random text'
        sample.pop_manager.patterns_collection[small_pattern] = Pop(small_pattern)
        found_pattern = sample.pop_manager.find_next_pattern(big_pattern)
        self.assertEqual(found_pattern.unrolled_pattern, small_pattern)

    def test_join_pattern(self):
        sample = StreamPredictor()
        cat_ate_ = Pop('The cat ate ')
        fruit = Pop('fruit')
        banana = Pop('banana')
        strawberry = Pop('strawberry')
        sample.pop_manager.add_pop(cat_ate_)
        sample.pop_manager.add_pop(fruit)
        sample.pop_manager.add_pop(banana)
        sample.pop_manager.add_pop(strawberry)
        banana.belongs_to_category = fruit
        strawberry.belongs_to_category = fruit
        sample.pop_manager.join_pattern(cat_ate_, banana, found_pattern_feed_ratio=1)
        self.assertTrue((cat_ate_.unrolled_pattern + fruit.unrolled_pattern) in sample.pop_manager.patterns_collection)

    def test_generate_stream(self):
        sample = self.get_sample()
        generated = sample.generate_stream(10)
        self.assertGreater(len(generated), 9)

    # def test_generailze(self):
    #     sp = StreamPredictor()
    #     sp.pop_manager.add_pop_string('apple')
    #     sp.pop_manager.add_pop_string('banana')
    #     text = DataObtainer.get_clean_text_from_file('data/Experimental/case.txt', 100000)
    #     sp.pop_manager.train(text)
    #     sp.pop_manager.generalize()
    #     print [i.belongs_to_category.__repr__() for i in sp.pop_manager.patterns_collection.values() if
    #            i.belongs_to_category is not None]
    #     self.assertTrue(sp.pop_manager.patterns_collection['apple'].
    #                     belongs_to_category is sp.pop_manager.patterns_collection['banana'].belongs_to_category)

    def test_change_component(self):
        a, ab, abc, sp, b, c, bc = self.setup_simple_patterns()
        self.assertTrue(len(a.first_child_parents) == 1)
        self.assertTrue(len(ab.first_child_parents) == 0)
        sp.pop_manager.change_components_string('ab', 'c', abc)
        self.assertTrue(len(a.first_child_parents) == 0)
        self.assertTrue(len(sp.pop_manager.patterns_collection['ab'].first_child_parents) == 1)

    def setup_simple_patterns(self):
        sp = StreamPredictor()
        abc = Pop('abc')
        ab = Pop('ab')
        bc = Pop('bc')
        a = Pop('a')
        b = Pop('b')
        c = Pop('c')
        sp.pop_manager.add_pop(abc)
        sp.pop_manager.add_pop(bc)
        sp.pop_manager.add_pop(ab)
        sp.pop_manager.add_pop(a)
        sp.pop_manager.add_pop(b)
        sp.pop_manager.add_pop(c)
        abc.set_components(a, bc)
        return a, ab, abc, sp, b, c, bc

    def test_is_right_child(self):
        a, ab, abc, sp, b, c, bc = self.setup_simple_patterns()
        self.assertTrue(abc.is_child(bc))
        self.assertFalse(abc.is_child(c))

    def test_has_common_child(self):
        sp, ab, abxe, abyd, xe, yd = self.form_simple_tree()
        self.assertTrue(abxe.has_common_child(abyd))
        self.assertTrue(ab.has_common_child(ab))
        self.assertFalse(xe.has_common_child(yd))

    def form_simple_tree(self):
        sp = StreamPredictor()
        abxe = Pop('abxe')
        abxe.strength = 600
        abyd = Pop('abyd')
        abyd.strength = 400
        ab = Pop('ab')
        xe = Pop('xe')
        yd = Pop('yd')
        a = Pop('a')
        b = Pop('b')
        d = Pop('d')
        e = Pop('e')
        x = Pop('x')
        y = Pop('y')
        sp.pop_manager.add_pop(abxe)
        sp.pop_manager.add_pop(ab)
        sp.pop_manager.add_pop(xe)
        sp.pop_manager.add_pop(yd)
        sp.pop_manager.add_pop(a)
        sp.pop_manager.add_pop(b)
        sp.pop_manager.add_pop(d)
        sp.pop_manager.add_pop(e)
        sp.pop_manager.add_pop(x)
        sp.pop_manager.add_pop(y)
        xe.set_components(x, e)
        yd.set_components(y, d)
        abxe.set_components(ab, xe)
        abyd.set_components(ab, yd)
        return sp, ab, abxe, abyd, xe, yd

    def test_pop_manager_repr(self):
        sample = self.get_sample()
        spm = sample.pop_manager.__repr__()
        self.assertGreater(len(spm), 10)

    def test_pop_get_next_prediction(self):
        sp, ab, abxe, abyd, xe, yd = self.form_simple_tree()
        words, probabilites = ab.get_next_distribution()
        self.assertTrue(len(words) > 1)
        self.assertEqual(probabilites[0], 0.6)
        self.assertEqual(probabilites[1], 0.4)
        self.assertTrue('xe' in words)
        self.assertTrue('yd' in words)

    def test_pop_get_smallest_next_prediction(self):
        sp, ab, abxe, abyd, xe, yd = self.form_simple_tree()
        words, probabilites = ab.get_next_smallest_distribution()
        self.assertTrue(len(words) > 1)
        self.assertEqual(probabilites[0], 0.6)
        self.assertEqual(probabilites[1], 0.4)
        self.assertTrue('x' in words)
        self.assertTrue('y' in words)

    def test_perplexity_step(self):
        sp, ab, abxe, abyd, xe, yd = self.form_simple_tree()
        words = ['ab', 'x']
        previous_words = ['ab']
        actual_next_word = 'x'
        N = 1
        log_running_perplexity = 0
        perplexity_list = []
        abxe.strength = 500
        abyd.strength = 500
        N, log_running_perplexity = sp.pop_manager.perplexity_step(N, log_running_perplexity, perplexity_list,
                                                                   previous_words, actual_next_word)
        self.assertEqual(N, 2)
        self.assertAlmostEqual(perplexity_list[0], 2, places=2)

    def test_train_token_perplexity_350(self):
        words = DataObtainer.get_clean_words_from_file('../data/pride.txt', 20000)
        sp = StreamPredictor()
        sp.pop_manager.train_token(words[:15000])
        perplexity_list = sp.pop_manager.calculate_perplexity(words[15000:])
        self.assertLess(perplexity_list[-1], 350)

    def test_train_token_step(self):
        sp, ab, abxe, abyd, xe, yd = self.form_simple_tree()
        next_words = [ 'd', 'garbage']
        N = 1
        N, previous_pop = sp.pop_manager.train_token_step(N, ab, next_words)
        self.assertEqual(N, 2)
        self.assertTrue('abd' in sp.pop_manager.patterns_collection)
        self.assertEqual(previous_pop.unrolled_pattern, 'd')

    def test_find_next_word(self):
        sp, ab, abxe, abyd, xe, yd = self.form_simple_tree()
        words = ['ab', 'd']
        current_pop, increment = sp.pop_manager.find_next_word(words[1:])
        self.assertEqual(current_pop.unrolled_pattern, 'd')
        self.assertEqual(increment, 1)
        words = ['ab', 'x', 'e']
        current_pop, increment = sp.pop_manager.find_next_word(words[1:])
        self.assertEqual(current_pop.unrolled_pattern, 'xe')
        self.assertEqual(increment, 2)

    def test_get_prediction_probability(self):
        words = ['and', 'what', 'where']
        sp = StreamPredictor()
