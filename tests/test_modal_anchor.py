"""
tests/test_modal_anchor.py

Testy timdr_modal.modal_anchor. Wartosci wzorcowe policzone implementacja walidowana (GIA-TIMDR: kw51_modal_anchor,
hbta_modal_curvature, transition_params; identyczna kopia w TIMDR-Structural-Health/timdr_shm.py) na tym samym
syntetycznym sygnale -- zgodnosc bit w bit sprawdzona przy przenoszeniu (2026-09-27).
Test na realnych danych (Hell Bridge, regula doboru kotwic) pomijany, gdy brak pliku w TIMDR_DATA (domyslnie ../DATA).
"""
import os
from pathlib import Path

import numpy as np
import pytest
from scipy.signal import iirpeak, lfilter

from timdr_modal import (align_signs, anchor_coherence, anchor_frequencies, coherence_cycles, mac, mode_shapes,
                         n_cycles)

PHI1 = np.sin(np.pi * np.arange(1, 7) / 7)          # 1. ksztalt belki (6 czujnikow)
PHI2 = np.sin(2 * np.pi * np.arange(1, 7) / 7)      # 2. ksztalt (zmiana znaku w srodku)


def _synth():
    """Belka z dwoma modami (5,2 Hz i 12,6 Hz) wzbudzana szumem ref; 6 kanalow + szum pomiarowy."""
    rng = np.random.default_rng(7); fs = 100.0; n = 20000
    ref = rng.standard_normal(n)
    b1, a1 = iirpeak(5.2, 20, fs); b2, a2 = iirpeak(12.6, 25, fs)
    X = np.outer(PHI1, lfilter(b1, a1, ref)) + np.outer(PHI2, lfilter(b2, a2, ref)) + 0.05 * rng.standard_normal((6, n))
    return X, ref, fs


def test_anchor_self_corrects_golden():
    # model mowi 5,0 / 12,5 Hz; kotwica sama przesuwa sie do rzeczywistych modow (w granicy +-4%)
    X, _, fs = _synth()
    f = anchor_frequencies(X, fs, [5.0, 12.5])
    assert f == pytest.approx([5.205248703166205, 12.540852182251298], abs=1e-12)
    fq = anchor_frequencies(X, fs, [5.0, 12.5], q=2)       # z decymacja
    assert fq == pytest.approx([5.137100749945629, 12.546139885557194], abs=1e-12)


def test_anchor_out_of_range_raises():
    X, _, fs = _synth()
    with pytest.raises(ValueError):
        anchor_frequencies(X, fs, [80.0])                  # powyzej Nyquista 50 Hz


def test_mode_shapes_phase_gives_signed_shape():
    # przejscie K->G: faza z widma wzajemnego daje ksztalt ZE ZNAKIEM (2. mod zmienia znak w srodku belki)
    X, ref, fs = _synth()
    sh = mode_shapes(X, ref, fs, [5.0, 12.5])
    gold = [[0.237345, 0.421265, 0.517753, 0.516441, 0.423488, 0.228213],
            [0.423642, 0.522332, 0.231951, -0.228004, -0.520051, -0.414074]]
    assert np.round(sh, 6).tolist() == gold
    assert mac(sh[0], PHI1) > 0.999 and mac(sh[1], PHI2) > 0.999
    assert np.sign(sh[1][:3]).tolist() == [1, 1, 1] and np.sign(sh[1][3:]).tolist() == [-1, -1, -1]


def test_align_signs_and_mac():
    ref = np.array([PHI1, PHI2]); flipped = np.array([-PHI1, PHI2])
    assert np.allclose(align_signs(flipped, ref), ref)
    assert mac(PHI1, -3 * PHI1) == pytest.approx(1.0)      # MAC niezalezny od skali i znaku
    assert mac(PHI1, PHI2) < 0.05


def test_feasibility_cycles():
    assert n_cycles(0.1, 50) == pytest.approx(5.0)         # < 10: sito bez szans
    x = np.sin(2 * np.pi * 7 * np.arange(4000) / 200) + 0.1 * np.random.default_rng(1).standard_normal(4000)
    assert coherence_cycles(x, 200, 7) == pytest.approx(70.0)   # linia nierozdzielona: granica okna Hanna f0/(2/T) = 7/(2/20 s)


def test_anchor_coherence_keeps_modes_drops_empty_band():
    X, ref, fs = _synth()
    r = anchor_coherence(X, ref, fs, [5.0, 12.5, 30.0])
    assert [x["keep"] for x in r] == [True, True, False]
    assert r[0]["median"] == pytest.approx(0.9431973424994997, abs=1e-12)


_DATA = Path(os.environ.get("TIMDR_DATA", Path(__file__).resolve().parents[2] / "DATA"))
_H5 = _DATA / "hell_bridge" / "data_100Hz.h5"


@pytest.mark.skipif(not _H5.is_file(), reason="brak DATA/hell_bridge/data_100Hz.h5 (Hell Bridge Test Arena)")
def test_hell_bridge_anchor_selection_matches_prereg():
    """PREREG_HBTA_MODAL_CURVATURE_v0_2: na UDS_01 zostaja 6,86/7,42/17,26/24,12/30,08/32,32, odpadaja 9,40 i 12,79.
    Rekonstrukcja reguly daje te sama decyzje (liczby: 9,40 mediana 0,51 = PREREG; 12,79 mediana 0,79, p10 0,62 --
    PREREG podaje p10 0,50; pierwotne liczenie nie bylo zapisane w kodzie)."""
    h5py = pytest.importorskip("h5py")
    names = [f"AL{i:02d}" for i in range(1, 41)]
    with h5py.File(_H5, "r") as f:
        acc = f["MVS_P2_UDS_NM_Z_01"]["acceleration"]
        X = np.array([acc[n]["z"][:] for n in names]); a = acc["AS"]["z"][:]
    r = anchor_coherence(X, a, 100.0, [6.86, 7.42, 9.40, 12.79, 17.26, 24.12, 30.08, 32.32])
    assert [x["keep"] for x in r] == [True, True, False, False, True, True, True, True]
    assert r[2]["median"] == pytest.approx(0.51, abs=0.01)
