#!/usr/bin/env python3
"""Print the top-N most frequent words in a file."""

import argparse
import collections
import re
import sys


def count_words(text):
    words = re.findall(r"[a-z]+", text.lower())
    return collections.Counter(words)


def main():
    parser = argparse.ArgumentParser(
        description="Print the top-N most frequent words in a file."
    )
    parser.add_argument("file", help="Path to the input file")
    parser.add_argument(
        "--top", type=int, default=10, metavar="N",
        help="Number of top words to display (default: 10)"
    )
    args = parser.parse_args()

    try:
        with open(args.file, encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    counts = count_words(text)
    for word, freq in counts.most_common(args.top):
        print(f"{freq:>6}  {word}")


if __name__ == "__main__":
    main()
