import os
import sys
import pytest

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.data_loader import load_all_datasets
from src.validation import run_full_system_validation

def test_full_system_validation():
    datasets = load_all_datasets()
    assert len(datasets) == 7
    report = run_full_system_validation(datasets)
    assert report.is_healthy is True
    assert len(report.summary_errors) == 0

def test_factory_counts():
    datasets = load_all_datasets()
    factories = datasets["factories"]
    machines = datasets["machines"]
    workforce = datasets["workforce"]
    
    assert len(factories) == 40
    assert len(machines) == 208
    assert len(workforce) == 469
