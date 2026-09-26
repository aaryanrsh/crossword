"""Word search solver.

Finds every word from a list in a letter grid, in all 8 directions.
Words are loaded into a trie so each walk stops as soon as its letters
stop matching the start of any word.

Usage:
    python wordsearch.py puzzle.txt
    python wordsearch.py puzzle.txt --all words.txt --min-length 4

Puzzle file format: grid rows, a blank line, then the words to find
(one per line or comma separated). Spaces inside grid rows are ignored.
"""

import argparse
import sys
import time

DIRECTIONS = [
    (0, 1), (0, -1), (1, 0), (-1, 0),
    (1, 1), (1, -1), (-1, 1), (-1, -1),
]

DIRECTION_NAMES = {
    (0, 1): "right", (0, -1): "left", (1, 0): "down", (-1, 0): "up",
    (1, 1): "down-right", (1, -1): "down-left",
    (-1, 1): "up-right", (-1, -1): "up-left",
}

END = "$"


def normalize(word):
    """Uppercase and drop anything that isn't a letter ("ICE CREAM" -> "ICECREAM")."""
    return "".join(ch for ch in word.upper() if ch.isalpha())


def build_trie(words):
    root = {}
    for word in words:
        key = normalize(word)
        if not key:
            continue
        node = root
        for ch in key:
            node = node.setdefault(ch, {})
        node.setdefault(END, []).append(word)
    return root


def solve(grid, words):
    """Return {word: [(start, end, direction), ...]} for every word found.

    start and end are (row, col) pairs, 0-indexed.
    """
    trie = build_trie(words)
    rows = len(grid)
    found = {}
    for r in range(rows):
        for c in range(len(grid[r])):
            if grid[r][c] not in trie:
                continue
            for dr, dc in DIRECTIONS:
                node = trie
                rr, cc = r, c
                while 0 <= rr < rows and 0 <= cc < len(grid[rr]):
                    node = node.get(grid[rr][cc])
                    if node is None:
                        break
                    for word in node.get(END, ()):
                        hits = found.setdefault(word, [])
                        # Palindromes match forwards and backwards over the
                        # same cells; keep one.
                        if not any({s, e} == {(r, c), (rr, cc)}
                                   for s, e, _ in hits):
                            hits.append(((r, c), (rr, cc), (dr, dc)))
                    rr += dr
                    cc += dc
    return found


def parse_puzzle(text):
    """Split a puzzle file into (grid, words)."""
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    grid = []
    i = 0
    while i < len(lines) and lines[i].strip():
        grid.append(normalize(lines[i]))
        i += 1
    words = []
    for line in lines[i:]:
        for part in line.split(","):
            if part.strip():
                words.append(part.strip())
    return grid, words


def cells_of(start, end, direction):
    (r, c), (dr, dc) = start, direction
    cells = [(r, c)]
    while (r, c) != end:
        r += dr
        c += dc
        cells.append((r, c))
    return cells


def render(grid, found):
    """Grid with found letters kept and every other letter replaced by '.'."""
    used = set()
    for hits in found.values():
        for start, end, direction in hits:
            used.update(cells_of(start, end, direction))
    return "\n".join(
        " ".join(ch if (r, c) in used else "." for c, ch in enumerate(row))
        for r, row in enumerate(grid)
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Solve a word search.")
    parser.add_argument("puzzle", help="puzzle file (grid, blank line, words)")
    parser.add_argument("--all", metavar="DICTIONARY",
                        help="ignore the puzzle's word list and find every "
                             "dictionary word in the grid")
    parser.add_argument("--min-length", type=int, default=4,
                        help="shortest word to report with --all (default 4)")
    args = parser.parse_args(argv)

    with open(args.puzzle) as f:
        grid, words = parse_puzzle(f.read())
    if not grid:
        sys.exit("No grid found in " + args.puzzle)

    if args.all:
        with open(args.all) as f:
            words = [w.strip() for w in f
                     if len(normalize(w)) >= args.min_length]

    t0 = time.perf_counter()
    found = solve(grid, words)
    elapsed = time.perf_counter() - t0

    print(render(grid, found))
    print()
    for word in sorted(found, key=lambda w: (found[w][0][0], w)):
        for (r1, c1), (r2, c2), direction in found[word]:
            print(f"{word:<20} row {r1 + 1}, col {c1 + 1} -> "
                  f"row {r2 + 1}, col {c2 + 1}  ({DIRECTION_NAMES[direction]})")
    if not args.all:
        missing = [w for w in words if w not in found]
        if missing:
            print("\nNot found: " + ", ".join(missing))
    print(f"\nFound {len(found)} word(s) in {elapsed * 1000:.2f} ms")


if __name__ == "__main__":
    main()
