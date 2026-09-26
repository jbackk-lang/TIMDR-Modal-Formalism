# Audyt twierdzeń README — gałąź K (MARS DAS, częstotliwość sieci) — pre-rejestracja

Status: ZAMROŻONE i zacommitowane PRZED pierwszym uruchomieniem `recompute_k.py` i audytu. Silnik:
`tools/claim_audit.py` (TIMDR-AI-Core `claim_audit` v0.2, `tools/VENDOR.lock.json`), reguły ogólne R1–R7 jak w
`TIMDR-AI-Core/CLAIM_AUDIT.md`. Audytor przeczytał README, pliki RESULT_*.json/PREREG_*.md i skrypty przed napisaniem kart;
surowych danych nie przeliczał.

## Zakres
README.md od „### Drugi test” (MARS DAS) do „## ⚠️ Czego to NIE robi” (bez niego). Ridgecrest (pierwsza sekcja) poza
zakresem: brak pliku RESULT.

## Poziomy dowodu (podawane w uwagach karty)
- SUROWE: przeliczone z surowych plików (`SYNC01.csv`, `PT_LI01_100ms.zip`, `TUR-IS01_100ms.zip`) własną implementacją
  `recompute_k.py` (bez importu skryptów repozytorium, bez scipy).
- JSON: zgodność README z `docs/RESULT_*.json` (MARS DAS — brak h5py na tym komputerze; przeliczenie z `.h5` poza zakresem).
- DOKUMENT: zapis w PREREG/README źródła danych, bez przeliczenia (UDOKUMENTOWANE).

## Reguły dodatkowe
- R2' Tolerancje: liczby z README bez „ok.”/„~” — zgodność do pokazanej precyzji (np. 0.90 ↔ [0.895; 0.905));
  z „~” — ±15%. p = 0.0005 odpowiada 1/2001 (dolna granica przy 2000 permutacjach).
- R8 Kontrola trywialna: jeśli kontrola pozytywna to kanał sparowany z samym sobą przy statystyce korelacji, jej wynik
  jest r = 1 z definicji i nie może nie przejść. Twierdzenie „kontrola pozytywna czysta” dostaje werdykt DO ZŁAGODZENIA
  (prawdziwe, ale nieinformatywne o czułości). Dla `is_resonant()` (DAS, sieć v0.1/v0.2) kontrola tożsamościowa może
  nie przejść (np. przy eps_f = 0), więc sprawdza mechanikę/kalibrację — bez flagi.
- R9 „głównie przez X”: POTWIERDZONE, jeśli X wyjaśnia > 50% spadku w skali logarytmicznej. Dla z: spadek z(v0.3)→z(v0.5)
  i z(v0.4)→z(v0.5); udział okien = ln(sqrt(n_stare/n_nowe)) / ln(z_stare/z_nowe).
- R10 „poniżej mediany null”: z p i liczby okien — jeśli p < 0,5, obserwacja jest powyżej mediany rozkładu null
  (P(null ≥ obs) < 0,5), więc twierdzenie jest SPRZECZNE.
- R11 Liczenie replikacji: replikacja = wynik z polem `replicates` w RESULT JSON; „n-ta replikacja” musi się zgadzać z
  liczbą takich wyników do tej wersji włącznie.
- R12 „losowo oczekiwane”: odsetek zgodnych binów przy niezależności liczony z rozkładów brzegowych szczytów PT i TR
  (Σ p_PT(k)·p_TR(k)); twierdzenie „~X%” przechodzi, jeśli ta wartość mieści się w ±15% X (albo w ±1 pp dla X < 5%).
- D1 (diagnostyka, bez werdyktu): odsetek wiązań v0.2 przy odjęciu średniej PRZED dopełnieniem zerami (skrypt v0.2
  dopełnia surowe okno i odejmuje średnią po dopełnieniu). Raportowane opisowo.
- R6 kotwice: dla każdej z 7 par (PREREG, RESULT.json).
