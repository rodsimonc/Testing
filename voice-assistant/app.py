import tempfile
from pathlib import Path

import streamlit as st

from intents import dispatch


@st.cache_resource
def load_whisper(size: str):
    from faster_whisper import WhisperModel
    return WhisperModel(size, device="cpu", compute_type="int8")


def transcribe(audio_bytes: bytes, suffix: str, size: str) -> str:
    model = load_whisper(size)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        path = tmp.name
    segments, _ = model.transcribe(path, vad_filter=True)
    return " ".join(s.text.strip() for s in segments).strip()


def try_speak(text: str) -> bytes | None:
    """Best-effort local TTS via pyttsx3. Returns WAV bytes or None on failure."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            path = tmp.name
        engine.save_to_file(text, path)
        engine.runAndWait()
        return Path(path).read_bytes()
    except Exception:
        return None


def main():
    st.set_page_config(page_title="Voice Assistant", page_icon="🎤")
    st.title("Voice Assistant")
    st.caption("Local Whisper for speech-in, rule-based intent routing, optional pyttsx3 for speech-out. No API.")

    with st.sidebar:
        st.header("Settings")
        model_size = st.selectbox("Whisper model", ["tiny", "base", "small"], index=0)
        speak_back = st.checkbox("Speak the reply (needs pyttsx3 + system TTS)", value=False)
        st.markdown("### Supported intents")
        st.markdown(
            "- Greeting / farewell\n"
            "- What time / date is it?\n"
            "- Tell me a joke\n"
            "- Weather in *place*\n"
            "- Calculate `12 * (7 + 3)`\n"
        )

    tab_voice, tab_text = st.tabs(["Voice", "Text"])

    query = None
    with tab_voice:
        uploaded = st.file_uploader("Audio", type=["mp3", "wav", "m4a", "webm", "ogg"])
        if uploaded and st.button("Transcribe & respond", type="primary"):
            suffix = Path(uploaded.name).suffix or ".mp3"
            with st.spinner("Transcribing…"):
                query = transcribe(uploaded.read(), suffix, model_size)
            st.write(f"**Heard:** {query}")

    with tab_text:
        typed = st.text_input("Ask something")
        if typed and st.button("Send"):
            query = typed

    if query:
        intent, reply = dispatch(query)
        st.subheader(f"Reply ({intent})")
        st.write(reply)
        if speak_back:
            wav = try_speak(reply)
            if wav:
                st.audio(wav, format="audio/wav")
            else:
                st.info("pyttsx3 isn't available or has no voice installed. Install `pyttsx3` + `espeak-ng`.")


if __name__ == "__main__":
    main()
