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

    def test_openai_stream_generator_continues_after_token_limit(self):
        start = self.source.index("async function* streamChat")
        end = self.source.index("\nasync function testLlmConnection", start)
        stream_chat = self.source[start:end]
        harness = f'''"use strict";
const assert = require("node:assert/strict");
const settings = {{llm: {{provider: "lmstudio", baseUrl: "http://localhost:1234/v1", model: "qwen"}}}};
function llmApiUrl(path) {{ return settings.llm.baseUrl + path; }}
function llmHeaders() {{ return {{"Content-Type": "application/json"}}; }}
function isEventStream(res) {{ return res.headers.get("content-type").includes("text/event-stream"); }}
function openAiResponseText(ev) {{ return ev.choices?.[0]?.delta?.content || ev.choices?.[0]?.message?.content || ""; }}
function openAiFinishReason(ev) {{ return ev.choices?.[0]?.finish_reason || ""; }}
function anthropicResponseText() {{ return ""; }}
let requestCount = 0;
const requestBodies = [];
async function* sseLines(res) {{
  yield JSON.stringify({{choices: [{{delta: {{content: res.part}}}}]}});
  yield JSON.stringify({{choices: [{{delta: {{}}, finish_reason: res.finishReason}}]}});
  yield "[DONE]";
}}
global.fetch = async (url, options) => {{
  requestBodies.push(JSON.parse(options.body));
  requestCount += 1;
  return {{
    ok: true,
    part: requestCount === 1 ? "## 議事" : "録\\n- 完了",
    finishReason: requestCount === 1 ? "length" : "stop",
    headers: {{get: () => "text/event-stream; charset=utf-8"}},
    text: async () => "",
  }};
}};
{stream_chat}
(async () => {{
  let result = "";
  for await (const chunk of streamChat("文字起こし", new AbortController().signal)) result += chunk;
  assert.equal(result, "## 議事録\\n- 完了");
  assert.equal(requestCount, 2);
  assert.equal(requestBodies[0].max_tokens, 4096);
  assert.equal(requestBodies[1].messages.at(-2).role, "assistant");
  assert.match(requestBodies[1].messages.at(-1).content, /切れた箇所から/);

  requestCount = 0;
  requestBodies.length = 0;
  global.fetch = async (url, options) => {{
    requestBodies.push(JSON.parse(options.body));
    requestCount += 1;
    return {{
      ok: true,
      headers: {{get: () => "application/json"}},
      json: async () => ({{choices: [{{
        message: {{content: requestCount === 1 ? "概要" : "と結論"}},
        finish_reason: requestCount === 1 ? "length" : "stop",
      }}]}}),
      text: async () => "",
    }};
  }};
  result = "";
  for await (const chunk of streamChat("文字起こし", new AbortController().signal)) result += chunk;
  assert.equal(result, "概要と結論");
  assert.equal(requestCount, 2);
  console.log("streamChat continuation test passed");
}})().catch(error => {{ console.error(error); process.exitCode = 1; }});
'''
        subprocess.run(["node", "-e", harness], check=True)

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
