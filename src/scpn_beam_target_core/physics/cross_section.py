# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — fusion cross sections and their thermal average

"""Total fusion cross sections of the light-ion reactions, and their average.

The cross section is the Duane fit the 2019 NRL Plasma Formulary prints
on page 44, together with the coefficients it tabulates there for the six
principal reactions. Its energy argument is the energy of the incident
ion **with the target ion at rest**, which is the geometry this
repository's device family is named for.

The thermal average exists here for one reason: it is what verifies the
transcription. The formulary prints the Duane coefficients and, further
down the same page, a table of Maxwellian-averaged reaction rates. One
implies the other, so averaging the fit reproduces the table — and does,
at the precision the table is printed to, for every one of its ten D-T
entries. It is a verification instrument, not a relation of the
beam-target family.
"""

from __future__ import annotations

import math
from typing import Final

from scpn_beam_target_core.errors import DeviceConfigurationError

DUANE_COEFFICIENTS: Final[dict[str, tuple[float, float, float, float, float]]] = {
    "d_d_t": (46.097, 372.0, 4.36e-4, 1.220, 0.0),
    "d_d_he3": (47.88, 482.0, 3.08e-4, 1.177, 0.0),
    "d_t": (45.95, 5.02e4, 1.368e-2, 1.076, 409.0),
    "d_he3": (89.27, 2.59e4, 3.98e-3, 1.297, 647.0),
    "t_t": (38.39, 448.0, 1.02e-3, 2.09, 0.0),
    "t_he3": (123.1, 11250.0, 0.0, 0.0, 0.0),
}
"""Coefficients A1 to A5 of the Duane fit, page 44. The two deuterium
branches are named for the heavy product that distinguishes them: the
tritium branch is the formulary's reaction 1a and the helium-3 branch its
reaction 1b."""

REACTIONS: Final = tuple(sorted(DUANE_COEFFICIENTS))

ELECTRON_MASS_KG: Final = 9.1094e-31
"""Electron mass, formulary constants page."""

ELECTRON_DEUTERON_MASS_RATIO: Final = 2.72e-4
ELECTRON_TRITON_MASS_RATIO: Final = 1.82e-4
"""Mass ratios printed on page 44 beside the reactions themselves. Taking
the ion masses from these rather than from a nuclear data table keeps
every constant in this module inside the one filed document."""

DEUTERON_MASS_KG: Final = ELECTRON_MASS_KG / ELECTRON_DEUTERON_MASS_RATIO
TRITON_MASS_KG: Final = ELECTRON_MASS_KG / ELECTRON_TRITON_MASS_RATIO
DT_REDUCED_MASS_KG: Final = (
    DEUTERON_MASS_KG * TRITON_MASS_KG / (DEUTERON_MASS_KG + TRITON_MASS_KG)
)
DT_LAB_ENERGY_RATIO: Final = (DEUTERON_MASS_KG + TRITON_MASS_KG) / TRITON_MASS_KG
"""Lab energy per unit centre-of-mass energy for a deuteron incident on a
triton at rest. It is 1.669, not 2: the equal-mass value the device
configuration uses is an approximation, and for this reaction it is
visibly wrong."""

ELEMENTARY_CHARGE_C: Final = 1.6022e-19
"""Elementary charge, formulary constants page; also the joules in a
kiloelectronvolt scaled by a thousand."""

KILOELECTRONVOLT_J: Final = ELEMENTARY_CHARGE_C * 1.0e3

BARN_M2: Final = 1.0e-28
"""One barn in square metres. The formulary states the barn in square
centimetres; the average below is carried in SI and converted once at the
end, so the square-metre form is what it needs."""

CUBIC_METRES_PER_CUBIC_CENTIMETRE: Final = 1.0e6

GAMOW_EXPONENT_CEILING: Final = 700.0
"""Above this the Gamow exponential overflows a double. The fit's value
there is smaller than the smallest positive double by hundreds of orders
of magnitude, so it is returned as zero rather than raised as an error;
for D-T that boundary sits at 0.0043 keV."""

DEFAULT_QUADRATURE_SAMPLES: Final = 2000
"""Midpoint intervals for the thermal average. Chosen by measurement: the
departure from the printed table is 1.4 % at this count and unchanged at
fifty times as many, so it is the source's own rounding and not
quadrature error."""


def require_reaction(reaction: str) -> tuple[float, float, float, float, float]:
    """Return the Duane coefficients of a known reaction.

    Parameters
    ----------
    reaction
        Reaction key from :data:`REACTIONS`.

    Returns
    -------
    tuple of float
        The coefficients A1 to A5.

    Raises
    ------
    DeviceConfigurationError
        If no coefficients are tabulated for that reaction.
    """
    try:
        return DUANE_COEFFICIENTS[reaction]
    except KeyError:
        raise DeviceConfigurationError(
            f"reaction: must be one of {REACTIONS!r}, got {reaction!r}"
        ) from None


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
        If ``value`` is non-finite or not strictly positive. Non-finite
        input is rejected, never clamped.
    """
    if not math.isfinite(value):
        raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    if value <= 0.0:
        raise DeviceConfigurationError(
            f"{name}: must be strictly positive, got {value!r}"
        )
    return value


def total_cross_section_barn(reaction: str, incident_energy_kev: float) -> float:
    """Total cross section of one reaction against a target ion at rest.

    The Duane fit of page 44,
    ``[A5 + A2 / ((A4 - A3 E)^2 + 1)] / (E [exp(A1 E^-1/2) - 1])``,
    with ``E`` the kinetic energy of the incident ion in keV.

    Parameters
    ----------
    reaction
        Reaction key from :data:`REACTIONS`.
    incident_energy_kev
        Kinetic energy of the incident ion in the frame where the target
        is at rest; strictly positive.

    Returns
    -------
    float
        The cross section in barns; zero below the energy at which the
        Gamow exponential leaves the range of a double.

    Raises
    ------
    DeviceConfigurationError
        If the reaction is unknown or the energy is non-finite or not
        strictly positive.
    """
    a1, a2, a3, a4, a5 = require_reaction(reaction)
    require_positive("incident_energy_kev", incident_energy_kev)
    exponent = a1 / math.sqrt(incident_energy_kev)
    if exponent > GAMOW_EXPONENT_CEILING:
        return 0.0
    resonance = a5 + a2 / ((a4 - a3 * incident_energy_kev) ** 2 + 1.0)
    return resonance / (incident_energy_kev * math.expm1(exponent))


def maxwellian_reactivity_cm3_per_s(
    reaction: str,
    temperature_kev: float,
    reduced_mass_kg: float = DT_REDUCED_MASS_KG,
    lab_energy_ratio: float = DT_LAB_ENERGY_RATIO,
    samples: int = DEFAULT_QUADRATURE_SAMPLES,
) -> float:
    """Average the cross section over a Maxwellian relative-velocity distribution.

    ``<sigma v> = sqrt(8 / (pi mu)) (kT)^-3/2 integral sigma(E) E exp(-E/kT) dE``
    over the centre-of-mass energy, with the fit evaluated at the lab
    energy the centre-of-mass energy corresponds to.

    The integral is taken by the midpoint rule out to forty temperatures
    plus a fixed margin, which covers the resonance even at the lowest
    temperature the formulary tabulates.

    Parameters
    ----------
    reaction
        Reaction key from :data:`REACTIONS`.
    temperature_kev
        Maxwellian temperature; strictly positive.
    reduced_mass_kg
        Reduced mass of the reacting pair; strictly positive. The default
        is the D-T value built from the formulary's own printed masses.
    lab_energy_ratio
        Lab energy per unit centre-of-mass energy, ``(m1 + m2) / m2`` for
        an incident ion of mass ``m1`` and a target of mass ``m2``;
        strictly positive.
    samples
        Midpoint intervals; strictly positive.

    Returns
    -------
    float
        The reaction rate coefficient in cubic centimetres per second.

    Raises
    ------
    DeviceConfigurationError
        If the reaction is unknown or any input leaves its interval.
    """
    require_reaction(reaction)
    require_positive("temperature_kev", temperature_kev)
    require_positive("reduced_mass_kg", reduced_mass_kg)
    require_positive("lab_energy_ratio", lab_energy_ratio)
    if samples <= 0:
        raise DeviceConfigurationError(
            f"samples: must be strictly positive, got {samples!r}"
        )
    upper = 40.0 * temperature_kev + 300.0
    step = upper / samples
    total = 0.0
    for index in range(samples):
        energy_kev = (index + 0.5) * step
        total += (
            total_cross_section_barn(reaction, energy_kev * lab_energy_ratio)
            * energy_kev
            * math.exp(-energy_kev / temperature_kev)
        )
    integral = total * step * KILOELECTRONVOLT_J * KILOELECTRONVOLT_J * BARN_M2
    thermal = math.pow(temperature_kev * KILOELECTRONVOLT_J, -1.5)
    return (
        math.sqrt(8.0 / (math.pi * reduced_mass_kg))
        * thermal
        * integral
        * CUBIC_METRES_PER_CUBIC_CENTIMETRE
    )
