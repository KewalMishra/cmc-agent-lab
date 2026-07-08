# Research Brief

## Interview-Derived Product Direction

The strongest project direction is not another biomedical retrieval assistant. The AstraZeneca
conversation pointed toward late-stage pharmaceutical technology and development: chemistry,
chemical engineering, formulation, process understanding, stability, manufacturability, and
auditable experiment planning. The relevant product surface is an agent that coordinates
scientific models and data products to reduce large physical experiment sets to a small,
reviewable set of high-value experiments.

## What Is Attractive Right Now

### 1. Digital twins and hybrid mechanistic/data models

Pharmaceutical manufacturing literature is converging on digital twins that combine
mechanistic process models, PAT data, data integration, and model-based control. The important
portfolio signal is not "I used an LLM"; it is that the agent understands when a scientific
question needs a mechanistic model, a surrogate model, or a human review gate.

Useful sources:

- [Digital Twins in Pharmaceutical and Biopharmaceutical Manufacturing](https://www.mdpi.com/2227-9717/8/9/1088)
- [Digital twins and mechanistic models for optimized bioprocessing](https://www.cytivalifesciences.com/en/us/insights/digital-twins-and-mechanistic-models-for-optimized-bioprocessing)
- [PharmaPy: An object-oriented tool for the development of hybrid pharmaceutical flowsheets](https://pmc.ncbi.nlm.nih.gov/articles/PMC10793241/)

### 2. Open-source pharmaceutical process simulation

PharmaPy is particularly aligned because it is an open-source library for pharmaceutical
manufacturing systems with dynamic ODE/DAE-style unit operations. It gives this project a
credible mechanistic/process-development anchor.

Useful sources:

- [PharmaPy documentation](https://pharmapy.readthedocs.io/)
- [Simulation-optimization framework using Pyomo and PharmaPy](https://pmc.ncbi.nlm.nih.gov/articles/PMC10765421/)
- [Application of PharmaPy in digital design of manufacturing processes](https://pmc.ncbi.nlm.nih.gov/articles/PMC10759178/)
- [PharmaPy 2.0: dynamic process modeling and end-to-end continuous manufacturing](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5902983)

### 3. Population-balance modeling for crystallization

Crystallization is a strong demo area because it links process variables to particle size,
yield, filterability, dissolution, and manufacturability. A moment-based population-balance
model is credible enough for a portfolio prototype and extensible to higher-fidelity PharmaPy
or custom solvers later.

Useful sources:

- [Advantages of Utilizing Population Balance Modeling of Crystallization Processes](https://www.mdpi.com/2227-9717/7/6/355)
- [State-of-the-art review of population-balanced equations in pharmaceutical crystallization](https://arabjchem.org/state-of-the-art-review-on-various-mathematical-approaches-towards-solving-population-balanced-equations-in-pharmaceutical-crystallization-process/)

### 4. Bayesian optimization and active learning for sparse experiments

The interview emphasized reducing many experiments to a top set. Bayesian optimization,
surrogate models, active learning, and self-driving lab ideas map cleanly to that. The agent
should recommend experiments, but also expose uncertainty and rationale.

Useful sources:

- [BoTorch introduction](https://botorch.org/docs/v0.16.1/introduction)
- [Ax and BoTorch for sequential experimentation](https://botorch.org/docs/botorch_and_ax)
- [Ax Bayesian optimization documentation](https://ax.dev/docs/0.5.0/bayesopt/)
- [AI/ML-guided formulation optimization review](https://pubmed.ncbi.nlm.nih.gov/41579967/)
- [Design of Biopharmaceutical Formulations Accelerated by Machine Learning](https://pubs.acs.org/doi/10.1021/acs.molpharmaceut.1c00469)
- [Efficient discovery of new medicine formulations using a semi-self-driven robotic formulator](https://pubs.rsc.org/en/content/articlehtml/2025/dd/d5dd00171d)

### 5. Regulated auditability

This is where the project can stand out. In CMC, the system must not just answer; it must show
what it did. The agent should record tool choices, model assumptions, inputs, outputs,
uncertainty, risk controls, and human approval requirements.

Useful sources:

- [FDA Process Analytical Technology guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/pat-framework-innovative-pharmaceutical-development-manufacturing-and-quality-assurance)
- [ICH Q8(R2) Pharmaceutical Development](https://database.ich.org/sites/default/files/Q8_R2_Guideline.pdf)
- [ICH Q9(R1) Quality Risk Management](https://database.ich.org/sites/default/files/ICH_Q9%28R1%29_Guideline_Step4_2022_1219.pdf)

### 6. LangGraph for stateful, reviewable orchestration

LangGraph is a good fit because the workflow is not a single chat completion. It is a stateful
process: scope, plan, route tools, run simulators, rank experiments, audit, and pause for human
review.

Useful sources:

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph human-in-the-loop documentation](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [LangSmith observability](https://docs.langchain.com/langsmith/observability)

## Resulting Project Thesis

Build an **Agentic Process Development Copilot** that helps CMC/process-development scientists
move from a vague development objective to a ranked, auditable set of next experiments.

The strongest demo slice is:

1. Parse a molecule/product/process-development question into QTPP, CQAs, CPPs, and constraints.
2. Select only the tools needed for the user-requested mode.
3. Run transparent mechanistic simulations for stability, reaction conversion, crystallization,
   and dissolution.
4. Fit or approximate a surrogate model over sparse historical experiments.
5. Recommend top five next experiments using expected performance and information gain.
6. Produce a QbD risk register and audit trail.
7. Require scientist approval before any experimental protocol is treated as actionable.
