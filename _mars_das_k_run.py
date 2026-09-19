"""Execution harness for docs/PREREG_K_MARS_DAS_v0.1.md.

Reuses the frozen extraction/statistics primitives from
timdr_modal/real_data_validation.py UNCHANGED (_fft_peak_f_phi_A,
_local_phase_to_global, is_resonant, permutation test with positive
control) -- the only difference from Ridgecrest is how the two
"modalities" are obtained: here both come from the SAME .h5 file / same
DAS interrogator clock (two channel rows), so there is no
recording-synch.log cross-station offset step -- t_start is simply
window_index * window_sec, as declared in the prereg.

NOT part of the frozen analysis itself -- this is purely the runner that
reads the real file per the prereg's Section 1/3/4 and calls the frozen
functions.
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

DATA_FILE = Path("/sessions/blissful-focused-lamport/mnt/Downloads/20220730T233258Z.h5")
WINDOW_SEC = 1.0
N_PERMUTATIONS = 2000
SEED = 0
ALPHA = 0.05
TARGET_REAL_RATE = 0.1
MIN_WINDOWS_FOR_CALIBRATION = 20


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
        fs = 1.0 / dt_s
        ch_a_idx = 0
        ch_b_idx = nch - 1  # frozen rule: Section 3 of the prereg
        s_a = np.asarray(d[ch_a_idx, :], dtype=float)
        s_b = np.asarray(d[ch_b_idx, :], dtype=float)

    n_per_window = int(round(WINDOW_SEC / dt_s))
    n_windows = nt // n_per_window

    def extract(s_full: np.ndarray):
        out = []
        for w in range(n_windows):
            i0 = w * n_per_window
            i1 = i0 + n_per_window
            s_window = s_full[i0:i1]
            f_peak, phi_local, A_peak = _fft_peak_f_phi_A(s_window, fs)
            t_start = w * WINDOW_SEC  # shared DAS clock, per prereg Section 4
            phi_global = _local_phase_to_global(phi_local, f_peak, t_start)
            out.append(Modality(f=f_peak, phi=phi_global, A=A_peak))
        return out

    mod_a = extract(s_a)
    mod_b = extract(s_b)
    n = len(mod_a)

    # --- calibrate_epsilons(), same method/target as Ridgecrest ---
    insufficient_data = n < MIN_WINDOWS_FOR_CALIBRATION
    if not insufficient_data:
        diffs_f = np.array([abs(a.f - b.f) for a, b in zip(mod_a, mod_b)])
        diffs_phi = np.array([abs(_wrap_to_pi(a.phi - b.phi)) for a, b in zip(mod_a, mod_b)])
        eps_f = float(np.percentile(diffs_f, TARGET_REAL_RATE * 100.0))
        eps_phi = float(np.percentile(diffs_phi, TARGET_REAL_RATE * 100.0))
    else:
        eps_f = eps_phi = None

    result = {
        "prereg": "docs/PREREG_K_MARS_DAS_v0.1.md",
        "data_file": str(DATA_FILE.name),
        "data_file_sha256": file_hash,
        "h5_attrs": {k: (v if isinstance(v, (int, float, str)) else str(v)) for k, v in attrs.items()},
        "nch": int(nch),
        "nt": int(nt),
        "channel_a": ch_a_idx,
        "channel_b": ch_b_idx,
        "window_sec": WINDOW_SEC,
        "n_windows": n,
        "insufficient_data_for_calibration": insufficient_data,
        "eps_f": eps_f,
        "eps_phi": eps_phi,
    }

    if insufficient_data:
        result["verdict"] = "INCONCLUSIVE"
        result["reason"] = f"only {n} windows, below MIN_WINDOWS_FOR_CALIBRATION={MIN_WINDOWS_FOR_CALIBRATION}"
        Path("docs/RESULT_K_MARS_DAS_v0.1.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
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

    # positive control: channel A vs itself
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

    Path("docs/RESULT_K_MARS_DAS_v0.1.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
