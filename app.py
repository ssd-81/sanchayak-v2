import streamlit as st
import os
from audio_recorder_streamlit import audio_recorder
from pipeline import run_pipeline, get_fd_advice
from test_utils import mock_fd_advice
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="FD Sahayak",
    page_icon="🎙️",
    layout="centered"
)

# ── CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #0a0a0a !important;
    color: #e0e0e0;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }

/* ── Container ── */
.main .block-container {
    padding: 2rem 1rem 1rem 1rem !important;
    max-width: 480px !important;
    margin: 0 auto;
}

/* ── Title Area ── */
.fd-header {
    text-align: center;
    padding: 24px 0 8px;
}

.fd-header h1 {
    font-size: 32px;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}

.fd-header p {
    font-size: 14px;
    color: #666;
    margin: 0;
    font-weight: 400;
}

/* ── Mode Toggle ── */
div[data-testid="stRadio"] {
    display: flex;
    justify-content: center;
}

div[data-testid="stRadio"] > div {
    display: flex;
    justify-content: center;
    gap: 4px;
}

div[data-testid="stRadio"] label {
    color: #aaa !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}

div[data-testid="stRadio"] label[data-checked="true"] {
    color: #fff !important;
}

/* ── Conversation Bubbles ── */
.bubble-user {
    background: #1a2e1a;
    border: 1px solid #2a4a2a;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    margin: 6px 0 6px 60px;
    color: #d0e8d0;
    font-size: 14px;
    line-height: 1.6;
}

.bubble-bot {
    background: #151520;
    border: 1px solid #252535;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 16px;
    margin: 6px 60px 6px 0;
    color: #d0d0e0;
    font-size: 14px;
    line-height: 1.6;
    white-space: pre-wrap;
}

/* ── Mic Button Centering ── */
div[data-testid="column"]:has(iframe) {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

iframe[title*="audio_recorder"] {
    border: none !important;
    background: transparent !important;
    display: block !important;
    margin: 0 auto !important;
}

/* ── Status Text ── */
.status-text {
    text-align: center;
    color: #555;
    font-size: 13px;
    margin-top: 12px;
    font-weight: 400;
    letter-spacing: 0.5px;
}

/* ── Processing Dots ── */
@keyframes dotPulse {
    0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
    40% { opacity: 1; transform: scale(1); }
}

.thinking-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 16px 0;
}

.thinking-indicator .dot {
    width: 8px;
    height: 8px;
    background: #555;
    border-radius: 50%;
    animation: dotPulse 1.4s infinite;
}

.thinking-indicator .dot:nth-child(2) { animation-delay: 0.2s; }
.thinking-indicator .dot:nth-child(3) { animation-delay: 0.4s; }

/* ── Reset Button ── */
div[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid #333 !important;
    color: #888 !important;
    border-radius: 20px !important;
    font-size: 13px !important;
    padding: 6px 20px !important;
    transition: all 0.2s !important;
}

div[data-testid="stButton"] button:hover {
    border-color: #555 !important;
    color: #ccc !important;
    background: #1a1a1a !important;
}

/* ── Spinner ── */
div[data-testid="stSpinner"] {
    text-align: center;
}

div[data-testid="stSpinner"] > div {
    justify-content: center;
}

/* ── Chat Input ── */
div[data-testid="stChatInput"] {
    max-width: 480px;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

# ── State ───────────────────────────────────────────
api_key = os.environ.get("GROQ_API_KEY")
api_key_set = bool(api_key and api_key.strip() and not api_key.startswith("your_"))

if not api_key_set:
    st.warning("⚠️ API key not set - running in demo mode")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processing" not in st.session_state:
    st.session_state.processing = False

# ── Header ──────────────────────────────────────────
st.markdown("""
<div class="fd-header">
    <h1>FD Sahayak</h1>
    <p>Hindi mein boliye, FD ke baare mein janiye</p>
</div>
""", unsafe_allow_html=True)

# ── Mode Toggle ─────────────────────────────────────
_, center_col, _ = st.columns([1, 2, 1])
with center_col:
    mode = st.radio("", ["🎙️ Voice", "💬 Chat"], horizontal=True, label_visibility="collapsed")

# ── Conversation ────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="bubble-user">🎤 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bubble-bot">{msg["content"]}</div>', unsafe_allow_html=True)

# ── Voice Mode ──────────────────────────────────────
if "Voice" in mode:
    # Centered mic
    _, mic_col, _ = st.columns([1, 1, 1])
    with mic_col:
        audio_bytes = audio_recorder(
            text="",
            icon_size="3x",
            sample_rate=16000,
            pause_threshold=2.0,
            neutral_color="#ffffff",
            recording_color="#ff4444",
        )

    st.markdown('<div class="status-text">Tap to record</div>', unsafe_allow_html=True)

    if audio_bytes and len(audio_bytes) > 1000:
        st.markdown("""
        <div class="thinking-indicator">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.spinner("सोच रहा हूँ..."):
            try:
                if api_key_set:
                    transcript, advice, audio_out = run_pipeline(audio_bytes)
                else:
                    transcript = "Mock transcription"
                    advice = mock_fd_advice("FD query")
                    audio_out = None

                st.session_state.messages.append({"role": "user", "content": transcript})
                st.session_state.messages.append({"role": "assistant", "content": advice})
                if audio_out:
                    st.audio(audio_out, format="audio/mp3", autoplay=True)
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})

        st.rerun()

# ── Chat Mode ───────────────────────────────────────
else:
    user_input = st.chat_input("Hindi mein likhiye...")
    if user_input:
        with st.spinner("सोच रहा हूँ..."):
            try:
                if api_key_set:
                    advice = get_fd_advice(user_input, chat_history=st.session_state.messages)
                else:
                    advice = mock_fd_advice(user_input)

                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.messages.append({"role": "assistant", "content": advice})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})

        st.rerun()

# ── Reset ───────────────────────────────────────────
if st.session_state.messages:
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        if st.button("नया सवाल", use_container_width=True):
            st.session_state.messages = []
            st.rerun()