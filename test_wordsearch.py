import random
import string
import time
import unittest

from wordsearch import DIRECTIONS, parse_puzzle, render, solve


class SolveTest(unittest.TestCase):
    def test_all_eight_directions(self):
        grid = [
            "ABCDE",
            "FGHIJ",
            "KLMNO",
            "PQRST",
            "UVWXY",
        ]
        cases = {
            "MNO": ((2, 2), (2, 4)),  # right
            "MLK": ((2, 2), (2, 0)),  # left
            "MRW": ((2, 2), (4, 2)),  # down
            "MHC": ((2, 2), (0, 2)),  # up
            "MSY": ((2, 2), (4, 4)),  # down-right
            "MQU": ((2, 2), (4, 0)),  # down-left
            "MIE": ((2, 2), (0, 4)),  # up-right
            "MGA": ((2, 2), (0, 0)),  # up-left
        }
        found = solve(grid, list(cases))
        for word, (start, end) in cases.items():
            self.assertEqual([(s, e) for s, e, _ in found[word]],
                             [(start, end)], word)

    def test_missing_word_not_reported(self):
        self.assertEqual(solve(["ABC", "DEF"], ["XYZ", "ABD"]), {})

    def test_word_found_twice(self):
        found = solve(["CATXCAT"], ["CAT"])
        self.assertEqual(len(found["CAT"]), 2)

    def test_palindrome_reported_once(self):
        found = solve(["XLEVELX"], ["LEVEL"])
        self.assertEqual(len(found["LEVEL"]), 1)

    def test_word_that_is_prefix_of_another(self):
        found = solve(["CATSX"], ["CAT", "CATS"])
        self.assertIn("CAT", found)
        self.assertIn("CATS", found)

    def test_spaces_and_case_in_words(self):
        found = solve(["ICECREAM"], ["ice cream"])
        self.assertIn("ice cream", found)

    def test_large_grid_is_fast(self):
        rng = random.Random(0)
        size = 100
        grid = [[rng.choice(string.ascii_uppercase) for _ in range(size)]
                for _ in range(size)]
        placed = set()
        words = []
        while len(words) < 300:
            word = "".join(rng.choice(string.ascii_uppercase)
                           for _ in range(rng.randint(5, 12)))
            dr, dc = rng.choice(DIRECTIONS)
            r = rng.randrange(size) if dr == 0 else (
                rng.randrange(size - len(word)) if dr > 0
                else rng.randrange(len(word) - 1, size))
            c = rng.randrange(size) if dc == 0 else (
                rng.randrange(size - len(word)) if dc > 0
                else rng.randrange(len(word) - 1, size))
            cells = [(r + dr * i, c + dc * i) for i in range(len(word))]
            if placed.intersection(cells):
                continue
            for (rr, cc), ch in zip(cells, word):
                grid[rr][cc] = ch
            placed.update(cells)
            words.append(word)
        grid = ["".join(row) for row in grid]

        t0 = time.perf_counter()
        found = solve(grid, words)
        elapsed = time.perf_counter() - t0

        self.assertEqual(set(found), set(words))
        self.assertLess(elapsed, 1.0)


class ParseTest(unittest.TestCase):
    def test_parse_puzzle(self):
        text = "\nC A T\nd o g\n\nCAT, DOG\nice cream\n"
        grid, words = parse_puzzle(text)
        self.assertEqual(grid, ["CAT", "DOG"])
        self.assertEqual(words, ["CAT", "DOG", "ice cream"])

    def test_render_hides_unused_letters(self):
        grid = ["CATX", "YYYY"]
        self.assertEqual(render(grid, solve(grid, ["CAT"])),
                         "C A T .\n. . . .")


if __name__ == "__main__":
    unittest.main()
