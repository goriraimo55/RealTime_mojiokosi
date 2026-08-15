import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


class _ScriptExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self._current = None

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self._current = []
            self.scripts.append(self._current)

    def handle_endtag(self, tag):
        if tag == "script":
            self._current = None

    def handle_data(self, data):
        if self._current is not None:
            self._current.append(data)


class LlmRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = INDEX.read_text(encoding="utf-8")

    def test_removed_reasoning_fallback_state_is_not_referenced(self):
        # These variables belonged to the removed reasoning fallback. Leaving
        # either reference behind causes the user-visible ReferenceError.
        self.assertNotIn("receivedAnswer", self.source)
        self.assertNotIn("reasoningFallback", self.source)
        self.assertNotIn("openAiReasoningText", self.source)

    def test_connection_check_does_not_use_streaming_generator(self):
        handler = self.source.split('$("testLlmBtn").addEventListener', 1)[1]
        handler = handler.split("/* =========================================================", 1)[0]
        self.assertIn("await testLlmConnection(abort.signal)", handler)
        self.assertNotIn("streamChat(", handler)

    def test_inline_javascript_has_valid_syntax(self):
        parser = _ScriptExtractor()
        parser.feed(self.source)
        self.assertGreaterEqual(len(parser.scripts), 2)

        with tempfile.TemporaryDirectory() as directory:
            for index, parts in enumerate(parser.scripts):
                script = Path(directory) / f"inline-{index}.js"
                script.write_text("".join(parts), encoding="utf-8")
                subprocess.run(["node", "--check", script], check=True)


if __name__ == "__main__":
    unittest.main()
