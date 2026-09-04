# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — level-0 physics fixtures

"""Fixtures shared by the level-0 physics tests.

The reference fixtures are synthetic and describe nothing. The anchor
data is transcribed from the 2019 NRL Plasma Formulary, page 44, and
exists so the tests can show each printed value is recoverable from the
built relations rather than merely stored beside them.
"""

from __future__ import annotations

import math
from typing import Final

from scpn_beam_target_core.configuration import DeviceConfiguration, RegistryBinding
from scpn_beam_target_core.parameters import BeamLine
from scpn_beam_target_core.physics import BeamInputs

REGISTRY: Final = RegistryBinding(version="1.0.0", digest_sha256="0" * 64)

PRINTED_DT_REACTIVITY_CM3_PER_S: Final = (
    (1.0, 5.5e-21),
    (2.0, 2.6e-19),
    (5.0, 1.3e-17),
    (10.0, 1.1e-16),
    (20.0, 4.2e-16),
    (50.0, 8.7e-16),
    (100.0, 8.5e-16),
    (200.0, 6.3e-16),
    (500.0, 3.7e-16),
    (1000.0, 2.7e-16),
)
"""Maxwellian-averaged D-T reaction rates, page 44, temperature in keV
against rate in cubic centimetres per second. Every entry is printed to
two significant figures."""

PRINTED_MASS_RATIO_PAIRS: Final = (
    ("m_e/m_D", 2.72e-4, 3670.0),
    ("m_e/m_T", 1.82e-4, 5496.0),
)
"""Each ratio printed both as a decimal and as a reciprocal, page 44."""

PRINTED_MASS_RATIO_ROOTS: Final = (
    ("(m_e/m_D)^1/2", 2.72e-4, 1.65e-2, 60.6),
    ("(m_e/m_T)^1/2", 1.82e-4, 1.35e-2, 74.1),
)
"""Each square root printed both as a decimal and as a reciprocal."""

PRINTED_SIGNIFICANT_FIGURES: Final = 2


def round_to_significant_figures(value: float, figures: int) -> float:
    """Round a positive value to a number of significant figures.

    Parameters
    ----------
    value
        Strictly positive value to round.
    figures
        Number of significant figures to keep.

    Returns
    -------
    float
        The rounded value.
    """
    exponent = math.floor(math.log10(value))
    scale = 10.0**exponent
    return round(value / scale, figures - 1) * scale


def synthetic_configuration(
    identifier: str = "beam_target",
    kinetic_energy_kev: float = 120.0,
    beam_current_ma: float = 50.0,
) -> DeviceConfiguration:
    """Build a valid synthetic configuration.

    Parameters
    ----------
    identifier
        Owned configuration identifier; the beam-line count follows from
        it, one for ``beam_target`` and two for ``colliding_beam``.
    kinetic_energy_kev
        Kinetic energy per ion.
    beam_current_ma
        Beam current per line.

    Returns
    -------
    DeviceConfiguration
        A configuration describing no real machine.
    """
    return DeviceConfiguration(
        identifier=identifier,
        beam=BeamLine(
            kinetic_energy_kev=kinetic_energy_kev,
            beam_current_ma=beam_current_ma,
        ),
        beam_line_count=1 if identifier == "beam_target" else 2,
        registry=REGISTRY,
    )


def reference_inputs() -> BeamInputs:
    """Build the synthetic reference input set.

    Returns
    -------
    BeamInputs
        A singly charged deuterium-tritium beam.
    """
    return BeamInputs(reaction="d_t")
