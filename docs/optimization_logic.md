# Scheduling and calculation logic

## Baseline and candidate schedules

The Smart Scheduler requests jobs for a selected factory and date from `DemandEngine`. The baseline places each job at the hour of its `job_release_time`. The CP-SAT model then chooses integer-hour start times for jobs and compares the resulting 24-hour demand profile with that baseline.

Job duration is rounded up to a whole number of hours for the scheduler. For shiftable jobs, the start range begins at the release hour and ends no later than the computed deadline hour minus the duration. Non-shiftable jobs have a fixed start at the release hour. The implementation is a daily, 24-hour model rather than a multi-day schedule.

## Implemented CP-SAT constraints

- **Release and deadline bounds:** Start times are bounded by the release hour and calculated deadline hour.
- **Fixed jobs:** Jobs with `can_shift` false remain at their release hour.
- **Machine no-overlap:** Intervals for jobs assigned to the same machine may not overlap.
- **Maintenance:** For scheduled maintenance windows that can be parsed for the target date, each job on that machine must finish before the window or start after it.
- **Grid connection:** The sum of scheduled machine demand for each hour is constrained to the factory's `grid_connection_capacity_kw`.

The scheduler does not enforce workforce availability, worker skills, machine availability hours, job-provided earliest/latest start fields, or workforce/overtime cost. The workforce analyzer is a separate calculation and does not add constraints to the CP-SAT model.

## Objective and energy/cost calculations

The CP-SAT objective minimizes the sum of hourly modeled grid energy multiplied by an hourly tariff rate. Solar available to a factory is estimated as:

```text
installed solar capacity × weather solar capacity factor
```

The `cloud_factor` and `solar_multiplier` parameters scale that estimate for simulations. At each hour, reported solar use is the smaller of scheduled demand and available solar; grid use is the remaining demand.

The `CostEngine` currently supplies fixed HT1 rates: ₹9.25/kWh from 18:00–21:59, ₹7.25/kWh from 06:00–17:59, and ₹5.75/kWh for the remaining hours. It does not read the rate values from `electricity_tariffs.csv` when calculating the schedule objective. The scheduler's baseline and optimized metrics also do not pass labor or overtime arrays, so those cost metrics are zero for these runs.

The UI offers objective labels for solar utilization and a cost/solar/workforce balance, but the selected label is not passed to the scheduler: the model minimizes modeled electricity cost in all cases.

## Solver outcomes

For `OPTIMAL` or `FEASIBLE` solver status, the app displays the model's candidate jobs and baseline comparison. For other statuses, the scheduler returns the baseline job list and logs a warning. Interpret the solver status alongside any displayed result; a baseline fallback is not an optimized solution.

The displayed comparisons are calculations over provided CSV data and model assumptions. They are not measured operational results, and no savings are guaranteed.
