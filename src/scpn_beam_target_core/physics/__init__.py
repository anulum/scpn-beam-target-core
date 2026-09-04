# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — level-0 device physics package

"""Level-0 device physics of the beam-target family.

The published cross-section fit of the light-ion reactions, evaluated at
the energy the declared configuration actually presents to a target at
rest, together with what a declared beam current and energy amount to.
The frame is the subject: a colliding-beam machine reaches the
centre-of-mass energy of a stationary-target machine at four times its
own beam energy. Design record: ADR 0005.
"""

from __future__ import annotations

from scpn_beam_target_core.physics.beam import (
    beam_power_w,
    ion_rate_per_s,
    require_charge_number,
)
from scpn_beam_target_core.physics.cross_section import (
    DEFAULT_QUADRATURE_SAMPLES,
    DT_LAB_ENERGY_RATIO,
    DT_REDUCED_MASS_KG,
    DUANE_COEFFICIENTS,
    REACTIONS,
    maxwellian_reactivity_cm3_per_s,
    require_reaction,
    total_cross_section_barn,
)
from scpn_beam_target_core.physics.level0 import (
    EQUAL_MASS_LAB_ENERGY_RATIO,
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    BeamInputs,
    Level0Physics,
    OperatingPoint,
    level0_physics,
)

__all__ = [
    "DEFAULT_QUADRATURE_SAMPLES",
    "DT_LAB_ENERGY_RATIO",
    "DT_REDUCED_MASS_KG",
    "DUANE_COEFFICIENTS",
    "EQUAL_MASS_LAB_ENERGY_RATIO",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "REACTIONS",
    "BeamInputs",
    "Level0Physics",
    "OperatingPoint",
    "beam_power_w",
    "ion_rate_per_s",
    "level0_physics",
    "maxwellian_reactivity_cm3_per_s",
    "require_charge_number",
    "require_reaction",
    "total_cross_section_barn",
]
