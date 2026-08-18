"""Audio analysis helpers: duration, sample rate, bitrate, loudness, rough noise estimate."""

import os
import numpy as np
import soundfile as sf


def _to_mono(data: np.ndarray) -> np.ndarray:
    if data.ndim == 1:
        return data
    return data.mean(axis=1)


def _frame_rms_db(mono: np.ndarray, sr: int, frame_ms: int = 20) -> np.ndarray:
    frame_len = max(1, int(sr * frame_ms / 1000))
    n_frames = len(mono) // frame_len
    if n_frames == 0:
        rms = np.sqrt(np.mean(mono ** 2)) if len(mono) else 0.0
        return np.array([20 * np.log10(rms) if rms > 1e-9 else -120.0])

    trimmed = mono[: n_frames * frame_len]
    frames = trimmed.reshape(n_frames, frame_len)
    rms = np.sqrt(np.mean(frames ** 2, axis=1))
    rms = np.clip(rms, 1e-9, None)
    return 20 * np.log10(rms)


def analyze_audio(file_path: str) -> dict:
    """Return duration, sample rate, bitrate, loudness and a rough noise/quality estimate."""

    with sf.SoundFile(file_path) as f:
        sr = f.samplerate
        channels = f.channels
        frames = len(f)

    duration_sec = frames / sr if sr else 0.0

    data, sr = sf.read(file_path, dtype="float32", always_2d=False)
    mono = _to_mono(np.asarray(data))

    rms = np.sqrt(np.mean(mono ** 2)) if len(mono) else 0.0
    loudness_dbfs = 20 * np.log10(rms) if rms > 1e-9 else -120.0

    file_size_bytes = os.path.getsize(file_path)
    bitrate_kbps = (file_size_bytes * 8 / duration_sec / 1000) if duration_sec > 0 else 0.0

    frame_db = _frame_rms_db(mono, sr)
    noise_floor_db = float(np.percentile(frame_db, 10))
    peak_level_db = float(np.percentile(frame_db, 95))
    snr_estimate_db = peak_level_db - noise_floor_db

    if snr_estimate_db >= 25:
        quality_label = "Good"
    elif snr_estimate_db >= 15:
        quality_label = "Fair"
    else:
        quality_label = "Poor / noisy"

    return {
        "duration_sec": round(duration_sec, 2),
        "sample_rate_hz": sr,
        "sample_rate_khz": round(sr / 1000, 2),
        "channels": channels,
        "bitrate_kbps": round(bitrate_kbps, 1),
        "loudness_dbfs": round(loudness_dbfs, 1),
        "noise_floor_db": round(noise_floor_db, 1),
        "snr_estimate_db": round(snr_estimate_db, 1),
        "quality_label": quality_label,
    }
