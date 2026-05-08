import streamlit as st
import os
import base64
from audio_recorder_streamlit import audio_recorder
from pipeline import run_pipeline, get_fd_advice
from test_utils import mock_fd_advice
from fd_data import FD_OPTIONS
from dotenv import load_dotenv
import pathlib

env_path = pathlib.Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

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
    padding: 2rem 1rem 120px 1rem !important; /* Padding at bottom for fixed mic */
    max-width: 640px !important;
    margin: 0 auto;
}

/* ── Title Area ── */
.fd-header {
    text-align: center;
    padding: 24px 0 8px;
}

.fd-header h1 {
    font-size: 48px;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}

.fd-header p {
    font-size: 13px;
    color: #888;
    margin: 0;
    font-weight: 400;
    letter-spacing: 0.3px;
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
    gap: 10px;
    padding: 12px 0;
}

.fd-card {
    background: #151520;
    border: 1px solid #2a2a3a;
    border-radius: 14px;
    padding: 16px 20px;
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

.fd-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.fd-card-bank {
    font-size: 17px;
    font-weight: 700;
    color: #e0e0e0;
}

.fd-card-rate {
    font-size: 20px;
    font-weight: 700;
    color: #4ade80;
}

.fd-card-details {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.fd-card-interest {
    font-size: 13px;
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

/* ── Voice Bottom Bar ── */
.voice-bottom-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 120px;
    background: linear-gradient(180deg, transparent 0%, #0a0a0a 40%);
    z-index: 998;
    pointer-events: none;
}

/* ── Mic Button Centering ── */
div[data-testid="column"]:has(iframe) {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

iframe[title*="audio_recorder"] {
    position: fixed !important;
    bottom: 45px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    z-index: 1000 !important;
    border: none !important;
    background: #151520 !important;
    border-radius: 50% !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
    display: block !important;
    margin: 0 !important;
    width: 64px !important;
    height: 64px !important;
}

/* ── Status Text ── */
.status-text {
    position: fixed !important;
    bottom: 15px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    z-index: 1000 !important;
    text-align: center;
    color: #888;
    font-size: 12px;
    margin: 0;
    font-weight: 500;
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
<script>
if (!window.audioStopSetup) {
    window.audioStopSetup = true;
    function stopAudio() {
        if (window.currentAudio && !window.currentAudio.paused) {
            window.currentAudio.pause();
        }
        document.querySelectorAll('audio').forEach(function(a) { a.pause(); });
    }
    window.addEventListener('blur', stopAudio);
    setInterval(function() {
        if (document.activeElement && document.activeElement.tagName === 'IFRAME') {
            stopAudio();
        }
    }, 200);
}
</script>
""", unsafe_allow_html=True)

# ── State ───────────────────────────────────────────
api_key = os.environ.get("GROQ_API_KEY")
api_key_set = bool(api_key and api_key.strip() and not api_key.startswith("your_"))

if not api_key_set:
    st.warning("API key nahi milega - demo mode chal raha hai")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processing" not in st.session_state:
    st.session_state.processing = False

if "pending_audio" not in st.session_state:
    st.session_state.pending_audio = None

if "voice_key" not in st.session_state:
    st.session_state.voice_key = 1

if "booking_confirmed" not in st.session_state:
    st.session_state.booking_confirmed = False

if "booking_success" not in st.session_state:
    st.session_state.booking_success = False

if "success_audio" not in st.session_state:
    st.session_state.success_audio = None

if "selection_audio" not in st.session_state:
    st.session_state.selection_audio = None

if "mode" not in st.session_state:
    st.session_state.mode = "voice"

if "show_fd_options" not in st.session_state:
    st.session_state.show_fd_options = False

if "selected_fd" not in st.session_state:
    st.session_state.selected_fd = None

if "user_amount" not in st.session_state:
    st.session_state.user_amount = None

if "user_tenure" not in st.session_state:
    st.session_state.user_tenure = None

if "otp_generated" not in st.session_state:
    st.session_state.otp_generated = None

if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False

# ── Header ──────────────────────────────────────────
st.markdown("""
<div class="fd-header">
    <h1>संचायक</h1>
    <p>हिंदी में बोलिए, एफडी के बारे में जानिए</p>
</div>
""", unsafe_allow_html=True)

# ── Mode Toggle ─────────────────────────────────────
col_v, col_c = st.columns(2, gap="small")
with col_v:
    if st.button("बोलें", key="mode_voice", use_container_width=True):
        st.session_state.mode = "voice"
        st.rerun()
with col_c:
    if st.button("लिखें", key="mode_chat", use_container_width=True):
        st.session_state.mode = "chat"
        st.rerun()

mode = "Voice" if st.session_state.mode == "voice" else "Chat"

# ── Conversation ────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="bubble-user">आप: {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bubble-bot">{msg["content"]}</div>', unsafe_allow_html=True)

# ── Voice Mode ──────────────────────────────────────
if "Voice" in mode:
    # Initialize voice key if needed
    if "voice_key" not in st.session_state:
        st.session_state.voice_key = 0

    # Stop any playing audio
    st.markdown("""
    <audio id="stopAllAudio" style="display:none;"></audio>
    <script>
    if (window.currentAudio) {
        window.currentAudio.pause();
        window.currentAudio.currentTime = 0;
    }
    var allAudios = document.querySelectorAll('audio');
    allAudios.forEach(function(audio) {
        audio.pause();
        audio.currentTime = 0;
    });
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="voice-bottom-bar"></div>', unsafe_allow_html=True)
    
    audio_bytes = audio_recorder(
        text="",
        icon_size="2x",
        sample_rate=16000,
        pause_threshold=2.0,
        neutral_color="#ffffff",
        recording_color="#ff4444",
        key=f"voice_recorder_{st.session_state.voice_key}"
    )

    st.markdown('<div class="status-text">रिकॉर्ड करने के लिए टैप करें</div>', unsafe_allow_html=True)

    if audio_bytes and len(audio_bytes) > 1000:
        st.session_state.processing = True
        
        transcript_placeholder = "रिकॉर्डिंग..."
        st.session_state.messages.append({"role": "user", "content": transcript_placeholder})
        
        with st.spinner("सोच रही हूँ..."):
            try:
                if api_key_set:
                    transcript, advice, audio_out = run_pipeline(audio_bytes, chat_history=st.session_state.messages)
                else:
                    transcript = "Mock transcription"
                    advice = mock_fd_advice("FD query")
                    audio_out = None
                
                from hindi_numbers import extract_amount, extract_tenure
                if amt := extract_amount(transcript):
                    st.session_state.user_amount = amt
                if ten := extract_tenure(transcript):
                    st.session_state.user_tenure = ten

                st.session_state.messages[-1] = {"role": "user", "content": transcript}
                st.session_state.messages.append({"role": "assistant", "content": advice})
                st.session_state.pending_audio = audio_out
                st.session_state.voice_key += 1
                
                if any(word in advice for word in ["विकल्प", "चुनना", "चुनें", "चुनिए", "मिलेगा", "ब्याज"]):
                    st.session_state.show_fd_options = True
                
                advice_lower = advice.lower()
                if any(word in advice_lower for word in ["aadhaar", "booking", "lena hai", "chahiye hoga", "confirm kija", "आधार", "बुकिंग", "कन्फर्म"]):
                    st.session_state.booking_confirmed = True
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
        
        st.rerun()

if st.session_state.pending_audio:
    # Convert to base64 for reliable autoplay
    b64_audio = base64.b64encode(st.session_state.pending_audio).decode('utf-8')
    import time
    audio_id = f"audio_{int(time.time() * 1000)}"
    audio_html = f'''
    <audio id="{audio_id}" autoplay style="display:none;">
        <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
    </audio>
    <script>
        if (window.currentAudio) window.currentAudio.pause();
        window.currentAudio = document.getElementById("{audio_id}");
        if (window.currentAudio) window.currentAudio.play().catch(e => console.log(e));
    </script>
    '''
    st.markdown(audio_html, unsafe_allow_html=True)
    st.session_state.pending_audio = None

# ── Chat Mode ───────────────────────────────────────
elif "Chat" in mode:
    user_input = st.chat_input("हिंदी में लिखिए...")
    if user_input:
        with st.spinner("सोच रही हूँ..."):
            try:
                if api_key_set:
                    advice = get_fd_advice(user_input, chat_history=st.session_state.messages)
                else:
                    advice = mock_fd_advice(user_input)

                from hindi_numbers import extract_amount, extract_tenure
                if amt := extract_amount(user_input):
                    st.session_state.user_amount = amt
                if ten := extract_tenure(user_input):
                    st.session_state.user_tenure = ten

                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.messages.append({"role": "assistant", "content": advice})
                
                # Trigger FD options AFTER message is shown
                if any(word in advice for word in ["विकल्प", "सुझाव", "रखे", "चुनना", "चुनें", "चुनिए", "ब्याज"]):
                    st.session_state.show_fd_options = True
                
                # Check booking - AFTER message shown
                advice_lower = advice.lower()
                if any(word in advice_lower for word in ["aadhaar", "booking", "lena hai", "chahiye hoga", "confirm kija", "आधार", "बुकिंग", "कन्फर्म"]):
                    st.session_state.booking_confirmed = True
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})

        st.rerun()

# ── FD Option Cards ─────────────────────────────────
if st.session_state.show_fd_options and not st.session_state.booking_confirmed and st.session_state.user_amount is not None and st.session_state.user_tenure is not None:
    amount = st.session_state.user_amount
    tenure = st.session_state.user_tenure
    
    cards_html = '<div class="fd-cards-container">'
    
    max_rate = max(fd["rate"] for fd in FD_OPTIONS)
    
    for i, fd in enumerate(FD_OPTIONS[:3]):
        interest = round(amount * fd["rate"] / 100 * tenure)
        badge_html = '<span class="fd-card-badge">सर्वोत्तम</span>' if fd["rate"] == max_rate else ""
        
        cards_html += f'<div class="fd-card" id="fd-card-{i}"><div class="fd-card-header"><span class="fd-card-bank">{fd["bank"]}</span><span class="fd-card-rate">{fd["rate"]}%</span></div><div class="fd-card-details"><span class="fd-card-interest">अनुमानित ब्याज: ₹{interest:,} ({tenure} साल)</span>{badge_html}</div></div>'

    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)
    
    for i, fd in enumerate(FD_OPTIONS[:3]):
        if st.button(f"{fd['bank']} चुनें", key=f"select_fd_{i}", use_container_width=True):
            st.session_state.selected_fd = fd
            st.session_state.show_fd_options = False
            st.session_state.booking_confirmed = True
            selected_msg = f"आपने {fd['bank']} को चुना है ({fd['rate']}% ब्याज दर)। अब बुकिंग के लिए अपना 12-अंकों का आधार नंबर बताएं।"
            st.session_state.messages.append({"role": "assistant", "content": selected_msg})
            if api_key_set:
                with st.spinner("🤔 सोच रही हूं..."):
                    from pipeline import text_to_speech_hindi
                    audio_out = text_to_speech_hindi(selected_msg)
                    st.session_state.selection_audio = audio_out
            st.rerun()

# Play selection confirmation audio
if st.session_state.booking_confirmed and hasattr(st.session_state, 'selection_audio') and st.session_state.selection_audio:
    b64_audio = base64.b64encode(st.session_state.selection_audio).decode('utf-8')
    import time
    audio_id = f"audio_sel_{int(time.time() * 1000)}"
    audio_html = f'''
    <audio id="{audio_id}" autoplay style="display:none;">
        <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
    </audio>
    <script>
        if (window.currentAudio) window.currentAudio.pause();
        window.currentAudio = document.getElementById("{audio_id}");
        if (window.currentAudio) window.currentAudio.play().catch(e => console.log(e));
    </script>
    '''
    st.markdown(audio_html, unsafe_allow_html=True)
    st.session_state.selection_audio = None

# ── Booking Flow ─────────────────────────────────
if st.session_state.booking_confirmed and not st.session_state.booking_success:
    st.markdown("---")
    
    # Aadhar Section
    aadhaar_input = st.text_input("अपना 12-अंकों का आधार नंबर दर्ज करें:", max_chars=12, key="aadhaar_input", disabled=bool(st.session_state.otp_generated))
    
    if not st.session_state.otp_generated:
        if st.button("OTP भेजें", key="send_otp"):
            if aadhaar_input and len(aadhaar_input) == 12:
                import random
                st.session_state.otp_generated = str(random.randint(100000, 999999))
                st.rerun()
            else:
                st.error("कृपया सही 12-अंकों का आधार नंबर दर्ज करें।")
    
    # OTP Section
    if st.session_state.otp_generated:
        st.markdown(f"""
        <div style="background: #1a2e1a; border: 1px solid #2a4a2a; border-radius: 12px; padding: 16px; margin: 12px 0; text-align: center;">
            <p style="color: #888; font-size: 13px; margin-bottom: 8px;">आपका OTP है:</p>
            <h2 style="color: #4ade80; font-size: 32px; letter-spacing: 8px; margin: 0;">{st.session_state.otp_generated}</h2>
            <p style="color: #666; font-size: 12px; margin-top: 8px;">(यह केवल डेमो के लिए है)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top: 12px;"></div>', unsafe_allow_html=True)
        otp_input = st.text_input("अपना 6-अंकों का OTP दर्ज करें:", max_chars=6, key="otp_input")
        
        if st.button("OTP वेरीफाई करें", key="verify_otp"):
            if otp_input == st.session_state.otp_generated:
                st.session_state.otp_verified = True
                st.session_state.booking_success = True
                success_msg = "आपका एफडी बुकिंग कन्फर्म हो गया है! हमारी सर्विस चुनने के लिए शुक्रिया। आपको कन्फर्मेशन एसएमएस मिल जाएगा।"
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": success_msg
                })
                if api_key_set:
                    with st.spinner("🤔 सोच रही हूं..."):
                        from pipeline import text_to_speech_hindi
                        audio_out = text_to_speech_hindi(success_msg)
                        st.session_state.success_audio = audio_out
                st.session_state.otp_generated = None
                st.session_state.otp_verified = False
                st.rerun()
            elif len(otp_input) != 6:
                st.error("कृपया 6-अंकों का OTP दर्ज करें।")
            else:
                st.error("गलत OTP! कृपया सही OTP दर्ज करें।")

# Play success audio
if st.session_state.booking_success and hasattr(st.session_state, 'success_audio') and st.session_state.success_audio:
    b64_audio = base64.b64encode(st.session_state.success_audio).decode('utf-8')
    import time
    audio_id = f"audio_suc_{int(time.time() * 1000)}"
    audio_html = f'''
    <audio id="{audio_id}" autoplay style="display:none;">
        <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
    </audio>
    <script>
        if (window.currentAudio) window.currentAudio.pause();
        window.currentAudio = document.getElementById("{audio_id}");
        if (window.currentAudio) window.currentAudio.play().catch(e => console.log(e));
    </script>
    '''
    st.markdown(audio_html, unsafe_allow_html=True)
    st.session_state.success_audio = None

# ── Success Screen ─────────────────────────────────
if st.session_state.booking_success:
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <h2 style="color: #4ade80; margin-bottom: 8px;">बुकिंग कन्फर्म!</h2>
        <p style="color: #666; font-size: 14px;">कन्फर्मेशन एसएमएस भेज दिया गया</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("नया सवाल", use_container_width=True, key="new_question_success"):
        st.session_state.messages = []
        st.session_state.booking_confirmed = False
        st.session_state.booking_success = False
        st.session_state.show_fd_options = False
        st.session_state.selected_fd = None
        st.session_state.selection_audio = None
        st.session_state.otp_generated = None
        st.session_state.otp_verified = False
        st.rerun()

# ── Reset ───────────────────────────────────────────
if st.session_state.messages and not st.session_state.booking_success:
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        if st.button("नया सवाल", use_container_width=True, key="new_question_reset"):
            st.session_state.messages = []
            st.session_state.booking_confirmed = False
            st.session_state.booking_success = False
            st.session_state.show_fd_options = False
            st.session_state.selected_fd = None
            st.session_state.selection_audio = None
            st.session_state.otp_generated = None
            st.session_state.otp_verified = False
            st.rerun()