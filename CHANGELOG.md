# Changelog

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
