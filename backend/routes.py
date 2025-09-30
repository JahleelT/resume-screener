from flask import request, jsonify, current_app
from threading import Thread
from pinecone import Index
import bcrypt
import os
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from .app import routes_bp
from .db import crud
from backend.utils.pinecone_init import begin_index
from backend.utils.resume_jd_match_utils import match_resume_with_retrieval
from backend.loaders.jd_loaders import load_jd, split_jd
from backend.loaders.resume_loaders import load_resume, split_resume
from backend.embeddings.jd_embeddings import embed_jd_chunks, embed_query
from backend.embeddings.resume_embeddings import embed_chunks, embed_query
from backend.utils import jd_pc, res_pc

"""
AUTH routes
"""

@routes_bp.route("/auth/register", methods=["POST"])
def create_user(): # TODO update parameters
    data = request.get_json()

    if not data or "email" not in data or "password" not in data or "name" not in data:
        return jsonify({"error": "Name, email, and password are all required"}), 400
    
    email = data["email"]
    raw_password = data["password"]
    name = data["name"]
    # First salt and hash the password
    hashed = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt(12))

    try:
        new_user = crud.create_user(name, email, hashed)
        access_token = create_access_token(identity= new_user.id)

        return jsonify({
            "access_token": access_token,
            "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "created_at": new_user.created_at.isoformat() if new_user.created_at else None
            }
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@routes_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "please enter an email and password to proceed"}), 401

    email = data.get("email")
    password = data.get("password")
    user = crud.get_user_by_email(email)

    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password_hash):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        "message": "login successful!",
        "access_token": access_token,
        "users": {
        "user_id": user.id,
        "name": user.name,
        "email": user.email
        }
        # TODO add Flask-JWT for actual login logic
    }), 200



@routes_bp.route("/auth/me", methods=["GET"])
@jwt_required
def get_me():
    current_user_id = get_jwt_identity()

    user = crud.get_user_by_id(current_user_id)

    if not user:
        return jsonify({
            "error": "User could not be found. Please try again."
        }), 404

    return jsonify({
        "user": {
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    }), 200


"""
USER routes
"""

@routes_bp.route("/users/me", methods=["PATCH"])
@jwt_required
def update_user():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if "updates" not in data:
        return jsonify({
            "error": "There is information missing from the payload (user_id or the updates in dictionary format)"
        }), 404
    
    updates: dict = data["updates"]
    
    updated = crud.update_user(current_user_id, updates)

    return jsonify({
        "name": updated.name,
        "email": updated.email
    }), 200

@routes_bp.route("/users/me", methods=["DELETE"])
@jwt_required
def delete_user():
    current_user_id = get_jwt_identity()

    user_exists = crud.get_user_by_id(current_user_id)

    if user_exists:
        success = crud.delete_user(current_user_id)
        if success:
            return jsonify({
                "message": "successfully deleted user account! We hope you return later"
            }), 204
        return jsonify({
            "error": "Failed to delete user. Please try again later."
        }), 400
    return jsonify({
        "error": "Failed to retrieve user. Please try again later."
    }), 404

"""
RESUME routes
"""

@routes_bp.route("/resume", methods=["POST"])
@jwt_required
def create_resume():
    data = request.form
    current_user_id = get_jwt_identity()

    text = data.get("text")

    resume_file = request.files["resume"]

    if not resume_file or not text:
        return jsonify({
            "error": "There is missing file or text."
        }), 400
    
    filename = os.path.join("/tmp", secure_filename(resume_file.filename))
    resume_file.save(filename)
    
    existing = crud.get_resume_by_filename(filename, current_user_id)

    if existing:
        resume_id = existing.id
    else:
        new_resume = crud.create_resume({"text": text}, current_user_id, filename)
        resume_id = new_resume.id

    os.remove(filename)

    return jsonify({
        "resume_id": resume_id, "text": text
    }), 201


@routes_bp.route("/resumes", methods=["GET"])
@jwt_required
def get_resumes():
    current_user_id = get_jwt_identity()

    resumes = crud.get_resume_by_id(current_user_id)

    if not resumes:
        return jsonify({
            "error": "No resumes found for this user. Please try again or add resumes"
        }), 404

    return jsonify({
        "resumes": [
            {
                "id": resume.id,
                "text": resume.text,
                "created_at": resume.created_at
            } for resume in resumes
        ]
    }), 200

@routes_bp.route("/resumes/<int:resume_id>", methods=["GET"])
@jwt_required
def get_resume_by_id(resume_id):
    fetched_resume = crud.get_resume_by_id(resume_id)

    if not fetched_resume:
        return jsonify({
            "error": "Resume ID could not be matched with current stored resumes. Please try another resume ID."
        }), 404
    
    return jsonify({
        "text": fetched_resume.text
    }), 200

@routes_bp.route("/resumes/<int:resume_id>", methods=["DELETE"])
@jwt_required
def delete_resume(resume_id):
    fetched_resume = crud.get_resume_by_id(resume_id)

    if fetched_resume:
        crud.delete_resume(resume_id)
        return jsonify({
            "message": "successfully deleted resume!"
        }), 204

    return jsonify({
        "error": "Resume could not be found. Please try again."
    }), 404

"""
ANALYSIS routes
"""

@routes_bp.route("/analyses", methods=["POST"])
@jwt_required
def create_analysis():
    current_user_id = get_jwt_identity()

    resume_index = current_config["RESUME_INDEX"]
    jd_index = current_config["JD_INDEX"]

    if "resume" not in request.files or not request.form.get("url"):
        return jsonify({
            "error": "There is information missing from the payload. Please make sure that you have sent a resume file (PDF, TXT, DOCX) and the URL to a job posting."
        }), 400
    
    resume = request.files['resume']
    filename = os.path.join("/tmp", secure_filename(resume.filename))
    resume.save(filename)

    jd_url = request.form.get('url')

    res_docs = load_resume(filename)
    jd_docs = load_jd(jd_url)

    res_split = split_resume(res_docs)
    jd_split = split_jd(jd_docs)

    retrieved_resume = crud.get_resume_by_filename(filename, current_user_id)
    jd_text = " ".join([c["text"] for c in jd_split])
    resume_text = " ".join([d.page_content for d in res_docs])
    if retrieved_resume:
        resume_id = retrieved_resume.id
    else:
        new_resume = crud.create_resume({"text": resume_text}, current_user_id, filename)
        resume_id = new_resume.id

    try:
        embedded_res = embed_chunks(res_split, current_user_id)
        embedded_jd = embed_jd_chunks(jd_split, current_user_id)
        
        res_pc.upsert_vectors(resume_index, embedded_res)
        jd_pc.upsert_vectors(jd_index, embedded_jd)

        analysis_data = match_resume_with_retrieval(resume_index, resume_id, jd_text)
    except:
        return jsonify({
            "error": "There was an error with the AI processing/pinecone. Please try again."
        }), 409
    
    new_analysis = crud.create_analysis(analysis_data, resume_id, current_user_id)
    os.remove(filename)
    if not new_analysis:
        return jsonify({
            "error": "failed to create analysis with the information provided. Please try again."
        }), 403
    
    return jsonify({
        "jd_text": new_analysis.jd_text,
        "result": new_analysis.result
    }), 201

@routes_bp.route("/analyses", methods=["GET"])
@jwt_required
def get_analyses():
    current_user_id = get_jwt_identity()

    analyses = crud.get_analyses_by_user(current_user_id)

    if not analyses:
        return jsonify({
            "error": "Analyses could not be retrieved. Please ensure you have created an analysis before trying again."
        }), 404
    
    return jsonify({
        "analyses": [
            {
                "resume_id": analysis.resume_id,
                "jd_text": analysis.jd_text,
                "result": analysis.result,
                "created_at": analysis.created_at
            } for analysis in analyses
        ]
    }), 200

@routes_bp.route("/analyses/<int:analysis_id>", methods=["GET"])
@jwt_required
def get_analysis(analysis_id):
    fetched_analysis = crud.get_analysis_by_id(analysis_id)

    if not fetched_analysis:
        return jsonify({
            "error": "Analysis could not be found. Please try again"
        }), 404
    
    return jsonify({
        "result": fetched_analysis.result
    }), 200

@routes_bp.route("/resumes/<int:resume_id>/analysis", methods=["GET"])
@jwt_required
def analyses_by_resume(resume_id):
    resume_id_analyses = crud.get_analyses_by_resume(resume_id)

    if not resume_id_analyses:
        return jsonify({
            "error": "Could not retrieve analyses from that resume ID. Please try again."
        }), 404
    

    return jsonify({
        "analyses": [
            {"jd_text": analysis.jd_text, "result": analysis.result}
            for analysis in resume_id_analyses
        ]
    }), 200

@routes_bp.route("/analyses/<int:analysis_id>", methods=["DELETE"])
@jwt_required
def delete_analysis(analysis_id):
    fetched_analysis = crud.get_analysis_by_id(analysis_id)

    if not fetched_analysis:
        return jsonify({
            "error": "Failed to retrieve analysis from the given ID. Please try again."
        }), 404
    
    deleted = crud.delete_analysis(analysis_id)

    if not deleted:
        return jsonify({
            "error": "Failed to delete the given analysis. Please try again."
        }), 404
    
    return jsonify({
        "message": "Successfully deleted analysis!"
    }), 200


"""
MISC routes
"""

@routes_bp.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

