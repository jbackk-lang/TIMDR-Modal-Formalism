"""Execution harness for docs/PREREG_K_GRID_FREQ_v0.2.md.

Identical to _grid_freq_k_run.py (v0.1) EXCEPT: each window is
zero-padded 16x (frozen in v0.2 prereg Section 1) before being passed,
UNCHANGED, to _fft_peak_f_phi_A. Everything else (file, channel pair,
run-selection rule, window_sec, calibration target, n_permutations,
seed, alpha, is_resonant semantics) is reused UNCHANGED from v0.1.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from timdr_modal.real_data_validation import (  # noqa: E402
    _fft_peak_f_phi_A,
    _local_phase_to_global,
    _wrap_to_pi,
)
from timdr_modal.phase_sync import Modality, is_resonant  # noqa: E402

# Dane: katalog ze zmiennej TIMDR_DATA, domyslnie ../DATA obok repozytorium (hash pliku sprawdzany nizej).
DATA_DIR = Path(os.environ.get("TIMDR_DATA", Path(__file__).resolve().parent.parent / "DATA"))
DATA_FILE = DATA_DIR / "SYNC01.csv"
FS_HZ = 1.0
WINDOW_SEC = 600.0
N_PERMUTATIONS = 2000
SEED = 0
ALPHA = 0.05
TARGET_REAL_RATE = 0.1
MIN_WINDOWS_FOR_CALIBRATION = 20
ZERO_PAD_FACTOR = 16  # frozen in PREREG_K_GRID_FREQ_v0.2.md Section 1

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
    n_padded = n_per_window * ZERO_PAD_FACTOR

    def extract(s_full: np.ndarray):
        out = []
        for w in range(n_windows):
            i0 = w * n_per_window
            i1 = i0 + n_per_window
            s_window = s_full[i0:i1]
            s_padded = np.pad(s_window, (0, n_padded - len(s_window)))
            f_peak, phi_local, A_peak = _fft_peak_f_phi_A(s_padded, FS_HZ)
            t_start = w * WINDOW_SEC
            phi_global = _local_phase_to_global(phi_local, f_peak, t_start)
            out.append(Modality(f=f_peak, phi=phi_global, A=A_peak))
        return out

    mod_pt = extract(s_pt)
    mod_tr = extract(s_tr)
    n = len(mod_pt)

    insufficient_data = n < MIN_WINDOWS_FOR_CALIBRATION

    result = {
        "prereg": "docs/PREREG_K_GRID_FREQ_v0.2.md",
        "data_file": str(DATA_FILE.name),
        "data_file_sha256": file_hash,
        "channel_a": "f50_PT",
        "channel_b": "f50_TR",
        "run_start_row": RUN_START_ROW,
        "run_start_time": start_time,
        "run_len_s": RUN_LEN_S,
        "window_sec": WINDOW_SEC,
        "zero_pad_factor": ZERO_PAD_FACTOR,
        "n_windows": n,
        "insufficient_data_for_calibration": insufficient_data,
    }

    if insufficient_data:
        result["verdict"] = "INCONCLUSIVE"
        result["reason"] = f"only {n} windows, below MIN_WINDOWS_FOR_CALIBRATION={MIN_WINDOWS_FOR_CALIBRATION}"
        Path("docs/RESULT_K_GRID_FREQ_v0.2.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
        print(json.dumps(result, indent=2, default=str))
        return

    diffs_f = np.array([abs(a.f - b.f) for a, b in zip(mod_pt, mod_tr)])
    diffs_phi = np.array([abs(_wrap_to_pi(a.phi - b.phi)) for a, b in zip(mod_pt, mod_tr)])
    eps_f = float(np.percentile(diffs_f, TARGET_REAL_RATE * 100.0))
    eps_phi = float(np.percentile(diffs_phi, TARGET_REAL_RATE * 100.0))
    result["eps_f"] = eps_f
    result["eps_phi"] = eps_phi
    result["diffs_f_exact_zero_count"] = int((diffs_f == 0).sum())

    def resonance_rate(a, b):
        count = sum(1 for wa, wb in zip(a, b) if is_resonant(wa, wb, eps_f=eps_f, eps_phi=eps_phi))
        return count, count / len(a)

    n_resonant_real, rate_real = resonance_rate(mod_pt, mod_tr)

    rng = np.random.default_rng(SEED)
    null_rates = np.empty(N_PERMUTATIONS)
    for i in range(N_PERMUTATIONS):
        perm = rng.permutation(n)
        shuffled = [mod_tr[j] for j in perm]
        _, rate = resonance_rate(mod_pt, shuffled)
        null_rates[i] = rate
    p_value = float((np.sum(null_rates >= rate_real) + 1) / (N_PERMUTATIONS + 1))

    n_pos, rate_pos = resonance_rate(mod_pt, mod_pt)
    pos_null_rates = np.empty(N_PERMUTATIONS)
    for i in range(N_PERMUTATIONS):
        perm = rng.permutation(n)
        shuffled = [mod_pt[j] for j in perm]
        _, rate = resonance_rate(mod_pt, shuffled)
        pos_null_rates[i] = rate
    pos_p_value = float((np.sum(pos_null_rates >= rate_pos) + 1) / (N_PERMUTATIONS + 1))

    controls_passed = (rate_pos > 0.0) and (pos_p_value < ALPHA)
    if not controls_passed:
        verdict = "INCONCLUSIVE"
    elif p_value < ALPHA:
        verdict = "SUPPORTED"
    else:
        verdict = "NOT SUPPORTED"

    result.update({
        "n_resonant_real": n_resonant_real,
        "resonance_rate_real": rate_real,
        "n_permutations": N_PERMUTATIONS,
        "p_value": p_value,
        "positive_control_rate": rate_pos,
        "positive_control_p_value": pos_p_value,
        "controls_passed": controls_passed,
        "alpha": ALPHA,
        "verdict": verdict,
    })

    Path("docs/RESULT_K_GRID_FREQ_v0.2.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
