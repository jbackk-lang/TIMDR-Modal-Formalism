"""Karty twierdzeń README (gałąź K: MARS DAS, częstotliwość sieci) dla tools/claim_audit.py.
Reguły: docs/audit/CLAIM_AUDIT_PREREG.md. Przeliczenia z surowych danych: docs/audit/RECOMPUTE_K.json (recompute_k.py).
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "tools"))
from claim_audit import (POTWIERDZONE, SPRZECZNE, NIEROZSTRZYGNIETE, UDOKUMENTOWANE, Claim, Result,  # noqa: E402
                         git_first_commit, within)

TITLE = "README → gałąź K: MARS DAS i częstotliwość sieci (TIMDR-Modal-Formalism)"
README = "README.md"
PREREG = "docs/audit/CLAIM_AUDIT_PREREG.md"
OUTPUT = "CLAIM_AUDIT.md"
SCOPES = [(r"^### Drugi test", r"^## ⚠️")]
DOCS = REPO / "docs"
DO_ZLAGODZENIA = "DO ZŁAGODZENIA"


def res(name: str) -> dict:
    return json.loads((DOCS / f"RESULT_K_{name}.json").read_text(encoding="utf-8"))


def rc() -> dict:
    return json.loads((HERE / "RECOMPUTE_K.json").read_text(encoding="utf-8"))


def doc(name: str) -> str:
    return (DOCS / name).read_text(encoding="utf-8")


def r2(x, d):  # zgodnosc do pokazanej precyzji
    return within(float(d), x, approx=False, decimals=len(d.split(".")[1]) if "." in d else 0)


def fmt(x, n=3):
    return f"{x:.{n}f}"


def anchor(pre: str, result: str) -> bool:
    a, b = git_first_commit(REPO, DOCS / pre), git_first_commit(REPO, DOCS / result)
    return bool(a and b and a[1] < b[1])


def days_between(t1: str, t2: str) -> float:
    return (datetime.fromisoformat(t2) - datetime.fromisoformat(t1)).total_seconds() / 86400


# ------------------------------------------------------------------ MARS DAS (poziom JSON)
def _das_geometry():
    j = res("MARS_DAS_v0.1")
    dx = float(j["h5_attrs"]["dx_m"])
    return j, dx, (j["channel_b"] - j["channel_a"]) * dx / 1000


def d_cable():
    ok = "52-kilometrowym" in doc("PREREG_K_MARS_DAS_v0.1.md")
    return Result(UDOKUMENTOWANE if ok else NIEROZSTRZYGNIETE, "PREREG_K_MARS_DAS_v0.1.md: 52-km kabel", "poziom DOKUMENT")


def d_ends():
    j, dx, km = _das_geometry()
    ends = j["channel_a"] == 0 and j["channel_b"] == j["nch"] - 1
    anc = anchor("PREREG_K_MARS_DAS_v0.1.md", "RESULT_K_MARS_DAS_v0.1.json")
    ok = ends and within(14.8, km, approx=True) and anc
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"kanały {j['channel_a']} i {j['channel_b']} z {j['nch']}, "
                  f"{km:.2f} km (dx {dx} m)".replace(".", ","),
                  "poziom JSON; pre-rejestracja w gicie przed wynikiem; moment pobrania danych nieweryfikowalny")


def d_ends_short():
    return d_ends()


def d_posctrl():
    j = res("MARS_DAS_v0.1")
    ok = r2(j["positive_control_p_value"], "0.0005") and j["controls_passed"]
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"p kontroli = {j['positive_control_p_value']:.5f}",
                  "poziom JSON; kontrola: kanał A z samym sobą w is_resonant() - sprawdza mechanikę/kalibrację (R8: bez flagi)")


def d_main():
    j = res("MARS_DAS_v0.1")
    nums = r2(j["p_value"], "0.365") and j["n_resonant_real"] == 1 and j["n_windows"] == 60 and j["verdict"] == "NOT SUPPORTED"
    above = j["p_value"] < 0.5  # R10: P(null >= obs) < 0.5 -> obserwacja powyzej mediany null
    if nums and above:
        return Result(SPRZECZNE, f"p = {j['p_value']:.3f}, 1/60 okien", "liczby i werdykt zgodne z JSON, ale p < 0,5 "
                      "oznacza, że 1/60 jest POWYŻEJ mediany null (mediana null = 0/60) - R10")
    return Result(POTWIERDZONE if nums else SPRZECZNE, f"p = {j['p_value']:.3f}", "poziom JSON")


def d_window():
    ok = res("MARS_DAS_v0.1")["window_sec"] == 1.0 == res("MARS_DAS_v0.2")["window_sec"]
    return Result(POTWIERDZONE if ok else SPRZECZNE, "window_sec = 1,0 s w v0.1 i v0.2",
                  "poziom JSON; czas propagacji fali wzdłuż kabla nie jest sprawdzany")


def d_near():
    j, j1 = res("MARS_DAS_v0.2"), res("MARS_DAS_v0.1")
    gl = "GL20m" in j1["h5_attrs"]["event_id"]
    ok = (j["channel_a"], j["channel_b"]) == (0, 7) and r2(j["channel_distance_m"], "36.4") and gl \
        and "opóźn" in doc("PREREG_K_MARS_DAS_v0.2.md")
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"kanały 0 i 7, {j['channel_distance_m']} m; baza 20 m z event_id "
                  f"(GL20m)".replace(".", ","), "poziom JSON; próg opóźnienia z PREREG v0.2 (DOKUMENT)")


def d_v02():
    j = res("MARS_DAS_v0.2")
    ok = j["n_resonant_real"] == 0 and j["n_windows"] == 60 and j["p_value"] == 1.0 and j["verdict"] == "NOT SUPPORTED"
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"0/{j['n_windows']}, p = {j['p_value']}".replace(".", ","), "poziom JSON")


# ------------------------------------------------------------------ siec (poziom SUROWE)
def g_source():
    ok = "arXiv:2006.01771" in doc("DATASOURCE_KIT_PowerGridFrequencyDB_ReadMe.txt")
    m = rc()["sync01"]["unit_hint_abs_max"]
    return Result(UDOKUMENTOWANE if ok else NIEROZSTRZYGNIETE, f"arXiv w ReadMe KIT; |f50_PT| ≤ {m:.0f} (odchylenie w mHz)",
                  "poziom DOKUMENT + SUROWE (skala wartości)")


def g_pair():
    lat1, lon1, lat2, lon2 = map(math.radians, (38.7223, -9.1393, 41.0082, 28.9784))
    km = 2 * 6371 * math.asin(math.sqrt(math.sin((lat2 - lat1) / 2) ** 2
                                        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2))
    ok = within(3400, km, approx=True) and anchor("PREREG_K_GRID_FREQ_v0.1.md", "RESULT_K_GRID_FREQ_v0.1.json")
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"Lizbona–Stambuł (centra miast) {km:.0f} km",
                  "odległość po łuku między centrami miast (stacje mogą leżeć gdzie indziej); pre-rejestracja w gicie "
                  "przed wynikiem, moment pobrania nieweryfikowalny")


def g_run():
    s, v = rc()["sync01"], rc()["v01_v03"]
    top = s["longest_valid_runs"][0]
    ok = top["start_row"] == 2071846 and top["len"] == 238902 and v["qi_all_zero"] and v["corr"]["n_windows"] == 398 \
        and r2(v["hours"], "66.4")
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"najdłuższy poprawny odcinek: wiersz {top['start_row']}, "
                  f"{top['len']} s = {v['hours']:.2f} h, {v['corr']['n_windows']} okien".replace(".", ","),
                  "poziom SUROWE (QI obu stacji = 0 w całym SYNC01.csv)")


def g_ties():
    t = rc()["v01_v03"]["v01"]
    ok = res("GRID_FREQ_v0.1")["eps_f"] == 0.0 and r2(100 * t["tie_fraction"], "96.5") \
        and 10 * 0.85 <= t["distinct_peak_bins"] <= 11 * 1.15
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"wiązania {100 * t['tie_fraction']:.1f}%, "
                  f"{t['distinct_peak_bins']} różnych szczytów".replace(".", ","), "poziom SUROWE")


def g_pad():
    ok = res("GRID_FREQ_v0.2")["zero_pad_factor"] == 16
    return Result(POTWIERDZONE if ok else SPRZECZNE, "zero_pad_factor = 16", "poziom JSON")


def g_ties_v02():
    v = rc()["v01_v03"]
    d1 = v["v02_diag_demean_before_pad"]["tie_fraction"]
    ok = r2(100 * v["v01"]["tie_fraction"], "96.5") and r2(100 * v["v02"]["tie_fraction"], "94.7") \
        and res("GRID_FREQ_v0.2")["eps_f"] == 0.0
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"{100 * v['v01']['tie_fraction']:.1f}% → "
                  f"{100 * v['v02']['tie_fraction']:.1f}%".replace(".", ","),
                  f"poziom SUROWE; D1 (średnia odjęta przed dopełnieniem): {100 * d1:.1f}%".replace(".", ","))


def g_chance():
    t = rc()["v01_v03"]["v02"]
    ch = 100 * t["chance_agreement_from_marginals"]
    bins_ok = within(50, t["distinct_peak_bins"], approx=True)
    chance_ok = abs(ch - 2) <= 1.0
    ok = r2(100 * t["tie_fraction"], "94.7") and bins_ok and chance_ok
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"{t['distinct_peak_bins']} różnych binów; oczekiwane losowo z "
                  f"rozkładów brzegowych {ch:.1f}% (jednostajnie {100 * t['chance_agreement_uniform']:.1f}%)".replace(".", ","),
                  "R12: losowa zgodność liczona z rozkładów brzegowych szczytów PT i TR")


def g_first():
    order = sorted(((git_first_commit(REPO, p) or ("", 1e18))[1], json.loads(p.read_text())["verdict"], p.name)
                   for p in DOCS.glob("RESULT_K_*.json"))
    first = next((n for _, v, n in order if v == "SUPPORTED"), None)
    ok = first == "RESULT_K_GRID_FREQ_v0.3.json"
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"pierwszy SUPPORTED wg kolejności commitów: {first}", "")


def _corr_ok(c, mean, med, z, zdec=0):
    return c and r2(c["mean_r"], mean) and r2(c["median_r"], med) and round(c["z"], zdec) == float(z) \
        and r2(c["p"], "0.0005")


def g_v03():
    c = rc()["v01_v03"]["corr"]
    j = res("GRID_FREQ_v0.3")
    ok = c["n_windows"] == 398 and _corr_ok(c, "0.90", "0.91", 78) and abs(c["z"] - j["z_score_vs_null"]) < 0.05
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"mean {fmt(c['mean_r'])}, mediana {fmt(c['median_r'])}, "
                  f"z {c['z']:.2f} (ziarno 12345: {c['z_seed12345']:.1f}), p {c['p']:.4f}".replace(".", ","),
                  f"poziom SUROWE; JSON z = {j['z_score_vs_null']:.2f}".replace(".", ","))


def g_trivial_control():
    texts = [(REPO / s).read_text(encoding="utf-8") for s in ("_grid_freq_k_run_v0_3.py", "_grid_freq_k_run_v0_4.py",
                                                              "_grid_freq_k_run_v0_5.py")]
    self_pair = all("row_corr(W_pt, norm_pt, W_pt, norm_pt" in t for t in texts)
    vals = [rc()[k]["corr"]["positive_control_mean_r"] for k in ("v01_v03", "v04", "v05")]
    if self_pair and all(abs(v - 1) < 1e-9 for v in vals):
        return Result(DO_ZLAGODZENIA, "kontrola = PT z samym sobą, r = 1 w v0.3/v0.4/v0.5",
                      "R8: prawdziwe, ale kontrola nie może nie przejść - nie sprawdza czułości (dotyczy v0.3, v0.4, v0.5)")
    return Result(POTWIERDZONE, "kontrola nietrywialna", "")


def g_v04_window():
    v3, v4 = rc()["v01_v03"], rc()["v04"]
    d = days_between(v3["start_time"], v4["start_time"])
    ok = v4["corr"]["n_windows"] == 305 and v4["start_time"].startswith("2019-08-11") and round(d) == 10 \
        and v3["end_time"] < v4["start_time"]
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"305 okien od {v4['start_time']}, {d:.1f} dni po starcie v0.3, "
                  "bez nakładania".replace(".", ","), "poziom SUROWE")


def g_v04():
    c = rc()["v04"]["corr"]
    ok = _corr_ok(c, "0.92", "0.92", 63)
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"mean {fmt(c['mean_r'])}, mediana {fmt(c['median_r'])}, "
                  f"z {c['z']:.2f}, p {c['p']:.4f}".replace(".", ","), "poziom SUROWE")


def g_overlap():
    a, b = rc()["v01_v03"]["corr"]["p25_p75"], rc()["v04"]["corr"]["p25_p75"]
    ov = max(0.0, min(a[1], b[1]) - max(a[0], b[0])) / min(a[1] - a[0], b[1] - b[0])
    dm = abs(rc()["v01_v03"]["corr"]["median_r"] - rc()["v04"]["corr"]["median_r"])
    ok = ov >= 0.5 and dm < 0.02
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"IQR {fmt(a[0])}–{fmt(a[1])} i {fmt(b[0])}–{fmt(b[1])}, "
                  f"nakładanie {100 * ov:.0f}%, różnica median {dm:.3f}".replace(".", ","), "")


def g_file41():
    s, v3, v4 = rc()["sync01"], rc()["v01_v03"], rc()["v04"]
    aug = all(x.startswith("2019-08") for x in (v3["start_time"], v3["end_time"], v4["start_time"], v4["end_time"]))
    ok = round(s["span_days"]) == 41 and aug
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"SYNC01.csv: {s['first']} – {s['last']} ({s['span_days']:.1f} dni); "
                  "oba okna w sierpniu 2019".replace(".", ","), "poziom SUROWE")


def g_replica_count():
    reps = [p.name for p in sorted(DOCS.glob("RESULT_K_GRID_FREQ_v0.*.json"))
            if "replicates" in json.loads(p.read_text()) and p.name <= "RESULT_K_GRID_FREQ_v0.5.json"]
    ok = len(reps) == 3
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"wyniki z polem replicates do v0.5: {len(reps)} ({', '.join(reps)})",
                  "" if ok else "v0.5 to druga replikacja (trzeci wynik SUPPORTED) - R11")


def g_v05_source():
    v = rc()["v05"]
    j = res("GRID_FREQ_v0.5")
    ok = round(1 / v["dt_s_median"]) == 10 and v["sha256_pt"] == j["data_file_pt_sha256"] \
        and v["sha256_tur"] == j["data_file_tur_sha256"] and "2023-04-21" in doc("PREREG_K_GRID_FREQ_v0.5.md")
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"krok {v['dt_s_median']} s, hashe zipów zgodne z JSON".replace(".", ","),
                  "poziom SUROWE; data publikacji 2023-04-21 z PREREG v0.5 (DOKUMENT)")


def g_v05_shift():
    v, s, v3 = rc()["v05"], rc()["sync01"], rc()["v01_v03"]
    ratio = s["dt_s_median"] / v["dt_s_median"]
    weeks = days_between(v["start_time"], v3["start_time"]) / 7
    ok = round(ratio) == 10 and within(3, weeks, approx=True) and v["start_time"].startswith("2019-07-11") \
        and v["end_time"].startswith("2019-07-12") and v["time_aligned"]
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"rozdzielczość ×{ratio:.0f}; {weeks:.1f} tyg. przed v0.3; "
                  f"{v['start_time']} – {v['end_time']}".replace(".", ","), "poziom SUROWE")


def g_v05():
    c = rc()["v05"]["corr"]
    ok = c["n_windows"] == 44 and _corr_ok(c, "0.88", "0.88", "18.2", 1) and r2(c["p25_p75"][0], "0.86") \
        and r2(c["p25_p75"][1], "0.93")
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"mean {fmt(c['mean_r'])}, mediana {fmt(c['median_r'])}, IQR "
                  f"{fmt(c['p25_p75'][0])}–{fmt(c['p25_p75'][1])}, z {c['z']:.2f}".replace(".", ","), "poziom SUROWE")


def g_mainly():
    z3, z4, z5 = (rc()[k]["corr"]["z"] for k in ("v01_v03", "v04", "v05"))
    n3, n4, n5 = (rc()[k]["corr"]["n_windows"] for k in ("v01_v03", "v04", "v05"))
    s3 = math.log(math.sqrt(n3 / n5)) / math.log(z3 / z5)
    s4 = math.log(math.sqrt(n4 / n5)) / math.log(z4 / z5)
    ok = s3 > 0.5 and s4 > 0.5 and (n5, n3, n4) == (44, 398, 305) and rc()["v05"]["corr"]["p"] < 0.00051
    return Result(POTWIERDZONE if ok else SPRZECZNE, f"liczba okien wyjaśnia {100 * s3:.0f}% (vs v0.3) i {100 * s4:.0f}% "
                  "(vs v0.4) spadku ln z", "R9")


def g_campaign():
    ok = rc()["v05"]["start_time"].startswith("2019") and "tej samej" in doc("PREREG_K_GRID_FREQ_v0.5.md")
    return Result(POTWIERDZONE if ok else SPRZECZNE, "dane v0.5 z 2019, PREREG v0.5: ta sama kampania", "")


CLAIMS = [
    Claim("D1", "roczny eksperyment DAS na 52-km podmorskim kablu telekomunikacyjnym w Monterey Bay", d_cable),
    Claim("D2", "Dwa kanały (skrajne końce ~14.8 km zarejestrowanego odcinka, reguła geometryczna zamrożona przed pobraniem)", d_ends),
    Claim("D3", "kontrola pozytywna przechodzi (p≈0.0005, mechanika testu działa)", d_posctrl),
    Claim("D4", "test główny **NOT SUPPORTED** (p=0.365, 1/60 okien rezonansowych — poniżej mediany null permutacyjnego)", d_main),
    Claim("D5", "v0.1 użył skrajnych końców kabla (~14,8 km)", d_ends_short),
    Claim("D6", "znacznie dłużej niż `window_sec=1.0s`", d_window),
    Claim("D7", "używa bliskich kanałów (0 i 7, 36,4 m — poniżej progu opóźnienia, powyżej długości bazy pomiarowej 20 m)", d_near),
    Claim("D8", "**NOT SUPPORTED, jeszcze mocniej** (0/60 okien, p=1.0)", d_v02),
    Claim("G1", "test na danych odchylenia częstotliwości 50 Hz (Jumar i in., KIT, arXiv:2006.01771)", g_source),
    Claim("G2", "Lizbona (PT) vs Stambuł (TR), ~3400 km, para wybrana PRZED pobraniem pliku", g_pair),
    Claim("G3", "Okno 600 s (konwencja literatury oscylacji międzyobszarowych), 398 okien z najdłuższego ciągłego odcinka "
                "o poprawnej jakości pomiaru (66.4 h)", g_run),
    Claim("G4", "zdegenerowała się do `0.0` (96.5% okien miało DOKŁADNIE równą częstotliwość szczytową PT/TR, bo siatka "
                "FFT przy 600 s ma tylko ~10-11 możliwych wartości)", g_ties),
    Claim("G5", "**v0.2 (poprawka kalibracji — zero-padding FFT 16×):**", g_pad),
    Claim("G6", "odsetek dokładnych wiązań spadł tylko nieznacznie (96.5%→94.7%), `eps_f` wciąż kalibruje się do `0.0`", g_ties_v02),
    Claim("G7", "PT i TR trafiają w ten sam dominujący bin FFT w 94.7% okien mimo ~50 kandydujących binów (losowo "
                "oczekiwane ~2%)", g_chance),
    Claim("G8", "PIERWSZY SUPPORTED w tym repo", g_first),
    Claim("G9", "(398 okien po 600 s). Wynik: `mean(r_w)=0.90` (mediana 0.91), z=78 względem null permutacyjnego, p=0.0005", g_v03),
    Claim("G10", "kontrola pozytywna czysta — **SUPPORTED**. **Kluczowe zastrzeżenie interpretacyjne**", g_trivial_control),
    Claim("G11", "(305 okien, 2019-08-11, 10 dni po oknie v0.3)", g_v04_window),
    Claim("G12", "`mean(r_w)=0.92` (mediana 0.92), z=63, p=0.0005", g_v04),
    Claim("G13", "spójne z v0.3 (mediany i IQR obu okien praktycznie się pokrywają)", g_overlap),
    Claim("G14", "oba okna pochodzą z tego samego 41-dniowego pliku i miesiąca (sierpień 2019)", g_file41),
    Claim("G15", "**v0.5 (replika na niezależnym pliku źródłowym) — trzecia replikacja potwierdzona:**", g_replica_count),
    Claim("G16", "plikach per-stacja 10 Hz (`PT_LI01_100ms.zip`/`TUR-IS01_100ms.zip`, KIT Power Grid Frequency Database, "
                 "udostępnione osobno 2023-04-21)", g_v05_source),
    Claim("G17", "inny plik i 10× wyższa rozdzielczość niż `SYNC01.csv`, okno przesunięte o ~3 tygodnie (2019-07-11/12 vs "
                 "sierpień)", g_v05_shift),
    Claim("G18", "`mean(r_w)=0.88` (mediana 0.88, IQR 0.86-0.93), z=18.2", g_v05),
    Claim("G19", "(niżej niż v0.3/v0.4 głównie przez mniej okien: 44 vs 398/305), p=0.0005", g_mainly),
    Claim("G20", "to wciąż ta sama kampania pomiarowa 2019 i ta sama para stacji", g_campaign),
]


def _frozen():
    out = {}
    for name, key in (("GRID_FREQ_v0.3", "data_file_sha256"), ("MARS_DAS_v0.1", "data_file_sha256")):
        j = res(name)
        out[f"../DATA/{j['data_file']}"] = j[key]
    j = res("GRID_FREQ_v0.5")
    out[f"../DATA/{j['data_file_pt']}"] = j["data_file_pt_sha256"]
    out[f"../DATA/{j['data_file_tur']}"] = j["data_file_tur_sha256"]
    return out


FROZEN = _frozen()
COMPLETENESS = [(f"docs/RESULT_K_{n}.json", r'"verdict": "(INCONCLUSIVE|NOT SUPPORTED)"', w, f"RESULT_K_{n}: werdykt negatywny")
                for n, w in (("GRID_FREQ_v0.1", "INCONCLUSIVE"), ("GRID_FREQ_v0.2", "sfałszowane|INCONCLUSIVE"),
                             ("MARS_DAS_v0.1", "NOT SUPPORTED"), ("MARS_DAS_v0.2", "NOT SUPPORTED"))]
ANCHORS = [(f"docs/PREREG_K_{n}.md", f"docs/RESULT_K_{n}.json") for n in
           ("MARS_DAS_v0.1", "MARS_DAS_v0.2", "GRID_FREQ_v0.1", "GRID_FREQ_v0.2", "GRID_FREQ_v0.3", "GRID_FREQ_v0.4",
            "GRID_FREQ_v0.5")]
ANCHOR_DISCLOSURE = None
FORBIDDEN = [(r"odkryci\w*|odkryw\w*", r"\bnie\b", "gałąź K na sieci wykrywa zjawisko gwarantowane fizyką - nie odkrycie"),
             (r"gałę?zi?\w* K\s+(jest\s+)?(zamknięt|potwierdzon)\w*", r"\bnie\b", "gałąź K nie jest zamknięta")]
ABSOLUTE = [(r"\btak samo\b", "podaj różnicę"), (r"\bzawsze\b|\bnigdy\b", "słowo bezwzględne"),
            (r"\bdowodzi\b|\budowodni\w*", "„dowodzi” wymaga dowodu"), (r"(?<!\d)100 ?%", "sprawdź liczność")]
