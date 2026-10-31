<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Beam Target Core — CHANGELOG
-->

# Changelog

## [Unreleased]

### Fixed

- Discrete inputs are integers or are refused with the family error before
  any computation: the ion charge number (`require_charge_number`,
  `ion_rate_per_s`, `beam_power_w`, `BeamInputs`), the quadrature sample
  count of the thermal average, the beam-line count at construction (the
  record decoder already refused) and the tessellation segment count.
  Booleans, integral and fractional floats, NaN and infinity used to be
  accepted or to fail with a bare `TypeError`; a charge of `True` or `1.5`
  produced a rate. Valid integers keep their results.

### Security

- `configuration_from_bytes` refuses duplicate JSON members and any document
  that is not byte-for-byte the canonical serialisation, as the
  diagnostic-plan and plan-envelope parsers already did; a duplicate member
  was resolved last-wins.
- All three public parsers report JSON nested deeper than the decoder can
  follow as their own error type; a `RecursionError` previously escaped
  them. Property and fuzz tests cover arbitrary bytes, single-byte
  mutations, field substitutions and overflowing number literals.

### Added

- Level-0 physics benchmark (`benchmarks/level0_physics.py`) after the
  ecosystem standard, with a committed local smoke artefact, and
  `docs/benchmarks.md` stating the computation contract of every kernel and
  the backend status (Python floor only; the native row is reported as
  unavailable). `benchmarks/` joins the strictly typed cohort in CI, Make,
  pre-commit and preflight.
- `tools/check_commit_trailers.py --audit-range REV_RANGE` checks the
  messages of existing commits read-only with the commit-msg rules; exit `2`
  when the range cannot be read.
- README badge block for the evidence this repository has earned: the CI,
  CodeQL, pre-commit, security-audit and docs workflows on `main`, the
  AGPL-3.0-or-later licence, the commercial licence route and GitHub
  Sponsors, bound by a contract test; unearned services stay forbidden.
- An installed-wheel job in the required CI gate: the wheel is built
  without build isolation from hash-locked `setuptools` and `wheel`
  (`requirements-build.txt`), installed into clean base and CAD environments
  and exercised from outside the checkout by `tools/installed_package_check.py`.

### Changed

- **Level-0 record schema `1.1.0`** (`scpn.beam-target-level0-physics.v1`):
  the record carries its declared inputs (reaction and charge number), so
  it replays from the configuration document and itself alone.
  `beam_inputs_from_record` and `replay_level0` are new public functions;
  `replay_level0` refuses another schema or version, another configuration
  and any record that does not recompute to the same bytes. The bytes and
  digest of every level-0 record change; 1.0.0 records are refused, not
  upgraded (ADR 0005 addendum).

- The formulary citations name the right page: the Duane coefficients and
  the thermal-average table are on page 45, not 44 (the fit and the mass
  ratios are on 44). The claim that averaging verifies all six coefficient
  tuples is corrected: it verified D-T only. Two new anchors recover the
  printed D-D (both branches) and T-T columns, so four tuples are now
  verified by the document; D-He3 and T-He3 remain transcriptions. No value
  changes.

- The physical constants in `physics/cross_section.py` name their edition:
  the five-figure CODATA 1986 values the 2019 NRL Plasma Formulary prints
  (p. 14) and the three-figure mass ratios of its p. 44, each with its
  offset from CODATA 2022 and its effect on the derived masses, ion rate and
  lab-to-centre-of-mass ratio. No value, output or digest changes; a test
  binds every edition and offset.

- `scpn_beam_target_core.observability` is now a package with one module
  per responsibility — vocabulary, catalogue binding, frames, clocks, signals
  and channels, plan composition, record parsing — behind the unchanged
  public import path. The 33 public names, canonical plan bytes and refusal
  behaviour are unchanged.

- The documentation gate reads only files git would publish, so a
  git-ignored private tree is never link-checked (it failed the gate locally
  while passing in CI, where that tree is absent). Hooks without their own
  stage list run before a commit and before a push only; commit-msg runs the
  trailer guard alone.
- Local and hosted gates check the same cohorts: `make typecheck` now checks
  `src/` as CI does, `make test` measures `src/` as CI does, `conftest.py`
  joins the typed cohort everywhere, and `make validate` runs the workflow
  audit. A parity test binds the make targets and the preflight plan to the
  hosted workflows, and an enrollment test maps every tracked file to exactly
  one gated surface.

- Install every CI dependency from hash-locked requirement sets with
  `--require-hashes`: the development toolchain, the CAD extra, the audit
  and inventory tools, and the first-party kernel library by source-archive
  digest at the commit pinned in `pyproject.toml`. `make lock` regenerates
  the sets; the package itself installs with `--no-deps`. Toolchain, action
  and interpreter pins move to their newest releases.
- Align Ruff, coverage and CycloneDX with the current compatible validation
  chain. Keep optional CAD on Trame 3 until the pinned kernel dependency is
  migrated with its full device contract; the current VTK adapter requires
  `trame-client<4`.

### Added

- Diagnostic-plan depth: per-channel signal inventories, frame
  transformations with a fixed kind-admissibility table and connectivity
  rule, and a clock topology partitioning the physical clocks into rooted
  domains with a star of relations to the reference root. Envelope
  `scpn.reactor-diagnostic-plan-envelope.v1` bumped to `1.2.0`; the
  fixture is regenerated from the public surface and re-pinned. All new
  members are declarations: no observation, phase, mapping, or control
  authority is created.

### Fixed

- Added the nullable `timing_uncertainty_s` channel member (always `null`;
  no event-relative candidate is applicable) so the diagnostic-plan
  channel shape matches the portfolio-uniform envelope 1.1.0 contract;
  fixture regenerated and re-pinned.

### Added

- Local gate parity with the wider ecosystem: the pre-commit chain now
  also runs REUSE licensing compliance and a typographical checker
  (`_typos.toml` carries the deliberate reactor vocabulary), and adds
  the upstream YAML, TOML, large-file and private-key guards. Licensing
  and spelling were previously verified only in hosted CI, so a broken
  REUSE annotation — including the aggregate annotation that covers the
  binary header images — could reach a push before being caught.
- Generated repository header artwork: `docs/assets/generate_header.py`
  renders three deterministic 1280x640 images from the repository's own
  domain surface (the beam on a stationary target used by the README,
  the beam-line invariant, and the cross-section energy window).
- Modular hosted-workflow surface per the ecosystem workflow-modularity
  standard: `ci.yml` reduced to a coordinator with a stable fail-closed
  `gate` job, single-responsibility reusable workflows for static
  analysis/repository policy and for tests, a versioned machine-readable
  inventory (`.github/workflow-inventory.json`,
  `scpn.workflow-inventory.v1` `1.0.0`), and a fail-closed modularity
  guard (`tools/audit_workflows.py`) enforced locally (preflight gate,
  pre-commit hook) and in hosted CI. The duplicate documentation-links
  step was removed from the CI chain; `docs.yml` remains the single
  owner of documentation validation.

- Typed reference frames, clock synchronisation relations (synthetic
  bounds only; no correlation evidence claimed), and per-channel
  acquisition windows and element counts in the diagnostic model;
  hardened decoders (recursive exact-key, duplicate-member, and
  byte-canonical refusal in both codecs); envelope `1.1.0` adding
  `manifest_sha256` over the committed canonical `reactor-domain.json`
  (fixture regenerated; byte hash re-pinned in tests).

- Portable diagnostic-plan envelope
  (`src/scpn_beam_target_core/plan_envelope.py`,
  `scpn.reactor-diagnostic-plan-envelope.v1` version `1.0.0`): a
  producer-owned, canonically serialised wrapper carrying project
  identity, exact owned configurations, capability and maturity,
  synthetic/review-only/non-actuating statements, both SPO registry
  pins, the inner plan's SHA-256, the producer revision, and fixed
  no-observation/no-control non-claims; strict parsers refuse unknown,
  duplicate, and non-finite members, and an immutable committed fixture
  exercises the exchange end to end.

- Diagnostic and clock semantics model
  (`src/scpn_beam_target_core/observability.py`), the second implemented
  capability at `computational_prototype`: frozen clock, channel,
  deferral, and plan objects aligned fail-closed with the pinned SPO
  observability-profile catalogue (candidate applicability, carrier
  admissibility, exact class-fixed evidence vocabularies, clock-kind
  compatibility, Nyquist bounds); a cited advisory RF band check;
  canonical serialisation with SHA-256 digests and strict NaN-rejecting
  round-trip parsing (design record
  `docs/adr/0003-diagnostic-clock-semantics.md`).

- Device configuration model (`src/scpn_beam_target_core/`), the first implemented
  capability at `computational_prototype`: validated frozen parameter
  objects with device-specific invariants and documented, cited
  consistency estimates; canonical serialisation with SHA-256 digests
  and strict NaN-rejecting round-trip parsing; a data-only pin to the
  SPO reactor registry; and the reactor-domain validator branch
  enforcing populated capability inventories with the ADR 0002
  evidence-maturity ceiling rule (design record
  `docs/adr/0002-device-configuration-model.md`).

- Architecture-only repository scaffold: governance, security, licensing,
  REUSE metadata, contribution and support policies, and citation metadata.
- Machine-readable domain manifest `reactor-domain.json` binding the project
  to SCPN Phase Orchestrator reactor registry `1.0.0`
  (configurations `beam_target`, `colliding_beam`).
- Device-owned CONTROL adapter specification and threat model.
- Derived Studio portfolio descriptor (`not_federated`) and generated
  capability inventory (zero implemented capabilities).
- Validation tooling: domain-manifest validator, descriptor derivation and
  inventory generation with drift checks, and a fail-closed preflight
  orchestrator, each with statement- and branch-complete tests.
- Continuous-integration, code-scanning, security-audit, documentation,
  SBOM, pre-commit, and Scorecard workflow definitions (read-only
  permissions; no publication or deployment workflows).

### Changed

- Studio portfolio descriptor schema ratified at version 1.1.0 after
  downstream review, before any consumer adoption (1.0.0 superseded
  unconsumed): canonical JSON Schema published in-repository with a strict
  unknown-field policy, explicit source repository, nullable lifecycle
  evidence pointer, nullable versioned control-intent reference, ratified
  capability item shape, and a machine-protection object (independent
  final-veto owner with availability `not_assessed`) replacing the former
  boolean flag.
