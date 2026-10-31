# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — level-0 record replay tests

"""A level-0 record replays from its configuration document and itself.

The record carries the configuration digest and the declared inputs, so
another process holding only the two documents rebuilds it byte for byte
through the public decoders. Everything that would make a replay silently
use other state is refused: another schema or version, another
configuration, altered inputs or outputs, and malformed documents.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from physics_fixtures import synthetic_configuration
from scpn_beam_target_core import configuration_from_bytes
from scpn_beam_target_core.errors import DeviceConfigurationError
from scpn_beam_target_core.physics import (
    LEVEL0_SCHEMA_VERSION,
    BeamInputs,
    beam_inputs_from_record,
    level0_physics,
    replay_level0,
)


def _record(identifier: str = "beam_target", charge: int = 1) -> bytes:
    configuration = synthetic_configuration(identifier)
    return level0_physics(
        configuration, BeamInputs(reaction="d_t", charge_number=charge)
    ).canonical_bytes()


def _edited(data: bytes, edit: dict[str, Any]) -> bytes:
    record = json.loads(data)
    record.update(edit)
    return (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()


@pytest.mark.parametrize("identifier", ["beam_target", "colliding_beam"])
@pytest.mark.parametrize("charge", [1, 2])
def test_a_record_replays_from_the_two_documents_alone(
    identifier: str, charge: int
) -> None:
    """Configuration bytes plus record bytes reproduce the record exactly."""
    configuration_document = synthetic_configuration(identifier).canonical_bytes()
    data = _record(identifier, charge)
    configuration = configuration_from_bytes(configuration_document)
    replayed = replay_level0(configuration, data)
    assert replayed.canonical_bytes() == data
    assert replayed.inputs == BeamInputs(reaction="d_t", charge_number=charge)


def test_the_record_names_every_consumed_input() -> None:
    """Version 1.1.0 carries the inputs block; the charge number is on record."""
    record = json.loads(_record(charge=2))
    assert record["schema_version"] == LEVEL0_SCHEMA_VERSION == "1.1.0"
    assert record["inputs"] == {"reaction": "d_t", "charge_number": 2}


@pytest.mark.parametrize(
    ("edit", "match"),
    [
        ({"schema": "scpn.other-level0-physics.v1"}, "schema: unknown"),
        ({"schema_version": "1.0.0"}, "schema_version"),
        ({"schema_version": "9.0.0"}, "schema_version"),
        ({"configuration_digest_sha256": "0" * 64}, "another configuration"),
        ({"inputs": {"reaction": "d_t", "charge_number": 3}}, "does not reproduce"),
        ({"inputs": {"reaction": "d_d_t", "charge_number": 1}}, "does not reproduce"),
        ({"non_claims": []}, "does not reproduce"),
        ({"extra": 1}, "exactly"),
    ],
    ids=[
        "schema",
        "old-version",
        "new-version",
        "stale-configuration",
        "charge-edited",
        "reaction-edited",
        "non-claims-dropped",
        "extra-member",
    ],
)
def test_a_record_that_would_not_replay_faithfully_is_refused(
    edit: dict[str, Any], match: str
) -> None:
    """Every mismatch is refused with the family error and its reason."""
    data = _edited(_record(), edit)
    with pytest.raises(DeviceConfigurationError, match=match):
        replay_level0(synthetic_configuration(), data)


def test_an_altered_output_is_refused() -> None:
    """A changed operating-point value does not survive the recomputation."""
    record = json.loads(_record())
    record["operating_point"]["total_beam_power_w"] *= 2.0
    data = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
    with pytest.raises(DeviceConfigurationError, match="does not reproduce"):
        replay_level0(synthetic_configuration(), data)


def test_a_record_for_another_configuration_is_refused() -> None:
    """The same inputs on another configuration name another digest."""
    with pytest.raises(DeviceConfigurationError, match="another configuration"):
        replay_level0(synthetic_configuration("colliding_beam"), _record())


def test_a_non_canonical_spelling_is_refused() -> None:
    """The replay compares bytes, so an indented form does not pass."""
    indented = json.dumps(json.loads(_record()), indent=2, sort_keys=True).encode()
    with pytest.raises(DeviceConfigurationError, match="does not reproduce"):
        replay_level0(synthetic_configuration(), indented)


@pytest.mark.parametrize(
    ("data", "match"),
    [
        (b"\xff", "invalid JSON"),
        (b"{", "invalid JSON"),
        (b"[]", "exactly"),
        (b'{"schema": NaN}', "non-finite"),
        (b'{"schema": 1, "schema": 2}', "duplicate member"),
        (b"[" * 100_000 + b"]" * 100_000, "nesting"),
    ],
    ids=["utf8", "truncated", "array", "nan", "duplicate", "deep"],
)
def test_a_malformed_document_is_refused(data: bytes, match: str) -> None:
    """Malformed bytes raise the family error, never a decoder exception."""
    with pytest.raises(DeviceConfigurationError, match=match):
        replay_level0(synthetic_configuration(), data)


@pytest.mark.parametrize(
    ("record", "match"),
    [
        (None, "inputs: must be an object"),
        ({"reaction": "d_t"}, "inputs: must be an object"),
        ({"reaction": 1, "charge_number": 1}, "reaction: must be a string"),
        ({"reaction": "x_y", "charge_number": 1}, "reaction"),
        ({"reaction": "d_t", "charge_number": True}, "charge_number: must be an int"),
        ({"reaction": "d_t", "charge_number": 1.0}, "charge_number: must be an int"),
    ],
    ids=["null", "missing", "reaction-type", "reaction-key", "bool", "float"],
)
def test_the_inputs_decoder_refuses_every_malformed_block(
    record: object, match: str
) -> None:
    """The inputs block decodes only to validated inputs."""
    with pytest.raises(DeviceConfigurationError, match=match):
        beam_inputs_from_record(record)
