import os
import re
import uuid

import streamlit as st

from audio_utils import analyze_audio
from db import (
    RECORDINGS_DIR,
    ensure_audio_table,
    fetch_recent_submissions,
    get_or_create_person,
    insert_submission,
)

st.set_page_config(page_title="Audio Submission", page_icon=":microphone:")

ensure_audio_table()

st.title("Audio Submission")
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
