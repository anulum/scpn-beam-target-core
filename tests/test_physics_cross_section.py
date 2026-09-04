# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — cross-section tests

"""Every branch of the cross section and its thermal average.

The central test is a cross-check inside one document: the formulary
prints the fit's coefficients and, separately, a table of thermal
averages, and averaging the fit reproduces the table.
"""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    PRINTED_DT_REACTIVITY_CM3_PER_S,
    PRINTED_MASS_RATIO_PAIRS,
    PRINTED_MASS_RATIO_ROOTS,
    PRINTED_SIGNIFICANT_FIGURES,
    round_to_significant_figures,
)
from scpn_beam_target_core.errors import DeviceConfigurationError
from scpn_beam_target_core.physics.cross_section import (
    DEFAULT_QUADRATURE_SAMPLES,
    DT_LAB_ENERGY_RATIO,
    DT_REDUCED_MASS_KG,
    DUANE_COEFFICIENTS,
    ELECTRON_DEUTERON_MASS_RATIO,
    ELECTRON_TRITON_MASS_RATIO,
    REACTIONS,
    maxwellian_reactivity_cm3_per_s,
    require_positive,
    require_reaction,
    total_cross_section_barn,
)


def test_every_tabulated_reaction_is_reachable_by_name() -> None:
    """The reaction keys and the coefficient table agree."""
    assert set(REACTIONS) == set(DUANE_COEFFICIENTS)
    assert len(REACTIONS) == len(DUANE_COEFFICIENTS)
    for reaction in REACTIONS:
        assert len(require_reaction(reaction)) == 5


def test_an_unknown_reaction_is_refused_and_the_known_ones_listed() -> None:
    """The refusal tells the caller what it could have asked for."""
    with pytest.raises(DeviceConfigurationError, match="d_li6"):
        require_reaction("d_li6")


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, 0.0, -1.0])
def test_the_positive_guard_refuses_by_name(value: float) -> None:
    """Non-finite and non-positive input is refused, never clamped."""
    with pytest.raises(DeviceConfigurationError, match="energy"):
        require_positive("energy", value)


def test_the_positive_guard_passes_a_valid_value_through() -> None:
    """A valid value comes back unchanged."""
    assert require_positive("energy", 120.0) == 120.0


@pytest.mark.parametrize(
    ("reaction", "energy", "field"),
    [
        ("d_li6", 120.0, "d_li6"),
        ("d_t", 0.0, "incident_energy_kev"),
        ("d_t", math.nan, "incident_energy_kev"),
    ],
)
def test_the_cross_section_refuses_by_name(
    reaction: str, energy: float, field: str
) -> None:
    """Both guards of the fit name what they refused."""
    with pytest.raises(DeviceConfigurationError, match=field):
        total_cross_section_barn(reaction, energy)


def test_the_cross_section_falls_to_zero_below_the_gamow_boundary() -> None:
    """Beneath the boundary the fit underflows, and zero is its value there.

    The Gamow exponential leaves the range of a double at 0.0043 keV for
    D-T. Returning zero is not a clamp of a representable value: the fit
    there is smaller than the smallest positive double by hundreds of
    orders of magnitude.
    """
    assert total_cross_section_barn("d_t", 0.004) == 0.0
    assert total_cross_section_barn("d_t", 0.005) > 0.0


def test_the_cross_section_rises_and_falls_around_one_resonance() -> None:
    """The D-T fit has a single maximum, as the reaction has one resonance."""
    energies = [e / 2.0 for e in range(2, 1200)]
    values = [total_cross_section_barn("d_t", e) for e in energies]
    peak = values.index(max(values))
    assert 0 < peak < len(values) - 1
    assert values[:peak] == sorted(values[:peak])
    assert values[peak:] == sorted(values[peak:], reverse=True)


def test_every_printed_thermal_average_is_recovered_at_its_printed_precision() -> None:
    """Averaging the printed fit reproduces the printed table exactly.

    The formulary prints the Duane coefficients and, further down page 44,
    a table of Maxwellian-averaged D-T rates. One implies the other, so
    this is a cross-check inside a single document and it verifies both
    the transcription of six coefficients and the average itself.

    Every one of the ten entries is recovered, and each computed value
    rounds to the printed one at the two significant figures the table
    carries. That is a stronger statement than a tolerance: the residual
    is the table's own rounding.
    """
    for temperature, printed in PRINTED_DT_REACTIVITY_CM3_PER_S:
        computed = maxwellian_reactivity_cm3_per_s("d_t", temperature)
        assert round_to_significant_figures(
            computed, PRINTED_SIGNIFICANT_FIGURES
        ) == pytest.approx(printed, rel=1e-9)


def test_the_average_is_converged_at_the_default_sample_count() -> None:
    """The residual against the table is the table's rounding, not quadrature.

    Fifty times as many intervals move the answer by less than a part in
    ten thousand, so the default is not a tolerance the anchor leans on.
    """
    for temperature in (1.0, 10.0, 1000.0):
        coarse = maxwellian_reactivity_cm3_per_s("d_t", temperature)
        fine = maxwellian_reactivity_cm3_per_s(
            "d_t", temperature, samples=DEFAULT_QUADRATURE_SAMPLES * 50
        )
        assert math.isclose(coarse, fine, rel_tol=1e-4)


@pytest.mark.parametrize(
    ("field", "reaction", "temperature", "mass", "ratio", "samples"),
    [
        ("d_li6", "d_li6", 10.0, DT_REDUCED_MASS_KG, DT_LAB_ENERGY_RATIO, 64),
        ("temperature_kev", "d_t", 0.0, DT_REDUCED_MASS_KG, DT_LAB_ENERGY_RATIO, 64),
        ("reduced_mass_kg", "d_t", 10.0, -1.0, DT_LAB_ENERGY_RATIO, 64),
        ("lab_energy_ratio", "d_t", 10.0, DT_REDUCED_MASS_KG, math.inf, 64),
        ("samples", "d_t", 10.0, DT_REDUCED_MASS_KG, DT_LAB_ENERGY_RATIO, 0),
    ],
)
def test_the_thermal_average_refuses_by_name(
    field: str,
    reaction: str,
    temperature: float,
    mass: float,
    ratio: float,
    samples: int,
) -> None:
    """Each guard of the average names what it refused."""
    with pytest.raises(DeviceConfigurationError, match=field):
        maxwellian_reactivity_cm3_per_s(reaction, temperature, mass, ratio, samples)


@pytest.mark.parametrize(("name", "ratio", "reciprocal"), PRINTED_MASS_RATIO_PAIRS)
def test_the_printed_mass_ratios_agree_with_their_printed_reciprocals(
    name: str, ratio: float, reciprocal: float
) -> None:
    """Page 44 prints each mass ratio twice, and the two agree.

    This is what proves the transcription: the reciprocal of the printed
    decimal rounds back to the printed reciprocal, and the reciprocal of
    the printed reciprocal rounds back to the printed decimal.
    """
    assert round_to_significant_figures(
        1.0 / reciprocal, PRINTED_SIGNIFICANT_FIGURES + 1
    ) == pytest.approx(ratio, rel=1e-9)
    assert abs(1.0 / ratio - reciprocal) < 0.01 * reciprocal
    assert name


@pytest.mark.parametrize(
    ("name", "ratio", "root", "reciprocal"), PRINTED_MASS_RATIO_ROOTS
)
def test_the_printed_square_roots_follow_from_the_printed_ratios(
    name: str, ratio: float, root: float, reciprocal: float
) -> None:
    """The printed roots and their printed reciprocals are recoverable."""
    assert math.sqrt(ratio) == pytest.approx(root, abs=5e-5)
    assert 1.0 / math.sqrt(ratio) == pytest.approx(reciprocal, abs=0.05)
    assert name


def test_the_ion_masses_are_built_from_the_formulary_alone() -> None:
    """The lab-to-centre-of-mass ratio is 1.669 for D-T, and not 2.

    The device configuration's centre-of-mass energy uses an equal-mass
    approximation, for which the ratio would be exactly 2. The exact
    value built from the formulary's own printed masses is 1.669, so the
    approximation is a sixth off and the record reports both.
    """
    assert pytest.approx(1.66912, abs=1e-5) == DT_LAB_ENERGY_RATIO
    assert DT_LAB_ENERGY_RATIO < 2.0
    ratio = ELECTRON_TRITON_MASS_RATIO / ELECTRON_DEUTERON_MASS_RATIO
    assert pytest.approx(1.0 + ratio, rel=1e-12) == DT_LAB_ENERGY_RATIO
