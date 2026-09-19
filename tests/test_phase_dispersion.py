"""
tests/test_phase_dispersion.py

Testy Lambda_K (dyspersja fazowa) i tau_K (jej tempo zmiany) - patrz
PRE-REJESTRACJA w naglowku `modal_phase_dispersion()`/`modal_phase_tempo()`
w phase_sync.py dla pelnego uzasadnienia wzorow.

Kontrolki, dokladnie takie jak przedrejestrowane:
  Lambda_K + pozytywna: identyczne (f,phi) -> Lambda_K=0 dla kazdego t.
  Lambda_K - negatywna: rozne losowe phi, bliskie f -> Lambda_K > 0.
  tau_K + pozytywna (ANALITYCZNA): wszystkie f_i rowne -> tau_K==0
    dokladnie (nie przyblizenie).
  tau_K - negatywna: rozne f_i -> Lambda_K(t) sie zmienia -> tau_K>0.
"""
import numpy as np
import pytest

from timdr_modal import (
    Modality,
    modal_phase_dispersion,
    modal_phase_tempo,
)


# ---------------------------------------------------------------------
# Lambda_K -- dyspersja fazowa w jednej chwili t
# ---------------------------------------------------------------------

def test_identical_modalities_give_zero_dispersion_at_any_t():
    """Kontrola pozytywna: wszystkie modalnosci maja DOKLADNIE ta sama
    (f,phi) -> ich faza chwilowa jest identyczna dla kazdego t ->
    Lambda_K=0 z definicji, dla dowolnego t."""
    mods = [Modality(f=2.0, phi=0.5, A=1.0) for _ in range(5)]
    for t in [0.0, 0.3, 1.7, 100.0]:
        result = modal_phase_dispersion(mods, t)
        assert result.lambda_k < 1e-10, f"t={t}: {result.lambda_k}"
        assert result.mean_resultant_length > 1.0 - 1e-10


def test_random_phases_give_high_dispersion():
    """Kontrola negatywna: wiele modalnosci o losowych, niezaleznych
    fazach poczatkowych (rozne f, zeby uniknac przypadkowego wyrownania
    w konkretnym t) -> Lambda_K wyraznie > 0 (bliskie 1 dla duzego n,
    zgodnie z oczekiwaniem statystycznym ~1/sqrt(n) dla |Z|)."""
    rng = np.random.default_rng(123)
    n = 200
    mods = [
        Modality(f=float(1.0 + 0.01 * i), phi=float(rng.uniform(0, 2 * np.pi)), A=1.0)
        for i in range(n)
    ]
    result = modal_phase_dispersion(mods, t=0.37)
    assert result.lambda_k > 0.8
    assert result.n_modalities == n


def test_two_modalities_analytic_dispersion():
    """Recznie policzalny przypadek: 2 modalnosci, roznica faz
    chwilowej DOKLADNIE pi (przeciwne) -> Z=0 -> Lambda_K=1 dokladnie."""
    # theta_1(0)=0, theta_2(0)=pi -> exp(i*0)+exp(i*pi) = 1 + (-1) = 0
    m1 = Modality(f=0.0, phi=0.0, A=1.0)
    m2 = Modality(f=0.0, phi=np.pi, A=1.0)
    result = modal_phase_dispersion([m1, m2], t=0.0)
    assert abs(result.lambda_k - 1.0) < 1e-10
    assert abs(result.mean_resultant_length) < 1e-10


def test_dispersion_requires_at_least_one_modality():
    with pytest.raises(ValueError):
        modal_phase_dispersion([], t=0.0)


# ---------------------------------------------------------------------
# tau_K -- tempo zmiany Lambda_K
# ---------------------------------------------------------------------

def test_equal_frequencies_give_exactly_zero_tempo():
    """Kontrola pozytywna (ANALITYCZNA, nie przyblizenie): wszystkie f_i
    identyczne (rozne phi) -> wzgledne fazy sa STALE w czasie ->
    Lambda_K(t) jest stala funkcja t -> tau_K==0 dokladnie (do bledu
    numerycznego float), dla DOWOLNEGO dt."""
    rng = np.random.default_rng(7)
    mods = [Modality(f=3.0, phi=float(rng.uniform(0, 2 * np.pi)), A=1.0) for _ in range(10)]
    tau = modal_phase_tempo(mods, t=0.5, dt=0.1)
    assert tau < 1e-9

    # Sprawdzenie niezaleznosci od t/dt - stalosc powinna trzymac sie
    # wszedzie, nie tylko w jednym punkcie sprawdzonym przypadkowo.
    tau2 = modal_phase_tempo(mods, t=5.0, dt=0.01)
    assert tau2 < 1e-9


def test_different_frequencies_give_positive_tempo():
    """Kontrola negatywna: modalnosci o wyraznie roznych czestotliwosciach
    -> wzgledne fazy zmieniaja sie w czasie -> Lambda_K(t) sie zmienia ->
    tau_K > 0 dla typowego (t, dt) - sprawdzone na kilku (t,dt), zeby nie
    polegac na jednym przypadkowo dobrym punkcie."""
    mods = [
        Modality(f=1.0, phi=0.0, A=1.0),
        Modality(f=1.37, phi=0.9, A=1.0),
        Modality(f=2.11, phi=2.4, A=1.0),
        Modality(f=0.6, phi=4.0, A=1.0),
    ]
    found_positive = False
    for t in [0.0, 0.2, 0.5, 1.3, 2.7]:
        tau = modal_phase_tempo(mods, t=t, dt=0.05)
        if tau > 1e-6:
            found_positive = True
    assert found_positive, "tau_K powinno byc >0 przynajmniej w czesci punktow t"


def test_tempo_requires_positive_dt():
    mods = [Modality(f=1.0, phi=0.0, A=1.0), Modality(f=1.5, phi=1.0, A=1.0)]
    with pytest.raises(ValueError):
        modal_phase_tempo(mods, t=0.0, dt=0.0)
    with pytest.raises(ValueError):
        modal_phase_tempo(mods, t=0.0, dt=-0.1)


def test_lambda_k_oscillates_over_time_for_beating_frequencies():
    """Dodatkowa, jawnie przedrejestrowana obserwacja: dla ukladu wielu
    czestosci Lambda_K(t) NIE jest monotoniczna, tylko oscyluje (typowe
    zjawisko dudnienia) - sprawdzamy, ze w oknie czasowym wystepuje i
    wzrost, i spadek Lambda_K (nie sprawdzamy konkretnego ksztaltu, tylko
    ze to NIE jest stala funkcja rosnaca/malejaca)."""
    mods = [
        Modality(f=1.0, phi=0.0, A=1.0),
        Modality(f=1.05, phi=0.0, A=1.0),
    ]
    ts = np.linspace(0.0, 20.0, 200)
    values = [modal_phase_dispersion(mods, t).lambda_k for t in ts]
    diffs = np.diff(values)
    assert np.any(diffs > 1e-6) and np.any(diffs < -1e-6), (
        "oczekiwano oscylacji (dudnienia), nie monotonicznego trendu"
    )
