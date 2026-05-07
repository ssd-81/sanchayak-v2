import streamlit as st
import os
import base64
from audio_recorder_streamlit import audio_recorder
from pipeline import run_pipeline, get_fd_advice
from test_utils import mock_fd_advice
from fd_data import FD_OPTIONS
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="संचायक",
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
    max-width: 640px !important;
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

/* ── Mode Toggle Buttons ── */
div[data-testid="stButton"]:has(button[key="mode_voice"]) button,
div[data-testid="stButton"]:has(button[key="mode_chat"]) button {
    border-radius: 40px !important;
    border: 1px solid #333 !important;
    background: #151520 !important;
    color: #888 !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 12px 28px !important;
    transition: all 0.25s ease !important;
}

div[data-testid="stButton"] button:hover {
    background: #202030 !important;
    border-color: #555 !important;
    color: #ccc !important;
}

/* ── FD Option Cards ── */
.fd-cards-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 8px 0;
}

.fd-card {
    background: #151520;
    border: 1px solid #2a2a3a;
    border-radius: 10px;
    padding: 10px 14px;
    cursor: pointer;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}

.fd-card:hover {
    border-color: #4a6a4a;
    background: #1a2020;
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.fd-card[data-selected="true"] {
    border-color: #4ade80;
    background: #1a2e1a;
}

.fd-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.fd-card-bank {
    font-size: 14px;
    font-weight: 700;
    color: #e0e0e0;
}

.fd-card-rate {
    font-size: 16px;
    font-weight: 700;
    color: #4ade80;
}

.fd-card-details {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 4px;
}

.fd-card-interest {
    font-size: 11px;
    color: #888;
}

.fd-card-badge {
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 20px;
    background: #1a2e1a;
    color: #4ade80;
    border: 1px solid #2a4a2a;
    font-weight: 600;
}

/* Force horizontal layout for columns at all widths */
div[data-testid="stColumns"] {
    flex-wrap: nowrap !important;
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
    st.warning("⚠️ API key nahi milega - demo mode chal raha hai")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processing" not in st.session_state:
    st.session_state.processing = False

if "pending_audio" not in st.session_state:
    st.session_state.pending_audio = None

if "voice_key" not in st.session_state:
    st.session_state.voice_key = 0

if "booking_confirmed" not in st.session_state:
    st.session_state.booking_confirmed = False

if "booking_success" not in st.session_state:
    st.session_state.booking_success = False

if "success_audio" not in st.session_state:
    st.session_state.success_audio = None

if "mode" not in st.session_state:
    st.session_state.mode = "voice"

if "show_fd_options" not in st.session_state:
    st.session_state.show_fd_options = False

if "selected_fd" not in st.session_state:
    st.session_state.selected_fd = None

if "user_amount" not in st.session_state:
    st.session_state.user_amount = 50000

if "user_tenure" not in st.session_state:
    st.session_state.user_tenure = 2

# ── Header ──────────────────────────────────────────
st.markdown("""
<div class="fd-header">
    <h1>संचायक</h1>
    <p>Hindi mein boliye, FD ke baare mein janiye</p>
</div>
""", unsafe_allow_html=True)

# ── Mode Toggle ─────────────────────────────────────
col_v, col_c = st.columns(2, gap="small")
with col_v:
    if st.button("🎙️ Voice", key="mode_voice", use_container_width=True):
        st.session_state.mode = "voice"
        st.rerun()
with col_c:
    if st.button("💬 Chat", key="mode_chat", use_container_width=True):
        st.session_state.mode = "chat"
        st.rerun()

mode = "Voice" if st.session_state.mode == "voice" else "Chat"

# ── Conversation ────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="bubble-user">🎤 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bubble-bot">{msg["content"]}</div>', unsafe_allow_html=True)

# ── Voice Mode ──────────────────────────────────────
if "Voice" in mode:
    # Initialize voice key if needed
    if "voice_key" not in st.session_state:
        st.session_state.voice_key = 0

    # Centered mic
    _, mic_col, _ = st.columns([1, 1, 1])
    with mic_col:
        # Stop any playing audio
        st.markdown("""
        <audio id="stopAllAudio" style="display:none;"></audio>
        <script>
        var allAudios = document.querySelectorAll('audio');
        allAudios.forEach(function(audio) {
            audio.pause();
            audio.currentTime = 0;
        });
        </script>
        """, unsafe_allow_html=True)
        
        audio_bytes = audio_recorder(
            text="",
            icon_size="3x",
            sample_rate=16000,
            pause_threshold=2.0,
            neutral_color="#ffffff",
            recording_color="#ff4444",
            key=f"voice_recorder_{st.session_state.voice_key}"
        )

    st.markdown('<div class="status-text">Tap to record</div>', unsafe_allow_html=True)

    if audio_bytes and len(audio_bytes) > 1000:
        st.session_state.processing = True
        
        # Append user message FIRST (so it's in history for LLM)
        transcript_placeholder = "Recording..."
        st.session_state.messages.append({"role": "user", "content": transcript_placeholder})
        
        with st.spinner("सोच रहा हूँ..."):
            try:
                if api_key_set:
                    transcript, advice, audio_out = run_pipeline(audio_bytes, chat_history=st.session_state.messages)
                else:
                    transcript = "Mock transcription"
                    advice = mock_fd_advice("FD query")
                    audio_out = None
                
                # Update the user message with actual transcript
                st.session_state.messages[-1] = {"role": "user", "content": transcript}
                st.session_state.messages.append({"role": "assistant", "content": advice})
                st.session_state.pending_audio = audio_out
                # Increment key to reset recorder and prevent re-submit
                st.session_state.voice_key += 1
                
                # Trigger FD options AFTER message shown
                if any(word in advice for word in ["विकल्प", "चुनना", "चुनें", "चुनिए", "मिलेगा", "ब्याज"]):
                    st.session_state.show_fd_options = True
                
                # Check booking - AFTER message shown
                advice_lower = advice.lower()
                if any(word in advice_lower for word in ["aadhaar", "booking", "lena hai", "chahiye hoga", "confirm kija", "आधार", "बुकिंग", "कन्फर्म"]):
                    st.session_state.booking_confirmed = True
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
        
        st.rerun()

if st.session_state.pending_audio:
    # Convert to base64 for autoplay
    b64_audio = base64.b64encode(st.session_state.pending_audio).decode('utf-8')
    audio_html = f'''
    <audio id="responseAudio" autoplay>
        <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
    </audio>
    '''
    st.markdown(audio_html, unsafe_allow_html=True)
    st.session_state.pending_audio = None

# ── Chat Mode ───────────────────────────────────────
elif "Chat" in mode:
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
                
                # Trigger FD options AFTER message is shown
                if any(word in advice for word in ["विकल्प", "सुझाव", "रखे"]):
                    st.session_state.show_fd_options = True
                
                # Check booking - AFTER message shown
                advice_lower = advice.lower()
                if any(word in advice_lower for word in ["aadhaar", "booking", "lena hai", "chahiye hoga", "confirm kija", "आधार", "बुकिंग", "कन्फर्म"]):
                    st.session_state.booking_confirmed = True
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})

        st.rerun()

# ── FD Option Cards ─────────────────────────────────
if st.session_state.show_fd_options and not st.session_state.booking_confirmed:
    amount = st.session_state.user_amount
    tenure = st.session_state.user_tenure
    
    st.markdown('<div class="fd-cards-container">', unsafe_allow_html=True)
    
    # Sort by rate descending and take top 3
    sorted_options = sorted(FD_OPTIONS, key=lambda x: x["rate"], reverse=True)[:3]
    
    # Radio selection (inline with cards)
    selection = st.radio(
        "Choose bank:",
        options=[i for i in range(len(sorted_options))],
        format_func=lambda i: f"{sorted_options[i]['bank']} @ {sorted_options[i]['rate']}%",
        label_visibility="collapsed",
        key="fd_radio_selection",
        horizontal=True
    )

    # Process selection
    if selection is not None:
        fd = sorted_options[selection]
        st.session_state.selected_fd = fd
        st.session_state.show_fd_options = False
        st.session_state.booking_confirmed = True
        selected_msg = f"आपने {fd['bank']} को चुना है ({fd['rate']}% ब्याज दर)। अब बुकिंग के लिए अपना 12-अंकों का आधार नंबर बताएं।"
        st.session_state.messages.append({"role": "assistant", "content": selected_msg})
        st.rerun()

    for i, fd in enumerate(sorted_options):
        interest = round(amount * fd["rate"] / 100 * tenure)
        badge_html = '<span class="fd-card-badge">सर्वोत्तम</span>' if i == 0 else ""
        
        st.markdown(f'''
        <div class="fd-card" data-index="{i}">
            <div class="fd-card-header">
                <span class="fd-card-bank">{fd["bank"]}</span>
                <span class="fd-card-rate">{fd["rate"]}%</span>
            </div>
            <div class="fd-card-details">
                <span class="fd-card-interest">अनुमानित ब्याज: ₹{interest:,} ({tenure} साल)</span>
                {badge_html}
            </div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown('</div>')

# ── Booking Flow ─────────────────────────────────
if st.session_state.booking_confirmed and not st.session_state.booking_success:
    st.markdown("---")
    aadhaar_input = st.text_input("अपना 12-अंकों का आधार नंबर दर्ज करें:", max_chars=12, key="aadhaar_input")
    if aadhaar_input and len(aadhaar_input) == 12:
        if st.button("बुकिंग कन्फर्म करें"):
            st.session_state.booking_success = True
            success_msg = "आपका एफडी बुकिंग कन्फर्म हो गया है! हमारी सर्विस चुनने के लिए शुक्रिया। आपको कन्फर्मेशन एसएमएस मिल जाएगा।"
            st.session_state.messages.append({
                "role": "assistant", 
                "content": success_msg
            })
            # Generate TTS for success message
            if api_key_set:
                from pipeline import text_to_speech_hindi
                audio_out = text_to_speech_hindi(success_msg)
                st.session_state.success_audio = audio_out
            st.rerun()

# Play success audio
if st.session_state.booking_success and hasattr(st.session_state, 'success_audio') and st.session_state.success_audio:
    b64_audio = base64.b64encode(st.session_state.success_audio).decode('utf-8')
    audio_html = f'''
    <audio id="successAudio" autoplay>
        <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
    </audio>
    <script>
        document.getElementById('successAudio').play().catch(function(e) {{}});
    </script>
    '''
    st.markdown(audio_html, unsafe_allow_html=True)
    st.session_state.success_audio = None

# ── Success Screen ─────────────────────────────────
if st.session_state.booking_success:
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <h1 style="font-size: 48px; margin-bottom: 24px;">✅</h1>
        <h2 style="color: #10a37f; margin-bottom: 16px;">बुकिंग कन्फर्म हो गई!</h2>
        <p style="color: #888; font-size: 16px;">आपको कन्फर्मेशन एसएमएस भेज दिया गया है</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("नया सवाल", use_container_width=True):
        st.session_state.messages = []
        st.session_state.booking_confirmed = False
        st.session_state.booking_success = False
        st.session_state.show_fd_options = False
        st.session_state.selected_fd = None
        st.rerun()

# ── Reset ───────────────────────────────────────────
if st.session_state.messages:
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        if st.button("नया सवाल", use_container_width=True):
            st.session_state.messages = []
            st.session_state.booking_confirmed = False
            st.session_state.booking_success = False
            st.session_state.show_fd_options = False
            st.session_state.selected_fd = None
            st.rerun()