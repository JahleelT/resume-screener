from flask import jsonify
from threading import Thread
from .app import routes_bp
from .db import crud
from pinecone import Index
from app.backend.utils.resume_jd_match_utils import match_resume_with_retrieval
from app.backend.utils.pinecone_init import begin_index

res_index = begin_index("resumes")
jd_index = begin_index("job_descriptions")

"""
AUTH routes
"""

@routes_bp.route("/auth/register", methods=["POST"])
def create_user(): # TODO update parameters
    # TODO
    return

@routes_bp.route("/auth/login", methods=["POST"])
def login():
    # TODO
    return

@routes_bp.route("/auth/me", methods=["GET"])
def get_me():
    # TODO
    return

"""
USER routes
"""

@routes_bp.route("/users/me", method=["PATCH"])
@routes_bp.login_required
def update_user():
    # TODO
    return

@routes_bp.route("/users/me", methods=["DELETE"])
@routes_bp.login_required
def delete_user():
    # TODO
    return


"""
RESUME routes
"""

@routes_bp.route("/resume", methods=["POST"])
def create_resume():
    # TODO
    return

@routes_bp.route("/resumes", methods=["GET"])
def get_resume():
    # TODO return
    return

@routes_bp.route("/resumes/<int:resume_id>", methods=["GET"])
def get_resume_by_id():
    # TODO
    return

@routes_bp.route("/resumes/<int:resume_id>", methods=["DELETE"])
def delete_resume():
    # TODO
    return

"""
ANALYSIS routes
"""

@routes_bp.route("/analyses", methods=["POST"])
def create_analysis():
    # TODO
    return

@routes_bp.route("/analyses", methods=["GET"])
def get_analyses():
    # TODO
    return

@routes_bp.route("/analyses/<int:analysis_id>", methods=["GET"])
def get_analysis():
    # TODO
    return

@routes_bp.route("/resumes/<int:resume_id>/analysis", methods=["GET"])
def analysis_by_resume():
    # TODO
    return

@routes_bp.route("/analyses/<int:analysis_id>", methods=["DELETE"])
def delete_analysis():
    # TODO
    return


"""
MISC routes
"""

@routes_bp.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

