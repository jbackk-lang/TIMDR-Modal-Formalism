"""Niezależne przeliczenie wyników gałęzi K (sieć energetyczna) z SUROWYCH danych dla audytu twierdzeń README.

Własna implementacja (NumPy/pandas, bez scipy i bez importu skryptów _grid_freq_k_run*.py): okna, odtrendowanie
liniowe (lstsq), korelacja Pearsona zero-lag, szczyt FFT, null permutacyjny z tym samym schematem losowania
(numpy default_rng(0), 2000 permutacji) co skrypty — zgodność oznacza zgodność implementacji, a z z innym ziarnem
jest raportowane opisowo. Reguły: docs/audit/CLAIM_AUDIT_PREREG.md.

Użycie (katalog repo):  python docs/audit/recompute_k.py sync   # SYNC01.csv: bieg, plik, v0.1-v0.4
                        python docs/audit/recompute_k.py v05    # PT_LI01_100ms.zip + TUR-IS01_100ms.zip
Dane: katalog TIMDR_DATA (domyślnie ../DATA obok repozytorium). Wynik: docs/audit/RECOMPUTE_K.json (dopisywany).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = Path(os.environ.get("TIMDR_DATA", HERE.parents[2] / "DATA"))
OUT = HERE / "RECOMPUTE_K.json"
W_SEC, N_PERM = 600, 2000


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def detrend_rows(W: np.ndarray) -> np.ndarray:
    n = W.shape[1]
    X = np.column_stack([np.arange(n, dtype=float), np.ones(n)])
    coef, *_ = np.linalg.lstsq(X, W.T, rcond=None)
    return W - (X @ coef).T


def windows(s: np.ndarray, per: int) -> np.ndarray:
    k = len(s) // per
    return s[: k * per].reshape(k, per)


def corr_stats(a: np.ndarray, b: np.ndarray, per: int) -> dict:
    A, B = detrend_rows(windows(a, per)), detrend_rows(windows(b, per))
    na, nb = np.linalg.norm(A, axis=1), np.linalg.norm(B, axis=1)
    r = (A * B).sum(1) / (na * nb)
    real = float(r.mean())

    def null(seed):
        rng = np.random.default_rng(seed)
        out = np.empty(N_PERM)
        for i in range(N_PERM):
            p = rng.permutation(len(r))
            out[i] = np.mean((A * B[p]).sum(1) / (na * nb[p]))
        return out
    n0, n1 = null(0), null(12345)
    pos = (A * A).sum(1) / (na * na)
    return {"n_windows": int(len(r)), "mean_r": real, "median_r": float(np.median(r)),
            "p25_p75": [float(np.percentile(r, 25)), float(np.percentile(r, 75))],
            "null_mean": float(n0.mean()), "null_std": float(n0.std()),
            "z": float((real - n0.mean()) / n0.std()), "z_seed12345": float((real - n1.mean()) / n1.std()),
            "p": float((np.sum(n0 >= real) + 1) / (N_PERM + 1)),
            "positive_control_mean_r": float(pos.mean()), "positive_control_min_r": float(pos.min())}


def peak_bins(s: np.ndarray, per: int, pad: int = 1, demean_first: bool = False) -> np.ndarray:
    """Indeks szczytu |rfft| bez składowej stałej (jak _fft_peak_f_phi_A: średnia odejmowana PO dopełnieniu)."""
    W = windows(s, per)
    if demean_first:
        W = W - W.mean(1, keepdims=True)
    if pad > 1:
        W = np.pad(W, ((0, 0), (0, per * (pad - 1))))
    W = W - W.mean(1, keepdims=True)
    spec = np.abs(np.fft.rfft(W, axis=1))
    return 1 + spec[:, 1:].argmax(1)


def tie_stats(a, b, per, **kw) -> dict:
    ka, kb = peak_bins(a, per, **kw), peak_bins(b, per, **kw)
    bins = np.union1d(ka, kb)
    pa = np.array([(ka == k).mean() for k in bins])
    pb = np.array([(kb == k).mean() for k in bins])
    return {"tie_fraction": float((ka == kb).mean()), "distinct_peak_bins": int(len(bins)),
            "chance_agreement_from_marginals": float((pa * pb).sum()),
            "chance_agreement_uniform": float(1 / len(bins))}


def save(key, value):
    d = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    d[key] = value
    OUT.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_sync():
    f = DATA / "SYNC01.csv"
    df = pd.read_csv(f, sep=";", usecols=["Time", "f50_PT", "QI_PT", "f50_TR", "QI_TR"])
    t = pd.to_datetime(df.Time)
    ok = ((df.QI_PT == 0) & (df.QI_TR == 0)).to_numpy()
    # najdluzszy ciagly odcinek wierszy z poprawna jakoscia obu stacji
    edges = np.diff(np.concatenate([[0], ok.astype(int), [0]]))
    starts, ends = np.where(edges == 1)[0], np.where(edges == -1)[0]
    lens = ends - starts
    order = np.argsort(-lens)
    runs = [{"start_row": int(starts[i]), "len": int(lens[i]), "start_time": str(t[starts[i]])} for i in order[:3]]
    save("sync01", {"sha256": sha(f), "rows": int(len(df)), "first": str(t.iloc[0]), "last": str(t.iloc[-1]),
                    "span_days": float((t.iloc[-1] - t.iloc[0]).total_seconds() / 86400 + 1 / 86400),
                    "dt_s_median": float(t.diff().dt.total_seconds().median()),
                    "longest_valid_runs": runs, "unit_hint_abs_max": float(df.f50_PT[ok].abs().max())})
    pt, tr = df.f50_PT.to_numpy(float), df.f50_TR.to_numpy(float)
    for key, start, n in (("v01_v03", 2071846, 238902), ("v04", 2913363, 183407)):
        # skrypty: skiprows=range(1, START+1) -> pierwszy wiersz danych ma indeks START w ramce bez naglowka
        a, b = pt[start:start + n], tr[start:start + n]
        rec = {"start_time": str(t[start]), "end_time": str(t[start + n - 1]), "qi_all_zero": bool(ok[start:start + n].all()),
               "hours": n / 3600}
        if key == "v01_v03":
            rec["v01"] = tie_stats(a, b, W_SEC)
            rec["v02"] = tie_stats(a, b, W_SEC, pad=16)
            rec["v02_diag_demean_before_pad"] = tie_stats(a, b, W_SEC, pad=16, demean_first=True)
        rec["corr"] = corr_stats(a, b, W_SEC)
        save(key, rec)


def run_v05():
    fp, ft = DATA / "PT_LI01_100ms.zip", DATA / "TUR-IS01_100ms.zip"
    sp, st, n = 1767960, 1837470, 269919
    a = pd.read_csv(fp, sep=";", skiprows=range(1, sp + 1), nrows=n)
    b = pd.read_csv(ft, sep=";", skiprows=range(1, st + 1), nrows=n)
    aligned = bool((a.Time.to_numpy() == b.Time.to_numpy()).all())
    ta = pd.to_datetime(a.Time)
    save("v05", {"sha256_pt": sha(fp), "sha256_tur": sha(ft), "time_aligned": aligned,
                 "qi_all_zero": bool((a.QI_PT == 0).all() and (b.QI_TR == 0).all()),
                 "start_time": str(ta.iloc[0]), "end_time": str(ta.iloc[-1]),
                 "dt_s_median": float(ta.diff().dt.total_seconds().median()),
                 "corr": corr_stats(a.f50_PT.to_numpy(float), b.f50_TR.to_numpy(float), W_SEC * 10)})


if __name__ == "__main__":
    {"sync": run_sync, "v05": run_v05}[sys.argv[1]]()
    print(OUT.read_text(encoding="utf-8"))
