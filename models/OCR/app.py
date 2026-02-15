"""
Standalone Flask app for the OCR / models module.
Uses local templates and static under models/OCR.
Run from project root: python -m models.OCR.app
Or from this directory: flask --app app run
"""
import os

from flask import Flask, render_template

# Run from repo root or from models/OCR
BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE, "templates"),
    static_folder=os.path.join(BASE, "static"),
    static_url_path="/static",
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/appointments")
def appointments():
    return render_template("appointments.html")

@app.route("/book_appointment")
def book_appointment():
    return render_template("book_appointment.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", doc_name="Doctor")

@app.route("/health_pred")
def health_pred():
    return render_template("health_pred.html")

@app.route("/ocr")
def ocr():
    return render_template("ocr.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/patient_search")
def patient_search():
    return render_template("patient_search.html")

@app.route("/search_result")
def search_result():
    return render_template("search_result.html", user=[])


if __name__ == "__main__":
    app.run(debug=True, port=5001)
