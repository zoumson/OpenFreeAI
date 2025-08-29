from flask import Flask
from server.database import db
from server.jobs.producer import api_v1 as producer_api
from server.config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)
with app.app_context():
    db.create_all()

# Register blueprint dynamically using the prefix from config
app.register_blueprint(producer_api, url_prefix=Config.API_PREFIX)

# Version endpoint using the same prefix
@api_v1.route("/version", methods=["GET"])
def get_version():
    return {"version": Config.APP_VERSION}

if __name__ == "__main__":
    app.run(debug=True, port=5000)