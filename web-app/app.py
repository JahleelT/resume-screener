from flask import Flask, request, render_template, jsonify
import requests
import os
from threading import Thread
from datetime import datetime
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask.json.provider import DefaultJSONProvider
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask import flash, redirect, url_for, abort
import fitz


class MongoJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)


app = Flask(__name__)
app.json = MongoJSONProvider(app)
app.secret_key = os.getenv("SECRET_KEY", "dev-change-me-to-a-real-secret")

mongo = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))
db_name = "resume_db"
db = mongo[db_name]
collection = db["analyses"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, mongo_doc):
        self.id = str(mongo_doc["_id"])
        self.username = mongo_doc["username"]


@login_manager.user_loader
def load_user(user_id):
    doc = mongo[db_name]["users"].find_one({"_id": ObjectId(user_id)})
    return User(doc) if doc else None


def extract_text_from_stream(file_stream):

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

        resume_text = extract_text_from_stream(resume.stream)

        db_payload = {
            "job_url": job_url,
            "resume_text": resume_text,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "user_id": ObjectId(current_user.id) if current_user.is_authenticated else None,
        }

        inserted = collection.insert_one(db_payload)
        job_id = str(inserted.inserted_id)

        def kick_off():
            try:
                requests.post(f"{os.getenv('ML_CLIENT_HOST')}/process", json={"id": job_id}, timeout=5)
            except Exception:
                pass

        Thread(target=kick_off, daemon=True).start()

        return render_template("loading.html", job_id=job_id)

    return render_template("index.html")


@app.route("/status/<job_id>")
def status(job_id):
    rec = collection.find_one({"_id": ObjectId(job_id)})
    if not rec:
        return jsonify({"error": "not_found"}), 404

    owner_id = rec.get("user_id")
    # if this job was created by a logged-in user, block everyone else
    if owner_id is not None:
        if not current_user.is_authenticated or str(owner_id) != current_user.id:
            abort(404)

    if rec.get("status") != "complete":
        return jsonify({"status": "pending"})
    return jsonify({"status": "complete"})


@app.route("/job/<job_id>")
def job(job_id):
    rec = collection.find_one({"_id": ObjectId(job_id)})
    if not rec:
        return jsonify({"error": "not_found"}), 404

    owner_id = rec.get("user_id")
    if owner_id is not None:
        if not current_user.is_authenticated or str(owner_id) != current_user.id:
            abort(404)

    if rec.get("status") != "complete":
        return jsonify({"status": "pending"})
    return render_template("result.html", result=rec)


@app.route("/history")
def history():
    if not current_user.is_authenticated:
        return render_template("history.html", records=[])
    query = {"user_id": ObjectId(current_user.id)}
    records = list(collection.find(query).sort("_id", -1).limit(10))
    for r in records:
        r["_id"] = str(r["_id"])
    return render_template("history.html", records=records)


from werkzeug.security import generate_password_hash, check_password_hash


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        u = request.form["username"]
        p = generate_password_hash(request.form["password"])
        mongo[db_name]["users"].insert_one({"username": u, "password": p})
        return redirect(url_for("login"))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        doc = mongo[db_name]["users"].find_one({"username": u})
        if doc and check_password_hash(doc["password"], request.form["password"]):
            login_user(User(doc))
            return redirect(url_for("index"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
