import streamlit as st
import os
from audio_recorder_streamlit import audio_recorder
from pipeline import run_pipeline, get_fd_comparison
from test_utils import mock_fd_advice
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="FD Advisor", page_icon="mic")

st.markdown("""
<style>
    .phone-frame {
        max-width: 360px;
        margin: 0 auto;
        border: 2px solid #333;
        border-radius: 20px;
        padding: 20px;
        background: #0f0f0f;
        color: #fff;
    }
    .stApp {
        background: #1a1a1a;
    }
    div.stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("FD Sahayak")
st.caption("Hindi mein boliye, FD ke baare mein janiye")

api_key = os.environ.get("GROQ_API_KEY")
api_key_set = bool(api_key and api_key.strip() and not api_key.startswith("your_"))

if not api_key_set:
    st.warning("GROQ_API_KEY not set. Using mock mode.")
    st.session_state.text_mode = True
else:
    st.session_state.text_mode = False

col1, col2 = st.columns([2, 1])
with col1:
    mode = st.radio("Mode", ["voice", "text"], horizontal=True)
with col2:
    st.markdown("")  
    st.caption("Demo" if st.session_state.text_mode else "Live")

st.markdown("---")

if mode == "voice" and not st.session_state.text_mode and api_key_set:
    st.subheader("Record apna sawaal")
    
    audio_bytes = audio_recorder(pause_threshold=2.0, sample_rate=16000)
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
        with st.spinner("Soch raha hoon..."):
            try:
                transcript, advice, audio_out = run_pipeline(audio_bytes)
                
                st.success("Ho gaya!")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**Aapne kaha:**")
                    st.info(transcript)
                with col_b:
                    st.markdown("**Salah:**")
                    st.success(advice)
                
                st.markdown("**Suniye:**")
                st.audio(audio_out, format="audio/mp3")
                
                if "Aadhaar" in advice or "aadhaar" in advice:
                    st.markdown("---")
                    st.warning("KYC ke liye Aadhaar zaroori hai")
                    aadhaar = st.text_input("Aadhaar Number")
                    if aadhaar and len(aadhaar) == 12:
                        st.button("Booking ke liye aage badhein")
                        
            except Exception as e:
                st.error(f"Kuch galat ho gaya: {e}")

else:
    st.subheader("Type apna sawaal")
    
    user_input = st.text_input("Question", placeholder="Mujhe 50,000 FD mein rakhne hain...")
    
    if st.button("Send") and user_input:
        with st.spinner("Soch raha hoon..."):
            try:
                if api_key_set:
                    advice = get_fd_comparison(user_input)
                else:
                    advice = mock_fd_advice(user_input)
                st.success("Ho gaya!")
                st.markdown(f"**Salah:** {advice}")
            except Exception as e:
                st.error(f"Kuch galat ho gaya: {e}")