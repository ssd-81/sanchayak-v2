# Vernacular Voice FD Advisor

Voice-based Hindi financial advisory for Tier 2/3 India. Speaks Hindi, hears Hindi.

## Quick Start

### 1. Create `.env` file

Create a `.env` file in the project root with your API keys:

```bash
# Required: Groq API key (get free key at https://console.groq.com)
GROQ_API_KEY=your_groq_key_here

# Optional: Backup key if you have one
# GROQ_API_KEY_BACKUP=your_backup_key_here

# Optional: Google Cloud TTS (leave empty to use free gTTS fallback)
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
```

### 2. Run the app

```bash
pip install -r requirements.txt
streamlit run app.py
```

> **Note:** If you skip `.env`, the app runs in demo mode with mock responses.

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

Get your API keys:

1. **Groq** (required): Sign up at https://console.groq.com → Create API key
2. **Google Cloud TTS** (optional): Enable Cloud Text-to-Speech API → Download credentials.json

See `.env.example` for the exact variable names.

## Demo

User: "Mujhe 50,000 rupaye FD mein rakhne hain, kahan rakhun?"

App responds with 3 FD comparisons in Hindi voice.