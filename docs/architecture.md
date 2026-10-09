# Architecture

## Application layers

```text
CSV files (data/ preferred; root-level fallback)
        |
        v
src/data_loader.py ----> src/validation.py
        |
        +--> src/solar_engine.py
        +--> src/demand_engine.py
        +--> src/workforce_optimizer.py
        +--> src/cost_engine.py
        +--> src/scheduler.py (OR-Tools CP-SAT)
        +--> src/scenario_engine.py / src/recommender.py
        |
        v
app.py --> components/* --> Streamlit interface, Plotly charts, exports
```

`app.py` loads all seven datasets and constructs the engines, then routes the selected sidebar page to one of seven screen renderers. `src/data_loader.py` uses Streamlit's data cache when Streamlit is importable. Dataset path resolution in `src/utils.py` prefers `data/<filename>` and then falls back to the project root.

## Data flow

1. **Load:** CSVs are read into Pandas dataframes; job, solar-weather, and historical date columns are parsed as datetimes.
2. **Select context:** The sidebar holds a factory ID and target date in Streamlit session state. The initial context is `FAC_016` when present and 2026-08-10.
3. **Prepare jobs:** `DemandEngine` selects jobs released on the target date. If there are none, it tries jobs active across that date, capped at ten; if still empty, it uses the first ten jobs for the factory. It enriches rows with machine power, duration, and estimated cost fields.
4. **Model solar:** `SolarEngine` matches the factory to a weather location using district/location text, then calculates hourly available solar from installed PV capacity and the weather dataset's capacity factor. If the selected date has no profile, it uses the location's average hourly profile.
5. **Schedule:** `SolarSyncScheduler` builds a CP-SAT model and minimizes modeled electricity cost. It includes job release/deadline hour bounds, non-overlap for jobs on the same machine, configured maintenance windows, and a factory grid-capacity bound.
6. **Evaluate and render:** `CostEngine` compares baseline and candidate 24-hour profiles. The UI displays model metrics, charts, validation results, recommendations, and scheduler PDF/Excel/CSV exports.

Workforce capacity and skill summaries are calculated by `WorkforceOptimizer` for the Energy & Workforce screen. They are not constraints in the CP-SAT scheduler. See [Limitations](limitations.md) for additional gaps between displayed controls and model inputs.

## Main modules

| Area | Files | Responsibility |
|---|---|---|
| Entry point | `app.py` | App setup, data/engine initialization, shared factory/date context, page routing |
| UI | `components/` | Seven routed views, reusable cards/charts, and 2D/3D visualizations |
| Data | `src/data_loader.py`, `src/utils.py` | Cached CSV loading, path resolution, formatting/time helpers |
| Models | `src/solar_engine.py`, `src/demand_engine.py`, `src/cost_engine.py` | Solar profile, job enrichment, baseline/optimized energy and cost metrics |
| Scheduling | `src/scheduler.py` | CP-SAT model and candidate schedule output |
| Workforce | `src/workforce_optimizer.py` | Hourly staffing and skill-capacity analysis separate from the scheduler |
| Scenarios/recommendations | `src/scenario_engine.py`, `src/recommender.py`, `src/result_engine.py` | Scenario runs, per-job explanations, and result-state messaging |
| Reports | `src/report_generator.py`, `src/pdf_generator.py` | Excel and PDF decision report generation |
| Validation | `src/validation.py` | CSV-level range, relationship, solar, tariff, and historical formula checks |
| Tests | `tests/` | Unit, integration, reporting, data, and UI-related checks |

## Dependencies

The application uses Streamlit, Pandas, NumPy, Plotly, and OR-Tools. PDF reports use ReportLab; Excel reports use OpenPyXL. pytest runs the automated test suite. See [`requirements.txt`](../requirements.txt).
