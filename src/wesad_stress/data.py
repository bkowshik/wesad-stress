"""WESAD data loading utilities.

The WESAD dataset is not included in this repo. Download from the UCI
ML Repository (dataset 465) and unzip into `data/raw/WESAD/` — one
folder per subject (S2/, S3/, ..., S17/). See the README for the
download command and `docs/SCHEMA.md` for the data contract returned
by `load_wesad()`.
"""

import pickle
from pathlib import Path
from typing import Any

DATA_ROOT = Path(__file__).resolve().parents[2] / "data" / "raw" / "WESAD"

# Subjects 1 and 12 excluded per dataset documentation.
VALID_SUBJECTS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17]


def load_wesad(subject_id: int) -> dict[str, Any]:
    """Load WESAD data for a single subject.

    Parameters
    ----------
    subject_id
        Numeric subject identifier. Must be in :data:`VALID_SUBJECTS`.

    Returns
    -------
    dict
        Top-level dict with keys ``'subject'``, ``'signal'``, ``'label'``.
        ``signal`` is a dict with ``'chest'`` (RespiBAN @ 700 Hz: ECG, EDA,
        EMG, Resp, Temp, ACC) and ``'wrist'`` (Empatica E4: BVP, EDA, TEMP,
        ACC) sub-dicts. ``label`` is an int array sampled at 700 Hz
        (1=baseline, 2=stress, 3=amusement, 4=meditation;
        0/5/6/7=transient/ignore). Full contract: ``docs/SCHEMA.md``.

    Raises
    ------
    ValueError
        If ``subject_id`` is not in :data:`VALID_SUBJECTS`.
    FileNotFoundError
        If the expected pickle file is missing — typically because the
        dataset has not been downloaded into ``data/raw/WESAD/``.
    """
    if subject_id not in VALID_SUBJECTS:
        raise ValueError(
            f"subject_id={subject_id} is not in VALID_SUBJECTS={VALID_SUBJECTS}"
        )

    pkl_path = DATA_ROOT / f"S{subject_id}" / f"S{subject_id}.pkl"
    if not pkl_path.is_file():
        raise FileNotFoundError(
            f"WESAD pickle not found at {pkl_path}. "
            "See README for download instructions."
        )

    # The pickles were serialised under Python 2; latin1 encoding lets
    # Python 3 deserialise the numpy arrays and dict structure intact.
    with pkl_path.open("rb") as f:
        return pickle.load(f, encoding="latin1")
