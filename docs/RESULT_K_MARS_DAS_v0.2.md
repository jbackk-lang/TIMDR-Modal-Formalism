# Wynik K-MARS-DAS v0.2 (2026-09-19) — NOT SUPPORTED (poprawiona para kanałów)

Zgodnie z `PREREG_K_MARS_DAS_v0.2.md`, zamrożonym PRZED ponownym
odczytaniem pliku. Poprawka v0.1: kanały bliżej siebie (0 i 7, 36,4 m —
zamiast 0 i 2844, ~14,8 km), żeby wyeliminować niedopasowanie czasowe
spowodowane opóźnieniem propagacji fali wzdłuż jednokierunkowego kabla
MARS (diagnoza w §0 prerejestracji v0.2, zgłoszona przez użytkownika).

## Wynik surowy

| | v0.1 (kanały 0, 2844 — ~14,8 km) | v0.2 (kanały 0, 7 — 36,4 m) |
|---|---|---|
| eps_f (kalibrowane) | 1.0000 Hz | 2.0000 Hz |
| eps_phi (kalibrowane) | 0.2578 rad | 0.2749 rad |
| kontrola pozytywna | rate=1.0, p=0.0005 ✓ | rate=1.0, p=0.0005 ✓ |
| `controls_passed` | true | **true** |
| test główny: rezonans realny | 1/60 = 0.0167 | **0/60 = 0.0** |
| test główny: p | 0.3653 | **1.0000** |
| Werdykt | NOT SUPPORTED | **NOT SUPPORTED** |

## Interpretacja

Poprawka metodologiczna (bliższe kanały, eliminacja niedopasowania
czasowego z powodu opóźnienia propagacji) NIE zmieniła werdyktu — wynik
jest teraz jeszcze mocniej negatywny (0/60 zamiast 1/60, p=1.0 zamiast
0.365). To ważne: gdyby v0.1 dawał NOT SUPPORTED TYLKO z powodu
niedopasowania czasowego (realny rezonans ukryty przez błąd metodologii),
poprawiona para kanałów powinna była ujawnić GO — zamiast tego wynik stał
się jeszcze słabszy. To wzmacnia (nie osłabia) wniosek, że w tym
konkretnym 60-sekundowym oknie, między tymi blisko rozstawionymi
kanałami, nie ma wykrywalnego wyrównania częstotliwości/fazy ponad
przypadek.

Kontrola pozytywna wciąż działa identycznie (p≈0.0005) — mechanika testu
jest sprawna, wynik negatywny nie jest artefaktem złamanego pipeline'u.

## Uczciwe ograniczenia (aktualizacja względem v0.1)

1. Problem niedopasowania czasowego z v0.1 — **usunięty** tym testem.
2. Wciąż: jeden plik, jedno 60-sekundowe okno, `event_time` puste (brak
   potwierdzonego zdarzenia sejsmicznego w metadanych tego pliku) — wynik
   może po prostu odzwierciedlać brak silnego, koherentnego sygnału w tym
   oknie, nie generalny brak zjawiska.
3. `v_min=150 m/s` (dolna granica prędkości fali użyta do doboru
   odległości kanałów) to konserwatywne założenie z literatury, nie
   zmierzone na tym konkretnym kablu — jeśli rzeczywista prędkość na tym
   odcinku jest NIŻSZA niż 150 m/s, nawet 36,4 m mogłoby dawać opóźnienie
   bliżej granicy 25% okna. Nie zweryfikowane niezależnie w tym teście.
4. Rozstaw 36,4 m wciąż >> gauge length (20 m), więc trywialne nakładanie
   się pomiaru nie tłumaczy wyniku zerowego (gdyby kanały nakładały się
   fizycznie, spodziewalibyśmy się WYŻSZEJ, nie zerowej, zgodności).

## Status: NOT SUPPORTED (v0.1 i v0.2, spójnie), NIE ustalony

Dwa niezależne dobory par kanałów (dalekie i bliskie), ten sam plik, ta
sama metoda — oba dają NOT SUPPORTED, drugi silniej niż pierwszy. To
zwiększa wiarygodność wyniku negatywnego dla TEGO pliku/okna, ale wciąż
nie jest testem przenośności (inny plik, inne zdarzenie, inny odcinek
kabla) — gałąź K na sygnałach światłowodowych pozostaje NIE ustalona,
teraz z dwoma spójnymi, uczciwie zgłoszonymi wynikami negatywnymi zamiast
jednego niejednoznacznego.
