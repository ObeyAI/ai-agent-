# app/views/dashboard.py
from flask import Blueprint, render_template, jsonify
from app.services.memory import get_all_calls
from app.dialer.manager import start_dialer_thread

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates")

@dashboard_bp.route("/")
def dashboard():
    return render_template("dashboard.html")

@dashboard_bp.route("/status")
def status():
    return jsonify(get_all_calls())

@dashboard_bp.route("/start", methods=["POST"])
def start():
    ok = start_dialer_thread()
    return jsonify({"started": ok})
