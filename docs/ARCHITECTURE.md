<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Beam Target Core — Architecture
-->

# Architecture

## Purpose and evidence state

`SCPN-BEAM-TARGET-CORE` is the device-family owner for beam-target and
colliding-beam fusion systems in the SCPN Reactor Systems Research Group
portfolio. The
repository owns one implemented capability — the device configuration model
at `computational_prototype` (`src/scpn_beam_target_core/`, design record ADR 0002,
evidence record `VALIDATION.md#device-configuration-model`). Every other
section below describes boundaries and contracts. The claim inventory is
empty; capability and claim inventories are generated and drift-checked.

## The five-surface boundary

1. **Governing confinement physics** — non-thermal fusion with reaction
   kinematics set directly by accelerated beams (`beam_target` registry
   family): the `beam_target` configuration drives an energetic beam onto
   a fixed or flowing target, and the `colliding_beam` configuration
   brings counter-propagating beams to collision, doubling the available
   centre-of-momentum energy. Neither configuration implodes or
   magnetically confines a thermal plasma; the defining physics is
   reaction-rate kinematics against the loss channels of beam stopping
   and small-angle scattering, which this family's contracts must always
   declare alongside yield. Beam-driven implosion, the plasma focus's
   internal beam component, and recirculating-well IEC devices are
   excluded.
2. **Primary driver and energy delivery** — accelerator systems (ion
   sources, linacs or storage rings, beam transport and focusing), target
   stations or interaction-region optics; luminosity management is the
   colliding-beam configuration's first-class facet.
3. **Plant and shot lifecycle** — run-oriented lifecycle: source and
   accelerator conditioning, beam tuning, sustained run with luminosity
   or target-current accounting, and controlled run end. Device-level
   hazard semantics cover beam loss and mis-steer, target thermal damage,
   and activation constraints.
4. **Diagnostic, reference-frame, and clock model** — beamline and
   interaction-region coordinate conventions, beam-current, emittance and
   luminosity channels, reaction-product detectors with
   centre-of-momentum kinematic accounting, and continuous-run clock
   identities with declared bunch-level resolution.
5. **Solver, evidence, and control-contract boundary** — versioned seams
   towards `SCPN-FUSION-CORE`, review-only semantics towards
   `SCPN-PHASE-ORCHESTRATOR`, and the device-owned CONTROL adapter
   specification towards `SCPN-CONTROL`.

## Position in the SCPN ecosystem

```text
SCPN-BEAM-TARGET-CORE (device truth: beam-kinematics policy, run
                       lifecycle, luminosity/yield accounting, safety
                       envelope, adapter spec)
   │  optional versioned solver seams (none active)
   ├──────────────► SCPN-FUSION-CORE      (solver mathematics, evidence)
   │  typed review-only semantics
   ├──────────────► SCPN-PHASE-ORCHESTRATOR (semantics, comparability)
   │  device-owned adapter (specification only; no implementation)
   ├──────────────► SCPN-CONTROL          (admission; sole ControlAction author)
   │  derived portfolio descriptor (not_federated)
   └──────────────► SCPN-STUDIO           (catalogue, evidence UI, gating)

SCPN-CONTROL ──admitted ControlAction──► independent machine protection
                                          (final veto) ─► plant actuators
```

## Repository layout

| Path | Role |
|---|---|
| `reactor-domain.json` | portable source of project identity and contracts |
| `studio/portfolio-descriptor.json` | derived Studio descriptor, `not_federated` |
| `capability-inventory.json` | generated, truthfully empty inventory |
| `docs/CONTROL_ADAPTER_SPECIFICATION.md` | device-owned adapter contract |
| `docs/THREAT_MODEL.md` | assets, trust boundaries, misuse paths |
| `docs/adr/0001-repository-boundary.md` | boundary decision record |
| `tools/` | validators, derivation tools, preflight orchestrator |
| `tests/` | statement- and branch-complete tests for `tools/` |
| `.github/workflows/` | read-only CI definitions (no publication) |

## Contract surfaces and versioning

- `reactor-domain.json` follows schema `scpn.reactor-domain.v1`; unknown
  schemas are rejected by consumers.
- The Studio descriptor is derived deterministically and embeds the
  manifest's SHA-256; manual edits are detected as drift.
- The CONTROL adapter contract is specification-only at `0.1.0-spec`.
- SPO binding is fixed to reactor registry `1.0.0`, digest
  `786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090`.

## What would change this architecture

Acceptance of a FUSION solver seam through the family migration gate,
ratification of an SPO `ControlIntent`-class contract, or Studio federation
after a real capability passes producer and consumer gates — each recorded
as a versioned contract change in a new ADR.
