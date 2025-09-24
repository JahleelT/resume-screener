import os
from flask import Flask
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from backend.utils.pinecone_init import begin_index

load_dotenv()


jwt = JWTManager()

def create_app():
  app = Flask(__name__)
  app.secret_key = os.getenv("SECRET_KEY", "dev-change-me")

  app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret")
  jwt.init_app(app)

  app.config["RESUME_INDEX"] = begin_index("resumes")
  app.config["JD_INDEX"] = begin_index("job_descriptions")

  CORS(app, resources={r"/api/*": {"origins": "*"}})


  from backend.app import routes_bp
  app.register_blueprint(routes_bp, url_prefix="/api")

  return app

app = create_app()

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
