#!/usr/bin/env python3
"""
V1. Does each estimator in the decomposition do what it claims?

A correction that cannot be shown to recover a known answer is an assertion.
Three checks, each with an answer fixed in advance:

  1. Attenuation. Generate a predictor with known true correlation rho against
     a latent trait, then observe it against a noisy label of known
     reliability. Dividing by sqrt(reliability) must return rho.
  2. Range restriction. Generate groups that differ only in the spread of the
     latent trait. Thorndike case II must return the same corrected value for
     each, and the uncorrected values must differ.
  3. Sampling-noise floor. Generate groups with identical true skill and
     identical annotation quality, differing only in size, and record the
     max-min spread of their observed correlations. The result is the gap an
     audit will report when there is nothing whatever to find.

Everything is written to results/ as the single source for the paper's
validation table.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/tts/results")
OUT.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(20261007)

N_BIG = 200_000
N_SIM = 4000


def thorndike(r: float, u: float) -> float:
    """Case II correction for restriction on the predictor's own range."""
    return u * r / np.sqrt(1.0 + r * r * (u * u - 1.0))


# ---------------------------------------------------------------- check 1
rows = []
RHO = 0.80
for rel in (0.85, 0.90, 0.95):
    T = RNG.normal(0, 1, N_BIG)
    P = RHO * T + RNG.normal(0, np.sqrt(1 - RHO ** 2), N_BIG)
    Y = T + RNG.normal(0, np.sqrt((1 - rel) / rel), N_BIG)
    r = float(stats.pearsonr(P, Y)[0])
    rows.append({"check": "attenuation", "parameter": f"reliability {rel:.2f}",
                 "true_rho": RHO, "observed": r,
                 "expected_observed": RHO * np.sqrt(rel),
                 "corrected": r / np.sqrt(rel)})

# ---------------------------------------------------------------- check 2
# A group is "restricted" when its label spread is narrower than the pooled
# spread. Realise that by truncating the label, which is selection on the
# variable u is computed from -- exactly the case Thorndike II covers.
T = RNG.normal(0, 1, N_BIG)
P = RHO * T + RNG.normal(0, np.sqrt(1 - RHO ** 2), N_BIG)
sd_pooled = float(T.std(ddof=1))
for cut in (3.0, 1.2, 0.8):
    sel = np.abs(T) < cut
    Ts, Ps = T[sel], P[sel]
    r = float(stats.pearsonr(Ps, Ts)[0])
    u = sd_pooled / float(Ts.std(ddof=1))
    rows.append({"check": "range restriction",
                 "parameter": f"u={u:.3f} (n={int(sel.sum()):,})",
                 "true_rho": RHO, "observed": r,
                 "expected_observed": np.nan,
                 "corrected": thorndike(r, u)})

pd.DataFrame(rows).to_csv(OUT / "v1_estimator_recovery.csv", index=False)
for r in rows:
    print(f"  {r['check']:18s} {r['parameter']:20s} observed {r['observed']:.4f}"
          f"  corrected {r['corrected']:.4f}  (true {r['true_rho']:.2f})")

# ---------------------------------------------------------------- check 3
designs = {
    "MEBeauty, 6 groups": [581, 197, 193, 174, 174, 72],
    "SCUT-FBP5500, 4 subgroups": [1993, 1989, 728, 719],
    "SCUT-FBP5500, 2 ethnicities": [3982, 1447],
}
floor = []
for name, ns in designs.items():
    for rho_t in (0.60, 0.70, 0.80):
        gaps = np.empty(N_SIM)
        sds = np.empty(N_SIM)
        for i in range(N_SIM):
            rs = np.empty(len(ns))
            for j, n in enumerate(ns):
                T = RNG.normal(0, 1, n)
                P = rho_t * T + RNG.normal(0, np.sqrt(1 - rho_t ** 2), n)
                rs[j] = stats.pearsonr(P, T)[0]
            gaps[i] = rs.max() - rs.min()
            sds[i] = rs.std(ddof=1)
        floor.append({"design": name, "n_groups": len(ns), "rho": rho_t,
                      "expected_gap": float(gaps.mean()),
                      "p95_gap": float(np.percentile(gaps, 95)),
                      "expected_sd": float(sds.mean())})
        print(f"  {name:28s} rho={rho_t:.2f}  floor {gaps.mean():.4f}"
              f"  (95th {np.percentile(gaps, 95):.4f})")

pd.DataFrame(floor).to_csv(OUT / "v1_noise_floor.csv", index=False)
json.dump({"n_big": N_BIG, "n_sim": N_SIM, "seed": 20261007},
          open(OUT / "v1_meta.json", "w"), indent=2)
print("done")
