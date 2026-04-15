from __future__ import annotations

import csv
import os
from pathlib import Path

from src.models.data_models import (
    Charger,
    District,
    HealthImpact,
    MonthlyUsage,
    PropertyImpact,
    Subsidy,
    WasteRecycling,
)

DATA_DIR = Path(os.environ.get("EV_DATA_DIR", Path(__file__).parent.parent / "data"))


def _read_csv(filename: str) -> list[dict[str, str]]:
    path = DATA_DIR / filename
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_districts() -> list[District]:
    return [
        District(
            district_id=row["district_id"],
            district_name=row["district_name"],
            province=row["province"],
            population=int(row["population"]),
            area_km2=float(row["area_km2"]),
            avg_property_value_eur=float(row["avg_property_value_eur"]),
            ev_adoption_rate_pct=float(row["ev_adoption_rate_pct"]),
            tourism_visitors_annual=int(row["tourism_visitors_annual"]),
            air_quality_index=int(row["air_quality_index"]),
            healthcare_cost_per_capita_eur=float(row["healthcare_cost_per_capita_eur"]),
        )
        for row in _read_csv("districts.csv")
    ]


def load_chargers() -> list[Charger]:
    return [
        Charger(
            charger_id=row["charger_id"],
            district_id=row["district_id"],
            location_name=row["location_name"],
            charger_type=row["charger_type"],
            power_kw=int(row["power_kw"]),
            install_cost_eur=float(row["install_cost_eur"]),
            install_date=row["install_date"],
            status=row["status"],
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            daily_sessions_avg=int(row["daily_sessions_avg"]),
            avg_session_kwh=float(row["avg_session_kwh"]),
            fee_per_kwh_eur=float(row["fee_per_kwh_eur"]),
            monthly_maintenance_eur=float(row["monthly_maintenance_eur"]),
            subsidy_received_eur=float(row["subsidy_received_eur"]),
        )
        for row in _read_csv("chargers.csv")
    ]


def load_monthly_usage() -> list[MonthlyUsage]:
    return [
        MonthlyUsage(
            charger_id=row["charger_id"],
            month=int(row["month"]),
            year=int(row["year"]),
            total_sessions=int(row["total_sessions"]),
            total_kwh=float(row["total_kwh"]),
            revenue_eur=float(row["revenue_eur"]),
            energy_cost_eur=float(row["energy_cost_eur"]),
            downtime_hours=float(row["downtime_hours"]),
            unique_users=int(row["unique_users"]),
        )
        for row in _read_csv("monthly_usage.csv")
    ]


def load_waste_recycling() -> list[WasteRecycling]:
    return [
        WasteRecycling(
            district_id=row["district_id"],
            year=int(row["year"]),
            waste_tons_total=float(row["waste_tons_total"]),
            waste_tons_recycled=float(row["waste_tons_recycled"]),
            waste_tons_landfill=float(row["waste_tons_landfill"]),
            landfill_cost_per_ton_eur=float(row["landfill_cost_per_ton_eur"]),
            recycling_revenue_per_ton_eur=float(row["recycling_revenue_per_ton_eur"]),
            recycling_jobs_created=int(row["recycling_jobs_created"]),
            ev_battery_recycling_tons=float(row["ev_battery_recycling_tons"]),
            ev_battery_recycling_revenue_eur=float(row["ev_battery_recycling_revenue_eur"]),
            co2_avoided_tons=float(row["co2_avoided_tons"]),
        )
        for row in _read_csv("waste_recycling.csv")
    ]


def load_health_impact() -> list[HealthImpact]:
    return [
        HealthImpact(
            district_id=row["district_id"],
            year=int(row["year"]),
            pm25_reduction_pct=float(row["pm25_reduction_pct"]),
            nox_reduction_pct=float(row["nox_reduction_pct"]),
            respiratory_cases_avoided=int(row["respiratory_cases_avoided"]),
            healthcare_savings_eur=float(row["healthcare_savings_eur"]),
            premature_deaths_avoided=float(row["premature_deaths_avoided"]),
            productivity_days_gained=int(row["productivity_days_gained"]),
            ev_km_displaced_fossil=int(row["ev_km_displaced_fossil"]),
            co2_savings_tons=float(row["co2_savings_tons"]),
        )
        for row in _read_csv("health_impact.csv")
    ]


def load_property_impact() -> list[PropertyImpact]:
    return [
        PropertyImpact(
            district_id=row["district_id"],
            year=int(row["year"]),
            properties_within_500m=int(row["properties_within_500m"]),
            avg_value_before_eur=float(row["avg_value_before_eur"]),
            avg_value_after_eur=float(row["avg_value_after_eur"]),
            value_uplift_pct=float(row["value_uplift_pct"]),
            total_uplift_eur=float(row["total_uplift_eur"]),
            tourism_revenue_baseline_eur=float(row["tourism_revenue_baseline_eur"]),
            tourism_revenue_with_ev_eur=float(row["tourism_revenue_with_ev_eur"]),
            tourism_uplift_eur=float(row["tourism_uplift_eur"]),
        )
        for row in _read_csv("property_impact.csv")
    ]


def load_subsidies() -> list[Subsidy]:
    return [
        Subsidy(
            subsidy_id=row["subsidy_id"],
            district_id=row["district_id"],
            program_name=row["program_name"],
            amount_eur=float(row["amount_eur"]),
            year_granted=int(row["year_granted"]),
            charger_ids=[c.strip() for c in row["charger_ids"].split(",")],
            payback_period_years=float(row["payback_period_years"]),
            status=row["status"],
            funding_source=row["funding_source"],
        )
        for row in _read_csv("subsidies.csv")
    ]
