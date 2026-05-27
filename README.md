# WESAD Stress Detection

Baseline study of stress detection from wearable physiological signals, using the WESAD dataset.

## Why

_To be written._

## Dataset

WESAD (Wearable Stress and Affect Detection) — multimodal physiological recordings from 15 subjects across baseline / stress / amusement / meditation conditions. Stress induced via the Trier Social Stress Test.

- Chest (RespiBAN @ 700 Hz): ECG, EDA, EMG, respiration, temperature, 3-axis accel
- Wrist (Empatica E4): BVP @ 64 Hz, EDA @ 4 Hz, temp @ 4 Hz, accel @ 32 Hz

Reference: Schmidt et al., "Introducing WESAD", ICMI 2018. Available via the UCI ML Repository. Place unzipped contents in `data/raw/WESAD/` (gitignored).

## Setup

```bash
uv sync
uv run python scripts/smoke_test_mlflow.py
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Python 3.11. Dependencies pinned via `uv.lock`.

## Results

_To be written._
