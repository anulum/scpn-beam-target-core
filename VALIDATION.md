<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Beam Target Core — VALIDATION
-->

# Validation

Every gate currently active in this repository, with its exact scope,
followed by the evidence record of each implemented capability.

## Local gates

| Gate | Command | Scope |
|---|---|---|
| Lint | `ruff check .` | all Python under `src/`, `tools/`, and `tests/` |
| Format | `ruff format --check .` | same scope |
| Typing | `mypy --strict src tools tests` | zero errors, strict mode |
| Tests + coverage | `pytest -q --cov=src --cov=tools --cov-branch --cov-fail-under=100` | 100 % statement and branch coverage of `src/` and `tools/` |
| Domain manifest | `python3 tools/validate_reactor_domain.py reactor-domain.json` | schema, registry version/digest, exact configuration set, capability inventory shape and ceiling rule, safety boundary |
| Studio descriptor | `python3 tools/derive_studio_descriptor.py --check` | committed descriptor byte-identical to a fresh derivation |
| Capability inventory | `python3 tools/generate_capability_inventory.py --check` | committed inventory byte-identical to a fresh generation |
| Licensing | `reuse lint` | REUSE 3.x compliance of the full tree |
| Workflow lint | `actionlint` | all files under `.github/workflows/` |
| Workflow modularity | `python3 tools/audit_workflows.py` | distributed workflow inventory: single ownership per job, coordinator/gate contract, action pinning, size ceilings |
| Documentation | `python3 tools/preflight.py --only docs` | UTF-8 readability and relative-link integrity of every Markdown file |
| Orchestrated | `python3 tools/preflight.py` | fail-closed run of all gates above |

## Workflow gates

Definitions are present in-repository; they run on the hosted platform
only once a remote exists under separate owner authority.

The hosted surface is modular: `ci.yml` is a coordinator that carries
only trigger policy, two reusable-workflow calls, and one stable
fail-closed `gate` job aggregating every category (failure,
cancellation, and unexpected skips all fail the gate). Every job is
declared and owned exactly once in the versioned inventory
`.github/workflow-inventory.json`, which the workflow-modularity guard
verifies locally and in hosted CI.

| Workflow | Purpose |
|---|---|
| `ci.yml` | coordinator and stable required gate |
| `reusable-static-policy.yml` | lint, format, typing, domain policy, workflow guard |
| `reusable-tests.yml` | tests with complete statement and branch coverage |
| `pre-commit.yml` | exact pre-commit parity |
| `codeql.yml` | Python code scanning |
| `security-audit.yml` | secrets, dependency, licence, and workflow policy |
| `docs.yml` | strict documentation and link validation, no deployment |
| `sbom.yml` | reproducible dependency inventory, no release |
| `scorecard.yml` | read-only supply-chain analysis |

## Shared ecosystem gate

From the monorepo root:

```bash
python3 agentic-shared/scripts/repository_tier0_scaffold_audit.py \
  03_CODE/SCPN-BEAM-TARGET-CORE --json
```

proves the Tier-0 local-scaffold machine profile (required and forbidden
paths, Git/remote boundary, workflow pins and permissions, badge non-claims,
JSON integrity, defensive ignore rules).

## Device configuration model

Evidence record of the `device_configuration_model` capability
(`computational_prototype`; design record: `docs/adr/0002-device-configuration-model.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Validated frozen parameter objects (`BeamLine`,
  `DeviceConfiguration`) rejecting non-finite values, non-positive
  extents, and the hard beam-line-count class invariant (one line for
  `beam_target`, two for `colliding_beam`) — every rejection branch is
  tested.
- The nonrelativistic equal-mass centre-of-mass relations (`E/2` fixed
  target, `2E` symmetric collider) as documented derived quantities,
  with an advisory finding outside the documented light-ion
  cross-section window `[10, 300] keV` (D-T peak near 64 keV c.m.;
  Bosch & Hale, Nucl. Fusion 32 (1992) 611), reported and never
  clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.
- A data-only pin equality check binding the model to the SPO reactor
  registry version and digest declared in `reactor-domain.json`.

Bounded claims — what is NOT claimed:

- No parameter set describes, approximates, or validates any real
  machine; every exercised parameter set is a synthetic test fixture.
- The estimates are advisory regime checks, not luminosity, yield, or
  energy-balance results; no benchmark, dataset, solver, controller, or
  experimental correlation exists in this repository.

## Diagnostic and clock semantics

Evidence record of the `diagnostic_clock_semantics` capability
(`computational_prototype`; design record: `docs/adr/0003-diagnostic-clock-semantics.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- The nullable `timing_uncertainty_s` member, declared `null` on every
  channel because no event-relative candidate is applicable here; a
  non-null value is refused. This keeps the channel shape identical across
  the portfolio under envelope 1.1.0.
- Validated frozen declaration objects (`ClockModel`,
  `DiagnosticChannelPlan`, `DeferredCandidate`, `DiagnosticPlan`)
  rejecting catalogue misalignment: inapplicable candidates,
  inadmissible carriers, evidence-vocabulary mismatches, incompatible
  clock kinds, Nyquist violations, and incomplete candidate coverage —
  every rejection branch is tested.
- A data-only pin (`ObservabilityBinding`) to the SPO
  observability-profile catalogue release `1.0.0`
  (`d70c0de696534e5a77066ef8420cf7ca17bc4d7321984b0ac83523dbc1dce609`),
  bound in turn to reactor registry `1.0.0`; a plan pinned to any other
  release is rejected.
- A reference plan mirroring canonical practice with synthetic
  declarations: an RF cavity/bunch-phase reference (direct cyclic
  against the facility clock), a target-outcome set (noncyclic against
  the beam-gate epoch), and the model-owned synthetic oscillator
  (simulation clock).
- A documented advisory band check with its source stated in the code:
  the common accelerator RF cavity range 10 MHz–3 GHz (Wangler, RF
  Linear Accelerators, 2nd ed., 2008); findings are reported, never
  clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.

Bounded claims — what is NOT claimed:

- No channel describes a real diagnostic, measurement, or facility;
  every plan is a synthetic declaration of HOW evidence slots would be
  bound, marked `synthetic=True` by hard invariant.
- No SPO semantic-profile ingress is declared; the profile registry
  `ingress_state` for this device family remains `not_declared`, and
  no adapter, producer, or handoff exists in this repository.

### Portable plan envelope

The `diagnostic_clock_semantics` capability additionally exercises a
producer-owned portable envelope
(`src/scpn_beam_target_core/plan_envelope.py`,
`scpn.reactor-diagnostic-plan-envelope.v1` version `1.0.0`): one
canonically serialised object carrying the exact project identity and
owned configurations, the capability and its maturity, the
synthetic/review-only/non-actuating statements, both SPO registry pins,
the SHA-256 digest of the inner canonical plan, the producer revision,
and fixed no-observation/no-control non-claims. The committed immutable
fixture (`tests/data/plan_envelope_fixture.json`, byte hash pinned in
the tests) is verified together with positive, tamper, wrong-project,
wrong-configuration, registry-drift, duplicate-member, and non-finite
rejection paths, all under the 100 % coverage gate. The envelope claims
nothing beyond the enveloped synthetic declaration.

### Typed frames, clock relations, and acquisition geometry

The deepened model adds typed reference frames (per-repository allowed
`FrameKind` subset; every noncyclic `coordinate_frame` binding must
reference a declared frame), clock synchronisation relations
(synthetic offset/uncertainty BOUNDS between declared non-simulation
clocks with an explicit method statement — no correlation evidence is
claimed and no clock is mapped to physical wall time), and per-channel
acquisition windows and element counts with device-cited advisory
scales. Both decoders are hardened per the SPO intake architecture:
recursive exact-key refusal in every nested entry, duplicate-member
refusal, and byte-canonical refusal (a document that is not exactly
canonical bytes is rejected). The envelope is `1.1.0`, adding
`manifest_sha256` — the SHA-256 of the committed canonical
`reactor-domain.json` — verified in tests against the committed file.
All declarations remain synthetic; nothing here observes or controls
anything.

### Signal inventories, frame transformations, and clock topology

The depth slice (envelope `1.2.0`; a `1.1.0` document is refused by the
`1.2.0` codec and vice versa — no defaults, no cross-version coercion;
`1.1.0` remains historical custody at the consumer) adds three typed
declaration surfaces, every branch under the 100 % statement-and-branch
gate:

- A per-channel **signal inventory** (`SignalDeclaration`: identifier,
  quantity, unit, role, description). Hard rules: non-empty, unique and
  sorted; exactly one `carrier`; no `timing_marker` (no
  event-relative candidate is applicable); numerical-only
  channels declare a single `phase`/`rad` carrier. Quantity and unit are
  declared tokens — no SI or UCUM validation is performed or claimed —
  and no declaration creates or overrides a candidate, carrier,
  observation, or phase: the candidate profile stays authoritative.
- **Frame transformations** (`FrameTransformation`) between declared
  frames: kind admissibility fixed by frame-kind pair (`flux_mapping`
  for machine↔flux, flux↔Boozer, field-line↔machine; `projection` for
  blanket↔machine; `rigid` for chamber↔beamline), `equilibrium_dependent`
  exactly for flux mappings, at most one transformation per frame pair,
  sorted by source then target, and — with two or more frames — a
  connected transformation graph. Methods are declarations;
  `evidence_claimed` is always `False`.
- A **clock topology** (`ClockDomain`, `ClockTopology`): every physical
  clock in exactly one domain, the simulation clock in none; a domain
  holding a facility clock is rooted there, otherwise at its shot-event
  epoch; every non-root member declares a relation to its root; every
  non-reference root declares a relation to the reference root (star);
  relations must not form a cycle. The reference plan declares one
  domain (`clk_facility` root, `clk_shot` member); multi-domain rules
  are exercised by test-constructed plans. Scopes are declarations;
  `mapping_state` stays `unmapped`.

## Level-0 device physics

Evidence record of the `level0_device_physics` capability
(`computational_prototype`; design record:
`docs/adr/0005-level0-device-physics.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- The Duane total cross section of the six principal light-ion reactions,
  with the coefficients the 2019 NRL Plasma Formulary tabulates on
  page 44. Its energy argument is the incident-ion energy with the target
  at rest, which is the frame the fit was made in.
- The record evaluating that fit at the **equivalent stationary-target
  energy** rather than at the declared beam energy, and carrying both.
  Under the equal-mass kinematics the configuration uses, a colliding-beam
  machine reaches the centre-of-mass energy of a stationary-target machine
  at four times its own beam energy; the ratio is exact and asserted as an
  equality.
- Which of the two cross sections is larger is **not** fixed, and both
  directions are exercised: a colliding-beam configuration below the
  resonance moves towards it and gains, one already at it is thrown past
  and loses.
- The centre-of-mass energy taken from the configuration's own method
  rather than restated, so the two cannot drift apart.
- The equal-mass approximation reported beside its exact value: 1.669 for
  D-T, from the formulary's own printed masses, against the 2 in force.
- The beam bookkeeping: ion rate from current, and power from energy and
  current with the elementary charge cancelling. A singly charged beam of
  one milliampere at one kiloelectronvolt carries exactly one watt, and
  that is asserted as an equality because the cancellation is algebraic.
- Fail-closed refusal of every input outside its documented interval, each
  naming its field. Nothing is clamped. A neutral or negative charge state
  is refused rather than reinterpreted.
- The Gamow boundary at 0.0043 keV tested from both sides: zero below it,
  positive above.
- Canonical serialisation with a SHA-256 digest, its idempotence under
  re-canonicalisation, and its movement under a changed configuration.

Anchors — a cross-check inside one filed document. The formulary prints
the Duane coefficients and, further down the same page, a table of
Maxwellian-averaged D-T reaction rates; one implies the other, so
averaging the fit verifies the transcription of all six coefficient
tuples.

| Printed | Where | Recovered |
|---|---|---|
| ten D-T reaction rates, 1 keV to 1000 keV | page 44 table | every one, rounding to the printed two significant figures |
| `m_e/m_D` as `2.72e-4` and as `1/3670` | page 44 | each recovers the other |
| `m_e/m_T` as `1.82e-4` and as `1/5496` | page 44 | each recovers the other |
| the printed square roots `1.65e-2 = 1/60.6` and `1.35e-2 = 1/74.1` | page 44 | both, from the ratios |

The residual against the reaction-rate table is at most 1.4 % and is the
table's own rounding, not quadrature error: fifty times as many intervals
move the answer by less than a part in ten thousand, and that is tested.

No parameter set describes any real machine, and no reaction rate, yield,
gain or breakeven statement follows from the record — no beam stopping,
target density or target thickness is modelled anywhere.

## Device 3D model

Evidence record of the `device_3d_model` capability
(`computational_prototype`; design record:
`docs/adr/0006-device-3d-and-cad-models.md`).

Consumer contract, written from this repository's own code:
`docs/DEVICE_3D_MODEL_CONTRACT.md`.

**No dimension in this capability reproduces a published value.** The two
works this repository cites for its beam physics are paywalled and neither
is on file; the one filed source prints no geometry. Every length is
declared, the fixtures say so, and no test claims otherwise.

What is exercised, all under the 100 % statement-and-branch coverage gate:

- A body set that **depends on the configuration**: a beam-target device
  is a beam pipe, a solid target and the dump behind it; a colliding-beam
  device is two beam pipes and nothing between them. Its beams are each
  other's target and they meet in vacuum, so neither an interaction region
  nor the beam itself carries a body.
- Both directions of that rule refused rather than defaulted: a
  beam-target device given no target assembly, and a colliding-beam device
  given one.
- A target or dump **below** the bore radius refused, naming both fields
  and printing both values — a body the beam passes around does not
  intercept it — while one exactly equal to the bore is admitted, because
  it intercepts everything the pipe can deliver.
- The two beam lines of a collider built as mirror images: equal volumes,
  z extents that are negatives of each other, and neither reaching the
  interaction point.
- The target at the origin and the dump immediately behind it, downstream
  being the positive direction.
- The tessellation losing exactly the inscribed polygon and nothing else,
  at 8, 64 and 256 segments.
- Fail-closed refusal of an invalid segment count and of a record built
  with the wrong bodies, the wrong order, or an unknown identifier.
- Canonical serialisation with a SHA-256 digest that moves with the
  envelope, the assembly, the segment count and the configuration; a
  colliding-beam record carries `null` for the target digest rather than
  omitting or inventing it.

## Device CAD model

Evidence record of the `device_cad_model` capability
(`computational_prototype`; design record:
`docs/adr/0006-device-3d-and-cad-models.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- The same configuration-dependent body set as exact B-rep solids through
  the shared library's `cad` group, each checked fail-closed by the
  library's evidence kernel against its analytic closed forms and against
  its tier-G1 twin, and exported as normalised STEP bytes with a digest.
- The target rules enforced at **both** tiers, not only where the meshes
  are built.
- **Which deflection binds, measured for this family.** At the declared
  `1e-5 m` and `0.1 rad` the **linear** criterion binds: doubling the
  angular deflection changes no deficit at all, and the three bodies of a
  beam-target build show three different deficits because their radii
  differ. That is the opposite of the tokamak family, where one angular
  step gave every body the same deficit.
- The deflections chosen for the **tightest bound that still passes**
  rather than the widest margin: every declared bound is under 0.07 % and
  every body clears it by more than twenty times. A coarser linear
  deflection was measured to give margins of a hundred and fifty times on
  a bound ten times looser, which claims less.
- The two beam lines of a collider sharing one bound exactly and one
  deficit to within 1.5e-9 relative — they sit at opposite ends of the
  axis, so their volume sums accumulate differently.
- Fail-closed refusal of a non-positive deflection, of a manifest of the
  wrong schema or body count, of bodies out of order, and of an unknown
  identifier.
- STEP bytes present, their digest matching them, and the two
  configurations producing different bytes.

Determinism of the STEP bytes is claimed within one pinned back-end
environment only, never across back-end versions. No body is an
engineering model, no fabrication tolerance is carried, and no value
describes any real machine or facility.
