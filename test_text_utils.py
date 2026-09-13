import unittest

from text_utils import clean_extracted_text


class CleanExtractedTextTests(unittest.TestCase):
    def test_non_breaking_spaces(self):
        raw = "Hello\xa0world\xa0again"
        self.assertEqual(clean_extracted_text(raw), "Hello world again")

    def test_multiple_newlines_and_tabs(self):
        raw = "Line one\n\n\nLine two\t\ttrailing\t"
        self.assertEqual(clean_extracted_text(raw), "Line one Line two trailing")

    def test_mixed_artifacts(self):
        raw = "  Lead-in\xa0\n\n\tbody\t\t\n"
        self.assertEqual(clean_extracted_text(raw), "Lead-in body")

    def test_empty_and_none(self):
        self.assertEqual(clean_extracted_text(""), "")
        self.assertEqual(clean_extracted_text(None), "")

    def test_already_clean(self):
        self.assertEqual(clean_extracted_text("Plain sentence."), "Plain sentence.")


if __name__ == "__main__":
    unittest.main()
