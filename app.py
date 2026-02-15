from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from urllib.parse import quote_plus
from flask_mail import Mail, Message
from datetime import datetime
from bson import ObjectId
import pyotp
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import os
import json
import time
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import pickle
import numpy as np



app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'y86761836@gmail.com'
app.config['MAIL_PASSWORD'] = 'hlgr qyvj jlpf nqhy'
app.config['MAIL_DEFAULT_SENDER'] = 'y86761836@gmail.com'

UPLOAD_FOLDER = "uploads_ocr"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

username = quote_plus("yrane4616")
password = quote_plus("y@S#rane46")
MONGO_URI = f"mongodb+srv://{username}:{password}@medicare.j9svm.mongodb.net/?retryWrites=true&w=majority&appName=MediCare"
client = MongoClient(MONGO_URI)


db = client['MediCare']
doctor = db['doctor_data']
patient_record = db['patient_record']
appointment_data = db['appointments']
otp_verify = db['verify_otp_email']
alerts = db['alerts']

mail = Mail(app)

with open(r'pickle\breast_cancer.pkl', 'rb') as f:
    breast_cancer_pipeline = pickle.load(f)

with open(r'pickle\heart_rf.pkl', 'rb') as f:
    heart_disease_pipeline = pickle.load(f)

with open(r'pickle\random_forest_pipeline.pkl', 'rb') as f:
    diabetes_pipeline = pickle.load(f)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/search_doctor', methods=['GET', 'POST'])
def search_doctor():
    return render_template('profile.html')

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    return render_template('book_appointment.html')

@app.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    if request.method == 'GET':
        return redirect(url_for('book_appointment'))
    doc_name = session.get('doc_name')
    if not doc_name:
        return redirect(url_for('login'))
    patient_name = request.form.get('name')
    patient_age = request.form.get('age')
    appointment_time = request.form.get('appointmentTime')
    disease = request.form.get('description')
    if not all([patient_name, patient_age, appointment_time, disease]):
        flash("Please fill all fields.", category='error')
        return render_template('book_appointment.html')
    existing_doc = appointment_data.find_one({"doctor_name": doc_name})
    if existing_doc:
        appointment_data.update_one(
            {"doctor_name": doc_name},
            {"$push": {"appointments": {
                "patient_name": patient_name,
                "disease": disease,
                "age": patient_age,
                "appointment_time": appointment_time
            }}}
        )
        flash("Appointment added successfully.", category='success')
    else:
        flash("Doctor session not found. Please log in again.", category='error')
    return render_template('book_appointment.html')


@app.route('/login_gen', methods=['POST'])
def login_gen():
    email = request.form.get('email')
    existing_user = doctor.find_one({"Email": email})

    if existing_user:
        secret_otp = pyotp.random_base32()
        totp = pyotp.TOTP(secret_otp, digits=6, interval=120)
        otp = totp.now()

        msg = Message('OTP Verification', recipients=[email], body=f"Your OTP for login is: {otp}")
        mail.send(msg)

        otp_verify.update_one(
            {"email": email},
            {"$set": {"otp_secret": secret_otp, "otp_timestamp": datetime.utcnow()}},
            upsert=True
        )

        session['email'] = email  # Store email in session

        return jsonify({"success": True, "message": "OTP sent successfully."})
    else:
        return jsonify({"success": False, "message": "User not found. Check your email."})


@app.route('/verify_otp_login', methods=['POST', 'GET'])
def verify_otp_login():
    if request.method == 'POST':
        email = session.get('email')
        otp_input = request.form.get('otp')

        user_data = otp_verify.find_one({"email": email})

        if not user_data:
            flash("No OTP request found. Please login again.", category='error')
            return redirect(url_for('login'))

        secret_otp = user_data['otp_secret'] 
        totp = pyotp.TOTP(secret_otp, digits=6, interval=120)

        
        if totp.verify(otp_input):
            doc_info = doctor.find_one({"Email": email})
            flash("OTP Verified Successfully!", category='success')
            session.pop('email',None)
            session['doc_name'] = doc_info['Name']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid OTP. Please try again.", category='error')
            return redirect(url_for('login'))

def serialize_doc(doc):
    """Convert ObjectId fields to string."""
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    elif isinstance(doc, dict):
        return {k: (str(v) if isinstance(v, ObjectId) else v) for k, v in doc.items()}
    return doc

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    doc_name = session.get('doc_name')
    if doc_name is None:
        return redirect(url_for('login'))
    return render_template('dashboard.html', doc_name=doc_name)

@app.route('/api/patient_alerts', methods=['GET'])
def alert_api():
    doc_name = session.get('doc_name')
    doc_alerts = alerts.find_one({'Doctor Name': doc_name})
    if doc_alerts:
        return jsonify(serialize_doc(doc_alerts))
    return jsonify({"alerts": []})

@app.route('/api/upcoming_appointments', methods=['GET'])
def appointment():
    doc_name = session.get('doc_name')
    doc_appointments = appointment_data.find_one({'doctor_name': doc_name})
    if doc_appointments:
        return jsonify(serialize_doc(doc_appointments))
    return jsonify({"appointments": []})

@app.route('/health_pred')
def health_pred():
    return render_template('health_pred.html')

@app.route('/ocr')
def ocr():
    return render_template('ocr.html')





#OCR Summarization
# Azure OCR Setup
AZURE_SUBSCRIPTION_KEY = "DyGSY4M79hwG0BNmlJYAFNbxS8tM0hCqeJO8h7bMCTUJ3ACOYFrfJQQJ99BEACGhslBXJ3w3AAAFACOGvIeF"
AZURE_ENDPOINT = "https://mediassit404.cognitiveservices.azure.com/"
client = ComputerVisionClient(AZURE_ENDPOINT, CognitiveServicesCredentials(AZURE_SUBSCRIPTION_KEY))

# Google Gemini AI Setup
os.environ["GOOGLE_API_KEY"] = "AIzaSyAgbm7-9iP4Z_CODVJf6xEeLS8fH-btDr4"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 100,
    "response_schema": content.Schema(
        type=content.Type.OBJECT,
        required=["Disease", "Causes"],
        properties={
            "Disease": content.Schema(type=content.Type.STRING),
            "Causes": content.Schema(type=content.Type.STRING),
            "Possible Remedies": content.Schema(type=content.Type.STRING),
        },
    ),
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)


def analyze_cbc_report(cbc_text):
    prompt = f"""
    You are a medical AI assistant. Analyze the given CBC report, summarize key findings, and predict possible diseases based on abnormalities.

    *CBC Report:*  
    {cbc_text}

    *Your tasks:*
    - Extract key blood parameters and values.
    - Identify abnormal values and possible implications.
    - Summarize findings concisely.
    - Predict potential diseases based on deviations.
    - Highlight key points in the report.

    *Output Format:*
    - Summary of CBC report in one word.
    - Possible conditions based on abnormalities.
    - Important highlights.

    Provide a structured response.
    """
    
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(prompt)
    
    return response.text


@app.route("/upload/ocr", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Save file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Run OCR
    with open(file_path, "rb") as image_file:
        response = client.read_in_stream(image_file, raw=True)

    operation_location = response.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]

    while True:
        result = client.get_read_result(operation_id)
        if result.status not in ["notStarted", "running"]:
            break
        time.sleep(1)

    extracted_ocr = ""
    if result.status == OperationStatusCodes.succeeded:
        for page in result.analyze_result.read_results:
            for line in page.lines:
                extracted_ocr += line.text + "\n"
    else:
        return jsonify({"error": "OCR Failed"}), 500

    # Run AI Analysis
    cbc_analysis_result = analyze_cbc_report(extracted_ocr)

    # Ensure the response is structured properly
    # try:
    #     analysis_data = eval(cbc_analysis_result)  # Convert string to dict if needed
    # except:
    #     return jsonify({"error": "Invalid AI response format"}), 500

    try:
        if isinstance(cbc_analysis_result, str):
            cbc_analysis_result = json.loads(cbc_analysis_result)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid AI response format"}), 500
    result = {
        "Abnormal Values": cbc_analysis_result.get("Causes", "N/A"),
        "Possible Disease": cbc_analysis_result.get("Disease", "N/A"),
        "Remedies": cbc_analysis_result.get("Possible Remedies", "N/A"),
    }

    return jsonify(result)



@app.route('/predict_diabetes', methods=['POST'])
def predict_diabetes():
    try:
        data = request.json
        features = [
            1 if data['gender'] == "Male" else 0,
            int(data['age']),
            int(data['hypertension']),
            int(data['heart_disease']),
            {"never": 0, "former": 1, "current": 2}[data['smoking_history']],
            float(data['bmi']),
            float(data['hba1c']),
            int(data['glucose'])
        ]
        prediction = diabetes_pipeline.predict([features])[0]
        return jsonify({'prediction': int(prediction)})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/predict_cancer', methods=['POST'])
def predict_cancer():
    try:
        data = request.json
        features = [float(data[key]) for key in data]  # Assuming all inputs are numeric
        prediction = breast_cancer_pipeline.predict([features])[0]
        return jsonify({'prediction': int(prediction)})
    except Exception as e:
        return jsonify({'error': str(e)})


os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/patient_search')
def patient_search_page():
    if session.get('doc_name') is None:
        return redirect(url_for('login'))
    return render_template('patient_search.html')

@app.route('/api/patient_search', methods=['GET'])
def api_patient_search():
    if session.get('doc_name') is None:
        return jsonify({"error": "Unauthorized"}), 401
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({"patients": []})
    regex_pattern = f".*{q}.*"
    cursor = patient_record.find({"Name": {"$regex": regex_pattern, "$options": "i"}}).limit(50)
    patients = [serialize_doc(doc) for doc in cursor]
    return jsonify({"patients": patients})

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip()
        if not search_query:
            return redirect(url_for('dashboard'))
        regex_pattern = f".*^{search_query}.*"
        search_result = list(patient_record.find({"Name": {"$regex": regex_pattern, "$options": "i"}}))
        return render_template('search_result.html', user=search_result)
    return redirect(url_for('dashboard'))


@app.route('/profile')
def profile():
    if session.get('doc_name') is None:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop("doc_name", None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
