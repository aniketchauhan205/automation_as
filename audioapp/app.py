import os
import re
import uuid

import streamlit as st

from audio_utils import analyze_audio
from db import (
    RECORDINGS_DIR,
    ensure_audio_table,
    fetch_recent_submissions,
    get_connection,
    get_or_create_person,
    insert_submission,
)

st.set_page_config(page_title="Audio Submission", page_icon=":microphone:")

ensure_audio_table()

st.title("Audio Submission App")

tab1, tab2 = st.tabs(["📝 Submit Audio", "🎵 View Recordings"])

with tab1:
    st.subheader("Submit New Audio")
    st.caption("Record or upload a short audio clip. It gets stored and logged to the database.")

    with st.form("submission_form", clear_on_submit=False):
        name = st.text_input("Full name")
        phone = st.text_input("Phone number")

        st.write("**Record audio**")
        recorded_audio = st.audio_input("Record in browser")

        st.write("**...or upload a file**")
        uploaded_file = st.file_uploader(
            "Upload audio", type=["wav", "mp3", "ogg", "flac", "aiff", "au"]
        )

        submitted = st.form_submit_button("Submit")

    if submitted:
        errors = []
        if not name.strip():
            errors.append("Name is required.")
        if not re.match(r"^\+?[0-9()\-\s]{7,15}$", phone.strip()):
            errors.append("Enter a valid phone number.")

        audio_source = None
        audio_bytes = None
        original_name = None

        if recorded_audio is not None:
            audio_source = "recorded"
            audio_bytes = recorded_audio.getvalue()
            original_name = "recording.wav"
        elif uploaded_file is not None:
            audio_source = "uploaded"
            audio_bytes = uploaded_file.getvalue()
            original_name = uploaded_file.name

        if audio_bytes is None:
            errors.append("Record audio or upload a file before submitting.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            ext = os.path.splitext(original_name)[1] or ".wav"
            safe_filename = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(RECORDINGS_DIR, safe_filename)

            with open(filepath, "wb") as f:
                f.write(audio_bytes)

            try:
                metrics = analyze_audio(filepath)
            except Exception as e:
                os.remove(filepath)
                st.error(f"Could not analyze this audio file: {e}")
            else:
                person_id = get_or_create_person(name.strip(), phone.strip())
                submission_id = insert_submission(
                    person_id=person_id,
                    name=name.strip(),
                    phone=phone.strip(),
                    filename=safe_filename,
                    filepath=filepath,
                    source=audio_source,
                    metrics=metrics,
                )

                st.success(f"Submitted. Record #{submission_id} saved for person #{person_id}.")

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Duration", f"{metrics['duration_sec']} s")
                c2.metric("Sample rate", f"{metrics['sample_rate_khz']} kHz")
                c3.metric("Bitrate", f"{metrics['bitrate_kbps']} kbps")
                c4.metric("Loudness", f"{metrics['loudness_dbfs']} dBFS")

                st.write(
                    f"Rough quality estimate: **{metrics['quality_label']}** "
                    f"(noise floor {metrics['noise_floor_db']} dB, "
                    f"estimated SNR {metrics['snr_estimate_db']} dB)"
                )

                st.audio(audio_bytes)

    st.divider()
    st.subheader("Recent submissions")

    columns, rows = fetch_recent_submissions()
    if rows:
        st.dataframe([dict(zip(columns, r)) for r in rows], use_container_width=True)
    else:
        st.caption("No submissions yet.")

with tab2:
    st.subheader("All Recordings")
    
    columns, rows = fetch_recent_submissions(limit=100)
    
    if not rows:
        st.info("No recordings yet.")
    else:
        st.write(f"**Total recordings: {len(rows)}**")
        st.divider()
        
        for row in rows:
            submission_id, name, phone, source, submitted_at, duration, sample_rate, bitrate, loudness, snr, quality = row
            
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{name}** | {phone}")
                    st.caption(f"Submission #{submission_id} • {submitted_at}")
                
                with col2:
                    st.metric("Duration", f"{duration}s")
                
                # Audio metrics in columns
                mc1, mc2, mc3, mc4, mc5 = st.columns(5)
                with mc1:
                    st.metric("Sample Rate", f"{sample_rate} kHz")
                with mc2:
                    st.metric("Bitrate", f"{bitrate} kbps")
                with mc3:
                    st.metric("Loudness", f"{loudness} dBFS")
                with mc4:
                    st.metric("SNR", f"{snr} dB")
                with mc5:
                    st.metric("Quality", quality)
                
                st.caption(f"Source: {source}")
                
                # Try to load and play the audio file
                try:
                    # Get filepath from database query - need to fetch it
                    from db import get_connection
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT filepath FROM audio_submissions WHERE submission_id = ?", (submission_id,))
                    filepath_row = cursor.fetchone()
                    conn.close()
                    
                    if filepath_row and os.path.exists(filepath_row[0]):
                        with open(filepath_row[0], "rb") as audio_file:
                            audio_bytes = audio_file.read()
                            st.audio(audio_bytes, format="audio/wav")
                    else:
                        st.warning("Audio file not found")
                except Exception as e:
                    st.warning(f"Could not load audio: {e}")
