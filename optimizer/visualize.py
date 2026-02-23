"""Visualization utilities for optimization results.

All ``plot_*`` functions return a matplotlib Figure so callers can
``plt.show()`` **outside** the OpenRocketInstance context (JVM shutdown
requirement).
"""

from __future__ import annotations

import math

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from optimizer.design_space import OptimizationProblem


# ---------------------------------------------------------------------------
# Pareto front
# ---------------------------------------------------------------------------

def plot_pareto_front(
    pareto_result: dict,
    problem: OptimizationProblem,
    top3: list[dict] | None = None,
) -> Figure:
    """Scatter plot of the Pareto front (2-objective only)."""
    F = pareto_result["F"]
    obj_names = [o.name for o in problem.objectives]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(F[:, 0], F[:, 1], c="steelblue", alpha=0.5, s=20, label="Pareto front")

    if top3:
        colors = ["red", "green", "orange"]
        markers = ["*", "D", "s"]
        for i, cand in enumerate(top3):
            f = cand["f"]
            ax.scatter(
                f[0], f[1],
                c=colors[i % len(colors)],
                marker=markers[i % len(markers)],
                s=200, zorder=5, edgecolors="black",
                label=cand["label"],
            )

    ax.set_xlabel(obj_names[0])
    ax.set_ylabel(obj_names[1] if len(obj_names) > 1 else "")
    ax.set_title("Pareto Front")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# DOE summary
# ---------------------------------------------------------------------------

def plot_doe_summary(
    doe_results: list[dict],
    problem: OptimizationProblem,
) -> Figure:
    """Scatter matrix: each design variable vs each objective."""
    var_names = [v.name for v in problem.variables]
    obj_names = [o.name for o in problem.objectives]

    n_var = len(var_names)
    n_obj = len(obj_names)

    X = np.array([r["x"] for r in doe_results])
    feasible = np.array([r.get("feasible", True) for r in doe_results])

    fig, axes = plt.subplots(n_obj, n_var, figsize=(4 * n_var, 3.5 * n_obj), squeeze=False)

    for row, obj_name in enumerate(obj_names):
        y = np.array([r.get(obj_name, float("nan")) for r in doe_results])
        for col, var_name in enumerate(var_names):
            ax = axes[row, col]
            # Plot infeasible in grey, feasible in blue
            mask_f = feasible & ~np.isnan(y)
            mask_i = ~feasible & ~np.isnan(y)
            if mask_i.any():
                ax.scatter(X[mask_i, col], y[mask_i], c="grey", alpha=0.4, s=15, label="infeasible")
            if mask_f.any():
                ax.scatter(X[mask_f, col], y[mask_f], c="steelblue", alpha=0.7, s=25, label="feasible")
            ax.set_xlabel(var_name)
            ax.set_ylabel(obj_name)
            ax.grid(True, alpha=0.3)

    fig.suptitle("DOE: Variables vs Objectives", fontsize=14)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Candidate comparison
# ---------------------------------------------------------------------------

def plot_candidate_comparison(
    top3: list[dict],
    problem: OptimizationProblem,
) -> Figure:
    """Bar chart comparing top-3 candidates across all objectives."""
    obj_names = [o.name for o in problem.objectives]
    n_obj = len(obj_names)
    n_cand = len(top3)

    x_pos = np.arange(n_obj)
    width = 0.25

    fig, ax = plt.subplots(figsize=(max(6, 2 * n_obj), 5))
    colors = ["#e74c3c", "#2ecc71", "#f39c12"]

    for i, cand in enumerate(top3):
        vals = [cand["f"][j] for j in range(n_obj)]
        offset = (i - (n_cand - 1) / 2) * width
        ax.bar(x_pos + offset, vals, width, label=cand["label"], color=colors[i % len(colors)])

    ax.set_xticks(x_pos)
    ax.set_xticklabels(obj_names)
    ax.set_ylabel("Objective Value")
    ax.set_title("Top-3 Candidate Comparison")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Results table (Markdown)
# ---------------------------------------------------------------------------

def format_results_table(
    top3: list[dict],
    problem: OptimizationProblem,
) -> str:
    """Format top-3 candidates as a Markdown table."""
    var_names = [v.name for v in problem.variables]
    obj_names = [o.name for o in problem.objectives]

    headers = ["Candidate"] + var_names + obj_names
    rows: list[str] = []
    rows.append("| " + " | ".join(headers) + " |")
    rows.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for cand in top3:
        cells = [cand["label"]]
        for j, vn in enumerate(var_names):
            v = cand["x"][j]
            if problem.variables[j].is_integer:
                cells.append(str(int(v)))
            else:
                cells.append(f"{v:.4f}")
        for j, on in enumerate(obj_names):
            val = cand["f"][j]
            if math.isnan(val):
                cells.append("NaN")
            else:
                cells.append(f"{val:.4f}")
        rows.append("| " + " | ".join(cells) + " |")

    return "\n".join(rows)
