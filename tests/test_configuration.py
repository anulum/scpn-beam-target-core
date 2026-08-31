# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — device configuration container tests

"""Every branch of the device configuration container and its parsers.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

from scpn_beam_target_core.configuration import (
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_beam_target_core.errors import DeviceConfigurationError
from scpn_beam_target_core.parameters import BeamLine

REGISTRY = RegistryBinding(version="1.0.0", digest_sha256="0" * 64)


def synthetic_configuration(
    identifier: str = "beam_target",
    beam_line_count: int = 1,
    kinetic_energy_kev: float = 120.0,
) -> DeviceConfiguration:
    """Build a valid synthetic configuration with optional overrides."""
    return DeviceConfiguration(
        identifier=identifier,
        beam=BeamLine(
            kinetic_energy_kev=kinetic_energy_kev,
            beam_current_ma=50.0,
        ),
        beam_line_count=beam_line_count,
        registry=REGISTRY,
    )


def test_registry_binding_rejects_bad_pins() -> None:
    """Malformed registry pins are rejected."""
    with pytest.raises(DeviceConfigurationError, match=r"registry\.version"):
        RegistryBinding(version="", digest_sha256="0" * 64)
    with pytest.raises(DeviceConfigurationError, match=r"registry\.digest_sha256"):
        RegistryBinding(version="1.0.0", digest_sha256="ZZ")


def test_both_owned_identifiers_construct() -> None:
    """Each owned identifier constructs with its beam-line count."""
    fixed = synthetic_configuration()
    collider = synthetic_configuration(
        "colliding_beam", beam_line_count=2, kinetic_energy_kev=40.0
    )
    assert fixed.identifier == "beam_target"
    assert collider.beam_line_count == 2


def test_unowned_identifier_is_rejected() -> None:
    """Identifiers outside this repository's ownership are rejected."""
    with pytest.raises(DeviceConfigurationError, match="not owned"):
        synthetic_configuration("gridded_iec")


def test_beam_line_count_class_invariants() -> None:
    """Beam-line counts must match the configuration class exactly."""
    with pytest.raises(DeviceConfigurationError, match="exactly 1"):
        synthetic_configuration(beam_line_count=2)
    with pytest.raises(DeviceConfigurationError, match="exactly 2"):
        synthetic_configuration("colliding_beam", beam_line_count=1)


def test_centre_of_mass_energy_formulas() -> None:
    """The c.m. energy follows two-body kinematics exactly."""
    fixed = synthetic_configuration()
    assert fixed.centre_of_mass_energy_kev() == pytest.approx(60.0)
    collider = synthetic_configuration(
        "colliding_beam", beam_line_count=2, kinetic_energy_kev=40.0
    )
    assert collider.centre_of_mass_energy_kev() == pytest.approx(80.0)


def test_consistency_report_clean_and_finding() -> None:
    """The report is empty in-window and precise outside it."""
    assert synthetic_configuration().consistency_report() == ()
    weak = synthetic_configuration(kinetic_energy_kev=4.0)
    findings = weak.consistency_report()
    assert len(findings) == 1
    assert "cross-section window" in findings[0].message


def test_canonical_round_trip_and_digest() -> None:
    """Canonical bytes round-trip losslessly and digest deterministically."""
    configuration = synthetic_configuration()
    data = configuration.canonical_bytes()
    assert data.endswith(b"\n")
    restored = configuration_from_bytes(data)
    assert restored == configuration
    expected = hashlib.sha256(data).hexdigest()
    assert configuration.digest_sha256() == expected


def test_from_record_round_trip_both_classes() -> None:
    """Both owned configuration classes round-trip through records."""
    for configuration in (
        synthetic_configuration(),
        synthetic_configuration(
            "colliding_beam", beam_line_count=2, kinetic_energy_kev=40.0
        ),
    ):
        assert configuration_from_record(configuration.to_record()) == configuration


@pytest.mark.parametrize(
    ("mutate", "fragment"),
    [
        (lambda _: "not-a-dict", "record: must be an object"),
        (lambda r: {**r, "extra": 1}, "unknown fields"),
        (lambda r: {**r, "beam": None}, "beam: must be an object"),
        (lambda r: {**r, "registry": 7}, "registry: must be an object"),
        (lambda r: {**r, "identifier": 3}, "identifier: must be a string"),
        (
            lambda r: {**r, "beam_line_count": "two"},
            "beam_line_count: must be an integer",
        ),
        (
            lambda r: {**r, "beam_line_count": True},
            "beam_line_count: must be an integer",
        ),
    ],
)
def test_from_record_shape_violations(mutate: Any, fragment: str) -> None:
    """Each record-shape violation is rejected with a precise message."""
    record = synthetic_configuration().to_record()
    with pytest.raises(DeviceConfigurationError, match=fragment):
        configuration_from_record(mutate(record))


def test_from_record_field_type_violations() -> None:
    """Nested field-type violations name the offending field."""
    record = synthetic_configuration().to_record()
    record["beam"]["kinetic_energy_kev"] = "big"
    with pytest.raises(DeviceConfigurationError, match="kinetic_energy_kev: must be"):
        configuration_from_record(record)
    record = synthetic_configuration().to_record()
    record["beam"]["beam_current_ma"] = True
    with pytest.raises(DeviceConfigurationError, match="beam_current_ma: must be"):
        configuration_from_record(record)
    record = synthetic_configuration().to_record()
    record["registry"]["version"] = None
    with pytest.raises(DeviceConfigurationError, match="version: must be a string"):
        configuration_from_record(record)


def test_from_bytes_rejects_invalid_documents() -> None:
    """Invalid UTF-8, invalid JSON, and non-finite literals are rejected."""
    with pytest.raises(DeviceConfigurationError, match="invalid JSON document"):
        configuration_from_bytes(b"\xff\xfe")
    with pytest.raises(DeviceConfigurationError, match="invalid JSON document"):
        configuration_from_bytes(b"{not json")
    record = synthetic_configuration().to_record()
    text = json.dumps(record).replace("120.0", "NaN", 1)
    with pytest.raises(DeviceConfigurationError, match="non-finite JSON literal"):
        configuration_from_bytes(text.encode("utf-8"))


def test_integer_accepted_where_number_expected() -> None:
    """Integral JSON numbers are accepted for real-valued fields."""
    record = synthetic_configuration().to_record()
    record["beam"]["kinetic_energy_kev"] = 120
    restored = configuration_from_record(record)
    assert restored.beam.kinetic_energy_kev == 120.0
