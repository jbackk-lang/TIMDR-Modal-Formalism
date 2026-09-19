# Gałąź K na częstotliwości sieci elektroenergetycznej — prerejestracja v0.2 (poprawka kalibracji)

**Status: PREREGISTERED, NOT YET RUN.** Poprawka jednej, konkretnej
wady zdiagnozowanej w v0.1 (`RESULT_K_GRID_FREQ_v0.1.md`) — zamrożona
PRZED ponownym uruchomieniem ekstrakcji, dokładnie jak poprawka
propagacji fali między K-MARS-DAS v0.1→v0.2.

## 0. Diagnoza wady v0.1 — powtórzona dla jasności

Przy `window_sec=600 s`, `fs=1 Hz`, siatka częstotliwości FFT ma
rozdzielczość `df=1/600≈0.001667 Hz`. Sygnał `f50` (odchylenie od
50 Hz) w oknie ma energię skupioną blisko DC, więc szczyt widma niemal
zawsze ląduje w jednym z zaledwie ~10-11 dyskretnych binów. Skutek:
384/398 okien (96.5%) miało DOKŁADNIE równe `f_PT` i `f_TR` — rozkład
`|Δf|` ma masę punktową w zerze, więc percentyl 10% (`target_real_rate`)
tego rozkładu wynosi dokładnie `0.0`. Przy ostrej nierówności w
`is_resonant()` (`|Δf|<eps_f`) to unieważnia NAWET kontrolę pozytywną
(`Δf=0` nie spełnia `0<0`) — stąd `controls_passed=false` i werdykt
INCONCLUSIVE, nie odzwierciedlający realnej hipotezy.

## 1. Wybór poprawki — uzasadnienie GENERYCZNE, podjęte PRZED ponownym dotknięciem wyniku

Rozważono dwie możliwe poprawki:

- (a) Zmiana `window_sec` — odrzucona: SKRÓCENIE okna pogarsza
  rozdzielczość FFT (`df` rośnie), więc pogłębia problem dyskretnych
  wiązań, zamiast go rozwiązać. WYDŁUŻENIE okna poprawiłoby
  rozdzielczość, ale zmieniłoby jednocześnie inny zamrożony parametr
  (konwencję literaturową 600 s dla oscylacji międzyobszarowych) bez
  niezależnego uzasadnienia domenowego dla nowej wartości — ryzyko
  dopasowania parametru do wyniku.
- (b) Zmiana `is_resonant()` z ostrej `<` na nieostrą `<=` — odrzucona:
  `is_resonant()` jest współdzieloną funkcją, operacjonalizującą
  Aksjomat 5 dla WSZYSTKICH dotychczasowych testów K (Ridgecrest, MARS
  DAS v0.1/v0.2). Zmiana jej semantyki retroaktywnie zmieniłaby
  interpretację testów już zamkniętych i opisanych — zbyt szeroki
  skutek uboczny dla poprawki jednego testu.

**Wybrana poprawka (c): zero-padding FFT przed ekstrakcją szczytu
częstotliwości**, zastosowany LOKALNIE tylko w skrypcie tego testu
(`_fft_peak_f_phi_A()` w `real_data_validation.py` pozostaje
NIETKNIĘTA — wywoływana z już wypełnionym zerami oknem, nie
zmodyfikowana). Zero-padding to standardowa technika DSP: dopełnienie
okna zerami przed FFT nie dodaje informacji spektralnej, ale
interpoluje siatkę częstotliwości gęściej, usuwając artefakt
"sklejania się" bliskich szczytów w te same dyskretne biny. Typowe
współczynniki dopełnienia w literaturze DSP: 4×-16× dla precyzyjnej
interpolacji szczytu. **Zamrożony współczynnik: 16×** (okrągła,
hojna wartość z górnego końca typowego zakresu, wybrana PRZED
uruchomieniem — nie dopasowywana do wyniku).

```text
n_per_window (surowe) = 600
n_padded = 600 * 16 = 9600
df_nowe = 1/9600 ≈ 0.0001042 Hz  (16x drobniejsze niż 0.001667 Hz)
```

Implementacja: `s_window_padded = np.pad(s_window, (0, n_padded -
len(s_window)))`, następnie `_fft_peak_f_phi_A(s_window_padded, fs)` —
sama funkcja niezmieniona, tylko jej wejście dopełnione.

## 2. Wszystko inne — w pełni odziedziczone z v0.1, zero zmian

```text
plik: SYNC01.csv, sha256 identyczny jak w v0.1
kanał A: f50_PT (Lizbona), kanał B: f50_TR (Stambuł)
reguła wyboru okna: ten sam najdłuższy ciągły odcinek
  (start 2019-08-01 23:30:46, długość 238 902 s)
window_sec: 600 (niezmienione)
target_real_rate (calibrate_epsilons): 0.1
n_permutations: 2000
seed: 0
alpha: 0.05
MIN_WINDOWS_FOR_CALIBRATION: 20
is_resonant(): ostra nierówność, niezmieniona
```

## 3. Przewidywanie — zapisane PRZED uruchomieniem

Jeśli diagnoza z §0 jest poprawna, zero-padding powinien: (i)
sprawić, że `eps_f` skalibrowane po poprawce będzie > 0 (bo rozkład
`|Δf|` przestanie mieć masę punktową dokładnie w zerze — ciągła
interpolacja rzadko daje idealnie identyczne wartości), (ii)
przywrócić przechodzenie kontroli pozytywnej (`controls_passed=true`),
(iii) odsłonić prawdziwy werdykt testu głównego (SUPPORTED lub NOT
SUPPORTED), zamiast wcześniejszego niediagnostycznego INCONCLUSIVE.
To NIE jest gwarancja SUPPORTED — poprawka naprawia MECHANIZM testu,
nie zakłada z góry jego wyniku.

## 4. Zasada anty-tuningu

Po zobaczeniu wyniku nie wolno zmieniać: współczynnika zero-padding
(16×), wyboru pary lokalizacji, reguły wyboru okna, `window_sec`,
`target_real_rate`, `seed`. Kolejna zmiana wymaga nowej
prerejestracji v0.3 z jawnym uzasadnieniem.

## 5. Status końcowy

**K-GRID-FREQ v0.2 — preregistered, not run.** Sekcje 0-4 nie mogą się
zmienić po zobaczeniu wyniku.
