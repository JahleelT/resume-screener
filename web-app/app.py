from flask import Flask, request, render_template, jsonify
import requests
import os
from threading import Thread
from datetime import datetime
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask.json.provider import DefaultJSONProvider


# JSON provider that handles ObjectId
class MongoJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)


app = Flask(__name__)
app.json = MongoJSONProvider(app)

# MongoDB connection
mongo = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))
db = mongo["resume_db"]
collection = db["analyses"]


def extract_text_from_stream(file_stream):
    import fitz  # PyMuPDF

    try:
        pdf_bytes = file_stream.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = "".join(page.get_text() for page in doc)
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

        # 1) Extract text
        resume_text = extract_text_from_stream(resume.stream)

        # 2) Create pending job
        db_payload = {
            "job_url": job_url,
            "resume_text": resume_text,
            "status": "pending",
            "created_at": datetime.utcnow(),
        }
        inserted = collection.insert_one(db_payload)
        job_id = str(inserted.inserted_id)

        # 3) Fire-and-forget trigger to ml-client
        def kick_off():
            try:
                requests.post(f"{os.getenv('ML_CLIENT_HOST')}/process", json={"id": job_id}, timeout=5)
            except Exception:
                pass

        Thread(target=kick_off, daemon=True).start()

        # 4) Return loader page
        return render_template("loading.html", job_id=job_id)

    return render_template("index.html")


@app.route("/status/<job_id>")
def status(job_id):
    rec = collection.find_one({"_id": ObjectId(job_id)})
    if not rec:
        return jsonify({"error": "not_found"}), 404
    if rec.get("status") != "complete":
        return jsonify({"status": "pending"})
    return jsonify({"status": "complete"})


@app.route("/job/<job_id>")
def job(job_id):
    rec = collection.find_one({"_id": ObjectId(job_id)})
    if not rec:
        return jsonify({"error": "not_found"}), 404
    if rec.get("status") != "complete":
        return jsonify({"status": "pending"})
    return render_template("result.html", result=rec)


@app.route("/history", methods=["GET"])
def history():
    try:
        records = list(collection.find().sort("_id", -1).limit(10))
        for r in records:
            r["_id"] = str(r["_id"])
        return render_template("history.html", records=records)
    except Exception as e:
        print("❌ Failed to retrieve history:", e)
        return render_template("history.html", records=[])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
