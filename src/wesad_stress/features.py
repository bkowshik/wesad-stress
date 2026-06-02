"""Feature extraction from WESAD chest signals.

First-pass, hand-rolled feature engineering over the RespiBAN chest array
(700 Hz) documented in ``docs/schema.md``. The output is a tidy table — one
row per analysis window, one column per feature — written to
``data/processed/features.parquet`` and consumed by the modelling notebooks.

Windowing follows the WESAD convention from Schmidt et al. (ICMI 2018,
Section 5.1): 60-second windows with a 30-second step (50 % overlap). Each
window inherits the majority label across its samples; windows whose majority
label is a transient/recovery code (0, 5, 6, 7) are dropped, leaving the four
condition classes (1 baseline, 2 stress, 3 amusement, 4 meditation).

Only chest modalities are used here. Wrist signals sit on their own sampling
grids (4–64 Hz) and fusing them is a separate preprocessing decision — see the
schema. Everything in this module operates on the 700 Hz chest grid alone.

Run as a module to build the full table::

    python -m wesad_stress.features

References
----------
Schmidt et al., *Introducing WESAD, a Multimodal Dataset for Wearable Stress
and Affect Detection*, ICMI 2018. https://dl.acm.org/doi/10.1145/3242969.3242985
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal

from .data import VALID_SUBJECTS, load_wesad

# --- Constants ---------------------------------------------------------------

CHEST_FS = 700  # Hz — RespiBAN chest sampling rate (verified by shape in 00).

WINDOW_S = 60  # Window length in seconds (Schmidt et al. §5.1).
STEP_S = 30  # Step between window starts in seconds (50 % overlap).
WINDOW_N = WINDOW_S * CHEST_FS  # 42_000 samples.
STEP_N = STEP_S * CHEST_FS  # 21_000 samples.

# Condition codes we keep. Transient/recovery codes (0, 5, 6, 7) are dropped.
CONDITION_LABELS = {1: "baseline", 2: "stress", 3: "amusement", 4: "meditation"}

# Minimum fraction of a window that must carry the majority label for the
# window to be accepted. Windows straddling two protocol blocks are mostly
# one label; requiring a clear majority keeps transition-contaminated windows
# out without discarding the legitimately homogeneous ones.
PURITY_THRESHOLD = 0.75

PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"
DEFAULT_OUTPUT = PROCESSED_DIR / "features.parquet"


# --- Signal helpers ----------------------------------------------------------


def _butter_filter(
    x: np.ndarray, cutoff, fs: int, btype: str, order: int = 4
) -> np.ndarray:
    """Zero-phase Butterworth filter (``filtfilt``) over a 1-D signal."""
    nyq = 0.5 * fs
    wn = np.asarray(cutoff, dtype=float) / nyq
    sos = signal.butter(order, wn, btype=btype, output="sos")
    return signal.sosfiltfilt(sos, x)


def _detect_r_peaks(ecg: np.ndarray, fs: int = CHEST_FS) -> np.ndarray:
    """Detect R-peak sample indices with a Pan–Tompkins-style pipeline.

    Bandpass (5–15 Hz) → derivative → square → moving-window integration →
    adaptive thresholding. Hand-rolled rather than pulled from a library so the
    dependency surface stays small and the steps are auditable; it is a
    first-pass detector, not a clinical-grade one.
    """
    # Bandpass to the QRS energy band.
    filtered = _butter_filter(ecg, [5, 15], fs, btype="bandpass", order=2)

    # Derivative emphasises the steep QRS slope.
    derivative = np.ediff1d(filtered, to_begin=0.0)

    # Square to make everything positive and amplify large slopes.
    squared = derivative**2

    # Moving-window integration over ~150 ms smooths into single QRS bumps.
    win = max(1, int(0.150 * fs))
    integrated = np.convolve(squared, np.ones(win) / win, mode="same")

    # Adaptive threshold: candidate peaks above a fraction of the running
    # signal level, separated by a physiological refractory period (200 ms,
    # i.e. an upper bound of 300 bpm).
    threshold = 0.3 * np.mean(integrated)
    min_distance = int(0.200 * fs)
    peaks, _ = signal.find_peaks(integrated, height=threshold, distance=min_distance)
    return peaks


def _hrv_features(ecg: np.ndarray, fs: int = CHEST_FS) -> dict[str, float]:
    """Heart-rate-variability features from a chest-ECG window.

    Time domain: RMSSD, SDNN, pNN50, plus mean heart rate. Frequency domain:
    LF/HF ratio from a Welch PSD of the evenly-resampled RR tachogram (LF
    0.04–0.15 Hz, HF 0.15–0.40 Hz — standard HRV bands).
    """
    peaks = _detect_r_peaks(ecg, fs)
    nan = {
        "hrv_rmssd": np.nan,
        "hrv_sdnn": np.nan,
        "hrv_pnn50": np.nan,
        "hrv_mean_hr": np.nan,
        "hrv_lf_hf": np.nan,
    }
    if peaks.size < 4:
        return nan

    # RR intervals in milliseconds.
    rr = np.diff(peaks) / fs * 1000.0

    # Physiological plausibility filter: drop intervals outside 300–2000 ms
    # (30–200 bpm). Detector glitches otherwise dominate RMSSD.
    rr = rr[(rr >= 300) & (rr <= 2000)]
    if rr.size < 4:
        return nan

    diff_rr = np.diff(rr)
    rmssd = float(np.sqrt(np.mean(diff_rr**2)))
    sdnn = float(np.std(rr, ddof=1))
    pnn50 = float(np.mean(np.abs(diff_rr) > 50.0) * 100.0)
    mean_hr = float(60000.0 / np.mean(rr))

    lf_hf = _lf_hf_ratio(rr)

    return {
        "hrv_rmssd": rmssd,
        "hrv_sdnn": sdnn,
        "hrv_pnn50": pnn50,
        "hrv_mean_hr": mean_hr,
        "hrv_lf_hf": lf_hf,
    }


def _lf_hf_ratio(rr: np.ndarray) -> float:
    """LF/HF power ratio from an RR-interval series (milliseconds)."""
    # Cumulative time of each beat, then resample the tachogram onto an even
    # 4 Hz grid so a PSD is well defined.
    t_beats = np.cumsum(rr) / 1000.0  # seconds
    if t_beats[-1] - t_beats[0] < 20.0:
        # Too short for a stable LF estimate (LF period ~6–25 s).
        return np.nan
    fs_rr = 4.0
    t_even = np.arange(t_beats[0], t_beats[-1], 1.0 / fs_rr)
    if t_even.size < 16:
        return np.nan
    rr_even = np.interp(t_even, t_beats, rr)
    rr_even = rr_even - np.mean(rr_even)

    nperseg = min(256, rr_even.size)
    freqs, psd = signal.welch(rr_even, fs=fs_rr, nperseg=nperseg)
    lf = np.trapz(psd[(freqs >= 0.04) & (freqs < 0.15)])
    hf = np.trapz(psd[(freqs >= 0.15) & (freqs < 0.40)])
    if hf <= 0:
        return np.nan
    return float(lf / hf)


def _eda_features(eda: np.ndarray, fs: int = CHEST_FS) -> dict[str, float]:
    """Electrodermal-activity features with a tonic/phasic split.

    Tonic (skin-conductance level) is the low-pass component below 0.05 Hz;
    the phasic (skin-conductance-response) component is the residual. This is
    the cheap filter-based decomposition rather than a convex model (cvxEDA);
    it captures the level-vs-response distinction that matters for stress
    without the extra dependency.
    """
    eda = np.asarray(eda, dtype=float)
    tonic = _butter_filter(eda, 0.05, fs, btype="lowpass", order=2)
    phasic = eda - tonic

    # Count SCR peaks in the phasic component: prominence in microsiemens,
    # separated by at least 1 s (SCRs don't recur faster than ~1 Hz).
    scr_peaks, _ = signal.find_peaks(
        phasic, prominence=0.01, distance=int(1.0 * fs)
    )

    # Tonic slope over the window (µS per second) — rising SCL tracks arousal.
    t = np.arange(tonic.size) / fs
    slope = float(np.polyfit(t, tonic, 1)[0]) if tonic.size > 1 else np.nan

    return {
        "eda_tonic_mean": float(np.mean(tonic)),
        "eda_tonic_slope": slope,
        "eda_phasic_mean": float(np.mean(phasic)),
        "eda_phasic_std": float(np.std(phasic)),
        "eda_scr_count": float(scr_peaks.size),
    }


def _emg_features(emg: np.ndarray, fs: int = CHEST_FS) -> dict[str, float]:
    """EMG envelope and spectral features from the trapezius channel.

    Envelope: rectify then low-pass at 5 Hz. Spectral: total band power and
    median frequency from a Welch PSD over 5–250 Hz (the muscle-activity band
    below the chest Nyquist).
    """
    emg = np.asarray(emg, dtype=float)
    rectified = np.abs(emg - np.mean(emg))
    envelope = _butter_filter(rectified, 5.0, fs, btype="lowpass", order=2)

    nperseg = min(2048, emg.size)
    freqs, psd = signal.welch(emg - np.mean(emg), fs=fs, nperseg=nperseg)
    band = (freqs >= 5) & (freqs <= 250)
    band_power = float(np.trapz(psd[band], freqs[band]))
    # Median frequency: where cumulative band power crosses half its total.
    if band_power > 0:
        cum = np.cumsum(psd[band])
        median_freq = float(freqs[band][np.searchsorted(cum, cum[-1] / 2.0)])
    else:
        median_freq = np.nan

    return {
        "emg_env_mean": float(np.mean(envelope)),
        "emg_env_std": float(np.std(envelope)),
        "emg_band_power": band_power,
        "emg_median_freq": median_freq,
    }


def _resp_features(resp: np.ndarray, fs: int = CHEST_FS) -> dict[str, float]:
    """Respiration rate and breath-to-breath variability.

    Bandpass to the breathing band (0.1–0.5 Hz, i.e. 6–30 breaths/min), detect
    inhalation peaks, and summarise rate plus inter-breath-interval spread.
    """
    resp = np.asarray(resp, dtype=float)
    filtered = _butter_filter(resp, [0.1, 0.5], fs, btype="bandpass", order=2)

    # Breaths can't recur faster than ~0.5 Hz → min 2 s between peaks.
    peaks, _ = signal.find_peaks(filtered, distance=int(2.0 * fs))
    nan = {"resp_rate": np.nan, "resp_ibi_std": np.nan}
    if peaks.size < 3:
        return nan

    ibi = np.diff(peaks) / fs  # inter-breath intervals, seconds
    resp_rate = float(60.0 / np.mean(ibi))  # breaths per minute
    ibi_std = float(np.std(ibi))
    return {"resp_rate": resp_rate, "resp_ibi_std": ibi_std}


def _acc_features(acc: np.ndarray) -> dict[str, float]:
    """Chest-accelerometer movement features from the 3-axis magnitude.

    Magnitude is rotation-invariant, so motion energy is summarised without
    committing to a body-axis convention. Mean/std capture activity level;
    the standard deviation of the magnitude is the simplest motion-intensity
    proxy.
    """
    acc = np.asarray(acc, dtype=float)
    magnitude = np.sqrt(np.sum(acc**2, axis=1))
    return {
        "acc_mag_mean": float(np.mean(magnitude)),
        "acc_mag_std": float(np.std(magnitude)),
        "acc_mag_max": float(np.max(magnitude)),
    }


# --- Windowing + assembly ----------------------------------------------------


def _squeeze(arr: np.ndarray) -> np.ndarray:
    """Collapse a chest modality to 1-D (modalities are stored as ``(N, 1)``)."""
    arr = np.asarray(arr)
    return arr[:, 0] if arr.ndim == 2 and arr.shape[1] == 1 else arr


def _window_label(labels: np.ndarray) -> tuple[int, float]:
    """Majority label of a window and the fraction of samples carrying it."""
    values, counts = np.unique(labels, return_counts=True)
    idx = int(np.argmax(counts))
    return int(values[idx]), float(counts[idx] / labels.size)


def extract_subject_features(subject_id: int) -> pd.DataFrame:
    """Extract the windowed feature table for one subject.

    Returns one row per accepted 60 s / 30 s-step window, with the feature
    columns plus ``subject``, ``window_start_s``, ``window_end_s``, ``label``,
    and ``label_name``. Windows whose majority label is a transient/recovery
    code, or that fail the purity threshold, are dropped.
    """
    data = load_wesad(subject_id)
    chest = data["signal"]["chest"]
    labels = np.asarray(data["label"]).reshape(-1)

    ecg = _squeeze(chest["ECG"])
    eda = _squeeze(chest["EDA"])
    emg = _squeeze(chest["EMG"])
    resp = _squeeze(chest["Resp"])
    acc = np.asarray(chest["ACC"])  # (N, 3)

    n = labels.size
    rows: list[dict] = []

    for start in range(0, n - WINDOW_N + 1, STEP_N):
        end = start + WINDOW_N
        win_labels = labels[start:end]
        label, purity = _window_label(win_labels)

        if label not in CONDITION_LABELS or purity < PURITY_THRESHOLD:
            continue

        row: dict[str, float | int | str] = {
            "subject": f"S{subject_id}",
            "window_start_s": start / CHEST_FS,
            "window_end_s": end / CHEST_FS,
            "label": label,
            "label_name": CONDITION_LABELS[label],
        }
        row.update(_hrv_features(ecg[start:end]))
        row.update(_eda_features(eda[start:end]))
        row.update(_emg_features(emg[start:end]))
        row.update(_resp_features(resp[start:end]))
        row.update(_acc_features(acc[start:end]))
        rows.append(row)

    return pd.DataFrame(rows)


def build_feature_table(
    subjects: list[int] | None = None, output: Path = DEFAULT_OUTPUT
) -> pd.DataFrame:
    """Build and persist the feature table across subjects.

    Parameters
    ----------
    subjects
        Subject IDs to process; defaults to :data:`VALID_SUBJECTS`.
    output
        Destination parquet path. The parent directory is created if needed.
        The ``data/processed/`` tree is gitignored — the parquet is a
        derived artifact, reproducible from the raw pickles via this module.
    """
    subjects = subjects or VALID_SUBJECTS
    frames = []
    for sid in subjects:
        df = extract_subject_features(sid)
        print(f"S{sid}: {len(df)} windows")
        frames.append(df)

    table = pd.concat(frames, ignore_index=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(output, index=False)
    print(f"\nWrote {len(table)} rows × {table.shape[1]} cols to {output}")
    return table


if __name__ == "__main__":
    build_feature_table()
