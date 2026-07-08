"""Adapter boundaries for external open-source simulators.

The local project does not require these packages. The adapter layer documents where validated
or higher-fidelity models would be plugged into the same tool contract used by built-in models.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExternalAdapter:
    name: str
    dependency: str
    intended_use: str
    integration_boundary: str


EXTERNAL_ADAPTERS = [
    ExternalAdapter(
        name="PharmaPy",
        dependency="PharmaPy",
        intended_use="Drug-substance unit operations, dynamic flowsheets, crystallization, drying.",
        integration_boundary="Map scenario design variables to PharmaPy unit operation parameters.",
    ),
    ExternalAdapter(
        name="Cantera",
        dependency="cantera",
        intended_use="Chemical kinetics, thermodynamics, transport, and reaction-path sensitivity.",
        integration_boundary="Map reaction mechanism files and operating conditions to Cantera reactors.",
    ),
    ExternalAdapter(
        name="IDAES/Pyomo",
        dependency="idaes",
        intended_use="Equation-oriented flowsheet simulation, optimization, surrogate modeling, control.",
        integration_boundary="Compile flowsheet blocks from scenario unit operations and solve with Pyomo.",
    ),
    ExternalAdapter(
        name="DWSIM",
        dependency="dwsim",
        intended_use="Steady-state and dynamic process flowsheets with property packages.",
        integration_boundary="Drive DWSIM through Python/.NET automation or exported flowsheet files.",
    ),
    ExternalAdapter(
        name="Thermo/Chemicals",
        dependency="thermo",
        intended_use="Chemical constants, mixture properties, phase equilibrium, transport properties.",
        integration_boundary="Use as property backend for dissolution, solubility, and separations models.",
    ),
]
