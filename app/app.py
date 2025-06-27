import os
from flask import Flask
from dotenv import load_dotenv

from web_app.routes import frontend_bp
from ml_client.routes import routes_bp
from flask_login import LoginManager

load_dotenv()

def create_app():
  app = Flask(__name__)
  app.secret_key = os.getenv("SECRET_KEY", "dev-change-me")

  app.register_blueprint(frontend_bp)
  app.register_blueprint(routes_bp)

  return app

if __name__ == "__main__":
  app = create_app()
  app.run(host="0.0.0.0", port=5000)

class MongoJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)