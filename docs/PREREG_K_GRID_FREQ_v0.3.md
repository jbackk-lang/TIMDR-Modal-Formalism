# Gałąź K na częstotliwości sieci elektroenergetycznej — prerejestracja v0.3 (nowa statystyka)

**Status: PREREGISTERED, NOT YET RUN.** Zamrożone PRZED uruchomieniem.
Reaguje na v0.1/v0.2 (`RESULT_K_GRID_FREQ_v0.1.md`,
`RESULT_K_GRID_FREQ_v0.2.md`): dwie kolejne próby oparte na
ekstrakcji `(f,φ,A)` przez dominujący szczyt FFT + kalibrowany `eps_f`
dały INCONCLUSIVE z tego samego strukturalnego powodu (masa punktowa w
rozkładzie różnic częstotliwości). v0.3 **zmienia samą statystykę
testu**, nie kolejny parametr — decyzja użytkownika po przedstawieniu
trzech opcji (test na identyczności binu / korelacja krzyżowa / zakończ
wątek): wybrana **korelacja krzyżowa**.

## 0. Zakres tej zmiany — jawnie ograniczony

Ta prerejestracja NIE modyfikuje `is_resonant()`, `_fft_peak_f_phi_A()`
ani żadnego wcześniejszego testu K (Ridgecrest, MARS DAS v0.1/v0.2,
GRID-FREQ v0.1/v0.2 pozostają zgłoszone dokładnie tak, jak były).
Korelacja krzyżowa jest ALTERNATYWNĄ operacjonalizacją "wyrównania
częstotliwości/fazy" (Aksjomat 5) DLA TEGO KONKRETNEGO TESTU —
uzasadnienie: dwa sygnały o silnie skorelowanych chwilowych
fluktuacjach (po usunięciu trendu) dzielą tę samą dominującą treść
niskoczęstotliwościową, co jest ciągłym odpowiednikiem dyskretnego
"ten sam szczyt FFT" bez podatności na degenerację kwantyzacji z
v0.1/v0.2.

## 1. Dane, para, okno — w pełni odziedziczone, zero zmian

```text
plik: SYNC01.csv, sha256 identyczny jak v0.1/v0.2
kanał A: f50_PT (Lizbona), kanał B: f50_TR (Stambuł)
reguła wyboru okna: ten sam najdłuższy ciągły odcinek
  (start 2019-08-01 23:30:46, długość 238 902 s)
window_sec: 600 (niezmienione, konwencja LFO)
n_windows: 398
```

## 2. Nowa statystyka — zamrożona PRZED uruchomieniem

**Krok 1 — odtrendowanie**: dla każdego okna, każdego kanału osobno,
usunięcie liniowego trendu metodą najmniejszych kwadratów
(`scipy.signal.detrend(..., type='linear')` lub równoważny
`polyfit`/odjęcie dopasowanej prostej) — standardowa, generyczna
technika, niedostrojona do tego zbioru.

**Krok 2 — korelacja krzyżowa przy opóźnieniu ZERO** (bez przeszukiwania
opóźnień — obie serie dzielą jedną kolumnę `Time`, więc zero-lag jest
fizycznie poprawnym wyborem; przeszukiwanie opóźnień i wybór
najlepszego byłoby dokładnie tym rodzajem post-hoc dopasowania, którego
ten ekosystem unika): współczynnik korelacji Pearsona
`r_w = corr(detrend(s_PT_w), detrend(s_TR_w))` dla każdego okna `w`.

**Krok 3 — statystyka testu**: `real_stat = mean(r_w)` po wszystkich
398 oknach.

**Krok 4 — test permutacyjny** (ten sam szkielet co v0.1/v0.2/MARS,
zero zmian w mechanice): losowa permutacja indeksów okien kanału TR
(`seed=0`, `n_permutations=2000`), dla każdej permutacji policz
`null_stat = mean(corr(detrend(s_PT_w), detrend(s_TR_perm(w))))`.
`p_value = (#{null_stat ≥ real_stat} + 1) / (n_permutations + 1)`
(jednostronny, bo hipoteza przewiduje DODATNIĄ korelację).

**Krok 5 — kontrola pozytywna**: `real_stat_pos = mean(corr(detrend(s_PT_w),
detrend(s_PT_w)))` — trywialnie `1.0` (kanał sparowany sam ze sobą, ten
sam indeks okna). Null przez tę samą permutację indeksów PT vs PT.
`controls_passed = (p_value_pos < alpha)`.

**Brak kalibracji `eps`** — ta statystyka jest ciągła (współczynnik
korelacji ∈[-1,1]), nie wymaga progu binarnego `is_resonant()`, więc
degeneracja kwantyzacji z v0.1/v0.2 nie może wystąpić strukturalnie.

## 3. Parametry bez zmian

```text
n_permutations: 2000
seed: 0
alpha: 0.05
MIN_WINDOWS_FOR_TEST: 20 (398 >> próg)
```

## 4. Werdykt

```text
controls_passed = false  → INCONCLUSIVE
controls_passed = true, p_value < alpha → SUPPORTED
controls_passed = true, p_value >= alpha → NOT SUPPORTED
```

## 5. Przewidywanie — zapisane PRZED uruchomieniem

Oczekiwane: kontrola pozytywna przejdzie czysto (korelacja sygnału z
samym sobą = 1.0, permutacyjny null << 1.0, p≈0.0005). Test główny —
otwarty: jeśli 94.7%-owa zgodność dominującego binu FFT z v0.2
odzwierciedlała realną zgodność niskoczęstotliwościowej treści, `mean(r_w)`
powinno być wyraźnie dodatnie i istotne (SUPPORTED). Jeśli była
artefaktem samej metody ekstrakcji FFT (a nie faktycznej korelacji
kształtu przebiegu), `mean(r_w)` może wyjść blisko zera (NOT SUPPORTED).
Obie możliwości są zgłaszane z równą uczciwością.

## 6. Zasada anty-tuningu

Po zobaczeniu wyniku nie wolno zmieniać: metody detrendowania, wyboru
lag=0 (bez przeszukiwania opóźnień), `window_sec`, pary lokalizacji,
reguły wyboru okna, `seed`, `n_permutations`. Kolejna zmiana wymaga
nowej prerejestracji v0.4.

## 7. Uczciwe ograniczenia przewidziane z góry

1. Korelacja krzyżowa przy zero-lag zakłada brak istotnego opóźnienia
   propagacji między lokalizacjami — dla efektów systemowych sieci AC
   (nie propagacji falowej w ośrodku fizycznym) to rozsądne założenie,
   ale nie niezależnie zweryfikowane.
2. `mean(r_w)` uśrednia po całym odcinku 66 godzin — nie wykrywa
   krótkotrwałych epizodów silnej korelacji ukrytych w średniej.
3. To wciąż jeden ciągły odcinek, jedna para lokalizacji — nawet
   SUPPORTED wymagałoby repliki.
4. Zmiana statystyki między v0.2 a v0.3 oznacza, że wyniki NIE są
   bezpośrednio porównywalne liczbowo (różne miary) — porównywalna
   jest tylko końcowa klasyfikacja SUPPORTED/NOT SUPPORTED/INCONCLUSIVE.

## 8. Status końcowy

**K-GRID-FREQ v0.3 — preregistered, not run.** Sekcje 0-7 nie mogą się
zmienić po zobaczeniu wyniku.
