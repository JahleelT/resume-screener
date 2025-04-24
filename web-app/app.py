from flask import Flask, request, render_template
import requests
import fitz  # PyMuPDF for PDF text extraction
import os
from flask.json.provider import DefaultJSONProvider
from bson import ObjectId

app = Flask(__name__)


class MongoJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)


app.json = MongoJSONProvider(app)


def extract_text_from_stream(file_stream):
    """
    Read the uploaded PDF from file_stream and extract up to first 3000 characters of text.
    """
    try:
        # Read the entire file into memory and open with PyMuPDF
        pdf_bytes = file_stream.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()[:3000]
    except Exception as e:
        print("❌ Error extracting text from PDF:", e)
        return "Resume text could not be extracted."


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        resume = request.files.get("resume")
        job_url = request.form.get("job_url")

        if not resume or not job_url:
            return "Missing fields", 400

        # Extract text from the uploaded PDF in-memory
        resume_text = extract_text_from_stream(resume.stream)

        # Send extracted text to ml-client
        payload = {"resume_text": resume_text, "job_url": job_url}
        response = requests.post(f"{os.getenv('ML_CLIENT_HOST')}/analyze", json=payload)

        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError:
            return "ML client did not return valid JSON", 500

        return render_template("result.html", result=result)

    return render_template("index.html")


@app.route("/history")
def view_history():
    try:
        response = requests.get(f"{os.getenv('ML_CLIENT_HOST')}/history")
        records = response.json()
        return render_template("history.html", records=records)
    except Exception as e:
        print("❌ Failed to fetch history:", e)
        return render_template("history.html", records=[])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
