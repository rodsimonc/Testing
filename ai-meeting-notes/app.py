import re
import tempfile
from pathlib import Path

import streamlit as st

from summarizer import extractive_summary, action_items


@st.cache_resource
def load_whisper(model_size: str):
    from faster_whisper import WhisperModel
    return WhisperModel(model_size, device="cpu", compute_type="int8")


def transcribe(file_bytes: bytes, suffix: str, model_size: str) -> str:
    model = load_whisper(model_size)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        path = tmp.name
    segments, _ = model.transcribe(path, vad_filter=True)
    return " ".join(seg.text.strip() for seg in segments).strip()


def main():
    st.set_page_config(page_title="AI Meeting Notes", page_icon="🎙️")
    st.title("AI Meeting Notes")
    st.caption("Local Whisper transcription + extractive summary + action items. No API calls.")

    with st.sidebar:
        st.header("Settings")
        model_size = st.selectbox(
            "Whisper model", ["tiny", "base", "small", "medium"], index=1,
            help="Larger = better quality, slower.",
        )
        num_sentences = st.slider("Summary sentences", 3, 15, 6)

    tab_audio, tab_text = st.tabs(["Audio / video file", "Paste transcript"])

    transcript = None
    with tab_audio:
        uploaded = st.file_uploader(
            "Recording", type=["mp3", "wav", "m4a", "mp4", "ogg", "webm", "flac"]
        )
        if uploaded and st.button("Transcribe", type="primary"):
            suffix = Path(uploaded.name).suffix or ".mp3"
            with st.spinner("Transcribing (first run downloads the model)…"):
                transcript = transcribe(uploaded.read(), suffix, model_size)
            st.session_state["transcript"] = transcript

    with tab_text:
        pasted = st.text_area("Meeting transcript", height=220)
        if pasted.strip() and st.button("Use this transcript"):
            st.session_state["transcript"] = pasted.strip()

    transcript = st.session_state.get("transcript")
    if not transcript:
        st.info("Upload audio or paste a transcript to get started.")
        return

    st.subheader("Transcript")
    st.write(transcript)

    st.subheader("Summary")
    summary = extractive_summary(transcript, num_sentences=num_sentences)
    for i, s in enumerate(summary, 1):
        st.markdown(f"{i}. {s}")

    st.subheader("Action items")
    items = action_items(transcript)
    if items:
        for item in items:
            st.markdown(f"- {item}")
    else:
        st.write("_none detected_")

    md = "# Meeting Notes\n\n## Summary\n" + "\n".join(f"- {s}" for s in summary) + \
         "\n\n## Action items\n" + ("\n".join(f"- {i}" for i in items) or "_none_") + \
         "\n\n## Transcript\n" + transcript
    st.download_button("Download notes (Markdown)", md, file_name="notes.md")


if __name__ == "__main__":
    main()
