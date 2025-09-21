from flask import request, jsonify
from threading import Thread
from .app import routes_bp
from .db import crud
from pinecone import Index
from app.backend.utils.resume_jd_match_utils import match_resume_with_retrieval
from app.backend.utils.pinecone_init import begin_index
import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

res_index = begin_index("resumes")
jd_index = begin_index("job_descriptions")

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
    hashed = bcrypt.hashpw(raw_password, bcrypt.gensalt(12))

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

    updates: dict = data["updates"]

    if "updates" not in data:
        return jsonify({
            "error": "There is information missing from the payload (user_id or the updates in dictionary format)"
        }), 404
    
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
    data = request.get_json()
    current_user_id = get_jwt_identity()

    text = data["text"]

    if not data or "text" not in data:
        return jsonify({
            "error": "There is missing data from the payload. Please try again"
        }), 400
    
    new_resume = crud.create_resume({"text": text}, current_user_id)

    return jsonify({
        "text": new_resume.text
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

    data = request.get_json()

    if not data or "resume_id" not in data or "analysis_data" not in data:
        return jsonify({
            "error": "There is information missing from the payload. Please make sure that the resume ID and analysis data are part of the payload."
        }), 400
    
    resume_id = data["resume_id"]
    analysis_data = data["analysis_data"]
    
    new_analysis = crud.create_analysis(analysis_data, resume_id, current_user_id)
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

