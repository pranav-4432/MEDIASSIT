import os
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

# Use Groq API (set GROQ_API_KEY in env). Fallback: groq package direct call if langchain-groq not installed.
try:
    from langchain_groq import ChatGroq
    _groq_api_key = os.getenv("GROQ_API_KEY")
    if not _groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is required for the chatbot.")
    _llm = ChatGroq(api_key=_groq_api_key, model_name="llama-3.1-8b-instant", temperature=0.3)
except Exception as e:
    _llm = None
    _groq_error = str(e)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

template = """
You are a helpful medical assistant. Answer the medical question below concisely and accurately.

Conversation history: {context}

Question: {question}

Answer: 
"""

prompt = ChatPromptTemplate.from_template(template)
chain = (prompt | _llm | StrOutputParser()) if _llm else None

def is_medical_question(question):
    medical_keywords = [
    "doctor", "physician", "surgeon", "specialist", "nurse", "healthcare", "hospital", "clinic",
    "pharmacy", "patient", "appointment", "prescription", "consultation", "check-up", "symptoms",
    "diagnosis", "disease", "infection", "fever", "allergy", "chronic", "cancer", "diabetes",
    "hypertension", "arthritis", "asthma", "stroke", "flu", "COVID", "pneumonia", "migraine",
    "depression", "anxiety", "obesity", "epilepsy", "surgery", "therapy", "medication", "vaccination",
    "preventive care", "emergency", "urgent care", "triage", "ICU", "intensive care", "ventilator",
    "defibrillator", "resuscitation", "transplant", "donor", "recipient", "immunization", 
    "screening", "mental health", "substance abuse", "addiction", "detoxification", "withdrawal",
    
    "brain", "heart", "lungs", "liver", "kidney", "stomach", "intestines", "pancreas",
    "spleen", "bladder", "prostate", "thyroid", "adrenal glands", "blood", "bones",
    "muscles", "nerves", "skin", "veins", "arteries", "lymph nodes", "joints",
    "spinal cord", "esophagus", "trachea", "diaphragm", "pelvis", "gallbladder",
    
    "cold", "cough", "fever", "sinusitis", "bronchitis", "tonsillitis", "conjunctivitis",
    "gastroenteritis", "UTI", "diarrhea", "constipation", "acid reflux", "GERD", "IBS",
    "hemorrhoids", "psoriasis", "eczema", "dermatitis", "acne", "rosacea", "ringworm",
    "athlete's foot", "herpes", "chickenpox", "measles", "mumps", "rubella", "malaria",
    "dengue", "chikungunya", "typhoid", "tuberculosis", "hepatitis", "HIV", "AIDS", 
    "syphilis", "gonorrhea", "HPV", "lyme disease", "MRSA", "ebola", "zika virus",
    "hantavirus", "leptospirosis", "tetanus", "whooping cough", "polio", "rabies", "COVID-19",
    
    "heart failure", "coronary artery disease", "arrhythmia", "atherosclerosis",
    "cardiomyopathy", "atrial fibrillation", "myocardial infarction", "pulmonary embolism",
    "COPD", "emphysema", "sleep apnea", "pulmonary fibrosis", "parkinson's disease",
    "alzheimer's", "multiple sclerosis", "ALS", "meningitis", "encephalitis",
    "bell's palsy", "schizophrenia", "bipolar disorder", "cushing's syndrome",
    "addison's disease", "hyperthyroidism", "hypothyroidism", "hashimoto's thyroiditis",
    "PCOS", "cirrhosis", "crohn's disease", "ulcerative colitis", "pancreatitis",
    "gallstones", "lupus", "rheumatoid arthritis", "scleroderma", "sjögren's syndrome",
    "myasthenia gravis", "leukemia", "lymphoma", "melanoma", "sarcoma", "brain tumor",
    "breast cancer", "prostate cancer", "colorectal cancer", "ovarian cancer",
    "pancreatic cancer", "thyroid cancer",
    
    "headache", "nausea", "vomiting", "dizziness", "fatigue", "weakness", "shortness of breath",
    "chest pain", "abdominal pain", "back pain", "joint pain", "swelling", "inflammation",
    "redness", "itching", "rash", "sore throat", "cough", "runny nose", "nasal congestion",
    "loss of taste", "loss of smell", "blurred vision", "double vision", "ear pain", "tinnitus",
    "hearing loss", "palpitations", "fainting", "seizures", "numbness", "tingling", "diarrhea",
    "constipation", "bloody stool", "dark urine", "frequent urination", "painful urination",
    "insomnia", "night sweats", "weight loss", "weight gain",
    
    "acetaminophen", "ibuprofen", "aspirin", "naproxen", "amoxicillin", "azithromycin",
    "ciprofloxacin", "doxycycline", "metronidazole", "clindamycin", "vancomycin",
    "oseltamivir", "acyclovir", "remdesivir", "ritonavir", "zanamivir", "fluconazole",
    "clotrimazole", "ketoconazole", "amphotericin B", "diphenhydramine", "loratadine",
    "cetirizine", "fexofenadine", "dextromethorphan", "guaifenesin", "phenylephrine",
    "pseudoephedrine", "atorvastatin", "rosuvastatin", "amlodipine", "metoprolol",
    "lisinopril", "losartan", "clopidogrel", "warfarin", "digoxin", "nitroglycerin",
    "metformin", "insulin", "glipizide", "pioglitazone", "dapagliflozin", "liraglutide",
    "albuterol", "salmeterol", "montelukast", "tiotropium", "budesonide", "fluticasone",
    "diazepam", "alprazolam", "fluoxetine", "sertraline", "duloxetine", "gabapentin",
    "pregabalin", "omeprazole", "ranitidine", "esomeprazole", "famotidine", "sucralfate",
    "methotrexate", "doxorubicin", "cisplatin", "paclitaxel", "bevacizumab", "imatinib",
    
    "blood test", "MRI", "X-ray", "CT scan", "ultrasound", "endoscopy", "colonoscopy",
    "biopsy", "ECG", "EEG", "mammography", "angiography", "bone scan", "DEXA scan",
    "allergy test", "genetic test", "lumbar puncture",
    
    "cardiology", "dermatology", "endocrinology", "gastroenterology", "hematology",
    "immunology", "neurology", "oncology", "ophthalmology", "orthopedics", "pediatrics",
    "psychiatry", "radiology", "urology", "gynecology", "obstetrics", "pathology",
    "pharmacology", "toxicology", "virology", "bacteriology", "genetics", "epidemiology",
    
    "acupuncture", "homeopathy", "chiropractic", "naturopathy", "herbal medicine",
    "massage therapy", "aromatherapy", "reflexology", "ayurveda", "yoga", "meditation",
    "reiki", "dietary supplements", "probiotics", "omega-3 fatty acids",
    
    "stem cell therapy", "gene therapy", "palliative care", "hospice care",
    "telemedicine", "e-health", "medical records", "health insurance"
]
    return any(re.search(rf"\b{kw}\b", question, re.IGNORECASE) for kw in medical_keywords)

def fetch_patient_details(patient_name):
    df = pd.read_csv("sheets/patients.csv")
    df["Name"] = df["Name"].str.strip().str.lower()  
    patient_name = patient_name.strip().lower()  

    patient_data = df[df["Name"] == patient_name] 

    if not patient_data.empty:
        return patient_data.to_dict(orient="records")[0]
    else:
        return None


class ChatRequest(BaseModel):
    question: str
    context: str = ""

class PatientSearchRequest(BaseModel):
    patient_name: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    patient_name_match = re.search(r"patient (.+)", request.question, re.IGNORECASE)
    if patient_name_match:
        patient_name = patient_name_match.group(1)
        patient_details = fetch_patient_details(patient_name)
        if patient_details:
            formatted_details = f"""
            ---
            Name          : {patient_details.get('Name', 'N/A')}
            Age           : {patient_details.get('Age', 'N/A')}
            Address       : {patient_details.get('Address', 'N/A')}
            BP Low        : {patient_details.get('BP Low', 'N/A')}
            BP High       : {patient_details.get('BP High', 'N/A')}
            Diabetic      : {patient_details.get('Diabetic', 'N/A')}
            Heart Rate    : {patient_details.get('Heart Rate', 'N/A')}
            Temperature   : {patient_details.get('Temperature', 'N/A')}
            Blood Group   : {patient_details.get('Blood Group', 'N/A')}
            Allergies     : {patient_details.get('Allergies', 'N/A')}
            Medications   : {patient_details.get('Medications', 'N/A')}
            Past Surgeries: {patient_details.get('Past Surgeries', 'N/A')}
            Notes         : {patient_details.get('Notes', 'N/A')}
            Admitted      : {patient_details.get('Admitted', 'N/A')}
            """
            return {"answer": formatted_details.strip(), "updated_context": request.context}
        else:
            return {"answer": "Patient not found.", "updated_context": request.context}
    
    if not _llm or chain is None:
        return {
            "answer": "Chatbot is not configured. Set GROQ_API_KEY and install: pip install langchain-groq",
            "updated_context": request.context,
        }

    if is_medical_question(request.question):
        result = chain.invoke({"context": request.context, "question": request.question})
    else:
        result = "I'm here to assist with medical-related queries only."

    return {"answer": result, "updated_context": f"{request.context}\nUser: {request.question}\nAI: {result}"}
