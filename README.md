# MediAssist - Healthcare Management System

![MediAssist Banner](static/images/Banner.png)

**MediAssist** is a healthcare management web application for doctors and staff: OTP-based login, dashboard with appointments and alerts, patient search, OCR blood report summarization, health prediction (diabetes, cancer), and appointment booking. Optional chatbot services use Groq or Gemini + PubMed.

---

## Overview

- **Doctor login** – Email OTP via Flask-Mail; session-based auth
- **Dashboard** – Upcoming appointments and patient alerts (MongoDB), links to OCR, Patient Search, Medical Prediction
- **Patient search** – Search by name (dashboard search bar → results page; or dedicated Patient Search page with live API)
- **OCR** – Upload blood report image → Azure OCR + Gemini analysis → summary (abnormal values, possible disease, remedies)
- **Health prediction** – Diabetes and breast cancer prediction via Flask APIs; UI also references external services (e.g. fracture/brain-tumor on other ports) and mock flows
- **Appointments** – Book-appointment form posts to `/add_appointment`; dashboard shows upcoming appointments from MongoDB
- **Optional services** – FastAPI medical chatbot (Groq) and CLI medical-academics bot (Gemini + PubMed)

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
│   ├── login.html            # OTP login
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
│   ├── chatbot.py            # FastAPI medical chatbot (Groq API)
│   ├── advance_chatbot.py    # CLI: Gemini + PubMed
│   └── README.md
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
| `GET/POST /login` | Login page |
| `POST /login_gen` | Send OTP |
| `POST/GET /verify_otp_login` | Verify OTP → dashboard |
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

- **MongoDB** – App uses a MongoDB Atlas connection (see `app.py`). Ensure the DB has collections used by the app (e.g. doctor_data, patient_record, appointments, verify_otp_email, alerts) or adjust the connection string.
- **Pickle models** – Ensure `pickle/` contains `breast_cancer.pkl`, `heart_rf.pkl`, `random_forest_pipeline.pkl` (used by prediction routes).
- **Azure OCR + Gemini** – OCR flow uses Azure Computer Vision and Google Gemini (keys in `app.py`). Replace with your own keys or env vars if needed.

Run the main app:

```sh
python app.py
```

Open **http://127.0.0.1:5000** (or the port shown in the console). Use **Login** → enter doctor email → OTP → **Dashboard**. From there you can use Patient Search, OCR, Medical Prediction, and Appointments.

### 3. Optional: OCR-only module (`models/OCR`)

To run only the OCR/front-end module (no MongoDB/auth):

```sh
cd models/OCR
python app.py
```

Runs on **http://127.0.0.1:5001** with local templates and static files.

### 4. Optional: FastAPI medical chatbot (Groq)

- Get an API key from [console.groq.com](https://console.groq.com).
- Set `GROQ_API_KEY` in your environment.
- From **project root**:

```sh
pip install langchain-groq
uvicorn services.chatbot:app --host 0.0.0.0 --port 8000 --reload
```

The main app’s script.js can call `http://127.0.0.1:8000/chat` for the chatbot if you keep that integration.

### 5. Optional: CLI medical-academics chatbot (Gemini + PubMed)

- Set `GEMINI_API_KEY` in `.env`.
- From project root:

```sh
python services/advance_chatbot.py
```

---

## Environment / Configuration

- **Flask** – `app.py`: MongoDB URI, Flask-Mail credentials, Azure OCR key, Gemini API key. Move secrets to env vars in production.
- **Chatbot (Groq)** – `GROQ_API_KEY`.
- **Advance chatbot** – `GEMINI_API_KEY` in `.env`.

---

## Technologies

- **Frontend:** HTML, CSS, JavaScript, FontAwesome, Bootstrap (search result page).
- **Backend:** Flask (sessions, MongoDB, REST endpoints).
- **AI/ML:** Google Gemini (OCR summary, advance_chatbot), Azure Computer Vision (OCR), Scikit-Learn (diabetes, cancer, heart pipelines), optional Groq (FastAPI chatbot).
- **Data:** MongoDB (doctors, patients, appointments, OTP, alerts).
- **Optional:** FastAPI, LangChain (Groq), PubMed API.

---

## Contributing

- Fork the repository and submit a **pull request** with your improvements.
- **Bug reports and feature requests** are welcome via GitHub Issues.
