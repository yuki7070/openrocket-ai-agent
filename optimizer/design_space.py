"""Design space definitions for rocket optimization.

Provides dataclass-based structures for defining design variables, objective
functions, constraints, and complete optimization problems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import orhelper


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Extraction(str, Enum):
    """How to extract a scalar from a time-series."""
    MAX = "max"
    MIN = "min"
    FINAL = "final"
    MEAN = "mean"


class Direction(str, Enum):
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"


class ConstraintOperator(str, Enum):
    GE = ">="
    LE = "<="
    EQ = "=="


# ---------------------------------------------------------------------------
# Core dataclasses
# ---------------------------------------------------------------------------

@dataclass
class DesignVariable:
    """A single design variable that maps to an OpenRocket component property."""
    name: str
    component_name: str
    setter_method: str
    getter_method: str
    lower_bound: float
    upper_bound: float
    unit: str = ""
    is_simulation_option: bool = False
    is_integer: bool = False


@dataclass
class ObjectiveFunction:
    """An objective to optimize, extracted from simulation flight data."""
    name: str
    flight_data_type: str  # FlightDataType attribute name, e.g. "TYPE_ALTITUDE"
    extraction: Extraction = Extraction.MAX
    direction: Direction = Direction.MAXIMIZE


@dataclass
class Constraint:
    """A constraint on the simulation output."""
    name: str
    flight_data_type: str
    extraction: Extraction
    operator: ConstraintOperator
    threshold: float


@dataclass
class OptimizationProblem:
    """Complete optimization problem definition."""
    ork_file: str
    variables: list[DesignVariable] = field(default_factory=list)
    objectives: list[ObjectiveFunction] = field(default_factory=list)
    constraints: list[Constraint] = field(default_factory=list)

    @property
    def n_var(self) -> int:
        return len(self.variables)

    @property
    def n_obj(self) -> int:
        return len(self.objectives)

    @property
    def n_constr(self) -> int:
        return len(self.constraints)

    @property
    def lower_bounds(self) -> list[float]:
        return [v.lower_bound for v in self.variables]

    @property
    def upper_bounds(self) -> list[float]:
        return [v.upper_bound for v in self.variables]


# ---------------------------------------------------------------------------
# Variable catalog — templates for commonly-used design variables
# ---------------------------------------------------------------------------

VARIABLE_CATALOG: dict[str, dict] = {
    "nose_length": dict(
        setter_method="setLength",
        getter_method="getLength",
        unit="m",
    ),
    "body_tube_length": dict(
        setter_method="setLength",
        getter_method="getLength",
        unit="m",
    ),
    "fin_root_chord": dict(
        setter_method="setRootChord",
        getter_method="getRootChord",
        unit="m",
    ),
    "fin_tip_chord": dict(
        setter_method="setTipChord",
        getter_method="getTipChord",
        unit="m",
    ),
    "fin_height": dict(
        setter_method="setHeight",
        getter_method="getHeight",
        unit="m",
    ),
    "fin_count": dict(
        setter_method="setFinCount",
        getter_method="getFinCount",
        unit="",
        is_integer=True,
    ),
    "parachute_diameter": dict(
        setter_method="setDiameter",
        getter_method="getDiameter",
        unit="m",
    ),
    "launch_rod_angle": dict(
        setter_method="setLaunchRodAngle",
        getter_method="getLaunchRodAngle",
        unit="rad",
        is_simulation_option=True,
    ),
    "launch_rod_length": dict(
        setter_method="setLaunchRodLength",
        getter_method="getLaunchRodLength",
        unit="m",
        is_simulation_option=True,
    ),
    "wind_speed": dict(
        setter_method="setWindSpeedAverage",
        getter_method="getWindSpeedAverage",
        unit="m/s",
        is_simulation_option=True,
    ),
}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def list_components(orh: orhelper.Helper, rocket) -> list[dict]:
    """List all components in the rocket tree.

    Returns a list of dicts with 'name', 'type', and 'class_name' keys.
    """
    components: list[dict] = []

    def _walk(component):
        class_name = type(component).__name__
        # JPype wraps Java types; get the simple Java class name
        try:
            java_class = component.getClass().getSimpleName()
        except Exception:
            java_class = class_name
        components.append({
            "name": str(component.getName()),
            "type": java_class,
            "class_name": class_name,
        })
        child_count = component.getChildCount()
        for i in range(child_count):
            _walk(component.getChild(i))

    _walk(rocket)
    return components


def get_current_values(
    orh: orhelper.Helper,
    sim,
    variables: list[DesignVariable],
) -> dict[str, float]:
    """Read the current design values from the simulation/rocket.

    Returns a dict mapping variable name to its current value.
    """
    opts = sim.getOptions()
    rocket = opts.getRocket()
    values: dict[str, float] = {}
    for var in variables:
        if var.is_simulation_option:
            target = opts
        else:
            target = orh.get_component_named(rocket, var.component_name)
        getter = getattr(target, var.getter_method)
        values[var.name] = float(getter())
    return values
