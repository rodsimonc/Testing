# Seven offline AI project starters

Seven small AI projects, each self-contained and API-free.

| Project | Stack | What it does |
|---|---|---|
| [`sentiment-analysis/`](./sentiment-analysis) | sklearn + Streamlit | TF-IDF + Logistic Regression sentiment classifier |
| [`resume-parser/`](./resume-parser) | spaCy + PyMuPDF + Streamlit | Extracts contact info, skills, sections from PDF/TXT resumes |
| [`ai-meeting-notes/`](./ai-meeting-notes) | faster-whisper + Streamlit | Local audio transcription → extractive summary + action items |
| [`rag-chatbot/`](./rag-chatbot) | sentence-transformers + Streamlit | Retrieval-only RAG over your text/markdown files |
| [`ai-code-reviewer/`](./ai-code-reviewer) | AST + Streamlit | Static Python review — mutable defaults, bare excepts, secrets, unused imports |
| [`multi-agent-system/`](./multi-agent-system) | Streamlit | Coordinator routing across Calculator / Retrieval / Summarizer specialists |
| [`vision-qa/`](./vision-qa) | CLIP + Streamlit | Zero-shot image classification / captioning |

Each folder has its own `requirements.txt` and `README.md`. Install into a fresh virtualenv per project.
