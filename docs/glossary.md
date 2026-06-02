# Glossary

Plain-language definitions for the signals and terms used across this repo. The raw-data contract lives in [`schema.md`](./schema.md) and the derived feature columns in [`features.md`](./features.md); this file is the place to decode what a name actually means.

## Signals (raw modalities)

Covers the union of chest (RespiBAN) and wrist (Empatica E4) sensors — several appear on both devices. Definitions follow Schmidt et al. §3 and the RespiBAN / Empatica E4 datasheets.

- **BVP — blood volume pulse:** optical (photoplethysmography) measure of blood-volume changes in the skin's microvasculature with each heartbeat; gives pulse rate and inter-beat intervals. Wrist only.
- **ECG — electrocardiogram:** electrical activity of the heart measured via skin electrodes; the clean source for heart rate and heart-rate variability. Chest only.
- **EDA — electrodermal activity:** skin conductance driven by sweat-gland activity (also called galvanic skin response); a direct proxy for sympathetic ("fight or flight") arousal. Both devices.
- **EMG — electromyogram:** electrical activity produced by muscle contraction; here, muscle tension at the trapezius. Chest only.
- **Resp — respiration:** chest/abdomen expansion measured by a stretch belt; yields breathing rate and depth/variability. Chest only.
- **Temp — body temperature:** skin temperature at the sensor site; shifts slowly with thermoregulation and stress. Both devices.
- **ACC — three-axis acceleration:** motion along x/y/z from an accelerometer; captures body movement, activity level, and posture. Both devices.

## Heart-rate variability (HRV) terms

HRV is computed from the **RR interval** series — the time between consecutive R-peaks (heartbeats) in the ECG. The terms below are the standard time- and frequency-domain summaries; they map to the `hrv_*` columns in [`features.md`](./features.md).

- **R-peak:** the tall spike of each heartbeat in the ECG (the "R" of the QRS complex); detected here with a **Pan–Tompkins**-style pipeline (bandpass → derivative → square → moving-window integration → adaptive threshold).
- **RR interval:** milliseconds between successive R-peaks. The inverse of heart rate; its beat-to-beat fluctuation is what HRV quantifies.
- **RMSSD:** root-mean-square of successive RR-interval differences (ms); the standard short-term HRV index, tracking parasympathetic ("rest and digest") tone. Falls under stress.
- **SDNN:** standard deviation of RR intervals (ms); overall variability across the window, reflecting both branches of the autonomic nervous system.
- **pNN50:** percentage of successive RR differences greater than 50 ms; another parasympathetic marker, correlated with RMSSD.
- **Mean HR:** mean heart rate (beats per minute) over the window, derived from the average RR interval. Rises under stress.
- **LF / HF ratio:** ratio of low-frequency (0.04–0.15 Hz) to high-frequency (0.15–0.40 Hz) power in the RR series; a rough index of sympatho-vagal balance, with higher values leaning sympathetic. HF tracks breathing; LF mixes both branches.

## EDA terms

The electrodermal signal is split into a slow background level and fast responses; these map to the `eda_*` columns.

- **Tonic / SCL (skin-conductance level):** the slowly drifting baseline of the EDA signal; here the low-pass component below 0.05 Hz. Rising SCL tracks sustained arousal.
- **Phasic / SCR (skin-conductance response):** the fast residual riding on top of the tonic level; discrete SCR peaks mark moments of momentary arousal (a startle, a stressor).

## Other feature terms

Terms behind the remaining EMG, respiration, accelerometer, and shared signal-processing columns.

- **EMG envelope:** the smoothed outline of muscle-activity amplitude — rectify the EMG, then low-pass — summarising tension level rather than individual spikes.
- **Median frequency:** the frequency that splits a signal's power spectrum into two equal halves; an EMG fatigue/activation marker.
- **Respiration rate:** breaths per minute, from the spacing of inhalation peaks in the respiration belt signal.
- **IBI (inter-breath interval):** seconds between consecutive breaths; its spread is a breathing-regularity measure (the respiratory analogue of the RR interval).
- **ACC magnitude:** the rotation-invariant length of the 3-axis acceleration vector, √(x²+y²+z²); a single motion-intensity number that ignores body orientation.
- **Acceleration-based context recognition:** using the accelerometer to infer the wearer's physical activity or situational context — sitting, standing, walking, running, and the like — rather than their affective state. It matters for stress detection because movement drives the same peripheral signals as arousal does (a brisk walk raises heart rate just as stress does), so knowing the motion context lets a model tell "aroused because stressed" apart from "aroused because moving," and down-weight or discard motion-contaminated windows. In WESAD the chest and wrist ACC channels are what make this possible; in the Schmidt et al. study the accelerometer is used partly as this kind of context/activity signal, not only as a feature.
- **Window:** a fixed-length slice of signal (here 60 s, stepped by 30 s) over which one row of features is computed — see [`features.md`](./features.md) for the windowing rules.
- **PSD / Welch:** power spectral density — how a signal's variance distributes across frequency; estimated with Welch's method (average of windowed segment spectra). Underlies the LF/HF and EMG-spectral features.
