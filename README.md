# Word search solver

Finds every word from a list in a letter grid, in all 8 directions. Pure Python, no dependencies.

## Web page

Open `web/index.html` in a browser. Paste the grid and the words (or upload a puzzle `.txt` in the format below), press Solve, and every word gets circled. Hover a word to pick out its loop. The solver runs in the browser, so nothing is sent anywhere.

## Command line

```
python wordsearch.py examples/animals.txt
```

A 100x100 grid with 300 words solves in about 20 ms.

## Puzzle format

Grid rows, a blank line, then the words (one per line or comma separated):

```
C A T X
D O G Q

CAT, DOG
```

Spaces in the grid and in words are ignored, and case doesn't matter.

## Find every word, no list

```
python wordsearch.py puzzle.txt --all /usr/share/dict/words --min-length 4
```

## How it works

The words go into a trie (a prefix tree). From every cell, the solver walks in each of the 8 directions and follows the trie letter by letter, stopping as soon as the letters stop matching the start of any word. Each cell is checked in at most 8 directions, and each walk ends early, so the work grows with grid size, not with the number of words.

## Tests

```
python -m unittest
```
