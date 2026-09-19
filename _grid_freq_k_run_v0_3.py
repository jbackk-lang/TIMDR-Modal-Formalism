"""Execution harness for docs/PREREG_K_GRID_FREQ_v0.3.md.

Replaces the FFT-peak + is_resonant() statistic (v0.1/v0.2, both
INCONCLUSIVE due to a discretization artifact) with a continuous,
zero-lag cross-correlation of linearly detrended windows. Data file,
channel pair, run-selection rule, window_sec, n_permutations, seed,
alpha are all reused UNCHANGED from v0.1/v0.2. Vectorized with numpy
(no per-window/per-permutation Python-level corrcoef calls) purely
for runtime -- the STATISTIC and its definition are unchanged from the
frozen prereg, this is only an implementation-speed detail.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import detrend

DATA_FILE = Path("/sessions/blissful-focused-lamport/mnt/Downloads/SYNC01.csv")
WINDOW_SEC = 600.0
FS_HZ = 1.0
N_PERMUTATIONS = 2000
SEED = 0
ALPHA = 0.05
MIN_WINDOWS_FOR_TEST = 20

RUN_START_ROW = 2071846
RUN_LEN_S = 238902


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    file_hash = sha256_of(DATA_FILE)
    assert file_hash == "2f81120c9057adac332cd910c92130cc1c023068940f61cd824d7e860a0bee83", (
        f"data file hash mismatch: {file_hash}"
    )

    df = pd.read_csv(
        DATA_FILE,
        sep=";",
        skiprows=range(1, RUN_START_ROW + 1),
        nrows=RUN_LEN_S,
        usecols=["Time", "f50_PT", "QI_PT", "f50_TR", "QI_TR"],
    )
    assert len(df) == RUN_LEN_S
    assert (df["QI_PT"] == 0).all() and (df["QI_TR"] == 0).all()
    start_time = str(df["Time"].iloc[0])

    s_pt = df["f50_PT"].to_numpy(dtype=float)
    s_tr = df["f50_TR"].to_numpy(dtype=float)

    n_per_window = int(round(WINDOW_SEC / (1.0 / FS_HZ)))
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
        "prereg": "docs/PREREG_K_GRID_FREQ_v0.3.md",
        "data_file": str(DATA_FILE.name),
        "data_file_sha256": file_hash,
        "channel_a": "f50_PT",
        "channel_b": "f50_TR",
        "run_start_row": RUN_START_ROW,
        "run_start_time": start_time,
        "run_len_s": RUN_LEN_S,
        "window_sec": WINDOW_SEC,
        "n_windows": n,
        "statistic": "mean zero-lag Pearson correlation of linearly detrended windows",
        "insufficient_data_for_test": insufficient_data,
    }

    if insufficient_data:
        result["verdict"] = "INCONCLUSIVE"
        result["reason"] = f"only {n} windows, below MIN_WINDOWS_FOR_TEST={MIN_WINDOWS_FOR_TEST}"
        Path("docs/RESULT_K_GRID_FREQ_v0.3.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
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
    real_stat_pos = float(np.mean(r_windows_pos))  # trivially ~1.0
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

    Path("docs/RESULT_K_GRID_FREQ_v0.3.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
