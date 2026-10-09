# User guide

## Start the application

From the project root, activate a Python virtual environment, install `requirements.txt`, and run:

```bash
streamlit run app.py
```

Open `http://localhost:8501`. Detailed Windows and macOS/Linux setup steps are in the [README](../README.md).

## Shared context

Use the sidebar to choose the active factory and target date. These values are shared by the relevant views. The initial date is set to 2026-08-10 in the app.

## Screens

1. **Executive Dashboard** — cluster and factory summaries, interactive visualizations, and available overview exports.
2. **Factory Intelligence** — selected-factory information, machine inventory/maintenance, workforce roster, and energy-flow views.
3. **Smart Scheduler** — request a schedule for the selected factory/date, inspect baseline versus candidate energy/cost charts and job recommendations, and download PDF, Excel, or CSV reports.
4. **Scenario Simulator** — vary solar availability, solar capacity, production demand, and displayed peak-tariff assumptions, then compare a scenario run. Not every control currently affects the calculations; see [Limitations](limitations.md).
5. **Energy & Workforce** — inspect weather/solar views and workforce capacity/skill summaries.
6. **History & System Health** — review historical energy metrics and run the seven-dataset validation report.
7. **About** — view the in-app project and problem-statement information.

## Interpreting a schedule

The scheduler compares a release-time baseline to an hourly CP-SAT candidate. Review the solver status, assumptions, selected factory/date, and job list before relying on the result. Workforce availability is analyzed elsewhere in the app and is not enforced by the scheduler. The tariff rates are currently fixed in code rather than read from the supplied tariff CSV.

The tool is decision support only. Validate any proposed schedule against actual factory operations, current tariffs, staffing, safety procedures, and equipment requirements before acting on it.
