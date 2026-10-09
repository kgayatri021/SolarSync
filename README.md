# SolarSync — Solar-Aware Industrial Production and Workforce Optimization System

A decision-support application for exploring solar-aware production scheduling and electricity-cost optimization in manufacturing.

**Hackathon:** DRE Enterprise Hackathon '26  
**Problem Statement:** PS07 — Solar-Aware Demand Shifting Scheduler

## Project overview

SolarSync is a Python and Streamlit application for exploring how production job timing, modeled solar availability, and time-of-use electricity prices interact. It is intended to help factory managers compare a release-time baseline with a candidate schedule and review modeled energy and electricity-cost impacts before making operational decisions.

Factories cannot move every job freely: jobs have release times and deadlines, machines may have maintenance windows, and machines cannot run overlapping jobs. The application models some of these constraints, but its current optimizer does not enforce workforce availability or skills. Its results are simulations based on the supplied CSVs and fixed model assumptions, not a live forecast or guaranteed savings.

## What is implemented

- Seven-screen Streamlit interface: Executive Dashboard, Factory Intelligence, Smart Scheduler, Scenario Simulator, Energy & Workforce, History & System Health, and About.
- CSV loading, data-quality checks, factory/machine/workforce summaries, and historical energy analytics.
- Hourly solar-availability profiles derived from the weather data and a factory's installed solar capacity.
- OR-Tools CP-SAT scheduling that minimizes modeled electricity cost subject to job time bounds, same-machine non-overlap, configured maintenance windows, and a grid-capacity bound.
- Baseline-versus-scheduled energy and electricity-cost metrics, per-job rationale, and PDF, Excel, and CSV exports.
- Scenario controls for solar availability, installed solar capacity, demand, and peak tariffs. Some displayed controls are not currently applied to the calculations; see [Limitations](docs/limitations.md).

Workforce analysis is available separately from the CP-SAT scheduling constraints. The optimizer currently uses a fixed tariff schedule rather than the tariff rates in `electricity_tariffs.csv`. See [Architecture](docs/architecture.md) and [Optimization logic](docs/optimization_logic.md) for details.

## Technologies

- **Python** — application and model code.
- **Streamlit** — interactive local web interface.
- **Pandas and NumPy** — CSV loading and numerical calculations.
- **OR-Tools CP-SAT** — bounded production-job scheduling.
- **Plotly** — interactive charts and factory/solar visualizations.
- **ReportLab and OpenPyXL** — PDF and Excel decision reports.
- **pytest** — automated tests.

## Project structure

```text
SolarSync/
├── app.py                  # Streamlit entry point
├── requirements.txt        # Runtime and test dependencies
├── factories.csv           # Root-level copy of each CSV is also in data/
├── machines.csv
├── production_jobs.csv
├── workforce.csv
├── solar_weather.csv
├── electricity_tariffs.csv
├── production_energy_history.csv
├── data/                   # Seven byte-identical CSV copies; loader checks here first
├── components/             # Streamlit screens, charts, and visualizations
├── src/                    # Data, validation, energy, scheduling, and report logic
├── tests/                  # Automated tests
└── docs/                   # Overview, architecture, data dictionary, guide, limitations
```

The root and `data/` copies of all seven datasets are currently byte-identical. `src/utils.py` resolves each dataset from `data/` first and falls back to the root copy.

## Data

The supplied CSVs contain factory, machine, job, workforce, weather/solar, tariff, and historical energy records. The repository does not document their source or licensing, so it does not characterize them as real or synthetic. `workforce.csv` includes a `worker_name` column; verify that it is synthetic, anonymized, or otherwise cleared for public release before publishing the data.

See the [data dictionary](docs/data_dictionary.md) for row counts, columns, relationships, and current use. The historical CSV is about 27.4 MB (decimal), below GitHub's 100 MB per-file limit, but the duplicate copies increase repository size.

## Installation and run

Python 3.10 or later is recommended.

From the project root, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, allow it for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux, activate with:

```bash
source .venv/bin/activate
```

Install dependencies and start the app:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501). Run the tests from the project root with:

```bash
python -m pytest -q
```

Once a GitHub repository exists, use its actual clone URL from GitHub before following these local setup steps; this workspace currently has no Git repository or remote configured.

## Results and responsible use

The application calculates scenario-specific model outputs; this README makes no claim of measured savings, operational deployment, or guaranteed improvement. Review the solver status, inputs, and limitations before using any output in planning. SolarSync is decision support only and does not control factory equipment or electricity grids.

## Documentation

- [Project overview](docs/project_overview.md)
- [Architecture and data flow](docs/architecture.md)
- [Dataset columns and relationships](docs/data_dictionary.md)
- [Optimization formulation and implemented constraints](docs/optimization_logic.md)
- [User guide](docs/user_guide.md)
- [Limitations and future work](docs/limitations.md)

## License and data rights

The source code is released under the [MIT License](LICENSE). This license does not cover the supplied datasets. You confirmed that the code and datasets are cleared for public release, but dataset sources and downstream reuse terms are not documented. `workforce.csv` includes a `worker_name` column; do not describe the data as synthetic or apply the code license to it without separate supporting terms.
