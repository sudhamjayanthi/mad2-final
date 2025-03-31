from datetime import datetime
from flask import Flask, jsonify, request
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    auth_required,
    roles_required,
    hash_password,
)
from flask_cors import CORS
from models import db, User, Role
from config import Config
from routes import init_routes

app = Flask(__name__)

from flask_migrate import Migrate 
migrate = Migrate(app, db) 

CORS(
    app,
    resources={
        r"/*": {
            "origins": ["http://localhost:5173"],  # Vue dev server
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authentication-Token"],
        }
    },
)
app.config.from_object(Config)

db.init_app(app)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

init_routes(app)

with app.app_context():
    db.create_all()

    if not user_datastore.find_role("admin"):
        user_datastore.create_role(name="admin")
    if not user_datastore.find_role("student"):
        user_datastore.create_role(name="student")
    db.session.commit()

    if not user_datastore.find_user(email="admin@gmail.com"):
        user_datastore.create_user(
            email="admin@gmail.com",
            password=hash_password("admin"),
            full_name="Admin",
            qualification="B.Tech",
            dob=datetime.strptime("2005-07-15", "%Y-%m-%d"),
            roles=["admin"],
        )
        db.session.commit()


@app.route("/")
def home():
    return "Welcome to Quiz Master API. You know which route to hit, if you are authorised :)"


@app.route("/admin/dashboard")
@auth_required("token")
@roles_required("admin")
def admin_dashboard():
    return jsonify({"message": "Welcome to admin dashboard"})


@app.route("/user/dashboard")
@auth_required("token")
def user_dashboard():
    return jsonify({"message": "Welcome to user dashboard"})


if __name__ == "__main__":
    app.run(port=6900, debug=True)
