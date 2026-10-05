"""Exercise the JavaScript emitted by build_site.sh before deploying it."""

import json
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import unittest


class SiteParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.scripts = []
        self.ids = []
        self.buttons = []
        self.custom_form = None
        self.in_script = False
        self.in_custom_form = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "form" and attrs.get("id") == "load-custom":
            self.custom_form = attrs
            self.in_custom_form = True
        if tag == "button" and self.in_custom_form:
            self.buttons.extend(attrs.get("class", "").split())
        if tag == "script" and "src" not in attrs:
            self.in_script = True
            self.scripts.append("")

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
        if tag == "form":
            self.in_custom_form = False

    def handle_data(self, data):
        if self.in_script:
            self.scripts[-1] += data


def run_page(page, query):
    # The real page scripts run against the parsed DOM and a worker boundary.
    # Starting Pyodide is unnecessary to check the database sent to the worker.
    result = subprocess.run(
        ["node", "-e", """
const fs = require('node:fs');
const vm = require('node:vm');
const page = JSON.parse(fs.readFileSync(0, 'utf8'));
const messages = [], workers = [], errors = [];
const elements = new Map(page.ids.map(id => [id, {addEventListener() {}}]));
const buttons = new Map(page.buttons.map(name => [
    `#load-custom button.${name}`, {addEventListener() {}}
]));
const context = vm.createContext({
    URL, URLSearchParams, console,
    location: new URL('https://primeradiant.com/terminal-bench-analysis/' + page.query),
    window: {},
    document: {
        getElementById: id => elements.get(id) || null,
        querySelector: selector => buttons.get(selector) || null
    },
    Worker: class {
        constructor(url) { workers.push(url); }
        postMessage(message) { messages.push(message); }
    }
});
for (const script of page.scripts) {
    try { vm.runInContext(script, context, {timeout: 1000}); }
    catch (error) { errors.push(error.message); }
}
process.stdout.write(JSON.stringify({messages, workers, errors}));
"""],
        input=json.dumps({"scripts": page.scripts, "ids": page.ids,
                         "buttons": page.buttons, "query": query}),
        text=True, capture_output=True, check=True,
    )
    return json.loads(result.stdout)


class SiteTests(unittest.TestCase):
    def test_viewers_load_terminal_bench_without_script_errors(self):
        for filename in ("index.html", "datasette-lite.html"):
            for query in ("", "?url=https://example.com/other.db"):
                with self.subTest(filename=filename, query=query):
                    page = SiteParser((Path("_site") / filename).read_text())
                    result = run_page(page, query)
                    startup = next(m for m in result["messages"]
                                   if m.get("type") == "startup")
                    self.assertEqual(startup["sqliteUrls"],
                                     ["/terminal-bench-analysis/terminal-bench.db"])
                    self.assertEqual(result["errors"], [])
                    for worker in result["workers"]:
                        self.assertTrue((Path("_site") / worker).is_file())
                    if page.custom_form is not None:
                        self.assertIn("hidden", page.custom_form)
        self.assertTrue(Path("_site/app.css").is_file())
        self.assertGreater(Path("_site/terminal-bench.db").stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
