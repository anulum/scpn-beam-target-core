<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Beam Target Core — ADR 0005
-->

# ADR 0005 — Level-0 device physics with the frame stated

Status: accepted (2026-09-04). Adds the third implemented capability,
`level0_device_physics`, under the evidence-maturity ceiling rule of
ADR 0002.

## Context

This repository owns two configurations that differ in one thing: whether
the target moves. A cross-section fit made for a stationary target cannot
be evaluated at a colliding-beam machine's beam energy without being
wrong, and wrong quietly — the number it returns is a perfectly ordinary
cross section, just for a machine that does not exist.

The size of the error is not small. Under the equal-mass kinematics the
configuration already uses, two beams of energy `E` meet at the same
centre-of-mass energy as one beam of `4E` striking a target at rest. So
the frame is not a footnote to this family's level-0 physics; it is the
content of it.

The two cited works for the cross section — Bosch and Hale, and Wangler —
are both paywalled and neither is on file. The 2019 NRL Plasma Formulary
is, and on page 44 it prints the Duane fit, the coefficients for six
reactions, the ion mass ratios, and a table of thermal averages.

## Decision

Implement the Duane fit with the formulary's coefficients, the beam
bookkeeping, and a level-0 record that composes them at the right energy.

- **The cross section** takes the energy of the incident ion with the
  target at rest, which is what the fit was made for, and the record
  evaluates it at the equivalent stationary-target energy rather than at
  the declared beam energy. It carries both, so that for a colliding-beam
  configuration the difference is on the record instead of being assumed
  away.
- **The centre-of-mass energy is not restated.** The device configuration
  computes it and the record calls that method. Two sources of truth for
  one number drift silently until they disagree.
- **The equal-mass approximation is reported, not hidden.** For D-T the
  exact lab-to-centre-of-mass ratio built from the formulary's own masses
  is 1.669, not 2. The record carries both numbers and the non-claims say
  which one is in force.
- **The beam bookkeeping** is two exact conversions. A current divided by
  the charge each ion carries is an ion rate; that rate times the energy
  per ion is a power, and the elementary charge cancels, so a singly
  charged beam of one milliampere at one kiloelectronvolt carries exactly
  one watt.

Every constant — the electron mass, the ion mass ratios, the elementary
charge, the barn — is taken from the one filed document, so the whole
computation closes inside a single source.

## Anchoring: a cross-check inside one document

The formulary prints the Duane coefficients and, further down the same
page, a table of Maxwellian-averaged D-T reaction rates. One implies the
other. So the thermal average is implemented here for a single purpose:
it verifies that six coefficient tuples were transcribed correctly from a
scanned page, and it does so against ten printed values spanning three
decades of temperature and five of reactivity.

**All ten are recovered at the precision they are printed to.** Each
computed value rounds to the printed two significant figures exactly.
That is a stronger statement than a tolerance, because it means the
residual — at most 1.4 % — is the table's own rounding and not an error
here. It is measured to be so: fifty times as many quadrature intervals
move the answer by less than a part in ten thousand.

The mass ratios are anchored the same way. Page 44 prints each as a
decimal and again as a reciprocal, and prints their square roots twice
over as well; the reciprocal of each printed decimal rounds back to the
printed reciprocal.

The thermal average is a verification instrument and not a relation of
the beam-target family. It is documented as such in the module.

## Consequences

The capability is registered at `computational_prototype` with its
evidence pointer at `VALIDATION.md#level-0-device-physics`, and the
package carries 100 % statement and branch coverage.

No kernel-library pin. The fit uses `exp` and `sqrt` from the standard
library, and the family's device relations are ratios; nothing needs the
shared transcendental kernels.

Below 0.0043 keV the Gamow exponential leaves the range of a double and
the cross section is returned as zero. That is the fit's value there, not
a clamp: it is smaller than the smallest positive double by hundreds of
orders of magnitude. The boundary is tested from both sides.

The record models no beam stopping, target density or thickness, so no
reaction rate, yield or gain follows from it, and the non-claims say so.
