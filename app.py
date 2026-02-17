import os
from datetime import datetime, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from pymongo import MongoClient
from pymongo.errors import ConfigurationError as MongoConfigurationError
from urllib.parse import quote_plus
from bson import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import re
import pickle
import numpy as np
# Optional: medical chatbot (Groq). Set GROQ_API_KEY to enable.
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    _groq_key = os.environ.get("GROQ_API_KEY")
    _chat_llm = ChatGroq(api_key=_groq_key, model_name="llama-3.1-8b-instant", temperature=0.3) if _groq_key else None
    _chat_prompt = ChatPromptTemplate.from_template(
        "You are a helpful medical assistant. Answer the medical question below concisely and accurately.\n\n"
        "Conversation history: {context}\n\nQuestion: {question}\n\nAnswer: "
    )
    _chat_chain = (_chat_prompt | _chat_llm | StrOutputParser()) if _chat_llm else None
except Exception:
    _chat_llm = None
    _chat_chain = None

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mysecretkey')
app.config['JWT_COOKIE_NAME'] = 'auth_token'
app.config['JWT_EXPIRY_HOURS'] = 24

UPLOAD_FOLDER = "uploads_ocr"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MongoDB: set MONGO_URI in .env (see .env.example). Leave unset to use default (may not resolve).
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    _user = quote_plus("yrane4616")
    _pass = quote_plus("y@S#rane46")
    MONGO_URI = f"mongodb+srv://{_user}:{_pass}@medicare.j9svm.mongodb.net/?retryWrites=true&w=majority&appName=MediCare"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    client.admin.command("ping")  # force connection attempt
    db = client["MediCare"]
    doctor = db["doctor_data"]
    patient_record = db["patient_record"]
    appointment_data = db["appointments"]
    alerts = db["alerts"]
except (MongoConfigurationError, Exception) as e:
    print("\n*** MongoDB connection failed ***")
    print("Set MONGO_URI in your .env file to your MongoDB Atlas connection string.")
    print("Example: MONGO_URI=mongodb+srv://USER:PASSWORD@YOUR-CLUSTER.mongodb.net/?retryWrites=true&w=majority")
    print("Error:", str(e))
    raise SystemExit(1) from e

with open(r'pickle\breast_cancer.pkl', 'rb') as f:
    breast_cancer_pipeline = pickle.load(f)

with open(r'pickle\heart_rf.pkl', 'rb') as f:
    heart_disease_pipeline = pickle.load(f)

with open(r'pickle\random_forest_pipeline.pkl', 'rb') as f:
    diabetes_pipeline = pickle.load(f)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

def _create_token(email: str, doc_name: str) -> str:
    payload = {
        'sub': email,
        'doc_name': doc_name,
        'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRY_HOURS']),
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def _load_user_from_token():
    if session.get('doc_name'):
        return
    token = request.cookies.get(app.config['JWT_COOKIE_NAME'])
    if not token:
        return
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        session['doc_name'] = payload.get('doc_name')
    except jwt.ExpiredSignatureError:
        pass
    except jwt.InvalidTokenError:
        pass


@app.before_request
def before_request():
    _load_user_from_token()


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    name = (request.form.get('name') or '').strip()
    email = (request.form.get('email') or '').strip().lower()
    password = request.form.get('password') or ''
    password_confirm = request.form.get('password_confirm') or ''
    if not name or not email or not password:
        flash('Name, email and password are required.', 'error')
        return redirect(url_for('signup'))
    if len(password) < 6:
        flash('Password must be at least 6 characters.', 'error')
        return redirect(url_for('signup'))
    if password != password_confirm:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('signup'))
    if doctor.find_one({'Email': email}):
        flash('An account with this email already exists. Log in instead.', 'error')
        return redirect(url_for('signup'))
    doctor.insert_one({
        'Name': name,
        'Email': email,
        'password_hash': generate_password_hash(password),
    })
    flash('Account created. You can now log in.', 'success')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    email = (request.form.get('email') or '').strip().lower()
    password = request.form.get('password') or ''
    if not email or not password:
        flash('Email and password are required.', 'error')
        return redirect(url_for('login'))
    doc = doctor.find_one({'Email': email})
    if not doc:
        flash('Invalid email or password.', 'error')
        return redirect(url_for('login'))
    password_hash = doc.get('password_hash')
    if password_hash:
        if not check_password_hash(password_hash, password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))
    else:
        doctor.update_one(
            {'Email': email},
            {'$set': {'password_hash': generate_password_hash(password)}}
        )
    doc_name = doc.get('Name', email)
    token = _create_token(email, doc_name)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    session['doc_name'] = doc_name
    resp = make_response(redirect(url_for('dashboard')))
    resp.set_cookie(
        app.config['JWT_COOKIE_NAME'],
        token,
        max_age=app.config['JWT_EXPIRY_HOURS'] * 3600,
        httponly=True,
        samesite='Lax',
    )
    flash('Logged in successfully.', 'success')
    return resp


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





# OCR: Tesseract (free, open-source). Install: https://github.com/UB-Mannheim/tesseract/wiki
try:
    import pytesseract
    from PIL import Image
    _ocr_available = True
except ImportError:
    _ocr_available = False


def _run_ocr(image_path: str) -> str:
    if not _ocr_available:
        return ""
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)


@app.route("/upload/ocr", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    if not _ocr_available:
        return jsonify({"error": "OCR not available. Install: pip install pytesseract Pillow, and install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki"}), 503

    try:
        extracted_ocr = _run_ocr(file_path)
    except Exception as e:
        return jsonify({"error": f"OCR failed: {str(e)}. Ensure Tesseract is installed on your system."}), 500

    text = extracted_ocr.strip() if extracted_ocr else "No text extracted."
    return jsonify({
        "Abnormal Values": "N/A",
        "Possible Disease": text,
        "Remedies": "N/A",
    })



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
    session.pop('doc_name', None)
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie(app.config['JWT_COOKIE_NAME'], '', max_age=0)
    return resp


# ---- Medical chatbot (integrated) ----
def _is_medical_question(question: str) -> bool:
    keywords = (
        "doctor physician surgeon specialist nurse healthcare hospital clinic pharmacy patient "
        "appointment prescription consultation check-up symptoms diagnosis disease infection fever allergy "
        "chronic cancer diabetes hypertension arthritis asthma stroke flu COVID pneumonia migraine "
        "brain heart lungs liver kidney stomach intestines pancreas spleen bladder prostate thyroid "
        "cold cough fever sinusitis bronchitis tonsillitis UTI diarrhea constipation acid reflux GERD IBS "
        "heart failure coronary artery disease arrhythmia COPD emphysema sleep apnea parkinson alzheimer "
        "headache nausea vomiting dizziness fatigue weakness shortness of breath chest pain abdominal pain "
        "blood test MRI X-ray CT scan ultrasound endoscopy biopsy ECG EEG mammography "
        "cardiology dermatology endocrinology gastroenterology neurology oncology pediatrics psychiatry "
        "medication vaccination therapy surgery"
    )
    q = question.lower()
    return any(kw in q for kw in keywords.split())


def _chat_patient_lookup(name: str):  # from MongoDB
    if not name or not name.strip():
        return None
    pattern = re.escape(name.strip())
    doc = patient_record.find_one({"Name": {"$regex": f"^{pattern}$", "$options": "i"}})
    if not doc:
        return None
    return {k: (str(v) if isinstance(v, ObjectId) else v) for k, v in doc.items()}


@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json(force=True, silent=True) or {}
    question = (data.get('question') or '').strip()
    context = data.get('context') or ''
    if not question:
        return jsonify({"answer": "Please enter a question.", "updated_context": context})

    # "patient <name>" lookup from MongoDB
    match = re.search(r"patient\s+(.+)", question, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        patient = _chat_patient_lookup(name)
        if patient:
            lines = [f"{k}: {v}" for k, v in patient.items()]
            answer = "Patient details:\n" + "\n".join(lines)
            return jsonify({"answer": answer, "updated_context": context})
        return jsonify({"answer": "Patient not found.", "updated_context": context})

    if not _chat_chain:
        return jsonify({
            "answer": "Chatbot is not configured. Set GROQ_API_KEY in your environment and install: pip install langchain-groq",
            "updated_context": context,
        })

    if _is_medical_question(question):
        result = _chat_chain.invoke({"context": context, "question": question})
    else:
        result = "I'm here to assist with medical-related queries only."

    new_context = f"{context}\nUser: {question}\nAssistant: {result}"
    return jsonify({"answer": result, "updated_context": new_context})


if __name__ == '__main__':
    app.run(debug=True)
