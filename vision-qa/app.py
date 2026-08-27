import io
from typing import Sequence

import streamlit as st
from PIL import Image


@st.cache_resource
def load_clip():
    import torch
    from transformers import CLIPModel, CLIPProcessor
    model_id = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(model_id)
    processor = CLIPProcessor.from_pretrained(model_id)
    model.eval()
    return model, processor, torch


def score(image: Image.Image, labels: Sequence[str]):
    model, processor, torch = load_clip()
    prompts = [f"a photo of {l.strip()}" for l in labels if l.strip()]
    inputs = processor(text=prompts, images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits_per_image[0]
    probs = logits.softmax(dim=0).tolist()
    ranked = sorted(zip(labels, probs), key=lambda x: -x[1])
    return ranked


def main():
    st.set_page_config(page_title="Vision QA", page_icon="🖼️")
    st.title("Vision QA")
    st.caption("Zero-shot image classification with CLIP. Upload an image, give it candidate labels or short questions, get scored answers. No API.")

    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded = st.file_uploader("Image", type=["png", "jpg", "jpeg", "webp"])
        if uploaded:
            image = Image.open(io.BytesIO(uploaded.read())).convert("RGB")
            st.image(image, use_container_width=True)
        else:
            image = None

    with col2:
        default_labels = "a cat\na dog\na person\na landscape\na piece of food\na building"
        labels_text = st.text_area(
            "Candidate labels (one per line)",
            value=default_labels,
            height=200,
        )
        labels = [l for l in labels_text.splitlines() if l.strip()]

    if image and labels and st.button("Score", type="primary"):
        with st.spinner("Loading CLIP (first run downloads ~150 MB) and scoring…"):
            results = score(image, labels)
        st.subheader("Ranked")
        for label, p in results:
            st.write(f"**{label}** — {p:.1%}")
            st.progress(float(p))


if __name__ == "__main__":
    main()
