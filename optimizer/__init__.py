"""Rocket design optimization package for OpenRocket.

Public API
----------
This package re-exports the key classes and functions so that users
can write ``from optimizer import RocketSimulator, generate_lhs, ...``.
"""

# Apply JVM patch on package import
from optimizer.jvm_patch import apply_patch as _apply_patch

_apply_patch()

# --- design_space ---
from optimizer.design_space import (  # noqa: E402
    ConstraintOperator,
    DesignVariable,
    Direction,
    Extraction,
    ObjectiveFunction,
    Constraint,
    OptimizationProblem,
    VARIABLE_CATALOG,
    list_components,
    get_current_values,
)

# --- simulation ---
from optimizer.simulation import RocketSimulator  # noqa: E402

# --- doe ---
from optimizer.doe import (  # noqa: E402
    generate_lhs,
    format_doe_table,
    run_doe,
    check_constraints,
    format_doe_results_table,
)

# --- surrogate ---
from optimizer.surrogate import SurrogateModel  # noqa: E402

# --- pareto ---
from optimizer.pareto import (  # noqa: E402
    run_nsga2,
    find_knee_point,
    select_top3,
)

# --- visualize ---
from optimizer.visualize import (  # noqa: E402
    plot_pareto_front,
    plot_doe_summary,
    plot_candidate_comparison,
    format_results_table,
)

__all__ = [
    # design_space
    "ConstraintOperator",
    "DesignVariable",
    "Direction",
    "Extraction",
    "ObjectiveFunction",
    "Constraint",
    "OptimizationProblem",
    "VARIABLE_CATALOG",
    "list_components",
    "get_current_values",
    # simulation
    "RocketSimulator",
    # doe
    "generate_lhs",
    "format_doe_table",
    "run_doe",
    "check_constraints",
    "format_doe_results_table",
    # surrogate
    "SurrogateModel",
    # pareto
    "run_nsga2",
    "find_knee_point",
    "select_top3",
    # visualize
    "plot_pareto_front",
    "plot_doe_summary",
    "plot_candidate_comparison",
    "format_results_table",
]
