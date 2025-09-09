from flask import Flask
from server.database import db
from server.jobs.producer import api_v1 as producer_api
from server.managers.client_manager import ClientManager
from server.config import Config

def create_app():
    
    app = Flask(__name__)
    app.config.from_object(Config)

   # Initialize database
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Database initialization failed: {e}")

    # Attach ClientManager
    app.client_manager = ClientManager()

    # Register blueprint
    app.register_blueprint(producer_api, url_prefix=Config.API_PREFIX)

    # Root endpoint
    @app.route("/")
    def index():
        return {"message": f"LLM Flask Server v{Config.APP_VERSION}"}, 200

    return app
# <<< ADD THIS for Gunicorn >>> 
app = create_app()

