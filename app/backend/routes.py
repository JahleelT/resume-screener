from flask import request, jsonify
import requests
import os
import json
import re
from threading import Thread
from .app import routes_bp
from .db import collection
from pinecone import Index
from app.backend.utils.resume_jd_match_utils import match_resume_with_retrieval
from app.backend.utils.pinecone_init import begin_index

res_index = begin_index("resumes")
jd_index = begin_index("job_descriptions")

@routes_bp.route("/match", methods=["POST"])
def match_resume_route():
    result = match_resume_with_retrieval(res_index, resume_id, jd_text)



@routes_bp.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

