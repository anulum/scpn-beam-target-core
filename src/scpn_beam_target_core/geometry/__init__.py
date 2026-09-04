# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — device geometry package

"""Beam-line envelope and the two geometry tiers of the beam-target family.

The body set depends on the configuration: a beam-target device is a beam
pipe, a solid target and the dump behind it; a colliding-beam device is
two beam pipes facing each other, with nothing between them because the
beams are each other's target. Design record: ADR 0006.
"""

from __future__ import annotations

from scpn_beam_target_core.geometry.cad import (
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
from scpn_beam_target_core.geometry.device import (
    BEAMLINE_FIELDS,
    TARGET_FIELDS,
    BeamlineEnvelope,
    TargetAssembly,
    beamline_from_record,
    target_from_record,
)
from scpn_beam_target_core.geometry.model import (
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
    require_assembly,
    require_intercept,
)

__all__ = [
    "BEAMLINE_FIELDS",
    "BODY_BEAM_DUMP",
    "BODY_DOWNSTREAM_BEAMLINE",
    "BODY_NAMES_BY_IDENTIFIER",
    "BODY_TARGET",
    "BODY_UPSTREAM_BEAMLINE",
    "CAD_MODEL_NON_CLAIMS",
    "CAD_MODEL_SCHEMA",
    "CAD_MODEL_SCHEMA_VERSION",
    "CAD_MODEL_UNITS",
    "DEFAULT_ANGULAR_DEFLECTION_RAD",
    "DEFAULT_LINEAR_DEFLECTION_M",
    "DEFAULT_REFERENCE_MESH_SEGMENTS",
    "MODEL_NON_CLAIMS",
    "MODEL_SCHEMA",
    "MODEL_SCHEMA_VERSION",
    "MODEL_UNITS",
    "TARGET_FIELDS",
    "BeamlineEnvelope",
    "DeviceModel3D",
    "DeviceModelCAD",
    "TargetAssembly",
    "beamline_from_record",
    "build_device_cad",
    "build_device_model",
    "require_assembly",
    "require_intercept",
    "target_from_record",
]
