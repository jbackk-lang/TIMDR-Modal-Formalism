# Wynik K-GRID-FREQ v0.2 (2026-09-19) — INCONCLUSIVE (przewidywanie z §3 sfałszowane)

Zgodnie z `PREREG_K_GRID_FREQ_v0.2.md`, zamrożonym PRZED ponownym
uruchomieniem. Poprawka: zero-padding FFT 16× (9600 próbek zamiast
600) przed ekstrakcją szczytu, żeby usunąć artefakt zbyt gruboziarnistej
siatki częstotliwości zdiagnozowany w v0.1.

## Wynik surowy — v0.1 vs v0.2

| | v0.1 (bez zero-padding) | v0.2 (zero-padding 16×) |
|---|---|---|
| rozdzielczość siatki FFT (`df`) | 0.001667 Hz | 0.000104 Hz |
| liczba unikalnych `f_PT` w 398 oknach | 11 | 52 |
| liczba unikalnych `f_TR` w 398 oknach | 10 | 46 |
| okna z DOKŁADNIE równym `f_PT`=`f_TR` | 384/398 = 96.5% | 377/398 = 94.7% |
| eps_f (kalibrowane) | 0.0 Hz | **0.0 Hz** |
| kontrola pozytywna | rate=0.0, p=1.0 ✗ | rate=0.0, p=1.0 ✗ |
| `controls_passed` | false | **false** |
| Werdykt | INCONCLUSIVE | **INCONCLUSIVE** |

## Przewidywanie z prerejestracji §3 — SFAŁSZOWANE

Prereg v0.2 jawnie przewidział: zero-padding powinien sprawić, że
rozkład `|Δf|` przestanie mieć masę punktową w zerze, bo interpolacja
FFT "rzadko da idealnie identyczne wartości". **To przewidywanie
okazało się błędne** — 16× drobniejsza siatka (52/46 unikalnych wartości
zamiast 11/10) zmniejszyła odsetek dokładnych wiązań tylko nieznacznie
(96.5%→94.7%), nie usuwając degeneracji kalibracji. Zgodnie z
dyscypliną tego ekosystemu, sfałszowane przewidywanie jest zgłaszane
wprost, nie przemilczane ani nie "ratowane" kolejną doraźną poprawką
w tym samym biegu.

## Głębsza diagnoza — dlaczego zero-padding nie wystarczyło

Dodatkowa (deterministyczna, nie dotykająca testu głównego) inspekcja
pokazuje, że hipoteza "szczyt zawsze ląduje w najniższym dostępnym
binie" (prosta degeneracja kwantyzacji) jest TYLKO częściowo
prawdziwa: ok. 65% okien ma szczyt w najniższym binie, ale widmo
magnitud NIE jest monotonicznie malejące od DC (rośnie przez
pierwsze ~10 binów w sprawdzonym przykładzie) — więc szczyt często
ląduje w jednym z kilkudziesięciu "typowych" binów, nie tylko w
pierwszym. Mimo to PT i TR trafiają w TEN SAM bin w 94.7% okien — przy
~50 kandydujących binach losowe trafienie dałoby rząd wielkości ~2%,
nie 94.7%. Oznacza to, że dominująca niskoczęstotliwościowa treść
widmowa PT i TR jest silnie skorelowana strukturalnie (podobny kształt
widma w większości okien) — ale metoda kalibracji przez percentyl
różnic zakłada rozkład BEZ masy punktowej, więc łamie się niezależnie
od rozdzielczości siatki, dopóki odsetek dokładnych wiązań przekracza
`target_real_rate=0.1`.

**Ważne rozróżnienie**: silna zgodność DOMINUJĄCEGO BINU między PT i TR
w 94.7% okien MOŻE być samym w sobie sugestywnym sygnałem (spójne z
hipotezą wyrównania częstotliwości w obszarze synchronicznym) — ale nie
może zostać zgłoszona jako potwierdzony wynik testu K, bo test
zaprojektowany był do wykrywania ciągłej bliskości `|Δf|<eps_f`, nie
dyskretnej identyczności bin-do-bin, i kontrola pozytywna (test
tożsamościowy) wciąż nie przechodzi przez tę samą wadę konstrukcyjną.

## Dlaczego to NIE jest kolejna doraźna poprawka w tym samym biegu

Prawdziwa naprawa wymagałaby zmiany SAMEJ STATYSTYKI testu (np. test
permutacyjny na częstości DOKŁADNYCH wiązań binów zamiast na
`is_resonant()` z ciągłym `eps`, albo zupełnie innej metody ekstrakcji
nieopartej na dyskretnym szczycie FFT — np. korelacja krzyżowa
odtrendowanego sygnału), nie tylko kolejnego parametru wewnątrz tej
samej metody. Zgodnie z zasadą anty-tuningu z prerejestracji v0.1/v0.2,
zmiana samej statystyki testu wymaga nowej, osobno uzasadnionej
prerejestracji v0.3 — nie jest wykonywana w tym biegu.

## Uczciwe ograniczenia

1. Dwie kolejne próby (v0.1 surowa siatka, v0.2 zero-padding 16×) obie
   dają INCONCLUSIVE z tego samego powodu strukturalnego — degeneracja
   nie jest prostym artefaktem rozdzielczości FFT, tylko odzwierciedla
   silną zgodność dominujących binów PT/TR w większości okien.
2. Ta zgodność binów jest sugestywna, ale NIEFORMALNA — nie przeszła
   przez zaprojektowaną bramkę kontrolną, więc nie może być zgłoszona
   jako potwierdzenie Aksjomatu 5.
3. Metoda ekstrakcji `(f,φ,A)` przez dominujący szczyt FFT (zaprojektowana
   i sprawdzona dla wąskopasmowych sygnałów: fale sejsmiczne, DAS) może
   być strukturalnie niedopasowana do szerokopasmowego, czerwonego widma
   odchylenia częstotliwości sieci — to jest inny rodzaj sygnału niż
   dotychczasowe dwa testy K.
4. `target_real_rate=0.1` zakłada rozkład różnic bez masy punktowej —
   niezweryfikowane wcześniej dla domen z silnie dyskretnym/kwantowanym
   widmem.

## Co dalej

Kolejny krok wymaga PRZEPROJEKTOWANIA statystyki testu (nie tylko
parametru), np.: (a) test permutacyjny bezpośrednio na częstości
dokładnej zgodności dominującego binu FFT między PT i TR, z osobną
kalibracją progu, albo (b) zamiana ekstrakcji przez szczyt FFT na
korelację krzyżową odtrendowanych serii czasowych (miara ciągła, nie
zależna od dyskretnej siatki). To jest zmiana metodologii, nie
kalibracji — wymaga świadomej decyzji, nie automatycznej kontynuacji.

## Status: INCONCLUSIVE (v0.1 i v0.2, ten sam mechanizm), NIE ustalony

Zero-padding nie naprawił degeneracji kalibracji `eps_f` — przewidywanie
z prerejestracji v0.2 zostało sfałszowane i zgłoszone wprost. Test K na
częstotliwości sieci elektroenergetycznej pozostaje NIEROZSTRZYGNIĘTY,
z jasno nazwaną przyczyną wymagającą przeprojektowania metody, nie
kolejnej poprawki parametru.
