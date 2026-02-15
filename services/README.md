# Optional services (not part of main Flask app)

These are **standalone** tools and are not linked to the main MedAssist Flask app (`app.py`).

- **chatbot.py** – FastAPI medical Q&A + patient lookup using **Groq API**. Set `GROQ_API_KEY` in your environment, then: `pip install langchain-groq` and run from project root: `uvicorn services.chatbot:app --reload`
- **advance_chatbot.py** – CLI script using Gemini + PubMed for medical academics. Run with: `python advance_chatbot.py`

Run them from the project root so paths like `sheets/patients.csv` resolve correctly, or adjust paths inside each file.
