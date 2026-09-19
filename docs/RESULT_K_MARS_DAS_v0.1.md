# Wynik K-MARS-DAS v0.1 (2026-09-19) — NOT SUPPORTED

Zgodnie z `PREREG_K_MARS_DAS_v0.1.md`, zamrożonym PRZED pobraniem pliku.
Pierwszy test operatora rezonansu modalnego (`is_resonant()`, Aksjomat 5)
na prawdziwym sygnale światłowodowym (DAS) — dotąd jedyna realna
walidacja gałęzi K używała danych sejsmometrycznych (Ridgecrest).

## Dane

```text
plik: 20220730T233258Z.h5 (MARS/SeaFOAM, Monterey Bay)
sha256: 72068d15979d59d49bb4ba2f83f0bc109193081418f779c6b6381470b591d406
kształt: (2845 kanałów, 12000 próbek czasu)
dt_s: 0.0049998760... (≈200 Hz)
dx_m: 5.2 (rozstaw kanałów) -> ~14.8 km rejestrowanego odcinka kabla
czas trwania: 60.0 s
```

`event_time`/`magnitude` w tym konkretnym pliku są puste
(`event_time_index=-1`) — plik nie ma potwierdzonego dopasowania do
katalogu trzęsień ziemi w metadanych zbioru; traktowany mimo to jako
zamrożony wybór "pierwszy plik na liście", zgodnie z regułą z §1
prerejestracji (nie wybieraliśmy pliku po jego jakości/zawartości).

## Kanały (modalności)

```text
kanał A = 0        (pierwszy kanał w pliku)
kanał B = 2844      (ostatni kanał w pliku, nch-1)
```

Zamrożona reguła geometryczna (skrajne końce zarejestrowanego odcinka),
nie wybór po zobaczeniu sygnału.

## Wynik surowy

| | wartość |
|---|---|
| okna (1.0 s każde) | 60 |
| eps_f (kalibrowane, percentyl 10%) | 1.0000 Hz |
| eps_phi (kalibrowane, percentyl 10%) | 0.2578 rad |
| kontrola pozytywna (kanał A vs A) | rate=1.0, p=0.0005 ✓ |
| `controls_passed` | **true** |
| test główny: rezonans realny | 1/60 = 0.0167 |
| test główny: p (permutacyjny, 2000 permutacji) | **0.3653** |
| Werdykt | **NOT SUPPORTED** |

## Interpretacja

Mechanika testu działa poprawnie (kontrola pozytywna wykryta czysto,
p≈0.0005) — to NIE jest porażka metody, tylko rzeczywisty wynik
negatywny: między skrajnymi końcami ~14.8 km odcinka kabla, w tym
konkretnym 60-sekundowym oknie, dominująca częstotliwość i faza
(per-sekundowe okna FFT) nie wyrównują się częściej niż przypadek. Realna
stopa rezonansu (1/60) jest NIŻSZA niż mediana null permutacyjnego —
zero przesłanki w stronę SUPPORTED.

To jest **uczciwy wynik negatywny**, dokładnie ten sam wzorzec co
Krakow_Centrum dla gałęzi M/S: mechanika działa, kontrola pozytywna to
potwierdza, ale sam sygnał testowy nie pokazuje efektu ponad przypadek —
w odróżnieniu od Krakow_Centrum, TU test miał wystarczającą moc
(60 okien, powyżej progu 20), więc to NIE jest "zero mocy", tylko
faktyczny brak wykrytego rezonansu modalnego między tymi dwoma kanałami w
tym oknie.

## Uczciwe ograniczenia

1. **Jeden plik, jedno okno czasowe, jedna para kanałów** — brak testu
   przenośności (inny plik, inna para kanałów, inny rozstaw
   przestrzenny między A i B).
2. **`event_time` puste w tym pliku** — nie wiadomo z pewnością, czy plik
   zawiera rzeczywiste zdarzenie sejsmiczne, czy tło; wybór pliku był
   mechaniczny ("pierwszy na liście"), więc to nie zniekształca wyniku,
   ale ogranicza jego interpretację fizyczną.
3. **Ekstremalny rozstaw kanałów (A=0, B=2844, ~14.8 km)** — może to być
   ZA DUŻO dla realnego wyrównania fazowego nawet gdyby modalny rezonans
   istniał lokalnie; reguła wyboru była geometryczna (skrajne końce), nie
   fizycznie umotywowana odległością korelacji.
4. **`window_sec=1.0 s`** — arbitralny wybór eksploracyjny (jak w
   Ridgecrest), nie skalibrowany do żadnej znanej częstotliwości
   charakterystycznej sygnału DAS.

## Co dalej (otwarte, nie zrobione tutaj)

1. Powtórzenie z parą kanałów BLIŻEJ siebie (np. A, A+10) — test, czy
   rezonans modalny pojawia się przy mniejszym rozstawie przestrzennym,
   wymagałoby OSOBNEJ prerejestracji (nowa reguła wyboru kanałów,
   zamrożona przed wynikiem).
2. Plik z potwierdzonym `event_time`/`magnitude` (np. `arcata` zamiast
   `monterey_bay`, gdzie metadane zdarzeń są pełniejsze).
3. Wiele plików/wiele par kanałów jako właściwy test przenośności,
   analogicznie do replik Brownie→Eggs w gałęzi G.

## Status: NOT SUPPORTED (pierwszy test K na sygnale światłowodowym, jedna próba, jedna para kanałów)

Zgodnie ze słownikiem statusów: **NIE ustalony** (pojedynczy wynik
negatywny, kontrole poprawne, brak testu przenośności). Nie odrzuca
istnienia rezonansu modalnego w danych DAS w ogóle — odrzuca go tylko
dla TEJ pary kanałów, TEGO okna czasowego, TEJ metody ekstrakcji.
