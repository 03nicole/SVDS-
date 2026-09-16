import re
from pathlib import Path
import markdown

THESIS = Path(r"C:\Users\user\Downloads\vrrs\thesis")

CHAPTER_FILES = [
    "00-front-matter.md",
    "01-introduction.md",
    "02-literature-review.md",
    "03-requirements-engineering.md",
    "04-system-design.md",
    "05-object-detection-module.md",
    "06-system-implementation.md",
    "07-integration.md",
    "08-testing-and-verification.md",
    "09-conclusion.md",
    "10-appendices.md",
    "11-references.md",
]

MERMAID_FENCE_RE = re.compile(r"```mermaid\n.*?\n```\n?", re.DOTALL)

STYLE = """
<style>
  @page { size: A4; margin: 2.5cm; }
  body {
    font-family: 'Times New Roman', Georgia, serif;
    font-size: 12pt;
    line-height: 1.5;
    color: #111;
    max-width: 210mm;
    margin: 0 auto;
  }
  h1 { font-size: 20pt; margin-top: 0; page-break-before: always; }
  h1:first-of-type { page-break-before: avoid; }
  h2 { font-size: 15pt; margin-top: 1.4em; }
  h3 { font-size: 13pt; margin-top: 1.2em; }
  p, li { text-align: justify; }
  code { font-family: Consolas, 'Courier New', monospace; background: #f2f2f2; padding: 1px 4px; font-size: 10pt; }
  pre { background: #f5f5f5; border: 1px solid #ddd; padding: 10px; overflow-x: auto; font-size: 9.5pt; }
  pre code { background: none; padding: 0; }
  table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 10.5pt; }
  th, td { border: 1px solid #999; padding: 5px 8px; text-align: left; vertical-align: top; }
  th { background: #eaeaea; }
  img { max-width: 100%; display: block; margin: 0.8em auto; border: 1px solid #ddd; }
  hr { border: none; border-top: 1px solid #999; margin: 2em 0; }
  .titlepage { text-align: center; padding-top: 3cm; }
</style>
"""

IMG_SRC_RE = re.compile(r'src="(?!https?://|file:///)([^"]+)"')

def absolutize_images(html: str) -> str:
    def repl(m):
        rel = m.group(1)
        abs_path = (THESIS / rel).resolve()
        return f'src="{abs_path.as_uri()}"'
    return IMG_SRC_RE.sub(repl, html)

body_parts = []
for fname in CHAPTER_FILES:
    raw = (THESIS / fname).read_text(encoding="utf-8")
    raw = MERMAID_FENCE_RE.sub("", raw)  # rendered PNGs already follow each fence
    html = markdown.markdown(raw, extensions=["tables", "fenced_code", "sane_lists"])
    html = absolutize_images(html)
    body_parts.append(html)

full_body = "\n<hr/>\n".join(body_parts)

doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>SVDS -- Vehicle Registry and Stolen Vehicle Detection System</title>
{STYLE}
</head>
<body>
{full_body}
</body>
</html>
"""

out_path = THESIS / "SVDS-Thesis.html"
out_path.write_text(doc, encoding="utf-8")
print("Wrote", out_path, "-", len(doc), "chars")
