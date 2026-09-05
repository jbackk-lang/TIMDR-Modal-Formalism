"""
tests/test_real_data_validation.py

Testy timdr_modal.real_data_validation:

  - testy JEDNOSTKOWE ekstrakcji FFT (f,phi,A) i konwersji fazy na
    synchronicznych/syntetycznych sygnalach o znanych parametrach --
    zawsze uruchamiane, nie wymagaja realnych danych, sprawdzaja
    POPRAWNOSC MATEMATYCZNA metody (konwersja konwencji cos->sin
    DFT, przeliczenie fazy lokalnej okna na wspolny t=0 sladu)
    niezaleznie od tego, co akurat pokazuja realne dane.

  - testy na PRAWDZIWYCH danych sejsmicznych trzesienia ziemi
    Ridgecrest 2019 (stacje CLC/RIO, repo siostrzane
    TIMDR-Earthquake-Core) -- pomijane (skip) z jasnym powodem, jesli
    to repo nie jest dostepne w danym checkoutcie, zamiast falszywie
    failowac na brakujacym pliku.

UWAGA O WYKONANIU: pisane w sesji bez dostepu do sandboxa
bash/pytest (workspace niedostepny) -- wzory sprawdzone recznie
(patrz komentarze i wyprowadzenia w real_data_validation.py), ale
`pytest tests/ -v` NIE zostalo tu faktycznie uruchomione przez
model, tylko przez uzytkownika po fakcie -- ten sam wzorzec co w
`phase_sync.py`/`test_phase_sync.py` ("napisane bez sandboxa, potem
zweryfikowane").
"""
import os

import numpy as np
import pytest

from timdr_modal.phase_sync import Modality, instantaneous_phase
from timdr_modal.real_data_validation import (
    RIDGECREST_FS_HZ,
    RIDGECREST_STATIONS,
    _default_data_dir,
    _fft_peak_f_phi_A,
    _local_phase_to_global,
    _wrap_to_pi,
    calibrate_epsilons,
    extract_modalities,
    load_station_csv,
    real_data_resonance_report,
)


def _real_data_present() -> bool:
    d = _default_data_dir()
    return all(os.path.isfile(os.path.join(d, fname)) for fname in RIDGECREST_STATIONS.values())


requires_real_data = pytest.mark.skipif(
    not _real_data_present(),
    reason=(
        "realne dane Ridgecrest 2019 (TIMDR-Earthquake-Core/data/ridgecrest_2019/"
        "real_waveform_CLC_RIO/*.csv) niedostepne w tym checkoutcie -- oczekiwane "
        "repo siostrzane wzgledem TIMDR-Modal-Formalism, patrz "
        "real_data_validation.py:_default_data_dir()"
    ),
)


# ---------------------------------------------------------------------
# _wrap_to_pi()
# ---------------------------------------------------------------------

def test_wrap_to_pi_identity_inside_range():
    assert _wrap_to_pi(0.5) == pytest.approx(0.5)


def test_wrap_to_pi_wraps_above_pi():
    assert _wrap_to_pi(1.5 * np.pi) == pytest.approx(-0.5 * np.pi)


def test_wrap_to_pi_wraps_below_negative_pi():
    assert _wrap_to_pi(-1.5 * np.pi) == pytest.approx(0.5 * np.pi)


# ---------------------------------------------------------------------
# _fft_peak_f_phi_A() -- ekstrakcja na SYNTETYCZNEJ sinusoidzie o
# znanych parametrach, bin-dokladnej (f0=k*fs/n pada dokladnie na bin
# FFT). Dla bin-dokladnej, nie-zdegenerowanej czestotliwosci (k!=0,
# n nie dzieli 2k) wyraz "ujemnej czestotliwosci" w wyprowadzeniu z
# naglowka modulu znika DOKLADNIE (skonczona suma geometryczna o
# liczniku =0) -- wiec metoda jest tu matematycznie dokladna, nie
# tylko w przyblizeniu, i tolerancje ponizej moga byc ciasne.
# ---------------------------------------------------------------------

def test_fft_peak_recovers_bin_exact_sine_f_phi_A():
    fs = 100.0
    n = 1000  # 10s okno, rozdzielczosc binu = 0.1 Hz
    f0 = 2.0  # k=20 -> f0=k*fs/n=2.0 Hz, dokladnie na binie; n nie dzieli 2k=40
    phi0 = 0.7
    a0 = 3.0
    t_local = np.arange(n) / fs
    s = a0 * np.sin(2.0 * np.pi * f0 * t_local + phi0)

    f_peak, phi_local, a_peak = _fft_peak_f_phi_A(s, fs)

    assert f_peak == pytest.approx(f0, abs=1e-9)
    assert phi_local == pytest.approx(phi0, abs=1e-6)
    assert a_peak == pytest.approx(a0, abs=1e-6)


def test_fft_peak_phase_convention_matches_sin_not_cos():
    # Test scisle celowany w blad latwy do popelnienia: uzycie fazy
    # DFT wprost (konwencja cosinusowa numpy.fft) bez korekty +pi/2
    # do konwencji SINUSOWEJ Aksjomatu 4 (interference() uzywa sin,
    # nie cos). phi0=0.0 -> sin(w*0+0)=0 w probce 0 -- najbardziej
    # jednoznaczny przypadek do odroznienia obu konwencji: bez korekty
    # phi_local wyszloby ok. -pi/2, nie ~0.
    fs = 100.0
    n = 1000
    f0 = 2.0
    phi0 = 0.0
    a0 = 1.0
    t_local = np.arange(n) / fs
    s = a0 * np.sin(2.0 * np.pi * f0 * t_local + phi0)

    _, phi_local, _ = _fft_peak_f_phi_A(s, fs)
    assert phi_local == pytest.approx(0.0, abs=1e-6)
    assert abs(phi_local - (-np.pi / 2.0)) > 1.0  # NIE konwencja cosinusowa


def test_fft_peak_rejects_too_short_window():
    with pytest.raises(ValueError):
        _fft_peak_f_phi_A(np.array([1.0, 2.0]), fs=100.0)


# ---------------------------------------------------------------------
# _local_phase_to_global() -- konwersja fazy lokalnej okna (przy
# globalnym t_start) na faze poczatkowa Modality wzgledem wspolnego
# t=0 sladu. Testowane WLASNOSCIA ROUNDTRIP przez instantaneous_phase
# (ten sam wzorzec co test_local_time_from_global_roundtrip_matches_
# global_phase w tests/test_phase_sync.py) -- z f/t_start CELOWO NIE
# bin-dokladnymi wzgledem zadnego okna, zeby test byl zdolny wykryc
# blad znaku (patrz uzasadnienie w komentarzu przy implementacji tej
# funkcji w real_data_validation.py: dla bin-dokladnych czestotliwosci
# na siatce okien t_start=j*window_sec czlon korekcyjny jest ZAWSZE
# wielokrotnoscia 2*pi, wiec test na takich danych nie odroznilby
# poprawnego wzoru od blednego znaku).
# ---------------------------------------------------------------------

def test_local_phase_to_global_roundtrips_via_instantaneous_phase():
    cases = [
        (1.0, 2.0, 0.37),
        (-2.5, 0.5, 3.2),
        (0.0, 5.0, 10.0),
        (3.0, -1.3, 0.9),
        (-3.0, 17.0, 60.04),  # rzedu wielkosci realnego t_event Ridgecrest
    ]
    for phi_local, f, t_start in cases:
        phi_global = _local_phase_to_global(phi_local, f, t_start)
        m = Modality(f=f, phi=phi_global, A=1.0)
        theta_at_t_start = float(instantaneous_phase(m, t_start))
        diff = _wrap_to_pi(theta_at_t_start - phi_local)
        assert diff == pytest.approx(0.0, abs=1e-9)


def test_local_phase_to_global_identity_when_t_start_zero():
    # t_start=0 -> zaden przelicznik, phi_global==phi_local (mod 2*pi)
    assert _local_phase_to_global(1.234, f=3.0, t_start=0.0) == pytest.approx(1.234)


# ---------------------------------------------------------------------
# extract_modalities() -- pelny potok (FFT per okno + konwersja fazy)
# na SYNTETYCZNYCH danych (tmp CSV w konwencji t,s bez naglowka),
# niezaleznie od obecnosci realnych danych Ridgecrest.
# ---------------------------------------------------------------------

def _write_synthetic_station_csv(tmp_path, filename, f0, phi0, a0, n_total, fs):
    t = np.arange(n_total) / fs
    s = a0 * np.sin(2.0 * np.pi * f0 * t + phi0)
    path = tmp_path / filename
    with open(path, "w", newline="") as f:
        for ti, si in zip(t, s):
            f.write(f"{ti},{si}\n")
    return str(tmp_path)


def test_extract_modalities_basic_shape_and_metadata(tmp_path):
    fs = RIDGECREST_FS_HZ
    f0, phi0, a0 = 2.0, 0.3, 1.5  # bin-dokladne dla window_sec=5.0 (n_per_window=500)
    n_total = 1000  # 2 pelne okna po 5s
    data_dir = _write_synthetic_station_csv(tmp_path, "CLC_HHZ.csv", f0, phi0, a0, n_total, fs)

    mods = extract_modalities("CLC", window_sec=5.0, data_dir=data_dir)

    assert len(mods) == 2
    assert [m.window_index for m in mods] == [0, 1]
    assert [m.station for m in mods] == ["CLC", "CLC"]
    assert mods[0].t_start_s == pytest.approx(0.0)
    assert mods[1].t_start_s == pytest.approx(5.0)
    for wm in mods:
        assert wm.modality.f == pytest.approx(f0, abs=1e-6)
        assert wm.modality.A == pytest.approx(a0, abs=1e-4)
    # Okno 0 zaczyna sie w t_start=0 -- tam phi_global==phi_local==phi0
    # wprost, bez zadnej korekty do sprawdzenia (korekta dla okna 1 na
    # tej bin-dokladnej, stacjonarnej sinusoidzie jest matematycznie
    # zawsze wielokrotnoscia 2*pi -- patrz test_local_phase_to_global_*
    # powyzej za wlasciwy test poprawnosci znaku korekty).
    assert mods[0].modality.phi == pytest.approx(phi0, abs=1e-4)


def test_extract_modalities_empty_when_shorter_than_one_window(tmp_path):
    fs = RIDGECREST_FS_HZ
    data_dir = _write_synthetic_station_csv(tmp_path, "RIO_HHZ.csv", 2.0, 0.0, 1.0, n_total=100, fs=fs)
    mods = extract_modalities("RIO", window_sec=5.0, data_dir=data_dir)  # 5s*100Hz=500 > 100 probek
    assert mods == []


def test_load_station_csv_rejects_unknown_station(tmp_path):
    with pytest.raises(ValueError):
        load_station_csv("NOT_A_STATION", data_dir=str(tmp_path))


def test_load_station_csv_missing_file_raises_clear_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_station_csv("CLC", data_dir=str(tmp_path))


# ---------------------------------------------------------------------
# Testy na PRAWDZIWYCH danych Ridgecrest 2019 -- pomijane, jesli repo
# siostrzane TIMDR-Earthquake-Core nie jest dostepne.
# ---------------------------------------------------------------------

@requires_real_data
def test_load_station_csv_real_data_shapes():
    for station in RIDGECREST_STATIONS:
        t, s = load_station_csv(station)
        assert len(t) == len(s)
        assert len(t) == 36001  # udokumentowane w naglowku modulu / results.txt
        assert np.allclose(np.diff(t), 1.0 / RIDGECREST_FS_HZ, atol=1e-6)


@requires_real_data
def test_extract_modalities_real_window_count_and_spacing():
    mods = extract_modalities("CLC", window_sec=10.0)
    assert len(mods) == 36  # 36001 // 1000
    assert [m.window_index for m in mods] == list(range(36))
    assert mods[1].t_start_s == pytest.approx(10.0)


@requires_real_data
def test_real_data_resonance_report_structure_and_invariants():
    report = real_data_resonance_report(window_sec=10.0, n_permutations=200, seed=1)

    assert report.n_paired_windows == 36
    assert 0 <= report.n_resonant_real <= report.n_paired_windows
    assert 0.0 <= report.resonance_rate_real <= 1.0
    assert 0.0 <= report.p_value <= 1.0
    assert report.null_resonance_rates.shape == (200,)

    # Kontrola pozytywna: stacja sparowana sama ze soba MUSI dac
    # rezonans w 100% okien (f_i=f_j, phi_i=phi_j dokladnie, eps>0) --
    # to jest gwarantowane konstrukcyjnie (is_resonant porownuje
    # modalnosc z nia sama), niezaleznie od tresci realnych danych.
    assert report.positive_control_rate == pytest.approx(1.0)
    assert 0.0 <= report.positive_control_p_value <= 1.0


@requires_real_data
def test_calibrate_epsilons_sufficient_data_at_default_window():
    calib = calibrate_epsilons(window_sec=10.0)
    assert calib.insufficient_data is False
    assert calib.n_paired_windows == 36
    assert calib.eps_f_suggested is not None and calib.eps_f_suggested >= 0.0
    assert calib.eps_phi_suggested is not None and 0.0 <= calib.eps_phi_suggested <= np.pi


@requires_real_data
def test_calibrate_epsilons_flags_insufficient_data_for_coarse_window():
    # window_sec=200s na sladzie 360.01s daje TYLKO 1 okno (36001//20000=1)
    # -- zdecydowanie ponizej progu kalibracji (20) -- MUSI zwrocic
    # insufficient_data=True zamiast fikcyjnej precyzji z jednej pary.
    calib = calibrate_epsilons(window_sec=200.0)
    assert calib.insufficient_data is True
    assert calib.eps_f_suggested is None
    assert calib.eps_phi_suggested is None
