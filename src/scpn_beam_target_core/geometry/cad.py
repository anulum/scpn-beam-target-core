# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — tier-G2 device model

"""Tier-G2 B-rep model of a beam line and what it fires into.

The same bodies as tier G1 — and the same dependence of the body set on
the configuration — built as exact solids through the shared library's
``cad`` group instead of tessellated, with every body checked fail-closed
by the library's evidence kernel against its analytic closed forms and
against its tier-G1 twin, and exported as normalised STEP bytes with a
digest.

Every body is a cylinder or an annular tube, so each has a well-defined
smallest circular radius and the faceting deficit bound needs no special
case here.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.cad import (
    MANIFEST_SCHEMA,
    BodyEvidence,
    BrepAssembly,
    annular_tube_brep,
    assembly_evidence,
    backend_versions,
    cylinder_solid_brep,
    facet_assembly,
    step_bytes,
    step_sha256,
)
from scpn_reactor_kernels.errors import CadError, GeometryError
from scpn_reactor_kernels.geometry import TriangleMesh

from scpn_beam_target_core.configuration import DeviceConfiguration
from scpn_beam_target_core.errors import DeviceGeometryError
from scpn_beam_target_core.geometry.device import BeamlineEnvelope, TargetAssembly
from scpn_beam_target_core.geometry.model import (
    BODY_BEAM_DUMP,
    BODY_DOWNSTREAM_BEAMLINE,
    BODY_NAMES_BY_IDENTIFIER,
    BODY_TARGET,
    BODY_UPSTREAM_BEAMLINE,
    MATERIAL_BEAM_PIPE,
    MATERIAL_DUMP_ABSORBER,
    MATERIAL_TARGET_SOLID,
    ROLE_BEAMLINE,
    ROLE_DUMP,
    ROLE_TARGET,
    build_device_model,
    require_assembly,
    require_intercept,
)

CAD_MODEL_SCHEMA: Final = "scpn.beam-target-cad-model.v1"
CAD_MODEL_SCHEMA_VERSION: Final = "1.0.0"
CAD_MODEL_UNITS: Final = {
    "length": "metre",
    "handedness": "right",
    "axis": "z along the beam axis, pointing downstream",
    "origin": "z = 0 at the interaction point",
}
CAD_MODEL_NON_CLAIMS: Final = (
    "exact solids of revolution of a synthetic configuration and envelope",
    (
        "no dimension here reproduces a published value: the two works this "
        "repository cites for its beam physics are unobtainable, and the one "
        "filed source prints no geometry, so every length is declared"
    ),
    (
        "neither the beam nor the interaction region carries a body, because "
        "neither is a solid"
    ),
    (
        "the beam pipe is one plain tube; no magnet, vacuum pump, diagnostic "
        "port, flange, bellows or support is modelled"
    ),
    (
        "determinism of the STEP bytes is claimed within one pinned back-end "
        "environment only, never across back-end versions"
    ),
    "no body is an engineering model and no fabrication tolerance is carried",
    "no value describes or validates any real machine or facility",
)

#: Reference tessellation the B-rep bodies are checked against.
DEFAULT_REFERENCE_MESH_SEGMENTS: Final = 8
#: Mesher deflections of the faceting comparison, both set by measurement
#: on this family's own scale rather than copied from a sibling.
DEFAULT_LINEAR_DEFLECTION_M: Final = 1.0e-5
DEFAULT_ANGULAR_DEFLECTION_RAD: Final = 0.1


@dataclass(frozen=True, slots=True)
class DeviceModelCAD:
    """The B-rep device model of one configuration and envelope.

    Parameters
    ----------
    identifier
        Configuration identifier the body set belongs to.
    configuration_digest_sha256, envelope_digest_sha256
        Digests of the inputs the model was built from.
    target_digest_sha256
        Digest of the target assembly, or ``None`` where there is none.
    reference_mesh_segments
        Tier-G1 reference the bodies were checked against.
    linear_deflection_m, angular_deflection_rad
        Mesher deflections of the faceting comparison.
    backend_versions
        Versions of the pinned back-ends that produced the solids.
    assembly_manifest
        The library's assembly manifest of the bodies.
    step_sha256
        Digest of the normalised STEP bytes.
    bodies
        Checked evidence of each body, in the fixed order.
    step_data
        The normalised STEP bytes themselves.
    faceted_meshes
        The faceted meshes the evidence was computed from.

    Raises
    ------
    DeviceGeometryError
        If the identifier is unknown, or the manifest schema, the body
        count or the body order is wrong.
    """

    identifier: str
    configuration_digest_sha256: str
    envelope_digest_sha256: str
    target_digest_sha256: str | None
    reference_mesh_segments: int
    linear_deflection_m: float
    angular_deflection_rad: float
    backend_versions: dict[str, str]
    assembly_manifest: dict[str, Any]
    step_sha256: str
    bodies: tuple[BodyEvidence, ...]
    step_data: bytes
    faceted_meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the manifest and the body set against the identifier.

        Raises
        ------
        DeviceGeometryError
            If the identifier is unknown, or the manifest schema, the
            body count or the body order is wrong.
        """
        expected = BODY_NAMES_BY_IDENTIFIER.get(self.identifier)
        if expected is None:
            raise DeviceGeometryError(
                f"identifier: must be one of "
                f"{tuple(BODY_NAMES_BY_IDENTIFIER)!r}, got {self.identifier!r}"
            )
        if self.assembly_manifest.get("schema") != MANIFEST_SCHEMA:
            raise DeviceGeometryError(
                f"assembly_manifest.schema: must be {MANIFEST_SCHEMA!r}"
            )
        if self.assembly_manifest.get("body_count") != len(expected):
            raise DeviceGeometryError(
                f"assembly_manifest.body_count: must be {len(expected)}, got "
                f"{self.assembly_manifest.get('body_count')!r}"
            )
        names = tuple(body.name for body in self.bodies)
        if names != expected:
            raise DeviceGeometryError(
                f"bodies: of {self.identifier!r} must be exactly {expected!r} "
                f"in order, got {names!r}"
            )

    def to_record(self) -> dict[str, Any]:
        """Project the model to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with one entry per body.
        """
        return {
            "schema": CAD_MODEL_SCHEMA,
            "schema_version": CAD_MODEL_SCHEMA_VERSION,
            "units": dict(CAD_MODEL_UNITS),
            "non_claims": list(CAD_MODEL_NON_CLAIMS),
            "identifier": self.identifier,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "envelope_digest_sha256": self.envelope_digest_sha256,
            "target_digest_sha256": self.target_digest_sha256,
            "reference_mesh_segments": self.reference_mesh_segments,
            "linear_deflection_m": self.linear_deflection_m,
            "angular_deflection_rad": self.angular_deflection_rad,
            "backend_versions": dict(self.backend_versions),
            "assembly_manifest": self.assembly_manifest,
            "step_sha256": self.step_sha256,
            "bodies": [body.to_record() for body in self.bodies],
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the model record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact model record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def build_device_cad(
    configuration: DeviceConfiguration,
    envelope: BeamlineEnvelope,
    target: TargetAssembly | None = None,
    segments: int = DEFAULT_REFERENCE_MESH_SEGMENTS,
    linear_deflection_m: float = DEFAULT_LINEAR_DEFLECTION_M,
    angular_deflection_rad: float = DEFAULT_ANGULAR_DEFLECTION_RAD,
) -> DeviceModelCAD:
    """Build the B-rep device model of a validated design.

    Parameters
    ----------
    configuration
        Validated beam configuration.
    envelope
        Validated beam-line envelope.
    target
        Target assembly, required for ``beam_target`` and refused for
        ``colliding_beam``.
    segments
        Segment count of the tier-G1 reference mesh of the comparison.
    linear_deflection_m, angular_deflection_rad
        Mesher deflections of the faceting comparison.

    Returns
    -------
    DeviceModelCAD
        The composed, fail-closed checked model with its STEP export.

    Raises
    ------
    DeviceGeometryError
        If a count or a deflection is invalid, the target assembly does
        not match the configuration, or a body violates a declared
        evidence bound; the library's refusals are re-raised under the
        device error type with their messages.
        :class:`~scpn_reactor_kernels.errors.CadUnavailableError` if the
        optional CAD back-end is absent.
    """
    reference = build_device_model(configuration, envelope, segments, target)
    assembly = require_assembly(configuration, target)
    bore = envelope.bore_radius_m
    outer = envelope.outer_radius_m
    gap = envelope.interaction_gap_m
    length = envelope.length_m
    solids = [
        annular_tube_brep(
            bore,
            outer,
            -gap - length,
            -gap,
            BODY_UPSTREAM_BEAMLINE,
            ROLE_BEAMLINE,
            MATERIAL_BEAM_PIPE,
        )
    ]
    radii = [bore]
    if assembly is None:
        solids.append(
            annular_tube_brep(
                bore,
                outer,
                gap,
                gap + length,
                BODY_DOWNSTREAM_BEAMLINE,
                ROLE_BEAMLINE,
                MATERIAL_BEAM_PIPE,
            )
        )
        radii.append(bore)
    else:
        require_intercept(envelope, assembly)
        thickness = assembly.target_thickness_m
        solids.append(
            cylinder_solid_brep(
                assembly.target_radius_m,
                0.0,
                thickness,
                BODY_TARGET,
                ROLE_TARGET,
                MATERIAL_TARGET_SOLID,
            )
        )
        solids.append(
            cylinder_solid_brep(
                assembly.dump_radius_m,
                thickness,
                thickness + assembly.dump_length_m,
                BODY_BEAM_DUMP,
                ROLE_DUMP,
                MATERIAL_DUMP_ABSORBER,
            )
        )
        radii.extend((assembly.target_radius_m, assembly.dump_radius_m))
    try:
        brep = BrepAssembly(tuple(solids))
        faceted = facet_assembly(brep, linear_deflection_m, angular_deflection_rad)
        bodies = assembly_evidence(
            brep.bodies,
            tuple(radii),
            faceted,
            reference.meshes,
            linear_deflection_m,
            segments,
        )
    except (CadError, GeometryError) as exc:
        raise DeviceGeometryError(str(exc)) from exc
    manifest = brep.manifest()
    extras = {
        "schema": CAD_MODEL_SCHEMA,
        "schema_version": CAD_MODEL_SCHEMA_VERSION,
        "identifier": configuration.identifier,
        "configuration_digest_sha256": configuration.digest_sha256(),
        "envelope_digest_sha256": envelope.digest_sha256(),
        "assembly_manifest_sha256": brep.manifest_sha256(),
        "units": dict(CAD_MODEL_UNITS),
        "non_claims": list(CAD_MODEL_NON_CLAIMS),
        "backend_versions": backend_versions(),
    }
    step_data = step_bytes(brep, extras)
    return DeviceModelCAD(
        identifier=configuration.identifier,
        configuration_digest_sha256=configuration.digest_sha256(),
        envelope_digest_sha256=envelope.digest_sha256(),
        target_digest_sha256=None if assembly is None else assembly.digest_sha256(),
        reference_mesh_segments=segments,
        linear_deflection_m=linear_deflection_m,
        angular_deflection_rad=angular_deflection_rad,
        backend_versions=backend_versions(),
        assembly_manifest=manifest,
        step_sha256=step_sha256(step_data),
        bodies=bodies,
        step_data=step_data,
        faceted_meshes=faceted,
    )
