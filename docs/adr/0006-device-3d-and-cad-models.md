<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Beam Target Core — ADR 0006
-->

# ADR 0006 — Device 3D and CAD models of a beam line and its target

Status: accepted (2026-09-04). Adds the fourth and fifth implemented
capabilities, `device_3d_model` and `device_cad_model`, under the
evidence-maturity ceiling rule of ADR 0002.

## Context

Two things about this family shape the tier, and both are unusual in this
group.

**There is no printed geometry to anchor on.** The two works this
repository cites for its beam physics — Bosch and Hale, and Wangler — are
both paywalled and neither is on file; Wangler is the one that would have
dimensioned a beam line. The single filed source, the plasma formulary,
prints reactivities, cross-section coefficients and constants, and no
dimensions at all. Every other family in this rollout had a printed radius
or a printed thickness to recover. This one has nothing.

**The two owned configurations are not the same machine.** A beam-target
device fires into something solid; a colliding-beam device has two beam
lines that are each other's target. The configuration already knows this —
`beam_line_count` is one and two — and a geometry that ignored it would
contradict a declaration the repository already validates.

## Decision

**Say plainly that nothing is anchored.** The envelope module, the model
non-claims, the fixtures and this record all state that every length is
declared. A consumer must not read any dimension here as reproducing a
published value. That is worse evidence than the other families carry, and
the honest response is to label it rather than to dress a synthetic number
as an anchor.

**Let the body set depend on the configuration.**

| Identifier | Bodies |
|---|---|
| `beam_target` | `upstream_beamline`, `target`, `beam_dump` |
| `colliding_beam` | `upstream_beamline`, `downstream_beamline` |

A colliding-beam device gets **no target body and no interaction-region
body**, because neither is a solid: the beams meet in vacuum. This is the
same rule the fusion-fission family applies to its vacuum zone — what is
not a solid is not drawn — and it is why the two sets differ in length as
well as in names.

The target assembly is therefore a **separate declaration**, required for
`beam_target` and refused for `colliding_beam`. Both directions are
refusals rather than defaults: supplying a target to a collider would put
a fiction in the record, and omitting one from a beam-target device would
leave the beam firing at nothing.

A target or dump narrower than the beam pipe's bore is refused, naming
both fields and printing both values: a body the beam passes around does
not intercept it. The rule is refusal *below* the bore, not below-or-equal
— a target exactly the width of the bore intercepts everything the pipe
can deliver.

## The faceting deflections, measured for this family

The declared bound is `2 d / r`. Which deflection binds depends on the
device, and this group now holds three different answers; this family is
the third.

Measured over a grid at the reference envelope, whose bore is three
centimetres:

| linear | angular | narrowest margin | cost |
|---|---|---|---|
| 1e-4 | 0.1 | 24x | 3.3 s |
| 1e-4 | 0.02 | 150x | 4.9 s |
| **1e-5** | **0.1** | **24x** | **7.7 s** |
| 1e-5 | 0.02 | 24x | 8.9 s |
| 1e-6 | 0.1 | 15x | 42 s |

At 1e-4 the angular criterion still binds — refining it from 0.1 to 0.02
moves the margin. At 1e-5 it no longer does: the two angular settings give
the same answer to four figures, so the linear criterion has taken over.

**The choice is 1e-5 and 0.1, and it is not the widest margin.** A margin
is only as good as the bound it is a margin on. The 150x row buys its
margin from a bound ten times looser, which claims less; at 1e-5 every
declared bound is under 0.07 % and every body still clears it by more than
twenty times. Refining further to 1e-6 costs six times the wall clock for
a *narrower* margin, because the bound tightens faster than the mesher
improves.

That the linear criterion binds is visible in the record itself: the three
bodies of a beam-target build have different radii and three different
deficits, where the tokamak family's angular-limited build gave every body
the same deficit whatever its radius.

## Consequences

Both capabilities are registered at `computational_prototype` with their
evidence pointers in `VALIDATION.md`, and the package carries 100 %
statement and branch coverage.

This landing gives the repository its first dependency: the shared kernel
library pinned by commit, with the CAD back-end as an optional extra
naming the same commit. Three workflows gain an install step and the test
workflow the system library the mesher links against.

The consumer contract is in `docs/DEVICE_3D_MODEL_CONTRACT.md`, written
from this repository's own constants, and its absence would now fail the
repository contract test.
