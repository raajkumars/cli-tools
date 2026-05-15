#!/usr/bin/env python3
"""Print the top-N most frequent words in a text file."""

import argparse
import collections
import re
import sys


def positive_int(value):
    v = int(value)
    if v < 1:
        raise argparse.ArgumentTypeError(f"N must be >= 1, got {value!r}")
    return v


def word_freq(path, top):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        sys.exit(f"error: file not found: {path}")
    except OSError as exc:
        sys.exit(f"error: cannot read {path}: {exc}")

    words = re.findall(r"[a-zA-Z']+", text.lower())
    counts = collections.Counter(words)
    for word, count in counts.most_common(top):
        print(f"{count:>6}  {word}")


def main():
    parser = argparse.ArgumentParser(description="Print top-N word frequencies.")
    parser.add_argument("file", help="path to text file")
    parser.add_argument(
        "--top", type=positive_int, default=10, metavar="N",
        help="number of words to show (default: 10)",
    )
    args = parser.parse_args()
    word_freq(args.file, args.top)


if __name__ == "__main__":
    main()
