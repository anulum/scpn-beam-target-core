# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — device geometry model

"""Validated mechanical envelope of a beam line and, where there is one, a target.

The configuration owns the beam — its kinetic energy, its current and how
many lines there are — and no length at all. Every dimension of the
hardware lives here.

**Nothing here is anchored on a filed source, and that is stated rather
than glossed.** The two works this repository cites for its beam physics
are both paywalled and neither is on file; the one document that is,
the plasma formulary, prints no geometry. So every value below is a
declaration, and a consumer must not read any of them as reproducing a
published dimension. The other families in this group have printed radii
to recover; this one does not, and saying so is the only honest way to
ship it.

The envelope splits in two because the two owned configurations are not
the same machine. A beam-target device fires into something solid and
needs a target and a dump; a colliding-beam device has two beam lines
that are each other's target, and drawing a target there would be a
fiction. So :class:`TargetAssembly` is **required** for ``beam_target``
and **refused** for ``colliding_beam``.

Validation is fail-closed, serialisation is canonical, and the SHA-256
digest identifies the exact geometry.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_beam_target_core.errors import DeviceGeometryError
from scpn_beam_target_core.parameters import require_positive

BEAMLINE_FIELDS: Final = (
    "bore_radius_m",
    "wall_thickness_m",
    "length_m",
    "interaction_gap_m",
)
TARGET_FIELDS: Final = (
    "target_radius_m",
    "target_thickness_m",
    "dump_radius_m",
    "dump_length_m",
)


def _positive(name: str, value: float) -> float:
    """Apply the shared positivity rule under the geometry error type.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceGeometryError
        If the value is non-finite or not strictly positive.
    """
    try:
        return require_positive(name, value)
    except ValueError as exc:
        raise DeviceGeometryError(str(exc)) from exc


def _canonical_bytes(record: dict[str, float]) -> bytes:
    """Serialise a record canonically.

    Parameters
    ----------
    record
        Mapping of field names to values.

    Returns
    -------
    bytes
        UTF-8 JSON with sorted keys, minimal separators and a trailing
        newline; NaN and infinity are never emitted.
    """
    text = json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return (text + "\n").encode("utf-8")


@dataclass(frozen=True, slots=True)
class BeamlineEnvelope:
    """Validated envelope of one beam line.

    Parameters
    ----------
    bore_radius_m
        Inner radius of the beam pipe; strictly positive.
    wall_thickness_m
        Radial thickness of the pipe wall; strictly positive.
    length_m
        Axial length of the pipe; strictly positive.
    interaction_gap_m
        Distance from the downstream end of the pipe to the interaction
        point at the origin; strictly positive.

    Raises
    ------
    DeviceGeometryError
        If any value is non-finite or not strictly positive.
    """

    bore_radius_m: float
    wall_thickness_m: float
    length_m: float
    interaction_gap_m: float

    def __post_init__(self) -> None:
        """Validate every declared value.

        Raises
        ------
        DeviceGeometryError
            If any value is non-finite or not strictly positive.
        """
        for name in BEAMLINE_FIELDS:
            _positive(name, getattr(self, name))

    @property
    def outer_radius_m(self) -> float:
        """Outer radius of the beam pipe (bore plus wall)."""
        return self.bore_radius_m + self.wall_thickness_m

    def to_record(self) -> dict[str, float]:
        """Project the envelope to a JSON-serialisable record.

        Returns
        -------
        dict[str, float]
            Every declared parameter under its name.
        """
        return {name: getattr(self, name) for name in BEAMLINE_FIELDS}

    def canonical_bytes(self) -> bytes:
        """Serialise the envelope canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline.
        """
        return _canonical_bytes(self.to_record())

    def digest_sha256(self) -> str:
        """Identify the exact envelope.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class TargetAssembly:
    """Validated envelope of a solid target and the dump behind it.

    Parameters
    ----------
    target_radius_m
        Radius of the target disc; strictly positive, and checked against
        the beam pipe's bore when a model is built.
    target_thickness_m
        Axial thickness of the target; strictly positive.
    dump_radius_m
        Radius of the beam dump behind it; strictly positive, and checked
        against the bore.
    dump_length_m
        Axial length of the dump; strictly positive.

    Raises
    ------
    DeviceGeometryError
        If any value is non-finite or not strictly positive.
    """

    target_radius_m: float
    target_thickness_m: float
    dump_radius_m: float
    dump_length_m: float

    def __post_init__(self) -> None:
        """Validate every declared value.

        Raises
        ------
        DeviceGeometryError
            If any value is non-finite or not strictly positive.
        """
        for name in TARGET_FIELDS:
            _positive(name, getattr(self, name))

    def to_record(self) -> dict[str, float]:
        """Project the assembly to a JSON-serialisable record.

        Returns
        -------
        dict[str, float]
            Every declared parameter under its name.
        """
        return {name: getattr(self, name) for name in TARGET_FIELDS}

    def canonical_bytes(self) -> bytes:
        """Serialise the assembly canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline.
        """
        return _canonical_bytes(self.to_record())

    def digest_sha256(self) -> str:
        """Identify the exact assembly.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _number(record: dict[str, Any], field: str) -> float:
    """Return one required real-number field of a record.

    Parameters
    ----------
    record
        Decoded object.
    field
        Field name.

    Returns
    -------
    float
        The value as a float.

    Raises
    ------
    DeviceGeometryError
        If the field is absent or is not a real number.
    """
    if field not in record:
        raise DeviceGeometryError(f"{field}: required")
    value = record[field]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DeviceGeometryError(f"{field}: must be a real number, got {value!r}")
    return float(value)


def _from_record(
    record: dict[str, Any], fields: tuple[str, ...], label: str
) -> dict[str, float]:
    """Read exactly the declared fields of a record, refusing anything else.

    Parameters
    ----------
    record
        Decoded object.
    fields
        Field names the record must carry, and only those.
    label
        Name of the object, used in the unknown-field rejection.

    Returns
    -------
    dict[str, float]
        The validated values, ready to construct with.

    Raises
    ------
    DeviceGeometryError
        If a field is missing, of the wrong type, or unknown.
    """
    unknown = sorted(set(record) - set(fields))
    if unknown:
        raise DeviceGeometryError(f"{label}: unknown fields {unknown!r}")
    return {name: _number(record, name) for name in fields}


def beamline_from_record(record: dict[str, Any]) -> BeamlineEnvelope:
    """Build a beam-line envelope from a decoded record.

    Parameters
    ----------
    record
        Decoded object carrying exactly :data:`BEAMLINE_FIELDS`.

    Returns
    -------
    BeamlineEnvelope
        The validated envelope.

    Raises
    ------
    DeviceGeometryError
        If a field is missing, of the wrong type, unknown, or violates a
        model invariant.
    """
    return BeamlineEnvelope(**_from_record(record, BEAMLINE_FIELDS, "beamline"))


def target_from_record(record: dict[str, Any]) -> TargetAssembly:
    """Build a target assembly from a decoded record.

    Parameters
    ----------
    record
        Decoded object carrying exactly :data:`TARGET_FIELDS`.

    Returns
    -------
    TargetAssembly
        The validated assembly.

    Raises
    ------
    DeviceGeometryError
        If a field is missing, of the wrong type, unknown, or violates a
        model invariant.
    """
    return TargetAssembly(**_from_record(record, TARGET_FIELDS, "target"))
