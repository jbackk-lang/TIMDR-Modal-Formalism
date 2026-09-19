# Wynik K-GRID-FREQ v0.1 (2026-09-19) — INCONCLUSIVE (degeneracja kalibracji eps_f)

Zgodnie z `PREREG_K_GRID_FREQ_v0.1.md`, zamrożonym PRZED odczytaniem
pliku. Para PT (Lizbona) vs TR (Stambuł), 398 okien po 600 s, odcinek
2019-08-01 23:30:46 → +238 902 s.

## Wynik surowy

```text
n_windows: 398
eps_f (kalibrowane, percentyl 10%): 0.0 Hz
eps_phi (kalibrowane, percentyl 10%): 0.002991 rad
test główny: rezonans realny: 0/398 = 0.0
test główny: p: 1.0000
kontrola pozytywna: rate=0.0, p=1.0000  ← NIE PRZESZŁA
controls_passed: false
Werdykt: INCONCLUSIVE
```

## Diagnoza mechanizmu — dlaczego kontrola pozytywna nie przeszła (nie "brak sygnału")

To NIE jest przypadek analogiczny do Ridgecrest/MARS (gdzie kontrola
pozytywna przechodziła, a test główny uczciwie nie). Tu zawiodła sama
**kalibracja `eps_f`**, z jasno zidentyfikowanej przyczyny liczbowej:

Przy `window_sec=600 s` i `fs=1 Hz`, rozdzielczość siatki częstotliwości
FFT wynosi `1/600 ≈ 0.001667 Hz`. Szczyt widma w każdym oknie ląduje w
jednym z zaledwie **10-11 dyskretnych binów** (zaobserwowane wartości
`f_PT`: 11 unikalnych, zakres 0.00167-0.01833 Hz; `f_TR`: 10 unikalnych,
podobny zakres) — bo sygnał `f50` (odchylenie od 50 Hz) w tej domenie ma
energię skupioną blisko DC, więc niemal zawsze wygrywa najniższy
nie-DC bin. Skutek: **384/398 okien (96.5%) ma DOKŁADNIE równe
`f_PT` i `f_TR`** — rozkład różnic częstotliwości jest zdegenerowany
(masa punktowa w zerze), więc percentyl 10% tego rozkładu wynosi
dokładnie `0.0`.

`is_resonant()` używa **ostrej nierówności** `|Δf|<eps_f`. Przy
`eps_f=0.0` nawet porównanie modalności **samej ze sobą** (`Δf=0`) daje
`0<0 → False` — stąd kontrola pozytywna (kanał PT sparowany z samym
sobą) sztucznie dała `rate=0.0`, mimo że częstotliwości są identyczne z
definicji. To wada kombinacji "kalibracja przez percentyl + ostra
nierówność" zastosowanej do **skwantowanej** domeny częstotliwości, nie
dowód przeciwko hipotezie rezonansu między PT a TR — sam fakt, że 96.5%
okien ma identyczną częstotliwość szczytową, jest raczej silną (choć
nieformalną, bo mechanizm testu ją zepsuł) przesłanką ZA wyrównaniem
częstotliwości między tymi dwiema lokalizacjami.

## Dlaczego to jest uczciwie INCONCLUSIVE, nie SUPPORTED ani NOT SUPPORTED

Zgodnie z §6 prerejestracji: klasyfikacja INCONCLUSIVE następuje, gdy
kontrola pozytywna nie przechodzi bramki (`controls_passed=false`) —
werdykt główny (p, rate) jest wtedy niediagnostyczny, bo nie wiadomo, czy
mechanizm testu w ogóle był zdolny wykryć rezonans. Tu dokładnie to się
stało: nie jest to porażka hipotezy fizycznej, jest to porażka
konkretnej kalibracji `eps` w tym konkretnym oknie czasowo-częstotliwościowym.

## Zasada anty-tuningu — brak samowolnej poprawki

Zgodnie z §7 prerejestracji v0.1, ten wynik (INCONCLUSIVE) NIE jest
poprawiany w miejscu. Żadna z zamrożonych decyzji (para lokalizacji,
reguła wyboru okna, `window_sec=600s`, `target_real_rate`, `seed`) nie
jest zmieniana teraz. Naprawa zdegenerowanej kalibracji `eps_f` (np.
krótsze `window_sec` dające drobniejszą siatkę FFT, zero-padding FFT dla
finiejszej interpolacji szczytu, albo nieostra nierówność `≤` zamiast
`<`) wymaga nowej, osobno uzasadnionej prerejestracji v0.2 — dokładnie
ten sam wzorzec co poprawka propagacji fali w K-MARS-DAS v0.1→v0.2.

## Uczciwe ograniczenia

1. Kalibracja `eps_f` metodą percentylową zakłada ciągły rozkład różnic
   — załamuje się przy silnie skwantowanej/zdyskretyzowanej domenie
   częstotliwości (tu: tylko ~10-11 możliwych wartości szczytu FFT na
   398 okien). Nie sprawdzone wcześniej dla tej klasy sygnału.
2. `is_resonant()` z ostrą nierównością `<` jest wrażliwy na `eps=0` w
   sposób, który unieważnia nawet trywialny test tożsamościowy
   (kontrola pozytywna) — to ogólna właściwość implementacji, nie
   specyficzna dla tego zbioru danych, warta odnotowania jako
   potencjalne ograniczenie API `is_resonant()` przy niskiej
   rozdzielczości częstotliwościowej.
3. Sam fakt 96.5% identycznych częstotliwości szczytowych między PT i
   TR jest sugestywny, ale nieformalny — nie przeszedł przez bramkę
   kontrolną, więc nie może być zgłoszony jako potwierdzony wynik.
4. Jeden ciągły odcinek 66 godzin, jedna para lokalizacji — nawet
   poprawiona kalibracja w v0.2 byłaby wciąż pojedynczym testem,
   wymagającym repliki.

## Co dalej

Nowa prerejestracja v0.2 mogłaby zawęzić `window_sec` (np. 60-120s,
wciąż w granicach literatury LFO) dla drobniejszej siatki FFT, ALBO
zmienić kryterium `is_resonant` na nieostrą nierówność — obie zmiany
wymagają jawnego uzasadnienia przed ponownym uruchomieniem, zgodnie z
dyscypliną tego ekosystemu.

## Status: INCONCLUSIVE (v0.1) — kontrola pozytywna nie przeszła z powodu zdegenerowanej kalibracji eps_f, nie z powodu braku sygnału

Pierwszy test K na danych sieci elektroenergetycznej. Nie potwierdza ani
nie zaprzecza hipotezie rezonansu modalnego między PT a TR — ujawnia
za to konkretną, nazwaną słabość metodologii kalibracji `eps_f` przy
zastosowaniu do silnie skwantowanej domeny częstotliwości, analogicznie
uczciwie zgłoszoną jak niejednoznaczny wynik Krakow_Centrum (gałąź M/S,
`TIMDR-Math-Formalism/docs/REAL_DATA_VALIDATION.md`) — tam też wysokie
"brak efektu" okazało się artefaktem braku mocy testu, nie potwierdzonym
brakiem zjawiska.
