from flask import Flask, request, render_template, redirect, url_for
import requests
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "/shared/resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        resume = request.files.get("resume")
        job_url = request.form.get("job_url")

        if not resume or not job_url:
            return "Missing fields", 400

        filename = secure_filename(resume.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        resume.save(filepath)

        response = requests.post("http://ml-client:5001/analyze", json={
            "resume_path": filepath,
            "job_url": job_url
        })
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError:
            return "ML client did not return valid JSON", 500
        return render_template("result.html", result=result)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
