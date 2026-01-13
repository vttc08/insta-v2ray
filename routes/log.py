from flask import Blueprint, render_template, jsonify
from configuration import api_password
from .auth import login_required

log_bp = Blueprint("logs", __name__, url_prefix=f"/{api_password}/logs")

@log_bp.route('/')
@login_required
def get_logs_file():
    with open("app.log", "r") as logfile:
        content = logfile.readlines()
    return render_template("logs.html", logs = content[-100:], api_path=api_password)

@log_bp.route("/all")
@login_required
def get_all_logs():
    with open("app.log", "r") as logfile:
        content = logfile.readlines()
    return jsonify(content[-250:])