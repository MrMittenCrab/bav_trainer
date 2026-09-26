"""Shared Matplotlib style derived from root STYLE.md.

Individual figures must not set typography, spacing, or palettes.
Fonts are resolved from the host; they are never copied into the repository.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
from matplotlib import font_manager, ft2font, pyplot as plt


PT = 1 / 72
TITLE_PT = 11
LABEL_PT = 9
RELATED_PT = 8
SECTION_PT = 16
LINE_SPACING = 1.25
BLACK = "#000000"
WHITE = "#FFFFFF"
GRAY = ("#000000", "#4D4D4D", "#808080", "#B3B3B3")
LATIN_FACE = "Aptos"
CJK_FACE = "DengXian"
LATIN_FILES = ("Aptos.ttf",)
CJK_FILES = ("Deng.ttf",)
SEARCH_DIRS = (
    Path("/Applications/Microsoft Excel.app/Contents/Resources/DFonts"),
    Path("/Applications/Microsoft Word.app/Contents/Resources/DFonts"),
    Path("/Library/Fonts"),
    Path.home() / "Library/Fonts",
)
FIGURE_SIZE = (7.5, 4.8)
FIGURE_DPI = 150
# Aptos and DengXian contain U+0020, not U+2002. One U+0020 advance is too
# narrow under Agg at figure sizes; repeat the supported space until the
# rasterized gap is visible. Never use a codepoint missing from the faces.
SPACE_CODEPOINT = 0x20
MIN_WORD_GAP_EM = 0.65
_SPACE_PROBES = ("Revenue growth", "store-count growth", "2 Feb 2025")
_ACTIVE_WORD_SPACE = " "
_VERIFIED_WORD_SPACE: tuple[tuple[Path, Path], str] | None = None


@dataclass(frozen=True)
class ResolvedFonts:
    latin_name: str
    latin_path: Path
    cjk_name: str
    cjk_path: Path


@dataclass(frozen=True)
class ResearchStyle:
    """STYLE.md figure implementation. Accent is optional and off by default."""

    fonts: ResolvedFonts
    accent: str | None = None
    accent_role: str = "latest fiscal period"

    title_pt: float = TITLE_PT
    label_pt: float = LABEL_PT
    related_pt: float = RELATED_PT
    section_pt: float = SECTION_PT
    black: str = BLACK
    white: str = WHITE
    word_space: str = " "

    def series_color(self, index: int, *, highlight: bool = False) -> str:
        if highlight and self.accent:
            return self.accent
        return GRAY[index % len(GRAY)]


def _candidate_files(filenames: tuple[str, ...]) -> list[Path]:
    found: list[Path] = []
    for directory in SEARCH_DIRS:
        if not directory.is_dir():
            continue
        for name in filenames:
            path = directory / name
            if path.is_file() and path not in found:
                found.append(path)
    return found


def _register(path: Path) -> str:
    font_manager.fontManager.addfont(str(path))
    return font_manager.FontProperties(fname=str(path)).get_name()


def _resolved_path(family: str, path: Path) -> Path:
    located = Path(
        font_manager.findfont(
            font_manager.FontProperties(family=family, weight="regular"),
            fallback_to_default=False,
        )
    )
    if located.resolve() != path.resolve():
        raise ValueError(
            f"required font {family!r} resolved to {located}, not {path}"
        )
    return located


def resolve_required_fonts() -> ResolvedFonts:
    """Resolve Aptos Regular and DengXian Regular without substitution."""
    missing: list[str] = []
    latin_files = _candidate_files(LATIN_FILES)
    cjk_files = _candidate_files(CJK_FILES)
    if not latin_files:
        missing.append(f"{LATIN_FACE} Regular")
    if not cjk_files:
        missing.append(f"{CJK_FACE} Regular")
    if missing:
        raise ValueError(
            "required fonts unavailable (no silent substitution): "
            + ", ".join(missing)
        )
    latin_path = latin_files[0]
    cjk_path = cjk_files[0]
    latin_name = _register(latin_path)
    cjk_name = _register(cjk_path)
    _resolved_path(latin_name, latin_path)
    _resolved_path(cjk_name, cjk_path)
    return ResolvedFonts(latin_name, latin_path, cjk_name, cjk_path)


def _font_has_codepoint(path: Path, codepoint: int) -> bool:
    return codepoint in ft2font.FT2Font(str(path)).get_charmap()


def _ink_gap_px(text: str, *, pt: float) -> float:
    """Largest interior column gap in an Agg raster of *text* at *pt*."""
    fig = plt.figure(figsize=(7.0, 0.6), dpi=FIGURE_DPI)
    fig.patch.set_facecolor(WHITE)
    fig.text(0.02, 0.45, text, fontsize=pt, color=BLACK, ha="left", va="center")
    fig.canvas.draw()
    ink_cols = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].min(axis=2) < 200
    ink_cols = ink_cols.any(axis=0)
    plt.close(fig)
    gaps: list[int] = []
    index = 0
    width = int(ink_cols.size)
    while index < width:
        if ink_cols[index]:
            index += 1
            continue
        end = index
        while end < width and not ink_cols[end]:
            end += 1
        if index > 0 and end < width:
            gaps.append(end - index)
        index = end
    return float(max(gaps) if gaps else 0.0)


def _min_visible_gap_px(pt: float) -> float:
    return pt * FIGURE_DPI * PT * MIN_WORD_GAP_EM


def _verified_word_space(fonts: ResolvedFonts) -> str:
    """Supported U+0020, repeated until Agg shows a visible word gap."""
    global _VERIFIED_WORD_SPACE
    key = (fonts.latin_path.resolve(), fonts.cjk_path.resolve())
    if _VERIFIED_WORD_SPACE and _VERIFIED_WORD_SPACE[0] == key:
        return _VERIFIED_WORD_SPACE[1]
    if not _font_has_codepoint(fonts.latin_path, SPACE_CODEPOINT):
        raise ValueError(
            f"{LATIN_FACE} Regular lacks U+0020 (no silent substitution)"
        )
    if not _font_has_codepoint(fonts.cjk_path, SPACE_CODEPOINT):
        raise ValueError(
            f"{CJK_FACE} Regular lacks U+0020 (no silent substitution)"
        )
    for count in range(1, 8):
        space = chr(SPACE_CODEPOINT) * count
        if all(
            _ink_gap_px(phrase.replace(" ", space), pt=pt) >= _min_visible_gap_px(pt)
            for pt in (TITLE_PT, LABEL_PT)
            for phrase in _SPACE_PROBES
        ):
            _VERIFIED_WORD_SPACE = (key, space)
            return space
    raise ValueError(
        "required fonts' U+0020 does not produce visible word separation "
        "under the Agg renderer"
    )


def apply_research_style(*, accent: str | None = None) -> ResearchStyle:
    """Apply the single STYLE.md Matplotlib implementation."""
    fonts = resolve_required_fonts()
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [fonts.latin_name, fonts.cjk_name],
            "font.weight": "regular",
            "font.size": LABEL_PT,
            "axes.titlesize": TITLE_PT,
            "axes.titleweight": "regular",
            "axes.labelsize": LABEL_PT,
            "axes.labelweight": "regular",
            "axes.titlepad": RELATED_PT,
            "axes.labelpad": RELATED_PT,
            "axes.facecolor": WHITE,
            "axes.edgecolor": BLACK,
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "axes.unicode_minus": True,
            "xtick.labelsize": LABEL_PT,
            "ytick.labelsize": LABEL_PT,
            "xtick.color": BLACK,
            "ytick.color": BLACK,
            "text.color": BLACK,
            "figure.facecolor": WHITE,
            "figure.edgecolor": WHITE,
            "figure.titlesize": TITLE_PT,
            "figure.titleweight": "regular",
            "figure.dpi": FIGURE_DPI,
            "savefig.dpi": FIGURE_DPI,
            "savefig.facecolor": WHITE,
            "savefig.edgecolor": WHITE,
            "legend.fontsize": LABEL_PT,
            "legend.frameon": False,
            "legend.borderpad": 0,
            "legend.labelspacing": RELATED_PT * PT,
            "lines.solid_joinstyle": "miter",
            "patch.linewidth": 0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    if "font.enable_last_resort" in plt.rcParams:
        plt.rcParams["font.enable_last_resort"] = False
    global _ACTIVE_WORD_SPACE
    _ACTIVE_WORD_SPACE = _verified_word_space(fonts)
    return ResearchStyle(fonts=fonts, accent=accent, word_space=_ACTIVE_WORD_SPACE)


def new_figure(style: ResearchStyle):
    fig, ax = plt.subplots(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
    fig.patch.set_facecolor(style.white)
    ax.set_facecolor(style.white)
    fig.subplots_adjust(
        left=0.11,
        right=0.97,
        top=0.82,
        bottom=0.24,
    )
    return fig, ax


def spaced(text: str, space: str | None = None) -> str:
    token = _ACTIVE_WORD_SPACE if space is None else space
    return text.replace(" ", token)


def _space_figure_text(fig, space: str) -> None:
    for artist in fig.findobj(plt.Text):
        artist.set_text(spaced(artist.get_text(), space))


def finish_figure(fig, ax, style: ResearchStyle, title: str, source: str, path: Path):
    ax.set_title(title, loc="left", color=style.black)
    ax.tick_params(colors=style.black, width=0.8)
    for spine in ax.spines.values():
        spine.set_color(style.black)
    fig.text(
        0.11,
        0.06,
        source,
        ha="left",
        va="bottom",
        color=style.black,
        fontsize=style.label_pt,
        linespacing=LINE_SPACING,
    )
    _space_figure_text(fig, style.word_space)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        path,
        dpi=FIGURE_DPI,
        facecolor=style.white,
        edgecolor=style.white,
        bbox_inches=None,
        metadata={"Software": "", "Creation Time": ""},
    )
    plt.close(fig)
