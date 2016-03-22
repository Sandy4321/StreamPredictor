from unittest import TestCase
import PatternOfPatternsStream
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
        first_string = sample.status(show_plot=False)
        sample.save(test_pattern_file)
        second = PatternOfPatternsStream.PopManager()
        second.load(test_pattern_file)
        second_string = second.status(show_plot=False)
        self.assertEqual(first_string, second_string)

    def test_find_next_pattern(self):
        sample = self.get_sample()
        small_pattern = 'somewhat '
        big_pattern = small_pattern + ' some random text'
        sample.patterns_collection[small_pattern] = PatternOfPatternsStream.Pop(small_pattern)
        found_pattern = sample.find_next_pattern(big_pattern)
        self.assertEqual(found_pattern.unrolled_pattern, small_pattern)
        small_pattern = 'somewhat'
        big_pattern = small_pattern + ' some random text'
        sample.patterns_collection[small_pattern] = PatternOfPatternsStream.Pop(small_pattern)
        found_pattern = sample.find_next_pattern(big_pattern)
        self.assertEqual(found_pattern.unrolled_pattern, small_pattern)
        small_pattern = 'somewha'
        big_pattern = small_pattern + ' some random text'
        sample.patterns_collection[small_pattern] = PatternOfPatternsStream.Pop(small_pattern)
        found_pattern = sample.find_next_pattern(big_pattern)
        self.assertEqual(found_pattern.unrolled_pattern, small_pattern)
