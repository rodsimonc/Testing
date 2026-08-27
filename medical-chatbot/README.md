# Medical Chatbot

**⚠️ Demo only. Not medical advice.** A symptom checker built on a tiny curated knowledge base, with strict guardrails for red-flag emergencies. The interesting part isn't the retrieval — it's the guardrails.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## What it does

- Takes free-text or checkbox symptoms
- Runs an **emergency check first** — chest pain, breathing difficulty, stroke signs, suicidal ideation, unconsciousness, severe bleeding, overdose, anaphylaxis → surfaces a "call emergency services" banner and stops
- Otherwise matches symptoms against a small condition knowledge base and returns the top 3 by overlap
- Every response is wrapped in a persistent disclaimer

## Layout

- `app.py` — Streamlit UI
- `knowledge.py` — condition → symptoms lookup
- `guardrails.py` — emergency patterns + disclaimer

Real medical LLM systems live and die by the guardrail layer, not the model. This project shows the shape.
