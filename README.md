# TIMDR-Modal-Formalism

Pierwsza implementacja gałęzi K (modalnej) TIMDR jako kodu — dotąd
istniały tylko aksjomaty (`GIA-TIMDR/docs/theory/Axioms_K_TIMDR.md`),
bez żadnej realizacji numerycznej, w odróżnieniu od gałęzi M/S
(`TIMDR-Math-Formalism`) i G (`TIMDR-Geometry-Formalism`).

Modalność `(f,φ,A)` — Aksjomat 3, dosłownie. Interferencja
`I(t)=ΣAᵢsin(2πfᵢt+φᵢ)` — Aksjomat 4, dosłownie. Rezonans modalny
`|fᵢ-fⱼ|<ε_f ∧ |φᵢ-φⱼ|<ε_φ` — Aksjomat 5, dosłownie. Plus jedna nowa
funkcja, `local_time_from_global`: formalizacja postulatu
"`t_lokalne=f(τ_globalne)`" z dyskusji Chronoprocesu
`Ξ=(T,x,Γ,φ)` (patrz `GIA-TIMDR/SKILL_timdr-signal-framework.md`
— **uwaga**: ta konstrukcja Chronoprocesu na dziś istnieje tylko w
rozmowie, która doprowadziła do tego repo, jeszcze nie jest zapisana w
tamtym dokumencie).

## 🔀 Mapa synchronizacji faz `f`

Dwie modalności, "lokalna" i "globalna". `f` znajduje taki czas
lokalny, przy którym FAZA CHWILOWA (argument sinusa, `θ(t)=2πft+φ`)
oscylatora lokalnego zrównuje się z fazą chwilową oscylatora
globalnego w chwili `τ_globalne`:

```
t_lokalne = (f_globalne/f_lokalne)·τ_globalne
            + (φ_globalne-φ_lokalne)/(2π·f_lokalne)
```

**Granica zakresu, jawnie:** ta mapa jest AFINICZNA, bo Aksjomaty K3/K4
modelują każdą modalność jako oscylator o STAŁYCH parametrach, nie
sprzężony (Kuramoto-style) oscylator o dynamicznie zmieniającej się
częstotliwości. Pełniejsza, nieliniowa mapa synchronizacji wymagałaby
ROZSZERZENIA Axioms_K o dynamikę sprzężenia — to jest jawnie NIE
zrobione tutaj. To, co jest, jest poprawną, sprawdzalną formalizacją
danego postulatu, przy aksjomatach dokładnie takich, jakie są dziś.

## 🔧 Instalacja

```
pip install -r requirements.txt
```

Wymaga tylko `numpy` (Python 3.9+).

## 🚀 Szybki start

```python
from timdr_modal import Modality, local_time_from_global, is_resonant, interference

local = Modality(f=1.0, phi=0.0, A=1.0)
global_ = Modality(f=2.0, phi=0.0, A=1.0)

t_lokalne = local_time_from_global(local, global_, tau_global=1.0)
print(t_lokalne)  # 2.0 -- lokalny (wolniejszy) oscylator potrzebuje 2x
                   # wiecej czasu, zeby zamiesc te sama faze co globalny

print(is_resonant(local, global_, eps_f=0.5, eps_phi=0.1))  # False (f rozne o 1.0)

print(interference([local, global_], t=0.0))  # 0.0 (obie fazy = 0 w t=0)
```

## 🧪 Testy

```
pip install pytest
pytest tests/ -v
```

Testy używają ręcznie policzalnych przypadków (patrz komentarze w
`tests/test_phase_sync.py`), plus test własności ogólnej: dla
dowolnej pary modalności i dowolnego `τ_globalne`,
`θ_lokalne(f(τ_globalne)) == θ_globalne(τ_globalne)` — to jest
dokładnie definiująca właściwość mapy `f`, nie tylko przypadek
brzegowy.

**⚠️ Nie uruchomione w tej sesji.** Napisane bez dostępu do sandboxa
bash — liczby w komentarzach testów są ręcznie prześledzone, ale
`pytest` nie został faktycznie odpalony. Uruchom `pytest tests/ -v`
przed zaufaniem tym liczbom.

## ⚠️ Czego to NIE robi

Nie implementuje sprzężenia oscylatorów (Kuramoto-style), nie
rozszerza Axioms_K o nowe aksjomaty, nie zamyka gałęzi K jako całości
— rezonans modalny (Aksjomat 5) tu tylko sprawdzony na dwóch
modalnościach o stałych parametrach, hierarchiczna struktura warstw
`R₁⊆R₂⊆...⊆Rₙ` (Aksjomaty 8-10) nie jest tu w ogóle poruszona. To jest
pierwsza, wąska instancja galęzi K jako kodu — punkt startowy, nie
domknięcie.
