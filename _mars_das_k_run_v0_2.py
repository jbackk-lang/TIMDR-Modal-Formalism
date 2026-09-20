"""Execution harness for docs/PREREG_K_MARS_DAS_v0.2.md.

Identical to _mars_das_k_run.py (v0.1) EXCEPT the channel pair (Section 1
of the v0.2 prereg): channel A=0, channel B=7 (36.4 m apart, chosen to
stay above gauge length and keep propagation delay <=25% of window_sec
even for a pessimistically slow wave). Everything else (file, window_sec,
n_permutations, seed, alpha, extraction functions) is reused UNCHANGED
from timdr_modal/real_data_validation.py / v0.1.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import h5py
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from timdr_modal.real_data_validation import (  # noqa: E402
    _fft_peak_f_phi_A,
    _local_phase_to_global,
    _wrap_to_pi,
)
from timdr_modal.phase_sync import Modality, is_resonant  # noqa: E402

DATA_FILE = Path("/sessions/blissful-focused-lamport/mnt/a/20220730T233258Z.h5")
WINDOW_SEC = 1.0
N_PERMUTATIONS = 2000
SEED = 0
ALPHA = 0.05
TARGET_REAL_RATE = 0.1
MIN_WINDOWS_FOR_CALIBRATION = 20
CHANNEL_A_IDX = 0
CHANNEL_B_IDX = 7  # frozen in PREREG_K_MARS_DAS_v0.2.md Section 1


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    file_hash = sha256_of(DATA_FILE)

    with h5py.File(DATA_FILE, "r") as f:
        d = f["data"]
        attrs = dict(d.attrs)
        nch, nt = d.shape
        dt_s = float(attrs["dt_s"])
        dx_m = float(attrs["dx_m"])
        fs = 1.0 / dt_s
        s_a = np.asarray(d[CHANNEL_A_IDX, :], dtype=float)
        s_b = np.asarray(d[CHANNEL_B_IDX, :], dtype=float)

    n_per_window = int(round(WINDOW_SEC / dt_s))
    n_windows = nt // n_per_window

    def extract(s_full: np.ndarray):
        out = []
        for w in range(n_windows):
            i0 = w * n_per_window
            i1 = i0 + n_per_window
            s_window = s_full[i0:i1]
            f_peak, phi_local, A_peak = _fft_peak_f_phi_A(s_window, fs)
            t_start = w * WINDOW_SEC
            phi_global = _local_phase_to_global(phi_local, f_peak, t_start)
            out.append(Modality(f=f_peak, phi=phi_global, A=A_peak))
        return out

    mod_a = extract(s_a)
    mod_b = extract(s_b)
    n = len(mod_a)

    insufficient_data = n < MIN_WINDOWS_FOR_CALIBRATION
    if not insufficient_data:
        diffs_f = np.array([abs(a.f - b.f) for a, b in zip(mod_a, mod_b)])
        diffs_phi = np.array([abs(_wrap_to_pi(a.phi - b.phi)) for a, b in zip(mod_a, mod_b)])
        eps_f = float(np.percentile(diffs_f, TARGET_REAL_RATE * 100.0))
        eps_phi = float(np.percentile(diffs_phi, TARGET_REAL_RATE * 100.0))
    else:
        eps_f = eps_phi = None

    result = {
        "prereg": "docs/PREREG_K_MARS_DAS_v0.2.md",
        "data_file": str(DATA_FILE.name),
        "data_file_sha256": file_hash,
        "nch": int(nch),
        "nt": int(nt),
        "dx_m": dx_m,
        "channel_a": CHANNEL_A_IDX,
        "channel_b": CHANNEL_B_IDX,
        "channel_distance_m": dx_m * (CHANNEL_B_IDX - CHANNEL_A_IDX),
        "window_sec": WINDOW_SEC,
        "n_windows": n,
        "insufficient_data_for_calibration": insufficient_data,
        "eps_f": eps_f,
        "eps_phi": eps_phi,
    }

    if insufficient_data:
        result["verdict"] = "INCONCLUSIVE"
        result["reason"] = f"only {n} windows, below MIN_WINDOWS_FOR_CALIBRATION={MIN_WINDOWS_FOR_CALIBRATION}"
        Path("docs/RESULT_K_MARS_DAS_v0.2.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
        print(json.dumps(result, indent=2, default=str))
        return

    def resonance_rate(a, b):
        count = sum(1 for wa, wb in zip(a, b) if is_resonant(wa, wb, eps_f=eps_f, eps_phi=eps_phi))
        return count, count / len(a)

    n_resonant_real, rate_real = resonance_rate(mod_a, mod_b)

    rng = np.random.default_rng(SEED)
    null_rates = np.empty(N_PERMUTATIONS)
    for i in range(N_PERMUTATIONS):
        perm = rng.permutation(n)
        shuffled = [mod_b[j] for j in perm]
        _, rate = resonance_rate(mod_a, shuffled)
        null_rates[i] = rate
    p_value = float((np.sum(null_rates >= rate_real) + 1) / (N_PERMUTATIONS + 1))

    n_pos, rate_pos = resonance_rate(mod_a, mod_a)
    pos_null_rates = np.empty(N_PERMUTATIONS)
    for i in range(N_PERMUTATIONS):
        perm = rng.permutation(n)
        shuffled = [mod_a[j] for j in perm]
        _, rate = resonance_rate(mod_a, shuffled)
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

    Path("docs/RESULT_K_MARS_DAS_v0.2.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
