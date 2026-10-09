# Project overview

## Background and problem

SolarSync is a decision-support prototype for the DRE Enterprise Hackathon '26, Problem Statement PS07 — Solar-Aware Demand Shifting Scheduler. It explores a planning challenge: production demand may occur when on-site solar generation is limited, while time-dependent electricity prices and job deadlines can influence which alternative start times are useful.

Jobs cannot necessarily be moved freely. Production plans may depend on release times, due dates, machine availability and maintenance, staffing, and required skills. The project models selected machine and timing constraints and displays separate workforce analytics; it does not yet combine every operational constraint in the scheduling solver.

## Objectives

- Show factory, machine, production, solar/weather, tariff, workforce, and historical-energy information in one local application.
- Compare a release-time baseline with a model-generated hourly candidate schedule.
- Estimate solar use, grid energy, and electricity cost from supplied CSV data and documented code assumptions.
- Make outputs reviewable through charts, per-job rationale, validation summaries, and downloadable reports.

## Intended users

The intended users are factory managers, production planners, and energy analysts evaluating hypothetical schedules. The application is a prototype for human review, not a control system or a substitute for facility-specific engineering and operating procedures.

## Workflow

```text
Factory, machine, and production CSVs
        + solar/weather and tariff CSVs
        + workforce and historical-energy CSVs
                    |
                    v
         Load, enrich, and validate data
                    |
                    v
     Solar profile + job demand preparation
                    |
                    v
       CP-SAT candidate schedule and baseline
                    |
                    v
      Modeled energy/cost comparison and UI
                    |
                    v
        Human review before any action
```

The actual CP-SAT objective is modeled electricity-cost minimization under a limited set of timing, machine, maintenance, and grid-capacity constraints. Current gaps and unconnected UI controls are listed in [Limitations](limitations.md).

## Potential business value

The application can help users inspect how candidate job timing interacts with modeled solar availability and a fixed time-of-use rate schedule. Any value is exploratory: the supplied data provenance is not documented, some model assumptions are simplified, and the application does not verify a proposed plan against every real operational constraint.
