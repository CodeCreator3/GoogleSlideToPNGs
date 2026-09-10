# GoogleSlideToPNGs

Simple Flask app that accepts a link to a Google Slides presentation and returns a ZIP of all slides converted to PNG.

Requirements
- Presentation must be shared "Anyone with the link can view" so the server can fetch the PDF export.
- Python 3.8+
- Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run

```bash
python app.py
```

Open http://localhost:7860 and paste the Slides link.

Notes
- Uses Google Slides export to PDF endpoint and renders pages to PNG using PyMuPDF.
- If your slides are not public, you'll need to supply OAuth credentials and use the Google Slides API instead.
