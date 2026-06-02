# WESAD paper feature catalogue

The full feature set listed in Table 1 of Schmidt et al. (ICMI 2018), reproduced here for reference. This is the catalogue the paper's classifiers drew from across all sensor modalities — it is *not* the set this repo currently computes. What we actually extract is the smaller, hand-rolled subset documented in [`features.md`](./features.md); term definitions live in [`glossary.md`](./glossary.md) and the raw signals in [`schema.md`](./schema.md). Keep this file as the "what the paper did" baseline to measure our coverage against.

Notation follows the paper: subscripts name the modality, $i$ indexes an axis or a per-channel computation, $j$ indexes a frequency component, and $\partial$ denotes a slope. Several rows expand into many columns once per-axis and per-band repetition is counted (e.g. the EMG and HRV spectral features), so the catalogue is larger than the row count suggests.

## Three-axis acceleration (ACC)

Motion and physical-activity features.

| Symbol | Meaning |
|---|---|
| $\mu_{ACC,i},\ \sigma_{ACC,i}$ | Mean and standard deviation, per axis (x, y, z) and for the combined 3D magnitude |
| $\lVert \int ACC,i \rVert$ | Absolute integral, per individual axis and for the combined 3D axes |
| $f_{peakACC,j}$ | Peak frequency, per individual axis |

## Electrocardiogram (ECG) and blood volume pulse (BVP)

Heart-related features; ECG on the chest, BVP on the wrist.

| Symbol | Meaning |
|---|---|
| $\mu_{HR},\ \sigma_{HR}$ | Mean and standard deviation of heart rate |
| $\mu_{HRV},\ \sigma_{HRV}$ | Mean and standard deviation of heart-rate variability |
| NN50, pNN50 | Number and percentage of successive HRV intervals differing by more than 50 ms |
| TINN | Triangular interpolation of the NN-interval histogram — a geometric HRV measure |
| rmsHRV | Root mean square of the HRV (RMSSD) |
| $f_{xHRV}$ | Spectral energy in four bands: ultra-low (ULF), low (LF), high (HF), ultra-high (UHF) |
| $f_{LF/HF\,HRV}$ | Ratio of energy in the low- vs high-frequency components |
| $\sum f_x$ | Sum of all frequency components across the ULF–HF range |
| $rel\ f_x$ | Relative power of specific frequency components |
| $LF_{norm},\ HF_{norm}$ | Normalised low- and high-frequency components |

## Electrodermal activity (EDA)

Skin electrical characteristics, sensitive to arousal.

| Symbol | Meaning |
|---|---|
| $\mu_{EDA},\ \sigma_{EDA}$ | Mean and standard deviation of the overall EDA signal |
| $min_{EDA},\ max_{EDA}$ | Minimum and maximum recorded values |
| $\partial EDA,\ range_{EDA}$ | Slope and dynamic range of the EDA signal |
| $\mu_{SCL},\ \sigma_{SCL},\ \sigma_{SCR}$ | Mean and standard deviation of the tonic (SCL) component, and standard deviation of the phasic (SCR) component |
| $corr(SCL, t)$ | Correlation between skin-conductance level and time |
| \#SCR | Total number of identified skin-conductance-response segments |
| $\sum Amp_{SCR},\ \sum t_{SCR}$ | Sum of SCR startle magnitudes and sum of their response durations |
| $\int SCR$ | Area under the curve for identified SCR segments |

## Electromyogram (EMG)

Muscle electrical-activity features (trapezius, chest device).

| Symbol | Meaning |
|---|---|
| $\mu_{EMG},\ \sigma_{EMG}$ | Mean and standard deviation of the EMG signal |
| $range_{EMG}$ | Dynamic range of muscle activity |
| $\lVert \int EMG \rVert$ | Absolute integral of the signal |
| $\tilde{\pi}_{EMG}$ | Median value of the EMG signal |
| $P_{10\,EMG},\ P_{90\,EMG}$ | 10th and 90th percentiles of the signal |
| $\mu_{fEMG},\ \tilde{f}_{EMG},\ f_{peakEMG}$ | Mean, median, and peak frequency of the muscle activity |
| $PSD(f_{EMG})$ | Spectral energy measured across seven frequency bands |
| \#peaksEMG | Total number of peaks detected in the signal |
| $\mu_{AmpEMG},\ \sigma_{AmpEMG}$ | Mean and standard deviation of the peak amplitudes |
| $\sum Amp_{EMG},\ \sum \bar{Amp}_{EMG}$ | Sum and normalised sum of all peak amplitudes |

## Respiration (RESP)

Breathing-pattern features from the chest stretch belt.

| Symbol | Meaning |
|---|---|
| $\mu_x,\ \sigma_x$ | Mean and standard deviation for both inhalation (I) and exhalation (E) durations |
| $I/E$ | Ratio between inhalation and exhalation time |
| $range_{RESP},\ vol_{insp}$ | Chest stretch range and inspiration volume |
| $rate_{RESP}$ | Overall breath rate |
| $\sum RESP$ | Total respiration duration |

## Body temperature (TEMP)

Skin-temperature features.

| Symbol | Meaning |
|---|---|
| $\mu_{TEMP},\ \sigma_{TEMP}$ | Mean and standard deviation of the temperature |
| $min_{TEMP},\ max_{TEMP}$ | Minimum and maximum temperature values |
| $range_{TEMP}$ | Dynamic range of the temperature signal |
| $\partial TEMP$ | Slope — the rate of temperature change |
