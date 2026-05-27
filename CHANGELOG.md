# Changelog

## Upcoming

### Data ingest

Implement `load_wesad()` to read a single subject's pickle file from `data/raw/WESAD/`. The dataset packages chest sensors (RespiBAN @ 700 Hz — ECG, EDA, EMG, respiration, temperature, 3-axis accelerometer) and wrist sensors (Empatica E4 at mixed rates) per subject; the loader returns both, with labels mapped per the dataset documentation (1=baseline, 2=stress, 3=amusement, 4=meditation; 0/5/6/7 are ignore/transition states). Companion EDA notebook follows — distributions per modality, label balance per subject, signal-quality checks across the two devices.

### Preprocessing and splits

60-second windows with overlap, leave-one-subject-out (LOSO) cross-validation as the primary protocol. Both classical features (HRV from ECG, phasic + tonic decomposition from EDA, respiration-rate features) and raw windowed signals get prepared — they feed different model families and the comparison is part of the point.

### Baseline models

LSTM in PyTorch first, end-to-end through MLflow tracking — the goal of the LSTM is not the best number, it's a credible reference and a working training loop. Then a small 1D CNN, which is usually a better fit for short-window physiological signals where the relevant patterns are local. Both evaluated under LOSO with confusion matrices and learning curves.

### Feature-engineered vs raw

The more interesting axis. Classical pipelines (HRV / SCR features fed into logistic regression or gradient boosting) often beat deep models on small datasets like WESAD. The ablation table compares feature-eng + classical, feature-eng + LSTM/CNN, and raw + LSTM/CNN, across single-modality (chest-only, wrist-only) and fused configurations.

### Writeup

Once results land, fill in the README's Why and Results sections, and write a longer-form blog post linked from there. Emphasis on what was surprising rather than the headline accuracy number.

## 2026-05-27

### Middleware

MLflow 3.x's security middleware rejects any request whose port-qualified Host header (e.g. 127.0.0.1:5000) isn't in `--allowed-hosts`, so the allowlist must include the port — otherwise the UI returns `403 Invalid Host` header.

```bash
cd /Users/bkowshik/code/bkowshik/wesad-stress

uv run mlflow ui \
  --backend-store-uri sqlite:///mlflow.db \
  --host 127.0.0.1 \
  --allowed-hosts 127.0.0.1:5000,localhost:5000
```

### MLflow UI

[MLflow AI Assistant](https://mlflow.org/docs/latest/genai/getting-started/try-assistant/) works with coding agents like Claude Code. 🎉

![MLflow smoke test runs](./images/2026-05-27-mlflow-smoke-test.png)
