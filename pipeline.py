import os
import json
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


def transcribe_audio(audio_bytes: bytes) -> str:
    """Hindi audio bytes → Hindi text via Groq Whisper"""
    from groq import Groq

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    transcription = client.audio.transcriptions.create(
        file=("audio.wav", audio_bytes),
        model="whisper-large-v3-turbo",
        language="hi",
        response_format="text",
    )
    return transcription


def get_fd_advice(user_query: str) -> str:
    """Hindi text → Hindi FD advice via Groq LLM"""
    from groq import Groq

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
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


def text_to_speech_hindi(text: str) -> bytes:
    """Hindi text → Hindi audio bytes via Google TTS"""
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


def run_pipeline(audio_bytes: bytes):
    """Full loop: audio → transcript → advice → speech"""
    transcript = transcribe_audio(audio_bytes)
    advice = get_fd_advice(transcript)
    audio_out = text_to_speech_hindi(advice)
    return transcript, advice, audio_out


def get_fd_comparison(user_query: str) -> str:
    """Text input for testing without audio"""
    return get_fd_advice(user_query)