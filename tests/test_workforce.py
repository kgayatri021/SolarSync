import os
import sys
import pytest

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.data_loader import load_workforce, load_machines
from src.workforce_optimizer import WorkforceOptimizer

def test_workforce_optimizer():
    workforce = load_workforce()
    machines = load_machines()
    opt = WorkforceOptimizer(workforce, machines)

    capacity = opt.get_hourly_worker_capacity("FAC_001")
    assert "total_workers_available" in capacity
    assert len(capacity["total_workers_available"]) == 24
    assert (capacity["total_workers_available"] >= 0).all()
