from flask import Blueprint, request, jsonify
from flask_security import auth_required, hash_password, verify_password
from flask_security.utils import login_user, logout_user
from models import User, db, Role
from datetime import datetime, timezone

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Missing email or password"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if user and verify_password(data["password"], user.password):
        if not user.active:
            return jsonify({"message": "Your access is disabled"}), 403

        login_user(user)
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        return jsonify(
            {
                "token": user.get_auth_token(),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "roles": [role.name for role in user.roles],
                },
            }
        ), 200

    return jsonify({"message": "Invalid email or password"}), 401


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    required_fields = ["email", "password", "full_name", "qualification", "dob"]

    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already registered"}), 409

    try:
        dob = datetime.strptime(data["dob"], "%Y-%m-%d")

        new_user = User(
            email=data["email"],
            password=hash_password(data["password"]),
            full_name=data["full_name"],
            qualification=data["qualification"],
            dob=dob,
        )

        student_role = Role.query.filter_by(name="student").first()
        new_user.roles.append(student_role)

        db.session.add(new_user)
        db.session.commit()

        return jsonify(
            {
                "message": "Registration successful",
                "user": {"email": new_user.email, "full_name": new_user.full_name},
            }
        ), 201

    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Registration failed", "error": str(e)}), 500


@auth_bp.route("/logout", methods=["POST"])
@auth_required()
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
@auth_required("token")
def get_profile():
    from flask_security import current_user

    return jsonify(
        {
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "qualification": current_user.qualification,
                "dob": current_user.dob.strftime("%Y-%m-%d"),
                "roles": [role.name for role in current_user.roles],
            }
        }
    ), 200
