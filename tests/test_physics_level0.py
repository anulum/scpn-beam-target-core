# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — level-0 physics record tests

"""Every branch of the level-0 record, and the frame it is about."""

from __future__ import annotations

import hashlib
import json

import pytest

from physics_fixtures import reference_inputs, synthetic_configuration
from scpn_beam_target_core.errors import DeviceConfigurationError
from scpn_beam_target_core.physics import (
    EQUAL_MASS_LAB_ENERGY_RATIO,
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    BeamInputs,
    level0_physics,
    total_cross_section_barn,
)

COLLIDING_BEAM_ADVANTAGE = 4.0


@pytest.mark.parametrize(
    ("reaction", "charge", "field"),
    [
        ("d_li6", 1, "d_li6"),
        ("d_t", 0, "charge_number"),
        ("d_t", -2, "charge_number"),
    ],
)
def test_declared_inputs_are_refused_by_name_at_construction(
    reaction: str, charge: int, field: str
) -> None:
    """A record can never be built from inputs the relations would refuse."""
    with pytest.raises(DeviceConfigurationError, match=field):
        BeamInputs(reaction=reaction, charge_number=charge)


def test_the_record_carries_the_configuration_digest() -> None:
    """The record names the exact configuration it was built from."""
    configuration = synthetic_configuration()
    record = level0_physics(configuration, reference_inputs())
    assert record.configuration_digest_sha256 == configuration.digest_sha256()


def test_the_centre_of_mass_energy_is_the_configuration_s_own() -> None:
    """The record calls the configuration's method rather than restating it.

    Two sources of truth for one number drift silently until they
    disagree, so the record has none of its own.
    """
    for identifier in ("beam_target", "colliding_beam"):
        configuration = synthetic_configuration(identifier)
        point = level0_physics(configuration, reference_inputs()).operating_point
        assert point.centre_of_mass_energy_kev == (
            configuration.centre_of_mass_energy_kev()
        )


def test_colliding_beams_reach_four_times_their_own_energy() -> None:
    """The reason colliding-beam machines exist, stated exactly.

    Two beams of energy E meet at the centre-of-mass energy of a single
    beam of 4E striking a stationary target. The ratio is exact under the
    equal-mass approximation the configuration makes, so it is asserted
    as an equality.
    """
    beam_target = level0_physics(
        synthetic_configuration("beam_target"), reference_inputs()
    ).operating_point
    colliding = level0_physics(
        synthetic_configuration("colliding_beam"), reference_inputs()
    ).operating_point
    assert beam_target.stationary_target_energy_ratio == 1.0
    assert colliding.stationary_target_energy_ratio == COLLIDING_BEAM_ADVANTAGE
    assert colliding.equivalent_stationary_target_energy_kev == (
        COLLIDING_BEAM_ADVANTAGE * 120.0
    )


def test_the_cross_section_is_taken_at_the_frame_the_fit_was_made_in() -> None:
    """The fit assumes the target at rest, so it is evaluated there.

    For a beam-target machine the two energies coincide and so do the two
    cross sections. For colliding beams they do not, and the record
    carries both so the difference is visible rather than assumed away.

    Which of the two is larger is not fixed, because the fit has a
    resonance. A colliding-beam machine below it moves towards the peak
    and gains; one already at the peak is thrown past it and loses. Both
    directions are exercised, because assuming the first was a mistake
    this test was written to correct.
    """
    beam_target = level0_physics(
        synthetic_configuration("beam_target"), reference_inputs()
    ).operating_point
    assert beam_target.total_cross_section_barn == (
        beam_target.beam_energy_cross_section_barn
    )
    colliding = level0_physics(
        synthetic_configuration("colliding_beam"), reference_inputs()
    ).operating_point
    assert colliding.total_cross_section_barn != (
        colliding.beam_energy_cross_section_barn
    )
    assert colliding.total_cross_section_barn == total_cross_section_barn(
        "d_t", COLLIDING_BEAM_ADVANTAGE * 120.0
    )
    below_the_peak = level0_physics(
        synthetic_configuration("colliding_beam", kinetic_energy_kev=20.0),
        reference_inputs(),
    ).operating_point
    assert below_the_peak.total_cross_section_barn > (
        below_the_peak.beam_energy_cross_section_barn
    )
    assert colliding.total_cross_section_barn < (
        colliding.beam_energy_cross_section_barn
    )


def test_the_equal_mass_approximation_is_reported_beside_its_exact_value() -> None:
    """The record states the size of the approximation instead of hiding it."""
    point = level0_physics(
        synthetic_configuration(), reference_inputs()
    ).operating_point
    assert point.equal_mass_lab_energy_ratio == EQUAL_MASS_LAB_ENERGY_RATIO
    assert point.deuterium_tritium_lab_energy_ratio < (
        point.equal_mass_lab_energy_ratio
    )
    assert point.deuterium_tritium_lab_energy_ratio == pytest.approx(1.669, abs=1e-3)


def test_the_beam_totals_follow_the_declared_line_count() -> None:
    """Two lines carry twice the ions and twice the power of one."""
    one = level0_physics(
        synthetic_configuration("beam_target"), reference_inputs()
    ).operating_point
    two = level0_physics(
        synthetic_configuration("colliding_beam"), reference_inputs()
    ).operating_point
    assert one.total_ion_rate_per_s == one.ion_rate_per_s
    assert two.total_ion_rate_per_s == 2.0 * two.ion_rate_per_s
    assert two.total_beam_power_w == 2.0 * one.total_beam_power_w
    assert one.total_beam_power_w == 120.0 * 50.0


def test_a_higher_charge_state_lowers_the_ion_rate_and_the_power() -> None:
    """The declared charge state enters both totals."""
    singly = level0_physics(
        synthetic_configuration(), BeamInputs(reaction="d_t")
    ).operating_point
    doubly = level0_physics(
        synthetic_configuration(), BeamInputs(reaction="d_t", charge_number=2)
    ).operating_point
    assert doubly.ion_rate_per_s == pytest.approx(singly.ion_rate_per_s / 2.0)
    assert doubly.total_beam_power_w == pytest.approx(singly.total_beam_power_w / 2.0)


def test_the_record_projects_every_field_it_carries() -> None:
    """The projection loses nothing the operating point holds."""
    record = level0_physics(synthetic_configuration(), reference_inputs())
    projected = record.to_record()
    assert set(projected["operating_point"]) == set(record.operating_point.__slots__)
    assert projected["schema"] == LEVEL0_SCHEMA
    assert projected["schema_version"] == LEVEL0_SCHEMA_VERSION
    assert projected["non_claims"] == list(LEVEL0_NON_CLAIMS)


def test_the_canonical_bytes_are_canonical() -> None:
    """Sorted keys, minimal separators, one trailing newline, and idempotent.

    Idempotence is the property that matters: re-canonicalising the
    parsed bytes reproduces them exactly. Asserting the absence of a
    separator would be wrong, because the non-claims are English prose
    that contains commas of its own.
    """
    record = level0_physics(synthetic_configuration(), reference_inputs())
    data = record.canonical_bytes()
    assert data.endswith(b"\n")
    assert data.count(b"\n") == 1
    again = json.dumps(
        json.loads(data), sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    assert (again + "\n").encode("utf-8") == data


def test_the_digest_identifies_the_record() -> None:
    """The digest is the SHA-256 of the canonical bytes and moves with them."""
    record = level0_physics(synthetic_configuration(), reference_inputs())
    assert (
        record.digest_sha256() == hashlib.sha256(record.canonical_bytes()).hexdigest()
    )
    moved = level0_physics(
        synthetic_configuration(kinetic_energy_kev=130.0), reference_inputs()
    )
    assert moved.digest_sha256() != record.digest_sha256()
