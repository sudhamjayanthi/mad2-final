from datetime import datetime
from flask import Flask
from models import db, User

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password="admin",
            full_name="Admin",
            qualification="B.Tech",
            dob=datetime.strptime("2005-07-15", "%Y-%m-%d"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()


@app.route("/")
def home():
    return "Welcome to Quiz Master API. You know which route to hit, if you are authorised :)"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
