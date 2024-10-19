import unittest
from slvsh_tr.eval import levenshtein_distance, PrecisionAndRecall


class TestLevenshteinDistance(unittest.TestCase):
    def test_levenshtein_distance(self):
        result = levenshtein_distance("hello world", "hello world")
        self.assertEqual(result, PrecisionAndRecall(
            prediction="hello world",
            expected="hello world",
            precision=1.0,
            recall=1.0,
            f1=1.0
        ))

        result = levenshtein_distance("hello", "world")
        self.assertEqual(result, PrecisionAndRecall(
            prediction="hello",
            expected="world",
            precision=0.0,
            recall=0.0,
            f1=0.0
        ))

        result = levenshtein_distance("", "")
        self.assertEqual(result, PrecisionAndRecall(
            prediction="",
            expected="",
            precision=1.0,
            recall=1.0,
            f1=1.0
        ))

        result = levenshtein_distance("a", "")
        self.assertAlmostEqual(result.precision, 0.0)
        self.assertAlmostEqual(result.recall, 1.0)
        self.assertAlmostEqual(result.f1, 0.0)

        result = levenshtein_distance("CORK 5", "  CORK  5")
        self.assertAlmostEqual(result.precision, 1.0)
        self.assertAlmostEqual(result.recall, 1.0)
        self.assertAlmostEqual(result.f1, 1.0)


if __name__ == '__main__':
    unittest.main()
