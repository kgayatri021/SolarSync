# SolarSync feature verification

**Inspection date:** 2026-10-09

**Source of truth:** Local SolarSync source, data loader, docs, and running Streamlit interface.

**Entry point:** `app.py` (`streamlit run app.py`).

## Runtime and interface checks

- The local app responded with `ok` from `http://localhost:8501/_stcore/health`.
- Browser navigation to all seven entries below displayed the matching page heading; no visible Streamlit exception or dataset-load error was found during that navigation check.
- The initial app context is `FAC_016` when present and 2026-08-10.
- The recorded Smart Scheduler run returned `OPTIMAL`. A Scenario Simulator run completed and displayed its comparison results.
- Export controls are visible in the recording, but no report was downloaded or validated. Displayed savings and energy values are modeled estimates, not independently verified results.

## Actual pages

| Navigation entry | Verified content in implementation | Recording guidance |
|---|---|---|
| Executive Dashboard | Cluster KPIs, factory/date context, modeled solar/demand profile, baseline/candidate comparison, map visualizations, exports, and an automatic scheduler run with a five-second solver time limit. | Show actual current solver status and clarify that the dashboard runs its modeled schedule automatically. |
| Factory Intelligence | Factory metadata, capacity cards, a solar chart, machine inventory, and a workforce skill table. Its demand curve is a hard-coded representative shape scaled by machine rated power. | Do not call its demand curve metered or actual hourly production demand. Avoid the table's employee names. |
| Smart Scheduler | Objective dropdown, advanced solar-factor and time-limit controls, manual optimize button, result KPIs/charts/table/rationales, PDF/Excel/CSV exports. | The submitted recording run returned `OPTIMAL`. Only electricity-cost minimization is implemented, regardless of dropdown selection. No export download was tested. |
| Scenario Simulator | Scenario label, solar availability, solar capacity, production demand, peak-electricity-price controls, run button, impact summaries and charts. | A submitted run displayed comparison results. Solar availability and solar capacity affect solar modeling; the demand and tariff sliders do not currently alter results as presented. |
| Energy & Workforce | Solar/weather location/date selectors, irradiance KPIs and charts, 3D solar visualization, workforce staffing chart and roster table. | Workforce analysis is separate from CP-SAT. The roster includes `worker_name`; do not reveal it in video. |
| History & System Health | Historical energy summaries/charts, tariff reference chart, sample history table, seven-dataset validation matrix. | Dataset source/provenance is undocumented; call this supplied project data. |
| About SOLAR SYNC | In-app problem/solution and constraint description. | Some About-page statements do not match enforcement in `src/scheduler.py`; use this report instead of repeating those claims. |

## Scheduler and calculation findings

| Feature or narrated claim | Status | Evidence and accurate wording |
|---|---|---|
| OR-Tools CP-SAT scheduler | Implemented | `src/scheduler.py` constructs and solves a CP-SAT model. |
| Electricity-cost objective | Implemented, simplified | Objective minimizes modeled hourly grid energy cost. `src/cost_engine.py` uses fixed HT1 rates (₹9.25 peak, ₹7.25 normal, ₹5.75 off-peak); rates are not loaded from `electricity_tariffs.csv` for optimization. |
| Selectable cost/solar/workforce objective | UI present, behavior not implemented | `opt_objective` changes the session key but is not passed into `optimize_schedule`. Describe it as a displayed selector only. |
| Job release/deadline and non-shiftable bounds | Implemented with daily/hourly simplification | Start variables use release/deadline hours; non-shiftable jobs are fixed at the release hour. Duration is rounded up to whole hours. |
| Machine no-overlap | Implemented | Same-machine job intervals use CP-SAT `AddNoOverlap`. |
| Maintenance window | Implemented for parseable matching-day windows | Jobs on an affected machine are constrained before or after the configured window. |
| Factory grid-capacity limit | Implemented | Sum of modeled hourly job power is bounded by factory `grid_connection_capacity_kw`. |
| Workforce/skill availability enforced by scheduler | Not implemented | Workforce analysis is a separate UI calculation; `SolarSyncScheduler` does not impose workforce or skill constraints. |
| Staffing feasibility for optimized schedule | Not verified by current page calculation | The workforce page builds demand from job release times and compares total workers by hour. It does not use the optimized schedule or prove worker skill/max-hours feasibility. |
| Baseline vs. candidate energy/cost comparison | Implemented estimate | Baseline jobs start at release times. Metrics compare 24 hourly power arrays against modeled solar availability and fixed tariffs; not measured factory results. |
| Solver fallback | Implemented | For statuses other than `OPTIMAL`/`FEASIBLE`, the scheduler returns the baseline list and logs a warning. Show the solver status and do not present the fallback as an optimized schedule. |
| Per-job deadline status | Displayed but not independently computed | `RecommendationEngine` currently sets `deadline_status` to `"Satisfied"` for every recommendation. Do not call this field a verified deadline audit. |
| Solar weather profile | Implemented estimate | Profile uses installed PV capacity × supplied solar capacity factor; if the date is absent it falls back to a location average. Factory-location matching uses district/location text. |
| Factory Intelligence power-demand curve | Illustrative, not measured | `components/factory_view.py` constructs a fixed 24-value demand shape and scales it by total machine rated power. |

## Scenario control wiring

| Visible control | Status |
|---|---|
| Solar Availability (% of normal) | Applied as `cloud_factor` to the solar profile. |
| Solar Capacity (% of current) | Applied as a solar-capacity multiplier. |
| Production Demand (% of normal) | Not reliably applied: scenario code multiplies `estimated_duration_hours` after enrichment, while the scheduler reads the existing `duration_hours` field. |
| Peak Electricity Price (% of current) | Displayed and stored in `ScenarioParams`, but never applied to the tariff rates or scheduler objective. |
| Workforce availability factor | Exists in the parameter dataclass but is not exposed on the screen and is not used by the scenario run. |

## Supplied voice-over sections

| Script section(s) | Verification and required edit before narration |
|---|---|
| 1–2, 13, 15 | Suitable as project intent if outcomes are described as modeled estimates and intended decision support. Avoid claims of guaranteed savings, deployment, or verified real-world data. |
| 3 | Sidebar factory and date controls exist. |
| 4 | An optional Dashboard override expander exists, but its production and solar override values are not wired through to its schedule calculation. Omit or explicitly describe only as UI controls. |
| 5 | Solar and demand charts exist. Clarify that the Factory Intelligence demand shape is illustrative and that the schedule metrics are modeled. |
| 6 | Replace the claim that selected objectives control optimization: only cost minimization is implemented. Describe actual constraints accurately; workforce is not one of them. |
| 7–8 | Schedule, recommendation table, and baseline comparison exist. Explain the baseline, fixed tariff assumptions, solver status, fallback behavior, and estimates. Do not present the hard-coded deadline status as proof. |
| 9 | Scenario screen exists. Demonstrate only the solar-availability and capacity changes as working model inputs; omit claims about demand/price sliders until corrected and retested. |
| 10 | Machine and workforce information exist, but workforce is not enforced by the scheduler. Avoid exposing worker names and avoid claiming skills are validated by the optimizer. |
| 11 | Historical analytics exist; provenance and whether data are real/synthetic are unknown. |
| 12 | PDF, Excel, and CSV download controls are present on the dashboard/scheduler. Test successful downloads before narrating them as verified. |
| 14 | Explain current gaps: fixed tariff assumptions, disconnected objective/demand/price controls, separate workforce analysis, simplified daily constraints, and no live systems integration. |

## Video and voice assets

| Deliverable | Format and verification |
|---|---|
| `SolarSync_Demo.mp4` | 1920×1080 H.264/AAC, 30 FPS, approximately 5:54. Contains a real Edge recording of the running app, title cards, female narration, and burned-in captions. |
| `SolarSync_Voiceover.wav` | 22050 Hz, mono, 16-bit PCM; narration mixed and timed to the video. |
| `SolarSync_Subtitles.srt` | English sidecar subtitles aligned to the narration and scene sequence. |
| `SolarSync_Thumbnail.png` | 1280×720 thumbnail composed around a genuine application screenshot. |

The voice is Microsoft Hazel Desktop, a synthetic female voice with a British English accent; an Indian English female voice was not available, so the voice has not been mislabeled. Caption timings are apportioned within each narrated segment and should be considered approximate at individual-word granularity. The video shows the submitted scheduler's `OPTIMAL` status and a completed scenario comparison. It does not claim that export files were downloaded, and it does not show the workforce roster.
