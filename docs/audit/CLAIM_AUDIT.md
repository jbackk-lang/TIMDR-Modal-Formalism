# Audyt twierdzeń: README → gałąź K: MARS DAS i częstotliwość sieci (TIMDR-Modal-Formalism)

Silnik: claim_audit v0.2 (TIMDR-AI-Core).

Drugi przebieg, po poprawkach README (`CLAIM_AUDIT_ADDENDUM_1.md`). Pierwszy przebieg z analizą: `CLAIM_AUDIT_v1.md`. Karty zmieniono po pierwszym przebiegu — ten raport sprawdza zgodność poprawionego README z plikami, nie jest niezależnym testem.

Wygenerowano: 2026-09-26 12:05 UTC; reguły: `docs/audit/CLAIM_AUDIT_PREREG.md` (sha256 96274f14678b), karty: `claims_k.py` (sha256 c1f8d7870b2a), README sha256 204cd3726284.

Werdykty kart: POTWIERDZONE 28, UDOKUMENTOWANE 2.

## Twierdzenia

| # | Twierdzenie (cytat z README) | Werdykt | Przeliczenie | Uwagi |
| --- | --- | --- | --- | --- |
| D1 | roczny eksperyment DAS na 52-km podmorskim kablu telekomunikacyjnym w Monterey Bay | UDOKUMENTOWANE | PREREG_K_MARS_DAS_v0.1.md: 52-km kabel | poziom DOKUMENT |
| D2 | Dwa kanały (skrajne końce ~14.8 km zarejestrowanego odcinka, reguła geometryczna zamrożona przed pobraniem) | POTWIERDZONE | kanały 0 i 2844 z 2845, 14,79 km (dx 5,2 m) | poziom JSON; pre-rejestracja w gicie przed wynikiem; moment pobrania danych nieweryfikowalny |
| D3 | kontrola pozytywna przechodzi (p≈0.0005, mechanika testu działa) | POTWIERDZONE | p kontroli = 0.00050 | poziom JSON; kontrola: kanał A z samym sobą w is_resonant() - sprawdza mechanikę/kalibrację (R8: bez flagi) |
| D4 | test główny **NOT SUPPORTED** (p=0.365, 1/60 okien rezonansowych — wynik zgodny z losowym parowaniem okien) | POTWIERDZONE | p = 0,365 > α = 0,05 | poziom JSON |
| D5 | v0.1 użył skrajnych końców kabla (~14,8 km) | POTWIERDZONE | kanały 0 i 2844 z 2845, 14,79 km (dx 5,2 m) | poziom JSON; pre-rejestracja w gicie przed wynikiem; moment pobrania danych nieweryfikowalny |
| D6 | znacznie dłużej niż `window_sec=1.0s` | POTWIERDZONE | window_sec = 1,0 s w v0.1 i v0.2 | poziom JSON; czas propagacji fali wzdłuż kabla nie jest sprawdzany |
| D7 | używa bliskich kanałów (0 i 7, 36,4 m — poniżej progu opóźnienia, powyżej długości bazy pomiarowej 20 m) | POTWIERDZONE | kanały 0 i 7, 36,4 m; baza 20 m z event_id (GL20m) | poziom JSON; próg opóźnienia z PREREG v0.2 (DOKUMENT) |
| D8 | **NOT SUPPORTED, jeszcze mocniej** (0/60 okien, p=1.0) | POTWIERDZONE | 0/60, p = 1,0 | poziom JSON |
| G1 | test na danych odchylenia częstotliwości 50 Hz (Jumar i in., KIT, arXiv:2006.01771) | UDOKUMENTOWANE | arXiv w ReadMe KIT; |f50_PT| ≤ 129 (odchylenie w mHz) | poziom DOKUMENT + SUROWE (skala wartości) |
| G2 | Lizbona (PT) vs Stambuł (TR), ~3400 km, para wybrana PRZED pobraniem pliku | POTWIERDZONE | Lizbona–Stambuł (centra miast) 3237 km | odległość po łuku między centrami miast (stacje mogą leżeć gdzie indziej); pre-rejestracja w gicie przed wynikiem, moment pobrania nieweryfikowalny |
| G3 | Okno 600 s (konwencja literatury oscylacji międzyobszarowych), 398 okien z najdłuższego ciągłego odcinka o poprawnej jakości pomiaru (66.4 h) | POTWIERDZONE | najdłuższy poprawny odcinek: wiersz 2071846, 238902 s = 66,36 h, 398 okien | poziom SUROWE (QI obu stacji = 0 w całym SYNC01.csv) |
| G4 | zdegenerowała się do `0.0` (96.5% okien miało DOKŁADNIE równą częstotliwość szczytową PT/TR, bo siatka FFT przy 600 s ma tylko ~10-11 możliwych wartości) | POTWIERDZONE | wiązania 96,5%, 11 różnych szczytów | poziom SUROWE |
| G5 | **v0.2 (poprawka kalibracji — zero-padding FFT 16×):** | POTWIERDZONE | zero_pad_factor = 16 | poziom JSON |
| G6 | odsetek dokładnych wiązań spadł tylko nieznacznie (96.5%→94.7%), `eps_f` wciąż kalibruje się do `0.0` | POTWIERDZONE | 96,5% → 94,7% | poziom SUROWE; D1 (średnia odjęta przed dopełnieniem): 85,9% |
| G7 | PT i TR trafiają w ten sam dominujący bin FFT w 94.7% okien mimo ~50 kandydujących binów (przy niezależnych kanałach oczekiwane ~43%, bo szczyty obu kanałów skupiają się w kilku najniższych binach; ~2% zakładałoby równomierny rozkład) | POTWIERDZONE | 52 binów; z rozkładów brzegowych 43,1%, jednostajnie 1,9% | R12, poziom SUROWE |
| G21 | po odjęciu średniej przed dopełnieniem odsetek wiązań spada z 94.7% do 85.9% | POTWIERDZONE | 94,7% → 85,9% | diagnostyka D1 (pre-rejestrowana); skrypt v0.2 dopełnia surowe okno |
| G8 | PIERWSZY SUPPORTED w tym repo | POTWIERDZONE | pierwszy SUPPORTED wg kolejności commitów: RESULT_K_GRID_FREQ_v0.3.json |  |
| G9 | (398 okien po 600 s). Wynik: `mean(r_w)=0.90` (mediana 0.91), z=78 względem null permutacyjnego, p=0.0005 | POTWIERDZONE | mean 0,901, mediana 0,906, z 78,23 (ziarno 12345: 80,5), p 0,0005 | poziom SUROWE; JSON z = 78,23 |
| G10 | kontrola pozytywna przeszła (to PT sparowany sam ze sobą, r = 1 z definicji — sprawdza mechanikę, nie czułość testu) | POTWIERDZONE | kontrola = PT z samym sobą, r = 1 w v0.3/v0.4/v0.5 | ograniczenie kontroli opisane w README |
| G11 | (305 okien, 2019-08-11, 10 dni po oknie v0.3) | POTWIERDZONE | 305 okien od 2019-08-11 17:16:03, 9,7 dni po starcie v0,3, bez nakładania | poziom SUROWE |
| G12 | `mean(r_w)=0.92` (mediana 0.92), z=63, p=0.0005 | POTWIERDZONE | mean 0,916, mediana 0,919, z 62,98, p 0,0005 | poziom SUROWE |
| G13 | spójne z v0.3 (mediany i IQR obu okien praktycznie się pokrywają) | POTWIERDZONE | IQR 0,882–0,925 i 0,895–0,938, nakładanie 71%, różnica median 0,013 |  |
| G14 | oba okna pochodzą z tego samego 41-dniowego pliku i miesiąca (sierpień 2019) | POTWIERDZONE | SYNC01,csv: 2019-07-09 00:00:00 – 2019-08-18 23:59:59 (41,0 dni); oba okna w sierpniu 2019 | poziom SUROWE |
| G15 | **v0.5 (replika na niezależnym pliku źródłowym) — druga replikacja potwierdzona (trzeci wynik SUPPORTED):** | POTWIERDZONE | replikacje: 2, wyniki SUPPORTED: 3 | R11 |
| G16 | plikach per-stacja 10 Hz (`PT_LI01_100ms.zip`/`TUR-IS01_100ms.zip`, KIT Power Grid Frequency Database, udostępnione osobno 2023-04-21) | POTWIERDZONE | krok 0,1 s, hashe zipów zgodne z JSON | poziom SUROWE; data publikacji 2023-04-21 z PREREG v0.5 (DOKUMENT) |
| G17 | inny plik i 10× wyższa rozdzielczość niż `SYNC01.csv`, okno przesunięte o ~3 tygodnie (2019-07-11/12 vs sierpień) | POTWIERDZONE | rozdzielczość ×10; 3,0 tyg, przed v0,3; 2019-07-11 22:07:59,100000 – 2019-07-12 05:37:50,900000 | poziom SUROWE |
| G18 | `mean(r_w)=0.88` (mediana 0.88, IQR 0.86-0.93), z=18.2 | POTWIERDZONE | mean 0,878, mediana 0,880, IQR 0,857–0,927, z 18,20 | poziom SUROWE |
| G19 | (niżej niż v0.3/v0.4 głównie przez mniej okien: 44 vs 398/305), p=0.0005 | POTWIERDZONE | liczba okien wyjaśnia 76% (vs v0.3) i 78% (vs v0.4) spadku ln z | R9 |
| G20 | to wciąż ta sama kampania pomiarowa 2019 i ta sama para stacji | POTWIERDZONE | dane v0.5 z 2019, PREREG v0.5: ta sama kampania |  |
| G22 | Wszystkie liczby v0.3–v0.5 odtwarzają się z surowych danych niezależną implementacją | POTWIERDZONE | maks. różnica względem JSON: 1.8e-16 | poziom SUROWE |

## Reguły całego fragmentu

| Reguła | Wynik | Szczegóły |
| --- | --- | --- |
| R4 świeżość | POTWIERDZONE | 4 plikow zgodnych z zamrozonymi hashami |
| R5 kompletność | POTWIERDZONE | RESULT_K_GRID_FREQ_v0.1: werdykt negatywny - README to podaje |
| R5 kompletność | POTWIERDZONE | RESULT_K_GRID_FREQ_v0.2: werdykt negatywny - README to podaje |
| R5 kompletność | POTWIERDZONE | RESULT_K_MARS_DAS_v0.1: werdykt negatywny - README to podaje |
| R5 kompletność | POTWIERDZONE | RESULT_K_MARS_DAS_v0.2: werdykt negatywny - README to podaje |
| R6 kotwica | POTWIERDZONE | docs/PREREG_K_MARS_DAS_v0.1.md (3c1062e) przed docs/RESULT_K_MARS_DAS_v0.1.json (1827ba9) |
| R6 kotwica | POTWIERDZONE | docs/PREREG_K_MARS_DAS_v0.2.md (03bd44a) przed docs/RESULT_K_MARS_DAS_v0.2.json (bfd4631) |
| R6 kotwica | POTWIERDZONE | docs/PREREG_K_GRID_FREQ_v0.1.md (ecc2d02) przed docs/RESULT_K_GRID_FREQ_v0.1.json (462d013) |
| R6 kotwica | POTWIERDZONE | docs/PREREG_K_GRID_FREQ_v0.2.md (c69bf63) przed docs/RESULT_K_GRID_FREQ_v0.2.json (a621359) |
| R6 kotwica | POTWIERDZONE | docs/PREREG_K_GRID_FREQ_v0.3.md (3b082c6) przed docs/RESULT_K_GRID_FREQ_v0.3.json (8dbb8d6) |
| R6 kotwica | UJAWNIONE | docs/PREREG_K_GRID_FREQ_v0.4.md i docs/RESULT_K_GRID_FREQ_v0.4.json w tym samym commicie (f6375dc / f6375dc); README opisuje to ograniczenie |
| R6 kotwica | UJAWNIONE | docs/PREREG_K_GRID_FREQ_v0.5.md i docs/RESULT_K_GRID_FREQ_v0.5.json w tym samym commicie (9ef311d / 9ef311d); README opisuje to ograniczenie |
