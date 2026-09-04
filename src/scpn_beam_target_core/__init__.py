# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — device capability package

"""Device capability models of the SCPN beam-target device family.

Public surface of the ``device_configuration_model``,
``diagnostic_clock_semantics``, ``level0_device_physics``,
``device_3d_model`` and ``device_cad_model`` capabilities at
``computational_prototype`` maturity: validated parameter objects,
synthetic diagnostic and clock declarations aligned with the pinned SPO
observability catalogue, the published cross-section fit of the light-ion
reactions with the frame it was made in stated, the tessellated and B-rep
models of a beam line and what it fires into,
documented consistency estimates, canonical serialisation with SHA-256
digests, and data-only pins to the SPO registries. No claim about any
real machine or diagnostic is made anywhere in this package.
"""

from __future__ import annotations

from typing import Final

from scpn_beam_target_core.configuration import (
    BEAM_LINES_BY_IDENTIFIER,
    CM_ENERGY_WINDOW_KEV,
    OWNED_CONFIGURATIONS,
    ConsistencyFinding,
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_beam_target_core.errors import (
    DeviceConfigurationError,
    DeviceGeometryError,
    DiagnosticPlanError,
)
from scpn_beam_target_core.geometry import (
    BODY_NAMES_BY_IDENTIFIER,
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    BeamlineEnvelope,
    DeviceModel3D,
    DeviceModelCAD,
    TargetAssembly,
    beamline_from_record,
    build_device_cad,
    build_device_model,
    target_from_record,
)
from scpn_beam_target_core.observability import (
    APPLICABLE_CANDIDATES,
    CATALOGUE_BINDING,
    CandidateProfile,
    ClockKind,
    ClockModel,
    ClockRelation,
    DeferredCandidate,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    FrameKind,
    ObservabilityBinding,
    ObservabilityClass,
    ReferenceFrame,
    SemanticCarrier,
    plan_from_bytes,
    plan_from_record,
)
from scpn_beam_target_core.parameters import BeamLine
from scpn_beam_target_core.physics import (
    DT_LAB_ENERGY_RATIO,
    EQUAL_MASS_LAB_ENERGY_RATIO,
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    REACTIONS,
    BeamInputs,
    Level0Physics,
    OperatingPoint,
    beam_power_w,
    ion_rate_per_s,
    level0_physics,
    maxwellian_reactivity_cm3_per_s,
    total_cross_section_barn,
)
from scpn_beam_target_core.plan_envelope import (
    PlanEnvelope,
    envelope_for_plan,
    envelope_from_bytes,
    envelope_from_record,
    verify_envelope,
)

__version__: Final = "0.1.0.dev0"

__all__ = [
    "APPLICABLE_CANDIDATES",
    "BEAM_LINES_BY_IDENTIFIER",
    "BODY_NAMES_BY_IDENTIFIER",
    "CAD_MODEL_NON_CLAIMS",
    "CAD_MODEL_SCHEMA",
    "CAD_MODEL_SCHEMA_VERSION",
    "CATALOGUE_BINDING",
    "CM_ENERGY_WINDOW_KEV",
    "DT_LAB_ENERGY_RATIO",
    "EQUAL_MASS_LAB_ENERGY_RATIO",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MODEL_NON_CLAIMS",
    "MODEL_SCHEMA",
    "MODEL_SCHEMA_VERSION",
    "OWNED_CONFIGURATIONS",
    "REACTIONS",
    "BeamInputs",
    "BeamLine",
    "BeamlineEnvelope",
    "CandidateProfile",
    "ClockKind",
    "ClockModel",
    "ClockRelation",
    "ConsistencyFinding",
    "DeferredCandidate",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "DeviceGeometryError",
    "DeviceModel3D",
    "DeviceModelCAD",
    "DiagnosticChannelPlan",
    "DiagnosticPlan",
    "DiagnosticPlanError",
    "FrameKind",
    "Level0Physics",
    "ObservabilityBinding",
    "ObservabilityClass",
    "OperatingPoint",
    "PlanEnvelope",
    "ReferenceFrame",
    "RegistryBinding",
    "SemanticCarrier",
    "TargetAssembly",
    "__version__",
    "beam_power_w",
    "beamline_from_record",
    "build_device_cad",
    "build_device_model",
    "configuration_from_bytes",
    "configuration_from_record",
    "envelope_for_plan",
    "envelope_from_bytes",
    "envelope_from_record",
    "ion_rate_per_s",
    "level0_physics",
    "maxwellian_reactivity_cm3_per_s",
    "plan_from_bytes",
    "plan_from_record",
    "target_from_record",
    "total_cross_section_barn",
    "verify_envelope",
]
