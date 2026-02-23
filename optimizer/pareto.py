"""Multi-objective optimization with NSGA-II on the surrogate model.

Uses pymoo for NSGA-II and provides knee-point detection and candidate
selection utilities.
"""

from __future__ import annotations

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import Problem
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.operators.sampling.lhs import LHS as PymooLHS

from optimizer.design_space import Direction, OptimizationProblem
from optimizer.surrogate import SurrogateModel


# ---------------------------------------------------------------------------
# pymoo Problem wrapper
# ---------------------------------------------------------------------------

class SurrogateProblem(Problem):
    """pymoo Problem that evaluates the surrogate model."""

    def __init__(self, surrogate: SurrogateModel, problem: OptimizationProblem):
        self.surrogate = surrogate
        self.opt_problem = problem

        xl = np.array(problem.lower_bounds)
        xu = np.array(problem.upper_bounds)

        super().__init__(
            n_var=problem.n_var,
            n_obj=problem.n_obj,
            xl=xl,
            xu=xu,
        )

    def _evaluate(self, X, out, *args, **kwargs):
        preds = self.surrogate.predict(X)
        F = np.column_stack([
            # pymoo minimizes; flip sign for maximization objectives
            -preds[obj.name] if obj.direction is Direction.MAXIMIZE else preds[obj.name]
            for obj in self.opt_problem.objectives
        ])
        out["F"] = F


# ---------------------------------------------------------------------------
# NSGA-II runner
# ---------------------------------------------------------------------------

def run_nsga2(
    surrogate: SurrogateModel,
    problem: OptimizationProblem,
    pop_size: int = 100,
    n_gen: int = 200,
    seed: int | None = 42,
) -> dict:
    """Run NSGA-II on the surrogate and return Pareto front results.

    Returns a dict with:
    - ``"X"``: (n_pareto, n_var) design vectors
    - ``"F"``: (n_pareto, n_obj) objective values (original scale, not flipped)
    - ``"F_minimized"``: raw pymoo F (minimization)
    """
    pymoo_problem = SurrogateProblem(surrogate, problem)

    algorithm = NSGA2(
        pop_size=pop_size,
        sampling=PymooLHS(),
    )
    termination = get_termination("n_gen", n_gen)

    res = minimize(
        pymoo_problem,
        algorithm,
        termination,
        seed=seed,
        verbose=False,
    )

    # Convert back to original objective scale
    F_original = res.F.copy()
    for j, obj in enumerate(problem.objectives):
        if obj.direction is Direction.MAXIMIZE:
            F_original[:, j] = -F_original[:, j]

    print(f"[NSGA-II] Found {len(res.X)} Pareto-optimal solutions.")
    return {
        "X": res.X,
        "F": F_original,
        "F_minimized": res.F,
    }


# ---------------------------------------------------------------------------
# Knee point & candidate selection
# ---------------------------------------------------------------------------

def find_knee_point(F: np.ndarray) -> int:
    """Find the knee point on the Pareto front.

    For 2 objectives: maximum perpendicular distance from the line
    connecting the two extreme points.
    For 3+ objectives: the point with the smallest normalized sum.
    """
    n = len(F)
    if n <= 2:
        return 0

    if F.shape[1] == 2:
        # Normalize to [0, 1]
        f_min = F.min(axis=0)
        f_max = F.max(axis=0)
        f_range = f_max - f_min
        f_range[f_range == 0] = 1.0
        F_norm = (F - f_min) / f_range

        # Line from extreme point A to B
        idx_a = np.argmin(F_norm[:, 0])
        idx_b = np.argmin(F_norm[:, 1])
        A = F_norm[idx_a]
        B = F_norm[idx_b]
        AB = B - A
        AB_len = np.linalg.norm(AB)
        if AB_len == 0:
            return 0

        # Perpendicular distance from each point to line AB
        dists = np.abs(np.cross(AB, A - F_norm)) / AB_len
        return int(np.argmax(dists))
    else:
        # 3+ objectives: normalized sum
        f_min = F.min(axis=0)
        f_max = F.max(axis=0)
        f_range = f_max - f_min
        f_range[f_range == 0] = 1.0
        F_norm = (F - f_min) / f_range
        sums = F_norm.sum(axis=1)
        return int(np.argmin(sums))


def select_top3(
    pareto_result: dict,
    problem: OptimizationProblem,
) -> list[dict]:
    """Select up to 3 representative candidates from the Pareto front.

    1. Knee point
    2. Best for each individual objective (pick the first one different from knee)
    3. Fill remaining slots with the most distant point from already-selected

    Returns a list of dicts with ``"index"``, ``"x"``, ``"f"``, and ``"label"`` keys.
    """
    F = pareto_result["F"]
    X = pareto_result["X"]
    n = len(F)

    if n == 0:
        return []

    knee_idx = find_knee_point(F)
    selected: list[dict] = [{
        "index": knee_idx,
        "x": X[knee_idx].tolist(),
        "f": F[knee_idx].tolist(),
        "label": "Knee point",
    }]
    used_indices = {knee_idx}

    # Best per objective
    for obj in problem.objectives:
        j = [o.name for o in problem.objectives].index(obj.name)
        if obj.direction is Direction.MAXIMIZE:
            best_idx = int(np.argmax(F[:, j]))
        else:
            best_idx = int(np.argmin(F[:, j]))

        if best_idx not in used_indices and len(selected) < 3:
            selected.append({
                "index": best_idx,
                "x": X[best_idx].tolist(),
                "f": F[best_idx].tolist(),
                "label": f"Best {obj.name}",
            })
            used_indices.add(best_idx)

    # Fill with most distant point
    if len(selected) < 3 and n > len(selected):
        f_min = F.min(axis=0)
        f_max = F.max(axis=0)
        f_range = f_max - f_min
        f_range[f_range == 0] = 1.0
        F_norm = (F - f_min) / f_range

        selected_norm = np.array([F_norm[s["index"]] for s in selected])
        min_dists = np.full(n, np.inf)
        for i in range(n):
            if i in used_indices:
                min_dists[i] = -1
                continue
            for s in selected_norm:
                d = np.linalg.norm(F_norm[i] - s)
                min_dists[i] = min(min_dists[i], d)
        farthest = int(np.argmax(min_dists))
        if farthest not in used_indices:
            selected.append({
                "index": farthest,
                "x": X[farthest].tolist(),
                "f": F[farthest].tolist(),
                "label": "Most diverse",
            })

    return selected
