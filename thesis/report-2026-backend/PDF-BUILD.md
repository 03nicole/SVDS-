# Backend report PDF

The paginated PDF is built directly from the chapter Markdown by `build_pdf.py`.
The older `build.py` creates an HTML preview; printing that preview does not
reproduce the PDF navigation or its vector diagrams.

From the repository root, using Python 3.12 on Windows:

```powershell
.venv312/Scripts/python.exe -m pip install reportlab markdown beautifulsoup4 pillow pymupdf
.venv312/Scripts/python.exe thesis/report-2026-backend/build_pdf.py
```

The build writes `output/pdf/FinalYearReport-2026-Backend.pdf`. It repeats pagination
until the contents, figure list and table list have stable page references.
It embeds Windows Times New Roman, Arial and Consolas fonts. Diagram definitions
are vector drawings in the builder; the original screenshot is rendered as
four labelled detail crops without cutting endpoint rows.

Review the rendered PDF before copying it over the report-folder PDF. Personal
details, acknowledgements, reference completion and contribution percentages
remain author-supplied fields. The layout pass does not verify the technical claims.
