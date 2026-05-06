import os
import json
import io
import traceback
import functools
from fd_data import FD_OPTIONS
from hindi_numbers import extract_amount, extract_tenure

@functools.lru_cache(maxsize=1)
def _get_cached_client():
    """Cached Groq client to avoid re-initialization"""
    from groq import Groq
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment")
    return Groq(api_key=api_key, timeout=60)


SYSTEM_PROMPT = """Aap (aurat) ek helpful FD advisor hain. Aapke Baal GM ka kaam hai, aapko customers ki madad karni hai. Aapka kaam users ko Hindi mein samjhana hai ki kahaan FD rakhein jo sabse zyada fayda milega.

Context:
- Users hajar ya हज़ार (1000) aur lakh ya लाख (1,00,000) use karte hain amounts ke liye
- saal tenure ke liye use hota hai
- Simple, natural Hindi mein baat karein - jaise aap apni behen ya dost se baat karti hain

IMPORTANT - Hindi Devanagari Script ONLY:
- rupaye matlab रुपये - DEVANAGARI mein likhein, Angreji script NAHIN
- Numbers bhi Hindi mein likhein: 50,000 -> 50,000 YA 50 हज़ार
- Koi bhi Angreji word bilkul mat use karein - pura Hindi mein baat karein

Aapki pehchan - feminine:
- Main aapki madad kar sakti hoon
- Mere hisab se...
- Mera suggestion...

Rules:
- PURE HINDI DEVNAGARI - Har ek shabd Hindi mein. Romanized Hindi ya English bilkul NAHIN.
- Jab user KOI OPTION SELECT kare, toh TURANT booking start karein: Booking confirm karne ke liye aapka 12-digit Aadhaar number batayein.
- Jab user amount aur tenure BATAYE, toh options BATAYEIN aur recommend karein
- Agar user sirf amount bataye, toh poocho Kitne saal ke liye?
- Agar user sirf tenure bataye, toh poocho Kitna amount rakhna chahti ho?
- EK simple recommendation ZAROOR DEIN - kis bank mein rakhe yeh sabse accha rahega
- Jawab natural, conversational hona chahiye - maximum 2-3 sentences.
- Agar user booking karna chahti hai, toh kahein Booking ke liye aapka Aadhaar number chahiye hoga.

FD Options (yeh data use karein): {fd_data}
"""


def get_groq_client():
    """Get Groq client with API key"""
    return _get_cached_client()


def transcribe_audio(audio_bytes: bytes) -> str:
    """Hindi audio bytes to Hindi text via Groq Whisper"""
    client = get_groq_client()
    
    # Streamlit audio_recorder returns a valid WAV file out of the box.
    # We pass the bytes directly. Wrapping it in wave.open corrupts the file headers.
    transcription = client.audio.transcriptions.create(
        file=("audio.wav", audio_bytes),
        model="whisper-large-v3-turbo",
        language="hi",
        response_format="text",
        prompt="Fixed deposit, FD, Bank, Interest rate, Byaaj dar, Tenure, Amount, Lakh, HDFC, SBI, Bajaj Finance"
    )
    return transcription


def get_fd_advice(user_query: str, chat_history: list = None) -> str:
    """Hindi text to Hindi FD advice via Groq LLM"""
    if chat_history is None:
        chat_history = []
        
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(
                fd_data=json.dumps(FD_OPTIONS, ensure_ascii=False)
            ),
        }
    ]
    
    for msg in chat_history:
        role = msg.get("role", "user")
        content = msg.get("content", msg.get("text", ""))
        messages.append({"role": role, "content": content})
        
    messages.append({"role": "user", "content": user_query})

    client = get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=200,
        temperature=0.3,
    )
    return response.choices[0].message.content


def text_to_speech_google(text: str) -> bytes:
    """Hindi text to Hindi audio bytes via Google Cloud TTS"""
    from google.cloud import texttospeech

    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="hi-IN", name="hi-IN-Wavenet-A"
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    return response.audio_content


def text_to_speech_gtts(text: str) -> bytes:
    """Hindi text to Hindi audio bytes via gTTS (fallback)"""
    from gtts import gTTS

    tts = gTTS(text=text, lang="hi", slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()


def text_to_speech_hindi(text: str, use_gtts: bool = False) -> bytes:
    """Hindi text to Hindi audio bytes. Try Google first, fallback to gTTS."""
    if use_gtts:
        return text_to_speech_gtts(text)
    try:
        return text_to_speech_google(text)
    except Exception:
        return text_to_speech_gtts(text)


def run_pipeline(audio_bytes: bytes, chat_history: list = None, use_gtts: bool = False):
    """Full loop: audio to transcript to advice to speech"""
    print(f"[PIPELINE] Audio received: {len(audio_bytes)} bytes")
    transcript = transcribe_audio(audio_bytes)
    print(f"[PIPELINE] Transcript: {transcript[:50]}...")
    advice = get_fd_advice(transcript, chat_history=chat_history)
    print(f"[PIPELINE] Advice: {advice[:50]}...")
    audio_out = text_to_speech_hindi(advice, use_gtts=use_gtts)
    print(f"[PIPELINE] Audio out: {len(audio_out)} bytes")
    return transcript, advice, audio_out


def get_fd_comparison(user_query: str, chat_history: list = None) -> str:
    """Text input for testing without audio"""
    return get_fd_advice(user_query, chat_history)