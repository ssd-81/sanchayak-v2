import os
import json
import io
from fd_data import FD_OPTIONS

SYSTEM_PROMPT = """Aap ek helpful FD advisor hain jo Tier 2/3 India ke users ke liye kaam karte hain.

Rules:
- Hamesha simple Hindi mein baat karein. Koi English jargon nahi.
- Neeche diye FD options mein se exactly 3 best options compare karein.
- Har option ke liye clearly batayein: bank ka naam, byaaj dar, aur 1 lakh pe kitna milega.
- Ek recommendation zaroor dein — user ki situation ke hisaab se.
- Jawab 60 words se zyada nahi hona chahiye (voice ke liye zaroori).
- Agar user booking karna chahta hai, kahein: "Booking ke liye aapka Aadhaar number chahiye."

FD Options: {fd_data}
"""


def get_groq_client():
    """Get Groq client with API key"""
    from groq import Groq

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment")
    return Groq(api_key=api_key)


def transcribe_audio(audio_bytes: bytes) -> str:
    """Hindi audio bytes → Hindi text via Groq Whisper"""
    client = get_groq_client()
    transcription = client.audio.transcriptions.create(
        file=("audio.wav", audio_bytes),
        model="whisper-large-v3-turbo",
        language="hi",
        response_format="text",
    )
    return transcription


def get_fd_advice(user_query: str) -> str:
    """Hindi text → Hindi FD advice via Groq LLM"""
    client = get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(
                    fd_data=json.dumps(FD_OPTIONS, ensure_ascii=False)
                ),
            },
            {"role": "user", "content": user_query},
        ],
        max_tokens=200,
        temperature=0.3,
    )
    return response.choices[0].message.content


def text_to_speech_google(text: str) -> bytes:
    """Hindi text → Hindi audio bytes via Google Cloud TTS"""
    from google.cloud import texttospeech

    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="hi-IN", name="hi-IN-Wavenet-D"
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    return response.audio_content


def text_to_speech_gtts(text: str) -> bytes:
    """Hindi text → Hindi audio bytes via gTTS (fallback)"""
    from gtts import gTTS

    tts = gTTS(text=text, lang="hi", slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()


def text_to_speech_hindi(text: str, use_gtts: bool = False) -> bytes:
    """Hindi text → Hindi audio bytes. Try Google first, fallback to gTTS."""
    if use_gtts:
        return text_to_speech_gtts(text)
    try:
        return text_to_speech_google(text)
    except Exception:
        return text_to_speech_gtts(text)


def run_pipeline(audio_bytes: bytes, use_gtts: bool = False):
    """Full loop: audio → transcript → advice → speech"""
    transcript = transcribe_audio(audio_bytes)
    advice = get_fd_advice(transcript)
    audio_out = text_to_speech_hindi(advice, use_gtts=use_gtts)
    return transcript, advice, audio_out


def get_fd_comparison(user_query: str) -> str:
    """Text input for testing without audio"""
    return get_fd_advice(user_query)