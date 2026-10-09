# SolarSync demonstration recording plan

**Project:** SolarSync — Solar-Aware Industrial Production and Workforce Optimization System

**Hackathon:** DRE Enterprise Hackathon '26

**Problem statement:** PS07 — Solar-Aware Demand Shifting Scheduler

**Application entry point:** `app.py`

**Run command:** `streamlit run app.py`
**Local application:** `http://localhost:8501`

## Scope and recording status

This plan maps the narrated demonstration to the application's seven Streamlit pages and current implementation. On 2026-10-09, the local app responded successfully and all seven page headings were browser-verified. The real Microsoft Edge recording shows the Executive Dashboard, Factory Intelligence, Smart Scheduler, Scenario Simulator, Energy & Workforce, and History & System Health; the About page is omitted because some of its claims exceed the implementation. A manual Smart Scheduler run returned `OPTIMAL`; a Scenario Simulator run completed and displayed its results. The recording shows export controls but does not claim that a report was downloaded or independently checked.

The final video combines genuine application captures with opening and closing title cards, a female synthetic voice-over, and English captions. The available voice is Microsoft Hazel Desktop (English, Great Britain), not Indian English. No worker names are shown.

## Screen-by-screen plan

| Script section | Actual screen and action | What can be explained accurately | Changes or cautions for narration |
|---|---|---|---|
| 1. Introduction | Executive Dashboard; show the app title and PS07 label. | The prototype's stated problem and decision-support purpose. | Do not imply industrial deployment, endorsement, or guaranteed savings. |
| 2. Proposed solution | Executive Dashboard; briefly show its solar/demand chart and comparison area. | Python/Streamlit interface, supplied CSV inputs, and modeled comparison. | Say tariff rates used by the scheduler are fixed in code; do not imply the tariff CSV's rates drive its optimizer. |
| 3. Factory and date | Sidebar; point out “Active Industrial Facility” and “Target Analysis Date.” | The selected factory and date are shared context. Defaults are `FAC_016` when present and 2026-08-10. | Do not imply every page uses these controls in the same way; solar analytics has its own location/date selectors. |
| 4. Operating conditions | Optionally open the Dashboard's “Today's Operating Conditions & Real-World Overrides” expander. | The interface offers dataset/override modes and sliders for production demand and expected solar generation. | The override sliders are not passed through to the dashboard's scheduler as displayed; do not claim they alter its results. Prefer omitting this expander from the demo. |
| 5. Solar and production demand | Executive Dashboard chart “Solar Availability vs Production Demand”; optionally Factory Intelligence chart. | Dashboard plots solar availability against a baseline demand profile and a scheduler-produced profile. | Factory Intelligence's demand curve is a fixed illustrative shape scaled by machine power, not measured hourly factory demand. Identify the Dashboard curves as modelled if discussing them. |
| 6. Smart Scheduler | Smart Scheduler; show its optimization-objective selector and “Advanced Settings & Solver Parameters.” | The action button requests a CP-SAT run. The implemented objective minimizes modeled electricity cost. Advanced controls include solar weather adjustment and solver time limit. | The displayed objective choices are not wired into the solver: all choices use electricity-cost minimization. Explain only implemented job bounds, machine no-overlap, applicable maintenance windows, and grid-capacity constraints. |
| 7. Scheduling results | Submit the Smart Scheduler run; the recorded run returned `OPTIMAL`. | The table compares baseline and recommended start times and shows modeled solar/grid energy and per-job rationale. | Baseline starts jobs at release time. Non-feasible/unknown outcomes fall back to baseline. The displayed deadline status is hard-coded, so do not describe it as an independent deadline audit. |
| 8. Baseline comparison | Smart Scheduler comparison chart and KPI cards. | The app compares hourly modeled demand and calculated grid energy, solar use, and electricity cost. | Rates are fixed HT1 values in `src/cost_engine.py`; hourly durations are rounded up. These are estimates, not measured savings or a validated factory bill. |
| 9. Scenario Simulator | Submit the recorded “Cloudy Day & Solar Expansion Test” run (70% solar availability, 140% capacity). | The results page displays the scenario comparison. | Solar availability and capacity affect the solar model. Do not attribute the displayed change to the production-demand or peak-price controls; those are not reliably applied. |
| 10. Workforce and machines | Factory Intelligence machine inventory, then Energy & Workforce staffing view. | Machine details and separate workforce supply/production-shift-demand summaries are present. | Workforce is not a CP-SAT scheduling constraint. The staffing chart uses release-time demand, not the optimized schedule; skill and maximum-hours feasibility are not established by that chart. Avoid exposing the worker roster's `worker_name` column. |
| 11. Historical analytics | History & System Health; show the historical analytics tab and, optionally, its validation tab. | The UI summarizes supplied historical energy records and runs dataset/formula checks. | Dataset provenance is undocumented. Describe the records as supplied project data, not as independently verified real-world operating data. |
| 12. Reports and exports | Show the Smart Scheduler's PDF, spreadsheet, and CSV controls. | Export controls are present in the application. | No export download was performed or validated in this recording. |
| 13. Usefulness | Return to Executive Dashboard. | SolarSync brings selected factory, modeled solar, jobs, and estimates into one interface for human review. | Frame benefits as intended decision support, not demonstrated production impact. |
| 14. Limitations and future scope | Dashboard or About screen, with concise text overlay if editing is available. | Explain simplified day-ahead model, fixed tariff assumptions, separate workforce analysis, unsupported controls, and missing live integrations. | The About page itself contains claims that exceed the scheduler implementation; do not repeat its workforce-constraint or “zero fake data” claims. |
| 15. Conclusion | Return to the Executive Dashboard and finish on a closing title card. | Restate the PS07 goal and decision-support nature. | Use no unverified result, deployment, prize, or endorsement claim. |

## Captured sequence

1. Open on a SolarSync title card, then show the live Executive Dashboard and its shared facility/date context.
2. Scroll through the dashboard comparison and visit Factory Intelligence.
3. Expand Smart Scheduler settings, submit an optimization, and show the returned `OPTIMAL` result.
4. Submit the Scenario Simulator and show its result; narrate only the controls that actually affect the model.
5. Visit Energy & Workforce, History & System Health, and the scheduler export controls. The worker roster is not exposed, and no downloads are claimed.
6. Return to the dashboard and close with a title card.

## Production and editorial notes

- The exported MP4 is 16:9, 1920×1080, H.264/AAC, 30 FPS, and approximately 5 minutes 54 seconds. The original browser capture was 25 FPS and was converted during export.
- The MP4 contains burned-in English captions; a separate SRT file is also provided. Captions are timed within each narration clip and synchronized to the recorded scene sequence.
- Microsoft Hazel Desktop is a female synthetic voice with a British English accent. It is not Indian English.
- All schedule, scenario, and savings figures shown are application-generated estimates. Data provenance is not independently verified; export downloads were not tested.
