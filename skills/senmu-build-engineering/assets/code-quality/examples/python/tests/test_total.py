import unittest

from sample_app.domain import total


class TotalTests(unittest.TestCase):
    def test_discount(self):
        self.assertEqual(total(100, 20), 80)

    def test_zero(self):
        self.assertEqual(total(100, 0), 100)

    def test_reject_negative(self):
        with self.assertRaises(ValueError):
            total(10, 20)
