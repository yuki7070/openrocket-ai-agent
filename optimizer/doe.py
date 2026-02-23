"""Design of Experiments (DOE) via Latin Hypercube Sampling.

Generates sample points, runs them through the simulator, and returns
structured results for downstream surrogate modelling.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.stats import qmc

from optimizer.design_space import OptimizationProblem
from optimizer.simulation import RocketSimulator, check_constraint


# ---------------------------------------------------------------------------
# LHS generation
# ---------------------------------------------------------------------------

def generate_lhs(
    problem: OptimizationProblem,
    n_samples: int = 30,
    seed: int | None = None,
) -> np.ndarray:
    """Generate LHS samples scaled to the variable bounds.

    Returns an (n_samples, n_var) array.  Integer variables are rounded.
    """
    sampler = qmc.LatinHypercube(d=problem.n_var, seed=seed)
    unit_samples = sampler.random(n=n_samples)  # in [0, 1]^d
    lower = np.array(problem.lower_bounds)
    upper = np.array(problem.upper_bounds)
    samples = qmc.scale(unit_samples, lower, upper)

    # Round integer variables
    for i, var in enumerate(problem.variables):
        if var.is_integer:
            samples[:, i] = np.round(samples[:, i])

    return samples


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_doe_table(
    problem: OptimizationProblem,
    samples: np.ndarray,
) -> str:
    """Format DOE samples as a Markdown table for human review."""
    headers = ["#"] + [v.name for v in problem.variables]
    rows: list[str] = []
    rows.append("| " + " | ".join(headers) + " |")
    rows.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for i, row in enumerate(samples):
        cells = [str(i + 1)]
        for j, val in enumerate(row):
            if problem.variables[j].is_integer:
                cells.append(str(int(val)))
            else:
                cells.append(f"{val:.4f}")
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


# ---------------------------------------------------------------------------
# DOE execution
# ---------------------------------------------------------------------------

def run_doe(
    simulator: RocketSimulator,
    problem: OptimizationProblem,
    samples: np.ndarray,
) -> list[dict]:
    """Run all DOE sample points and return results.

    Each result dict contains:
    - ``"x"``: the design vector (list of float)
    - one key per objective/constraint name with the extracted scalar
    - ``"feasible"``: whether all constraints are satisfied
    """
    results: list[dict] = []
    n = len(samples)
    for i, x in enumerate(samples):
        print(f"[DOE] Running sample {i + 1}/{n} ...")
        outcome = simulator.evaluate(problem, x)
        if outcome is None:
            outcome = {
                o.name: float("nan")
                for o in problem.objectives + problem.constraints  # type: ignore[operator]
            }

        record: dict = {"x": x.tolist(), **outcome}
        record["feasible"] = check_constraints(problem, outcome)
        results.append(record)

    n_feasible = sum(1 for r in results if r["feasible"])
    print(f"[DOE] Done. {n_feasible}/{n} feasible points.")
    return results


def check_constraints(problem: OptimizationProblem, outcome: dict[str, float]) -> bool:
    """Return True if all constraints are satisfied."""
    for con in problem.constraints:
        val = outcome.get(con.name, float("nan"))
        if not check_constraint(con, val):
            return False
    return True


# ---------------------------------------------------------------------------
# Results table
# ---------------------------------------------------------------------------

def format_doe_results_table(
    problem: OptimizationProblem,
    results: list[dict],
) -> str:
    """Format DOE results as a Markdown table."""
    var_names = [v.name for v in problem.variables]
    obj_names = [o.name for o in problem.objectives]
    con_names = [c.name for c in problem.constraints]
    headers = ["#"] + var_names + obj_names + con_names + ["feasible"]

    rows: list[str] = []
    rows.append("| " + " | ".join(headers) + " |")
    rows.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for i, rec in enumerate(results):
        cells = [str(i + 1)]
        for j, vn in enumerate(var_names):
            val = rec["x"][j]
            if problem.variables[j].is_integer:
                cells.append(str(int(val)))
            else:
                cells.append(f"{val:.4f}")
        for name in obj_names + con_names:
            val = rec.get(name, float("nan"))
            if math.isnan(val):
                cells.append("NaN")
            else:
                cells.append(f"{val:.4f}")
        cells.append("Yes" if rec["feasible"] else "No")
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)
