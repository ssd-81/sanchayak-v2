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

SYSTEM_PROMPT = """Aap ek helpful FD (fixed deposit) advisor hain jo Tier 2/3 India ke users ke liye kaam karte hain. Users ke paas byaaj (interest rate), savings, rupaye, aur fd options ke baare mein sawaal ho sakte hain.

Context - Transcription notes:
- Audio transcript mein common terms hain: FD, fixed deposit, byaaj, rupaye, SBI, HDFC, Bajaj, Aadhaar, savings, hazaar, lakh, saal, sal
- Users "hazaar" (1000) aur "lakh" (1,00,000) use karte hain amounts ke liye
- "saal" ya "sal" tenure ke liye use hota hai

Rules:
- Hamesha simple Hindi mein baat karein. Koi English jargon nahi.
- PEHLE AMOUNT AUR TENURE SAMJHO - Jab user kuch amount aur tenure bataye (jaise "5 lakh 2 saal ke liye"), toh AISHI KE BAD TURANT recommend banks.
- Agar user sirf amount bataye, toh pucho "Kitne saal ke liye?"
- Agar user sirf tenure bataye, toh pucho "Kitna amount invest karna chahte ho?"
- Jab amount + tenure dono mil jayein, toh WAHEIN BEST BANKS RECOMMEND KAREIN - user se poochne ki zaroorat nahi.
- FD options mein se highest rate wale top 2-3 banks recommend karein.
- Jab options batayein: bank ka naam, byaaj dar (%), aur interest amount clearly batayein.
- Amounts ko lakh/hazaar mein explain karein (jaise: "1 lakh pe 7.5% se ₹7,500 milega ek saal mein").
- Ek recommendation zaroor dein agar options bata rahe ho.
- Jawab EXTREMELY chota (sirf 1 ya 2 lines, max 30 words), crisp aur to-the-point hona chahiye kyunki yeh voice output ke liye hai. Lambe messages bilkul mat bhejein.
- Agar user booking karna chahta hai, kahein: "Booking ke liye aapka Aadhaar number chahiye."

FD Options: {fd_data}
"""


def get_groq_client():
    """Get Groq client with API key"""
    return _get_cached_client()


def transcribe_audio(audio_bytes: bytes) -> str:
    """Hindi audio bytes → Hindi text via Groq Whisper"""
    client = get_groq_client()
    
    # Streamlit audio_recorder returns a valid WAV file out of the box.
    # We pass the bytes directly. Wrapping it in wave.open corrupts the file headers.
    transcription = client.audio.transcriptions.create(
        file=("audio.wav", audio_bytes),
        model="whisper-large-v3-turbo",
        language="hi",
        response_format="text",
        prompt="Fixed deposit, FD, Bank, Interest rate, Byaaj dar, Tenure, Amount, Lakh, HDFC, SBI, Bajaj Finance" # Helps with domain-specific terms
    )
    return transcription


def get_fd_advice(user_query: str, chat_history: list = None) -> str:
    """Hindi text → Hindi FD advice via Groq LLM"""
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
    print(f"[PIPELINE] Audio received: {len(audio_bytes)} bytes")
    transcript = transcribe_audio(audio_bytes)
    print(f"[PIPELINE] Transcript: {transcript[:50]}...")
    advice = get_fd_advice(transcript)
    print(f"[PIPELINE] Advice: {advice[:50]}...")
    audio_out = text_to_speech_hindi(advice, use_gtts=use_gtts)
    print(f"[PIPELINE] Audio out: {len(audio_out)} bytes")
    return transcript, advice, audio_out


def get_fd_comparison(user_query: str, chat_history: list = None) -> str:
    """Text input for testing without audio"""
    return get_fd_advice(user_query, chat_history)