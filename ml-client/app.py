from flask import Flask, request, jsonify
import requests
import os
import base64
import json
import re
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
    # TODO: Add real PDF parsing later
    return f"Simulated resume content for: {path}"

def fetch_job_description(url):
    # TODO: Replace with scraping logic if needed
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

    # Construct prompt for GPT
    prompt = f"""
    You're a resume screener. Compare the resume below with the job description.
    Give a short summary and a list of 3–5 suggestions to improve the resume to better match the job.

    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Respond with ONLY a JSON object, and nothing else. Format it like this:
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

        print("✅ Raw OpenAI HTTP response status:", gpt_response.status_code)
        print("📦 Full OpenAI response body:")
        print(gpt_response.text)

        gpt_response.raise_for_status()
        raw_output = gpt_response.json()["choices"][0]["message"]["content"].strip()

        print("RAW GPT OUTPUT >>>")
        print(raw_output)
        print("<<< END GPT OUTPUT")

        # Clean up markdown code block
        if raw_output.startswith("```"):
            raw_output = re.sub(r"^```(?:json)?\\s*", "", raw_output)
            raw_output = re.sub(r"\\s*```$", "", raw_output)

        try:
            result = json.loads(raw_output)
        except json.JSONDecodeError:
            print("❌ Failed to decode GPT output:\n", raw_output)
            result = {
                "summary": "GPT response could not be parsed.",
                "suggestions": []
            }

    except Exception as e:
        import traceback
        print("❌ Error communicating with OpenAI:")
        traceback.print_exc()
        result = {
            "summary": "OpenAI API call failed.",
            "suggestions": []
        }

    result["job_url"] = job_url
    result["resume_path"] = resume_path

    # Save to MongoDB
    inserted = collection.insert_one(result)
    result["_id"] = str(inserted.inserted_id)

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
