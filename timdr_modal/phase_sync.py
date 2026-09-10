"""
timdr_modal/phase_sync.py

Galaz K (modalna) chronoprocesu: mapa synchronizacji faz `f`, ktora
daje sprawdzalna tresc postulatowi "t_lokalne = f(tau_globalne)" z
sekcji 7.3 glownego README GIA-TIMDR. Pelny opis Chronoprocesu
Xi=(T,x,Gamma,phi), w tym tej konstrukcji: `GIA-TIMDR/docs/theory/
TIMDR_Chronoprocess.md` (sekcja 4) oraz `GIA-TIMDR/SKILL_timdr-signal-
framework.md` (sekcja 5, skrocona wersja).

Obiekt modalnosci `(f,phi,A)` -- czestotliwosc/faza/amplituda -- jest
DOKLADNIE Aksjomatem 3 z GIA-TIMDR/docs/theory/Axioms_K_TIMDR.md:

    M = M(I) = {(f_i, phi_i, A_i)}

Aksjomat 4 definiuje interferencje:

    I(t) = sum_i A_i * sin(2*pi*f_i*t + phi_i)

-- czyli FAZA CHWILOWA modalnosci i w chwili t to
theta_i(t) = 2*pi*f_i*t + phi_i (argument sinusa), a phi_i samo w
sobie jest tylko faza POCZATKOWA (stala, wartosc w t=0). Aksjomat 5
definiuje rezonans jako wyrownanie (f_i,phi_i) MIEDZY DWIEMA
modalnosciami -- czyli literalnie porownanie faz POCZATKOWYCH, nie
chwilowych; ten modul implementuje to doslownie, bez interpretacji.

## Mapa synchronizacji faz f

Dwie modalnosci, "lokalna" i "globalna", kazda monochromatyczna (stale
f,phi,A -- DOKLADNIE tak, jak Aksjomat 3 je definiuje, zaden nowy
aksjomat nie zostal dodany). "t_lokalne=f(tau_globalne)" jest
formalizowane jako: znajdz taki czas lokalny t_lokalne, przy ktorym
FAZA CHWILOWA oscylatora lokalnego rownai sie fazie chwilowej
oscylatora globalnego w chwili tau_globalne:

    theta_lokalne(t_lokalne) = theta_globalne(tau_globalne)
    2*pi*f_lokalne*t_lokalne + phi_lokalne = 2*pi*f_globalne*tau_globalne + phi_globalne

Rozwiazujac wprost dla t_lokalne (wymaga f_lokalne != 0, inaczej
theta_lokalne jest stala -- nie da sie odwrocic):

    t_lokalne = (f_globalne/f_lokalne)*tau_globalne
                + (phi_globalne - phi_lokalne)/(2*pi*f_lokalne)

To jest funkcja `local_time_from_global()` ponizej -- DOKLADNIE ten
sam obiekt matematyczny co "mapa resynchronizacji faz
f:=phi_lokalne∘phi_globalne^-1" z dyskusji w czacie, tylko rozpisana
jawnie na czas->czas zamiast czas->faza->czas.

## Granica zakresu -- jawnie, uczciwie

Ta mapa jest AFINICZNA (liniowa + przesuniecie) -- bo Aksjomaty
K3/K4 modeluja kazda modalnosc jako oscylator o STALYCH parametrach,
nie oscylator SPRZEZONY o dynamicznie zmieniajacej sie czestotliwosci.
Pelniejsza, NIELINIOWA mapa synchronizacji w stylu Kuramoto (gdzie
oscylatory wzajemnie dostrajaja swoja czestotliwosc przez sile
sprzezenia) wymagalaby ROZSZERZENIA Axioms_K o dynamike sprzezenia,
ktorej tam dzis NIE MA -- to jest jawnie NIE zrobione tutaj, nie
ukryte uproszczenie. To, co jest tutaj, jest poprawna, sprawdzalna
formalizacja postulatu "t_lokalne=f(tau_globalne)" DANE aksjomaty
dokladnie takie, jakie sa dzisiaj -- pierwsza instancja galezi K jako
kodu (K nie mialo dotad ZADNEJ implementacji w tym ekosystemie).

UWAGA O WYKONANIU: napisane w sesji bez dostepu do sandboxa bash,
odtad faktycznie uruchomione przez uzytkownika (`pytest tests/ -v`) i
ZWERYFIKOWANE -- 17/17 testow przeszlo. Jeden test
(`test_is_resonant_frequency_at_threshold_is_false`) najpierw padl --
byl to blad TESTU (zalozenie dokladnej arytmetyki float dla
`1.0+1e-6`), nie bledu w `is_resonant()`; naprawiony, patrz komentarz
w tests/test_phase_sync.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

__all__ = [
    "Modality",
    "instantaneous_phase",
    "interference",
    "is_resonant",
    "local_time_from_global",
    "PhaseDispersionResult",
    "modal_phase_dispersion",
    "modal_phase_tempo",
]


@dataclass(frozen=True)
class Modality:
    """(f,phi,A) -- Aksjomat 3 z Axioms_K_TIMDR.md, doslownie.

    f: czestotliwosc (Hz, jednostki 1/[t]), MOZE byc ujemna (kierunek
        fazy) ale nie sprawdzana tu jako > 0 -- tylko != 0 jest
        wymagane tam, gdzie potrzebna jest odwracalnosc (patrz
        `local_time_from_global`).
    phi: faza poczatkowa (radiany), wartosc w t=0.
    A: amplituda.
    """

    f: float
    phi: float
    A: float = 1.0


def instantaneous_phase(modality: Modality, t) -> np.ndarray:
    """theta(t) = 2*pi*f*t + phi -- argument sinusa z Aksjomatu 4,
    ODCZYTANY jako funkcja czasu (Aksjomat 4 sam pisze go tylko w
    srodku sumy interferencji; to jest ten sam wzor, wyciagniety jako
    samodzielna funkcja fazy chwilowej, potrzebna do mapy f)."""
    t = np.asarray(t, dtype=float)
    return 2.0 * np.pi * modality.f * t + modality.phi


def interference(modalities: Sequence[Modality], t) -> np.ndarray:
    """I(t) = sum_i A_i*sin(2*pi*f_i*t+phi_i) -- Aksjomat 4, doslownie."""
    if len(modalities) == 0:
        raise ValueError("interference() wymaga >=1 modalnosci")
    t = np.asarray(t, dtype=float)
    total = np.zeros_like(t)
    for m in modalities:
        total = total + m.A * np.sin(instantaneous_phase(m, t))
    return total


def is_resonant(
    m_i: Modality, m_j: Modality, eps_f: float = 1e-6, eps_phi: float = 1e-6
) -> bool:
    """Aksjomat 5, doslownie: |f_i-f_j| < eps_f ORAZ |phi_i-phi_j| < eps_phi.
    Nierownosci SCISLE (<), zgodnie z zapisem aksjomatu -- rownosc
    dokladnie na progu NIE liczy sie jako rezonans."""
    return abs(m_i.f - m_j.f) < eps_f and abs(m_i.phi - m_j.phi) < eps_phi


def local_time_from_global(local: Modality, global_: Modality, tau_global) -> np.ndarray:
    """Mapa f: t_lokalne=f(tau_globalne), zdefiniowana przez dopasowanie
    FAZY CHWILOWEJ (patrz wyprowadzenie w naglowku modulu):

        t_lokalne = (f_globalne/f_lokalne)*tau_globalne
                    + (phi_globalne-phi_lokalne)/(2*pi*f_lokalne)

    Wymaga local.f != 0 -- inaczej theta_lokalne jest stala funkcja
    czasu (oscylator lokalny "nie plynie"), wiec nie da sie jej
    odwrocic, zeby znalezc t_lokalne (dokladnie ten warunek
    odwracalnosci/monotonicznosci, ktory byl flagowany jako wymagany w
    dyskusji przed napisaniem tego kodu).
    """
    if local.f == 0:
        raise ValueError(
            "local.f == 0 -- faza lokalna jest stala, mapa f nie jest "
            "odwracalna (wymagana monotonicznosc theta_lokalne(t))"
        )
    tau_global = np.asarray(tau_global, dtype=float)
    theta_g = instantaneous_phase(global_, tau_global)
    return (theta_g - local.phi) / (2.0 * np.pi * local.f)


# ---------------------------------------------------------------------
# Lambda_K, tau_K: dyspersja fazowa i jej tempo zmiany (DODANE 2026-09-10)
# ---------------------------------------------------------------------
#
# PRE-REJESTRACJA (zamrozone TUTAJ, przed uruchomieniem jakiegokolwiek
# testu na tych funkcjach):
#
# Kontekst: ten sam wniosek uzytkownika co w weingarten.py (galaz G) --
# traktowac Lambda/tau z META-DYNAMICS jako RODZINE sygnalow, jeden
# ksztalt pytania realizowany OSOBNYM wzorem w kazdej galezi. Audyt PRZED
# napisaniem kodu (grep na `Axioms_K_TIMDR.md` i tym module) pokazal
# ZERO istniejacego operatora dyspersji/tempa w galezi K -- Aksjomat 5
# ma tylko PROGOWE porownanie PARY modalnosci (rezonans/brak), nie ciagla
# miare "jak bardzo caly zbior modalnosci jest zsynchronizowany W CHWILI
# t", ani tym bardziej jej tempa zmiany.
#
# KLUCZOWA ROZNICA wzgledem proby w galezi G (odrzuconej tam): modalnosci
# TU maja WSPOLNY, GLOBALNY uklad odniesienia dla fazy chwilowej --
# theta_i(t) = 2*pi*f_i*t + phi_i, WSZYSTKIE na tym samym okregu (mod
# 2*pi), bez problemu "roznych przestrzeni stycznych" z siatki 3D. Wiec
# TUTAJ (w przeciwienstwie do proby z kierunkami krzywizny w G) DA SIE
# uzasadnione uzyc dokladnie tego samego zespolonego parametru porzadku
# co circular_dispersion() w TIMDR-Quantum-Lattice i wind_direction_
# coherence() w Synoptyk-v3 -- TA SAMA formula, bo TU faktycznie jest
# TEN SAM obiekt matematyczny (uklad wielu oscylatorow na wspolnym
# okregu fazowym), nie tylko podobienstwo slowne.
#
# PRZYJETE DEFINICJE:
#
#   Lambda_K(modalities, t) = 1 - |mean_i(exp(i*theta_i(t)))|
#
# gdzie theta_i(t) = instantaneous_phase(modality_i, t) (Aksjomat 4,
# funkcja juz istniejaca powyzej w tym pliku). Interpretacja identyczna
# jak wszedzie indziej w ekosystemie: 0 = wszystkie modalnosci maja
# identyczna faze chwilowa w t (idealna synchronizacja), ~1 = fazy
# rozrzucone losowo po okregu.
#
#   tau_K(modalities, t, dt) = |Lambda_K(t+dt) - Lambda_K(t)| / dt
#
# Tempo zmiany dyspersji fazowej -- bezposrednia analogia do
# tau=srednie|D(t)-D(t-1)| w meta_adapter.py (Quantum-Lattice), INNY
# wzor (pochodna Lambda_K zamiast tempa zmiany defektu D), bo Lambda_K
# jest tu jedynym istniejacym "polem" do rozniczkowania w czasie -- w
# tej galezi NIE ma odrebnego kanalu "defektu" jak D(x,y,t) na siatce.
#
# WAZNE, NIETRYWIALNE: modalnosci sa monochromatyczne (STALE f,phi --
# Aksjomat 3, explicite bez dynamiki sprzezenia, patrz UWAGA O ZAKRESIE
# w naglowku modulu) -- ale to NIE oznacza, ze Lambda_K(t) jest stala w
# czasie dla WIELU modalnosci o ROZNYCH czestotliwosciach: wzgledna faza
# miedzy para i,j narasta liniowo jako 2*pi*(f_i-f_j)*t, wiec Lambda_K(t)
# (funkcja WSZYSTKICH par naraz) generalnie OSCYLUJE w czasie (typowe
# zjawisko dudnienia/beating dla ukladow wielu czestosci) -- to jest
# realna, nietrywialna dynamika do zmierzenia, NIE martwa stala.
# WYJATEK, przedrejestrowany jako analityczna kontrola negatywna: gdy
# WSZYSTKIE f_i sa identyczne, wzgledne fazy sa DOKLADNIE stale (roznia
# sie tylko o stala phi_i-phi_j) -> Lambda_K(t) jest wtedy DOKLADNIE
# stala funkcja t -> tau_K==0 analitycznie (nie przyblizenie numeryczne).
#
# PRZEDREJESTROWANE KONTROLE (przed uruchomieniem):
#   Lambda_K + pozytywna: modalnosci o IDENTYCZNYCH (f,phi) -> Lambda_K=0
#     dla kazdego t (synchronizacja doskonala z definicji).
#   Lambda_K - negatywna: wiele modalnosci o roznych, losowych phi i
#     bliskich f (generyczne t) -> Lambda_K wyraznie > 0.
#   tau_K + pozytywna (tau_K==0 DOKLADNIE): wszystkie f_i rownE (roznymi
#     phi) -> patrz wyzej, analityczna stalosc.
#   tau_K - negatywna (tau_K>0): rozne f_i -> Lambda_K(t) sie zmienia,
#     tau_K > 0 dla wiekszosci wyborow t,dt.


@dataclass
class PhaseDispersionResult:
    """Wynik Lambda_K w jednej chwili t -- patrz PRE-REJESTRACJA powyzej."""

    lambda_k: float
    mean_resultant_length: float  # |Z|, tak ze lambda_k = 1 - to
    n_modalities: int


def modal_phase_dispersion(modalities: Sequence[Modality], t: float) -> PhaseDispersionResult:
    """Lambda_K(modalities, t) -- dyspersja fazowa (zespolony parametr
    porzadku) zbioru modalnosci w JEDNEJ chwili t. Patrz PRE-REJESTRACJA
    powyzej za pelne uzasadnienie wzoru."""
    if len(modalities) == 0:
        raise ValueError("modal_phase_dispersion() wymaga >=1 modalnosci")
    thetas = np.array([instantaneous_phase(m, t) for m in modalities], dtype=float)
    z = np.mean(np.exp(1j * thetas))
    resultant = float(np.abs(z))
    return PhaseDispersionResult(
        lambda_k=1.0 - resultant, mean_resultant_length=resultant, n_modalities=len(modalities),
    )


def modal_phase_tempo(modalities: Sequence[Modality], t: float, dt: float) -> float:
    """tau_K(modalities, t, dt) -- tempo zmiany Lambda_K w chwili t,
    przyblizone roznica skonczona krok naprzod. Patrz PRE-REJESTRACJA
    powyzej za pelne uzasadnienie (w tym analityczny przypadek tau_K==0
    dla identycznych czestotliwosci).

    Rzuca ValueError dla dt<=0 (kierunek/rozmiar kroku musi byc jawny,
    nie domyslny -- ta sama dyscyplina co dt=0 w
    TIMDR-META-DYNAMICS/core_meta/meta_operator_M.py)."""
    if dt <= 0:
        raise ValueError(f"dt musi byc > 0, dostano {dt}")
    lambda_t = modal_phase_dispersion(modalities, t).lambda_k
    lambda_t_plus_dt = modal_phase_dispersion(modalities, t + dt).lambda_k
    return abs(lambda_t_plus_dt - lambda_t) / dt
