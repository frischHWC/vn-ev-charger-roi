from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class District:
    district_id: str
    district_name: str
    province: str
    population: int
    area_km2: float
    avg_property_value_eur: float
    ev_adoption_rate_pct: float
    tourism_visitors_annual: int
    air_quality_index: int
    healthcare_cost_per_capita_eur: float


@dataclass
class Charger:
    charger_id: str
    district_id: str
    location_name: str
    charger_type: str
    power_kw: int
    install_cost_eur: float
    install_date: str
    status: str
    latitude: float
    longitude: float
    daily_sessions_avg: int
    avg_session_kwh: float
    fee_per_kwh_eur: float
    monthly_maintenance_eur: float
    subsidy_received_eur: float


@dataclass
class MonthlyUsage:
    charger_id: str
    month: int
    year: int
    total_sessions: int
    total_kwh: float
    revenue_eur: float
    energy_cost_eur: float
    downtime_hours: float
    unique_users: int


@dataclass
class WasteRecycling:
    district_id: str
    year: int
    waste_tons_total: float
    waste_tons_recycled: float
    waste_tons_landfill: float
    landfill_cost_per_ton_eur: float
    recycling_revenue_per_ton_eur: float
    recycling_jobs_created: int
    ev_battery_recycling_tons: float
    ev_battery_recycling_revenue_eur: float
    co2_avoided_tons: float


@dataclass
class HealthImpact:
    district_id: str
    year: int
    pm25_reduction_pct: float
    nox_reduction_pct: float
    respiratory_cases_avoided: int
    healthcare_savings_eur: float
    premature_deaths_avoided: float
    productivity_days_gained: int
    ev_km_displaced_fossil: int
    co2_savings_tons: float


@dataclass
class PropertyImpact:
    district_id: str
    year: int
    properties_within_500m: int
    avg_value_before_eur: float
    avg_value_after_eur: float
    value_uplift_pct: float
    total_uplift_eur: float
    tourism_revenue_baseline_eur: float
    tourism_revenue_with_ev_eur: float
    tourism_uplift_eur: float


@dataclass
class Subsidy:
    subsidy_id: str
    district_id: str
    program_name: str
    amount_eur: float
    year_granted: int
    charger_ids: list[str] = field(default_factory=list)
    payback_period_years: float = 0.0
    status: str = "active"
    funding_source: str = ""


@dataclass
class ROISummary:
    district_id: str
    district_name: str
    total_investment_eur: float
    total_subsidies_eur: float
    net_investment_eur: float
    annual_charging_revenue_eur: float
    annual_energy_cost_eur: float
    annual_maintenance_cost_eur: float
    annual_net_charging_profit_eur: float
    property_value_uplift_eur: float
    tourism_uplift_eur: float
    healthcare_savings_eur: float
    waste_savings_eur: float
    recycling_revenue_eur: float
    total_annual_benefit_eur: float
    roi_pct: float
    payback_years: float


@dataclass
class ScenarioResult:
    scenario_name: str
    additional_chargers: int
    additional_investment_eur: float
    projected_annual_charging_revenue_eur: float
    projected_property_uplift_eur: float
    projected_health_savings_eur: float
    projected_waste_savings_eur: float
    projected_tourism_uplift_eur: float
    total_projected_annual_benefit_eur: float
    projected_roi_pct: float
    projected_payback_years: float


@dataclass
class SubsidyRecommendation:
    district_id: str
    district_name: str
    recommended_subsidy_eur: float
    expected_roi_pct: float
    payback_years: float
    priority_score: float
    rationale: str
