# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — level-0 physics record

"""Level-0 physics record of one validated beam configuration.

The record's subject is the frame. A cross section fitted for a target at
rest cannot be evaluated at a colliding-beam machine's beam energy, and
the difference is not small: two beams of energy ``E`` meet at the same
centre-of-mass energy as a single beam of ``4E`` striking a stationary
target. That factor is the reason colliding-beam machines exist, and
evaluating the fit at the wrong energy would be a silent error rather
than a visible one.

The centre-of-mass energy itself is not restated here. The device
configuration already computes it, and the record calls that method, so
the two can never drift apart. Its equal-mass approximation is carried
through and reported alongside the exact ratio for D-T, which is 1.669
rather than 2 — a limitation the record states rather than hides.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_beam_target_core.configuration import DeviceConfiguration
from scpn_beam_target_core.physics.beam import (
    beam_power_w,
    ion_rate_per_s,
    require_charge_number,
)
from scpn_beam_target_core.physics.cross_section import (
    DT_LAB_ENERGY_RATIO,
    require_reaction,
    total_cross_section_barn,
)

LEVEL0_SCHEMA: Final = "scpn.beam-target-level0-physics.v1"
LEVEL0_SCHEMA_VERSION: Final = "1.0.0"
EQUAL_MASS_LAB_ENERGY_RATIO: Final = 2.0
"""Lab energy per unit centre-of-mass energy under the equal-mass
approximation the device configuration makes."""

LEVEL0_NON_CLAIMS: Final = (
    (
        "closed-form evaluation of a published cross-section fit on a declared "
        "beam energy, with the frame stated"
    ),
    (
        "the cross section is a fit to data, carrying the fit's accuracy and "
        "not that of the measurements behind it"
    ),
    (
        "the centre-of-mass energy is the configuration's own nonrelativistic "
        "equal-mass value; for D-T the exact lab-to-centre-of-mass ratio is "
        "1.669 and not 2, and the record reports both rather than choosing"
    ),
    (
        "no beam stopping, target density, target thickness or beam-plasma "
        "interaction is modelled, so no reaction rate, yield or gain follows "
        "from this record"
    ),
    (
        "the ion rate and beam power assume every ion carries the declared "
        "charge and the declared energy; no charge-state distribution, energy "
        "spread, divergence, neutralisation or duty cycle is modelled"
    ),
    "no confinement, breakeven, ignition or net-energy statement",
    (
        "no value describes or validates any real machine; an anchor reproduces "
        "a number the filed source prints and nothing further"
    ),
)


@dataclass(frozen=True, slots=True)
class BeamInputs:
    """Declared inputs the record is evaluated at.

    Parameters
    ----------
    reaction
        Reaction key from
        :data:`~scpn_beam_target_core.physics.cross_section.REACTIONS`.
    charge_number
        Charge state of the beam ions; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If the reaction is unknown or the charge number is not strictly
        positive.
    """

    reaction: str
    charge_number: int = 1

    def __post_init__(self) -> None:
        """Validate the declared inputs.

        Raises
        ------
        DeviceConfigurationError
            If the reaction is unknown or the charge number is not
            strictly positive.
        """
        require_reaction(self.reaction)
        require_charge_number(self.charge_number)


@dataclass(frozen=True, slots=True)
class OperatingPoint:
    """The composed operating point of one validated configuration.

    Parameters
    ----------
    reaction
        The declared reaction the cross section is taken for.
    centre_of_mass_energy_kev
        From the configuration's own method, unchanged.
    equivalent_stationary_target_energy_kev
        The energy an incident ion would need against a target at rest to
        reach the same centre-of-mass energy, under the same equal-mass
        approximation the configuration makes.
    stationary_target_energy_ratio
        That energy divided by the declared beam energy: one for a
        beam-target machine and four for symmetric colliding beams.
    total_cross_section_barn
        The fit evaluated at the equivalent stationary-target energy.
    beam_energy_cross_section_barn
        The fit evaluated at the declared beam energy instead. For a
        beam-target machine the two are the same number; for colliding
        beams they are not, and the record carries both so that the
        difference is visible rather than assumed away.
    ion_rate_per_s
        Ions per second in one beam line.
    total_ion_rate_per_s
        The same across every declared beam line.
    total_beam_power_w
        Power carried by every declared beam line.
    equal_mass_lab_energy_ratio
        The approximation in force, two.
    deuterium_tritium_lab_energy_ratio
        What that ratio exactly is for D-T, from the formulary's own
        printed masses. Reported so the size of the approximation is on
        the record.
    """

    reaction: str
    centre_of_mass_energy_kev: float
    equivalent_stationary_target_energy_kev: float
    stationary_target_energy_ratio: float
    total_cross_section_barn: float
    beam_energy_cross_section_barn: float
    ion_rate_per_s: float
    total_ion_rate_per_s: float
    total_beam_power_w: float
    equal_mass_lab_energy_ratio: float
    deuterium_tritium_lab_energy_ratio: float

    def to_record(self) -> dict[str, Any]:
        """Project the operating point to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per field, in the declaration order of the class.
        """
        return {
            "reaction": self.reaction,
            "centre_of_mass_energy_kev": self.centre_of_mass_energy_kev,
            "equivalent_stationary_target_energy_kev": (
                self.equivalent_stationary_target_energy_kev
            ),
            "stationary_target_energy_ratio": self.stationary_target_energy_ratio,
            "total_cross_section_barn": self.total_cross_section_barn,
            "beam_energy_cross_section_barn": self.beam_energy_cross_section_barn,
            "ion_rate_per_s": self.ion_rate_per_s,
            "total_ion_rate_per_s": self.total_ion_rate_per_s,
            "total_beam_power_w": self.total_beam_power_w,
            "equal_mass_lab_energy_ratio": self.equal_mass_lab_energy_ratio,
            "deuterium_tritium_lab_energy_ratio": (
                self.deuterium_tritium_lab_energy_ratio
            ),
        }


@dataclass(frozen=True, slots=True)
class Level0Physics:
    """Composed level-0 record of one configuration.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the configuration the record was built from.
    operating_point
        The composed operating point.
    """

    configuration_digest_sha256: str
    operating_point: OperatingPoint

    def to_record(self) -> dict[str, Any]:
        """Project the record to a JSON-serialisable object.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with its non-claims.
        """
        return {
            "schema": LEVEL0_SCHEMA,
            "schema_version": LEVEL0_SCHEMA_VERSION,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "operating_point": self.operating_point.to_record(),
            "non_claims": list(LEVEL0_NON_CLAIMS),
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def level0_physics(
    configuration: DeviceConfiguration, inputs: BeamInputs
) -> Level0Physics:
    """Compose the level-0 physics record of one validated configuration.

    Parameters
    ----------
    configuration
        Validated beam configuration. It supplies the beam energy and
        current, the beam-line count, and the centre-of-mass energy,
        which this function calls rather than restates.
    inputs
        Declared reaction and charge state.

    Returns
    -------
    Level0Physics
        The composed record.

    Raises
    ------
    DeviceConfigurationError
        If a declared input leaves its documented interval; the refusals
        name the field.
    """
    beam = configuration.beam
    centre_of_mass = configuration.centre_of_mass_energy_kev()
    equivalent = EQUAL_MASS_LAB_ENERGY_RATIO * centre_of_mass
    rate = ion_rate_per_s(beam.beam_current_ma, inputs.charge_number)
    return Level0Physics(
        configuration_digest_sha256=configuration.digest_sha256(),
        operating_point=OperatingPoint(
            reaction=inputs.reaction,
            centre_of_mass_energy_kev=centre_of_mass,
            equivalent_stationary_target_energy_kev=equivalent,
            stationary_target_energy_ratio=equivalent / beam.kinetic_energy_kev,
            total_cross_section_barn=total_cross_section_barn(
                inputs.reaction, equivalent
            ),
            beam_energy_cross_section_barn=total_cross_section_barn(
                inputs.reaction, beam.kinetic_energy_kev
            ),
            ion_rate_per_s=rate,
            total_ion_rate_per_s=rate * configuration.beam_line_count,
            total_beam_power_w=beam_power_w(
                beam.kinetic_energy_kev, beam.beam_current_ma, inputs.charge_number
            )
            * configuration.beam_line_count,
            equal_mass_lab_energy_ratio=EQUAL_MASS_LAB_ENERGY_RATIO,
            deuterium_tritium_lab_energy_ratio=DT_LAB_ENERGY_RATIO,
        ),
    )
