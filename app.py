import streamlit as st
import os
import time
from audio_recorder_streamlit import audio_recorder
from pipeline import run_pipeline, get_fd_comparison
from test_utils import mock_fd_advice
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="FD Sahayak", page_icon="mic", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');
    
    * { font-family: 'IBM Plex Sans', sans-serif !important; }
    
    html, body, .stApp {
        height: 100vh;
        overflow: hidden;
    }
    
    .stApp {
        background: #000;
        display: flex;
        flex-direction: column;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main-wrapper {
        flex: 1;
        display: flex;
        flex-direction: column;
        max-width: 600px;
        width: 100%;
        margin: 0 auto;
        padding: 12px;
    }
    
    .header {
        text-align: center;
        padding: 8px 0;
        flex-shrink: 0;
    }
    
    .header h1 {
        font-size: 18px;
        font-weight: 600;
        color: #fff;
        margin: 0;
    }
    
    .header p {
        font-size: 12px;
        color: #555;
        margin: 4px 0 0;
    }
    
    .mode-toggle {
        display: flex;
        justify-content: center;
        gap: 8px;
        padding: 8px 0;
        flex-shrink: 0;
        min-height: 44px;
    }

    .stButton > button {
        height: 40px !important;
        min-height: 40px !important;
    }
    
    .mode-btn {
        padding: 8px 20px;
        border: none;
        background: transparent;
        color: #555;
        font-size: 14px;
        cursor: pointer;
        border-radius: 20px;
        transition: all 0.2s;
    }
    
    .mode-btn.active {
        background: #10a37f;
        color: #fff;
    }
    
    .content-area {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 200px;
        max-height: 500px;
        overflow-y: auto;
    }
    
    /* Voice Mode */
    .voice-center {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
    }
    
    .voice-btn {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: #10a37f;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 0 40px rgba(16,163,127,0.4);
        transition: all 0.3s;
    }
    
    .voice-btn:hover {
        transform: scale(1.08);
        box-shadow: 0 0 60px rgba(16,163,127,0.6);
    }
    
    .voice-btn svg {
        width: 32px;
        height: 32px;
        fill: #fff;
    }
    
    .voice-hint {
        font-size: 14px;
        color: #666;
    }

    .voice-recorder {
        margin: 20px 0;
        min-height: 80px;
    }

    .voice-recorder iframe {
        border-radius: 12px;
    }
    
    /* Voice Response */
    .voice-response {
        display: flex;
        flex-direction: column;
        gap: 12px;
        width: 100%;
    }
    
    .resp-card {
        background: #111;
        border-radius: 12px;
        padding: 14px;
    }
    
    .resp-card h4 {
        color: #10a37f;
        font-size: 11px;
        font-weight: 600;
        margin: 0 0 8px;
        text-transform: uppercase;
    }
    
    .resp-card p {
        color: #ccc;
        font-size: 14px;
        margin: 0;
        line-height: 1.5;
    }
    
    /* Chat Mode */
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 10px;
        padding: 8px 0;
    }
    
    .chat-messages::-webkit-scrollbar {
        display: none;
    }
    
    .msg {
        max-width: 85%;
        padding: 10px 14px;
        border-radius: 14px;
        font-size: 14px;
        line-height: 1.4;
    }
    
    .msg-user {
        align-self: flex-end;
        background: #10a37f;
        color: #fff;
        border-bottom-right-radius: 4px;
    }
    
    .msg-bot {
        align-self: flex-start;
        background: #222;
        color: #ddd;
        border-bottom-left-radius: 4px;
    }
    
    /* Input Area */
    .input-area {
        flex-shrink: 0;
        padding: 8px 0 0;
    }
    
    .input-wrapper {
        display: flex;
        gap: 8px;
        background: #222;
        border-radius: 24px;
        padding: 6px 12px;
        align-items: center;
    }
    
    .input-wrapper input {
        flex: 1;
        background: transparent !important;
        border: none !important;
        color: #fff !important;
        font-size: 14px;
        padding: 8px 0 !important;
    }
    
    .input-wrapper input::placeholder {
        color: #555;
    }
    
    .input-wrapper input:focus {
        box-shadow: none !important;
    }
    
    .input-wrapper button {
        background: #10a37f !important;
        border-radius: 50% !important;
        width: 32px;
        height: 32px !important;
        padding: 0 !important;
    }
    
    .stSpinner {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    
    .stAudio {
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

api_key = os.environ.get("GROQ_API_KEY")
api_key_set = bool(api_key and api_key.strip() and not api_key.startswith("your_"))

if not api_key_set:
    st.warning("⚠️ API key not set - running in demo mode")

if "mode" not in st.session_state:
    st.session_state.mode = "voice"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_advice" not in st.session_state:
    st.session_state.current_advice = ""

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "audio_out" not in st.session_state:
    st.session_state.audio_out = None

if "processing" not in st.session_state:
    st.session_state.processing = False

if "recorder_count" not in st.session_state:
    st.session_state.recorder_count = 0

st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h1>FD Sahayak</h1>
    <p>Hindi mein boliye, FD ke baare mein janiye</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🎤 Voice" if st.session_state.mode != "voice" else "🎤 Voice", use_container_width=True):
        st.session_state.mode = "voice"
        st.rerun()
with col2:
    if st.button("💬 Chat" if st.session_state.mode != "chat" else "💬 Chat", use_container_width=True):
        st.session_state.mode = "chat"
        st.rerun()

st.markdown('<div class="content-area">', unsafe_allow_html=True)

if st.session_state.mode == "voice":
    if not st.session_state.current_advice:
        st.markdown('<div class="voice-center">', unsafe_allow_html=True)
        
        audio_bytes = audio_recorder(
            text="Tap to record",
            pause_threshold=2.0,
            sample_rate=16000,
            energy_threshold=0.01,
            icon_name="microphone",
            icon_size="4x",
            neutral_color="#10a37f",
            recording_color="#ff0000",
            key=f"vrec_{st.session_state.recorder_count}"
        )
        
        print(f"[DEBUG] mode={st.session_state.mode}, has_advice={bool(st.session_state.current_advice)}, has_audio={bool(audio_bytes)}")
        
        if audio_bytes and not st.session_state.current_advice:
            print("[APP] Processing new audio...")
            with st.spinner("Processing..."):
                try:
                    if api_key_set:
                        from pipeline import transcribe_audio, get_fd_advice
                        transcript = transcribe_audio(audio_bytes)
                        advice = get_fd_advice(transcript)
                    else:
                        transcript = "Mock transcription"
                        advice = mock_fd_advice("FD query")
                    
                    print(f"[APP] Got transcript: {transcript[:30]}...")
                    print(f"[APP] Got advice: {advice[:50]}...")
                    st.session_state.transcript = transcript
                    st.session_state.current_advice = advice
                except Exception as e:
                    print(f"[APP] Error: {e}")
                    st.error(f"Error: {str(e)}")
                    st.session_state.transcript = "Error"
                    st.session_state.current_advice = str(e)
            
            audio_bytes = None
        
        if st.session_state.current_advice:
            print("[APP] Showing response")
            st.markdown(f'''
            <div class="voice-response">
                <div class="resp-card">
                    <h4>Aapne kaha</h4>
                    <p>{st.session_state.transcript}</p>
                </div>
                <div class="resp-card">
                    <h4>Salah</h4>
                    <p>{st.session_state.current_advice}</p>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            if st.button("Naya sawaal"):
                st.session_state.transcript = ""
                st.session_state.current_advice = ""
                st.session_state.recorder_count += 1

else:
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    
    for msg in st.session_state.chat_history:
        cls = "msg-user" if msg["type"] == "user" else "msg-bot"
        st.markdown(f'<div class="msg {cls}">{msg["text"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="input-area">', unsafe_allow_html=True)
    st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)
    
    user_input = st.text_input("", placeholder="Mujhe 50,000 FD mein rakhne hain...", label_visibility="collapsed", key="chat_in")
    send_btn = st.button("➤", key="send")
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    if send_btn and user_input:
        st.session_state.chat_history.append({"type": "user", "text": user_input})
        
        with st.spinner("Soch raha hoon..."):
            try:
                if api_key_set:
                    advice = get_fd_comparison(user_input)
                else:
                    advice = mock_fd_advice(user_input)
                st.session_state.chat_history.append({"type": "bot", "text": advice})
            except Exception as e:
                st.session_state.chat_history.append({"type": "bot", "text": f"Error: {e}"})
        
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)