"""Execution harness for docs/PREREG_K_GRID_FREQ_v0.1.md.

Reuses _fft_peak_f_phi_A / _local_phase_to_global / _wrap_to_pi
UNCHANGED from timdr_modal/real_data_validation.py, applied to the
f50_XX (mHz deviation from 50 Hz) series instead of a raw acoustic /
seismic waveform. All parameters (location pair, window-selection
rule, window_sec, calibration target, n_permutations, seed, alpha)
are frozen in the prereg BEFORE this script is run.
"""
from __future__ import annotations

import hashlib
import json
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

DATA_FILE = Path("/sessions/blissful-focused-lamport/mnt/Downloads/SYNC01.csv")
FS_HZ = 1.0
WINDOW_SEC = 600.0
N_PERMUTATIONS = 2000
SEED = 0
ALPHA = 0.05
TARGET_REAL_RATE = 0.1
MIN_WINDOWS_FOR_CALIBRATION = 20

# Frozen in PREREG_K_GRID_FREQ_v0.1.md Section 3: longest contiguous
# run where QI_PT==0 AND QI_TR==0.
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

    # sanity checks: reproduce the deterministic properties frozen in the prereg
    assert len(df) == RUN_LEN_S, f"unexpected run length: {len(df)}"
    assert (df["QI_PT"] == 0).all() and (df["QI_TR"] == 0).all(), (
        "run contains non-zero QI in the frozen window -- prereg assumption violated"
    )
    start_time = str(df["Time"].iloc[0])

    s_pt = df["f50_PT"].to_numpy(dtype=float)
    s_tr = df["f50_TR"].to_numpy(dtype=float)

    n_per_window = int(round(WINDOW_SEC / (1.0 / FS_HZ)))
    n_windows = len(s_pt) // n_per_window

    def extract(s_full: np.ndarray):
        out = []
        for w in range(n_windows):
            i0 = w * n_per_window
            i1 = i0 + n_per_window
            s_window = s_full[i0:i1]
            f_peak, phi_local, A_peak = _fft_peak_f_phi_A(s_window, FS_HZ)
            t_start = w * WINDOW_SEC
            phi_global = _local_phase_to_global(phi_local, f_peak, t_start)
            out.append(Modality(f=f_peak, phi=phi_global, A=A_peak))
        return out

    mod_pt = extract(s_pt)
    mod_tr = extract(s_tr)
    n = len(mod_pt)

    insufficient_data = n < MIN_WINDOWS_FOR_CALIBRATION

    result = {
        "prereg": "docs/PREREG_K_GRID_FREQ_v0.1.md",
        "data_file": str(DATA_FILE.name),
        "data_file_sha256": file_hash,
        "channel_a": "f50_PT",
        "channel_b": "f50_TR",
        "run_start_row": RUN_START_ROW,
        "run_start_time": start_time,
        "run_len_s": RUN_LEN_S,
        "window_sec": WINDOW_SEC,
        "n_windows": n,
        "insufficient_data_for_calibration": insufficient_data,
    }

    if insufficient_data:
        result["verdict"] = "INCONCLUSIVE"
        result["reason"] = f"only {n} windows, below MIN_WINDOWS_FOR_CALIBRATION={MIN_WINDOWS_FOR_CALIBRATION}"
        Path("docs/RESULT_K_GRID_FREQ_v0.1.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
        print(json.dumps(result, indent=2, default=str))
        return

    diffs_f = np.array([abs(a.f - b.f) for a, b in zip(mod_pt, mod_tr)])
    diffs_phi = np.array([abs(_wrap_to_pi(a.phi - b.phi)) for a, b in zip(mod_pt, mod_tr)])
    eps_f = float(np.percentile(diffs_f, TARGET_REAL_RATE * 100.0))
    eps_phi = float(np.percentile(diffs_phi, TARGET_REAL_RATE * 100.0))
    result["eps_f"] = eps_f
    result["eps_phi"] = eps_phi

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

    Path("docs/RESULT_K_GRID_FREQ_v0.1.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
