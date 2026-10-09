# Data dictionary

The application currently has seven datasets in both the project root and `data/`. The pairs are byte-identical. The loader checks `data/` first and uses the root-level copy only as a fallback. Counts below are CSV data rows, excluding the header; sizes are approximate decimal MB.

| File | Rows | Approx. size | Key fields and relationships | Application use |
|---|---:|---:|---|---|
| `factories.csv` | 40 | 0.008 MB | `factory_id` identifies factories. | Factory metadata, installed solar and grid capacities, location matching, and selected-factory summaries. |
| `machines.csv` | 208 | 0.029 MB | `machine_id`; `factory_id` relates machines to factories. | Machine power and job-machine lookup, maintenance windows, inventory, and data checks. |
| `production_jobs.csv` | 8,495 | 1.600 MB | `job_id`; `factory_id`; `eligible_machine_id` relates jobs to machines. | Job selection, release/deadline bounds, durations, power estimates, and schedule recommendations. |
| `workforce.csv` | 469 | 0.058 MB | `worker_id`; `factory_id` relates workers to factories. | Workforce summaries and separate hourly capacity/skill analysis. Includes `worker_name`; public-sharing status must be verified. |
| `solar_weather.csv` | 10,800 | 1.732 MB | `timestamp` and `location` are checked as a compound duplicate key; factory matching uses location/district text. | Hourly weather and solar capacity-factor inputs for factory solar profiles and maps. |
| `electricity_tariffs.csv` | 8 | 0.002 MB | `tariff_id` and state/consumer/time-period descriptors. | Loaded for validation and app context. The scheduler's current rate calculation uses fixed rates in code instead of these row rates. |
| `production_energy_history.csv` | 241,402 | 27.383 MB | Contains `factory_id`, `machine_id`, `historical_job_id`, and timestamps. | Historical energy/cost analytics and arithmetic consistency checks. |

## Columns

Column names below are the exact CSV headers, grouped by file. Descriptions of purpose are based on field names and their use in the source code; source-system definitions are not supplied.

### `factories.csv`

`factory_id`, `factory_name`, `industry_type`, `location`, `district`, `state`, `factory_size`, `operating_days_per_week`, `shift_count`, `daily_operating_hours`, `opening_time`, `closing_time`, `installed_solar_capacity_kw`, `battery_capacity_kwh`, `grid_connection_capacity_kw`, `contracted_demand_kw`, `baseline_daily_energy_kwh`, `number_of_machines`, `number_of_workers`.

### `machines.csv`

`machine_id`, `factory_id`, `machine_name`, `machine_type`, `rated_power_kw`, `standby_power_kw`, `minimum_run_time_minutes`, `maximum_continuous_runtime_hours`, `production_rate_units_per_hour`, `energy_per_unit_kwh`, `machine_availability`, `available_start_time`, `available_end_time`, `maintenance_status`, `maintenance_start_time`, `maintenance_end_time`, `required_skill_level`, `workers_required`, `startup_energy_kwh`.

### `production_jobs.csv`

`job_id`, `factory_id`, `product_id`, `product_type`, `quantity_required`, `priority`, `job_release_time`, `deadline`, `estimated_duration_hours`, `eligible_machine_id`, `energy_required_kwh`, `workers_required`, `skill_required`, `can_shift`, `earliest_start_time`, `latest_start_time`, `job_status`, `flexibility_window_hours`.

### `workforce.csv`

`worker_id`, `factory_id`, `worker_name`, `worker_role`, `skill_level`, `primary_machine_skill`, `secondary_machine_skill`, `shift_start`, `shift_end`, `hourly_labour_cost`, `overtime_allowed`, `overtime_cost_per_hour`, `availability_status`, `productivity_factor`, `maximum_daily_hours`.

### `solar_weather.csv`

`timestamp`, `date`, `hour`, `location`, `latitude`, `longitude`, `temperature_c`, `relative_humidity_percent`, `cloud_cover_percent`, `wind_speed_mps`, `solar_irradiance_w_m2`, `ghi_w_m2`, `dni_w_m2`, `dhi_w_m2`, `weather_condition`, `solar_capacity_factor`, `forecast_generation_kw`, `forecast_error_percent`.

### `electricity_tariffs.csv`

`tariff_id`, `state`, `utility`, `consumer_category`, `voltage_level`, `time_period`, `start_time`, `end_time`, `energy_rate_rs_per_kwh`, `demand_charge_rs_per_kw`, `fixed_charge`, `peak_period`, `off_peak_period`, `effective_from`, `effective_to`.

### `production_energy_history.csv`

`date`, `timestamp`, `factory_id`, `machine_id`, `historical_job_id`, `product_id`, `units_produced`, `runtime_hours`, `energy_consumed_kwh`, `solar_energy_used_kwh`, `grid_energy_used_kwh`, `workers_used`, `labour_cost_rs`, `electricity_cost_rs`, `total_operating_cost_rs`.

## Relationships and validation

- `factory_id` connects factories to their machines, jobs, and workers. The validator checks factory IDs and declared machine/worker counts.
- `eligible_machine_id` connects a job to its eligible machine; the validator checks that referenced machines belong to the job's factory.
- Historical rows include factory and machine IDs, but the validator currently checks energy/cost arithmetic rather than all historical foreign-key relationships.
- Solar weather is associated to factories by matching the factory district/location text against weather locations. It is not linked through a dedicated location ID.
- `solar_weather.csv` is checked for duplicate `(timestamp, location)` pairs. Other key uniqueness checks are implemented for factory, machine, worker, and job IDs.

## Provenance, privacy, and sharing

No source citation, data-generation note, or dataset license was found in the inspected project files. The project owner confirmed that the code and datasets are cleared for public release, but source provenance and downstream reuse terms remain undocumented; this document does not label the data synthetic or real. `workforce.csv` has a `worker_name` field. The MIT license in the repository applies to source code only, not the datasets.
