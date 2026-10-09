# SolarSync demonstration recording plan

**Project:** SolarSync — Solar-Aware Industrial Production and Workforce Optimization System

**Hackathon:** DRE Enterprise Hackathon '26

**Problem statement:** PS07 — Solar-Aware Demand Shifting Scheduler

**Application entry point:** `app.py`

**Run command:** `streamlit run app.py`
**Local application:** `http://localhost:8501`

## Scope and recording status

This plan maps the supplied narration to the actual seven-page Streamlit navigation and the source code as inspected on 2026-10-09. The live application health endpoint returned `ok`; browser navigation confirmed that all seven page headings rendered without a visible Streamlit error. Navigating to a page is not the same as testing every button or downloading every report: a scheduler optimization and a scenario run were not manually submitted as part of this inspection.

No screen-recording or video-editing application, FFmpeg executable, or audio/video Python toolkit was available in the inspected environment. Therefore, no screen recording or video has been made. Local speech synthesis is available, but the installed female voices are English (United States) and English (Great Britain), not Indian English. No narration, subtitles, thumbnail, or MP4 has been generated.

## Screen-by-screen plan

| Script section | Actual screen and action | What can be explained accurately | Changes or cautions for narration |
|---|---|---|---|
| 1. Introduction | Executive Dashboard; show the app title and PS07 label. | The prototype's stated problem and decision-support purpose. | Do not imply industrial deployment, endorsement, or guaranteed savings. |
| 2. Proposed solution | Executive Dashboard; briefly show its solar/demand chart and comparison area. | Python/Streamlit interface, supplied CSV inputs, and modeled comparison. | Say tariff rates used by the scheduler are fixed in code; do not imply the tariff CSV's rates drive its optimizer. |
| 3. Factory and date | Sidebar; point out “Active Industrial Facility” and “Target Analysis Date.” | The selected factory and date are shared context. Defaults are `FAC_016` when present and 2026-08-10. | Do not imply every page uses these controls in the same way; solar analytics has its own location/date selectors. |
| 4. Operating conditions | Optionally open the Dashboard's “Today's Operating Conditions & Real-World Overrides” expander. | The interface offers dataset/override modes and sliders for production demand and expected solar generation. | The override sliders are not passed through to the dashboard's scheduler as displayed; do not claim they alter its results. Prefer omitting this expander from the demo. |
| 5. Solar and production demand | Executive Dashboard chart “Solar Availability vs Production Demand”; optionally Factory Intelligence chart. | Dashboard plots solar availability against a baseline demand profile and a scheduler-produced profile. | Factory Intelligence's demand curve is a fixed illustrative shape scaled by machine power, not measured hourly factory demand. Identify the Dashboard curves as modelled if discussing them. |
| 6. Smart Scheduler | Smart Scheduler; show its optimization-objective selector and “Advanced Settings & Solver Parameters.” | The action button requests a CP-SAT run. The implemented objective minimizes modeled electricity cost. Advanced controls include solar weather adjustment and solver time limit. | The displayed objective choices are not wired into the solver: all choices use electricity-cost minimization. Explain only implemented job bounds, machine no-overlap, applicable maintenance windows, and grid-capacity constraints. |
| 7. Scheduling results | After deliberately submitting a run, show solver status and the schedule table. | The table compares baseline and recommended start times and shows modeled solar/grid energy and per-job rationale. | Baseline starts jobs at release time. Show the actual solver status; non-feasible/unknown outcomes fall back to baseline. The displayed deadline status is hard-coded, so do not describe it as an independent deadline audit. |
| 8. Baseline comparison | Smart Scheduler comparison chart and KPI cards. | The app compares hourly modeled demand and calculated grid energy, solar use, and electricity cost. | Rates are fixed HT1 values in `src/cost_engine.py`; hourly durations are rounded up. These are estimates, not measured savings or a validated factory bill. |
| 9. Scenario Simulator | Show scenario controls; run only after confirming the chosen case and solver status. | Solar availability (`cloud_factor`) and solar capacity multiplier are passed into solar-profile generation and can change that model input. | Do not claim that the production-demand or peak-price sliders change calculated results: the demand multiplier is not applied to the scheduler's enriched duration, and the tariff multiplier is recorded/displayed but not applied to tariff rates. |
| 10. Workforce and machines | Factory Intelligence machine inventory, then Energy & Workforce staffing view. | Machine details and separate workforce supply/production-shift-demand summaries are present. | Workforce is not a CP-SAT scheduling constraint. The staffing chart uses release-time demand, not the optimized schedule; skill and maximum-hours feasibility are not established by that chart. Avoid exposing the worker roster's `worker_name` column. |
| 11. Historical analytics | History & System Health; show the historical analytics tab and, optionally, its validation tab. | The UI summarizes supplied historical energy records and runs dataset/formula checks. | Dataset provenance is undocumented. Describe the records as supplied project data, not as independently verified real-world operating data. |
| 12. Reports and exports | Smart Scheduler export area. | The source generates PDF, Excel, and CSV download buttons. | Only claim a format works after testing its download during recording. Avoid showing unrelated local files in any download dialog. |
| 13. Usefulness | Return to Executive Dashboard. | SolarSync brings selected factory, modeled solar, jobs, and estimates into one interface for human review. | Frame benefits as intended decision support, not demonstrated production impact. |
| 14. Limitations and future scope | Dashboard or About screen, with concise text overlay if editing is available. | Explain simplified day-ahead model, fixed tariff assumptions, separate workforce analysis, unsupported controls, and missing live integrations. | The About page itself contains claims that exceed the scheduler implementation; do not repeat its workforce-constraint or “zero fake data” claims. |
| 15. Conclusion | Executive Dashboard title, then a simple closing title card. | Restate the PS07 goal and decision-support nature. | Use no unverified result, deployment, prize, or endorsement claim. |

## Suggested recording sequence

1. Use a clean browser window at a readable zoom and open the running app at `http://localhost:8501`.
2. Hide notifications and unrelated desktop content. Keep developer tools, personal email, authentication pages, file paths, and tokens out of frame.
3. Show the Executive Dashboard first. Let its automatic model calculation finish; capture only the result and solver status actually displayed.
4. Show the shared factory/date selectors. Keep the defaults unless a deliberate, data-backed alternative date/factory has been checked.
5. Visit Factory Intelligence and Energy & Workforce. Do not expose individual worker names or present the staffing analysis as a scheduler constraint.
6. Visit Smart Scheduler. If demonstrating the run button, wait for completion and verify the solver status before narrating the output. Use only an objective label that is honestly described as a UI choice, not as an implemented change in the optimization objective.
7. Show the baseline comparison and export controls. Test file downloads outside the recorded segment first.
8. Demonstrate a Scenario Simulator run using solar availability and/or solar capacity only. Do not attribute changes to the unimplemented demand or tariff multipliers.
9. Visit History & System Health and About only for claims consistent with the feature-verification report.
10. Return to the dashboard for a brief closing.

## Production and editorial notes

- Target a 16:9 desktop capture, 1920×1080 at 30 FPS if the eventual recorder supports it.
- Record the application itself, not a recreated dashboard or slideshow. Use slow pointer movements and deliberate pauses for charts and solver runs.
- Record voice separately, then align captions to the final edited narration. The subtitle file must be timed to the actual final audio; do not create placeholder timings.
- The requested female Indian English voice is not available in the installed local voices. Select a suitable Indian English female voice before recording or use a human narrator; do not label a US/UK synthetic voice as Indian English.
- Use only properly licensed instrumental music, if any, mixed quietly below the narration.
- Review the full export for readable text, genuine app output, privacy, synchronization, and playback before delivery.
