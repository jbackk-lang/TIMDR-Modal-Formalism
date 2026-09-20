"""Execution harness for docs/PREREG_K_GRID_FREQ_v0.5.md.

Replication of the v0.3/v0.4 statistic (zero-lag Pearson correlation of
linearly detrended windows) on an INDEPENDENT SOURCE: separate raw
per-station 10 Hz files (PT_LI01_100ms.zip / TUR-IS01_100ms.zip) from
the KIT Power Grid Frequency Database, distinct from the pre-synced
SYNC01.csv used in v0.1-v0.4 -- same underlying 2019 measurement
campaign and station pair, but a different file, different native
resolution (10 Hz vs 1 Hz), and a non-overlapping time window (July
11-12 vs August 2019). See PREREG_K_GRID_FREQ_v0.5.md Section 0 for the
honest scope caveat.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import detrend

DATA_FILE_PT = Path("/sessions/blissful-focused-lamport/mnt/Downloads/PT_LI01_100ms.zip")
DATA_FILE_TUR = Path("/sessions/blissful-focused-lamport/mnt/Downloads/TUR-IS01_100ms.zip")

WINDOW_SEC = 600.0
FS_HZ = 10.0  # native resolution of this source (v0.1-v0.4 used 1.0 Hz)
N_PERMUTATIONS = 2000
SEED = 0
ALPHA = 0.05
MIN_WINDOWS_FOR_TEST = 20

# Frozen in PREREG_K_GRID_FREQ_v0.5.md Section 2 -- deterministic,
# based on data availability (longest joint QI=0 run in a 48h probe
# window chosen for extraction speed), not on the statistic's outcome.
RUN_START_ROW_PT = 1767960
RUN_START_ROW_TUR = 1837470
RUN_LEN_S = 269919


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    pt_hash = sha256_of(DATA_FILE_PT)
    tur_hash = sha256_of(DATA_FILE_TUR)
    assert pt_hash == "31c28fe570751693b42f1f7074ba5dbd73d4ecde9041efe52d5b5f756381501f", (
        f"PT data file hash mismatch: {pt_hash}"
    )
    assert tur_hash == "390a2431a913d6ad1cddd206fba7de32f65a3ad105e2ad3aff3d865bf4106938", (
        f"TUR data file hash mismatch: {tur_hash}"
    )

    df_pt = pd.read_csv(
        DATA_FILE_PT, sep=";", skiprows=range(1, RUN_START_ROW_PT + 1), nrows=RUN_LEN_S,
    )
    df_tur = pd.read_csv(
        DATA_FILE_TUR, sep=";", skiprows=range(1, RUN_START_ROW_TUR + 1), nrows=RUN_LEN_S,
    )
    assert len(df_pt) == RUN_LEN_S and len(df_tur) == RUN_LEN_S
    assert (df_pt["QI_PT"] == 0).all() and (df_tur["QI_TR"] == 0).all()
    assert (df_pt["Time"].to_numpy() == df_tur["Time"].to_numpy()).all(), (
        "PT/TUR timestamps do not align row-for-row"
    )
    start_time = str(df_pt["Time"].iloc[0])
    end_time = str(df_pt["Time"].iloc[-1])

    s_pt = df_pt["f50_PT"].to_numpy(dtype=float)
    s_tr = df_tur["f50_TR"].to_numpy(dtype=float)

    n_per_window = int(round(WINDOW_SEC * FS_HZ))
    n_windows = len(s_pt) // n_per_window

    def window_stack(s_full: np.ndarray) -> np.ndarray:
        out = np.empty((n_windows, n_per_window))
        for w in range(n_windows):
            i0 = w * n_per_window
            i1 = i0 + n_per_window
            out[w] = detrend(s_full[i0:i1], type="linear")
        return out

    W_pt = window_stack(s_pt)
    W_tr = window_stack(s_tr)
    n = n_windows

    insufficient_data = n < MIN_WINDOWS_FOR_TEST

    result = {
        "prereg": "docs/PREREG_K_GRID_FREQ_v0.5.md",
        "data_file_pt": DATA_FILE_PT.name,
        "data_file_pt_sha256": pt_hash,
        "data_file_tur": DATA_FILE_TUR.name,
        "data_file_tur_sha256": tur_hash,
        "channel_a": "f50_PT",
        "channel_b": "f50_TR",
        "run_start_row_pt": RUN_START_ROW_PT,
        "run_start_row_tur": RUN_START_ROW_TUR,
        "run_start_time": start_time,
        "run_end_time": end_time,
        "run_len_samples": RUN_LEN_S,
        "fs_hz": FS_HZ,
        "window_sec": WINDOW_SEC,
        "n_windows": n,
        "statistic": "mean zero-lag Pearson correlation of linearly detrended windows",
        "insufficient_data_for_test": insufficient_data,
        "replicates": "docs/RESULT_K_GRID_FREQ_v0.3.md and v0.4.md (independent source: separate raw 10Hz per-station files, non-overlapping window)",
    }

    if insufficient_data:
        result["verdict"] = "INCONCLUSIVE"
        result["reason"] = f"only {n} windows, below MIN_WINDOWS_FOR_TEST={MIN_WINDOWS_FOR_TEST}"
        Path("docs/RESULT_K_GRID_FREQ_v0.5.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
        print(json.dumps(result, indent=2, default=str))
        return

    norm_pt = np.linalg.norm(W_pt, axis=1)
    norm_tr = np.linalg.norm(W_tr, axis=1)
    norm_pt = np.where(norm_pt == 0.0, 1e-12, norm_pt)
    norm_tr = np.where(norm_tr == 0.0, 1e-12, norm_tr)

    def row_corr(A: np.ndarray, normA: np.ndarray, B: np.ndarray, normB: np.ndarray, order: np.ndarray) -> np.ndarray:
        Bp = B[order]
        normBp = normB[order]
        dots = np.einsum("ij,ij->i", A, Bp)
        return dots / (normA * normBp)

    identity = np.arange(n)
    r_windows = row_corr(W_pt, norm_pt, W_tr, norm_tr, identity)
    real_stat = float(np.mean(r_windows))

    rng = np.random.default_rng(SEED)
    null_stats = np.empty(N_PERMUTATIONS)
    for i in range(N_PERMUTATIONS):
        perm = rng.permutation(n)
        null_stats[i] = np.mean(row_corr(W_pt, norm_pt, W_tr, norm_tr, perm))
    p_value = float((np.sum(null_stats >= real_stat) + 1) / (N_PERMUTATIONS + 1))

    r_windows_pos = row_corr(W_pt, norm_pt, W_pt, norm_pt, identity)
    real_stat_pos = float(np.mean(r_windows_pos))
    pos_null_stats = np.empty(N_PERMUTATIONS)
    for i in range(N_PERMUTATIONS):
        perm = rng.permutation(n)
        pos_null_stats[i] = np.mean(row_corr(W_pt, norm_pt, W_pt, norm_pt, perm))
    pos_p_value = float((np.sum(pos_null_stats >= real_stat_pos) + 1) / (N_PERMUTATIONS + 1))

    controls_passed = bool(pos_p_value < ALPHA)
    if not controls_passed:
        verdict = "INCONCLUSIVE"
    elif p_value < ALPHA:
        verdict = "SUPPORTED"
    else:
        verdict = "NOT SUPPORTED"

    result.update({
        "real_stat_mean_corr": real_stat,
        "real_r_windows_median": float(np.median(r_windows)),
        "real_r_windows_p25_p75": [float(np.percentile(r_windows, 25)), float(np.percentile(r_windows, 75))],
        "null_stat_mean": float(np.mean(null_stats)),
        "null_stat_std": float(np.std(null_stats)),
        "z_score_vs_null": float((real_stat - np.mean(null_stats)) / np.std(null_stats)) if np.std(null_stats) > 0 else None,
        "n_permutations": N_PERMUTATIONS,
        "p_value": p_value,
        "positive_control_stat": real_stat_pos,
        "positive_control_p_value": pos_p_value,
        "controls_passed": controls_passed,
        "alpha": ALPHA,
        "verdict": verdict,
    })

    Path("docs/RESULT_K_GRID_FREQ_v0.5.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
