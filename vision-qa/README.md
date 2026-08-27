# Vision QA

Zero-shot image classification with CLIP (`openai/clip-vit-base-patch32`). Upload an image, provide candidate labels or short questions, get a ranked probability distribution back. Runs locally on CPU — no API.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

The CLIP checkpoint (~150 MB) downloads on first launch. CPU inference is a few seconds per image.

## How it works

CLIP embeds the image and each candidate label into the same vector space and returns the cosine-similarity distribution, softmaxed across labels. That's it — no fine-tuning, no API.

## Ideas

- Content moderation: `"a safe photo"` vs `"unsafe content"`
- Scene classification: `"indoor", "outdoor at night", "outdoor during day"`
- Product tagging: `"a shirt", "shoes", "a bag", "a watch"`

## Layout

- `app.py` — Streamlit UI + CLIP scoring
