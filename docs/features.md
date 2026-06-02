# Features

Contract for the windowed feature table built from the raw WESAD signals documented in [`schema.md`](./schema.md). The table is produced by [`src/wesad_stress/features.py`](../src/wesad_stress/features.py) and written to `data/processed/features.parquet` (gitignored — a derived artifact, reproducible from the raw pickles via `python -m wesad_stress.features`). This file is the contract the modelling notebooks read against; unlike `schema.md`, which pins a fixed external dataset, this one tracks the code and changes whenever the feature set does.

The 19 features below are a deliberate first-pass subset of the much larger catalogue the WESAD paper used — the full Table 1 list is reproduced in [`wesad-paper-features.md`](./wesad-paper-features.md), which is the reference to measure our coverage against as the feature set grows.

## Windowing

Chest signals are sliced into **60-second windows with a 30-second step** (50 % overlap), the convention from Schmidt et al. §5.1. At 700 Hz that is 42 000 samples per window, 21 000 between window starts.

Each window inherits the **majority label** across its samples. A window is kept only if (a) its majority label is one of the four condition codes (1 baseline, 2 stress, 3 amusement, 4 meditation) and (b) the majority label covers at least **75 %** of the window (`PURITY_THRESHOLD`). Condition (a) drops windows dominated by transient/recovery codes (0, 5, 6, 7 — roughly half of each recording); condition (b) keeps windows straddling a protocol boundary out of the table. The result is ~95 windows per subject, **1 422 rows across the 15 subjects**.

Only chest modalities feed the features. Wrist signals sit on their own 4–64 Hz grids; fusing them is a separate preprocessing decision and is out of scope for this first pass.

## Row identity

| Column | Type | Meaning |
|---|---|---|
| `subject` | str | `S2`–`S17` |
| `window_start_s` | float | Window start, seconds from recording start |
| `window_end_s` | float | Window end, seconds (always `start + 60`) |
| `label` | int | Majority condition code (1–4) |
| `label_name` | str | `baseline` / `stress` / `amusement` / `meditation` |

## Feature columns

19 features, all computed on the 700 Hz chest grid. HRV uses a hand-rolled Pan–Tompkins-style R-peak detector (bandpass → derivative → square → moving-window integration → adaptive threshold); it is a first-pass detector, so absolute RR-derived magnitudes carry detector noise even though the between-condition ordering is clean. EDA is split into tonic/phasic by a 0.05 Hz low-pass filter rather than a convex model.

| Column | Source | What it measures |
|---|---|---|
| `hrv_rmssd` | ECG | Root-mean-square of successive RR differences (ms) — parasympathetic tone |
| `hrv_sdnn` | ECG | Std. dev. of RR intervals (ms) — overall HRV |
| `hrv_pnn50` | ECG | % of successive RR diffs > 50 ms |
| `hrv_mean_hr` | ECG | Mean heart rate (bpm) |
| `hrv_lf_hf` | ECG | LF (0.04–0.15 Hz) / HF (0.15–0.40 Hz) power ratio from the Welch PSD of the resampled RR tachogram — sympatho-vagal balance |
| `eda_tonic_mean` | EDA | Mean skin-conductance level (µS), low-pass < 0.05 Hz |
| `eda_tonic_slope` | EDA | Linear trend of the tonic component (µS/s) |
| `eda_phasic_mean` | EDA | Mean of the phasic residual (µS) |
| `eda_phasic_std` | EDA | Std. dev. of the phasic residual (µS) |
| `eda_scr_count` | EDA | Number of skin-conductance-response peaks in the window |
| `emg_env_mean` | EMG | Mean of the rectified, 5 Hz low-pass envelope |
| `emg_env_std` | EMG | Std. dev. of the envelope |
| `emg_band_power` | EMG | Integrated PSD power, 5–250 Hz |
| `emg_median_freq` | EMG | Median frequency of the 5–250 Hz band (Hz) |
| `resp_rate` | Resp | Breathing rate (breaths/min) from inhalation-peak intervals |
| `resp_ibi_std` | Resp | Std. dev. of inter-breath intervals (s) |
| `acc_mag_mean` | ACC | Mean of the 3-axis acceleration magnitude (g) |
| `acc_mag_std` | ACC | Std. dev. of the magnitude — motion intensity |
| `acc_mag_max` | ACC | Peak magnitude in the window (g) |

Cohort-level medians move in the physiologically expected directions: stress shows the highest mean heart rate (~91 vs ~73 bpm baseline), the lowest RMSSD, and the highest tonic EDA; meditation shows the slowest breathing (~12 breaths/min) and the highest RMSSD. These are face-validity checks on the extraction, not modelling results.
