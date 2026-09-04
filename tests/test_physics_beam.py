# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — beam bookkeeping tests

"""Every branch of the beam bookkeeping, and the identity behind it."""

from __future__ import annotations

import math

import pytest

from scpn_beam_target_core.errors import DeviceConfigurationError
from scpn_beam_target_core.physics.beam import (
    beam_power_w,
    ion_rate_per_s,
    require_charge_number,
)
from scpn_beam_target_core.physics.cross_section import ELEMENTARY_CHARGE_C


@pytest.mark.parametrize("charge", [0, -1, -3])
def test_a_neutral_or_negative_charge_state_is_refused(charge: int) -> None:
    """The guard names its field and refuses rather than reinterpreting."""
    with pytest.raises(DeviceConfigurationError, match="charge_number"):
        require_charge_number(charge)


@pytest.mark.parametrize("charge", [1, 2, 6])
def test_a_positive_charge_state_passes_through(charge: int) -> None:
    """A valid charge number comes back unchanged."""
    assert require_charge_number(charge) == charge


@pytest.mark.parametrize(
    ("current", "charge", "field"),
    [
        (0.0, 1, "beam_current_ma"),
        (math.nan, 1, "beam_current_ma"),
        (50.0, 0, "charge_number"),
    ],
)
def test_the_ion_rate_refuses_by_name(current: float, charge: int, field: str) -> None:
    """Both guards of the ion rate name what they refused."""
    with pytest.raises(DeviceConfigurationError, match=field):
        ion_rate_per_s(current, charge)


def test_the_ion_rate_is_the_current_divided_by_the_charge_each_ion_carries() -> None:
    """A current is a count of charges, so the rate follows by division."""
    assert ion_rate_per_s(1.0) == pytest.approx(1.0e-3 / ELEMENTARY_CHARGE_C)
    assert ion_rate_per_s(50.0, 2) == pytest.approx(ion_rate_per_s(50.0) / 2.0)


@pytest.mark.parametrize(
    ("energy", "current", "charge", "field"),
    [
        (0.0, 50.0, 1, "kinetic_energy_kev"),
        (120.0, math.inf, 1, "beam_current_ma"),
        (120.0, 50.0, -1, "charge_number"),
    ],
)
def test_the_beam_power_refuses_by_name(
    energy: float, current: float, charge: int, field: str
) -> None:
    """Each guard of the beam power names what it refused."""
    with pytest.raises(DeviceConfigurationError, match=field):
        beam_power_w(energy, current, charge)


def test_one_milliampere_at_one_kilovolt_is_exactly_one_watt() -> None:
    """The elementary charge cancels between the ion rate and the energy.

    Asserted as an equality rather than a tolerance, because the
    cancellation is algebraic: the charge appears once in the denominator
    of the ion rate and once in the numerator of the energy per ion, and
    the implementation never forms either.
    """
    assert beam_power_w(1.0, 1.0) == 1.0
    assert beam_power_w(120.0, 50.0) == 6000.0


def test_the_beam_power_agrees_with_the_ion_rate_times_the_energy() -> None:
    """The short form and the long form are the same number.

    The long form goes through the elementary charge twice; the short one
    not at all. They agree to within a relative tolerance rather than
    exactly, because the round trip through the charge is not lossless in
    binary.
    """
    for energy in (1.0, 120.0, 2500.0):
        for current in (0.5, 50.0, 1000.0):
            for charge in (1, 2):
                long_form = (
                    ion_rate_per_s(current, charge)
                    * energy
                    * 1.0e3
                    * ELEMENTARY_CHARGE_C
                )
                assert math.isclose(
                    beam_power_w(energy, current, charge), long_form, rel_tol=1e-12
                )
