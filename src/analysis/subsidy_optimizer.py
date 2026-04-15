from __future__ import annotations

from src.analysis.roi_calculator import compute_roi_by_district
from src.data_loader import load_chargers, load_districts
from src.models.data_models import SubsidyRecommendation

SUBSIDY_BUDGET_DEFAULT = 500000


def optimize_subsidies(
    budget_eur: float = SUBSIDY_BUDGET_DEFAULT,
    year: int = 2024,
) -> list[SubsidyRecommendation]:
    districts = {d.district_id: d for d in load_districts()}
    roi_summaries = compute_roi_by_district(year)
    chargers = load_chargers()

    charger_count = {}
    for c in chargers:
        charger_count[c.district_id] = charger_count.get(c.district_id, 0) + 1

    scored = []
    for roi in roi_summaries:
        d = districts[roi.district_id]
        n_chargers = charger_count.get(roi.district_id, 0)

        ev_demand_score = d.ev_adoption_rate_pct / 7.2 * 100
        coverage_gap = d.population / max(n_chargers, 1) / 50000 * 100
        coverage_gap = min(coverage_gap, 100)
        health_urgency = d.air_quality_index / 88 * 100
        tourism_potential = min(d.tourism_visitors_annual / 3200000 * 100, 100)
        current_roi_score = min(roi.roi_pct / 500 * 100, 100)

        priority_score = (
            ev_demand_score * 0.25
            + coverage_gap * 0.20
            + health_urgency * 0.20
            + tourism_potential * 0.15
            + current_roi_score * 0.20
        )

        recommended_subsidy = budget_eur * (priority_score / 100) * 0.15
        recommended_subsidy = min(recommended_subsidy, budget_eur * 0.25)
        recommended_subsidy = max(recommended_subsidy, 5000)

        expected_additional_chargers = recommended_subsidy / 30000
        expected_additional_revenue = expected_additional_chargers * 50000
        expected_roi = (expected_additional_revenue / recommended_subsidy * 100) if recommended_subsidy > 0 else 0
        payback = recommended_subsidy / expected_additional_revenue if expected_additional_revenue > 0 else float("inf")

        rationale_parts = []
        if ev_demand_score > 70:
            rationale_parts.append(f"High EV adoption ({d.ev_adoption_rate_pct}%)")
        if coverage_gap > 60:
            rationale_parts.append(f"Low charger coverage ({n_chargers} chargers for {d.population:,} people)")
        if health_urgency > 80:
            rationale_parts.append(f"Poor air quality (AQI {d.air_quality_index})")
        if tourism_potential > 50:
            rationale_parts.append(f"High tourism ({d.tourism_visitors_annual:,} visitors/year)")
        if current_roi_score > 60:
            rationale_parts.append("Strong existing ROI performance")
        if not rationale_parts:
            rationale_parts.append("Moderate potential across all factors")

        scored.append(
            SubsidyRecommendation(
                district_id=roi.district_id,
                district_name=roi.district_name,
                recommended_subsidy_eur=round(recommended_subsidy, 2),
                expected_roi_pct=round(expected_roi, 1),
                payback_years=round(payback, 1),
                priority_score=round(priority_score, 1),
                rationale="; ".join(rationale_parts),
            )
        )

    scored.sort(key=lambda r: r.priority_score, reverse=True)

    remaining_budget = budget_eur
    allocated = []
    for rec in scored:
        if remaining_budget <= 0:
            break
        alloc = min(rec.recommended_subsidy_eur, remaining_budget)
        allocated.append(
            SubsidyRecommendation(
                district_id=rec.district_id,
                district_name=rec.district_name,
                recommended_subsidy_eur=round(alloc, 2),
                expected_roi_pct=rec.expected_roi_pct,
                payback_years=rec.payback_years,
                priority_score=rec.priority_score,
                rationale=rec.rationale,
            )
        )
        remaining_budget -= alloc

    return allocated


def get_top_subsidy_recommendations(
    n: int = 5,
    budget_eur: float = SUBSIDY_BUDGET_DEFAULT,
    year: int = 2024,
) -> list[SubsidyRecommendation]:
    return optimize_subsidies(budget_eur, year)[:n]
