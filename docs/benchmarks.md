<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Beam Target Core — Benchmarks and computation contract
-->

# Benchmarks and computation contract

## Computation contract

The level-0 physics of this package is a set of closed forms evaluated in
IEEE-754 binary64 on the Python floor (energies in keV, currents in mA,
cross sections in barn, rates in cm³/s, power in W):

| Module | Kernels | Operations |
|---|---|---|
| `physics/cross_section.py` | Duane total cross section `[A5 + A2 / ((A4 - A3 E)^2 + 1)] / (E (exp(A1 / sqrt E) - 1))`; the Maxwellian average used only to verify the transcription | `* / - +`, `sqrt`, **`expm1`**, the square `x ** 2` (platform `pow`); the average adds **`exp`**, **`pow(x, -1.5)`**, `sqrt`, `pi` |
| `physics/beam.py` | ion rate `I / (Z e)`, beam power `E I / Z` | `* /` |
| `configuration.py` | equal-mass centre-of-mass energy | `* /` |
| `physics/level0.py` | the composed record with canonical bytes and SHA-256 digest; `replay_level0` | composition, JSON serialisation |

Every input outside its domain is refused with the package error, never
clamped; discrete inputs are integers. The square root is correctly
rounded by IEEE-754; `expm1`, `exp` and `pow` (the square included) are the platform's, which the
standard does not require to be correctly rounded. A native backend that
must agree bit for bit would have to use one deterministic implementation
of each on both sides. The constants and their editions are documented in
`physics/cross_section.py` and bound by tests.

**Backend status.** Python floor only. There is no native crate. Audit
plan Q01 asks for a native path on required numeric paths and allows a
scoped, owner-approved exception for trivial non-hot arithmetic; that
decision is the owner's and is recorded as open in the backlog. The
benchmark marks the native backend as unavailable instead of omitting it.

## Level-0 physics — local workstation (non-isolated)

Artefact: `benchmarks/results/level0_physics.local.json` (schema
`scpn-beam-target-core.level0-physics-benchmark.v1`, generated 2026-10-31T03:25:55.967312+00:00, at commit
`9881ca7e22a3` with the working tree of the landing commit).
Host: 11th Gen Intel(R) Core(TM) i5-11600K @ 3.90GHz, Linux-7.0.0-34-generic-x86_64-with-glibc2.39, Python 3.12.3; load average
at start 3.18 (other sessions were active on the host);
cores not isolated, so treat the numbers as a smoke timing, not a
performance measurement. Parameters: 20000 closed-form points and
2000 records, 3 warm-up passes, 20 timed passes.

### `closed_forms` (six Duane cross sections, ion rate and beam power per point)

| Backend | P50 µs/point | P95 µs/point | P99 µs/point | mean µs/point | throughput points/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 1.994 | 2.381 | 2.920 | 2.087 | 501402 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

### `level0_record` (composed record with canonical bytes per point)

| Backend | P50 µs/record | P95 µs/record | P99 µs/record | mean µs/record | throughput records/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 23.265 | 26.043 | 27.265 | 23.391 | 42983 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

## Regenerate

```bash
.venv/bin/python benchmarks/level0_physics.py --label local
```

The script writes `benchmarks/results/level0_physics.<label>.json` with the
provenance above. A number from a fixed CI runner or isolated cores would
replace the smoke timing here; none is claimed yet.
