# Voice Assistant

Local voice assistant with no API. Whisper for speech-to-text, rule-based intent routing, optional pyttsx3 for speech-out.

## Run

```bash
pip install -r requirements.txt
# Linux (Debian/Ubuntu):
#   sudo apt-get install espeak-ng ffmpeg   # espeak-ng for TTS, ffmpeg for non-WAV audio
# macOS:
#   brew install espeak-ng ffmpeg
streamlit run app.py
```

## Supported intents

- Greeting / farewell
- Current time / date
- Tell a joke
- Weather in `<place>` (demo response — no real weather API)
- Calculate arithmetic

## Layout

- `app.py` — Streamlit UI, Whisper glue, TTS best-effort
- `intents.py` — regex-driven intent dispatcher

## Why like this

The list called for Speech AI + gTTS + OpenAI, but gTTS reaches Google and OpenAI is an API. Whisper (STT) + pyttsx3 (TTS) is the fully-offline equivalent. The intent layer stays deterministic — swap it for an LLM later if you want free-form conversation.
