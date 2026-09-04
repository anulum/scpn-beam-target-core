# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — tier-G1 device model tests

"""Every branch of the tier-G1 model, and the asymmetry it is built around.

The two owned configurations are not the same machine, and the tests that
matter here are the ones that show the model refuses to pretend they are.
"""

from __future__ import annotations

import hashlib
import json
import math

import pytest

from geometry_fixtures import (
    inscribed_polygon_ratio,
    reference_beamline,
    reference_target,
    synthetic_configuration,
)
from scpn_beam_target_core.errors import DeviceGeometryError
from scpn_beam_target_core.geometry import (
    BODY_BEAM_DUMP,
    BODY_DOWNSTREAM_BEAMLINE,
    BODY_NAMES_BY_IDENTIFIER,
    BODY_TARGET,
    BODY_UPSTREAM_BEAMLINE,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    MODEL_UNITS,
    DeviceModel3D,
    build_device_model,
)

REFERENCE_SEGMENTS = 64


def beam_target_model(segments: int = REFERENCE_SEGMENTS) -> DeviceModel3D:
    """Build the beam-target model."""
    return build_device_model(
        synthetic_configuration("beam_target"),
        reference_beamline(),
        segments,
        reference_target(),
    )


def colliding_model(segments: int = REFERENCE_SEGMENTS) -> DeviceModel3D:
    """Build the colliding-beam model."""
    return build_device_model(
        synthetic_configuration("colliding_beam"), reference_beamline(), segments
    )


@pytest.mark.parametrize("segments", [0, 7, 12, -8])
def test_an_invalid_segment_count_is_refused_under_the_device_error(
    segments: int,
) -> None:
    """The library's rule is enforced, and its message is carried through."""
    with pytest.raises(DeviceGeometryError, match="segments"):
        build_device_model(
            synthetic_configuration(),
            reference_beamline(),
            segments,
            reference_target(),
        )


def test_the_two_configurations_have_different_body_sets() -> None:
    """A colliding-beam device has no target, and that is the point.

    Flattening the two into one body set would put a solid where there is
    none: the beams are each other's target, so the interaction region is
    vacuum and carries no body.
    """
    assert tuple(mesh.name for mesh in beam_target_model().meshes) == (
        BODY_UPSTREAM_BEAMLINE,
        BODY_TARGET,
        BODY_BEAM_DUMP,
    )
    assert tuple(mesh.name for mesh in colliding_model().meshes) == (
        BODY_UPSTREAM_BEAMLINE,
        BODY_DOWNSTREAM_BEAMLINE,
    )
    assert set(BODY_NAMES_BY_IDENTIFIER) == {"beam_target", "colliding_beam"}


def test_a_beam_target_device_without_a_target_is_refused() -> None:
    """It fires into something solid, so the something is required."""
    with pytest.raises(DeviceGeometryError, match="target: required"):
        build_device_model(
            synthetic_configuration("beam_target"),
            reference_beamline(),
            REFERENCE_SEGMENTS,
        )


def test_a_colliding_beam_device_with_a_target_is_refused() -> None:
    """A target body there would be a fiction, so it is refused, not ignored."""
    with pytest.raises(DeviceGeometryError, match="must be absent"):
        build_device_model(
            synthetic_configuration("colliding_beam"),
            reference_beamline(),
            REFERENCE_SEGMENTS,
            reference_target(),
        )


@pytest.mark.parametrize("field", ["target_radius_m", "dump_radius_m"])
def test_a_body_narrower_than_the_bore_is_refused(field: str) -> None:
    """A body the beam passes around does not intercept it.

    The refusal names both fields and prints both values, so a caller can
    see by how much it missed.
    """
    bore = reference_beamline().bore_radius_m
    with pytest.raises(DeviceGeometryError, match=field):
        build_device_model(
            synthetic_configuration("beam_target"),
            reference_beamline(),
            REFERENCE_SEGMENTS,
            reference_target(**{field: bore / 2.0}),
        )


def test_a_body_exactly_as_wide_as_the_bore_is_admitted() -> None:
    """The rule is refusal below the bore, not below-or-equal.

    A target the width of the bore intercepts every particle the pipe can
    deliver, so there is nothing to refuse.
    """
    bore = reference_beamline().bore_radius_m
    model = build_device_model(
        synthetic_configuration("beam_target"),
        reference_beamline(),
        REFERENCE_SEGMENTS,
        reference_target(target_radius_m=bore, dump_radius_m=bore),
    )
    assert len(model.meshes) == 3


def test_the_colliding_beam_lines_are_mirror_images_across_the_origin() -> None:
    """Two identical pipes, one each side of the interaction point.

    Their volumes are equal, and their z extents are negatives of each
    other.
    """
    upstream, downstream = colliding_model().meshes
    assert upstream.signed_volume_m3() == pytest.approx(downstream.signed_volume_m3())
    up_z = {round(vertex[2], 12) for vertex in upstream.vertices}
    down_z = {round(vertex[2], 12) for vertex in downstream.vertices}
    assert up_z == {-value for value in down_z}
    assert max(up_z) < 0.0 < min(down_z)


def test_the_beam_pipe_leaves_the_interaction_point_clear() -> None:
    """The gap is a gap: no body reaches the origin from upstream."""
    envelope = reference_beamline()
    upstream = colliding_model().meshes[0]
    assert max(vertex[2] for vertex in upstream.vertices) == pytest.approx(
        -envelope.interaction_gap_m
    )


def test_the_target_sits_at_the_origin_and_the_dump_behind_it() -> None:
    """Downstream is the positive direction, and the bodies stack that way."""
    target_assembly = reference_target()
    _, target, dump = beam_target_model().meshes
    target_z = [vertex[2] for vertex in target.vertices]
    dump_z = [vertex[2] for vertex in dump.vertices]
    assert min(target_z) == pytest.approx(0.0)
    assert max(target_z) == pytest.approx(target_assembly.target_thickness_m)
    assert min(dump_z) == pytest.approx(target_assembly.target_thickness_m)
    assert max(dump_z) == pytest.approx(
        target_assembly.target_thickness_m + target_assembly.dump_length_m
    )


@pytest.mark.parametrize("segments", [8, 64, 256])
def test_the_target_volume_is_its_closed_form_times_the_polygon_ratio(
    segments: int,
) -> None:
    """The tessellation loses exactly the inscribed polygon and nothing else."""
    assembly = reference_target()
    analytic = (
        math.pi
        * assembly.target_radius_m
        * assembly.target_radius_m
        * assembly.target_thickness_m
    )
    target = beam_target_model(segments).meshes[1]
    assert math.isclose(
        target.signed_volume_m3() / analytic,
        inscribed_polygon_ratio(segments),
        rel_tol=1e-13,
    )


def test_a_model_built_from_the_wrong_bodies_is_refused() -> None:
    """The container validates its own body set, not only the builder."""
    model = beam_target_model()
    with pytest.raises(DeviceGeometryError, match="must be exactly"):
        DeviceModel3D(
            identifier=model.identifier,
            configuration_digest_sha256=model.configuration_digest_sha256,
            envelope_digest_sha256=model.envelope_digest_sha256,
            target_digest_sha256=model.target_digest_sha256,
            segments=model.segments,
            meshes=model.meshes[::-1],
        )


def test_a_model_of_an_unknown_identifier_is_refused() -> None:
    """The body set is selected by identifier, so an unknown one has none."""
    model = beam_target_model()
    with pytest.raises(DeviceGeometryError, match="identifier"):
        DeviceModel3D(
            identifier="storage_ring",
            configuration_digest_sha256=model.configuration_digest_sha256,
            envelope_digest_sha256=model.envelope_digest_sha256,
            target_digest_sha256=model.target_digest_sha256,
            segments=model.segments,
            meshes=model.meshes,
        )


def test_the_record_carries_the_schema_units_and_non_claims() -> None:
    """The projection states what the model is and what it is not."""
    record = beam_target_model().to_record()
    assert record["schema"] == MODEL_SCHEMA
    assert record["schema_version"] == MODEL_SCHEMA_VERSION
    assert record["units"] == dict(MODEL_UNITS)
    assert record["non_claims"] == list(MODEL_NON_CLAIMS)
    assert record["identifier"] == "beam_target"
    assert record["target_digest_sha256"] == reference_target().digest_sha256()


def test_a_colliding_beam_record_carries_no_target_digest() -> None:
    """There is no assembly, so the field is null rather than invented."""
    record = colliding_model().to_record()
    assert record["target_digest_sha256"] is None
    assert record["identifier"] == "colliding_beam"


def test_the_canonical_bytes_are_canonical_and_the_digest_identifies_them() -> None:
    """One trailing newline, idempotent re-canonicalisation, matching digest."""
    model = beam_target_model()
    data = model.canonical_bytes()
    assert data.endswith(b"\n")
    assert data.count(b"\n") == 1
    again = json.dumps(
        json.loads(data), sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    assert (again + "\n").encode("utf-8") == data
    assert model.digest_sha256() == hashlib.sha256(data).hexdigest()


def test_the_digest_moves_with_every_input_of_the_build() -> None:
    """The envelope, the assembly, the segment count and the configuration."""
    base = beam_target_model()
    assert (
        base.digest_sha256()
        != beam_target_model(REFERENCE_SEGMENTS * 2).digest_sha256()
    )
    assert base.digest_sha256() != colliding_model().digest_sha256()
    assert (
        base.digest_sha256()
        != build_device_model(
            synthetic_configuration("beam_target"),
            reference_beamline(length_m=2.0),
            REFERENCE_SEGMENTS,
            reference_target(),
        ).digest_sha256()
    )
    assert (
        base.digest_sha256()
        != build_device_model(
            synthetic_configuration("beam_target", kinetic_energy_kev=150.0),
            reference_beamline(),
            REFERENCE_SEGMENTS,
            reference_target(),
        ).digest_sha256()
    )
