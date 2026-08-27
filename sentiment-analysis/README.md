# Sentiment Analysis

Small end-to-end sentiment classifier: TF-IDF + Logistic Regression, served with Streamlit.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

The model trains on first launch from `data/reviews.csv` and caches to `model.joblib`. Click **Retrain** in the sidebar to rebuild.

## Layout

- `app.py` — Streamlit UI, training pipeline, inference
- `data/reviews.csv` — labeled examples (1 = positive, 0 = negative)
- `model.joblib` — cached fitted pipeline (created on first run)
