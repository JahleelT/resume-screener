import os
from flask import Flask
from dotenv import load_dotenv
from flask.json.provider import DefaultJSONProvider
from bson import ObjectId

from login import login_manager

load_dotenv()

class MongoJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

def create_app():
  app = Flask(__name__)
  app.secret_key = os.getenv("SECRET_KEY", "dev-change-me")

  app.json_provider_class = MongoJSONProvider

  login_manager.init_app(app)
  login_manager.login_view = "frontend.login"

  from web_app.routes import frontend_bp
  from ml_client.app import routes_bp
  
  app.register_blueprint(frontend_bp)
  app.register_blueprint(routes_bp, url_prefix="/api")

  return app

app = create_app()

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
