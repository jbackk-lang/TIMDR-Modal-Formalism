"""
timdr_modal/modal_anchor.py

Galaz K w praktyce: samokorygujaca kotwica modalna, przejscie K->G (faza -> ksztalt modu) oraz parametry
wykonalnosci galezi K (N_cyk, L_koh, koherencja kanalow z kotwica). Funkcje przeniesione 1:1 (bez importu -- repo
niezalezne) z wersji walidowanych pre-rejestrowanymi testami w GIA-TIMDR; zgodnosc liczbowa pilnowana testami
wzorcowymi (tests/test_modal_anchor.py).

Skad i na czym sprawdzone (pary PREREG/RESULT w GIA-TIMDR/docs/geometry/):
  anchor_frequencies   core/kw51_modal_anchor.py       most kolejowy KW51: AUC 1,00 (= OMA/SSI autorow), AR 0,67 -- SUPPORTED
                       core/real_lanl_modal_anchor.py  rama LANL: ciezkosc uszkodzenia rho -0,57 -> +0,98 -- SUPPORTED
                       core/hbta_modal_anchor.py       most Hell Bridge, sama kotwica: 0,65 vs AR 0,79 -- NOT SUPPORTED
  mode_shapes          core/hbta_modal_curvature.py    ksztalt z faza 0,78 (krzywizna 0,72, AR 0,80) -- NOT SUPPORTED sam,
                       core/hbta_discontinuity.py      ale jako wejscie przerwy ciaglosci: uszkodzenia pionowe 0,93-0,94
  n_cycles, coherence_cycles  core/transition_params.py   regula wykonalnosci (docs/theory/TIMDR_Parametry_Przejsc.md)
  anchor_coherence     regula doboru kotwic z PREREG_HBTA_MODAL_CURVATURE_v0_2 (gamma^2 >= 0,8, mediana i p10)

Obserwacja z testow: kotwica uzyta sama wygrywa, gdy uszkodzenie zmienia globalna sztywnosc (KW51, LANL); przy
uszkodzeniu lokalnym potrzebny jest most K->G (faza -> ksztalt) i szukanie przerwy w przestrzeni (repo
TIMDR-Structural-Health, DiscontinuityBaseline).

Wymaga scipy (Welch / widmo wzajemne) -- zgodnie z implementacja walidowana.
"""
from __future__ import annotations

from typing import Dict, List, Sequence

import numpy as np
from scipy.signal import coherence, csd, decimate, welch

TOL = 0.04        # samokorekta kotwicy: +-4% wokol czestotliwosci modelu modalnego
GAMMA2_MIN = 0.8  # koherencja kanalow z kotwica (mediana i 10. percentyl) wymagana dla kotwicy


def _decim(x: np.ndarray, q: int) -> np.ndarray:
    """Decymacja FIR zero-phase w krokach (preferowane 10, 8, 4, 2) -- jak w walidacji."""
    y = np.asarray(x, float)
    while q > 1:
        s = 10 if q % 10 == 0 else (8 if q % 8 == 0 else (4 if q % 4 == 0 else (2 if q % 2 == 0 else q)))
        y = decimate(y, s, ftype="fir", zero_phase=True); q //= s
    return y


def _mean_normalized_spectrum(Y: np.ndarray, fs: float, nperseg: int):
    f, P = welch(Y - Y.mean(1, keepdims=True), fs, nperseg=min(nperseg, Y.shape[1]))
    return f, (P / np.median(P, 1, keepdims=True)).mean(0)


def _anchor_bin(f: np.ndarray, S: np.ndarray, a: float) -> int:
    m = np.where(np.abs(f - a) <= TOL * a)[0]
    if len(m) == 0:
        raise ValueError(f"kotwica {a} Hz poza zakresem widma lub za waska rozdzielczosc")
    return int(m[np.argmax(S[m])])


def anchor_frequencies(X: np.ndarray, fs: float, anchors: Sequence[float], q: int = 1, nperseg: int = 1024) -> List[float]:
    """Samokorygujaca kotwica. X: (kanaly, probki). Widmo usrednione po kanalach (kazdy znormalizowany mediana);
    w +-4% wokol kazdej kotwicy z modelu szczyt z interpolacja paraboliczna (w skali log). Zwraca czestotliwosci [Hz]."""
    Y = np.stack([_decim(c, q) for c in np.atleast_2d(X)])
    f, S = _mean_normalized_spectrum(Y, fs / q, nperseg)
    out = []
    for a in anchors:
        j = _anchor_bin(f, S, a)
        if 0 < j < len(S) - 1:
            y0, y1, y2 = np.log(S[j - 1:j + 2]); d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-12)
        else:
            d = 0.0
        out.append(float(f[j] + d * (f[1] - f[0])))
    return out


def mode_shapes(X: np.ndarray, ref: np.ndarray, fs: float, anchors: Sequence[float], nperseg: int = 2048) -> np.ndarray:
    """Przejscie K->G: ksztalty modow z faza. H_i = S_i,ref / S_ref,ref przy kotwicy (samokorekta +-4%),
    obrot do osi rzeczywistej (theta = arg(sum H^2)/2), psi = Re(H e^{-i theta}), znormalizowane.
    ref: sila/przyspieszenie wzbudnika albo kanal odniesienia. Zwraca (kotwice, kanaly); znak umowny (align_signs)."""
    X = np.atleast_2d(X); Xc = X - X.mean(1, keepdims=True); r = np.asarray(ref, float) - np.mean(ref)
    f, Prr = welch(r, fs, nperseg=nperseg); _, P = welch(Xc, fs, nperseg=nperseg)
    S = (P / np.median(P, 1, keepdims=True)).mean(0); _, Sxr = csd(Xc, r[None, :], fs, nperseg=nperseg)
    out = []
    for a in anchors:
        j = _anchor_bin(f, S, a)
        H = Sxr[:, j] / (Prr[j] + 1e-30); th = 0.5 * np.angle(np.sum(H ** 2)); psi = np.real(H * np.exp(-1j * th))
        out.append(psi / (np.linalg.norm(psi) + 1e-30))
    return np.array(out)


def align_signs(shapes: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Znak kazdego ksztaltu zgodny z ksztaltem wzorcowym."""
    s = np.array(shapes, float, copy=True)
    for k in range(len(s)):
        if np.dot(s[k], reference[k]) < 0:
            s[k] = -s[k]
    return s


def mac(a: np.ndarray, b: np.ndarray) -> float:
    """Modal Assurance Criterion (znany odpowiednik porownania ksztaltow; 1 - MAC = odniesienie w teście HBTA v0.2)."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    return float(np.dot(a, b) ** 2 / (np.dot(a, a) * np.dot(b, b) + 1e-30))


# ---------------- wykonalnosc galezi K (liczona PRZED testem) ----------------
def n_cycles(window_s: float, f_rhythm: float) -> float:
    """N_cyk: liczba cykli rytmu w oknie; < 10 -> grzebien sita rozmyty."""
    return float(window_s * f_rhythm)


def coherence_cycles(x, fs, f0, rel_band=0.2):
    """L_koh ~ f0 / FWHM linii przy f0 (widmo z oknem Hanna). Nierozdzielona linia -> dolna granica = N_cyk.
    L_koh < N_cyk -> wyprostowac rure (zegar katowy / zdarzeniowy). Nie odroznia tlumienia od dryfu."""
    x = np.asarray(x, float) - np.mean(x); n = len(x)
    S = np.abs(np.fft.rfft(x * np.hanning(n), 8 * n)) ** 2; f = np.fft.rfftfreq(8 * n, 1 / fs)
    m = np.abs(f - f0) <= rel_band * f0
    if not m.any():
        return float("nan")
    i0 = np.where(m)[0][np.argmax(S[m])]; half = S[i0] / 2
    lo = i0
    while lo > 0 and S[lo] > half:
        lo -= 1
    hi = i0
    while hi < len(S) - 1 and S[hi] > half:
        hi += 1
    fwhm = max(f[hi] - f[lo], 2.0 * fs / n)
    return float(f[i0] / fwhm)


def anchor_coherence(X: np.ndarray, ref: np.ndarray, fs: float, anchors: Sequence[float], nperseg: int = 2048,
                     gamma2_min: float = GAMMA2_MIN) -> List[Dict[str, float]]:
    """Dobor kotwic do ksztaltu modu: koherencja gamma^2 kazdego kanalu z odniesieniem przy kotwicy (samokorekta +-4%);
    kotwica zostaje, gdy mediana i 10. percentyl po kanalach >= gamma2_min. Liczyc na rejestracji uczacej, przed testem."""
    X = np.atleast_2d(X); Xc = X - X.mean(1, keepdims=True); r = np.asarray(ref, float) - np.mean(ref)
    f, C = coherence(Xc, r[None, :], fs, nperseg=nperseg)
    _, P = welch(Xc, fs, nperseg=nperseg); S = (P / np.median(P, 1, keepdims=True)).mean(0)
    out = []
    for a in anchors:
        j = _anchor_bin(f, S, a); c = C[:, j]
        med, p10 = float(np.median(c)), float(np.percentile(c, 10))
        out.append({"anchor": float(a), "f": float(f[j]), "median": med, "p10": p10,
                    "keep": bool(med >= gamma2_min and p10 >= gamma2_min)})
    return out
