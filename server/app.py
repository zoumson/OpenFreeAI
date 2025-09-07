from flask import Flask
from server.database import db
from server.jobs.producer import api_v1 as producer_api
from server.managers.client_manager import ClientManager
from server.config import Config

def create_app():
    api_key = Config.OPENAI_API_KEY

    # if api_key:
    #     print(f"OPENAI_API_KEY loaded ✅ (...{api_key[:6]})")
    # else:
    #     print("⚠️ OPENAI_API_KEY is missing!")
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Attach ClientManager
    app.client_manager = ClientManager()

    # Register blueprint
    app.register_blueprint(producer_api, url_prefix=Config.API_PREFIX)

    # Root endpoint
    @app.route("/")
    def index():
        return {"message": f"LLM Flask Server v{Config.APP_VERSION}"}, 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=True)
