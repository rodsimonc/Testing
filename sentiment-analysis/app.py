import re
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

MODEL_PATH = Path(__file__).parent / "model.joblib"
DATA_PATH = Path(__file__).parent / "data" / "reviews.csv"


def clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["text"] = df["text"].map(clean)
    return df


def train():
    df = load_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(max_iter=1000, C=4.0)),
    ])
    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)
    metrics = {
        "accuracy": accuracy_score(y_test, preds),
        "report": classification_report(y_test, preds, zero_division=0),
    }
    joblib.dump(pipe, MODEL_PATH)
    return pipe, metrics


def get_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH), None
    pipe, metrics = train()
    return pipe, metrics


def main():
    st.set_page_config(page_title="Sentiment Analysis", page_icon="💬")
    st.title("Sentiment Analysis")
    st.caption("TF-IDF + Logistic Regression, trained on a small labeled set of reviews.")

    model, train_metrics = get_model()

    with st.sidebar:
        st.header("Model")
        if st.button("Retrain"):
            with st.spinner("Training…"):
                model, train_metrics = train()
            st.success("Retrained.")
        if train_metrics:
            st.metric("Holdout accuracy", f"{train_metrics['accuracy']:.2f}")
            with st.expander("Classification report"):
                st.code(train_metrics["report"])

    text = st.text_area(
        "Enter text",
        placeholder="This product is amazing, best purchase I've made all year!",
        height=140,
    )
    if st.button("Analyze", type="primary") and text.strip():
        cleaned = clean(text)
        pred = model.predict([cleaned])[0]
        proba = model.predict_proba([cleaned])[0]
        classes = model.classes_
        label = "Positive" if pred == 1 else "Negative"
        confidence = float(proba[list(classes).index(pred)])
        st.subheader(f"{label}  ·  {confidence:.0%} confident")
        st.progress(confidence)
        st.write({str(c): float(p) for c, p in zip(classes, proba)})


if __name__ == "__main__":
    main()
