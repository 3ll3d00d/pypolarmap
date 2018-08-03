import unittest

from model.log import resize, get_iterable_for_rb


class TestRing(unittest.TestCase):
    def test_expand_from_zero(self):
        data = list(range(0, 10))
        newIdx = resize(10, 20, data, 0)
        expected = list(range(0, 10)) + ([None] * 10)
        self.assertEqual(data, expected)
        self.assertEqual(newIdx, 0)
        iterated = [i for i in get_iterable_for_rb(data, newIdx)]
        self.assertEqual(expected, iterated)

    def test_expand_middle(self):
        data = list(range(0, 10))
        newIdx = resize(10, 20, data, 5)
        expected = list(range(0, 10)) + ([None] * 10)
        self.assertEqual(data, expected)
        self.assertEqual(newIdx, 5)
        iterated = [i for i in get_iterable_for_rb(data, newIdx)]
        expectedIterated = list(range(5, 10)) + ([None] * 10) + list(range(0, 5))
        self.assertEqual(expectedIterated, iterated)

    def test_reduce_beginning(self):
        data = list(range(0, 10))
        newIdx = resize(10, 5, data, 0)
        expected = list(range(5, 10))
        self.assertEqual(data, expected)
        self.assertEqual(newIdx, 0)
        iterated = [i for i in get_iterable_for_rb(data, newIdx)]
        self.assertEqual(expected, iterated)

    def test_reduce_middle(self):
        data = list(range(0, 10))
        newIdx = resize(10, 5, data, 3)
        expected = [0, 1, 2, 8, 9]
        self.assertEqual(data, expected)
        self.assertEqual(newIdx, 3)
        iterated = [i for i in get_iterable_for_rb(data, newIdx)]
        self.assertEqual([8, 9, 0, 1, 2], iterated)

    def test_reduce_end(self):
        data = list(range(0, 10))
        newIdx = resize(10, 5, data, 8)
        expected = [3, 4, 5, 6, 7]
        self.assertEqual(data, expected)
        self.assertEqual(newIdx, 4)
        iterated = [i for i in get_iterable_for_rb(data, newIdx)]
        self.assertEqual([7, 3, 4, 5, 6], iterated)


if __name__ == '__main__':
    unittest.main()
