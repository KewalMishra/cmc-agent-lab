# Simulator Stack

## Design Principle

The project should not pretend that an LLM is the scientific model. The LLM/agent should route
to models, simulators, optimizers, and human review. Simulator execution must have a shared
contract:

- declared intended use
- required inputs
- assumptions
- outputs and units
- uncertainty or known limitations
- provenance record

## Built-In Local Models

These make the project runnable on any laptop:

1. **Arrhenius stability model**
   - Purpose: shelf-life/degradation sensitivity.
   - Inputs: temperature, time, activation energy, reference degradation rate.
   - Output: predicted purity remaining and degradation rate.

2. **Batch reaction ODE model**
   - Purpose: conversion, yield, and impurity tradeoff.
   - Inputs: temperature and residence time.
   - Output: conversion, isolated-yield proxy, impurity proxy.

3. **Moment-based crystallization model**
   - Purpose: particle-size/yield sensitivity from supersaturation trajectory.
   - Inputs: temperature, cooling rate, antisolvent fraction, residence time.
   - Output: crystallization yield, d50 proxy, nucleation-density proxy.

4. **Noyes-Whitney dissolution model**
   - Purpose: dissolution and solubility/formulation screening.
   - Inputs: pH, antisolvent fraction, particle-size proxy.
   - Output: 30-minute dissolution proxy and solubility capacity.

## Optional Open-Source Adapters

### PharmaPy

Best fit for this project. PharmaPy is an open-source pharmaceutical manufacturing simulation
library with dynamic models and unit operations. It should be the first external integration
target after the local prototype.

Sources:

- [PharmaPy documentation](https://pharmapy.readthedocs.io/)
- [PharmaPy paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC10793241/)

### IDAES/Pyomo

Best fit for equation-oriented process simulation, parameter estimation, optimization, surrogate
modeling, and control. It is broader than pharma, but strong for process systems engineering.

Sources:

- [IDAES overview](https://idaes.org/overview/)
- [IDAES documentation: why IDAES](https://idaes-pse.readthedocs.io/en/latest/explanations/why_idaes.html)
- [Pyomo.DAE documentation](https://pyomo.readthedocs.io/en/6.8.0/modeling_extensions/dae.html)

### Cantera

Useful for reaction kinetics, thermodynamics, transport, and reaction-path analysis when the
chemistry mechanism is available.

Sources:

- [Cantera documentation](https://cantera.org/)
- [Cantera GitHub](https://github.com/Cantera/cantera)

### DWSIM

Useful for flowsheeting and process simulation when a GUI/process-simulator style demonstration
is desirable. The project should treat it as an automation-backed external simulator.

Sources:

- [DWSIM official site](https://dwsim.org/)
- [DWSIM automation documentation](https://dwsim.org/wiki/index.php?title=Automation)

### Thermo/Chemicals

Useful as a property backend for phase equilibrium, mixture properties, and thermodynamic
screening.

Sources:

- [Thermo documentation](https://thermo.readthedocs.io/index.html)
- [Chemicals documentation](https://chemicals.readthedocs.io/index.html)

## Integration Roadmap

1. Keep built-in models as deterministic test fixtures.
2. Add PharmaPy adapter for a crystallizer or reactor flowsheet.
3. Add Thermo/Chemicals property calls to replace heuristic solubility terms.
4. Add IDAES/Pyomo optimization for one equation-oriented unit operation.
5. Add DWSIM automation only if a visual flowsheet demo is worth the extra setup cost.
