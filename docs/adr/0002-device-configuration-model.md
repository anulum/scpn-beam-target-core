<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Beam Target Core — ADR 0002: device configuration model
-->

# ADR 0002 — Device configuration model and evidence-maturity semantics

**Status:** accepted (2026-08-31)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The repository was established architecture-only (ADR 0001). The first
capability lane is the device configuration model for the two registry
configurations this repository owns (`beam_target`, `colliding_beam`).
The claim boundary and repository-level `evidence_maturity` semantics
follow the family pilot.

## Decision

1. The package `scpn_beam_target_core` implements the device
   configuration model as frozen, strictly typed value objects: the
   beam line (per-particle kinetic energy, beam current) and the
   configuration container with the beam-line count.
2. Claim boundary — identical to the family pilot: internal-consistency
   validation, cited textbook estimates with documented bounds,
   canonical serialisation with SHA-256 digest, and the data-only SPO
   registry pin. No claim about any real machine; every exercised
   parameter set is a synthetic test fixture.
3. Hard class invariant: `beam_target` declares exactly one beam line
   (beam on a stationary target) and `colliding_beam` exactly two.
4. Derived quantity with citation: the nonrelativistic equal-mass
   centre-of-mass kinetic energy — ``E_cm = E/2`` for a stationary
   target and ``E_cm = 2E`` for symmetric colliding beams (standard
   two-body kinematics). Advisory finding, reported by
   `consistency_report()` and never clamped: a centre-of-mass energy
   outside the documented ``[10, 300] keV`` window in which
   light-ion fusion cross sections are appreciable (D-T peak near
   64 keV c.m.; H.-S. Bosch, G. M. Hale, Nucl. Fusion 32 (1992) 611).
5. Repository-level `evidence_maturity` = the highest state claimed by
   any capability entry; per-capability states are the authoritative
   claim surface.
6. Everything else is unchanged: review-only/non-actionable SPO
   profile, no adapter implementation, empty solver seams,
   `not_federated` Studio state, independent machine-protection veto,
   all non-claims.

## Consequences

- The Studio descriptor's `capabilities` array carries its first item
  (schema 1.1.0 data change only).
- The reactor-domain validator gains the populated-capabilities branch
  with the ceiling rule.
- Later lanes (beam/luminosity/product diagnostic semantics with
  bunch-level clocks, safety envelope) build on these types; maturity
  advances per capability only with the evidence the family standard
  requires.
