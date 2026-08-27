# AI Meeting Notes

Local pipeline: transcribe a meeting recording with Whisper, then produce an extractive summary and a list of action items. No API keys, no external calls.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Whisper models download on first use into the local cache. The `tiny`/`base` models run comfortably on CPU; `small`/`medium` are slower but sharper.

**System dependency:** `faster-whisper` decodes non-WAV audio (mp3, m4a, ogg, webm) via libav/ffmpeg. Install ffmpeg (`apt install ffmpeg` on Debian/Ubuntu, `brew install ffmpeg` on macOS) or upload WAV files.

## What it does

- **Transcription** — `faster-whisper` (int8 CPU) on any common audio/video format
- **Summary** — TF-IDF-style sentence scoring; picks the top N sentences in original order
- **Action items** — regex on common commitment phrases ("we'll…", "action item", "follow-up", deadlines, owners)
- **Export** — download the full notes as Markdown

You can also skip audio entirely and paste a transcript in the second tab.

## Layout

- `app.py` — Streamlit UI and Whisper glue
- `summarizer.py` — sentence splitting, scoring, action-item detection
