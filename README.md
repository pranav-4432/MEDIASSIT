# MediAssist - Healthcare Management System

**MediAssist** is a healthcare management web application for doctors and staff: JWT login (email + password), dashboard with appointments and alerts, patient search, OCR blood report extraction, health prediction (diabetes, cancer), and appointment booking. Optional chatbot uses Groq.

---

## Overview

- **Doctor login** – Email + password; JWT stored in httpOnly cookie; no email/OTP
- **Dashboard** – Upcoming appointments and patient alerts (MongoDB), links to OCR, Patient Search, Medical Prediction
- **Patient search** – Search by name (dashboard search bar → results page; or dedicated Patient Search page with live API)
- **OCR** – Upload blood report image → Tesseract (free) text extraction → raw text returned
- **Health prediction** – Diabetes and breast cancer prediction via Flask APIs; UI also references external services (e.g. fracture/brain-tumor on other ports) and mock flows
- **Appointments** – Book-appointment form posts to `/add_appointment`; dashboard shows upcoming appointments from MongoDB
- **Medical chatbot** – Chat button on homepage; Groq-powered (set GROQ_API_KEY). Patient lookup: type "patient &lt;name&gt;".

---

## File Structure

```
📂 MediAssist
├── app.py                    # Main Flask app (run this for the full application)
├── requirements.txt
├── README.md
│
├── 📂 templates              # Jinja2 templates (all pages use url_for for links)
│   ├── index.html            # Landing: Search Doctors, Book Now
│   ├── login.html            # Login (email + password, JWT)
│   ├── appointments.html     # Available doctors → Book Appointment
│   ├── book_appointment.html # Booking form → /add_appointment
│   ├── dashboard.html        # Doctor dashboard (search, OCR, appointments, alerts)
│   ├── health_pred.html      # Health prediction UI
│   ├── ocr.html              # Blood report upload & analysis
│   ├── profile.html          # Doctor profile / Search Doctors
│   ├── patient_search.html   # Patient search page (API-backed)
│   └── search_result.html    # Patient search results (from dashboard search)
│
├── 📂 static
│   ├── css/                  # style, login, dashboard, ocr, health_pred, etc.
│   ├── js/                   # script, login, dashboard, ocr, health_pred, patient_search, etc.
│   └── images/               # Banner.png, home_gif.gif
│
├── 📂 services               # Optional; not required for main app
│   └── README.md              # (Chatbot is in main app: /api/chat)
│
├── 📂 models
│   ├── 📂 OCR                # Standalone copy of templates + static + minimal Flask app
│   │   ├── app.py            # Optional: run on port 5001 for OCR-only UI
│   │   ├── templates/
│   │   └── static/
│   └── ...                   # ML notebooks & data (e.g. heart, breast cancer)
│
├── 📂 pickle                 # ML pipelines (breast_cancer, heart_rf, random_forest_pipeline)
└── uploads_ocr/              # Created at runtime for OCR uploads
```

---

## Main App Routes (Flask – `app.py`)

| Route | Description |
|-------|-------------|
| `GET /` | Landing (index) |
| `GET /signup` | Sign-up form (name, email, password) |
| `POST /signup` | Create account → redirect to login |
| `GET /login` | Login form (email + password) |
| `POST /login` | Submit credentials → JWT cookie + redirect to dashboard |
| `GET /search_doctor` | Doctor profile / search doctors |
| `GET /book_appointment` | Booking form |
| `POST /add_appointment` | Submit booking (requires session) |
| `GET /dashboard` | Doctor dashboard (requires session) |
| `GET /patient_search` | Patient search page (requires session) |
| `GET /api/patient_search?q=` | Patient search API (JSON) |
| `POST /search` | Dashboard search → search_result page |
| `GET /profile` | Redirects to dashboard |
| `GET /logout` | Clear session → login |
| `GET /health_pred` | Health prediction page |
| `GET /ocr` | OCR upload page |
| `POST /upload/ocr` | OCR analysis API |
| `POST /predict_diabetes` | Diabetes prediction API |
| `POST /predict_cancer` | Breast cancer prediction API |
| `GET /api/upcoming_appointments` | Dashboard appointments (JSON) |
| `GET /api/patient_alerts` | Dashboard alerts (JSON) |
| `POST /api/chat` | Medical chatbot (JSON: `question`, `context` → `answer`, `updated_context`) |

All template links use `url_for(...)` so routes stay consistent.

---

## Installation & Run

### 1. Clone and install

```sh
git clone https://github.com/Git-Rexdev/Techathon-Error404.git
cd Techathon-Error404
pip install -r requirements.txt
```

### 2. Main application

- **MongoDB** – App uses a MongoDB Atlas connection (see `app.py`). Ensure the DB has collections used by the app (e.g. doctor_data, patient_record, appointments, alerts). Doctors need `Email`, `Name`; optional `password_hash` for JWT login. or adjust the connection string.
- **Pickle models** – Ensure `pickle/` contains `breast_cancer.pkl`, `heart_rf.pkl`, `random_forest_pipeline.pkl` (used by prediction routes).
- **OCR** – Uses **Tesseract** (free, open-source). Install the Tesseract engine: [Windows](https://github.com/UB-Mannheim/tesseract/wiki), then `pip install pytesseract Pillow`. No API keys needed.

Run the main app:

```sh
python app.py
```

Open **http://127.0.0.1:5000** (or the port shown in the console). Use **Login** with a doctor email and password → **Dashboard**. From there you can use Patient Search, OCR, Medical Prediction, and Appointments. First time a doctor logs in, their password is stored (hashed) in MongoDB.

### 3. Optional: OCR-only module (`models/OCR`)

To run only the OCR/front-end module (no MongoDB/auth):

```sh
cd models/OCR
python app.py
```

Runs on **http://127.0.0.1:5001** with local templates and static files.

### 4. Optional: Medical chatbot (Groq)

The chatbot is built into the Flask app. On the homepage, click **Chat** to open the assistant.

- Get a free API key at [console.groq.com](https://console.groq.com).
- Set `GROQ_API_KEY` in your environment and run the main app. No separate server needed.
- Install: `pip install langchain-groq` (included in requirements).
- Type **"patient &lt;name&gt;"** to look up a patient from MongoDB.

---

## Environment / Configuration

- **Flask** – `app.py`: MongoDB URI, `SECRET_KEY` for JWT. Move secrets to env vars in production.
- **Chatbot (Groq)** – `GROQ_API_KEY` (optional).

---

## Technologies

- **Frontend:** HTML, CSS, JavaScript, FontAwesome, Bootstrap (search result page).
- **Backend:** Flask (sessions, MongoDB, REST endpoints).
- **AI/ML:** Tesseract OCR (free), Scikit-Learn (diabetes, cancer, heart), Groq + LangChain (medical chatbot in Flask).
- **Data:** MongoDB (doctors, patients, appointments, alerts). Auth: JWT in cookie, password hash in doctor document.

---

## Contributing

- Fork the repository and submit a **pull request** with your improvements.
- **Bug reports and feature requests** are welcome via GitHub Issues.
