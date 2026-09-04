# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — device geometry tests

"""Every branch of the two envelopes and their parsers.

All parameter sets are synthetic and declared; none reproduces a
published dimension, because this repository has none on file.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any

import pytest

from geometry_fixtures import (
    REFERENCE_BEAMLINE_FIELDS,
    REFERENCE_TARGET_FIELDS,
    reference_beamline,
    reference_target,
)
from scpn_beam_target_core.errors import DeviceGeometryError
from scpn_beam_target_core.geometry import (
    BEAMLINE_FIELDS,
    TARGET_FIELDS,
    beamline_from_record,
    target_from_record,
)


@pytest.mark.parametrize("field", BEAMLINE_FIELDS)
@pytest.mark.parametrize("value", [0.0, -1.0, math.nan, math.inf])
def test_every_beamline_field_is_refused_by_name_when_not_positive(
    field: str, value: float
) -> None:
    """Each declared value is validated, and the refusal names it."""
    with pytest.raises(DeviceGeometryError, match=field):
        reference_beamline(**{field: value})


@pytest.mark.parametrize("field", TARGET_FIELDS)
@pytest.mark.parametrize("value", [0.0, -1.0, math.nan, math.inf])
def test_every_target_field_is_refused_by_name_when_not_positive(
    field: str, value: float
) -> None:
    """The same rule holds on the assembly."""
    with pytest.raises(DeviceGeometryError, match=field):
        reference_target(**{field: value})


def test_the_pipe_outer_radius_is_the_bore_plus_the_wall() -> None:
    """The wall is radial thickness, not an outer radius in disguise."""
    envelope = reference_beamline()
    assert envelope.outer_radius_m == pytest.approx(
        envelope.bore_radius_m + envelope.wall_thickness_m
    )
    assert envelope.outer_radius_m > envelope.bore_radius_m


@pytest.mark.parametrize(
    ("build", "fields", "expected"),
    [
        (reference_beamline, BEAMLINE_FIELDS, REFERENCE_BEAMLINE_FIELDS),
        (reference_target, TARGET_FIELDS, REFERENCE_TARGET_FIELDS),
    ],
)
def test_the_record_carries_exactly_the_declared_fields(
    build: Any, fields: tuple[str, ...], expected: dict[str, float]
) -> None:
    """The projection neither loses nor invents a field."""
    record = build().to_record()
    assert set(record) == set(fields)
    assert record == expected


@pytest.mark.parametrize("build", [reference_beamline, reference_target])
def test_the_canonical_bytes_are_canonical(build: Any) -> None:
    """Sorted keys, minimal separators and exactly one trailing newline."""
    data = build().canonical_bytes()
    assert data.endswith(b"\n")
    assert data.count(b"\n") == 1
    again = json.dumps(
        json.loads(data), sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    assert (again + "\n").encode("utf-8") == data


def test_each_digest_identifies_its_own_object() -> None:
    """The digest is the SHA-256 of the canonical bytes and moves with them."""
    envelope = reference_beamline()
    assert (
        envelope.digest_sha256()
        == hashlib.sha256(envelope.canonical_bytes()).hexdigest()
    )
    assert reference_beamline(length_m=2.0).digest_sha256() != envelope.digest_sha256()
    target = reference_target()
    assert (
        target.digest_sha256() == hashlib.sha256(target.canonical_bytes()).hexdigest()
    )
    assert reference_target(dump_length_m=0.3).digest_sha256() != target.digest_sha256()
    assert envelope.digest_sha256() != target.digest_sha256()


@pytest.mark.parametrize(
    ("build", "parse"),
    [
        (reference_beamline, beamline_from_record),
        (reference_target, target_from_record),
    ],
)
def test_a_record_round_trips_through_its_parser(build: Any, parse: Any) -> None:
    """Parsing a projection reproduces the object exactly."""
    original = build()
    assert parse(original.to_record()) == original


@pytest.mark.parametrize(
    ("parse", "record", "match"),
    [
        (beamline_from_record, {}, "bore_radius_m"),
        (beamline_from_record, {"extra": 1.0}, "beamline: unknown fields"),
        (target_from_record, {}, "target_radius_m"),
        (target_from_record, {"extra": 1.0}, "target: unknown fields"),
    ],
)
def test_each_parser_refuses_a_missing_or_unknown_field(
    parse: Any, record: dict[str, Any], match: str
) -> None:
    """A missing or unknown field is refused, and the rejection names the object."""
    with pytest.raises(DeviceGeometryError, match=match):
        parse(record)


@pytest.mark.parametrize("value", ["0.03", True, None, [0.03]])
def test_the_parser_refuses_a_field_that_is_not_a_real_number(value: Any) -> None:
    """A boolean is refused explicitly.

    Python would otherwise accept it as an integer and read ``True`` as a
    bore radius of one metre.
    """
    record = {**REFERENCE_BEAMLINE_FIELDS, "bore_radius_m": value}
    with pytest.raises(DeviceGeometryError, match="real number"):
        beamline_from_record(record)


def test_an_integer_length_is_accepted_as_a_real_number() -> None:
    """JSON carries no float-integer distinction, so an integer is a length."""
    record = {**REFERENCE_BEAMLINE_FIELDS, "length_m": 2}
    assert beamline_from_record(record).length_m == 2.0
