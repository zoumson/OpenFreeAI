from flask import Flask
from server.database import db
from server.jobs.producer import api_v1 as producer_api
from server.managers.client_manager import ClientManager
from server.config import Config
import os 

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # db_path = Config.SQLALCHEMY_DATABASE_URI.replace("sqlite:///", "")
    # if os.path.exists(db_path):
    #     os.remove(db_path)

    # app = create_app()
    # with app.app_context():
    #     db.create_all()



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
