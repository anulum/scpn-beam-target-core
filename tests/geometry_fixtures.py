# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — device model fixtures

"""Fixtures shared by the tier-G1 and tier-G2 tests.

**There is no anchor fixture here, and that is the honest state of this
family rather than an omission.** Reproducing a printed value is an
anchor, never a claim about that machine — but this repository has no
printed geometry to reproduce. Both works it cites for its beam physics
are paywalled and unobtainable, and the one document on file, the plasma
formulary, prints reactivities and constants and no dimensions at all.

So every length below is **declared**. A test may show that the bodies
are consistent with each other and with the declaration; none can show
that any of them reproduces a published dimension, and none claims to.
"""

from __future__ import annotations

import math
from typing import Final

from scpn_beam_target_core.configuration import DeviceConfiguration, RegistryBinding
from scpn_beam_target_core.geometry import BeamlineEnvelope, TargetAssembly
from scpn_beam_target_core.parameters import BeamLine

REGISTRY: Final = RegistryBinding(version="1.0.0", digest_sha256="0" * 64)

REFERENCE_BEAMLINE_FIELDS: Final = {
    "bore_radius_m": 0.03,
    "wall_thickness_m": 0.004,
    "length_m": 1.2,
    "interaction_gap_m": 0.15,
}
"""A synthetic beam pipe. Declared, not sourced."""

REFERENCE_TARGET_FIELDS: Final = {
    "target_radius_m": 0.05,
    "target_thickness_m": 0.002,
    "dump_radius_m": 0.08,
    "dump_length_m": 0.25,
}
"""A synthetic target and dump. Declared, not sourced. Both radii exceed
the bore so the beam cannot pass around either, which the model checks."""

REFERENCE_KINETIC_ENERGY_KEV: Final = 120.0
REFERENCE_BEAM_CURRENT_MA: Final = 50.0


def synthetic_configuration(
    identifier: str = "beam_target",
    kinetic_energy_kev: float = REFERENCE_KINETIC_ENERGY_KEV,
) -> DeviceConfiguration:
    """Build a valid synthetic configuration.

    Parameters
    ----------
    identifier
        Owned configuration identifier; the beam-line count follows from
        it, one for ``beam_target`` and two for ``colliding_beam``.
    kinetic_energy_kev
        Kinetic energy per ion.

    Returns
    -------
    DeviceConfiguration
        A configuration describing no real machine.
    """
    return DeviceConfiguration(
        identifier=identifier,
        beam=BeamLine(
            kinetic_energy_kev=kinetic_energy_kev,
            beam_current_ma=REFERENCE_BEAM_CURRENT_MA,
        ),
        beam_line_count=1 if identifier == "beam_target" else 2,
        registry=REGISTRY,
    )


def reference_beamline(**overrides: float) -> BeamlineEnvelope:
    """Build the synthetic beam-line envelope with optional overrides.

    Parameters
    ----------
    **overrides
        Field values replacing those of
        :data:`REFERENCE_BEAMLINE_FIELDS`.

    Returns
    -------
    BeamlineEnvelope
        The validated envelope.
    """
    return BeamlineEnvelope(**{**REFERENCE_BEAMLINE_FIELDS, **overrides})


def reference_target(**overrides: float) -> TargetAssembly:
    """Build the synthetic target assembly with optional overrides.

    Parameters
    ----------
    **overrides
        Field values replacing those of :data:`REFERENCE_TARGET_FIELDS`.

    Returns
    -------
    TargetAssembly
        The validated assembly.
    """
    return TargetAssembly(**{**REFERENCE_TARGET_FIELDS, **overrides})


def inscribed_polygon_ratio(segments: int) -> float:
    """Return the area of the inscribed regular polygon over the circle's.

    ``(n / 2 pi) sin(2 pi / n)``. Every body of these tiers is tessellated
    by inscribing a regular polygon in each circular section, so a mesh
    volume is smaller than the analytic volume by exactly this factor.

    Parameters
    ----------
    segments
        Circumferential segment count.

    Returns
    -------
    float
        The ratio, which approaches one from below as the count rises.
    """
    return segments * math.sin(2.0 * math.pi / segments) / (2.0 * math.pi)
