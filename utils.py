import unittest
import re

def canonicalize_word(word):
    rex = re.compile(r'\W+')
    return rex.sub(' ', word.lower().strip())


class TestCanonicalize(unittest.TestCase):
    def test(self):
        cases = [
            ["Rill", "rill"],
            [" Rill ", "rill"],
            ["Bill of FARE", "bill of fare"],
            ["regal  snowflake", "regal snowflake"],
            ["deep   may", "deep may"],
        ]

        for [a, b] in cases:
            self.assertEqual(canonicalize_word(a), b)

if __name__ == '__main__':
    unittest.main()
