"""TIMDR-Modal-Formalism — pierwsza implementacja galezi K (modalnej).

Modalnosc (f,phi,A) z Aksjomatu 3, interferencja z Aksjomatu 4, rezonans
modalny z Aksjomatu 5 (wszystkie z GIA-TIMDR/docs/theory/Axioms_K_TIMDR.md),
plus mapa synchronizacji faz `local_time_from_global` -- formalizacja
postulatu "t_lokalne=f(tau_globalne)" z dyskusji Chronoprocesu.
"""

from .phase_sync import (
    Modality,
    instantaneous_phase,
    interference,
    is_resonant,
    local_time_from_global,
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

__all__ = [
    "Modality",
    "instantaneous_phase",
    "interference",
    "is_resonant",
    "local_time_from_global",
    "CalibrationResult",
    "RealResonanceResult",
    "WindowedModality",
    "calibrate_epsilons",
    "extract_modalities",
    "load_station_csv",
    "real_data_resonance_report",
]
