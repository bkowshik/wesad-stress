# WESAD Schema

Reference contract for the WESAD dataset as consumed by this repo. Every modeling and feature-engineering pass downstream assumes this structure; if a future loader returns something different, this doc is wrong and needs updating first.

Anchor citation: Schmidt et al., [*Introducing WESAD, a Multimodal Dataset for Wearable Stress and Affect Detection*](https://dl.acm.org/doi/pdf/10.1145/3242969.3242985), ICMI 2018. [UCI ML Repository ID 465](https://archive.ics.uci.edu/dataset/465/wesad+wearable+stress+and+affect+detection).

Per-subject artifact: `data/raw/WESAD/S<id>/S<id>.pkl` — one pickle per subject, ~700 MB each, total ~2.5 GB unpacked. Pickles were serialised under Python 2; load with `pickle.load(f, encoding='latin1')` in Python 3.

## Subjects

15 subjects, IDs **S2–S17 excluding S1 and S12** — encoded as [`VALID_SUBJECTS`](../src/wesad_stress/data.py). S1 was a pilot dropped from the final release; S12 has corrupted data per the dataset documentation. Subjects ran a fixed protocol: baseline → amusement → stress (Trier Social Stress Test) → meditation, plus transition intervals.

## Top-level structure

The pickle deserialises to a dict with three keys:

```
{
  'subject': str,                   # e.g. 'S2'
  'signal': {
    'chest': { ... 6 modalities },  # RespiBAN Professional, 700 Hz
    'wrist': { ... 4 modalities },  # Empatica E4, mixed rates
  },
  'label': np.ndarray,              # int, length = chest signal length
}
```

The `label` array shares the chest sampling rate (700 Hz). Wrist signals are *not* time-aligned to the chest grid — each modality has its own sample count derived from its rate × the session duration. Aligning across devices is a downstream concern; the schema preserves the raw layout.

## Chest modalities — RespiBAN @ 700 Hz

All chest signals are sampled synchronously at **700 Hz**. Session length is the chest array length / 700; for S2 this is ~101 min (~6079 s). Verify measured rate via shape arithmetic — do not trust the nominal value alone.

| Modality | Channels | Shape          | dtype   | Nominal range¹     | Notes                                  |
|----------|----------|----------------|---------|--------------------|----------------------------------------|
| ACC      | 3        | (N, 3)         | float64 | ±2g                | 3-axis accelerometer, body-mounted     |
| ECG      | 1        | (N, 1)         | float64 | ±5 mV              | Lead-II configuration                  |
| EMG      | 1        | (N, 1)         | float64 | ±5 mV              | Trapezius                              |
| EDA      | 1        | (N, 1)         | float64 | 0–25 µS            | Galvanic skin response                 |
| Temp     | 1        | (N, 1)         | **float32** | 0–50 °C        | Skin temperature — note dtype differs  |
| Resp     | 1        | (N, 1)         | float64 | device raw units²  | Respiration belt deflection            |

¹ Nominal hardware ranges from the RespiBAN Professional datasheet. The notebook prints the *observed* min/max per subject — those should sit inside the nominal envelope but typically use a much smaller portion of it. See the observed envelope for S2 below.

² Respiration is reported in raw belt-deflection units rather than a normalised percentage; observed range for S2 is roughly ±28. Treat it as an unscaled signal and standardise per-subject before modelling.

## Wrist modalities — Empatica E4 @ mixed rates

The wrist device samples each modality at its own rate. A 60-minute session produces vastly different sample counts across modalities — useful to keep in mind when designing windowing.

| Modality | Rate (Hz) | Channels | Shape      | dtype   | Nominal range  | Notes                              |
|----------|-----------|----------|------------|---------|----------------|------------------------------------|
| ACC      | 32        | 3        | (N₃₂, 3)   | float64 | ±2g            | 3-axis accelerometer, wrist        |
| BVP      | 64        | 1        | (N₆₄, 1)   | float64 | raw PPG units  | Blood volume pulse (photoplethysmography) |
| EDA      | 4         | 1        | (N₄, 1)    | float64 | 0–100 µS       | ~14k samples per hour — coarse     |
| TEMP     | 4         | 1        | (N₄, 1)    | float64 | -40 to 115 °C  | Skin temperature, wrist            |

The wrist EDA at 4 Hz is the lowest-resolution channel in the dataset; any model that fuses chest and wrist EDA has to decide between upsampling the wrist signal or downsampling the chest signal to a common grid. That decision belongs in the preprocessing pipeline, not here.

For a plain-language description of what each modality actually measures (BVP, ECG, EDA, EMG, Resp, Temp, ACC), see [`glossary.md`](./glossary.md).

## Labels

The label array carries integer codes at the chest rate (700 Hz). The full code book per Schmidt et al. is:

| Code | Name                       | Use in canonical 3-class problem |
|------|----------------------------|----------------------------------|
| 0    | Not defined / transient    | ignore                           |
| 1    | Baseline                   | **baseline** class               |
| 2    | Stress                     | **stress** class                 |
| 3    | Amusement                  | **amusement** class              |
| 4    | Meditation                 | ignore (sometimes added as 4th)  |
| 5    | Ignore (recovery 1)        | ignore                           |
| 6    | Ignore (recovery 2)        | ignore                           |
| 7    | Ignore (recovery 3)        | ignore                           |

The headline result in the paper uses the 3-class problem (1, 2, 3); we mirror that for the baseline LSTM. Adding meditation (code 4) as a 4th class is a defensible variant for ablation but not the default.

Empirically the duration split is unbalanced — baseline and meditation each ~20 min, stress ~10 min, amusement ~6 min. Class-balanced training or stratified sampling is worth thinking about; in untreated form a constant-baseline predictor scores ~50% accuracy on the 3-class problem.

A separate gotcha worth knowing: **label 0 (transient / not defined) is roughly half the recording.** For S2 it accounts for ~3061 s out of a ~6079 s session — protocol transitions, instructions, breaks. The "active" labels (1–4) together make up only ~48 minutes of a ~100-minute recording. Any pipeline that doesn't filter on label first will be modelling mostly transients.

## Observed envelope — S2

What the data actually looks like for one subject. Generated by [`notebooks/00-load-one-subject.ipynb`](../notebooks/00-load-one-subject.ipynb); rerun with a different `SUBJECT_ID` to see another subject. Subject-to-subject variation is real (especially in EDA and temperature baseline), so treat these as illustrative — not as bounds to validate against.

| Device | Modality | Shape          | dtype   | Observed min | Observed max |
|--------|----------|----------------|---------|--------------|--------------|
| chest  | ACC      | (4 255 300, 3) | float64 |        -1.14 |         2.03 |
| chest  | ECG      | (4 255 300, 1) | float64 |        -1.50 |         1.50 |
| chest  | EMG      | (4 255 300, 1) | float64 |        -0.41 |         0.30 |
| chest  | EDA      | (4 255 300, 1) | float64 |         0.26 |         7.58 |
| chest  | Temp     | (4 255 300, 1) | float32 |        28.05 |        34.37 |
| chest  | Resp     | (4 255 300, 1) | float64 |       -27.90 |        27.38 |
| wrist  | ACC      | (194 528, 3)   | float64 |      -128.00 |       127.00 |
| wrist  | BVP      | (389 056, 1)   | float64 |      -873.67 |       988.08 |
| wrist  | EDA      | (24 316, 1)    | float64 |         0.05 |         1.72 |
| wrist  | TEMP     | (24 316, 1)    | float64 |        32.31 |        35.97 |

Wrist ACC's `[-128, 127]` envelope hints at int8-style hardware quantisation cast to float; the device firmware exposes raw 8-bit counts here, not g-units. Any model that fuses chest and wrist accel needs to harmonise scale before concatenating.

The wrist EDA range (0.05–1.72 µS) is much narrower than the chest EDA range (0.26–7.58 µS) for the same subject. Different electrodes, different sites, different physiology — not a calibration bug. Worth remembering that "EDA" is not one signal but two.

## Companion files (not loaded by `load_wesad`)

Each subject folder also contains:

- `S<id>_readme.txt` — protocol order and any per-subject notes from the data collection
- `S<id>_quest.csv` — questionnaire responses (PANAS, STAI, SAM, SSSQ) administered between protocol blocks
- `S<id>_respiban.txt` / `S<id>_E4_*.csv` — raw device exports, redundant with the pickle but with device-side timestamps if needed

The baseline pipeline works from the pickle only. The questionnaires become relevant for stretch analyses — for example, whether self-reported stress correlates with classifier confidence.

## What this contract pins down for the rest of the repo

- `load_wesad(subject_id)` returns the dict above unchanged — no flattening, no resampling, no label remapping. Those transforms live in `preprocess.py` (not yet written).
- Any feature extractor that expects e.g. ECG at 700 Hz with shape `(N, 1)` can rely on the contract here; if a future loader switches to flattened `(N,)`, this doc gets updated and the change is announced in `CHANGELOG.md`.
- Subjects S1 and S12 are out of scope. `VALID_SUBJECTS` is the canonical list.

---

The derived feature table built from this raw contract — windowing rules, row identity, and the 19 feature columns — is documented separately in [`features.md`](./features.md), since it tracks the code in `features.py` and changes on a different cadence than this fixed dataset contract.
