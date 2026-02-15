import google.generativeai as genai
from dotenv import load_dotenv
import os
import requests

# Load API Key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

PUBMED_API_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# Initialize Gemini model
model = genai.GenerativeModel("gemini-pro")

def is_medical_academics_question(user_message: str) -> bool:
    """Determines if the query is related to medical academics."""
    prompt = (
        "You are an AI that determines if a question is related to medical academics. "
        "Medical academics include anatomy, diseases, physiology, medical research, and treatments. "
        "Respond with only 'Yes' or 'No'.\n\n"
        f"Query: {user_message}"
    )
    
    response = model.generate_content(prompt)
    classification = response.text.strip().lower()
    return classification == "yes"

def fetch_pubmed_references(query: str, max_references: int = 3) -> list[str]:
    """Fetches references from PubMed."""
    params = {"db": "pubmed", "term": query, "retmax": max_references, "retmode": "json"}
    response = requests.get(f"{PUBMED_API_BASE}esearch.fcgi", params=params)

    if response.status_code != 200:
        return []

    article_ids = response.json().get("esearchresult", {}).get("idlist", [])
    references: list[str] = []

    for article_id in article_ids:
        details_response = requests.get(
            f"{PUBMED_API_BASE}esummary.fcgi",
            params={"db": "pubmed", "id": article_id, "retmode": "json"},
        )
        if details_response.status_code == 200:
            details = details_response.json().get("result", {}).get(article_id, {})
            title = details.get("title", "No title available")
            link = f"https://pubmed.ncbi.nlm.nih.gov/{article_id}"
            references.append(f"{title} - [Read more]({link})")

    return references

def generate_response(user_message: str) -> str:
    """Generates an AI response after moderation and medical check."""

    # Step 1: Moderation Check
    moderation_prompt = (
        "You are a content moderator AI. "
        "Determine if the following message contains inappropriate or harmful content. "
        "Answer only 'Yes' or 'No'.\n\n"
        f"Message: {user_message}"
    )
    
    moderation_response = model.generate_content(moderation_prompt)

    if moderation_response.text.strip().lower() == "yes":
        return "Sorry, your message contains inappropriate content and cannot be processed."

    # Step 2: Medical Question Classification
    if not is_medical_academics_question(user_message):
        return "Sorry, I can only provide answers related to medical students' academics. Please ask a relevant question."

    # Step 3: Generate Medical Response
    medical_prompt = (
        "You are a medical student assistant. "
        "Answer only questions related to medical academics, such as anatomy, diseases, treatments, and medical research. "
        "Keep responses concise within 80 tokens.\n\n"
        f"User Question: {user_message}"
    )
    
    response = model.generate_content(medical_prompt)
    answer = response.text.strip()

    # Step 4: Fetch PubMed References
    references = fetch_pubmed_references(user_message)
    if references:
        answer += "\n\n*References:*\n" + "\n".join(references)

    return answer

# Example Usage:
if __name__ == "__main__":
    user_input = input("Ask a medical-related question: ")
    print(generate_response(user_input))
