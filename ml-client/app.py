from flask import Flask, request, jsonify
import requests
import os
import base64
import json
from dotenv import load_dotenv
from pymongo import MongoClient

app = Flask(__name__)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# MongoDB setup
mongo = MongoClient("mongodb://mongo:27017/")
db = mongo["resume_db"]
collection = db["analyses"]

def extract_text_from_file(path):
    # In production, use pdfplumber / python-docx here
    return f"Simulated resume content for: {path}"

def fetch_job_description(url):
    # Optional future step: scrape job posting from the URL
    return f"Simulated job description for URL: {url}"

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
You're a resume screener. Compare the resume below with the job description.
Give a summary and a list of 3–5 improvement suggestions to better match the job.

Resume:
{resume_text}

Job Description:
{job_description}

Respond in this exact JSON format:
{{
  "summary": "...",
  "suggestions": ["...", "...", "..."]
}}
"""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.7
    }

    try:
        gpt_response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        gpt_response.raise_for_status()
        raw_output = gpt_response.json()["choices"][0]["message"]["content"]

        try:
            result = json.loads(raw_output)
        except json.JSONDecodeError:
            print("Failed to decode GPT output:", raw_output)
            result = {
                "summary": "GPT response could not be parsed.",
                "suggestions": []
            }

    except Exception as e:
        print("Error communicating with OpenAI:", e)
        result = {
            "summary": "OpenAI API call failed.",
            "suggestions": []
        }

    result["job_url"] = job_url
    result["resume_path"] = resume_path

    # Save to MongoDB
    collection.insert_one(result)

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
