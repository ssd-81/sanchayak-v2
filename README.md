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

| Layer | Tool | Why |
|---|---|---|
| STT | Groq whisper-large-v3 | Hindi support, fast |
| LLM | Groq llama-3.3-70b-versatile | Fast, cheap |
| TTS | Google Cloud TTS (hi-IN-Wavenet-D) | Natural Hindi voice |
| UI | Streamlit | Browser-based, record button built-in |

## File Structure

```
fd-advisor/
├── app.py              # Main Streamlit app
├── pipeline.py         # STT → LLM → TTS logic
├── fd_data.py          # Hardcoded FD JSON
├── requirements.txt
└── .env                # GROQ_API_KEY, GOOGLE_APPLICATION_CREDENTIALS
```

## What Is Mocked

- FD rate data is hardcoded JSON (4 banks)
- Bank booking API is mock
- KYC/Aadhaar verification is placeholder input

## Prerequisites

Get your API keys before running:

1. Groq: console.groq.com (free tier works)
2. Google Cloud: Enable Cloud TTS API, download credentials.json

## Build Schedule

- Day 1: Text loop (type question, get Hindi advice)
- Day 2: Add STT (audio file in, Hindi text out)
- Day 3: Add TTS (full audio in, audio out)
- Day 4: Streamlit UI (phone-frame styling)
- Day 5: Polish and rehearse

## Demo

User: "Mujhe 50,000 rupaye FD mein rakhne hain, kahan rakhun?"

App responds with 3 FD comparisons in Hindi voice.