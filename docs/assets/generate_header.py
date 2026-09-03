# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Beam Target Core — repository header artwork generator

"""Generate the three README header images (1280x640) for this repository.

Every image is original generated artwork derived from this repository's
own domain surface — the beam on a stationary target, the
one-versus-two beam-line class invariant, and the documented
centre-of-mass cross-section window. The right-hand text panel states
only facts backed by the repository itself.

Outputs (written next to this script):

- ``repo_header.png`` — the accelerator beam line, stationary target
  and reaction products (used by ``README.md``).
- ``repo_header_line_invariant.png`` — one beam line for a target,
  exactly two for colliding beams.
- ``repo_header_energy_window.png`` — the cross-section curve with the
  documented window and flagged energies on both sides.

Generation-time tooling only: requires ``numpy`` and ``matplotlib``,
which are deliberately not part of the pinned development lock. Run as
``python3 docs/assets/generate_header.py`` from the repository root.
The output is deterministic (fixed geometry, no random input).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

OUT_DIR = Path(__file__).resolve().parent

BG = "#00050a"
CYAN = "#00ccff"
MAGENTA = "#ff00ff"
STEEL = "#334466"
PROBE = "#66aaff"
RED = "#ff3366"
GREEN = "#3ddc84"

WIDTH_IN, HEIGHT_IN, DPI = 12.8, 6.4, 100

TITLE_METRICS: list[tuple[str, str]] = [
    ("Device Configurations", "beam_target · colliding_beam"),
    ("Beam-Line Invariant", "one for target, two for colliding"),
    ("Energy Window", "outside cross-section window flagged"),
    ("Reference", "Bosch & Hale, NF 32 (1992) 611"),
    ("Plan Envelope", "v1.1.0 · synthetic · review-only"),
    ("Quality Gates", "100% branch cov · mypy --strict"),
]


def _pyplot() -> Any:
    """Return pyplot configured for headless Agg rendering."""
    import matplotlib as mpl

    mpl.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _glow_cmap() -> Any:
    """Build the family glow colormap (deep navy to cyan)."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "scpn_glow",
        ["#00050a", "#001428", "#002d55", "#005588", "#0088bb", "#00ccff"],
    )


def _text_panel(fig: Any, subtitle: str) -> None:
    """Draw the family right-hand text panel onto ``fig``."""
    ax = fig.add_axes([0.62, 0.0, 0.38, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.08,
        0.84,
        "SCPN",
        color="white",
        fontsize=36,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.745,
        "BEAM TARGET",
        color="white",
        fontsize=25,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.695,
        "CORE",
        color="white",
        fontsize=25,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.635,
        subtitle,
        color=CYAN,
        fontsize=11,
        fontfamily="monospace",
        alpha=0.85,
    )
    ax.plot([0.08, 0.85], [0.595, 0.595], color=STEEL, lw=0.8, alpha=0.5)
    y = 0.535
    for label, value in TITLE_METRICS:
        ax.text(
            0.08,
            y,
            f"▸ {label}",
            color="#6688aa",
            fontsize=9,
            fontfamily="monospace",
            alpha=0.9,
        )
        ax.text(
            0.10,
            y - 0.030,
            value,
            color="#99bbdd",
            fontsize=8,
            fontfamily="monospace",
            alpha=0.7,
        )
        y -= 0.072
    ax.text(
        0.08,
        0.06,
        "© 1996–2026 Miroslav Šotek",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.6,
    )
    ax.text(
        0.08,
        0.03,
        "anulum.li | AGPL-3.0",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.5,
    )


def _art_axes(fig: Any) -> Any:
    """Return the borderless left-hand art axes of ``fig``."""
    ax = fig.add_axes([0.0, 0.0, 0.68, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _save(fig: Any, plt: Any, name: str) -> None:
    """Save ``fig`` to ``name`` inside the assets directory and close it."""
    target = OUT_DIR / name
    fig.savefig(target, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"generated {target}")


def _interaction_glow(
    ax: Any,
    centre_x: float,
    centre_z: float,
    core_radius: float,
    halo_radius: float,
) -> None:
    """Draw the glowing interaction region."""
    grid_x = np.linspace(centre_x - halo_radius, centre_x + halo_radius, 150)
    grid_z = np.linspace(centre_z - halo_radius, centre_z + halo_radius, 150)
    mesh_x, mesh_z = np.meshgrid(grid_x, grid_z)
    rho = np.sqrt((mesh_x - centre_x) ** 2 + (mesh_z - centre_z) ** 2) / core_radius
    ax.contourf(
        mesh_x,
        mesh_z,
        np.exp(-rho * 1.8),
        levels=28,
        cmap=_glow_cmap(),
        alpha=0.92,
    )


def _beamline(
    ax: Any,
    x_start: float,
    x_end: float,
    y_centre: float,
    plt: Any,
    direction: int = 1,
    magnets: int = 4,
    spread: float = 0.16,
) -> None:
    """Draw an accelerator beam line with focusing magnets."""
    for magnet_x in np.linspace(x_start, x_end - direction * 0.75, magnets):
        ax.add_patch(
            plt.Rectangle(
                (magnet_x - 0.18, y_centre - 0.30),
                0.36,
                0.60,
                fill=False,
                ec=STEEL,
                lw=1.5,
                alpha=0.85,
            )
        )
    for offset in (-spread, -spread / 2, 0.0, spread / 2, spread):
        along = np.linspace(0, 1, 120)
        ax.plot(
            x_start + (x_end - x_start) * along,
            y_centre + offset * (1 - along * 0.9),
            color=GREEN,
            lw=1.0,
            alpha=0.75,
        )
    ax.annotate(
        "",
        xy=(x_end, y_centre),
        xytext=(x_end - direction * 0.32, y_centre),
        arrowprops={
            "arrowstyle": "-|>",
            "color": GREEN,
            "lw": 1.6,
            "alpha": 0.95,
            "mutation_scale": 11,
        },
    )


def generate_beam_on_target() -> None:
    """Generate ``repo_header.png``: the beam on a stationary target."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-2.6, 2.6)

    _beamline(ax, 0.7, 5.05, 0.0, plt, direction=1, magnets=5)
    ax.text(
        2.6,
        0.72,
        "accelerator beam line",
        color="#667799",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        2.6,
        -0.78,
        "energetic light-ion beam",
        color=GREEN,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    _interaction_glow(ax, 5.55, 0.0, 0.38, 1.15)
    ax.add_patch(
        plt.Rectangle(
            (5.42, -1.15),
            0.30,
            2.3,
            fill=True,
            fc="#22303f",
            ec=STEEL,
            lw=1.8,
            alpha=0.9,
        )
    )
    ax.text(
        5.57,
        -1.45,
        "stationary target",
        color="#8899aa",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    for angle in np.linspace(-0.55, 0.55, 7):
        ax.plot(
            [5.72, 5.72 + 2.9 * np.cos(angle)],
            [0.0, 2.9 * np.sin(angle)],
            color=MAGENTA,
            lw=0.9,
            alpha=0.55,
        )
    ax.text(
        8.15,
        1.35,
        "reaction products",
        color=MAGENTA,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    ax.text(
        5.0,
        -2.35,
        "one beam line, one target · the simplest declared geometry",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "One Beam, One Target")
    _save(fig, plt, "repo_header.png")


def generate_line_invariant() -> None:
    """Generate ``repo_header_line_invariant.png``: one line or two."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-3.2, 3.2)

    y_top = 1.35
    _beamline(ax, 0.7, 4.35, y_top, plt, direction=1, magnets=4)
    _interaction_glow(ax, 4.75, y_top, 0.24, 0.7)
    ax.add_patch(
        plt.Rectangle(
            (4.64, y_top - 0.62),
            0.22,
            1.24,
            fill=True,
            fc="#22303f",
            ec=STEEL,
            lw=1.5,
            alpha=0.9,
        )
    )
    ax.text(
        6.85,
        y_top + 0.42,
        "beam_target",
        color="#99bbdd",
        fontsize=9,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        6.85,
        y_top + 0.05,
        "exactly one beam line",
        color="#667799",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    y_bottom = -1.35
    _beamline(ax, 0.7, 4.55, y_bottom, plt, direction=1, magnets=4)
    _beamline(ax, 8.9, 5.45, y_bottom, plt, direction=-1, magnets=4)
    _interaction_glow(ax, 5.0, y_bottom, 0.22, 0.62)
    ax.plot(5.0, y_bottom, "o", color="white", ms=5, alpha=0.95)
    ax.text(
        5.0,
        y_bottom + 0.85,
        "interaction point",
        color="white",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.85,
    )
    ax.text(
        5.0,
        y_bottom - 1.05,
        "colliding_beam · exactly two beam lines",
        color="#99bbdd",
        fontsize=9,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    ax.plot([0.7, 8.9], [0.0, 0.0], color=STEEL, lw=0.8, alpha=0.35)
    ax.text(
        5.0,
        2.85,
        "the beam-line count is a hard class invariant",
        color=PROBE,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        5.0,
        -2.95,
        "a declared line count contradicting the identifier is rejected",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "One Line Or Two, Never Both")
    _save(fig, plt, "repo_header_line_invariant.png")


def generate_energy_window() -> None:
    """Generate ``repo_header_energy_window.png``: the energy gate."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    ax.plot([1.0, 9.2], [1.7, 1.7], color=STEEL, lw=1.0, alpha=0.7)
    ax.plot([1.0, 1.0], [1.7, 9.1], color=STEEL, lw=1.0, alpha=0.7)
    ax.text(
        8.85,
        1.25,
        "centre-of-mass energy",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
        ha="right",
    )
    ax.text(
        1.15,
        8.85,
        "fusion cross-section",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
    )

    energy = np.linspace(0.02, 1.0, 400)
    shape = np.exp(-0.16 / energy) * np.exp(-1.5 * energy)
    peak = shape.max()
    ax.plot(
        1.0 + 8.0 * energy,
        1.7 + 6.6 * shape / peak,
        color=CYAN,
        lw=2.6,
        alpha=0.95,
    )
    ax.fill_between(
        1.0 + 8.0 * energy,
        1.7 + 6.6 * shape / peak,
        1.7,
        color=CYAN,
        alpha=0.06,
    )

    window_low, window_high = 0.22, 0.62
    x_low = 1.0 + 8.0 * window_low
    x_high = 1.0 + 8.0 * window_high
    ax.fill_between([x_low, x_high], 1.7, 9.0, color=GREEN, alpha=0.07)
    for edge_x in (x_low, x_high):
        ax.plot(
            [edge_x, edge_x],
            [1.7, 9.0],
            color=GREEN,
            lw=1.0,
            alpha=0.6,
            ls=(0, (5, 3)),
        )
    ax.text(
        (x_low + x_high) / 2,
        8.55,
        "documented cross-section window",
        color=GREEN,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    for fraction, inside in ((0.09, False), (0.40, True), (0.86, False)):
        value = np.exp(-0.16 / fraction) * np.exp(-1.5 * fraction) / peak
        mark_x, mark_y = 1.0 + 8.0 * fraction, 1.7 + 6.6 * value
        if inside:
            ax.plot(mark_x, mark_y, "o", color=CYAN, ms=7, alpha=0.95)
        else:
            ax.plot(
                mark_x,
                mark_y,
                "x",
                color=RED,
                ms=9,
                mew=2.2,
                alpha=0.95,
            )
    ax.text(
        1.75,
        3.1,
        "below window\n· FLAGGED",
        color="#ff8899",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        va="center",
        alpha=0.9,
    )
    ax.text(
        8.25,
        3.1,
        "above window\n· FLAGGED",
        color="#ff8899",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        va="center",
        alpha=0.9,
    )

    ax.text(
        5.0,
        0.95,
        "declared centre-of-mass energy checked against the documented "
        "light-ion window",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    ax.text(
        5.0,
        0.58,
        "Bosch & Hale, Nucl. Fusion 32 (1992) 611",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Energy Where The Cross-Section Lives")
    _save(fig, plt, "repo_header_energy_window.png")


if __name__ == "__main__":
    generate_beam_on_target()
    generate_line_invariant()
    generate_energy_window()
