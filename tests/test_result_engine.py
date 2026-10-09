import pytest
from src.result_engine import evaluate_result_state

def test_result_state_infeasible():
    state = evaluate_result_state(
        solver_status="INFEASIBLE",
        shifted_count=0,
        baseline_grid_kwh=400.0,
        optimized_grid_kwh=400.0,
        baseline_solar_kwh=100.0,
        optimized_solar_kwh=100.0,
        baseline_cost_rs=3000.0,
        optimized_cost_rs=3000.0,
        limiting_constraint="Machine maintenance overlap"
    )
    assert state.code == "INFEASIBLE"
    assert state.is_feasible is False
    assert "NO FEASIBLE SCHEDULE" in state.title

def test_result_state_no_change():
    state = evaluate_result_state(
        solver_status="OPTIMAL",
        shifted_count=0,
        baseline_grid_kwh=400.0,
        optimized_grid_kwh=400.0,
        baseline_solar_kwh=100.0,
        optimized_solar_kwh=100.0,
        baseline_cost_rs=3000.0,
        optimized_cost_rs=3000.0
    )
    assert state.code == "NO_CHANGE"
    assert state.is_feasible is True
    assert "NO SCHEDULE CHANGE REQUIRED" in state.title

def test_result_state_no_benefit():
    state = evaluate_result_state(
        solver_status="FEASIBLE",
        shifted_count=1,
        baseline_grid_kwh=400.0,
        optimized_grid_kwh=410.0,
        baseline_solar_kwh=100.0,
        optimized_solar_kwh=90.0,
        baseline_cost_rs=3000.0,
        optimized_cost_rs=3150.0
    )
    assert state.code == "NO_BENEFIT"
    assert state.is_feasible is True
    assert "NO BENEFIT IDENTIFIED" in state.title

def test_result_state_improved():
    state = evaluate_result_state(
        solver_status="OPTIMAL",
        shifted_count=2,
        baseline_grid_kwh=400.0,
        optimized_grid_kwh=350.0,
        baseline_solar_kwh=100.0,
        optimized_solar_kwh=150.0,
        baseline_cost_rs=3000.0,
        optimized_cost_rs=2600.0
    )
    assert state.code == "IMPROVED"
    assert state.is_feasible is True
    assert "SOLAR SYNC RECOMMENDS A SCHEDULE CHANGE" in state.title
