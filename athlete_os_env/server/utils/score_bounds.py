"""
Final task / episode scores must lie strictly in (0, 1) for some submission validators
(endpoints 0.0 and 1.0 are rejected).

Also: hackathon stdout uses reward:.2f — values like 1e-4 round to "0.00" and 0.9999 to "1.00",
which parsers treat as out of range. Keep scores in [0.01, 0.99] so 2-decimal formatting stays valid.
"""

from __future__ import annotations

from typing import Any, Dict

import numpy as np

# Inclusive inner range; safe for f"{x:.2f}" (never 0.00 or 1.00)
_OPEN_LO = 0.01
_OPEN_HI = 0.99


def sanitize_performance_metrics(metrics: Any) -> Dict[str, float]:
    """Clip every numeric metric into the open unit interval (for observation JSON)."""
    if not metrics:
        return {}
    out: Dict[str, float] = {}
    for k, v in metrics.items():
        try:
            out[str(k)] = clip_open_unit_interval(float(v))
        except (TypeError, ValueError):
            continue
    return out


def clip_open_unit_interval(x: float) -> float:
    """Map a real-valued score into (0, 1), excluding endpoints; 2dp-safe for protocol logs."""
    if x is None:
        return float(0.5 * (_OPEN_LO + _OPEN_HI))
    t = float(x)
    if not np.isfinite(t):
        return float(0.5 * (_OPEN_LO + _OPEN_HI))
    return float(np.clip(t, _OPEN_LO, _OPEN_HI))
