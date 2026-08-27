# Resume Parser

Extracts contact info, skills, and sections from a PDF or `.txt` resume. spaCy for NER, PyMuPDF for PDF text, Streamlit for the UI. Runs entirely offline.

## Run

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
```

The app also downloads the spaCy model on first launch if it isn't installed.

## What it extracts

- Name (from spaCy `PERSON` entities, with a header-line fallback)
- Emails, phone numbers, URLs (LinkedIn, GitHub, …)
- Organizations mentioned
- Skills matched against a built-in vocabulary
- Text of each recognized section (Summary, Experience, Education, Skills, Projects, …)
