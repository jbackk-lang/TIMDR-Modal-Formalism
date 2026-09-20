# Wynik K-GRID-FREQ v0.5 (2026-09-20) — **SUPPORTED** (replika na niezależnym pliku źródłowym, innej rozdzielczości, nienachodzącym oknie)

Zgodnie z `PREREG_K_GRID_FREQ_v0.5.md`, zamrożonym PRZED uruchomieniem
statystyki. Ta sama statystyka co v0.3/v0.4 (korelacja krzyżowa zero-lag
odtrendowanych okien), ta sama para stacji (PT/TR), ale **inny plik
źródłowy** (`PT_LI01_100ms.zip`/`TUR-IS01_100ms.zip` — surowe dane
per-stacja 10 Hz z KIT Power Grid Frequency Database, osobno
udostępnione 2023-04-21, różne od `SYNC01.csv` użytego w v0.1-v0.4) i
**nienachodzące okno czasowe** (2019-07-11/12, ~3 tygodnie przed oknami
v0.3/v0.4 z sierpnia 2019).

## Wynik surowy

```text
n_windows: 44 (okno 7.5 h @ 10 Hz, vs 398 okien/66h w v0.3, 305/51h w v0.4)
statystyka: mean(r_w), Pearson r zero-lag, okna odtrendowane liniowo

real_stat (mean korelacji PT↔TR): 0.8784   (v0.3: 0.9009, v0.4: 0.9164)
mediana r_w: 0.8803                        (v0.3: 0.9057, v0.4: 0.9190)
25.-75. percentyl: 0.857 - 0.927           (v0.3: 0.882-0.925, v0.4: 0.895-0.938)
null (permutacyjny): mean=0.0243, std=0.0469
z-score realnego vs null: 18.2             (v0.3: 78.2, v0.4: 63.0 — spadek
  wynika głównie z n_windows=44 (vs 398/305), nie z osłabienia efektu:
  mediana/IQR pozostają w tym samym zakresie 0.86-0.93)
p-value: 0.0005 (0/2000 permutacji ≥ realny wynik)

kontrola pozytywna (PT vs PT): stat=1.0, p=0.0005 ✓
controls_passed: true

Werdykt: SUPPORTED
```

## Zgodność z przewidywaniem z prerejestracji

Prereg v0.5 §6 przewidział: jeśli wynik v0.3/v0.4 odzwierciedla realną,
systemową własność sieci AC niezależną od pliku/rozdzielczości/miesiąca,
replika na niezależnym źródle powinna dać podobnie silny wynik
(SUPPORTED). **Potwierdzone** — mediana korelacji 0.880, w tym samym
paśmie co v0.3 (0.906) i v0.4 (0.919), mimo 10× wyższej natywnej
rozdzielczości (10 Hz vs 1 Hz) i 3-tygodniowego przesunięcia okresu.
Otwarte pytanie z §6 (czy wyższa rozdzielczość podniesie czy obniży
medianę korelacji przez dodatkowy szum wysokoczęstotliwościowy) wypadło
w stronę lekkiego obniżenia (0.880 vs 0.906-0.919) — spójne z hipotezą,
że próbki 10 Hz niosą więcej lokalnego szumu pomiarowego niż uśrednione
do 1 Hz wartości w `SYNC01.csv`, choć efekt jest mały (~3 punkty
procentowe mediany) i nie zmienia werdyktu.

## Co ta replika faktycznie ustala — i czego NIE ustala (uczciwie, patrz też PREREG §0)

**Ustala**: wynik v0.3/v0.4 nie jest artefaktem jednego pliku
(`SYNC01.csv`), jednej rozdzielczości (1 Hz) ani jednego miesiąca
(sierpień 2019) — ten sam efekt (silna, dodatnia, wysoce istotna
korelacja niskoczęstotliwościowych fluktuacji częstotliwości sieci
między Lizboną a Stambułem) występuje też w kompletnie osobnym pliku,
przy 10× gęstszym próbkowaniu, w oknie przesuniętym o ~3 tygodnie.

**NIE ustala** — zastrzeżenie z `PREREG_K_GRID_FREQ_v0.5.md` §0
pozostaje w mocy: mimo osobnych plików, to wciąż ta sama kampania
pomiarowa 2019 i ta sama para stacji. Prawdziwa replika na innym roku,
innym źródle danych (np. inna sieć synchroniczna) lub innej parze
lokalizacji pozostaje otwartym, przyszłym krokiem. Interpretacyjne
zastrzeżenie z v0.3 pozostaje też w mocy: to fizycznie gwarantowane
wyrównanie częstotliwości sieci AC, nie "odkrycie ukrytego rezonansu" —
trzeci, niezależny wynik waliduje MECHANIKĘ testu, nie odkrywa nowej
fizyki.

## Podsumowanie trzech replik K-GRID-FREQ

| Wersja | Plik | fs | Okres | n_windows | mediana r_w | z | Werdykt |
|---|---|---|---|---|---|---|---|
| v0.3 | SYNC01.csv | 1 Hz | 2019-08-01/04 | 398 | 0.906 | 78.2 | SUPPORTED |
| v0.4 | SYNC01.csv | 1 Hz | 2019-08-11/13 | 305 | 0.919 | 63.0 | SUPPORTED |
| v0.5 | PT_LI01/TUR-IS01 (osobne) | 10 Hz | 2019-07-11/12 | 44 | 0.880 | 18.2 | SUPPORTED |

Trzy niezależne (pod względem pliku i/lub okna) uruchomienia tej samej,
zamrożonej statystyki dają spójny, silny, wysoce istotny wynik.

## Zasada anty-tuningu — przestrzegana

Zero zmian względem v0.3 poza `FS_HZ` (konsekwencja natywnej
rozdzielczości nowego źródła, nie wybór dopasowany do wyniku) i
granicami okna, zamrożonymi w `PREREG_K_GRID_FREQ_v0.5.md` PRZED
policzeniem statystyki.
