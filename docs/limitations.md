# Limitations and future work

## Verified limitations

- **Data provenance and reuse terms:** The project contains no dataset source notes or data license. The project owner confirmed permission to publish the code and datasets, but the data's provenance and downstream reuse terms are not documented. `workforce.csv` includes a `worker_name` column.
- **Separate code and data terms:** The source code is licensed under MIT. That license does not cover the CSV datasets; document separate data terms if their downstream reuse is intended.
- **Workforce not enforced by scheduler:** `WorkforceOptimizer` produces separate staffing summaries, but `SolarSyncScheduler` does not use its workforce availability or skills as CP-SAT constraints. Scheduler metrics are calculated without labor/overtime arrays.
- **Tariff CSV is not used for optimization rates:** `CostEngine` uses fixed HT1 rates (₹9.25 peak, ₹7.25 normal, ₹5.75 off-peak); it does not derive hourly rates from `electricity_tariffs.csv`.
- **Some controls do not affect calculations:** The scheduler objective selector is not passed to the scheduler. The scenario peak-tariff multiplier is recorded/displayed but is not applied to the tariff rates. The demand multiplier scales `estimated_duration_hours` after job enrichment, but the scheduler prefers the already-populated `duration_hours`; consequently the slider does not reliably alter the modeled job duration.
- **Simplified schedule constraints:** The model is hourly and limited to a 24-hour day. It rounds job durations up to whole hours and does not enforce machine available-start/end fields, job earliest/latest-start fields, skill requirements, or multi-day scheduling. Its grid-capacity constraint applies to total scheduled machine demand.
- **Scenario coverage:** `ScenarioParams` contains a workforce availability factor, but the scenario screen does not expose or apply it to the scheduler.
- **Data selection fallback:** When a factory has no jobs released on the selected date, the data engine tries jobs active that day (up to ten) and then the first ten jobs for that factory. Check the selected jobs before interpreting a result.
- **Weather fallback:** If no solar record exists for the requested date, the solar engine uses an hourly average for the matched location. If no location matches, it chooses the first weather location.
- **Duplicate datasets:** The seven CSVs exist both at the root and under `data/`. The copies are currently byte-identical, but this increases the checkout size and creates a risk of drift if only one copy is updated.
- **Model outputs are not operational results:** The app is a local decision-support prototype. It has no live utility, weather, factory-control, or production-system integration and makes no guarantee of savings or feasibility in a real facility.

## Future work

1. Establish and document data provenance, privacy review, and redistribution permissions; anonymize or remove personal data only with an approved plan.
2. Select an appropriate code license and document separate dataset terms.
3. Connect tariff records and scenario tariff changes to the actual hourly objective.
4. Define and implement each selectable optimization objective, or remove controls that are not supported.
5. Integrate workforce, skill, shift, overtime, machine availability, and job-window requirements into a validated scheduling model.
6. Replace fallback job selection with transparent user-selected scope and report which jobs were scheduled.
7. Consolidate the duplicate CSV copies after confirming and testing the intended canonical data location.
8. Add verified data citations, reproducible result examples, and deployment integrations only when available.
