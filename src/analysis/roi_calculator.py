from __future__ import annotations

from collections import defaultdict

from src.data_loader import (
    load_chargers,
    load_districts,
    load_health_impact,
    load_monthly_usage,
    load_property_impact,
    load_subsidies,
    load_waste_recycling,
)
from src.models.data_models import ROISummary


def compute_roi_by_district(year: int = 2024) -> list[ROISummary]:
    districts = {d.district_id: d for d in load_districts()}
    chargers = load_chargers()
    usage = load_monthly_usage()
    health = load_health_impact()
    properties = load_property_impact()
    waste = load_waste_recycling()
    subsidies = load_subsidies()

    chargers_by_district: dict[str, list] = defaultdict(list)
    for c in chargers:
        chargers_by_district[c.district_id].append(c)

    usage_by_charger: dict[str, list] = defaultdict(list)
    for u in usage:
        if u.year == year:
            usage_by_charger[u.charger_id].append(u)

    health_by_district = {h.district_id: h for h in health if h.year == year}
    property_by_district = {p.district_id: p for p in properties if p.year == year}
    waste_by_district = {w.district_id: w for w in waste if w.year == year}

    subsidy_by_district: dict[str, float] = defaultdict(float)
    for s in subsidies:
        subsidy_by_district[s.district_id] += s.amount_eur

    results = []
    for district_id, district in districts.items():
        district_chargers = chargers_by_district.get(district_id, [])
        if not district_chargers:
            continue

        total_investment = sum(c.install_cost_eur for c in district_chargers)
        total_subsidy = subsidy_by_district.get(district_id, 0.0)
        net_investment = total_investment - total_subsidy

        annual_revenue = 0.0
        annual_energy_cost = 0.0
        for c in district_chargers:
            charger_usage = usage_by_charger.get(c.charger_id, [])
            if charger_usage:
                months_with_data = len(charger_usage)
                rev = sum(u.revenue_eur for u in charger_usage)
                cost = sum(u.energy_cost_eur for u in charger_usage)
                annual_revenue += rev * (12 / months_with_data)
                annual_energy_cost += cost * (12 / months_with_data)
            else:
                annual_revenue += c.daily_sessions_avg * c.avg_session_kwh * c.fee_per_kwh_eur * 365
                annual_energy_cost += c.daily_sessions_avg * c.avg_session_kwh * 0.14 * 365

        annual_maintenance = sum(c.monthly_maintenance_eur * 12 for c in district_chargers)
        net_charging_profit = annual_revenue - annual_energy_cost - annual_maintenance

        h = health_by_district.get(district_id)
        healthcare_savings = h.healthcare_savings_eur if h else 0.0

        p = property_by_district.get(district_id)
        property_uplift = p.total_uplift_eur if p else 0.0
        tourism_uplift = p.tourism_uplift_eur if p else 0.0

        w = waste_by_district.get(district_id)
        waste_savings = 0.0
        recycling_revenue = 0.0
        if w:
            waste_savings = w.ev_battery_recycling_tons * w.landfill_cost_per_ton_eur
            recycling_revenue = w.ev_battery_recycling_revenue_eur

        total_annual_benefit = (
            net_charging_profit
            + property_uplift
            + tourism_uplift
            + healthcare_savings
            + waste_savings
            + recycling_revenue
        )

        roi_pct = (total_annual_benefit / net_investment * 100) if net_investment > 0 else 0.0
        payback_years = (net_investment / total_annual_benefit) if total_annual_benefit > 0 else float("inf")

        results.append(
            ROISummary(
                district_id=district_id,
                district_name=district.district_name,
                total_investment_eur=total_investment,
                total_subsidies_eur=total_subsidy,
                net_investment_eur=net_investment,
                annual_charging_revenue_eur=round(annual_revenue, 2),
                annual_energy_cost_eur=round(annual_energy_cost, 2),
                annual_maintenance_cost_eur=annual_maintenance,
                annual_net_charging_profit_eur=round(net_charging_profit, 2),
                property_value_uplift_eur=property_uplift,
                tourism_uplift_eur=tourism_uplift,
                healthcare_savings_eur=healthcare_savings,
                waste_savings_eur=round(waste_savings, 2),
                recycling_revenue_eur=recycling_revenue,
                total_annual_benefit_eur=round(total_annual_benefit, 2),
                roi_pct=round(roi_pct, 1),
                payback_years=round(payback_years, 2),
            )
        )

    results.sort(key=lambda r: r.roi_pct, reverse=True)
    return results


def compute_total_roi(year: int = 2024) -> dict:
    summaries = compute_roi_by_district(year)
    total_investment = sum(s.total_investment_eur for s in summaries)
    total_subsidies = sum(s.total_subsidies_eur for s in summaries)
    total_net_investment = sum(s.net_investment_eur for s in summaries)
    total_revenue = sum(s.annual_charging_revenue_eur for s in summaries)
    total_energy_cost = sum(s.annual_energy_cost_eur for s in summaries)
    total_maintenance = sum(s.annual_maintenance_cost_eur for s in summaries)
    total_net_profit = sum(s.annual_net_charging_profit_eur for s in summaries)
    total_property = sum(s.property_value_uplift_eur for s in summaries)
    total_tourism = sum(s.tourism_uplift_eur for s in summaries)
    total_health = sum(s.healthcare_savings_eur for s in summaries)
    total_waste = sum(s.waste_savings_eur for s in summaries)
    total_recycling = sum(s.recycling_revenue_eur for s in summaries)
    total_benefit = sum(s.total_annual_benefit_eur for s in summaries)

    return {
        "year": year,
        "num_districts": len(summaries),
        "total_chargers": sum(1 for _ in load_chargers()),
        "total_investment_eur": round(total_investment, 2),
        "total_subsidies_eur": round(total_subsidies, 2),
        "total_net_investment_eur": round(total_net_investment, 2),
        "annual_charging_revenue_eur": round(total_revenue, 2),
        "annual_energy_cost_eur": round(total_energy_cost, 2),
        "annual_maintenance_cost_eur": round(total_maintenance, 2),
        "annual_net_charging_profit_eur": round(total_net_profit, 2),
        "property_value_uplift_eur": round(total_property, 2),
        "tourism_uplift_eur": round(total_tourism, 2),
        "healthcare_savings_eur": round(total_health, 2),
        "waste_savings_eur": round(total_waste, 2),
        "recycling_revenue_eur": round(total_recycling, 2),
        "total_annual_benefit_eur": round(total_benefit, 2),
        "overall_roi_pct": round(total_benefit / total_net_investment * 100, 1) if total_net_investment > 0 else 0,
        "overall_payback_years": round(total_net_investment / total_benefit, 2) if total_benefit > 0 else float("inf"),
    }
