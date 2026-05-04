# Vernacular Voice FD Advisor

Voice-based Hindi financial advisory for Tier 2/3 India. Speaks Hindi, hears Hindi.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## What This Does

User speaks Hindi -> transcribes -> compares FD options -> speaks Hindi back.

## Stack

- STT: Groq Whisper
- LLM: Groq LLaMA
- TTS: Google Cloud
- UI: Streamlit