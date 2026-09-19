# Gałąź K na częstotliwości sieci elektroenergetycznej — prerejestracja v0.1

**Status: PREREGISTERED, NOT YET RUN.** Zamrożone PRZED wywołaniem
ekstrakcji `(f,φ,A)` czy testu statystycznego. Fizycznie umotywowany
kandydat na potwierdzenie rezonansu modalnego (Aksjomat 5) — w
odróżnieniu od Ridgecrest (sejsmika, hipoteza otwarta) i MARS DAS
(światłowód, hipoteza otwarta, oba NOT SUPPORTED), tu FIZYKA sieci AC z
definicji wymusza niemal identyczną częstotliwość w każdym punkcie
jednego obszaru synchronicznego — to najsilniejszy a priori argument za
oczekiwanym wyrównaniem częstotliwości spośród wszystkich dotychczasowych
testów K.

**Uczciwe zastrzeżenie na starcie**: to NIE jest polowanie na zbiór
danych, który "zadziała" — wybór umotywowany fizyką PRZED zobaczeniem
wyniku, dokładnie jak przy wyborze fal Scholte'a dla MARS (który mimo
motywacji fizycznej dał NOT SUPPORTED). Jeśli i ten test da NOT
SUPPORTED, zostanie zgłoszony tak samo uczciwie jak poprzednie dwa.

## 1. Dane — struktura ustalona przez deterministyczną inspekcję (nie dotyczy hipotezy)

```text
plik: SYNC01.csv (OSF, https://osf.io/p5xyr/download, 218 MB)
sha256: 2f81120c9057adac332cd910c92130cc1c023068940f61cd824d7e860a0bee83
wiersze: 3 542 400 (41 dni, rozdzielczość 1 s)
kolumny: Time; f50_DE_KA; QI_DE_KA; f50_DE_OL; QI_DE_OL; f50_PT; QI_PT; f50_TR; QI_TR
```

`f50_XX` — odchylenie częstotliwości od 50 Hz w mHz (wartość placeholder
`0` gdy `QI_XX≠0`). `QI_XX` — wskaźnik jakości (0 = poprawny pomiar,
≠0 = brak/nieprawidłowy pomiar). Wszystkie cztery lokalizacje dzielą
JEDNĄ kolumnę `Time` — pełna, gotowa synchronizacja czasu, zero potrzeby
przeliczania offsetu (mocniejsza własność niż nawet DAS).

## 2. Para lokalizacji — zamrożona PRZED pobraniem pliku (w poprzedniej wiadomości)

```text
kanał A = f50_PT  (Lizbona, Portugalia)
kanał B = f50_TR  (Stambuł, Turcja)
```

Reguła: największy dystans geograficzny w zbiorze (~3400 km) —
najbardziej rygorystyczny test synchronizacji jednego obszaru
synchronicznego (Continental Europe).

## 3. Reguła wyboru okna czasowego — deterministyczna, oparta na DOSTĘPNOŚCI danych, nie na wyniku

`QI_PT`/`QI_TR` mają luki (różne okresy niedostępności pomiaru per
lokalizacja). Zamrożona reguła: użyj NAJDŁUŻSZEGO CIĄGŁEGO odcinka, w
którym `QI_PT=0 AND QI_TR=0` dla KAŻDEJ sekundy. To pytanie o dostępność
danych, nie o hipotezę rezonansu — analogiczne do `n_valid_blocks`
liczonego deterministycznie w manifeście B4-Kitchen.

Zmierzone (deterministycznie, PRZED ekstrakcją `f,φ,A`):

```text
najdłuższy ciągły odcinek: początek 2019-08-01 23:30:46, długość 238 902 s (~66.4 h)
```

## 4. Okno analizy (`window_sec`) — uzasadnienie DOMENOWE, nie dopasowane do tego zbioru

`window_sec = 600 s` (10 minut) — standardowa długość okna w literaturze
analizy oscylacji międzyobszarowych (inter-area low-frequency
oscillations) systemów elektroenergetycznych (typowo 0.1-1 Hz, analiza
Prony'ego/FFT na oknach rzędu 5-15 minut). Decyzja podjęta na podstawie
konwencji dziedzinowej, NIE dopasowana do zawartości tego konkretnego
pliku.

```text
n_per_window = 600 (fs=1 Hz)
n_windows = floor(238902 / 600) = 398
```

398 okien — znacznie powyżej progu mocy statystycznej (20).

## 5. Ekstrakcja (f,φ,A) — w pełni odziedziczona, zero zmian

Identyczna z `_fft_peak_f_phi_A()` + `_local_phase_to_global()`
(`timdr_modal/real_data_validation.py`), zastosowana do surowego szeregu
`f50_XX` (odchylenie częstotliwości w mHz) jako sygnału wejściowego —
zamiast do surowej fali akustycznej/sejsmicznej. Odejmowana jest średnia
okna (usunięcie składowej DC), szczyt FFT szukany z wykluczeniem binu
f=0, faza przeliczona na konwencję sinusową i na wspólne `t=0` startu
odcinka (`t_start = window_index × window_sec` — zero offsetu
międzystacyjnego, bo obie lokalizacje dzielą jedną kolumnę `Time`).

To wykrywa DOMINUJĄCY TRYB OSCYLACJI NISKOCZĘSTOTLIWOŚCIOWEJ (nie samą
wartość 50 Hz, która jest odjęta w źródle danych) w każdym oknie — fizyczny
sens: czy oscylacje międzyobszarowe (znane zjawisko w sieciach AC) są
zgodne fazowo/częstotliwościowo między Lizboną a Stambułem.

## 6. Kalibracja i test statystyczny — bez zmian z Ridgecrest/MARS

```text
target_real_rate (calibrate_epsilons): 0.1
n_permutations: 2000
seed: 0
alpha: 0.05
kontrola pozytywna: kanał PT sparowany sam ze sobą
```

## 7. Werdykt i zasada anty-tuningu

Identyczna trójstopniowa klasyfikacja co w Ridgecrest/MARS. Po zobaczeniu
wyniku nie wolno zmieniać: wyboru pary lokalizacji, reguły wyboru okna
czasowego (najdłuższy ciągły odcinek), `window_sec`, `target_real_rate`,
`seed`. Jeśli wynik to NOT SUPPORTED/INCONCLUSIVE, kolejna zmiana
(np. inny odcinek czasowy, inna para) wymaga nowej prerejestracji v0.2 z
jawnym uzasadnieniem.

## 8. Co ten test NIE rozstrzyga

Jedna para lokalizacji, jeden ciągły odcinek 66 godzin z 41-dniowego
zbioru — nie test na wszystkich czterech lokalizacjach, nie replika na
innym obszarze synchronicznym. Nawet SUPPORTED byłoby pierwszym
pozytywnym sygnałem K na realnych danych w ogóle (po dwóch negatywnych:
Ridgecrest niejednoznaczny, MARS DAS NOT SUPPORTED), wymagającym
własnej repliki przed uznaniem za ustalone.

## 9. Status końcowy

**K-GRID-FREQ v0.1 — preregistered, not run.** Sekcje 1-7 nie mogą się
zmienić po zobaczeniu wyniku.
