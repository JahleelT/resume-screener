from flask import Flask, Blueprint, abort, flash, redirect, url_for, request, render_template, jsonify
import requests
import os
from threading import Thread
from datetime import datetime
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask.json.provider import DefaultJSONProvider
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import fitz
from werkzeug.security import generate_password_hash, check_password_hash
from login import login_manager

frontend_bp = Blueprint(
    'frontend', 
    __name__,
    template_folder='templates',
    )

mongo = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))
db_name = "resume_db"
db = mongo[db_name]
collection = db["analyses"]

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
        return "Error: Resume text could not be extracted."

@frontend_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        resume = request.files.get("resume")
        job_url = request.form.get("job_url")
        if not resume or not job_url:
            flash("Please provide both a resume and job URL.", "danger")
            return redirect(url_for("frontend.index"))

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

@frontend_bp.route("/status/<job_id>")
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

@frontend_bp.route("/job/<job_id>")
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

@frontend_bp.route("/history")
def history():
    if not current_user.is_authenticated:
        return render_template("history.html", records=[])
    query = {"user_id": ObjectId(current_user.id)}
    records = list(collection.find(query).sort("_id", -1).limit(10))
    for r in records:
        r["_id"] = str(r["_id"])
    return render_template("history.html", records=records)

@frontend_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        u = request.form["username"]
        p = generate_password_hash(request.form["password"])
        mongo[db_name]["users"].insert_one({"username": u, "password": p})
        return redirect(url_for("frontend.login"))
    return render_template("signup.html")

@frontend_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        doc = mongo[db_name]["users"].find_one({"username": u})
        if doc and check_password_hash(doc["password"], request.form["password"]):
            login_user(User(doc))
            return redirect(url_for("frontend.index"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@frontend_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("frontend.index"))
