<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Beam Target Core — README
-->

# SCPN Beam Target Core

Governed device-family repository for beam-target and colliding-beam fusion
systems within the SCPN Reactor Systems Research Group. This repository is
the designated owner of device-level truth for the two beam-target
configurations of the SCPN Phase Orchestrator reactor registry:
`beam_target` (energetic beam on target) and `colliding_beam`
(counter-propagating particle beams).

**Evidence maturity: `computational_prototype`** (per-capability; ADR 0002).
Two capabilities are implemented: the device configuration model —
validated parameter objects with documented consistency estimates,
canonical serialisation, and a data-only SPO registry pin
(evidence: `VALIDATION.md#device-configuration-model`) — and the
diagnostic and clock semantics model — synthetic channel and clock
declarations aligned fail-closed with the pinned SPO observability
catalogue (ADR 0003, evidence:
`VALIDATION.md#diagnostic-and-clock-semantics`). No parameter set or
channel describes any real machine or diagnostic; the claim inventory
is empty and verified by the domain validator.

## Scope

This repository owns, for the beam-target device family:

- the device boundary: plant and experiment truth, run lifecycle, and
  configuration policy for non-thermal fusion systems in which reaction
  kinematics are set directly by accelerated beams — an energetic beam on
  a fixed or flowing target, or two counter-propagating beams brought to
  collision — without imploding or magnetically confining a thermal
  plasma;
- beam-kinematics semantics as device truth: beam-energy and luminosity
  declarations, target-state declarations (solid, gas, plasma-loaded),
  centre-of-momentum reaction-rate accounting, and the honest energy-
  balance declarations this family requires (stopping-power and
  scattering losses against fusion output);
- diagnostic semantics, reference frames, and clock identity declarations;
- actuator-response model boundaries and the declared safety envelope;
- the device-owned CONTROL adapter specification;
- the binding to the SCPN Phase Orchestrator reactor registry
  (version `1.0.0`, digest
  `786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090`);
- the machine-readable domain manifest `reactor-domain.json` and the derived
  Studio portfolio descriptor (integration state `not_federated`).

## Explicit exclusions

- **Beam-driven implosion ICF**: `SCPN-ICF-BEAM-CORE`.
- **Dense plasma focus** (internally generated beam-target component):
  `SCPN-DENSE-PLASMA-FOCUS-CORE`.
- **Electrostatic potential-well devices** (recirculating-ion IEC):
  `SCPN-IEC-CORE`.
- **Solver mathematics and validation evidence**: `SCPN-FUSION-CORE` until
  an exact surface passes the reactor family migration gate; no solver code
  exists in, or was copied into, this repository.
- **Typed signal semantics and comparability**: `SCPN-PHASE-ORCHESTRATOR`
  (review-only output; never actuation).
- **Control admission and action formation**: `SCPN-CONTROL` is the sole
  software authority that forms an admitted `ControlAction`.
- **Machine protection**: independent systems retain the final veto.
- **Portfolio presentation, identity, entitlement, and execution gating**:
  `SCPN-STUDIO`.

## Non-claims

This repository is not machine-ready, not safety-certified, and not
reactor-ready. It contains no implemented solver, no controller, no
benchmark result, no experimental correlation, no dataset, and no published
artefact, and no parameter set describes or validates any real machine. Accelerator-architecture, target-state, and fuel
choices are configuration facets, not separate claims — and no
energy-gain claim of any kind is made or implied for this family. No capability has reached any
evidence-maturity state beyond `computational_prototype`.

## Architecture

The five-surface boundary and the position of this repository in the SCPN
ecosystem are defined in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and
fixed by
[`docs/adr/0001-repository-boundary.md`](docs/adr/0001-repository-boundary.md).
The threat model is in [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md); the
CONTROL adapter contract is in
[`docs/CONTROL_ADAPTER_SPECIFICATION.md`](docs/CONTROL_ADAPTER_SPECIFICATION.md).

## Validation

Every gate currently active in this repository is listed in
[`VALIDATION.md`](VALIDATION.md). The local sequence is:

```bash
make lint        # ruff check + ruff format --check
make typecheck   # mypy --strict tools tests
make test        # pytest with 100 % statement and branch coverage on tools/
make validate    # domain manifest, descriptor, and inventory checks
make preflight   # the full fail-closed gate sequence
```

## Security

See [`SECURITY.md`](SECURITY.md) for the supported states and the private
reporting route (protoscience@anulum.li).

## Licensing

AGPL-3.0-or-later for the public repository, with a commercial licence
available (see [`NOTICE.md`](NOTICE.md)). Licence texts are under
[`LICENSES/`](LICENSES/); machine-readable licensing metadata follows
REUSE 3.x (`REUSE.toml`).

## Citation

Citation metadata is provided in [`CITATION.cff`](CITATION.cff). No release,
version, or DOI exists yet; cite the repository state you inspected.
