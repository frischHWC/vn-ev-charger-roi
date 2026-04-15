from __future__ import annotations

from src.data_loader import load_districts
from src.models.data_models import ScenarioResult

AVG_DC_FAST_COST = 50000
AVG_AC_LEVEL2_COST = 8500
AVG_DC_FAST_DAILY_SESSIONS = 20
AVG_AC_LEVEL2_DAILY_SESSIONS = 12
AVG_DC_FAST_KWH_SESSION = 38.0
AVG_AC_LEVEL2_KWH_SESSION = 16.0
AVG_FEE_PER_KWH = 0.28
AVG_ENERGY_COST_PER_KWH = 0.14
AVG_DC_MAINTENANCE_MONTHLY = 400
AVG_AC_MAINTENANCE_MONTHLY = 110

PROPERTY_UPLIFT_PER_CHARGER = 20000
HEALTH_SAVINGS_PER_CHARGER = 15000
WASTE_SAVINGS_PER_CHARGER = 3500
TOURISM_UPLIFT_PER_CHARGER = 12000


def model_scenario(
    district_id: str,
    additional_dc_fast: int = 0,
    additional_ac_level2: int = 0,
    scenario_name: str = "Custom Scenario",
) -> ScenarioResult:
    districts = {d.district_id: d for d in load_districts()}
    district = districts.get(district_id)
    if not district:
        raise ValueError(f"District {district_id} not found")

    total_additional = additional_dc_fast + additional_ac_level2
    additional_investment = (
        additional_dc_fast * AVG_DC_FAST_COST + additional_ac_level2 * AVG_AC_LEVEL2_COST
    )

    dc_annual_revenue = (
        additional_dc_fast
        * AVG_DC_FAST_DAILY_SESSIONS
        * AVG_DC_FAST_KWH_SESSION
        * AVG_FEE_PER_KWH
        * 365
    )
    ac_annual_revenue = (
        additional_ac_level2
        * AVG_AC_LEVEL2_DAILY_SESSIONS
        * AVG_AC_LEVEL2_KWH_SESSION
        * AVG_FEE_PER_KWH
        * 365
    )
    total_revenue = dc_annual_revenue + ac_annual_revenue

    dc_energy_cost = (
        additional_dc_fast
        * AVG_DC_FAST_DAILY_SESSIONS
        * AVG_DC_FAST_KWH_SESSION
        * AVG_ENERGY_COST_PER_KWH
        * 365
    )
    ac_energy_cost = (
        additional_ac_level2
        * AVG_AC_LEVEL2_DAILY_SESSIONS
        * AVG_AC_LEVEL2_KWH_SESSION
        * AVG_ENERGY_COST_PER_KWH
        * 365
    )
    total_energy_cost = dc_energy_cost + ac_energy_cost

    total_maintenance = (
        additional_dc_fast * AVG_DC_MAINTENANCE_MONTHLY * 12
        + additional_ac_level2 * AVG_AC_MAINTENANCE_MONTHLY * 12
    )

    net_charging_revenue = total_revenue - total_energy_cost - total_maintenance

    ev_factor = district.ev_adoption_rate_pct / 5.0
    property_uplift = total_additional * PROPERTY_UPLIFT_PER_CHARGER * ev_factor
    health_savings = total_additional * HEALTH_SAVINGS_PER_CHARGER * (district.air_quality_index / 80.0)
    waste_savings = total_additional * WASTE_SAVINGS_PER_CHARGER
    tourism_uplift = total_additional * TOURISM_UPLIFT_PER_CHARGER * (district.tourism_visitors_annual / 1000000)

    total_benefit = net_charging_revenue + property_uplift + health_savings + waste_savings + tourism_uplift

    roi_pct = (total_benefit / additional_investment * 100) if additional_investment > 0 else 0.0
    payback_years = (additional_investment / total_benefit) if total_benefit > 0 else float("inf")

    return ScenarioResult(
        scenario_name=scenario_name,
        additional_chargers=total_additional,
        additional_investment_eur=round(additional_investment, 2),
        projected_annual_charging_revenue_eur=round(net_charging_revenue, 2),
        projected_property_uplift_eur=round(property_uplift, 2),
        projected_health_savings_eur=round(health_savings, 2),
        projected_waste_savings_eur=round(waste_savings, 2),
        projected_tourism_uplift_eur=round(tourism_uplift, 2),
        total_projected_annual_benefit_eur=round(total_benefit, 2),
        projected_roi_pct=round(roi_pct, 1),
        projected_payback_years=round(payback_years, 2),
    )


def model_expansion_scenarios(district_id: str) -> list[ScenarioResult]:
    scenarios = [
        ("Conservative: +2 AC chargers", 0, 2),
        ("Moderate: +5 DC Fast + 5 AC", 5, 5),
        ("Aggressive: +10 DC Fast + 10 AC", 10, 10),
        ("DC Fast Focus: +10 DC Fast", 10, 0),
        ("AC Network: +20 AC Level 2", 0, 20),
    ]
    return [
        model_scenario(district_id, dc, ac, name)
        for name, dc, ac in scenarios
    ]


def compare_districts(
    district_ids: list[str],
    additional_dc_fast: int = 5,
    additional_ac_level2: int = 5,
) -> list[ScenarioResult]:
    results = []
    districts = {d.district_id: d for d in load_districts()}
    for did in district_ids:
        d = districts.get(did)
        name = f"{d.district_name} ({d.province})" if d else did
        results.append(
            model_scenario(did, additional_dc_fast, additional_ac_level2, scenario_name=name)
        )
    results.sort(key=lambda r: r.projected_roi_pct, reverse=True)
    return results
