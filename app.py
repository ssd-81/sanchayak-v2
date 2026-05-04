import streamlit as st
from audio_recorder_streamlit import audio_recorder
from pipeline import run_pipeline, get_fd_comparison

st.set_page_config(page_title="FD Advisor", page_icon="mic")
st.title("FD Sahayak — अपना सवाल पूछें")
st.caption("Hindi mein boliye, FD ke baare mein janiye")

st.markdown("---")
st.subheader("Record karna shuru karein")

audio_bytes = audio_recorder(pause_threshold=2.0, sample_rate=16000)

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")

    with st.spinner("Soch raha hoon..."):
        transcript, advice, audio_out = run_pipeline(audio_bytes)

    st.success("Done")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Aapne kaha:**")
        st.info(transcript)
    with col2:
        st.markdown("**Salah:**")
        st.success(advice)

    st.markdown("**Suniye:**")
    st.audio(audio_out, format="audio/mp3")

if advice and "Aadhaar" in advice:
    st.markdown("---")
    st.warning("KYC Handoff")
    st.text_input("Aadhaar Number (Demo only — not stored)")
    st.button("Booking shuru karein →")