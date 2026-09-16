"""Render every ```mermaid fenced block in the thesis chapter files to a real
PNG using an already-installed Chrome (headless) + mermaid.js from a CDN,
driven over the raw DevTools Protocol (same technique used for the UI
screenshots -- avoids any large binary downloads).
"""
import base64
import json
import re
import subprocess
import time
from pathlib import Path

import requests
import websocket

THESIS = Path(r"C:\Users\user\Downloads\vrrs\thesis")
DIAGRAMS_DIR = THESIS / "assets" / "diagrams"
DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEBUG_PORT = 9421
USER_DATA_DIR = r"C:\Users\user\AppData\Local\Temp\vrrs-thesis-mermaid-profile"

MERMAID_RE = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL)

HTML_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  html, body {{ margin:0; padding:24px; background:#ffffff; }}
  .mermaid {{ font-family: 'Trebuchet MS', Verdana, Arial, sans-serif; }}
</style>
</head>
<body>
<pre class="mermaid">
{diagram}
</pre>
<script>
  mermaid.initialize({{ startOnLoad: true, theme: 'default', securityLevel: 'loose' }});
</script>
</body></html>
"""

# 1. Collect all mermaid blocks from every chapter file, in file order.
files = sorted(THESIS.glob("*.md"))
jobs = []  # (md_path, match_span, diagram_text, out_png_path)
for md_path in files:
    text = md_path.read_text(encoding="utf-8")
    for i, m in enumerate(MERMAID_RE.finditer(text)):
        out_name = f"{md_path.stem}-{i+1}.png"
        jobs.append({
            "md_path": md_path,
            "diagram": m.group(1),
            "out_path": DIAGRAMS_DIR / out_name,
        })

print(f"Found {len(jobs)} mermaid diagrams to render.")

# 2. Launch headless Chrome with devtools.
proc = subprocess.Popen([
    CHROME, "--headless=new", f"--remote-debugging-port={DEBUG_PORT}",
    "--remote-allow-origins=*",
    f"--user-data-dir={USER_DATA_DIR}", "--no-first-run", "--no-default-browser-check",
    "--window-size=1600,1200", "--hide-scrollbars",
])
time.sleep(2)
for _ in range(20):
    try:
        requests.get(f"http://localhost:{DEBUG_PORT}/json/version", timeout=1)
        break
    except requests.RequestException:
        time.sleep(0.5)

TMP_HTML_DIR = Path(r"C:\Users\user\AppData\Local\Temp\vrrs-thesis-mermaid-html")
TMP_HTML_DIR.mkdir(exist_ok=True)

try:
    for idx, job in enumerate(jobs):
        html_path = TMP_HTML_DIR / f"diagram-{idx}.html"
        html_path.write_text(HTML_TEMPLATE.format(diagram=job["diagram"]), encoding="utf-8")

        r = requests.put(f"http://localhost:{DEBUG_PORT}/json/new?about:blank")
        info = r.json()
        ws = websocket.create_connection(info["webSocketDebuggerUrl"], timeout=20)
        _id = 0

        def send(method, params=None):
            nonlocal_id = send.counter = getattr(send, "counter", 0) + 1
            ws.send(json.dumps({"id": nonlocal_id, "method": method, "params": params or {}}))
            while True:
                data = json.loads(ws.recv())
                if data.get("id") == nonlocal_id:
                    return data

        send("Page.enable")
        send("Runtime.enable")
        send("Page.navigate", {"url": html_path.as_uri()})
        time.sleep(1.0)

        ok = False
        for _ in range(30):
            res = send("Runtime.evaluate", {
                "expression": "document.querySelector('.mermaid svg') ? document.querySelector('.mermaid svg').outerHTML.length : 0"
            })
            val = res.get("result", {}).get("result", {}).get("value", 0)
            if val and val > 100:
                ok = True
                break
            time.sleep(0.3)

        if not ok:
            err = send("Runtime.evaluate", {"expression": "document.body.innerText"})
            print(f"  ! FAILED to render {job['out_path'].name}: {err}")
        else:
            # Wait for the SVG's own size to stop changing (mermaid can report
            # the element as "present" before its layout has fully settled on
            # larger diagrams), instead of a fixed sleep.
            last_size = None
            for _ in range(20):
                sz = send("Runtime.evaluate", {
                    "expression": (
                        "(() => { const r = document.querySelector('.mermaid svg')"
                        ".getBoundingClientRect(); return r.width + 'x' + r.height; })()"
                    ),
                })
                cur = sz.get("result", {}).get("result", {}).get("value")
                if cur == last_size:
                    break
                last_size = cur
                time.sleep(0.4)
            time.sleep(0.5)
            rect = send("Runtime.evaluate", {
                "expression": (
                    "(() => { const r = document.querySelector('.mermaid svg')"
                    ".getBoundingClientRect(); return JSON.stringify({x:r.x, y:r.y, "
                    "width:r.width, height:r.height}); })()"
                ),
                "returnByValue": True,
            })
            box = json.loads(rect["result"]["result"]["value"])
            pad = 12
            clip = {
                "x": max(0, box["x"] - pad), "y": max(0, box["y"] - pad),
                "width": box["width"] + pad * 2, "height": box["height"] + pad * 2,
                "scale": 1,
            }
            shot = send("Page.captureScreenshot", {
                "format": "png", "clip": clip, "captureBeyondViewport": True,
            })
            data = shot["result"]["data"]
            job["out_path"].write_bytes(base64.b64decode(data))
            print(f"  rendered -> {job['out_path'].name} ({clip['width']:.0f}x{clip['height']:.0f})")

        ws.close()
        requests.get(f"http://localhost:{DEBUG_PORT}/json/close/{info['id']}")
finally:
    proc.terminate()

print("DONE rendering mermaid diagrams.")

# NOTE: re-running this regenerates images at the SAME paths (chapter-stem +
# occurrence index), so existing ![...](assets/diagrams/...) embeds in the
# chapter .md files keep working without any manual edits.
