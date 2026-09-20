# Wynik K-GRID-FREQ v0.4 (2026-09-20) — **SUPPORTED** (replika v0.3 na niezależnym oknie)

Zgodnie z `PREREG_K_GRID_FREQ_v0.4.md`, zamrożonym PRZED uruchomieniem
statystyki. Ten sam plik (`SYNC01.csv`, identyczny sha256), ta sama
para kanałów (PT/TR), identyczna statystyka co `RESULT_K_GRID_FREQ_v0.3.md`
(korelacja krzyżowa zero-lag odtrendowanych okien) — jedyna zmienna to
okno czasowe: drugi najdłuższy ciągły odcinek `QI_PT=0 AND QI_TR=0`,
deterministycznie wybrany jako pierwszy nienachodzący na okno v0.1-v0.3,
10 dni później (2019-08-11 17:16:03 vs 2019-08-01 23:30:46 w v0.3).

## Wynik surowy

```text
n_windows: 305 (okno 50.9 h, vs 398 okien / 66.4 h w v0.3)
statystyka: mean(r_w), Pearson r zero-lag, okna odtrendowane liniowo

real_stat (mean korelacji PT↔TR): 0.9164   (v0.3: 0.9009)
mediana r_w: 0.9190                        (v0.3: 0.9057)
25.-75. percentyl: 0.895 - 0.938           (v0.3: 0.882 - 0.925)
null (permutacyjny): mean=0.0235, std=0.0142
z-score realnego vs null: 63.0             (v0.3: 78.2)
p-value: 0.0005 (0/2000 permutacji ≥ realny wynik)

kontrola pozytywna (PT vs PT): stat=1.0, p=0.0005 ✓
controls_passed: true

Werdykt: SUPPORTED
```

## Zgodność z przewidywaniem z prerejestracji

Prereg v0.4 §6 przewidział: jeśli wynik v0.3 odzwierciedla realną,
systemową własność sieci AC (nie artefakt jednego okna), replika na
niezależnym, nienachodzącym oknie powinna dać podobnie silny wynik
(SUPPORTED, korelacja rzędu 0.8-0.95). **Potwierdzone** — mediana
korelacji 0.919 (v0.3: 0.906), z=63.0 (v0.3: 78.2, różnica wynika
głównie z liczby okien: 305 vs 398, nie z siły efektu — mediany i
IQR obu okien praktycznie się pokrywają).

## Co ta replika faktycznie ustala — i czego NIE ustala

**Ustala**: wynik v0.3 nie był artefaktem jednego, konkretnego
66-godzinnego okna z początku sierpnia 2019 — ten sam efekt
(silna, dodatnia, wysoce istotna korelacja niskoczęstotliwościowych
fluktuacji częstotliwości sieci między Lizboną a Stambułem) występuje
też w innym, niezależnym 51-godzinnym oknie 10 dni później. To
domyka dokładnie tę lukę, którą prereg v0.3 §7 pkt 3 zostawił otwartą
("nawet SUPPORTED wymagałoby repliki").

**NIE ustala** (odziedziczone wprost z ograniczeń v0.3 + nowe z v0.4
§8): oba okna pochodzą z TEGO SAMEGO 41-dniowego pliku i tego samego
miesiąca (sierpień 2019) — to replika na niezależnym OKNIE, nie na
niezależnym ROKU, ŹRÓDLE ani PARZE LOKALIZACJI. Silniejsza replika
(inny rok, inny zbiór, inna para krajów) pozostaje otwartym, przyszłym
krokiem. Interpretacyjne zastrzeżenie z v0.3 pozostaje w mocy: to
fizycznie gwarantowane wyrównanie częstotliwości sieci AC, nie
"odkrycie ukrytego rezonansu" — wynik waliduje MECHANIKĘ testu
(operator K poprawnie wykrywa znane, silne wyrównanie, gdy ono
faktycznie występuje) w drugim, niezależnym oknie, nie odkrywa nowej
fizyki.

## Zasada anty-tuningu — przestrzegana

Zero zmian względem v0.3 poza granicami okna, zamrożonymi w
`PREREG_K_GRID_FREQ_v0.4.md` PRZED policzeniem statystyki (okno
wyznaczone deterministyczną regułą dostępności danych, nie dopasowane
do wyniku).
