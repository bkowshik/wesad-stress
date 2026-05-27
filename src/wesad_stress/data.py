"""WESAD data loading utilities.

The WESAD dataset is not included in this repo. Download from the UCI
ML Repository (search 'WESAD') and unzip into `data/raw/WESAD/` —
one folder per subject (S2/, S3/, ..., S17/).
"""

from pathlib import Path

DATA_ROOT = Path(__file__).resolve().parents[2] / "data" / "raw" / "WESAD"

# Subjects 1 and 12 excluded per dataset documentation.
VALID_SUBJECTS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17]


def load_wesad(subject_id: int):
    """Load WESAD data for a single subject.

    Returns a dict with chest sensors (RespiBAN @ 700 Hz: ECG, EDA, EMG,
    resp, temp, accel), wrist sensors (Empatica E4: BVP, EDA, temp, accel)
    and labels (1=baseline, 2=stress, 3=amusement, 4=meditation;
    0/5/6/7=ignore).
    """
    raise NotImplementedError(
        f"load_wesad() — first function to write tomorrow.\n"
        f"Expected file: {DATA_ROOT / f'S{subject_id}' / f'S{subject_id}.pkl'}"
    )
