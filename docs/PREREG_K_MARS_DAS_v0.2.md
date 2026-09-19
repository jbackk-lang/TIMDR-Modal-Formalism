# Gałąź K na sygnałach światłowodowych — v0.2: poprawka doboru kanałów (opóźnienie propagacji)

**Status: PREREGISTERED, NOT YET RUN.** Zamrożone PRZED ponownym
odczytaniem pliku danych. Poprawka metodologiczna do
`PREREG_K_MARS_DAS_v0.1.md` — jedyna zmieniana rzecz to para kanałów
(Sekcja 1 niżej); wszystko inne (plik, `window_sec`, metoda ekstrakcji,
test statystyczny, `n_permutations`, `seed`, `alpha`) pozostaje BEZ ZMIAN
z v0.1.

## 0. Diagnoza błędu w v0.1 (zgłoszona przez użytkownika, PRZED tą prerejestracją)

v0.1 porównywał kanał 0 z kanałem 2844 — skrajne końce ~14,8 km
zarejestrowanego odcinka kabla MARS. MARS jest kablem JEDNOKIERUNKOWYM
(brzeg → węzeł naukowy, Kanion Monterey, bez pętli/odbicia — zweryfikowane
niezależnie: MBARI, Wikipedia). Fala sejsmiczna/akustyczna biegnąca wzdłuż
kabla dociera do kanału 2844 z opóźnieniem względem kanału 0 rzędu
`odległość / prędkość_fali`. Dla fal powierzchniowych/Scholte'a w osadzie
dna morskiego (typowe dla płytko ułożonych kabli DAS) prędkości rzędu
150-600 m/s są typowe w literaturze — przy 14,8 km i dolnej granicy
150 m/s opóźnienie wynosi **~99 s**, wielokrotność `window_sec=1.0 s` z
v0.1. v0.1 parował "okno nr w kanału A" z "oknem nr w kanału B" w TYM
SAMYM momencie zegara — dla fali biegnącej to NIE jest ten sam fragment
fali w obu miejscach. Test mógł nie wykryć rezonansu nawet gdyby
fizycznie istniał, z powodu niedopasowania czasowego, niezależnie od
tego, czy modalny rezonans w danych faktycznie występuje.

**To NIE unieważnia wyniku v0.1 jako "błędny pomiar"** — `NOT SUPPORTED`
pozostaje poprawnym zapisem tego, co dokładnie ten test (te kanały, ten
sposób parowania okien) pokazał. v0.2 to OSOBNY, nowy test z inną, lepiej
dobraną parą kanałów — nie retrospektywna poprawka v0.1.

## 1. Nowa reguła doboru kanałów — zamrożona PRZED odczytaniem sygnału

Dwa wymagania, oba policzalne bez patrzenia na sam sygnał:

1. **Odległość > długość bazy pomiarowej (gauge length)**, żeby uniknąć
   trywialnej korelacji z nakładania się fizycznego odcinka włókna, który
   dwa "sąsiednie" kanały uśredniają. `event_id` w pliku v0.1
   (`MBARI_GL20m_OCP5m_FS200Hz_...`) deklaruje `GL20m` — gauge length
   20 m. Wymóg: odległość ≥ 1.5× gauge length = **30 m**.
2. **Opóźnienie propagacji ≤ 25% `window_sec`, nawet dla PESYMISTYCZNIE
   wolnej fali** — przyjęta dolna granica prędkości `v_min=150 m/s`
   (dolny kraniec typowego zakresu fal Scholte'a w osadzie morskim z
   literatury, nie dopasowana do tego pliku). Przy `window_sec=1.0 s`
   (bez zmian z v0.1): odległość ≤ `0.25 × 1.0 × 150 = 37.5 m`.

Przedział spełniający oba warunki: **(30 m, 37.5 m]**. Wybrana wartość:
**7 kanałów** (`dx_m≈5.2` z manifestu v0.1 → `7×5.2=36.4 m`), w tym
przedziale, wybrana jako największa liczba całkowita kanałów, która się
mieści (konserwatywny wybór maksymalizujący odległość, więc minimalizujący
ryzyko trywialnego nakładania, przy zachowaniu marginesu bezpieczeństwa
opóźnienia).

```text
kanał A = 0
kanał B = 7   (0 + 7, zamrożone tu, przed odczytaniem sygnału z tych indeksów)
```

Przy `v_min=150 m/s` maksymalne oczekiwane opóźnienie: `36.4/150=0.243 s`
(24,3% okna). Przy realistycznie szybszych falach (P-fale w
skonsolidowanym osadzie/skale, rzędu 1000-3000 m/s) opóźnienie spada do
0.012-0.036 s — pomijalne.

## 2. Wszystko inne — bez zmian z v0.1

```text
plik: 20220730T233258Z.h5 (ten sam, sha256 zweryfikowany w v0.1)
window_sec: 1.0
n_permutations: 2000
seed: 0
alpha: 0.05
metoda ekstrakcji (f,φ,A): _fft_peak_f_phi_A + _local_phase_to_global,
  BEZ ZMIAN z timdr_modal/real_data_validation.py
target_real_rate (calibrate_epsilons): 0.1
kontrola pozytywna: kanał A sparowany sam ze sobą
```

## 3. Werdykt i zasada anty-tuningu

Identyczna z v0.1 §5. Po zobaczeniu wyniku nie wolno zmieniać: pary
kanałów, `window_sec`, `v_min`, progu 25%, `seed`. Jeśli i TEN wynik
będzie NOT SUPPORTED/INCONCLUSIVE, kolejna zmiana pary kanałów wymaga
nowej prerejestracji v0.3 z jawnym uzasadnieniem — nie cichej próby
kolejnych indeksów.

## 4. Status końcowy

**K-MARS-DAS v0.2 — preregistered, not run.** Sekcje 1-3 nie mogą się
zmienić po zobaczeniu wyniku.
