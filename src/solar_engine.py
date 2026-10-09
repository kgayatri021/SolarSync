import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.logger import logger

class SolarEngine:
    def __init__(self, solar_weather_df: pd.DataFrame, factories_df: pd.DataFrame):
        self.solar_df = solar_weather_df.copy()
        self.factories_df = factories_df.copy()
        
        # Ensure timestamp and date format
        if "timestamp" in self.solar_df.columns and not pd.api.types.is_datetime64_any_dtype(self.solar_df["timestamp"]):
            self.solar_df["timestamp"] = pd.to_datetime(self.solar_df["timestamp"])
        if "date" in self.solar_df.columns:
            self.solar_df["date_str"] = pd.to_datetime(self.solar_df["date"]).dt.strftime("%Y-%m-%d")

        self.locations_in_solar = self.solar_df["location"].unique().tolist()
        self._build_factory_location_map()

    def _build_factory_location_map(self):
        """Maps each factory_id to the most appropriate weather location."""
        self.factory_location_map = {}
        for _, f in self.factories_df.iterrows():
            fid = f["factory_id"]
            district = str(f.get("district", "")).lower()
            loc = str(f.get("location", "")).lower()

            matched = None
            for sol_loc in self.locations_in_solar:
                sol_loc_lower = sol_loc.lower()
                if district and district in sol_loc_lower:
                    matched = sol_loc
                    break
                elif loc and loc in sol_loc_lower:
                    matched = sol_loc
                    break
            
            if not matched:
                matched = self.locations_in_solar[0] # Default fallback
            self.factory_location_map[fid] = matched

    def get_solar_profile_for_factory(
        self, 
        factory_id: str, 
        target_date: str, 
        cloud_factor: float = 1.0, 
        solar_capacity_multiplier: float = 1.0
    ) -> pd.DataFrame:
        """
        Returns 24-hour solar availability profile for a factory on a given date (YYYY-MM-DD).
        Calculates:
        - solar_capacity_factor (adjusted for cloud_factor scenario if specified)
        - solar_available_kw = installed_solar_capacity_kw * solar_capacity_factor * solar_capacity_multiplier
        - solar_available_kwh (1-hour energy = kw)
        """
        factory_info = self.factories_df[self.factories_df["factory_id"] == factory_id]
        if factory_info.empty:
            raise ValueError(f"Factory ID {factory_id} not found.")

        installed_kw = float(factory_info.iloc[0]["installed_solar_capacity_kw"])
        weather_loc = self.factory_location_map.get(factory_id, self.locations_in_solar[0])

        target_date_str = pd.to_datetime(target_date).strftime("%Y-%m-%d")
        
        subset = self.solar_df[
            (self.solar_df["location"] == weather_loc) & 
            (self.solar_df["date_str"] == target_date_str)
        ].sort_values("hour")

        if subset.empty:
            # Fallback if specific date not found: pick mean profile across all dates for location
            logger.warning(f"No exact solar weather data for {weather_loc} on {target_date_str}. Using location average.")
            subset = self.solar_df[self.solar_df["location"] == weather_loc].groupby("hour").mean(numeric_only=True).reset_index()

        profile = subset.copy()
        
        # Adjust capacity factor for cloud conditions (cloud_factor = 1.0 is normal, 0.5 is heavy cloud)
        adj_capacity_factor = profile["solar_capacity_factor"] * cloud_factor
        adj_capacity_factor = np.clip(adj_capacity_factor, 0.0, 1.0)
        
        profile["adjusted_capacity_factor"] = adj_capacity_factor
        profile["installed_solar_capacity_kw"] = installed_kw * solar_capacity_multiplier
        profile["solar_available_kw"] = profile["installed_solar_capacity_kw"] * profile["adjusted_capacity_factor"]
        profile["solar_available_kwh"] = profile["solar_available_kw"] * 1.0 # 1 hour resolution

        return profile[["hour", "timestamp", "temperature_c", "cloud_cover_percent", "solar_irradiance_w_m2", 
                        "adjusted_capacity_factor", "installed_solar_capacity_kw", "solar_available_kw", "solar_available_kwh"]]

    def get_hourly_solar_array(
        self, 
        factory_id: str, 
        target_date: str, 
        cloud_factor: float = 1.0,
        solar_capacity_multiplier: float = 1.0
    ) -> np.ndarray:
        """Returns 24-length array of available solar kWh for hours 0..23."""
        df = self.get_solar_profile_for_factory(factory_id, target_date, cloud_factor, solar_capacity_multiplier)
        full_hours = pd.DataFrame({"hour": list(range(24))})
        merged = pd.merge(full_hours, df, on="hour", how="left").fillna(0.0)
        return merged["solar_available_kwh"].to_numpy()
