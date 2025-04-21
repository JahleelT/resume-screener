from flask import Flask, request, jsonify
import requests
import os
import json
import re
import fitz
from dotenv import load_dotenv
from pymongo import MongoClient
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

app = Flask(__name__)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# MongoDB setup
mongo = MongoClient("mongodb://mongo:27017/")
db = mongo["resume_db"]
collection = db["analyses"]


def extract_text_from_file(path):
    try:
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()[:3000]
    except Exception as e:
        print("❌ Error reading PDF:", e)
        return "Resume text could not be extracted."

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

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    resume_path = data.get("resume_path")
    job_url = data.get("job_url")

    if not resume_path or not job_url:
        return jsonify({"error": "Missing resume_path or job_url"}), 400

    resume_text = extract_text_from_file(resume_path)
    job_description = fetch_job_description(job_url)

    prompt = f"""
    You're a resume screener. Compare the resume and job description below.
    Give your response as a JSON object with three keys:
    - "summary": a short summary of the candidate
    - "suggestions": 3–5 concrete ways to improve the resume
    - "job_focus": a bullet-style list of what the job posting emphasizes (skill sets, experience, traits)

        Resume:
        {resume_text}

        Job Description:
        {job_description}

    Respond with only the raw JSON object. No commentary or formatting. Format exactly like:
    {{
    "summary": "...",
    "suggestions": ["...", "..."],
    "job_focus": ["...", "..."]
    }}
    """

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}

    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400,
        "temperature": 0.7
    }

    try:
        gpt_response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30
        )

        print("✅ OpenAI response status:", gpt_response.status_code)
        print("📦 Raw GPT response:", gpt_response.text)

        gpt_response.raise_for_status()
        raw_output = gpt_response.json()["choices"][0]["message"]["content"].strip()

        if raw_output.startswith("```"):
            raw_output = re.sub(r"^```(?:json)?\s*", "", raw_output)
            raw_output = re.sub(r"\s*```$", "", raw_output)
        if (raw_output.startswith("'") and raw_output.endswith("'")) or \
           (raw_output.startswith('"') and raw_output.endswith('"')):
            raw_output = raw_output[1:-1]

        try:
            m = re.search(r"\{.*\}", raw_output, re.DOTALL)
            if m:
                result = json.loads(m.group(0))
        except json.JSONDecodeError:
            print("❌ Failed to decode GPT output:\n", raw_output)
            result = {
                "summary": "GPT response could not be parsed.",
                "suggestions": [],
                "job_focus": []
            }

    except Exception as e:
        import traceback

        print("❌ Error communicating with OpenAI:")
        traceback.print_exc()
        result = {
            "summary": "OpenAI API call failed.",
            "suggestions": [],
            "job_focus": []
        }

    result["job_url"] = job_url
    result["resume_path"] = resume_path

    inserted = collection.insert_one(result)
    result["_id"] = str(inserted.inserted_id)

    return jsonify(result)

@app.route("/history", methods=["GET"])
def history():
    try:
        records = list(collection.find().sort("_id", -1).limit(10))
        for r in records:
            r["_id"] = str(r["_id"])
        return jsonify(records)
    except Exception as e:
        print("❌ Failed to retrieve history:", e)
        return jsonify([])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
