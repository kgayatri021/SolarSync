import os
import sys
import pytest

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.data_loader import load_all_datasets
from components.dashboard import render_executive_dashboard
from components.factory_view import render_factory_view
from components.energy_workforce_view import render_energy_workforce_view
from components.history_health_view import render_history_health_view
from components.three_d_visuals import plot_3d_factory_cluster, plot_2d_factory_cluster_map

def test_components_import_and_execution():
    datasets = load_all_datasets()
    assert datasets is not None
    
    # Verify 3D and 2D visual components run without exception
    fig_3d = plot_3d_factory_cluster(datasets["factories"])
    assert fig_3d is not None
    
    fig_2d = plot_2d_factory_cluster_map(datasets["factories"])
    assert fig_2d is not None
