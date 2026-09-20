# Gałąź K na częstotliwości sieci elektroenergetycznej — prerejestracja v0.4 (replikacja na niezależnym oknie)

**Status: PREREGISTERED, NOT YET RUN.** Zamrożone PRZED uruchomieniem
statystyki (choć PO deterministycznym wyznaczeniu granic okna, patrz §2 —
dokładnie ta sama kolejność co w v0.1: reguła wyboru okna dotyczy
dostępności danych, nie hipotezy).

## 0. Dlaczego ta prerejestracja istnieje

`RESULT_K_GRID_FREQ_v0.3.md` dał **SUPPORTED** (z=78.2, p=0.0005,
mediana korelacji PT↔TR 0.91) na JEDNYM, ciągłym 66.4-godzinnym oknie
(`RUN_START_ROW=2071846`, 2019-08-01 23:30:46). Prereg v0.3 §7 pkt 3
zastrzegł wprost: *"To wciąż jeden ciągły odcinek, jedna para
lokalizacji — nawet SUPPORTED wymagałoby repliki."* Protokół
anty-numerologiczny tego ekosystemu (§2 pkt 9 `timdr-signal-framework`)
wymaga replikacji na niezależnym zbiorze/oknie przed uznaniem
pojedynczego pozornie pozytywnego wyniku za ustalony. Ta prerejestracja
jest tą replikacją.

## 1. Zmiana względem v0.3 — TYLKO okno, zero innych zmian

Statystyka, plik danych, para kanałów, `window_sec`, `n_permutations`,
`seed`, `alpha` są odziedziczone 1:1 z `PREREG_K_GRID_FREQ_v0.3.md` —
zero zmian w metodzie. Jedyna zmienna to granice okna czasowego.

## 2. Nowe okno — reguła deterministyczna, ustalona PRZED policzeniem statystyki

Reguła (analogiczna do v0.1 §3, rozszerzona o wymóg niezależności od
okna już użytego): **drugi najdłuższy ciągły odcinek, w którym
`QI_PT=0 AND QI_TR=0` dla każdej sekundy, spośród odcinków NIE
nachodzących na okno użyte w v0.1/v0.2/v0.3** (`start_row=2071846`,
`len=238902`, tj. wiersze `[2071846, 2310748)`).

Zmierzone deterministycznie (skan wszystkich ciągłych bloków
`QI_PT=0 AND QI_TR=0` w `SYNC01.csv`, posortowane malejąco po
długości):

```text
1. start_row=2071846, len=238902 s  -- UŻYTE w v0.1/v0.2/v0.3, WYKLUCZONE tutaj
2. start_row=2913363, len=183407 s  -- WYBRANE (pierwszy nienachodzący, deterministycznie)
3. start_row=2729646, len=175337 s
4. start_row=489335,  len=154252 s
...
```

Wybrany blok (#2, pierwszy na liście po wykluczeniu #1):

```text
plik: SYNC01.csv, sha256 identyczny jak v0.1-v0.3
     (2f81120c9057adac332cd910c92130cc1c023068940f61cd824d7e860a0bee83)
run_start_row: 2913363
run_len_s: 183407  (~50.9 h)
start_time: 2019-08-11 17:16:03  (10 dni po oknie v0.3, zero nakładania)
```

## 3. Statystyka — odziedziczona 1:1 z v0.3, zero zmian

Krok 1 (odtrendowanie liniowe per okno per kanał), krok 2 (korelacja
Pearsona zero-lag `r_w`), krok 3 (`real_stat = mean(r_w)`), krok 4
(test permutacyjny, `seed=0`, `n_permutations=2000`), krok 5 (kontrola
pozytywna PT-vs-PT) — dokładnie jak `PREREG_K_GRID_FREQ_v0.3.md` §2,
żadna litera nie zmieniona.

## 4. Parametry bez zmian

```text
window_sec: 600
n_permutations: 2000
seed: 0
alpha: 0.05
MIN_WINDOWS_FOR_TEST: 20  (183407 // 600 = 305 okien >> próg)
```

## 5. Werdykt

```text
controls_passed = false                    → INCONCLUSIVE
controls_passed = true, p_value < alpha    → SUPPORTED
controls_passed = true, p_value >= alpha   → NOT SUPPORTED
```

## 6. Przewidywanie — zapisane PRZED uruchomieniem

Jeśli wynik v0.3 (mediana r≈0.91, z=78) odzwierciedla realną, systemową
własność sieci AC (a nie artefakt jednego okna czasowego), to okno #2
— inna para dni, ten sam obszar synchroniczny — powinno dać podobnie
silny, dodatni, istotny wynik (SUPPORTED, korelacja rzędu 0.8-0.95).
Jeśli wynik v0.3 był artefaktem konkretnych warunków sieciowych z
początku sierpnia 2019 (np. lokalny epizod niestabilności), replika
może dać słabszy lub nieistotny wynik. Obie możliwości zgłaszane z
równą uczciwością.

## 7. Zasada anty-tuningu

Po zobaczeniu wyniku nie wolno zmieniać: reguły wyboru okna (§2),
metody detrendowania, wyboru lag=0, `window_sec`, pary lokalizacji,
`seed`, `n_permutations`. Kolejna zmiana wymaga nowej prerejestracji v0.5.

## 8. Uczciwe ograniczenia przewidziane z góry

1. To wciąż JEDNA para lokalizacji (PT/TR) i JEDEN plik źródłowy —
   replika na innej parze krajów lub innym źródle danych pozostaje
   otwarta nawet po tym teście.
2. Oba okna (v0.3 i v0.4) pochodzą z tego samego 41-dniowego pliku i
   tego samego miesiąca (sierpień 2019) — to replika NA NIEZALEŻNYM
   OKNIE CZASOWYM, nie na niezależnym zbiorze danych czy roku. Silniejsza
   replika (inny rok, inne źródło) pozostaje przyszłą pracą.
3. `mean(r_w)` uśrednia po całym 50.9-godzinnym odcinku — nie wykrywa
   krótkotrwałych epizodów.

## 9. Status końcowy

**K-GRID-FREQ v0.4 — preregistered, not run.** Sekcje 0-8 nie mogą się
zmienić po zobaczeniu wyniku.
