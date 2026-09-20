# Gałąź K na częstotliwości sieci elektroenergetycznej — prerejestracja v0.5 (replika na niezależnym źródle: surowe dane per-stacja, inny plik, inna rozdzielczość)

**Status: PREREGISTERED, NOT YET RUN.** Zamrożone PRZED uruchomieniem
statystyki (granice okna wyznaczone deterministycznie z dostępności
danych, jak w v0.1/v0.4 — patrz §2).

## 0. Dlaczego ta prerejestracja istnieje

`RESULT_K_GRID_FREQ_v0.3.md` (SUPPORTED, z=78.2) i `RESULT_K_GRID_FREQ_v0.4.md`
(replika SUPPORTED, z=63.0) obie używają **tego samego pliku**
(`SYNC01.csv`) — dwóch nienachodzących okien z tego samego 41-dniowego
zapisu i tego samego miesiąca (sierpień 2019). `PREREG_K_GRID_FREQ_v0.4.md`
§8 zastrzegł wprost: replika na innym roku/źródle/parze lokalizacji
pozostaje otwarta. Ta prerejestracja adresuje TĘ konkretną lukę —
**inny plik źródłowy** (osobne pliki per-stacja zamiast wspólnego,
wstępnie zsynchronizowanego `SYNC01.csv`), z tej samej bazy
(KIT Power Grid Frequency Database, Jumar et al. 2020), ale
udostępniony osobno w 2023.

**Uczciwe zastrzeżenie z góry**: to NIE jest inny rok pomiarowy — po
rozpakowaniu okazało się, że `PT_LI01_100ms.zip`/`TUR-IS01_100ms.zip`
(mimo daty publikacji na OSF 2023-04-21) zawierają dane z **tej samej
kampanii pomiarowej 2019 r.** (PT: 2019-07-09 do 2019-08-16, TR:
2019-07-09 do 2019-08-18), tylko w surowej, natywnej rozdzielczości
10 Hz per-stacja, zamiast wstępnie zsynchronizowanego do 1 Hz pliku
zbiorczego. To odkryto PO pobraniu plików (nie dało się sprawdzić z
samych metadanych OSF) — zgłoszone tu wprost, żeby nie zawyżać
znaczenia tej repliki: to replika na **innym pliku źródłowym i innej
rozdzielczości**, na **niezachodzącym oknie czasowym** (lipiec zamiast
sierpnia), ale wciąż tym samym rokiem/kampanią/parą stacji co v0.1-v0.4.

## 1. Dane

```text
plik A: PT_LI01_100ms.zip
  sha256: 31c28fe570751693b42f1f7074ba5dbd73d4ecde9041efe52d5b5f756381501f
  zawartość: PT_LI01_100msForOSF.csv (Time;f50_PT;QI_PT), 10 Hz, 2019-07-09..2019-08-16

plik B: TUR-IS01_100ms.zip
  sha256: 390a2431a913d6ad1cddd206fba7de32f65a3ad105e2ad3aff3d865bf4106938
  zawartość: TUR-IS01_100msForOSF.csv (Time;f50_TR;QI_TR), 10 Hz, 2019-07-09..2019-08-18

Źródło: OSF node by5hu (KIT Power Grid Frequency Database),
folder /FrequencyData/PT_LI01/ i /FrequencyData/TUR_IS01/, dodane
2023-04-21 — osobne od folderu /FrequencyData/sync01/ (SYNC01.csv,
użyty w v0.1-v0.4).
```

## 2. Reguła wyboru okna — deterministyczna, oparta na dostępności danych

Zamiast skanować cały 38-41-dniowy zapis (kosztowne obliczeniowo w
tej sesji — dekompresja ~1 GB na plik), zawężono poszukiwanie do
pierwszych 48 godzin obu plików PO ich wspólnym starcie
(`2019-07-11 00:00:00` – `2019-07-13 00:00:00`) — wybrane WYŁĄCZNIE
dla szybkości ekstrakcji (blisko początku pliku), NIE dopasowane do
wyniku (żadna wartość `f50_PT`/`f50_TR` nie została jeszcze policzona
w momencie wyboru tego przedziału sondażowego). W tym 48-godzinnym
oknie znaleziono wszystkie ciągłe odcinki, w których `QI_PT=0 AND
QI_TR=0` jednocześnie dla każdej próbki (10 Hz), i wybrano
NAJDŁUŻSZY:

```text
start (wiersz danych, 0-indeksowany, po nagłówku):
  plik A (PT):  RUN_START_ROW = 1767960
  plik B (TUR): RUN_START_ROW = 1837470
  (różne indeksy wierszy — pliki mają różne znaczniki czasu startu,
  1h56min różnicy — ale IDENTYCZNY zakres czasowy po przeliczeniu:
  zweryfikowano bezpośrednio, że wiersze te odpowiadają tej samej
  sekundzie zegarowej w obu plikach)
run_len: 269919 próbek (10 Hz) = 26991.9 s ≈ 7.50 h
start_time: 2019-07-11 22:07:59.1
end_time:   2019-07-12 05:37:50.9
```

Zweryfikowano bezpośrednio (nie założono): 0 wierszy `QI_PT≠0` i 0
wierszy `QI_TR≠0` w całym wybranym oknie; znaczniki czasu obu plików
zgadzają się dokładnie wiersz-po-wierszu (0 niezgodności na 269919
porównań).

## 3. Statystyka — odziedziczona 1:1 z v0.3/v0.4, tylko FS_HZ zmienione

Krok 1 (odtrendowanie liniowe per okno per kanał), krok 2 (korelacja
Pearsona zero-lag `r_w`), krok 3 (`real_stat=mean(r_w)`), krok 4 (test
permutacyjny, `seed=0`, `n_permutations=2000`), krok 5 (kontrola
pozytywna PT-vs-PT) — identyczne jak `PREREG_K_GRID_FREQ_v0.3.md` §2.
**Jedyna zmiana**: `FS_HZ=10.0` (zamiast `1.0`), więc `n_per_window =
window_sec * FS_HZ = 6000` próbek (zamiast 600) — konsekwencja
wyższej natywnej rozdzielczości źródła, nie zmiana metody.

## 4. Parametry

```text
window_sec: 600 (niezmienione)
FS_HZ: 10.0 (NOWE — było 1.0 w v0.1-v0.4)
n_per_window: 6000
n_windows: 269919 // 6000 = 44  (>> MIN_WINDOWS_FOR_TEST=20)
n_permutations: 2000
seed: 0
alpha: 0.05
```

## 5. Werdykt

```text
controls_passed = false                    → INCONCLUSIVE
controls_passed = true, p_value < alpha    → SUPPORTED
controls_passed = true, p_value >= alpha   → NOT SUPPORTED
```

## 6. Przewidywanie — zapisane PRZED uruchomieniem

Jeśli wynik v0.3/v0.4 (mediana r≈0.91-0.92, z=63-78) odzwierciedla
realną, systemową własność sieci AC — niezależną od konkretnego pliku,
rozdzielczości czy miesiąca — replika na tym niezależnym pliku/oknie
powinna dać podobnie silny, dodatni, istotny wynik (SUPPORTED). Wyższa
rozdzielczość (10 Hz vs 1 Hz) może też zmienić medianę korelacji w
którąkolwiek stronę (więcej szumu wysokoczęstotliwościowego per próbka
mogłoby ją obniżyć; więcej punktów per okno mogłoby ją ustabilizować) —
obie strony przewidywania niepewne, oceniane z równą uczciwością.

## 7. Zasada anty-tuningu

Po zobaczeniu wyniku nie wolno zmieniać: wyboru pliku, reguły wyboru
okna (§2), metody detrendowania, lag=0, `window_sec`, `FS_HZ`, `seed`,
`n_permutations`. Kolejna zmiana wymaga nowej prerejestracji v0.6.

## 8. Uczciwe ograniczenia przewidziane z góry

1. **To wciąż ta sama kampania pomiarowa 2019 i ta sama para stacji**
   (patrz zastrzeżenie w §0) — nie jest to replika na innym roku ani
   innej parze lokalizacji, tylko na innym pliku/rozdzielczości/oknie
   czasowym z tej samej kampanii.
2. Okno sondażowe (lipiec 11-13) zostało wybrane dla szybkości
   ekstrakcji, nie w pełni losowo z całego 38-41-dniowego zakresu —
   pełne skanowanie całego zakresu obu plików pozostaje przyszłą pracą.
3. `mean(r_w)` uśrednia po 7.5-godzinnym odcinku — krótszym niż okna
   v0.3 (66h) i v0.4 (51h) — mniejsza próba (44 okna vs 398/305).

## 9. Status końcowy

**K-GRID-FREQ v0.5 — preregistered, not run.** Sekcje 0-8 nie mogą się
zmienić po zobaczeniu wyniku.
