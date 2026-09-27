"""TIMDR-Modal-Formalism — pierwsza implementacja galezi K (modalnej).

Modalnosc (f,phi,A) z Aksjomatu 3, interferencja z Aksjomatu 4, rezonans
modalny z Aksjomatu 5 (wszystkie z GIA-TIMDR/docs/theory/Axioms_K_TIMDR.md),
plus mapa synchronizacji faz `local_time_from_global` -- formalizacja
postulatu "t_lokalne=f(tau_globalne)" z dyskusji Chronoprocesu.

modal_anchor: samokorygujaca kotwica, przejscie K->G (faza -> ksztalt modu) i wykonalnosc
galezi K -- 1:1 z wersji walidowanych w GIA-TIMDR (KW51, LANL, Hell Bridge).
"""

from .phase_sync import (
    Modality,
    instantaneous_phase,
    interference,
    is_resonant,
    local_time_from_global,
    PhaseDispersionResult,
    modal_phase_dispersion,
    modal_phase_tempo,
)
from .real_data_validation import (
    CalibrationResult,
    RealResonanceResult,
    WindowedModality,
    calibrate_epsilons,
    extract_modalities,
    load_station_csv,
    real_data_resonance_report,
)
from .modal_anchor import (
    align_signs,
    anchor_coherence,
    anchor_frequencies,
    coherence_cycles,
    mac,
    mode_shapes,
    n_cycles,
)

__all__ = [
    "Modality",
    "instantaneous_phase",
    "interference",
    "is_resonant",
    "local_time_from_global",
    "PhaseDispersionResult",
    "modal_phase_dispersion",
    "modal_phase_tempo",
    "CalibrationResult",
    "RealResonanceResult",
    "WindowedModality",
    "calibrate_epsilons",
    "extract_modalities",
    "load_station_csv",
    "real_data_resonance_report",
    "align_signs",
    "anchor_coherence",
    "anchor_frequencies",
    "coherence_cycles",
    "mac",
    "mode_shapes",
    "n_cycles",
]
