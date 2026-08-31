# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — beam-target parameter model

"""Validated parameter objects of a beam-target configuration.

The derived quantities implement standard two-body kinematics and
nothing more: the nonrelativistic equal-mass centre-of-mass kinetic
energy for a stationary target (``E/2``) and for symmetric colliding
beams (``2E``). Both are rough consistency instruments with documented
applicability bounds (light-ion cross-section window; H.-S. Bosch,
G. M. Hale, Nucl. Fusion 32 (1992) 611); no claim about any real
machine follows from them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from scpn_beam_target_core.errors import DeviceConfigurationError


def require_finite(name: str, value: float) -> float:
    """Return ``value`` when finite, otherwise fail closed.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is NaN or infinite; non-finite input is rejected,
        never clamped.
    """
    if not math.isfinite(value):
        raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    return value


def require_positive(name: str, value: float) -> float:
    """Return ``value`` when finite and strictly positive.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is non-finite or not strictly positive.
    """
    require_finite(name, value)
    if value <= 0.0:
        raise DeviceConfigurationError(
            f"{name}: must be strictly positive, got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True)
class BeamLine:
    """Beam-line parameters of a beam-target configuration.

    Parameters
    ----------
    kinetic_energy_kev
        Per-particle kinetic energy in kiloelectronvolts; strictly
        positive.
    beam_current_ma
        Beam current in milliamperes; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If any parameter is non-finite or not strictly positive.
    """

    kinetic_energy_kev: float
    beam_current_ma: float

    def __post_init__(self) -> None:
        """Validate the beam-line invariants.

        Raises
        ------
        DeviceConfigurationError
            If any parameter is non-finite or not strictly positive.
        """
        require_positive("kinetic_energy_kev", self.kinetic_energy_kev)
        require_positive("beam_current_ma", self.beam_current_ma)
