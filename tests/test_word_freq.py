import collections
import os
import sys
import tempfile
import unittest
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from word_freq import count_words


class TestCountWords(unittest.TestCase):

    def test_basic_frequency(self):
        counts = count_words("cat dog cat cat dog fish")
        self.assertEqual(counts["cat"], 3)
        self.assertEqual(counts["dog"], 2)
        self.assertEqual(counts["fish"], 1)

    def test_case_insensitive(self):
        counts = count_words("Apple APPLE apple")
        self.assertEqual(counts["apple"], 3)

    def test_punctuation_stripped(self):
        counts = count_words("hello, world! hello.")
        self.assertEqual(counts["hello"], 2)
        self.assertEqual(counts["world"], 1)
        self.assertNotIn("hello,", counts)

    def test_empty_string(self):
        counts = count_words("")
        self.assertEqual(len(counts), 0)

    def test_most_common_order(self):
        counts = count_words("a a a b b c")
        top = counts.most_common(2)
        self.assertEqual(top[0], ("a", 3))
        self.assertEqual(top[1], ("b", 2))


class TestCLI(unittest.TestCase):

    def _run_cli(self, args):
        """Run word_freq.main() capturing stdout; returns (stdout_lines, exit_code)."""
        import io
        import contextlib
        from unittest.mock import patch

        buf = io.StringIO()
        exit_code = 0
        try:
            with contextlib.redirect_stdout(buf):
                with patch("sys.argv", ["word_freq.py"] + args):
                    import word_freq
                    word_freq.main()
        except SystemExit as exc:
            exit_code = exc.code
        return buf.getvalue().splitlines(), exit_code

    def test_top_n_limits_output(self):
        # Use purely alphabetic distinct words so the regex doesn't collapse them.
        unique_words = [
            "alpha", "bravo", "charlie", "delta", "echo",
            "foxtrot", "golf", "hotel", "india", "juliet",
            "kilo", "lima", "mike", "november", "oscar",
            "papa", "quebec", "romeo", "sierra", "tango",
        ]
        text = " ".join(unique_words)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as fh:
            fh.write(text)
            path = fh.name
        try:
            lines, code = self._run_cli(["--top", "5", path])
            self.assertEqual(code, 0)
            self.assertEqual(len(lines), 5)
        finally:
            os.unlink(path)

    def test_missing_file_exits_nonzero(self):
        missing = f"/tmp/word_freq_missing_{uuid.uuid4().hex}.txt"
        _, code = self._run_cli([missing])
        self.assertNotEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
