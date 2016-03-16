from unittest import TestCase
import PatternOfPatternsStream
import os
test_csv = 'test.csv'

class TestPatternOfPatterns(TestCase):
    def get_sample(self):
        sample = PatternOfPatternsStream.PopManager()
        sample.train('cat hat mat bat sat in the barn')
        return  sample

    # def test_set_components_from_string(self):
    #     self.fail()
    #
    # def test_train(self):
    #     self.fail()
    #
    # def test_cull(self):
    #     self.fail()
    #
    # def test_status(self):
    #     self.fail()

    def test_save(self):
        sample = self.get_sample()
        sample.save(test_csv)
        self.assertTrue(os.path.isfile(test_csv))

    def test_load(self):
        self.test_save()
        empty_sample = PatternOfPatternsStream.PopManager()
        self.assertFalse(len(empty_sample.patterns_collection) > 10)
        empty_sample.load(test_csv)
        self.assertTrue(len(empty_sample.patterns_collection) > 10)

    def test_save_load_equal(self):
        sample = self.get_sample()
        sample.patterns_collection['karma'] = PatternOfPatternsStream.Pop('karma')
        first_string = sample.status()
        sample.save(test_csv)
        second = PatternOfPatternsStream.PopManager()
        second.load(test_csv)
        second_string = second.status()
        self.assertEqual(first_string, second_string)


