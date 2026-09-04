<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Beam Target Core — device model contract
-->

# Device model contract

What a consumer of this repository's device models may rely on, written
from the code rather than from a template. Design record:
`docs/adr/0006-device-3d-and-cad-models.md`.

## The one thing to read first

**No dimension in these models reproduces a published value.** The two
works this repository cites for its beam physics are paywalled and neither
is on file; the one filed source prints no geometry. Every length is a
declaration. The other families in this group carry printed radii their
bodies recover; this one does not, and a consumer must not treat any
number here as an anchor.

## The two tiers

| Tier | Record | Schema | Built from |
|---|---|---|---|
| G1, tessellated | `DeviceModel3D` | `scpn.beam-target-3d-model.v1` 1.0.0 | the library's `geometry` group |
| G2, B-rep | `DeviceModelCAD` | `scpn.beam-target-cad-model.v1` 1.0.0 | the library's `cad` group |

Both are built from the same validated `DeviceConfiguration`,
`BeamlineEnvelope` and — where the configuration has one — `TargetAssembly`.
Tier G2 is optional: it needs the `cad` extra, and every other capability
of this package works without a B-rep back-end.

## Units and frame

| Quantity | Value |
|---|---|
| length | metre |
| handedness | right |
| axis | `z` along the beam axis, pointing downstream |
| origin | `z = 0` at the interaction point |

## The bodies depend on the configuration

| Identifier | Bodies, in this order |
|---|---|
| `beam_target` | `upstream_beamline`, `target`, `beam_dump` |
| `colliding_beam` | `upstream_beamline`, `downstream_beamline` |

| Name | Role | Material token |
|---|---|---|
| `upstream_beamline` | `beamline` | `beam_pipe` |
| `downstream_beamline` | `beamline` | `beam_pipe` |
| `target` | `target` | `target_solid` |
| `beam_dump` | `dump` | `dump_absorber` |

The set and its order are fixed per identifier and checked at construction
on both tiers. A record whose bodies are reordered, renamed, or belong to
the other configuration is refused.

**A colliding-beam device has no target body and no interaction-region
body.** Its beams are each other's target and they meet in vacuum; what is
not a solid is not drawn. Neither the beam itself nor the bore is a body
either — the bore is the space a beam would occupy.

## Where each dimension comes from

The configuration owns the beam — kinetic energy, current, and how many
lines there are — and no length at all. The `BeamlineEnvelope` owns the
bore radius, the wall thickness, the pipe length and the interaction gap.
The `TargetAssembly` owns the target's radius and thickness and the dump's
radius and length.

Three relations are refused, each naming both fields and printing both
values:

- a `beam_target` device given no target assembly;
- a `colliding_beam` device given one;
- a target or dump radius **below** the bore radius, where the beam would
  pass around it. Equal to the bore is admitted: such a body intercepts
  everything the pipe can deliver.

## Exports and identity

Both records serialise canonically (sorted keys, minimal separators, a
trailing newline, NaN and infinity refused) and carry a SHA-256 digest of
those bytes. Each binds the digests of the configuration, the envelope and
the target assembly; for a colliding-beam device the target digest is
`null` rather than absent or invented. Tier G2 additionally carries
normalised STEP bytes with their own digest and the versions of the pinned
back-ends.

## Declared limits

- **STEP determinism is claimed inside one pinned back-end environment
  only**, never across back-end versions. The record carries the versions.
- The faceting comparison runs at a linear deflection of `1e-5 m` and an
  angular deflection of `0.1 rad`, against an 8-segment tier-G1 reference.
  **Both are measured for this family, and the linear one binds**: at this
  setting the two angular values tried give the same answer to four
  figures, and the three bodies of a beam-target build show three
  different deficits because their radii differ.
- The setting was chosen for the **tightest bound that still passes**, not
  the widest margin. Every declared bound is under 0.07 %, and every body
  clears it by more than twenty times. A coarser linear deflection would
  report margins of a hundred and fifty times on a bound ten times looser,
  which claims less.
- The evidence kernel **refuses** a body that misses its bound, naming the
  body, and refuses a non-positive deflection, naming the deflection.

## Non-claims

- The beam pipe is one plain tube. No magnet, vacuum pump, diagnostic
  port, flange, bellows or support is modelled.
- No body is an engineering model; no material property, load, field, dose
  or activation quantity is carried, and no fabrication tolerance.
- No value describes or validates any real machine or facility, and none
  reproduces a published dimension.
