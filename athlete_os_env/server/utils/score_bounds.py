"""
Final task / episode scores must lie strictly in (0, 1) for some submission validators
(endpoints 0.0 and 1.0 are rejected).
"""

from __future__ import annotations

import numpy as np

_OPEN_LO = 1e-4
_OPEN_HI = 1.0 - 1e-4


def clip_open_unit_interval(x: float) -> float:
    """Map a real-valued score into (0, 1), excluding 0.0 and 1.0."""
    if x is None:
        return float(0.5 * (_OPEN_LO + _OPEN_HI))
    t = float(x)
    if not np.isfinite(t):
        return float(0.5 * (_OPEN_LO + _OPEN_HI))
    return float(np.clip(t, _OPEN_LO, _OPEN_HI))
