"""OpenRocket simulation wrapper for optimization.

Provides :class:`RocketSimulator`, a context manager that handles JVM
lifecycle and exposes helpers for applying design variables and extracting
scalar objectives from simulation results.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

import optimizer.jvm_patch  # noqa: F401  — ensure patch applied
import orhelper
from orhelper import FlightDataType

from optimizer.design_space import (
    Constraint,
    ConstraintOperator,
    DesignVariable,
    Extraction,
    ObjectiveFunction,
    OptimizationProblem,
)


def _extract_scalar(series: np.ndarray, extraction: Extraction) -> float:
    """Extract a scalar value from a 1-D time-series array."""
    if len(series) == 0:
        return float("nan")
    if extraction is Extraction.MAX:
        return float(np.nanmax(series))
    if extraction is Extraction.MIN:
        return float(np.nanmin(series))
    if extraction is Extraction.FINAL:
        return float(series[-1])
    if extraction is Extraction.MEAN:
        return float(np.nanmean(series))
    raise ValueError(f"Unknown extraction: {extraction}")


class RocketSimulator:
    """Context manager wrapping an OpenRocket instance for batch evaluation.

    Usage::

        with RocketSimulator("simple.ork") as sim:
            result = sim.evaluate(problem, x_vector)
    """

    def __init__(self, ork_file: str):
        self.ork_file = ork_file
        self._instance = None
        self._orh: orhelper.Helper | None = None
        self._doc = None
        self._sim = None

    # -- context manager ----------------------------------------------------

    def __enter__(self) -> RocketSimulator:
        self._instance = orhelper.OpenRocketInstance()
        instance = self._instance.__enter__()
        self._orh = orhelper.Helper(instance)
        self._doc = self._orh.load_doc(self.ork_file)
        self._sim = self._doc.getSimulation(0)
        return self

    def __exit__(self, *exc):
        if self._instance is not None:
            self._instance.__exit__(*exc)
        self._instance = None
        self._orh = None
        self._doc = None
        self._sim = None

    # -- accessors ----------------------------------------------------------

    @property
    def orh(self) -> orhelper.Helper:
        assert self._orh is not None, "Simulator not entered"
        return self._orh

    @property
    def sim(self):
        assert self._sim is not None, "Simulator not entered"
        return self._sim

    @property
    def rocket(self):
        return self.sim.getOptions().getRocket()

    # -- design application -------------------------------------------------

    def apply_design(
        self,
        variables: list[DesignVariable],
        values: list[float] | np.ndarray,
    ) -> None:
        """Set design variable values on the rocket / simulation options."""
        opts = self.sim.getOptions()
        rocket = opts.getRocket()
        for var, val in zip(variables, values):
            if var.is_integer:
                val = int(round(val))
            if var.is_simulation_option:
                target = opts
            else:
                target = self.orh.get_component_named(rocket, var.component_name)
            setter = getattr(target, var.setter_method)
            setter(val)

    # -- simulation & extraction -------------------------------------------

    def run_and_extract(
        self,
        objectives: list[ObjectiveFunction],
        constraints: list[Constraint] | None = None,
    ) -> dict[str, float]:
        """Run the simulation and extract scalar values for objectives/constraints.

        Returns a dict mapping name -> scalar value.
        """
        # Collect all FlightDataType enums we need
        needed_types: dict[str, Any] = {}
        for obj in objectives:
            needed_types[obj.flight_data_type] = getattr(FlightDataType, obj.flight_data_type)
        if constraints:
            for con in constraints:
                needed_types[con.flight_data_type] = getattr(FlightDataType, con.flight_data_type)

        self.orh.run_simulation(self.sim)
        data = self.orh.get_timeseries(self.sim, list(needed_types.values()))

        results: dict[str, float] = {}
        for obj in objectives:
            fdt = needed_types[obj.flight_data_type]
            results[obj.name] = _extract_scalar(data[fdt], obj.extraction)
        if constraints:
            for con in constraints:
                fdt = needed_types[con.flight_data_type]
                results[con.name] = _extract_scalar(data[fdt], con.extraction)
        return results

    def evaluate(
        self,
        problem: OptimizationProblem,
        x: list[float] | np.ndarray,
    ) -> dict[str, float] | None:
        """Apply design, run simulation, extract objectives & constraints.

        Returns None (with NaN results) if the simulation fails.
        """
        try:
            self.apply_design(problem.variables, x)
            return self.run_and_extract(problem.objectives, problem.constraints)
        except Exception as exc:
            print(f"[Simulator] evaluation failed: {exc}")
            # Return NaN for all objectives and constraints
            names = [o.name for o in problem.objectives] + [c.name for c in problem.constraints]
            return {name: float("nan") for name in names}


def check_constraint(constraint: Constraint, value: float) -> bool:
    """Check whether a single constraint is satisfied."""
    if math.isnan(value):
        return False
    if constraint.operator is ConstraintOperator.GE:
        return value >= constraint.threshold
    if constraint.operator is ConstraintOperator.LE:
        return value <= constraint.threshold
    if constraint.operator is ConstraintOperator.EQ:
        return math.isclose(value, constraint.threshold, rel_tol=1e-6)
    raise ValueError(f"Unknown operator: {constraint.operator}")
