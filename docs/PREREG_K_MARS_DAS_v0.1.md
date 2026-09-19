# Gałąź K na sygnałach światłowodowych — prerejestracja testu na danych MARS DAS v0.1

**Status: PREREGISTERED, NOT YET RUN.** Zamrożone PRZED pobraniem czy
dotknięciem jakiegokolwiek pliku danych. Pierwszy test operatora rezonansu
modalnego (`is_resonant()`, Aksjomat 5, `timdr_modal/phase_sync.py`) na
prawdziwym sygnale ŚWIATŁOWODOWYM (Distributed Acoustic Sensing) — dotąd
jedyna realna walidacja gałęzi K używała danych sejsmometrycznych
(Ridgecrest, `real_data_validation.py`), nie samego światłowodu jako
czujnika.

## 0. Dlaczego DAS, nie phi-fiber-dsp

`phi-fiber-dsp` (repo siostrzane) nie zawiera żadnych prawdziwych danych
światłowodowych — wyłącznie filtr DSP działający na syntetycznych
sinusoidach. Do prawdziwego testu potrzeba realnie zmierzonego sygnału z
włókna. Wybrany zbiór: **MARS/SeaFOAM** — rok trwający, prawdziwy
eksperyment DAS na 52-kilometrowym podmorskim kablu telekomunikacyjnym
(Monterey Accelerated Research System, Monterey Bay, Kalifornia),
publicznie dostępny przez PubDAS/Hugging Face
(`AI4EPS/quakeflow_das`, katalog `monterey_bay/data/`), format i
metodologia opisane w Romanowicz i in. 2023 (SRL 94(5):2348-2359).

## 1. Dane wejściowe — wybór PRZED zobaczeniem pliku

Katalog `monterey_bay/data/` zawiera 33 pliki `.h5`, po jednym per
zdarzenie sejsmiczne, nazwane znacznikiem czasu (`YYYYMMDDTHHMMSSZ.h5`),
posortowane chronologicznie. Wybrany plik: **pierwszy chronologicznie w
katalogu**, `20220730T233258Z.h5` — reguła wyboru ("pierwszy na liście"),
NIE wybór po przejrzeniu zawartości/jakości sygnału żadnego pliku. Rozmiar
137 MB (do pobrania ręcznie przez użytkownika — sandbox blokuje
bezpośrednie pobieranie z huggingface.co).

```text
źródło: https://huggingface.co/datasets/AI4EPS/quakeflow_das/resolve/main/monterey_bay/data/20220730T233258Z.h5
```

Hash SHA-256 pliku zostanie zweryfikowany i zapisany PRZED uruchomieniem
ekstrakcji geometrii sygnału (analogicznie do `b4_kitchen_manifest*.json`).

## 2. Format danych (z dokumentacji zbioru, nie z zawartości pliku)

Zgodnie z dataset card `AI4EPS/quakeflow_das`: `data` to tablica 2D
`float32` o kształcie `(nch, nt)` (kanał × czas), jednostka mikroodkształcenie/s.
Atrybuty na `data`: `dt_s` (interwał próbkowania), `dx_m` (rozstaw
kanałów), `event_time`, `magnitude`, `latitude`/`longitude`. Te wartości
są WŁASNością konkretnego pliku i zostaną odczytane, a nie zgadywane —
ale sama STRUKTURA (2D array, jeden dt dla wszystkich kanałów) jest znana
z dokumentacji przed pobraniem.

## 3. Dwie "modalności" — reguła wyboru kanałów, PRZED zobaczeniem danych

W przeciwieństwie do Ridgecrest (dwie fizycznie osobne stacje sejsmiczne,
wymagające przeliczenia fazy na wspólne `t=0` przez `recording-synch.log`),
DAS ma WSZYSTKIE kanały zarejestrowane przez JEDEN interrogator ze
wspólnym zegarem — więc synchronizacja czasu jest już dana, żadnego
przeliczenia offsetu nie trzeba robić (mocniejsza własność niż w
Ridgecrest, nie słabsza).

Zamrożona reguła wyboru dwóch kanałów jako modalności A i B (indeksy
0-based):

```text
kanał A = 0                      (pierwszy kanał w pliku)
kanał B = nch - 1                (ostatni kanał w pliku)
```

Skrajne końce zarejestrowanego odcinka kabla — reguła geometryczna
(maksymalny rozstaw przestrzenny dostępny w pliku), nie wybór na
podstawie tego, które dwa kanały "wyglądają" na zsynchronizowane.
`nch` odczytywane z kształtu tablicy po otwarciu pliku (nieznane teraz,
ale reguła nie zależy od jego wartości).

## 4. Metoda — w pełni odziedziczona z `real_data_validation.py`, zero zmian

Ekstrakcja `(f,φ,A)` per okno: identyczna z `_fft_peak_f_phi_A()` +
`_local_phase_to_global()` (`timdr_modal/real_data_validation.py`) —
szczyt FFT z wykluczeniem DC, korekta fazy cosinus→sinus, przeliczenie na
wspólne `t=0` pliku (tu: `t_start = window_index * window_sec`, bo DAS ma
już wspólny zegar — nie trzeba `recording-synch.log`).

`window_sec`: zamrożone na **1.0 s** — MARS ma znacznie wyższą
częstotliwość próbkowania czasowego niż Ridgecrest (100 Hz), typowe DAS
`dt_s` rzędu 0.002-0.01 s (100-500 Hz), a zdarzenia sejsmiczne w takich
plikach trwają rzędu dziesiątek sekund (nie setek jak cały ślad
Ridgecrest) — 1 s daje rozsądną liczbę nie-zachodzących okien bez zgadywania
długości pliku. Jeśli po otwarciu pliku okaże się to dawać <20 okien
(próg mocy statystycznej z `calibrate_epsilons()`), zostanie to
zgłoszone jako brak mocy, NIE powód do zmiany `window_sec` po fakcie.

`eps_f`/`eps_phi`: metodą `calibrate_epsilons()` (percentyl realnych
różnic |f_A-f_B|/|φ_A-φ_B|), **target_real_rate=0.1** — identyczna
metoda i identyczny cel jak w Ridgecrest, zero nowych parametrów.

Test permutacyjny + kontrola pozytywna (kanał A sparowany sam ze sobą):
identyczne z `real_data_resonance_report()`, `n_permutations=2000`,
`seed=0` — te same literalne wartości co Ridgecrest.

## 5. Werdykt i zasada anty-tuningu

Identyczna trójstopniowa klasyfikacja: SUPPORTED (kontrola pozytywna
przechodzi I `p_value < 0.05`) / NOT SUPPORTED (obie kontrole liczą się,
`p_value >= 0.05`) / INCONCLUSIVE (za mało okien do kalibracji, albo
kontrola pozytywna nie przechodzi — co by wskazywało na błąd w
mechanice testu, nie w sygnale). Po zobaczeniu wyniku nie wolno zmieniać:
wyboru pliku, wyboru kanałów, `window_sec`, `target_real_rate`, `seed`.

## 6. Co ten test NIE rozstrzyga

Jeden plik, jedno zdarzenie, dwa kanały tego samego kabla — nie test
przenośności międzydomenowej, nie replika. Nawet SUPPORTED byłoby
pierwszym, pojedynczym sygnałem na gałęzi K ze światłowodu, analogicznym
do statusu B4-Kitchen v0.1 przed replikami, nie ustalonym wynikiem.

## 7. Status końcowy

**K-MARS-DAS v0.1 — preregistered, not run.** Sekcje 1-5 nie mogą się
zmienić po zobaczeniu wyniku.
