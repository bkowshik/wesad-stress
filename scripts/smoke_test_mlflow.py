"""Verify MLflow tracking works end-to-end before any real modelling."""

import mlflow
import random
from pathlib import Path

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("smoke-test")

with mlflow.start_run(run_name="setup-verification") as run:
    mlflow.log_param("purpose", "verify mlflow tracking works")
    mlflow.log_param("subject_id", "none")
    mlflow.log_metric("dummy_accuracy", round(0.42 + random.random() * 0.1, 4))
    mlflow.log_metric("dummy_loss", 0.69)

    artifact = Path("smoke-artifact.txt")
    artifact.write_text("MLflow smoke test artifact.\n")
    mlflow.log_artifact(str(artifact))
    artifact.unlink()

    print(f"\nMLflow smoke test passed.")
    print(f"  Run ID:       {run.info.run_id}")
    print(f"  Experiment:   {run.info.experiment_id}")
    print(f"  Tracking URI: {mlflow.get_tracking_uri()}\n")
    print("Next: uv run mlflow ui --backend-store-uri sqlite:///mlflow.db")
    print("Then open http://127.0.0.1:5000 and screenshot the run.")
