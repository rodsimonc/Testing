# Ten offline AI project starters

Ten small AI projects — each self-contained and API-free.

| # | Project | Stack | What it does |
|---|---|---|---|
| 1 | [`sentiment-analysis/`](./sentiment-analysis) | sklearn + Streamlit | TF-IDF + Logistic Regression sentiment classifier |
| 2 | [`resume-parser/`](./resume-parser) | spaCy + PyMuPDF + Streamlit | Contact info, skills, sections from PDF/TXT resumes |
| 3 | [`rag-chatbot/`](./rag-chatbot) | sentence-transformers + Streamlit | Retrieval-only RAG over your text/markdown files |
| 4 | [`ai-code-reviewer/`](./ai-code-reviewer) | AST + Streamlit | Static Python review — 12 rules across 3 severities |
| 5 | [`medical-chatbot/`](./medical-chatbot) | Streamlit | Symptom checker with emergency guardrails |
| 6 | [`voice-assistant/`](./voice-assistant) | faster-whisper + pyttsx3 + Streamlit | STT → intent router → optional TTS |
| 7 | [`ai-meeting-notes/`](./ai-meeting-notes) | faster-whisper + Streamlit | Audio → transcript → extractive summary + action items |
| 8 | [`multi-agent-system/`](./multi-agent-system) | Streamlit | Coordinator routing across Calculator / Retrieval / Summarizer |
| 9 | [`vision-qa/`](./vision-qa) | CLIP + Streamlit | Zero-shot image classification |
| 10 | [`ai-saas-app/`](./ai-saas-app) | FastAPI + SQLite + Docker | Summarize-as-a-Service with signup + API keys |

Each folder has its own `requirements.txt` and `README.md`. Install into a fresh virtualenv per project.
