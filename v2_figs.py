#!/usr/bin/env python3
"""
V2. Figures for the TTS manuscript.

fig1  what a measured subgroup gap contains -- the three sources, as a schematic
fig2  per-group accuracy before and after the two label-side corrections,
      both datasets, with each group's annotation parameters on the axis
fig3  the cascade: reported gap, gap after corrections, and the sampling-noise
      floor each is measured against, for three groupings
fig4  the residual on SCUT is training representation: per-group accuracy with
      the training mix as collected and balanced
fig5  leave-one-population-out transfer, geometry against appearance
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "/home/claude/q1/scripts")
import ieee_style as S  # noqa: E402

S.apply()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

F = Path("/home/claude/tts/figs")
F.mkdir(parents=True, exist_ok=True)
Q, FX, SF, SR = (Path("/home/claude/q1/results"),
                 Path("/home/claude/fix/results"),
                 Path("/home/claude/scutfix/results"),
                 Path("/home/claude/scutrun/results"))

MEB_LBL = {"asian": "Asian", "black": "Black", "caucasian": "Caucasian",
           "hispanic": "Hispanic", "indian": "Indian",
           "mideastern": "Mid-Eastern"}
SCUT_LBL = {"asian_female": "Asian F", "asian_male": "Asian M",
            "caucasian_female": "Cauc. F", "caucasian_male": "Cauc. M"}


# ===================================================================== fig 1
def fig_schematic() -> None:
    """The quantity an audit reports, and the three things inside it."""
    fig, ax = plt.subplots(figsize=(S.COL1, 2.28))
    ax.set_xlim(-0.03, 1.03)
    ax.set_ylim(-0.03, 1.03)
    ax.axis("off")
    D = S.C["dark"]

    def box(x, y, w, h, t, fc, fs=6.5, bold=False, ec=None):
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.02",
            lw=0.6, edgecolor=ec or D, facecolor=fc, zorder=2))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center",
                fontsize=fs, zorder=3,
                fontweight="bold" if bold else "normal")

    def arr(p, q):
        ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=6,
                                     lw=0.7, color=D, shrinkA=1, shrinkB=1,
                                     zorder=1))

    box(0.16, 0.845, 0.68, 0.135,
        "reported disparity\n$\\max_g r_g - \\min_g r_g$", "#EDF0F3",
        fs=6.2, bold=True)

    cols = ["#DCE8F4", "#FBE6D4", "#DDF0E4"]
    texts = [
        "sampling noise\nfinite groups differ\nat equal skill",
        "annotation artefact\nunequal reliability\nand label spread",
        "model-side bias\nwhat the audit\nis meant to find",
    ]
    for i, (t, c) in enumerate(zip(texts, cols)):
        x = 0.015 + i * 0.335
        box(x, 0.455, 0.315, 0.275, t, c, fs=5.5)
        arr((0.5, 0.845), (x + 0.1575, 0.732))

    rem = [
        "simulate equal skill\nat the observed $n_g$",
        "$r/\\sqrt{\\rho_g}$,\nThorndike case II",
        "attributable,\nand actionable",
    ]
    for i, t in enumerate(rem):
        x = 0.015 + i * 0.335
        box(x, 0.145, 0.315, 0.225, t, "#FFFFFF", fs=5.5, ec=S.C["grey"])
        arr((x + 0.1575, 0.455), (x + 0.1575, 0.372))

    ax.text(0.5, 0.055, "a finding only if the first two are removed first",
            ha="center", va="center", fontsize=6.2, style="italic",
            color=S.C["grey"])
    S.save(fig, str(F / "fig1_decomposition"))


# ===================================================================== fig 2
def fig_per_group() -> None:
    """Observed and corrected per-group accuracy, with annotation parameters."""
    meb = pd.read_csv(FX / "table_label_bias_v2.csv")
    meb["lbl"] = meb.group.map(MEB_LBL)
    meb = meb.sort_values("r_fusion")
    sc = pd.read_csv(SR / "scut_group_decomposition.csv")
    sc = sc[sc.grouping == "subgroup"].copy()
    sc["lbl"] = sc.group.map(SCUT_LBL)
    sc = sc.sort_values("r")

    fig, axes = plt.subplots(1, 2, figsize=(S.COL2, 2.18),
                             gridspec_kw={"width_ratios": [1.32, 1.0],
                                          "wspace": 0.42})
    panels = [
        (axes[0], meb, "r_fusion", "r_fully_corrected", "sd_ratio",
         "ceiling", "(a) MEBeauty, 6 populations"),
        (axes[1], sc, "r", "r_both", "u", "ceiling",
         "(b) SCUT-FBP5500, 4 subgroups"),
    ]
    for ax, d, raw, cor, uc, ce, title in panels:
        y = np.arange(len(d))
        ax.hlines(y, d[raw], d[cor], color=S.C["grey"], lw=1.0, zorder=1)
        ax.scatter(d[raw], y, s=22, color=S.C["blue"], zorder=3,
                   label="as measured", edgecolor="white", linewidth=0.4)
        ax.scatter(d[cor], y, s=22, color=S.C["red"], zorder=3, marker="D",
                   label="label-side corrected", edgecolor="white",
                   linewidth=0.4)
        ax.set_yticks(y)
        ax.set_yticklabels(
            [f"{l}\n$\\rho${r_:.3f}  $u${u_:.2f}" for l, r_, u_ in
             zip(d["lbl"], d[ce] ** 2, d[uc])], fontsize=5.6)
        ax.set_xlabel("Pearson $r$ against the group's own labels")
        ax.set_title(title, fontsize=7.2, pad=3)
        ax.grid(True, axis="x")
        ax.set_axisbelow(True)
        lo = min(d[raw].min(), d[cor].min())
        hi = max(d[raw].max(), d[cor].max())
        ax.set_xlim(lo - 0.055, hi + 0.045)
        for yy, a, b in zip(y, d[raw], d[cor]):
            ax.annotate("", xy=(b, yy), xytext=(a, yy),
                        arrowprops=dict(arrowstyle="-|>", lw=0.0,
                                        color=S.C["grey"], mutation_scale=5))
    axes[0].legend(loc="upper left", fontsize=6.2, handletextpad=0.3,
                   borderpad=0.25)
    S.save(fig, str(F / "fig2_per_group"))


# ===================================================================== fig 3
def fig_cascade() -> None:
    """Reported gap and corrected gap, each against its own noise floor."""
    meb = json.load(open(SF / "s5_reframe.json"))
    sc = json.load(open(SR / "t2_scut.json"))

    meb_gap_both = 0.0
    lb = pd.read_csv(FX / "table_label_bias_v2.csv")
    meb_gap_both = float(lb.r_fully_corrected.max() - lb.r_fully_corrected.min())
    meb_floor_both = meb_gap_both - meb["excess_corrected"]

    rows = [
        ("MEBeauty\n6 populations\n$n=1{,}391$",
         meb["obs_gap"], meb["null_gap_mean"],
         meb_gap_both, meb_floor_both, meb["p_gap"]),
        ("SCUT-FBP5500\n4 subgroups\n$n=5{,}429$",
         sc["subgroup"]["gap_raw"], sc["subgroup"]["noise_floor"],
         sc["subgroup"]["gap_both"],
         sc["subgroup"]["gap_both"] - sc["subgroup"]["excess_both"],
         sc["subgroup"]["p_vs_noise"]),
        ("SCUT-FBP5500\n2 ethnicities\n$n=5{,}429$",
         sc["ethnicity"]["gap_raw"], sc["ethnicity"]["noise_floor"],
         sc["ethnicity"]["gap_both"],
         sc["ethnicity"]["gap_both"] - sc["ethnicity"]["excess_both"],
         sc["ethnicity"]["p_vs_noise"]),
    ]

    fig, ax = plt.subplots(figsize=(S.COL2, 2.35))
    h, pad = 0.30, 1.00
    yt, ytl = [], []
    for i, (lbl, g_raw, f_raw, g_cor, f_cor, p) in enumerate(rows):
        base = i * pad
        for j, (g, f, tag) in enumerate(
                ((g_raw, f_raw, "as reported"),
                 (g_cor, f_cor, "corrected"))):
            y = base + (0.215 if j == 0 else -0.215)
            ax.barh(y, f, height=h, color="#C9D6E4", edgecolor=S.C["dark"],
                    lw=0.5, zorder=2,
                    label="sampling-noise floor" if i == 0 and j == 0 else None)
            resid = g - f
            ax.barh(y, max(resid, 0.0), left=f, height=h,
                    color=S.C["red"], edgecolor=S.C["dark"], lw=0.5, zorder=2,
                    label="excess over the floor"
                    if i == 0 and j == 0 else None)
            if resid < 0:
                ax.barh(y, -resid, left=g, height=h, color="white",
                        edgecolor=S.C["grey"], lw=0.5, hatch="////", zorder=2,
                        label="below the floor" if i == 0 else None)
            ax.plot([g, g], [y - h / 2, y + h / 2], color=S.C["dark"], lw=1.1,
                    zorder=4)
            ax.text(max(g, f) + 0.006, y,
                    f"{tag}:  gap {g:.3f},  excess "
                    f"{resid:+.3f}".replace("-", "\u2212"),
                    va="center", fontsize=6.0, zorder=5)
        yt.append(base)
        ytl.append(lbl)
        ax.text(0.004, base + 0.215 + h / 2 + 0.055,
                f"$p$ = {p:.3f}" if p > 0.001 else "$p$ < 0.001",
                fontsize=5.9, color=S.C["dark"], va="bottom", style="italic")

    ax.set_yticks(yt)
    ax.set_yticklabels(ytl, fontsize=6.4)
    ax.set_ylim(-0.60, 2 * pad + 0.72)
    ax.set_xlim(0, 0.345)
    ax.set_xlabel("max$-$min Pearson $r$ across groups")
    ax.grid(True, axis="x")
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", fontsize=6.1, handlelength=1.2,
              handletextpad=0.4, borderpad=0.3)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)
    S.save(fig, str(F / "fig3_cascade"))


# ===================================================================== fig 4
def fig_balance() -> None:
    """Balancing the training mix against the residual disparity."""
    b = json.load(open(SR / "t3_balance.json"))
    fig, ax = plt.subplots(figsize=(S.COL1, 1.92))
    groups = ["asian", "caucasian"]
    lbl = {"asian": "Asian\n(3,982 faces)", "caucasian": "Caucasian\n(1,447)"}
    x = np.arange(2)
    w = 0.33
    for k, (tag, col, hatch) in enumerate(
            (("unbalanced", S.C["blue"], ""),
             ("balanced", S.C["orange"], "///"))):
        v = [b[tag]["per_group_r"][g] for g in groups]
        ax.bar(x + (k - 0.5) * w, v, w, color=col, hatch=hatch,
               edgecolor="white", lw=0.4, zorder=3,
               label="training mix as collected" if k == 0
               else "training mix balanced")
        for xi, vi in zip(x + (k - 0.5) * w, v):
            ax.text(xi, vi + 0.006, f"{vi:.3f}", ha="center", fontsize=5.9,
                    zorder=4)
    for k, tag in enumerate(("unbalanced", "balanced")):
        g = b[tag]["gap"]
        ax.plot([-0.42 + k * 0.02, 1.42], [0.60 - k * 0.018] * 2, lw=0)
    ax.set_xticks(x)
    ax.set_xticklabels([lbl[g] for g in groups], fontsize=6.4)
    ax.set_ylabel("Pearson $r$")
    ax.set_ylim(0.55, 0.80)
    ax.grid(True, axis="y")
    ax.set_axisbelow(True)
    ax.legend(loc="upper center", fontsize=5.9, ncol=1, handlelength=1.3,
              handletextpad=0.4, borderpad=0.25)
    ax.set_title(f"gap {b['unbalanced']['gap']:.3f} $\\rightarrow$ "
                 f"{b['balanced']['gap']:.3f}   "
                 f"pooled {b['unbalanced']['pooled_r']:.3f} $\\rightarrow$ "
                 f"{b['balanced']['pooled_r']:.3f}", fontsize=6.6, pad=3)
    S.save(fig, str(F / "fig4_balance"))


# ===================================================================== fig 5
def fig_loeo() -> None:
    """Held-out-population transfer: geometry against appearance."""
    lo = pd.read_csv(FX / "table_loeo_v2.csv")
    piv = lo.pivot_table(index="held_out", columns="mode", values="PC",
                         aggfunc="mean")
    order = piv["geometry"].sort_values().index.tolist()
    piv = piv.reindex(order)
    fig, ax = plt.subplots(figsize=(S.COL1, 1.95))
    x = np.arange(len(piv))
    w = 0.27
    series = [("geometry", "geometry (56)", S.C["blue"], ""),
              ("appearance_512", "appearance (512)", S.C["orange"], "///"),
              ("fusion_512", "fusion", S.C["green"], "...")]
    for k, (c, lab, col, hatch) in enumerate(series):
        ax.bar(x + (k - 1) * w, piv[c], w, color=col, hatch=hatch,
               edgecolor="white", lw=0.35, label=lab, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels([MEB_LBL[g] for g in piv.index], fontsize=6.0,
                       rotation=28, ha="right")
    ax.set_ylabel("Pearson $r$ on the held-out\npopulation", fontsize=7)
    ax.set_ylim(0, 0.97)
    ax.grid(True, axis="y")
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", fontsize=6.0, ncol=3, handlelength=1.1,
              handletextpad=0.3, columnspacing=0.7, borderpad=0.2)
    S.save(fig, str(F / "fig5_loeo"))


def main() -> int:
    for fn in (fig_schematic, fig_per_group, fig_cascade, fig_balance,
               fig_loeo):
        try:
            fn()
            print("  ok", fn.__name__)
        except Exception as exc:
            import traceback
            print(f"  !! {fn.__name__}: {type(exc).__name__}: {exc}")
            traceback.print_exc()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
