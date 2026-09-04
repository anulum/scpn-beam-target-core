# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — tier-G1 device model

"""Tier-G1 tessellated model of a beam line and what it fires into.

**The body set depends on the configuration, because the two owned
configurations are not the same machine.** A beam-target device is a beam
pipe, a solid target and the dump behind it. A colliding-beam device is
two beam pipes facing each other across a gap, and nothing between them:
the beams are each other's target, and the interaction region is vacuum.

That asymmetry is the whole point of the family, and flattening it into
one body set would have put a solid where there is none. Neither the beam
nor the interaction region carries a body, for the same reason the
fusion-fission family's vacuum zone does not: what is not a solid is not
drawn.

Every body is a cylinder or an annular tube about ``z``, so this tier
needs no primitive the shared library does not already have.

Nothing in this tier is anchored on a filed source. See the envelope
module for why, and the non-claims for the statement of it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.errors import GeometryError
from scpn_reactor_kernels.geometry import (
    TriangleMesh,
    annular_tube,
    cylinder_solid,
    require_segments,
)

from scpn_beam_target_core.configuration import DeviceConfiguration
from scpn_beam_target_core.errors import DeviceGeometryError
from scpn_beam_target_core.geometry.device import BeamlineEnvelope, TargetAssembly

MODEL_SCHEMA: Final = "scpn.beam-target-3d-model.v1"
MODEL_SCHEMA_VERSION: Final = "1.0.0"
MODEL_UNITS: Final = {
    "length": "metre",
    "handedness": "right",
    "axis": "z along the beam axis, pointing downstream",
    "origin": "z = 0 at the interaction point",
}
MODEL_NON_CLAIMS: Final = (
    "analytic surfaces tessellated from a synthetic configuration and envelope",
    (
        "no dimension here reproduces a published value: the two works this "
        "repository cites for its beam physics are unobtainable, and the one "
        "filed source prints no geometry, so every length is declared"
    ),
    (
        "neither the beam nor the interaction region carries a body, because "
        "neither is a solid; the bore is the space a beam would occupy and "
        "nothing is drawn inside it"
    ),
    (
        "the beam pipe is one plain tube; no magnet, vacuum pump, diagnostic "
        "port, flange, bellows or support is modelled, and a colliding-beam "
        "device has no target because its beams are each other's"
    ),
    "no body is a CAD solid or an engineering model",
    "no material property, load, field, dose or activation quantity is carried",
    "no value describes or validates any real machine or facility",
)

ROLE_BEAMLINE: Final = "beamline"
ROLE_TARGET: Final = "target"
ROLE_DUMP: Final = "dump"
MATERIAL_BEAM_PIPE: Final = "beam_pipe"
MATERIAL_TARGET_SOLID: Final = "target_solid"
MATERIAL_DUMP_ABSORBER: Final = "dump_absorber"

BODY_UPSTREAM_BEAMLINE: Final = "upstream_beamline"
BODY_DOWNSTREAM_BEAMLINE: Final = "downstream_beamline"
BODY_TARGET: Final = "target"
BODY_BEAM_DUMP: Final = "beam_dump"

BODY_NAMES_BY_IDENTIFIER: Final = {
    "beam_target": (BODY_UPSTREAM_BEAMLINE, BODY_TARGET, BODY_BEAM_DUMP),
    "colliding_beam": (BODY_UPSTREAM_BEAMLINE, BODY_DOWNSTREAM_BEAMLINE),
}
"""The body set of each owned configuration. A beam-target device fires
into a target and a dump; a colliding-beam device has a second beam line
instead, and no solid between the two."""


@dataclass(frozen=True, slots=True)
class DeviceModel3D:
    """The tessellated device model of one configuration and envelope.

    Parameters
    ----------
    identifier
        Configuration identifier the body set belongs to.
    configuration_digest_sha256
        Digest of the configuration the model was built from.
    envelope_digest_sha256
        Digest of the beam-line envelope.
    target_digest_sha256
        Digest of the target assembly, or ``None`` for a colliding-beam
        device, which has none.
    segments
        Circumferential segment count every body was tessellated at.
    meshes
        The bodies, in the fixed order for that identifier.

    Raises
    ------
    DeviceGeometryError
        If the identifier is unknown, or the body names or their order
        differ from the set that identifier owns.
    """

    identifier: str
    configuration_digest_sha256: str
    envelope_digest_sha256: str
    target_digest_sha256: str | None
    segments: int
    meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the body set and its order against the identifier.

        Raises
        ------
        DeviceGeometryError
            If the identifier is unknown, or the body names or their
            order differ from the set that identifier owns.
        """
        expected = BODY_NAMES_BY_IDENTIFIER.get(self.identifier)
        if expected is None:
            raise DeviceGeometryError(
                f"identifier: must be one of "
                f"{tuple(BODY_NAMES_BY_IDENTIFIER)!r}, got {self.identifier!r}"
            )
        names = tuple(mesh.name for mesh in self.meshes)
        if names != expected:
            raise DeviceGeometryError(
                f"meshes: bodies of {self.identifier!r} must be exactly "
                f"{expected!r} in order, got {names!r}"
            )

    def to_record(self) -> dict[str, Any]:
        """Project the model to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with one entry per body.
        """
        return {
            "schema": MODEL_SCHEMA,
            "schema_version": MODEL_SCHEMA_VERSION,
            "units": dict(MODEL_UNITS),
            "non_claims": list(MODEL_NON_CLAIMS),
            "identifier": self.identifier,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "envelope_digest_sha256": self.envelope_digest_sha256,
            "target_digest_sha256": self.target_digest_sha256,
            "segments": self.segments,
            "bodies": [
                {
                    "name": mesh.name,
                    "role": mesh.role,
                    "material_identifier": mesh.material_identifier,
                    "vertex_count": mesh.vertex_count,
                    "face_count": mesh.face_count,
                    "volume_m3": mesh.signed_volume_m3(),
                    "surface_area_m2": mesh.surface_area_m2(),
                }
                for mesh in self.meshes
            ],
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


def require_assembly(
    configuration: DeviceConfiguration, target: TargetAssembly | None
) -> TargetAssembly | None:
    """Refuse a target assembly that does not match the configuration.

    Parameters
    ----------
    configuration
        Validated device configuration.
    target
        Declared target assembly, or ``None``.

    Returns
    -------
    TargetAssembly or None
        The assembly, unchanged, once it matches the identifier.

    Raises
    ------
    DeviceGeometryError
        If a ``beam_target`` device is given no assembly, or a
        ``colliding_beam`` device is given one. A colliding-beam device's
        beams are each other's target; a target body there would be a
        fiction, so it is refused rather than ignored.
    """
    wanted = BODY_TARGET in BODY_NAMES_BY_IDENTIFIER[configuration.identifier]
    if wanted and target is None:
        raise DeviceGeometryError(
            f"target: required for {configuration.identifier!r}, which fires "
            f"into a solid target"
        )
    if not wanted and target is not None:
        raise DeviceGeometryError(
            f"target: must be absent for {configuration.identifier!r}, whose "
            f"beams are each other's target"
        )
    return target


def require_intercept(envelope: BeamlineEnvelope, target: TargetAssembly) -> None:
    """Refuse a target or dump narrower than the beam pipe's bore.

    Parameters
    ----------
    envelope
        Validated beam-line envelope.
    target
        Validated target assembly.

    Raises
    ------
    DeviceGeometryError
        If the target or the dump is narrower than the bore. A body the
        beam can pass around does not intercept it, and each refusal
        names both fields and their values.
    """
    bore = envelope.bore_radius_m
    for name, radius in (
        ("target_radius_m", target.target_radius_m),
        ("dump_radius_m", target.dump_radius_m),
    ):
        if radius < bore:
            raise DeviceGeometryError(
                f"{name}: must not be smaller than bore_radius_m or the beam "
                f"passes around it ({radius!r} < {bore!r})"
            )


def build_device_model(
    configuration: DeviceConfiguration,
    envelope: BeamlineEnvelope,
    segments: int,
    target: TargetAssembly | None = None,
) -> DeviceModel3D:
    """Tessellate the bodies of a validated design.

    Parameters
    ----------
    configuration
        Validated beam configuration; its identifier selects the body set
        and its beam-line count is checked against it.
    envelope
        Validated beam-line envelope.
    segments
        Circumferential segments for every body; at least 8, multiple
        of 8.
    target
        Target assembly, required for ``beam_target`` and refused for
        ``colliding_beam``.

    Returns
    -------
    DeviceModel3D
        The composed model.

    Raises
    ------
    DeviceGeometryError
        If the segment count is invalid, the target assembly does not
        match the configuration, or a target does not intercept the bore;
        the library's refusal is re-raised under the device error type
        with its message.
    """
    try:
        require_segments(segments)
    except GeometryError as exc:
        raise DeviceGeometryError(str(exc)) from exc
    assembly = require_assembly(configuration, target)
    bore = envelope.bore_radius_m
    outer = envelope.outer_radius_m
    gap = envelope.interaction_gap_m
    length = envelope.length_m
    bodies = [
        (
            BODY_UPSTREAM_BEAMLINE,
            ROLE_BEAMLINE,
            MATERIAL_BEAM_PIPE,
            annular_tube(bore, outer, -gap - length, -gap, segments),
        )
    ]
    if assembly is None:
        bodies.append(
            (
                BODY_DOWNSTREAM_BEAMLINE,
                ROLE_BEAMLINE,
                MATERIAL_BEAM_PIPE,
                annular_tube(bore, outer, gap, gap + length, segments),
            )
        )
    else:
        require_intercept(envelope, assembly)
        thickness = assembly.target_thickness_m
        bodies.append(
            (
                BODY_TARGET,
                ROLE_TARGET,
                MATERIAL_TARGET_SOLID,
                cylinder_solid(assembly.target_radius_m, 0.0, thickness, segments),
            )
        )
        bodies.append(
            (
                BODY_BEAM_DUMP,
                ROLE_DUMP,
                MATERIAL_DUMP_ABSORBER,
                cylinder_solid(
                    assembly.dump_radius_m,
                    thickness,
                    thickness + assembly.dump_length_m,
                    segments,
                ),
            )
        )
    meshes = tuple(
        TriangleMesh(
            name=name,
            role=role,
            material_identifier=material,
            vertices=vertices,
            faces=faces,
        )
        for name, role, material, (vertices, faces) in bodies
    )
    return DeviceModel3D(
        identifier=configuration.identifier,
        configuration_digest_sha256=configuration.digest_sha256(),
        envelope_digest_sha256=envelope.digest_sha256(),
        target_digest_sha256=None if assembly is None else assembly.digest_sha256(),
        segments=segments,
        meshes=meshes,
    )
