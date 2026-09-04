# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — beam-line bookkeeping

"""What a declared beam current and energy amount to.

Two conversions, both exact. A current is a count of charges per second,
so dividing it by the charge each ion carries gives the ion rate. The
power that rate carries is the ion rate times the energy each ion has,
and the elementary charge cancels between the two: a beam of one
milliampere at one kilovolt per unit charge carries exactly one watt.

Neither conversion knows anything about what the beam strikes. The
stopping of the beam in a target, and therefore whether any of this
energy is recovered, is not modelled anywhere in this repository.
"""

from __future__ import annotations

from typing import Final

from scpn_beam_target_core.errors import DeviceConfigurationError
from scpn_beam_target_core.physics.cross_section import (
    ELEMENTARY_CHARGE_C,
    require_positive,
)

MILLI: Final = 1.0e-3


def require_charge_number(charge_number: int) -> int:
    """Return ``charge_number`` when it is a positive integer.

    Parameters
    ----------
    charge_number
        Charge state of the beam ions in units of the elementary charge.

    Returns
    -------
    int
        The validated charge number.

    Raises
    ------
    DeviceConfigurationError
        If the charge number is not strictly positive. A neutral or
        negative beam is refused rather than reinterpreted: the device
        family declares accelerated ions, and a current carried by
        anything else would make the ion rate below meaningless.
    """
    if charge_number <= 0:
        raise DeviceConfigurationError(
            f"charge_number: must be strictly positive, got {charge_number!r}"
        )
    return charge_number


def ion_rate_per_s(beam_current_ma: float, charge_number: int = 1) -> float:
    """Ions per second carried by a declared beam current.

    Parameters
    ----------
    beam_current_ma
        Beam current in milliamperes; strictly positive.
    charge_number
        Charge state of the ions; strictly positive.

    Returns
    -------
    float
        Ions per second.

    Raises
    ------
    DeviceConfigurationError
        If the current is non-finite or not strictly positive, or the
        charge number is not strictly positive.
    """
    require_positive("beam_current_ma", beam_current_ma)
    require_charge_number(charge_number)
    return beam_current_ma * MILLI / (charge_number * ELEMENTARY_CHARGE_C)


def beam_power_w(
    kinetic_energy_kev: float, beam_current_ma: float, charge_number: int = 1
) -> float:
    """Power a declared beam carries.

    The ion rate times the energy each ion has. The elementary charge
    cancels, leaving the energy in kiloelectronvolts times the current in
    milliamperes divided by the charge number — so a singly charged beam
    of one milliampere at one kiloelectronvolt carries exactly one watt.

    Parameters
    ----------
    kinetic_energy_kev
        Kinetic energy per ion in keV; strictly positive.
    beam_current_ma
        Beam current in milliamperes; strictly positive.
    charge_number
        Charge state of the ions; strictly positive.

    Returns
    -------
    float
        Beam power in watts.

    Raises
    ------
    DeviceConfigurationError
        If any input leaves its documented interval.
    """
    require_positive("kinetic_energy_kev", kinetic_energy_kev)
    require_positive("beam_current_ma", beam_current_ma)
    require_charge_number(charge_number)
    return kinetic_energy_kev * beam_current_ma / charge_number
