"""RBF surrogate model for approximating simulation responses.

Wraps :class:`scipy.interpolate.RBFInterpolator` with convenience methods
for fitting from DOE results and leave-one-out cross-validation.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.interpolate import RBFInterpolator

from optimizer.design_space import OptimizationProblem


class SurrogateModel:
    """Multi-output RBF surrogate built from DOE results.

    One :class:`RBFInterpolator` is constructed per objective function.
    """

    def __init__(self):
        self._models: dict[str, RBFInterpolator] = {}
        self._obj_names: list[str] = []
        self._X: np.ndarray | None = None
        self._Y: dict[str, np.ndarray] = {}

    # -- fitting ------------------------------------------------------------

    def fit(
        self,
        doe_results: list[dict],
        problem: OptimizationProblem,
        kernel: str = "thin_plate_spline",
    ) -> None:
        """Fit one RBF per objective using feasible DOE points.

        Infeasible (NaN-objective) points are excluded.
        """
        self._obj_names = [o.name for o in problem.objectives]

        # Filter to rows where all objectives are finite
        valid = [
            r for r in doe_results
            if all(not math.isnan(r.get(name, float("nan"))) for name in self._obj_names)
        ]
        if len(valid) < 2:
            raise ValueError(
                f"Need at least 2 valid DOE points to fit; got {len(valid)}"
            )

        X = np.array([r["x"] for r in valid])
        self._X = X

        for name in self._obj_names:
            y = np.array([r[name] for r in valid])
            self._Y[name] = y
            self._models[name] = RBFInterpolator(X, y, kernel=kernel)

        print(f"[Surrogate] Fitted {len(self._models)} models on {len(valid)} points.")

    # -- prediction ---------------------------------------------------------

    def predict(self, X: np.ndarray) -> dict[str, np.ndarray]:
        """Predict all objectives for multiple input points.

        Parameters
        ----------
        X : (n, n_var) array

        Returns
        -------
        dict mapping objective name -> (n,) prediction array
        """
        return {name: model(X) for name, model in self._models.items()}

    def predict_single(self, x: np.ndarray | list[float]) -> dict[str, float]:
        """Predict all objectives for a single point."""
        x_2d = np.atleast_2d(x)
        preds = self.predict(x_2d)
        return {name: float(arr[0]) for name, arr in preds.items()}

    # -- quality metrics ----------------------------------------------------

    def get_r2_scores(self) -> dict[str, float]:
        """Compute leave-one-out R^2 for each objective.

        A score close to 1.0 indicates good surrogate fidelity.
        """
        if self._X is None:
            raise RuntimeError("Model not fitted yet.")

        scores: dict[str, float] = {}
        X = self._X
        n = len(X)

        for name in self._obj_names:
            y = self._Y[name]
            y_pred_loo = np.empty(n)
            for i in range(n):
                X_train = np.delete(X, i, axis=0)
                y_train = np.delete(y, i)
                loo_model = RBFInterpolator(X_train, y_train, kernel="thin_plate_spline")
                y_pred_loo[i] = float(loo_model(X[[i]])[0])

            ss_res = np.sum((y - y_pred_loo) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
            scores[name] = round(r2, 4)

        return scores

    def format_r2_report(self) -> str:
        """Return a human-readable R^2 report."""
        scores = self.get_r2_scores()
        lines = ["**Surrogate Model Quality (LOO R^2):**"]
        for name, r2 in scores.items():
            quality = "good" if r2 >= 0.9 else "acceptable" if r2 >= 0.7 else "poor"
            lines.append(f"- {name}: R^2 = {r2:.4f} ({quality})")
        return "\n".join(lines)
