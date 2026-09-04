# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — tier-G2 device model tests

"""Every branch of the tier-G2 model, and what its faceting is limited by.

The builds are cached: each costs about eight seconds, and rebuilding one
per test buys no evidence a single build does not already carry.
"""

from __future__ import annotations

import functools
import hashlib
import json
from collections.abc import Callable
from typing import Any

import pytest
from scpn_reactor_kernels.cad import BodyEvidence

from geometry_fixtures import (
    reference_beamline,
    reference_target,
    synthetic_configuration,
)
from scpn_beam_target_core.errors import DeviceGeometryError
from scpn_beam_target_core.geometry import (
    BODY_NAMES_BY_IDENTIFIER,
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    CAD_MODEL_UNITS,
    DEFAULT_ANGULAR_DEFLECTION_RAD,
    DEFAULT_LINEAR_DEFLECTION_M,
    DEFAULT_REFERENCE_MESH_SEGMENTS,
    DeviceModelCAD,
    build_device_cad,
)

#: The strongest guarantee the declared bound makes on any body. Measured:
#: the widest is the beam pipe's at 0.0667 %.
BOUND_CEILING = 1e-3


@functools.cache
def beam_target_model() -> DeviceModelCAD:
    """Build and cache the beam-target B-rep model."""
    return build_device_cad(
        synthetic_configuration("beam_target"), reference_beamline(), reference_target()
    )


@functools.cache
def colliding_model() -> DeviceModelCAD:
    """Build and cache the colliding-beam B-rep model."""
    return build_device_cad(
        synthetic_configuration("colliding_beam"), reference_beamline()
    )


def evidence(model: DeviceModelCAD) -> list[tuple[float, float]]:
    """Return each body's relative deficit and its declared bound."""
    return [
        (
            body.to_record()["faceted_volume_relative_deficit"],
            body.to_record()["faceted_volume_deficit_bound"],
        )
        for body in model.bodies
    ]


def test_each_configuration_builds_its_own_body_set() -> None:
    """Tier G2 keeps the asymmetry tier G1 has."""
    assert (
        tuple(body.name for body in beam_target_model().bodies)
        == (BODY_NAMES_BY_IDENTIFIER["beam_target"])
    )
    assert (
        tuple(body.name for body in colliding_model().bodies)
        == (BODY_NAMES_BY_IDENTIFIER["colliding_beam"])
    )


def test_a_colliding_beam_device_with_a_target_is_refused_here_too() -> None:
    """The rule is enforced at both tiers, not only where the meshes are built."""
    with pytest.raises(DeviceGeometryError, match="must be absent"):
        build_device_cad(
            synthetic_configuration("colliding_beam"),
            reference_beamline(),
            reference_target(),
        )


def test_a_beam_target_device_without_a_target_is_refused_here_too() -> None:
    """The same, in the other direction."""
    with pytest.raises(DeviceGeometryError, match="target: required"):
        build_device_cad(synthetic_configuration("beam_target"), reference_beamline())


@pytest.mark.parametrize("model", [beam_target_model, colliding_model])
def test_every_body_stays_well_inside_a_bound_worth_having(
    model: Callable[[], DeviceModelCAD],
) -> None:
    """A margin is only as good as the bound it is a margin on.

    The deflections were chosen for the **tightest** bound that still
    passes rather than the widest margin. Measured, a coarser linear
    deflection would give margins of a hundred and fifty times on a bound
    ten times looser, which claims less. Every declared bound here is
    under a tenth of a per cent and every body clears it by more than
    twenty times.
    """
    built = model()
    for deficit, bound in evidence(built):
        assert 0.0 < deficit < bound
        assert bound < BOUND_CEILING
        assert bound / deficit > 20.0


def test_the_faceting_deficit_depends_on_the_radius_here() -> None:
    """At these deflections the linear criterion binds, not the angular one.

    The three bodies of the beam-target build have different radii and
    different deficits, which is the signature of a linear criterion —
    the opposite of the tokamak family, where one angular step gave every
    body the same deficit whatever its radius. Measured on the grid: at
    this linear deflection, changing the angular deflection moves nothing.
    """
    deficits = [deficit for deficit, _ in evidence(beam_target_model())]
    assert len(set(deficits)) == len(deficits)
    coarser = build_device_cad(
        synthetic_configuration("beam_target"),
        reference_beamline(),
        reference_target(),
        angular_deflection_rad=DEFAULT_ANGULAR_DEFLECTION_RAD * 2.0,
    )
    assert [deficit for deficit, _ in evidence(coarser)] == deficits


def test_the_two_beam_lines_of_a_collider_share_one_deficit() -> None:
    """Identical bodies face the mesher almost identically.

    Their declared bounds are the same number exactly, because the bound
    depends only on the radius. Their measured deficits are not: the two
    pipes sit at opposite ends of the axis, and the volume sums accumulate
    differently, so they part at the ninth significant figure — 1.5e-9
    relative, measured. The tolerance sits an order above that.
    """
    (first_deficit, first_bound), (second_deficit, second_bound) = evidence(
        colliding_model()
    )
    assert first_bound == second_bound
    assert first_deficit == pytest.approx(second_deficit, rel=1e-8)


@pytest.mark.parametrize(
    ("field", "linear", "angular"),
    [
        ("linear_deflection_m", -1.0e-5, DEFAULT_ANGULAR_DEFLECTION_RAD),
        ("angular_deflection_rad", DEFAULT_LINEAR_DEFLECTION_M, 0.0),
    ],
)
def test_an_invalid_deflection_is_refused_under_the_device_error(
    field: str, linear: float, angular: float
) -> None:
    """The library validates the mesher's own inputs, and its message carries.

    The refusal comes from the shared library and is re-raised under this
    repository's error type with its text intact, so a caller sees which
    deflection it rejected and why without needing to know which package
    it came from.
    """
    with pytest.raises(DeviceGeometryError, match=field):
        build_device_cad(
            synthetic_configuration("beam_target"),
            reference_beamline(),
            reference_target(),
            linear_deflection_m=linear,
            angular_deflection_rad=angular,
        )


def test_a_manifest_of_the_wrong_shape_is_refused() -> None:
    """The container validates the manifest it was handed, not only the build."""
    model = beam_target_model()
    for broken, match in (
        ({**model.assembly_manifest, "schema": "wrong"}, "assembly_manifest.schema"),
        ({**model.assembly_manifest, "body_count": 9}, "body_count"),
    ):
        with pytest.raises(DeviceGeometryError, match=match):
            _rebuild(model, assembly_manifest=broken)


def test_bodies_out_of_order_are_refused() -> None:
    """The fixed order is enforced on the container as well as the builder."""
    model = beam_target_model()
    with pytest.raises(DeviceGeometryError, match="must be exactly"):
        _rebuild(model, bodies=model.bodies[::-1])


def test_an_unknown_identifier_is_refused() -> None:
    """The body set is selected by identifier, so an unknown one has none."""
    model = beam_target_model()
    with pytest.raises(DeviceGeometryError, match="identifier"):
        _rebuild(model, identifier="storage_ring")


def _rebuild(
    model: DeviceModelCAD,
    identifier: str | None = None,
    assembly_manifest: dict[str, Any] | None = None,
    bodies: tuple[BodyEvidence, ...] | None = None,
) -> DeviceModelCAD:
    """Reconstruct a record with one field replaced, to exercise its guards.

    The three replaceable fields are named and typed rather than splatted
    from a mapping: a mapping would have to be typed loosely enough that
    the constructor could not be checked, which is exactly the check these
    tests exist to exercise.
    """
    return DeviceModelCAD(
        identifier=model.identifier if identifier is None else identifier,
        configuration_digest_sha256=model.configuration_digest_sha256,
        envelope_digest_sha256=model.envelope_digest_sha256,
        target_digest_sha256=model.target_digest_sha256,
        reference_mesh_segments=model.reference_mesh_segments,
        linear_deflection_m=model.linear_deflection_m,
        angular_deflection_rad=model.angular_deflection_rad,
        backend_versions=model.backend_versions,
        assembly_manifest=(
            model.assembly_manifest if assembly_manifest is None else assembly_manifest
        ),
        step_sha256=model.step_sha256,
        bodies=model.bodies if bodies is None else bodies,
        step_data=model.step_data,
        faceted_meshes=model.faceted_meshes,
    )


def test_the_step_export_is_present_and_its_digest_matches_its_bytes() -> None:
    """The digest names the exact bytes the model carries."""
    model = beam_target_model()
    assert model.step_data.startswith(b"ISO-10303-21;")
    assert model.step_sha256 == hashlib.sha256(model.step_data).hexdigest()


def test_the_two_configurations_produce_different_step_bytes() -> None:
    """The export carries the machine, not a template."""
    assert beam_target_model().step_sha256 != colliding_model().step_sha256


def test_the_record_carries_the_schema_units_and_non_claims() -> None:
    """The projection states what the model is and what it is not."""
    record = beam_target_model().to_record()
    assert record["schema"] == CAD_MODEL_SCHEMA
    assert record["schema_version"] == CAD_MODEL_SCHEMA_VERSION
    assert record["units"] == dict(CAD_MODEL_UNITS)
    assert record["non_claims"] == list(CAD_MODEL_NON_CLAIMS)
    assert record["reference_mesh_segments"] == DEFAULT_REFERENCE_MESH_SEGMENTS
    assert record["linear_deflection_m"] == DEFAULT_LINEAR_DEFLECTION_M
    assert record["angular_deflection_rad"] == DEFAULT_ANGULAR_DEFLECTION_RAD
    assert record["backend_versions"]
    assert colliding_model().to_record()["target_digest_sha256"] is None


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


def test_both_tiers_are_bound_to_the_same_inputs() -> None:
    """The model names the configuration, envelope and assembly it used."""
    model = beam_target_model()
    assert model.configuration_digest_sha256 == (
        synthetic_configuration("beam_target").digest_sha256()
    )
    assert model.envelope_digest_sha256 == reference_beamline().digest_sha256()
    assert model.target_digest_sha256 == reference_target().digest_sha256()
