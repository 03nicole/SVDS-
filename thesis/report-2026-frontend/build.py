"""Assemble the 2026-template final year report (AI/vision individual report)
from the chapter Markdown files into one HTML document that mirrors the
template's page order: cover, declaration, approval, abstract, acknowledgements,
contents, abbreviations, note on group projects, chapters 1-8, references,
appendices A-G.

Usage: python build.py   ->  FinalYearReport-2026.html
Then: build_docx.ps1 for .docx, or headless Chrome for .pdf (see README).
"""
import re
from pathlib import Path
import markdown

HERE = Path(__file__).resolve().parent
META = {
    "title": "SVDS: A Camera-Based Stolen Vehicle Detection System for the Zambia Police Service &mdash; The Web Portals, Analytics and Quality Assurance",
    "degree": "[DEGREE PROGRAMME &mdash; confirm]",
    "name": "[STUDENT NAME &mdash; Role 4: Frontend]",
    "number": "[COMPUTER NUMBER]",
    "supervisor": "[SUPERVISOR NAME]",
    "date": "[DATE OF SUBMISSION]",
}

STYLE = """
<style>
  @page { size: A4; margin: 2.5cm; }
  body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.5; color: #000; max-width: 210mm; margin: 0 auto; }
  h1 { font-size: 20pt; text-align: center; page-break-before: always; margin-top: 0; }
  h2 { font-size: 15pt; margin-top: 1.4em; }
  h3 { font-size: 13pt; margin-top: 1.1em; }
  p, li { text-align: justify; }
  code { font-family: Consolas, 'Courier New', monospace; font-size: 10pt; }
  pre { background: #f5f5f5; border: 1px solid #ddd; padding: 8px; font-size: 9pt; white-space: pre-wrap; }
  table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 10.5pt; }
  th, td { border-top: 1px solid #444; border-bottom: 1px solid #444; padding: 4px 8px; text-align: left; vertical-align: top; }
  th { background: #efefef; }
  img { max-width: 100%; display: block; margin: 0.8em auto; }
  .cover { text-align: center; page-break-after: always; }
  .cover h2, .cover h3 { text-align: center; }
  .plain-title { font-size: 20pt; font-weight: bold; text-align: center; page-break-before: always; margin: 1em 0; }
  .sig { margin: 1.4em 0; } .sig span { display: inline-block; border-bottom: 1px solid #000; width: 60%; }
  .center { text-align: center; }
  .todo { background: #fff3b0; }
</style>
"""

def md(path):
    text = (HERE / path).read_text(encoding="utf-8")
    html = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    # make relative image paths absolute so Word/Chrome can find them
    def repl(m):
        p = (HERE / m.group(1)).resolve()
        return f'src="{p.as_uri()}"'
    return re.sub(r'src="(?!https?://|file:///)([^"]+)"', repl, html)

def sig(*labels):
    return "".join(f'<p class="sig"><b>{l}:</b> <span>&nbsp;</span></p>' for l in labels)

cover = f"""
<div class="cover">
<h3>THE UNIVERSITY OF ZAMBIA</h3>
<h3>SCHOOL OF NATURAL AND APPLIED SCIENCES</h3>
<h3>DEPARTMENT OF COMPUTING AND INFORMATICS</h3>
<br/><br/>
<h2>FINAL YEAR PROJECT REPORT</h2>
<h3>ACADEMIC YEAR 2026</h3>
<br/><br/>
<h1 style="page-break-before:avoid">{META['title']}</h1>
<br/>
<p class="center">A Final Year Project Report Submitted to the<br/>Department of Computing and Informatics<br/>in partial fulfilment of the requirements for the award of</p>
<p class="center"><b>{META['degree']}</b></p>
<br/><br/>
<p class="center"><b>Student Name:</b> {META['name']}<br/>
<b>Computer Number:</b> {META['number']}<br/>
<b>Supervisor:</b> {META['supervisor']}<br/>
<b>Date of Submission:</b> {META['date']}</p>
</div>
"""

declaration = f"""
<div class="plain-title">DECLARATION</div>
<p>I declare that this final year project report is my own work and has been prepared in accordance with the academic requirements of the University of Zambia. All sources of information, ideas, data, software, images, and other material that are not my own have been appropriately acknowledged and referenced.</p>
<p>Where this project was undertaken as part of a group, I have clearly identified my individual contributions and have not presented the work of other group members as my own.</p>
<p class="sig"><b>Student Name:</b> {META['name']}</p>
{sig('Computer Number','Signature','Date')}
"""

approval = f"""
<div class="plain-title">APPROVAL</div>
<p>This final year project report has been submitted for examination with the approval of the project supervisor.</p>
{sig('Supervisor Name','Signature','Date','Departmental/Examiner Approval (if applicable)')}
"""

front_md = markdown.markdown((HERE / "front-matter.md").read_text(encoding="utf-8"), extensions=["tables", "sane_lists"])

CHAPTERS = [
    "ch01-introduction.md", "ch02-literature-review.md", "ch03-methodology.md",
    "ch04-analysis-design.md", "ch05-implementation.md", "ch06-testing-results.md",
    "ch07-discussion.md", "ch08-conclusion.md", "references.md",
    "appendix-a-contribution.md", "appendix-b-to-g.md",
]

parts = [cover, declaration, approval, front_md]
parts += [md(c) for c in CHAPTERS]
doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Final Year Project Report 2026</title>{STYLE}</head><body>
{''.join(parts)}
</body></html>"""
out = HERE / "FinalYearReport-2026.html"
out.write_text(doc, encoding="utf-8")
print("Wrote", out, len(doc), "chars")
