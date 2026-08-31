# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — parameter model tests

"""Every validation branch of the beam-target parameter model.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import math

import pytest

from scpn_beam_target_core.errors import DeviceConfigurationError
from scpn_beam_target_core.parameters import (
    BeamLine,
    require_finite,
    require_positive,
)


def synthetic_beam(**overrides: float) -> BeamLine:
    """Build a valid synthetic beam line with optional overrides."""
    values: dict[str, float] = {
        "kinetic_energy_kev": 120.0,
        "beam_current_ma": 50.0,
    }
    values.update(overrides)
    return BeamLine(**values)


def test_require_finite_accepts_and_rejects() -> None:
    """The finite guard returns the value and rejects NaN and infinity."""
    assert require_finite("x", 1.5) == 1.5
    for bad in (math.nan, math.inf, -math.inf):
        with pytest.raises(DeviceConfigurationError, match="x: must be finite"):
            require_finite("x", bad)


def test_require_positive_accepts_and_rejects() -> None:
    """The positive guard returns the value and rejects zero and below."""
    assert require_positive("x", 0.1) == 0.1
    for bad in (0.0, -2.0):
        with pytest.raises(DeviceConfigurationError, match="strictly positive"):
            require_positive("x", bad)
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        require_positive("x", math.nan)


def test_valid_beam_constructs() -> None:
    """A valid beam line constructs unchanged."""
    assert synthetic_beam().kinetic_energy_kev == 120.0


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"kinetic_energy_kev": 0.0}, "kinetic_energy_kev"),
        ({"beam_current_ma": -1.0}, "beam_current_ma"),
        ({"kinetic_energy_kev": math.nan}, "kinetic_energy_kev"),
    ],
)
def test_invalid_beam_is_rejected(overrides: dict[str, float], fragment: str) -> None:
    """Each beam-line violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        synthetic_beam(**overrides)
