# Aneks 1 do CLAIM_AUDIT_PREREG.md (zapisany PRZED drugim uruchomieniem audytu)

Pierwszy przebieg: commit c7be2fb, raport `CLAIM_AUDIT_v1.md` z analizą post hoc. Po nim:

1. README (gałąź K) poprawione: D4 — „wynik zgodny z losowym parowaniem okien” zamiast „poniżej mediany null”; G7 —
   poziom losowy ~43% z rozkładów brzegowych zamiast ~2%; dopisana diagnostyka D1 (dopełnianie zerami bez odjęcia średniej:
   94.7% → 85.9%); G10 — opis kontroli pozytywnej (PT z samym sobą, r = 1 z definicji); G15 — „druga replikacja (trzeci wynik
   SUPPORTED)”; ujawnione wspólne commity pre-rejestracji i wyników v0.4/v0.5; wzmianka o odtworzeniu z surowych danych.
2. Karty v1.1 (`claims_k.py`, lista w nagłówku): nowe cytaty D4/G7/G10/G15, nowe karty G21 i G22, `ANCHOR_DISCLOSURE`,
   wzorzec „zawsze” pomija „niemal-zawsze” (fałszywy alarm z przebiegu 1).
3. Karty zmieniono PO zobaczeniu wyników przebiegu 1 — drugi przebieg sprawdza zgodność poprawionego README z plikami,
   nie jest niezależnym testem. `RECOMPUTE_K.json` bez zmian (nie przeliczano ponownie).
