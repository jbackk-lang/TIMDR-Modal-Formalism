"""
tests/test_phase_sync.py

Testy timdr_modal.phase_sync. Zasada projektowa jak w siostrzanych repo
(TIMDR-Math-Formalism, TIMDR-Geometry-Formalism): recznie policzalne
przypadki, komentarze z obliczeniami, zero polegania na "typowym"
zachowaniu losowego seeda.

UWAGA: ten plik zostal odtad faktycznie uruchomiony przez uzytkownika
(`pytest tests/ -v`) -- ZWERYFIKOWANE, 17/17 przeszlo. Jeden test
najpierw padl z powodu bledu float w samym tescie (nie w kodzie), patrz
komentarz przy `test_is_resonant_frequency_at_threshold_is_false`
ponizej.
"""
import numpy as np
import pytest

from timdr_modal import (
    Modality,
    instantaneous_phase,
    interference,
    is_resonant,
    local_time_from_global,
)


# ---------------------------------------------------------------------
# instantaneous_phase() -- Aksjomat 4, argument sinusa
# ---------------------------------------------------------------------

def test_instantaneous_phase_scalar():
    # theta(t) = 2*pi*f*t + phi ; f=1, phi=0, t=0.25 -> theta = pi/2
    m = Modality(f=1.0, phi=0.0, A=1.0)
    assert instantaneous_phase(m, 0.25) == pytest.approx(np.pi / 2)


def test_instantaneous_phase_array():
    m = Modality(f=1.0, phi=0.0, A=1.0)
    result = instantaneous_phase(m, [0.0, 0.25, 0.5])
    expected = np.array([0.0, np.pi / 2, np.pi])
    np.testing.assert_allclose(result, expected)


def test_instantaneous_phase_includes_initial_offset():
    # phi != 0 przesuwa fazę o stałą -- theta(0) = phi dokładnie.
    m = Modality(f=3.0, phi=1.2345, A=1.0)
    assert instantaneous_phase(m, 0.0) == pytest.approx(1.2345)


# ---------------------------------------------------------------------
# interference() -- Aksjomat 4, pełna suma
# ---------------------------------------------------------------------

def test_interference_single_modality_matches_A_sin_theta():
    m = Modality(f=1.0, phi=0.0, A=2.0)
    # t=0.25 -> theta=pi/2 -> sin=1 -> I=2*1=2.0
    assert interference([m], 0.25) == pytest.approx(2.0)


def test_interference_two_modalities_hand_computed():
    # m1: A=2, theta(0)=0 -> sin=0 -> wklad 0
    # m2: A=3, phi=pi/2, f=1 -> theta(0)=pi/2 -> sin=1 -> wklad 3
    # I(0) = 0 + 3 = 3.0
    m1 = Modality(f=1.0, phi=0.0, A=2.0)
    m2 = Modality(f=1.0, phi=np.pi / 2, A=3.0)
    assert interference([m1, m2], 0.0) == pytest.approx(3.0)


def test_interference_rejects_empty_list():
    with pytest.raises(ValueError):
        interference([], 0.0)


def test_interference_array_input():
    m = Modality(f=1.0, phi=0.0, A=1.0)
    result = interference([m], [0.0, 0.25])
    # t=0 -> sin(0)=0 ; t=0.25 -> sin(pi/2)=1
    np.testing.assert_allclose(result, np.array([0.0, 1.0]), atol=1e-12)


# ---------------------------------------------------------------------
# is_resonant() -- Aksjomat 5, doslownie (obie nierownosci SCISLE)
# ---------------------------------------------------------------------

def test_is_resonant_identical_modalities():
    m_i = Modality(f=1.0, phi=0.5, A=1.0)
    m_j = Modality(f=1.0, phi=0.5, A=99.0)  # amplituda nie wchodzi do Aksjomatu 5
    assert is_resonant(m_i, m_j) is True


def test_is_resonant_frequency_at_threshold_is_false():
    # |f_i-f_j| = eps_f dokladnie -> NIE < eps_f -> nie rezonans (scisla nierownosc).
    #
    # UWAGA (znaleziono przez uzytkownika przez pytest, naprawiono tutaj):
    # oryginalna wersja uzywala m_j=Modality(f=1.0+1e-6, ...) -- to NIE daje
    # dokladnie 1e-6 roznicy w float64. 1e-6 trzeba zaokraglic do najblizszej
    # reprezentowalnej wielokrotnosci ULP w poblizu 1.0 (~2.22e-16), wiec
    # (1.0+1e-6)-1.0 wychodzi ~9.9999999977e-07 -- SCISLE MNIEJSZE niz
    # eps_f=1e-6 -- wiec is_resonant() (poprawnie, zgodnie z Aksjomatem 5)
    # zwracalo True, a test blednie oczekiwal False. To byl blad TESTU
    # (zalozenie dokladnej arytmetyki), nie bledu w is_resonant().
    #
    # Naprawa: licz roznice od 0.0, nie od 1.0 -- wtedy m_j.f jest po prostu
    # zapisana wartoscia 1e-6 (bez zadnego dodawania/zaokraglania), wiec
    # abs(m_i.f-m_j.f) to DOKLADNIE ten sam bit-wzorzec co eps_f=1e-6 ->
    # rownosc, nie "mniejsze niz" -> scisla nierownosc daje False dokladnie
    # jak zamierzone.
    m_i = Modality(f=0.0, phi=0.0, A=1.0)
    m_j = Modality(f=1e-6, phi=0.0, A=1.0)
    assert is_resonant(m_i, m_j, eps_f=1e-6, eps_phi=1e-6) is False


def test_is_resonant_phase_mismatch_is_false_even_if_frequency_matches():
    m_i = Modality(f=1.0, phi=0.0, A=1.0)
    m_j = Modality(f=1.0, phi=1.0, A=1.0)
    assert is_resonant(m_i, m_j, eps_f=1e-6, eps_phi=1e-6) is False


def test_is_resonant_within_tolerance_bands():
    m_i = Modality(f=1.0, phi=0.0, A=1.0)
    m_j = Modality(f=1.02, phi=0.03, A=1.0)
    assert is_resonant(m_i, m_j, eps_f=0.05, eps_phi=0.05) is True


# ---------------------------------------------------------------------
# local_time_from_global() -- mapa f
# ---------------------------------------------------------------------

def test_local_time_from_global_self_sync_is_identity():
    # local == global -> dopasowanie fazy do samej siebie -> t_lokalne=tau_globalne
    m = Modality(f=2.0, phi=0.7, A=1.0)
    result = local_time_from_global(m, m, tau_global=5.0)
    assert result == pytest.approx(5.0)


def test_local_time_from_global_hand_computed():
    # local f=1,phi=0 ; global f=2,phi=0 ; tau=1.0
    # theta_global(1.0) = 2*pi*2*1 + 0 = 4*pi
    # t_lokalne = (theta_global - phi_lokalne) / (2*pi*f_lokalne) = 4*pi/(2*pi*1) = 2.0
    local = Modality(f=1.0, phi=0.0, A=1.0)
    global_ = Modality(f=2.0, phi=0.0, A=1.0)
    result = local_time_from_global(local, global_, tau_global=1.0)
    assert result == pytest.approx(2.0)


def test_local_time_from_global_phase_offset_hand_computed():
    # local f=1,phi=pi/2 ; global f=1,phi=0 ; tau=0.0
    # theta_global(0)=0 ; t_lokalne = (0 - pi/2)/(2*pi*1) = -0.25
    local = Modality(f=1.0, phi=np.pi / 2, A=1.0)
    global_ = Modality(f=1.0, phi=0.0, A=1.0)
    result = local_time_from_global(local, global_, tau_global=0.0)
    assert result == pytest.approx(-0.25)


def test_local_time_from_global_rejects_zero_local_frequency():
    local = Modality(f=0.0, phi=0.0, A=1.0)
    global_ = Modality(f=1.0, phi=0.0, A=1.0)
    with pytest.raises(ValueError):
        local_time_from_global(local, global_, tau_global=1.0)


def test_local_time_from_global_array_input():
    m = Modality(f=1.0, phi=0.0, A=1.0)
    result = local_time_from_global(m, m, tau_global=[0.0, 1.0, 2.0])
    np.testing.assert_allclose(result, np.array([0.0, 1.0, 2.0]))


def test_local_time_from_global_roundtrip_matches_global_phase():
    # Wlasnosc definiujaca f: theta_lokalne(t_lokalne) == theta_globalne(tau)
    # -- sprawdzone dla kilku roznych par modalnosci/tau, nie jednego
    # recznie dobranego przypadku.
    cases = [
        (Modality(1.0, 0.0, 1.0), Modality(2.0, 0.3, 1.0), 1.7),
        (Modality(0.5, 1.1, 1.0), Modality(3.0, -0.4, 1.0), 4.2),
        (Modality(-1.0, 0.2, 1.0), Modality(1.0, 0.0, 1.0), 0.9),
    ]
    for local, global_, tau in cases:
        t_local = local_time_from_global(local, global_, tau)
        assert instantaneous_phase(local, t_local) == pytest.approx(
            instantaneous_phase(global_, tau)
        )
