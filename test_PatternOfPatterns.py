from unittest import TestCase
import PatternOfPatternsStream
from PatternOfPatternsStream import PopManager, Pop
import DataObtainer
import os

test_pattern_file = 'PatternStore/test.tsv'


class TestPatternOfPatterns(TestCase):
    def get_sample(self):
        sample = PatternOfPatternsStream.PopManager()
        sample.train('cat hat mat bat sat in the barn')
        return sample

    def test_save(self):
        sample = self.get_sample()
        sample.save(test_pattern_file)
        self.assertTrue(os.path.isfile(test_pattern_file))

    def test_load(self):
        self.test_save()
        empty_sample = PatternOfPatternsStream.PopManager()
        self.assertFalse(len(empty_sample.patterns_collection) > 10)
        empty_sample.load(test_pattern_file)
        self.assertTrue(len(empty_sample.patterns_collection) > 10)

    def test_save_load_equal(self):
        sample = self.get_sample()
        sample.patterns_collection['karma'] = PatternOfPatternsStream.Pop('karma')
        first_string = sample.status()
        sample.save(test_pattern_file)
        second = PatternOfPatternsStream.PopManager()
        second.load(test_pattern_file)
        second_string = second.status()
        self.assertEqual(first_string, second_string)

    def test_find_next_pattern(self):
        sample = self.get_sample()
        small_pattern = 'somew'
        big_pattern = small_pattern + ' some random text'
        sample.patterns_collection[small_pattern] = PatternOfPatternsStream.Pop(small_pattern)
        found_pattern = sample.find_next_pattern(big_pattern)
        self.assertEqual(found_pattern.unrolled_pattern, small_pattern)
        small_pattern = 'somewhat'
        big_pattern = small_pattern + ' some random text'
        sample.patterns_collection[small_pattern] = PatternOfPatternsStream.Pop(small_pattern)
        found_pattern = sample.find_next_pattern(big_pattern)
        self.assertEqual(found_pattern.unrolled_pattern, small_pattern)
        small_pattern = 'somewhatapa'
        big_pattern = small_pattern + ' some random text'
        sample.patterns_collection[small_pattern] = PatternOfPatternsStream.Pop(small_pattern)
        found_pattern = sample.find_next_pattern(big_pattern)
        self.assertEqual(found_pattern.unrolled_pattern, small_pattern)

    def test_join_pattern(self):
        sample = PatternOfPatternsStream.PopManager()
        cat_ate_ = PatternOfPatternsStream.Pop('The cat ate ')
        fruit = PatternOfPatternsStream.Pop('fruit')
        banana = PatternOfPatternsStream.Pop('banana')
        strawberry = PatternOfPatternsStream.Pop('strawberry')
        sample.add_pop(cat_ate_)
        sample.add_pop(fruit)
        sample.add_pop(banana)
        sample.add_pop(strawberry)
        banana.belongs_to_category = fruit
        strawberry.belongs_to_category = fruit
        sample.join_pattern(cat_ate_, banana, found_pattern_feed_ratio=1)
        self.assertTrue((cat_ate_.unrolled_pattern + fruit.unrolled_pattern) in sample.patterns_collection)

    def test_generailze(self):
        pm = PatternOfPatternsStream.PopManager()
        pm.add_pop_string('apple')
        pm.add_pop_string('banana')
        text = DataObtainer.get_clean_text_from_file('data/Experimental/case.txt', 100000)
        pm.train(text)
        pm.generalize()
        print [i.belongs_to_category.__repr__ for i in  pm.patterns_collection.values() if i.belongs_to_category is not None]
        self.assertTrue(pm.patterns_collection['apple'].
                        belongs_to_category is pm.patterns_collection['banana'].belongs_to_category)

    def test_change_component(self):
        a, ab, abc, pm, b, c , bc = self.setup_simple_patterns()
        self.assertTrue(len(a.first_child_parents) == 1)
        self.assertTrue(len(ab.first_child_parents) == 0)
        pm.change_components_string('ab', 'c', abc)
        self.assertTrue(len(a.first_child_parents) == 0)
        self.assertTrue(len(pm.patterns_collection['ab'].first_child_parents) == 1)

    def setup_simple_patterns(self):
        pm = PopManager()
        abc = Pop('abc')
        ab = Pop('ab')
        bc = Pop('bc')
        a = Pop('a')
        b = Pop('b')
        c = Pop('c')
        pm.add_pop(abc)
        pm.add_pop(bc)
        pm.add_pop(ab)
        pm.add_pop(a)
        pm.add_pop(b)
        pm.add_pop(c)
        abc.set_components(a, bc)
        return a, ab, abc, pm, b, c, bc

    def test_is_right_child(self):
        a, ab, abc, pm, b, c , bc = self.setup_simple_patterns()
        self.assertTrue(abc.is_right_child(bc))
        self.assertFalse(abc.is_right_child(c))


