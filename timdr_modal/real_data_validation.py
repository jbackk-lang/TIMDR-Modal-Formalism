"""
timdr_modal/real_data_validation.py

Pierwszy kontakt operatora rezonansu modalnego `is_resonant()`
(Aksjomat 5, `timdr_modal/phase_sync.py`) z PRAWDZIWYMI, zmierzonymi
danymi. Dotad (`tests/test_phase_sync.py`) operator byl sprawdzany
WYLACZNIE na recznie dobranych liczbach syntetycznych -- to jest
najmniej zwalidowana czesc calego ekosystemu TIMDR (patrz
`GIA-TIMDR/docs/theory/Resonance_M_Operator_Empiryczny.md`, ktory
jawnie wylacza rezonans modalny ze swojego zakresu: "Rezonans modalny
(2) pozostaje poza zakresem tego dokumentu"). Ten modul jest tym
brakujacym pierwszym kontaktem z danymi + krokiem kalibracyjnym,
zbudowanym wedlug tego samego wzorca co
`TIMDR-Math-Formalism/examples/real_weather_resonance_validation.py`
(permutacja, kontrola pozytywna, uczciwe zglaszanie braku mocy
statystycznej zamiast wymuszania wyniku pozytywnego).

## Zrodlo danych (realne, nie fabrykowane)

Dwa PRAWDZIWE, ciagle slady sejsmiczne zarejestrowane podczas
faktycznego trzesienia ziemi M7.1 Ridgecrest, Kalifornia,
2019-07-06T03:19:53.040Z -- pobrane przez autora repozytorium
bezposrednio z IRIS/EarthScope przez ObsPy (patrz
`TIMDR-Earthquake-Core/real_waveform_test.py` w repo siostrzanym za
dokladny skrypt pobierania i pre-rejestracje parametrow):

    stacje: CI.CLC i CI.RIO (Southern California Seismic Network)
    kanal:  HHZ (broadband, pionowy)
    fs:     100.0 Hz
    n:      36001 probek (360.01 s) kazda
    start:  2019-07-06T03:18:52.9983Z -- IDENTYCZNY dla obu stacji
            (zweryfikowane w TIMDR-Earthquake-Core/data/ridgecrest_2019/
            real_waveform_CLC_RIO/results.txt)

Ten modul NIE duplikuje tych plikow -- czyta je bezposrednio z
katalogu siostrzanego repo `TIMDR-Earthquake-Core` (patrz
`_default_data_dir()`), gdzie zostaly umieszczone przez
`real_waveform_test.py` tamtego repo. Dwie NIEZALEZNE stacje
rejestrujace TO SAMO prawdziwe trzesienie ziemi sluza tu jako dwie
"modalnosci" testowane pod katem rezonansu Aksjomatu 5.

Identyczny czas startu obu sladow jest tym, co pozwala traktowac ich
fazy jako wspolmierne bez dodatkowego kroku synchronizacji zegarow --
patrz `extract_modalities()`.

## Jak wydobywane sa (f, phi, A) z prawdziwych probek

Kazdy slad dzielony jest na NIE-zachodzace na siebie okna dlugosci
`window_sec` sekund. Dla kazdego okna:

  1. Odejmowana jest srednia okna (usuniecie skladowej DC) -- ZADEN
     taper (Hann/Hamming/...) NIE jest stosowany, celowo: taper
     znieksztalcalby odczyt fazy w probce 0 okna (patrz punkt 3),
     kosztem: wiecej leakage widmowego w odczycie czestotliwosci niz
     dalby taper. Dla uczciwej, eksploracyjnej walidacji scislego
     kryterium Aksjomatu 5 (dopasowanie FAZY) ten kompromis wybiera
     poprawnosc fazy kosztem precyzji czestotliwosci.
  2. `numpy.fft.rfft()` okna, szczyt szukany po amplitudzie z
     WYKLUCZENIEM binu f=0 (DC) -- to jest "dominujaca czestotliwosc"
     tego okna. Realne dane sejsmiczne sa szerokopasmowe (nie czystym
     tonem), wiec to jest NAJLEPSZE OBRONIALNE PODSUMOWANIE
     JEDNYM-SZCZYTEM danego okna, nie twierdzenie o istnieniu czystej
     sinusoidy w danych.
  3. Konwersja fazy z konwencji cosinusowej DFT na konwencje SINUSOWA
     Aksjomatu 4 (`interference()` uzywa `sin(2*pi*f*t+phi)`, nie
     `cos`) -- to jest krok, ktory latwo pominac i dostac faze przesunieta
     o pi/2. Wyprowadzenie: dla `x[n] = A*sin(w*n+phi0)` z `w` trafiajacym
     dokladnie w bin FFT,

         X[k] = sum_n x[n]*exp(-i*w*n)
              = (A/2i)*exp(i*phi0)*sum_n exp(i*w*n)*exp(-i*w*n)
                - (A/2i)*exp(-i*phi0)*sum_n exp(-i*w*n)*exp(-i*w*n)
              ~= (A*N/2i)*exp(i*phi0)          (drugi wyraz O(1), pomijalny dla N>>1)
              =  (A*N/2)*exp(i*(phi0 - pi/2))

     wiec `angle(X[k]) = phi0 - pi/2 (mod 2*pi)`, czyli
     `phi0 = angle(X[k]) + pi/2`. Bez tej korekty kazda faza
     odczytana z realnych danych bylaby systematycznie przesunieta
     o pi/2 rad wzgledem konwencji Aksjomatu 4 -- to nie jest szczegol
     kosmetyczny, tylko blad, ktory falszowalby KAZDE porownanie faz.
  4. `A = 2*|X[k]|/n` -- amplituda szczytowa odpowiadajacej sinusoidy
     (energia rzeczywistego sygnalu dzieli sie miedzy bin +f i -f,
     stad czynnik 2).
  5. Faza z kroku 3 (`phi_local`) jest faza CHWILOWA w PROBCE 0 OKNA,
     liczona od poczatku SLADU (bo to numpy indeksuje probki okna
     lokalnie od 0, a probka 0 okna `w` odpowiada globalnemu czasowi
     `t_start = t[i0]`). Modality.phi z definicji (Aksjomat 3,
     `instantaneous_phase`) to faza w t=0 WSPOLNEGO poczatku sladu,
     wiec:

         theta(t_start) = 2*pi*f*t_start + phi_global = phi_local
         => phi_global = wrap_to_pi(phi_local - 2*pi*f*t_start)

     Dzieki temu, ze obie stacje maja IDENTYCZNY czas startu sladu,
     `phi_global` z okna `w` stacji CLC i okna `w` stacji RIO sa
     odniesione do TEGO SAMEGO t=0 i moga byc bezposrednio porownane
     przez `is_resonant()` -- bez tego przeliczenia porownanie faz
     dwoch stacji byloby bez sensu (kazda mierzylaby faze wzgledem
     wlasnego, przesunietego w czasie okna).

## Test statystyczny

Dla kazdego indeksu okna `w`, CLC i RIO daja po jednej Modality.
Liczymy realna stope `is_resonant()` po wszystkich sparowanych oknach,
i porownujemy z NULLEM PERMUTACYJNYM: losowe przetasowanie, ktore okno
RIO jest sparowane z ktorym oknem CLC (zrywa realne wyrownanie
czasowe, zachowuje realny, empiryczny rozklad wartosci f/phi kazdej
stacji z osobna) -- powtorzone `n_permutations` razy. p-wartosc =
frakcja permutacji null o stopie >= realnej (test jednostronny:
hipoteza, ze PRAWDZIWE wyrownanie czasowe daje wiecej rezonansu niz
losowe parowanie tych samych wartosci).

Kontrola pozytywna (jak w `Resonance_M_Operator_Empiryczny.md` sekcja
3): CLC sparowane samo ze soba daje rezonans z definicji w KAZDYM
oknie (f_i=f_j, phi_i=phi_j dokladnie) -- sprawdza, ze mechanika testu
(is_resonant + petla + permutacja) faktycznie wykrywa realne
wyrownanie, gdy ono istnieje, niezaleznie od tego, co pokaza prawdziwa
para CLC/RIO.

UCZCIWA UWAGA O MOCY STATYSTYCZNEJ: przy oknach 10-sekundowych z
360-sekundowego sladu wychodzi ~36 sparowanych okien -- bardzo mala
proba. Wynik zerowy (lub bliski zeru) NIE jest dowodem, ze modalny
rezonans nigdy nie zachodzi w naturze -- jest dowodem tylko na to, ze
TEN JEDEN slad, przetworzony W TEN SPOSOB, go nie pokazuje bardziej
niz przypadek. Dokladnie ten sam zastrzezenie, co w sekcji 3 dokumentu
`Resonance_M_Operator_Empiryczny.md` dla rezonansu sygnalowego.
"""
from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from .phase_sync import Modality, is_resonant

__all__ = [
    "RIDGECREST_STATIONS",
    "RIDGECREST_FS_HZ",
    "WindowedModality",
    "RealResonanceResult",
    "CalibrationResult",
    "load_station_csv",
    "extract_modalities",
    "real_data_resonance_report",
    "calibrate_epsilons",
]

# ---------------------------------------------------------------------
# 1. Lokalizacja i wczytywanie realnych danych
# ---------------------------------------------------------------------

_DATA_DIR_ENV = "TIMDR_RIDGECREST_DATA_DIR"

RIDGECREST_STATIONS: Dict[str, str] = {
    "CLC": "CLC_HHZ.csv",
    "RIO": "RIO_HHZ.csv",
}

# Zweryfikowane w TIMDR-Earthquake-Core/data/ridgecrest_2019/
# real_waveform_CLC_RIO/results.txt dla OBU stacji ("fs=100.0Hz").
# Nie jest odczytywane z samego CSV (ktory ma tylko t,s -- fs
# wynikaloby z dt miedzy wierszami, ale trzymamy jawnie udokumentowana
# wartosc zamiast cichego zalozenia rownomiernego próbkowania).
RIDGECREST_FS_HZ = 100.0


def _default_data_dir() -> str:
    """Katalog z CLC_HHZ.csv / RIO_HHZ.csv.

    Domyslnie katalog siostrzany `TIMDR-Earthquake-Core/data/
    ridgecrest_2019/real_waveform_CLC_RIO` (patrz naglowek modulu) --
    zaklada, ze oba repo sa sciagniete obok siebie (tak jak w tej
    sesji, `Downloads/a/<repo>`). Nadpisywalne zmienna srodowiskowa
    `TIMDR_RIDGECREST_DATA_DIR`, gdyby uklad katalogow byl inny.
    """
    env = os.environ.get(_DATA_DIR_ENV)
    if env:
        return env
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(here)            # .../TIMDR-Modal-Formalism
    siblings_root = os.path.dirname(repo_root)   # .../a
    return os.path.join(
        siblings_root,
        "TIMDR-Earthquake-Core",
        "data",
        "ridgecrest_2019",
        "real_waveform_CLC_RIO",
    )


def load_station_csv(station: str, data_dir: Optional[str] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Wczytuje jeden realny slad (t sekundy od startu, s = surowe liczby
    licznika/count) z bezglowkowego CSV `t,s` (bez naglowka -- ta sama
    konwencja co `TIMDR-Earthquake-Core/seismic_loader.py`)."""
    if station not in RIDGECREST_STATIONS:
        raise ValueError(
            f"Nieznana stacja {station!r}; oczekiwano jednej z {sorted(RIDGECREST_STATIONS)}"
        )
    data_dir = data_dir or _default_data_dir()
    path = os.path.join(data_dir, RIDGECREST_STATIONS[station])
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Nie znaleziono realnych danych sejsmicznych: {path!r}. "
            f"Ten modul czyta CSV bezposrednio z checkoutu TIMDR-Earthquake-Core "
            f"(patrz docstring modulu real_data_validation.py) -- upewnij sie, ze "
            f"ten katalog jest sciagniety jako repo siostrzane wzgledem "
            f"TIMDR-Modal-Formalism, albo ustaw zmienna srodowiskowa "
            f"'{_DATA_DIR_ENV}' na katalog zawierajacy CLC_HHZ.csv/RIO_HHZ.csv."
        )
    t, s = [], []
    with open(path, "r", newline="") as f:
        for row in csv.reader(f):
            if len(row) < 2:
                continue
            t.append(float(row[0]))
            s.append(float(row[1]))
    return np.asarray(t, dtype=float), np.asarray(s, dtype=float)


# ---------------------------------------------------------------------
# 2. Ekstrakcja (f, phi, A) per okno -- rdzen metodologiczny
# ---------------------------------------------------------------------

def _wrap_to_pi(x: float) -> float:
    """Zawija kat do (-pi, pi]."""
    return float((x + np.pi) % (2.0 * np.pi) - np.pi)


def _local_phase_to_global(phi_local: float, f: float, t_start: float) -> float:
    """Konwertuje faze chwilowa zmierzona w probce 0 okna (ktora to
    probka odpowiada globalnemu czasowi `t_start` liczonemu od
    poczatku sladu) na faze POCZATKOWA wzgledem wspolnego t=0 sladu
    (`Modality.phi`, Aksjomat 3). Wyprowadzenie (patrz tez naglowek
    modulu): z definicji `instantaneous_phase`,
    `theta(t) = 2*pi*f*t + phi`; w t=t_start faza chwilowa jest z
    konstrukcji rowna `phi_local` (bo probka 0 okna JEST probka w
    czasie t_start), wiec

        theta(t_start) = 2*pi*f*t_start + phi_global = phi_local
        => phi_global = phi_local - 2*pi*f*t_start

    Wydzielone jako samodzielna funkcja (zamiast zapisane inline w
    `extract_modalities`), zeby dalo sie ja przetestowac wlasnoscia
    roundtrip (`instantaneous_phase(Modality(f,phi_global,A),
    t_start) == phi_local mod 2*pi`) niezaleznie od FFT -- patrz
    `tests/test_real_data_validation.py`."""
    return _wrap_to_pi(phi_local - 2.0 * np.pi * f * t_start)


def _fft_peak_f_phi_A(s_window: np.ndarray, fs: float) -> Tuple[float, float, float]:
    """Dominant-frequency (f, phi, A) z jednego okna sygnalu rzeczywistego,
    phi juz w konwencji SINUSOWEJ Aksjomatu 4 (patrz wyprowadzenie
    w naglowku modulu). phi jest faza w PROBCE 0 OKNA (nie jeszcze
    przeliczona na wspolny t=0 sladu -- tym zajmuje sie
    `extract_modalities()`)."""
    n = len(s_window)
    if n < 4:
        raise ValueError("okno za krotkie do FFT (n<4)")
    x = s_window - np.mean(s_window)
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    if len(spec) < 2:
        raise ValueError("okno za krotkie -- brak binow FFT poza DC")
    idx = 1 + int(np.argmax(np.abs(spec[1:])))
    f_peak = float(freqs[idx])
    phi_cos_convention = float(np.angle(spec[idx]))
    phi_local = _wrap_to_pi(phi_cos_convention + np.pi / 2.0)
    A_peak = float(2.0 * np.abs(spec[idx]) / n)
    return f_peak, phi_local, A_peak


@dataclass(frozen=True)
class WindowedModality:
    """Jedna (f,phi,A) odczytana z jednego okna jednego realnego sladu,
    plus metadane audytowe (bez nich sama Modality nie mowi, skad
    wzieta faza/czestotliwosc/z jakiego czasu okna)."""

    station: str
    window_index: int
    t_start_s: float
    modality: Modality


def extract_modalities(
    station: str,
    window_sec: float = 10.0,
    data_dir: Optional[str] = None,
) -> List[WindowedModality]:
    """Dzieli realny slad `station` na nie-zachodzace na siebie okna
    dlugosci `window_sec` i zwraca liste `WindowedModality` z faza
    przeliczona na WSPOLNY punkt odniesienia t=0 (wspolny start obu
    stacji Ridgecrest -- patrz naglowek modulu), zeby okna o tym samym
    `window_index` z roznych stacji byly bezposrednio porownywalne
    przez `is_resonant()`."""
    t, s = load_station_csv(station, data_dir=data_dir)
    fs = RIDGECREST_FS_HZ
    n_per_window = int(round(window_sec * fs))
    if n_per_window < 4:
        raise ValueError("window_sec za male przy tym fs (n_per_window<4)")
    if len(s) < n_per_window:
        return []
    n_windows = len(s) // n_per_window
    out: List[WindowedModality] = []
    for w in range(n_windows):
        i0 = w * n_per_window
        i1 = i0 + n_per_window
        s_window = s[i0:i1]
        t_start = float(t[i0])  # sekundy od poczatku sladu -- wspolne dla obu stacji
        f_peak, phi_local, A_peak = _fft_peak_f_phi_A(s_window, fs)
        phi_global = _local_phase_to_global(phi_local, f_peak, t_start)
        out.append(
            WindowedModality(
                station=station,
                window_index=w,
                t_start_s=t_start,
                modality=Modality(f=f_peak, phi=phi_global, A=A_peak),
            )
        )
    return out


# ---------------------------------------------------------------------
# 3. Test rezonansu na realnych danych + null permutacyjny
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class RealResonanceResult:
    window_sec: float
    eps_f: float
    eps_phi: float
    n_paired_windows: int
    n_resonant_real: int
    resonance_rate_real: float
    n_permutations: int
    null_resonance_rates: np.ndarray = field(repr=False)
    p_value: float
    positive_control_rate: float
    positive_control_p_value: float


def _resonance_rate(
    a: List[WindowedModality], b: List[WindowedModality], eps_f: float, eps_phi: float
) -> Tuple[int, float]:
    n = len(a)
    if n == 0:
        return 0, float("nan")
    count = sum(
        1
        for wa, wb in zip(a, b)
        if is_resonant(wa.modality, wb.modality, eps_f=eps_f, eps_phi=eps_phi)
    )
    return count, count / n


def real_data_resonance_report(
    window_sec: float = 10.0,
    eps_f: float = 0.05,
    eps_phi: float = 0.2,
    n_permutations: int = 2000,
    seed: int = 0,
    data_dir: Optional[str] = None,
) -> RealResonanceResult:
    """Uruchamia NIEZMODYFIKOWANY `is_resonant()` (Aksjomat 5) na realnych
    (f,phi,A) wydobytych z prawdziwego trzesienia ziemi Ridgecrest 2019
    (stacje CLC i RIO jako dwie modalnosci), z nullem permutacyjnym i
    kontrola pozytywna. Patrz naglowek modulu za pelna metodologie i
    zastrzezenie o mocy statystycznej.

    UWAGA O DOMYSLNYCH eps_f/eps_phi: literalne domyslne wartosci
    Aksjomatu 5 w `is_resonant()` (1e-6, 1e-6) sa NIEUZYWALNE dla
    jakiegokolwiek odczytu z okna FFT -- rozdzielczosc binow przy
    window_sec=10s wynosi 0.1 Hz, o 5 rzedow wielkosci grubsza niz
    1e-6. Uzycie literalnego domyslnego eps dawaloby TRYWIALNE zero
    rezonansow przy kazdym realnym zbiorze danych, niezaleznie od tego,
    czy jakiekolwiek sensowne wyrownanie istnieje -- to nie byloby
    test, tylko gwarantowana klapa. Domyslne tutaj (0.05 Hz, 0.2 rad)
    sa jawnie EKSPLORACYJNYM wyborem (rzedu ulamka szerokosci binu /
    ~11 stopni), NIE twierdzeniem fizycznym o tym, jaka tolerancja jest
    "wlasciwa" -- do tego sluzy `calibrate_epsilons()` ponizej, ktora
    wyprowadza prog z rozkladu realnych roznic zamiast go zgadywac.
    """
    clc = extract_modalities("CLC", window_sec=window_sec, data_dir=data_dir)
    rio = extract_modalities("RIO", window_sec=window_sec, data_dir=data_dir)
    n = min(len(clc), len(rio))
    if n == 0:
        raise ValueError(
            "brak sparowanych okien -- sprawdz window_sec (za duze wzgledem "
            "dlugosci sladu) lub dostepnosc danych wejsciowych"
        )
    clc, rio = clc[:n], rio[:n]

    n_resonant_real, rate_real = _resonance_rate(clc, rio, eps_f, eps_phi)

    rng = np.random.default_rng(seed)
    null_rates = np.empty(n_permutations)
    for i in range(n_permutations):
        perm = rng.permutation(n)
        shuffled = [rio[j] for j in perm]
        _, rate = _resonance_rate(clc, shuffled, eps_f, eps_phi)
        null_rates[i] = rate
    # p-wartosc permutacyjna, jednostronna (real wyrownanie >= przypadek),
    # z korekta +1/+1 (Davison & Hinkley) -- nigdy dokladnie 0.
    p_value = float((np.sum(null_rates >= rate_real) + 1) / (n_permutations + 1))

    # Kontrola pozytywna: CLC sparowane samo ze soba -- f_i=f_j,
    # phi_i=phi_j DOKLADNIE w kazdym oknie -> rezonans z definicji
    # (dla eps_f,eps_phi>0) w KAZDYM oknie. Sprawdza mechanike testu
    # (is_resonant + permutacja), niezaleznie od tego, co pokazuje
    # prawdziwa para CLC/RIO powyzej.
    n_pos, rate_pos = _resonance_rate(clc, clc, eps_f, eps_phi)
    pos_null_rates = np.empty(n_permutations)
    for i in range(n_permutations):
        perm = rng.permutation(n)
        shuffled = [clc[j] for j in perm]
        _, rate = _resonance_rate(clc, shuffled, eps_f, eps_phi)
        pos_null_rates[i] = rate
    pos_p_value = float((np.sum(pos_null_rates >= rate_pos) + 1) / (n_permutations + 1))

    return RealResonanceResult(
        window_sec=window_sec,
        eps_f=eps_f,
        eps_phi=eps_phi,
        n_paired_windows=n,
        n_resonant_real=n_resonant_real,
        resonance_rate_real=rate_real,
        n_permutations=n_permutations,
        null_resonance_rates=null_rates,
        p_value=p_value,
        positive_control_rate=rate_pos,
        positive_control_p_value=pos_p_value,
    )


# ---------------------------------------------------------------------
# 4. Kalibracja eps_f/eps_phi -- lub uczciwe zgloszenie braku mocy
# ---------------------------------------------------------------------

MIN_WINDOWS_FOR_CALIBRATION = 20


@dataclass(frozen=True)
class CalibrationResult:
    method: str
    window_sec: float
    n_paired_windows: int
    target_real_rate: float
    eps_f_suggested: Optional[float]
    eps_phi_suggested: Optional[float]
    rationale: str
    insufficient_data: bool


def calibrate_epsilons(
    window_sec: float = 10.0,
    target_real_rate: float = 0.1,
    data_dir: Optional[str] = None,
) -> CalibrationResult:
    """Proponuje (eps_f, eps_phi) z ROZKLADU REALNYCH roznic |f_CLC-f_RIO|,
    |phi_CLC-phi_RIO| miedzy czasowo wyrownanymi oknami -- zamiast z gory
    zgadywac liczby -- w duchu tego samego wzorca "kalibruj z danych albo
    uczciwie zglos brak mocy", co
    `GIA-TIMDR/docs/theory/Resonance_M_Operator_Empiryczny.md` sekcja 3
    (tam: permutacyjna walidacja rezonansu SYGNALOWEGO na danych
    pogodowych; tu: to samo podejscie zastosowane do rezonansu
    MODALNEGO, ktory tamten dokument jawnie zostawia poza swoim
    zakresem).

    Metoda: `eps_f`/`eps_phi` = `target_real_rate`-ty percentyl
    obserwowanych |f_i-f_j|/|phi_i-phi_j| miedzy sparowanymi oknami.
    To NIE jest twierdzenie, ze modalny rezonans FIZYCZNIE zachodzi
    przy tym progu -- to odpowiedz na pytanie kalibracyjne "jaka
    tolerancja odpowiadalaby temu, ze okolo target_real_rate najbardziej
    zgodnych par w TYM JEDNYM realnym zbiorze danych zostalyby uznane
    za rezonans", nic wiecej.

    UCZCIWOSC: przy n_paired_windows < MIN_WINDOWS_FOR_CALIBRATION
    (domyslnie 20) zwraca `insufficient_data=True` i NIE proponuje
    liczb -- fikcyjna precyzja z garstki okien bylaby gorsza niz jawny
    brak wyniku. Zageszczenie siatki (mniejsze `window_sec`) NIE jest
    tu lekarstwem: to dalej TEN SAM jeden 360-sekundowy slad, wiecej
    okien z niego nie dodaje niezaleznej informacji o tym, czy modalny
    rezonans jest zjawiskiem realnym -- do tego trzeba wiecej
    niezaleznych zdarzen/par stacji, nie drobniejszej siatki tego
    samego zdarzenia.
    """
    clc = extract_modalities("CLC", window_sec=window_sec, data_dir=data_dir)
    rio = extract_modalities("RIO", window_sec=window_sec, data_dir=data_dir)
    n = min(len(clc), len(rio))
    clc, rio = clc[:n], rio[:n]

    if n < MIN_WINDOWS_FOR_CALIBRATION:
        return CalibrationResult(
            method="percentile-of-real-differences",
            window_sec=window_sec,
            n_paired_windows=n,
            target_real_rate=target_real_rate,
            eps_f_suggested=None,
            eps_phi_suggested=None,
            rationale=(
                f"tylko {n} sparowanych okien (window_sec={window_sec}s) -- "
                f"ponizej progu {MIN_WINDOWS_FOR_CALIBRATION} przyjetego jako "
                f"minimum do sensownej kalibracji percentylowej. Za malo "
                f"danych do kalibracji -- zwiekszenie liczby okien tego samego "
                f"360-sekundowego sladu (mniejsze window_sec) nie rozwiazuje "
                f"tego uczciwie, bo to dalej jedno zdarzenie/jedna para stacji, "
                f"nie niezalezne probki modalnego rezonansu."
            ),
            insufficient_data=True,
        )

    diffs_f = np.array([abs(c.modality.f - r.modality.f) for c, r in zip(clc, rio)])
    diffs_phi = np.array(
        [abs(_wrap_to_pi(c.modality.phi - r.modality.phi)) for c, r in zip(clc, rio)]
    )
    eps_f = float(np.percentile(diffs_f, target_real_rate * 100.0))
    eps_phi = float(np.percentile(diffs_phi, target_real_rate * 100.0))

    return CalibrationResult(
        method="percentile-of-real-differences",
        window_sec=window_sec,
        n_paired_windows=n,
        target_real_rate=target_real_rate,
        eps_f_suggested=eps_f,
        eps_phi_suggested=eps_phi,
        rationale=(
            f"eps_f/eps_phi ustawione na {target_real_rate:.0%} percentyl "
            f"realnych roznic |f_CLC-f_RIO| ({eps_f:.4g} Hz) i "
            f"|phi_CLC-phi_RIO| ({eps_phi:.4g} rad) miedzy {n} czasowo "
            f"wyrownanymi oknami ({window_sec}s kazde) prawdziwego sladu "
            f"Ridgecrest 2019. Kalibracyjna odpowiedz na 'jaka tolerancja "
            f"odpowiada X% najbardziej zgodnych par w TYM zbiorze danych', "
            f"NIE fizyczne twierdzenie o istnieniu modalnego rezonansu."
        ),
        insufficient_data=False,
    )


if __name__ == "__main__":  # pragma: no cover -- reczne uruchomienie diagnostyczne
    try:
        report = real_data_resonance_report()
        print(
            f"[real_data_resonance_report] window_sec={report.window_sec} "
            f"eps_f={report.eps_f} eps_phi={report.eps_phi}"
        )
        print(
            f"  realna stopa rezonansu: {report.n_resonant_real}/"
            f"{report.n_paired_windows} = {report.resonance_rate_real:.3f}"
        )
        print(
            f"  null permutacyjny ({report.n_permutations}x): "
            f"mean={np.mean(report.null_resonance_rates):.3f} "
            f"p-value={report.p_value:.4f}"
        )
        print(
            f"  kontrola pozytywna (CLC vs CLC): "
            f"rate={report.positive_control_rate:.3f} "
            f"p-value={report.positive_control_p_value:.4f}"
        )

        calib = calibrate_epsilons()
        print(f"\n[calibrate_epsilons] insufficient_data={calib.insufficient_data}")
        print(f"  {calib.rationale}")
    except FileNotFoundError as e:
        print(f"Realne dane niedostepne: {e}")
