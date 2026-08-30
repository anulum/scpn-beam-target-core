<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Beam Target Core — ADR 0001: repository boundary
-->

# ADR 0001 — Repository boundary and ownership

**Status:** accepted (2026-08-30)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The SCPN reactor portfolio assigns every built-in configuration of the SCPN
Phase Orchestrator reactor registry (version `1.0.0`, 32 configurations) to
exactly one device-family repository. The `beam_target` registry family is
the portfolio's only non-thermal, non-confining family and borders three
other owners with beam heritage; a boundary decision was needed on those
edges.

## Decision

1. `SCPN-BEAM-TARGET-CORE` owns exactly two registry configurations:
   `beam_target` and `colliding_beam`. Both set reaction kinematics
   directly with accelerated beams and share the accelerator driver
   class, run lifecycle, detector-based diagnostics, and the mandatory
   honest energy-balance accounting; fixed-target versus colliding
   geometry is the configuration parameter.
2. The repository owns device-level truth only: beam-kinematics
   configuration policy (beam energy, luminosity, target-state
   declarations), run lifecycle semantics with beam-loss and
   target-damage hazard records, kinematic diagnostic and clock
   declarations, actuator-response model boundaries, the safety-envelope
   declaration, and the device-owned CONTROL adapter specification. The
   family's contracts must always pair yield declarations with
   stopping/scattering loss declarations; no gain claim is made or
   implied.
3. Beam-driven implosion stays with `SCPN-ICF-BEAM-CORE`; the plasma
   focus's internally generated beam component with
   `SCPN-DENSE-PLASMA-FOCUS-CORE`; recirculating potential-well devices
   with `SCPN-IEC-CORE`.
4. Solver mathematics remains in `SCPN-FUSION-CORE` until an exact surface
   passes the family migration gate. No solver code is copied here.
5. Typed semantics remain in `SCPN-PHASE-ORCHESTRATOR` (review-only).
   Admission and `ControlAction` formation remain exclusively in
   `SCPN-CONTROL`. Machine protection remains independent with the final
   veto. Presentation remains in `SCPN-STUDIO`; this project is
   `not_federated`.
6. The repository starts, and remains until evidenced otherwise, at
   `architecture_only` with empty capability and claim inventories.

## Alternatives considered

- **Grouping with beam-driven ICF** (shared accelerator heritage):
  rejected — no implosion exists here; lifecycle is run-oriented rather
  than shot-cycle, and the physics question is kinematic rate-versus-loss
  accounting, not implosion hydrodynamics.
- **Separate repositories for fixed-target and colliding-beam**:
  rejected — all five boundary surfaces are substantially shared; the
  split would duplicate contracts for a geometry parameter.
- **Absorbing solver code at scaffold time**: rejected — violates the
  migration gate.

## Consequences

- Downstream consumers get one stable identity per beam-target
  configuration and a manifest to bind against.
- The validator fails on any capability or claim entry while maturity is
  `architecture_only`.
- Boundary changes require a portfolio-level map change first; a future
  ADR records any such change here.
