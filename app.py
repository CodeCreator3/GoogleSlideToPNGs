from flask import Flask, request, send_file, render_template, redirect, url_for
import requests
import io
import re
import zipfile
import fitz  # PyMuPDF

app = Flask(__name__)


def extract_presentation_id(url: str) -> str:
    patterns = [
        r"/d/([a-zA-Z0-9_-]+)",
        r"presentation/d/([a-zA-Z0-9_-]+)",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    url = request.form.get("url") or (request.json and request.json.get("url"))
    if not url:
        return redirect(url_for("index"))

    pres_id = extract_presentation_id(url)
    if not pres_id:
        return "Could not extract presentation ID from URL", 400

    pdf_url = f"https://docs.google.com/presentation/d/{pres_id}/export/pdf"

    try:
        resp = requests.get(pdf_url, stream=True, timeout=30)
    except Exception as e:
        return f"Error downloading PDF: {e}", 500

    if resp.status_code != 200 or 'application/pdf' not in resp.headers.get('Content-Type', ''):
        return (
            "Failed to download presentation as PDF. Ensure the presentation is shared 'Anyone with the link can view'.",
            400,
        )

    pdf_bytes = resp.content

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        return f"Error opening PDF: {e}", 500

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, page in enumerate(doc, start=1):
            mat = fitz.Matrix(2, 2)  # increase resolution
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            name = f"slide_{i:03}.png"
            zf.writestr(name, img_data)

    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"presentation_{pres_id}_pngs.zip",
        mimetype="application/zip",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
