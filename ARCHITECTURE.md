<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Beam Target Core — Architecture summary
-->

# Architecture summary

`SCPN-BEAM-TARGET-CORE` is the device-family owner for beam-target and
colliding-beam fusion systems inside the SCPN Reactor Systems Research
Group. The repository is currently `architecture_only`: it defines the
device boundary, its ecosystem contracts, and the validation tooling that
enforces both, and it implements no reactor capability.

The authoritative architecture record is
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). The ownership decision and
its consequences are fixed in
[`docs/adr/0001-repository-boundary.md`](docs/adr/0001-repository-boundary.md).

Boundary in one paragraph: this repository owns beam-target plant and
experiment truth — configuration policy for non-thermal fusion whose
kinematics are set directly by accelerated beams (fixed/flowing target or
counter-propagating beams), run-oriented lifecycle semantics with beam-loss
and target-damage hazard records, kinematic diagnostic and clock
declarations that always pair yield with stopping and scattering losses,
actuator-response boundaries, safety-envelope declarations, and the
device-owned CONTROL adapter specification — with no energy-gain claim of
any kind made or implied. Beam-driven implosion stays with
`SCPN-ICF-BEAM-CORE`; solver mathematics in `SCPN-FUSION-CORE`; typed
semantics in `SCPN-PHASE-ORCHESTRATOR` (review-only); admitted control
actions are formed only by `SCPN-CONTROL`; independent machine protection
keeps the final veto; portfolio presentation belongs to `SCPN-STUDIO`,
towards which this project is `not_federated`.
