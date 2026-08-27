# RAG Chatbot

Retrieval-only RAG: embed your text/markdown documents with `sentence-transformers` (MiniLM), then ask questions and get the top-K most relevant passages back with cosine similarity scores. No generator, no API — retrieval is honest about what it knows and can't hallucinate.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

The MiniLM model (~90 MB) downloads on first launch.

## What it does

- Chunks docs with configurable size + overlap
- Embeds each chunk with `all-MiniLM-L6-v2`
- Cosine-similarity retrieval (dot product over L2-normalized vectors)
- Returns top-K passages with source filenames and scores

## Layout

- `app.py` — Streamlit UI
- `rag.py` — chunking, embedding, index, retrieval

## Extending

Swap the retrieval-only output for an actual generator by feeding `hits` into a local LLM (llama-cpp-python, Ollama). The retrieval layer is deliberately isolated so this is a two-line change.
