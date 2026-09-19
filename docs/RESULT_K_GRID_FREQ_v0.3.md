# Wynik K-GRID-FREQ v0.3 (2026-09-19) — **SUPPORTED** (pierwszy potwierdzony realny wynik gałęzi K)

Zgodnie z `PREREG_K_GRID_FREQ_v0.3.md`, zamrożonym PRZED uruchomieniem.
Nowa statystyka (korelacja krzyżowa zero-lag odtrendowanych okien)
zastępuje ekstrakcję `(f,φ,A)`+`is_resonant()` z v0.1/v0.2, które dwa
razy dały INCONCLUSIVE z powodu degeneracji kalibracji `eps_f`.

## Wynik surowy

```text
n_windows: 398
statystyka: mean(r_w), Pearson r zero-lag, okna odtrendowane liniowo

real_stat (mean korelacji PT↔TR): 0.9009
mediana r_w: 0.9057   (25.-75. percentyl: 0.882 - 0.925)
null (permutacyjny): mean=0.0292, std=0.0111
z-score realnego vs null: 78.2
p-value: 0.0005 (0/2000 permutacji ≥ realny wynik)

kontrola pozytywna (PT vs PT): stat=1.0, p=0.0005 ✓
controls_passed: true

Werdykt: SUPPORTED
```

## Zgodność z przewidywaniem z prerejestracji

Prereg §5 przewidział dwie możliwości: silna dodatnia korelacja
(SUPPORTED) jeśli 94.7%-owa zgodność binu FFT z v0.2 odzwierciedlała
realną zgodność treści niskoczęstotliwościowej, albo korelacja bliska
zeru (NOT SUPPORTED) jeśli to był artefakt samej ekstrakcji FFT. Wynik:
**pierwsza możliwość się potwierdziła**, i to bardzo mocno — mediana
korelacji między oknami 0.91, z=78 względem rozkładu null.

## Uczciwa interpretacja — dlaczego to NIE jest "odkrycie ukrytego rezonansu"

To jest ważne rozróżnienie, wymagane przez dyscyplinę tego ekosystemu:
domena tego testu (częstotliwość sieci AC w jednym obszarze
synchronicznym) została wybrana WŁAŚNIE dlatego, że fizyka energetyki
a priori GWARANTUJE wyrównanie częstotliwości — to nie jest hipoteza
otwarta jak w Ridgecrest czy MARS DAS, tylko dobrze udokumentowana
własność inżynierska sieci elektroenergetycznych (częstotliwość jest
zmienną systemową całego obszaru synchronicznego, aktywnie regulowaną;
koherencja częstotliwości między odległymi punktami tego samego obszaru
synchronicznego jest znanym zjawiskiem w literaturze energetyki,
wykorzystywanym np. w systemach pomiaru szerokoobszarowego typu FNET).

**Właściwe odczytanie tego wyniku**: to PIERWSZY test, w którym
formalizm gałęzi K (Aksjomat 5, operacjonalizowany tu jako korelacja
krzyżowa zamiast dyskretnego `is_resonant()`) poprawnie wykrył
wyrównanie tam, gdzie wyrównanie było fizycznie ZAGWARANTOWANE z góry —
czyli walidacja MECHANIZMU/PIPELINE'U testu (analogicznie do kontroli
pozytywnej w poprzednich testach, tylko na poziomie całej domeny), NIE
odkrycie nowego, zaskakującego zjawiska. Dotychczasowe testy na
domenach z OTWARTĄ hipotezą (Ridgecrest — niejednoznaczny; MARS DAS —
NOT SUPPORTED) pozostają bez zmian i bez tej interpretacji.

## Ograniczenia statusu — dlaczego to NIE jest "ustalony (diagnostyka)"

Zgodnie ze słownikiem statusów mostów w `TIMDR_Branch_Specification.md`,
status "USTALONY (diagnostyka)" wymaga m.in.: kontroli SYNTETYCZNYCH
pozytywnej i negatywnej (tu jest tylko REALNA kontrola pozytywna,
PT-vs-PT — brak syntetycznej), testu przenośności na ≥3 domenach (tu:
jedna para lokalizacji, jeden odcinek czasowy), niezależnej repliki.
Ten wynik nie spełnia tych kryteriów — jest to pojedynczy, mocny,
uczciwie zgłoszony wynik SUPPORTED, nie ustalona własność gałęzi K.

## Zakres zmiany statystyki — przypomnienie z prerejestracji §0

Ta korelacja krzyżowa jest ALTERNATYWNĄ operacjonalizacją Aksjomatu 5
DLA TEGO TESTU — nie modyfikuje `is_resonant()` ani nie zmienia
interpretacji Ridgecrest/MARS DAS v0.1/v0.2, które pozostają zgłoszone
dokładnie tak, jak były.

## Uczciwe ograniczenia

1. Wynik potwierdza znane zjawisko fizyczne (koherencja częstotliwości
   w obszarze synchronicznym) — wartość novum leży w tym, że TIMDR K
   poprawnie go wykrył, nie w samym zjawisku.
2. Brak kontroli syntetycznej (wstrzyknięty efekt w danych sztucznych) —
   tylko realna kontrola pozytywna (kanał sam ze sobą).
3. Jedna para lokalizacji (PT-TR, ekstremalny dystans), jeden ciągły
   odcinek 66 h z 41-dniowego zbioru — brak testu na innych parach
   (np. DE_KA-DE_OL, znacznie bliżej) czy innych oknach czasowych.
4. Różna statystyka niż v0.1/v0.2 — liczby nieporównywalne wprost,
   tylko klasyfikacja końcowa.
5. `mean(r_w)=0.90` to duży efekt w skali intuicyjnej, ale nie
   przeliczony na formalny rozmiar efektu rank-biserial (statystyka
   ciągła oparta na średniej, nie na Mann-Whitney U) — z-score=78
   podany jako miara pomocnicza, nie zamiennik.

## Co dalej

Naturalna replika: ta sama metoda na parze DE_KA-DE_OL (dystans rzędu
dziesiątek km, ten sam obszar synchroniczny) — jeśli korelacja jest
podobnie wysoka, wzmacnia interpretację "koherencja systemowa"; jeśli
wyraźnie niższa niż PT-TR, byłoby to zaskakujące i warte zbadania.
Wymaga osobnej prerejestracji v0.4, nie wykonane tutaj.

## Status: **SUPPORTED (v0.3)** — pierwszy potwierdzony realny wynik testu K w tym repo, z jawnie ograniczoną interpretacją

Trzy kolejne wersje tego samego testu (v0.1 surowa kalibracja, v0.2
zero-padding, v0.3 nowa statystyka) ilustrują dokładnie dyscyplinę tego
ekosystemu: dwa uczciwe INCONCLUSIVE zamiast ukrywania degeneracji
metody, jawna decyzja o zmianie statystyki (nie parametru) za zgodą
użytkownika, i w końcu mocny, ale precyzyjnie zinterpretowany wynik
pozytywny — pierwszy dla całej gałęzi K na realnych danych.
