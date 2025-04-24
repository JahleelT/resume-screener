from flask import Flask, request, jsonify
import requests
import os
import json
import re
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from playwright.sync_api import sync_playwright

app = Flask(__name__)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# MongoDB setup
mongo = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))
db = mongo["resume_db"]
collection = db["analyses"]


def fetch_job_description(url):
    """
    Uses Playwright to scrape the job description text from the given URL.
    """
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
    data = request.get_json(force=True)
    resume_text = data.get("resume_text")
    job_url = data.get("job_url")

    if not resume_text or not job_url:
        return jsonify({"error": "Missing resume_text or job_url"}), 400

    # Fetch job description separately
    job_description = fetch_job_description(job_url)

    # Build prompt for OpenAI
    prompt = f"""
You're a resume screener. Compare the resume and job description below.
Give your response as a JSON object with three keys:
- "summary": a short summary of the candidate
- "suggestions": 3–5 concrete ways to improve the resume
- "job_focus": a bullet-style list of what the job posting emphasizes (skill sets, experience, traits). Definitely include location and salary if mentioned.

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
        "temperature": 0.7,
    }

    try:
        gpt_response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30
        )
        gpt_response.raise_for_status()
        raw_output = gpt_response.json()["choices"][0]["message"]["content"].strip()

        # Strip Markdown fences if present
        if raw_output.startswith("```"):
            raw_output = re.sub(r"^```(?:json)?\s*", "", raw_output)
            raw_output = re.sub(r"\s*```$", "", raw_output)
        # Strip surrounding quotes
        if (raw_output.startswith("'") and raw_output.endswith("'")) or (
            raw_output.startswith('"') and raw_output.endswith('"')
        ):
            raw_output = raw_output[1:-1]

        # Extract JSON object
        match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if match:
            result = json.loads(match.group(0))
        else:
            raise ValueError("Could not locate JSON in GPT output")
    except Exception as e:
        print("❌ Error during OpenAI processing:", e)
        result = {"summary": "An error occurred during analysis.", "suggestions": [], "job_focus": []}

    # Attach metadata
    result["job_url"] = job_url

    # Persist to MongoDB
    try:
        inserted = collection.insert_one(result)
        result["_id"] = str(inserted.inserted_id)
    except Exception as e:
        print("❌ Failed to save analysis to DB:", e)

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
