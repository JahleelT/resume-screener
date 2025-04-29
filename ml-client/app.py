from flask import Flask, request, jsonify
import requests
import os
import json
import re
from threading import Thread
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask.json.provider import DefaultJSONProvider
from bson import ObjectId
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

title_app = Flask(__name__)


class MongoJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)


app = Flask(__name__)
app.json = MongoJSONProvider(app)

mongo = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))
db = mongo["resume_db"]
collection = db["analyses"]


def fetch_job_description(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=15000)
            page.wait_for_timeout(3000)
            text = page.inner_text("body")
            browser.close()
            return text[:3000]
    except Exception as e:
        print("⚠️ Failed to fetch job description:", e)
        return "Job description could not be fetched."


def build_prompt(resume_text, job_desc):
    return f"""
You're a resume screener. Compare the resume and job description below.
Give your response as a JSON object with three keys:
- \"summary\": a short summary of the candidate
- \"suggestions\": 3–5 concrete ways to improve the resume
- \"job_focus\": a bullet-style list of what the job posting emphasizes.

Resume:
{resume_text}

Job Description:
{job_desc}

Respond with only the raw JSON object:
{{
"summary": "...",
"suggestions": ["..."],
"job_focus": ["..."]
}}
"""


def call_openai(prompt):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400,
        "temperature": 0.7,
    }
    r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    raw = r.json()["choices"][0]["message"]["content"].strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    if (raw.startswith("'") and raw.endswith("'")) or (raw.startswith('"') and raw.endswith('"')):
        raw = raw[1:-1]
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError("Could not parse OpenAI response as JSON")


@app.route("/process", methods=["POST"])
def process():
    data = request.get_json(force=True)
    job_id = data.get("id")
    if not job_id:
        return jsonify({"error": "missing id"}), 400

    Thread(target=do_work, args=(job_id,), daemon=True).start()
    return jsonify({"status": "started"}), 202


def do_work(job_id):
    rec = collection.find_one({"_id": ObjectId(job_id)})
    if not rec:
        print(f"Job with id {job_id} not found in the database.")
        return
    print(f"Updating status to 'processing' for job_id: {job_id}")
    collection.update_one({"_id": ObjectId(job_id)}, {"$set": {"status": "processing"}})

    try:
        jd = fetch_job_description(rec["job_url"])
        print(f"Fetched job description for job_id: {job_id}")
    except Exception as e:
        print(f"Failed to fetch job description for job_id {job_id}: {e}")
        jd = "Job description not available."

    result = call_openai(build_prompt(rec["resume_text"], jd))
    print(f"OpenAI result: {result}")

    print(f"Updating MongoDB to 'complete' for job_id: {job_id}")
    collection.update_one(
        {"_id": ObjectId(job_id)},
        {
            "$set": {
                "status": "complete",
                "summary": result["summary"],
                "suggestions": result["suggestions"],
                "job_focus": result["job_focus"],
            }
        },
    )
    print(f"Job {job_id} has been processed and status updated to 'complete'.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
