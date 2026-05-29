# WESAD Stress Detection

Baseline study of stress detection from wearable physiological signals, using the WESAD dataset.

## Why

_To be written._

## Dataset

WESAD (Wearable Stress and Affect Detection) — multimodal physiological recordings from 15 subjects across baseline / stress / amusement / meditation conditions. Stress induced via the Trier Social Stress Test.

- Chest (RespiBAN @ 700 Hz): ECG, EDA, EMG, respiration, temperature, 3-axis accel
- Wrist (Empatica E4): BVP @ 64 Hz, EDA @ 4 Hz, temp @ 4 Hz, accel @ 32 Hz

Reference: Schmidt et al., [*Introducing WESAD, a Multimodal Dataset for Wearable Stress and Affect Detection*](https://dl.acm.org/doi/pdf/10.1145/3242969.3242985), ICMI 2018. Hosted on the [UCI ML Repository (dataset 465)](https://archive.ics.uci.edu/dataset/465/wesad+wearable+stress+and+affect+detection). Schema contract: [`docs/SCHEMA.md`](./docs/SCHEMA.md).

## Setup

Python 3.11. Dependencies pinned via `uv.lock`.

```bash
uv sync
```

### Download the dataset

~2.5 GB, ~5–10 min depending on bandwidth. Lands as `data/raw/WESAD/S2/`, `data/raw/WESAD/S3/`, … `S17/` (skipping S1 and S12 per the dataset documentation — encoded as [`VALID_SUBJECTS`](./src/wesad_stress/data.py)). The `data/raw/` directory is gitignored.

```bash
cd data/raw
curl -L -o WESAD.zip 'https://uni-siegen.sciebo.de/s/HGdUkoNlW1Ub0Gx/download'
unzip -q WESAD.zip
rm WESAD.zip
ls -la WESAD/
```

The link above is from the [official Siegen dataset page](https://ubi29.informatik.uni-siegen.de/usi/data_wesad.html) — check there if it ever rotates.

### MLflow tracking

```bash
uv run python scripts/smoke_test_mlflow.py
uv run mlflow ui \
  --backend-store-uri sqlite:///mlflow.db \
  --host 127.0.0.1 \
  --allowed-hosts 127.0.0.1:5000,localhost:5000
```

## Results

_To be written._
