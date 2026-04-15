"""MCP server exposing EV Charger ROI analysis tools.

Run with: python -m src.mcp_server
Or use as an MCP connector endpoint.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict

from src.analysis.roi_calculator import compute_roi_by_district, compute_total_roi
from src.analysis.scenario_modeler import compare_districts, model_expansion_scenarios, model_scenario
from src.analysis.subsidy_optimizer import get_top_subsidy_recommendations, optimize_subsidies
from src.data_loader import (
    load_chargers,
    load_districts,
    load_health_impact,
    load_monthly_usage,
    load_property_impact,
    load_subsidies,
    load_waste_recycling,
)

TOOLS = [
    {
        "name": "get_districts",
        "description": "List all districts with demographic and EV adoption data. Returns district_id, name, province, population, area, property values, EV adoption rate, tourism visitors, air quality index, healthcare costs.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_chargers",
        "description": "List all EV chargers with location, type, power, costs, usage stats, and fees. Optionally filter by district_id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "district_id": {"type": "string", "description": "Filter by district ID (e.g. D001)"},
            },
            "required": [],
        },
    },
    {
        "name": "get_monthly_usage",
        "description": "Get monthly usage data for chargers: sessions, kWh, revenue, energy costs, downtime, unique users. Optionally filter by charger_id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "charger_id": {"type": "string", "description": "Filter by charger ID (e.g. CH001)"},
            },
            "required": [],
        },
    },
    {
        "name": "get_health_impact",
        "description": "Get health impact data by district: PM2.5/NOx reduction, respiratory cases avoided, healthcare savings, premature deaths avoided, CO2 savings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "district_id": {"type": "string", "description": "Filter by district ID"},
                "year": {"type": "integer", "description": "Filter by year (2023 or 2024)"},
            },
            "required": [],
        },
    },
    {
        "name": "get_property_impact",
        "description": "Get property value and tourism impact data by district: property uplift %, total uplift EUR, tourism revenue baseline vs with EV.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "district_id": {"type": "string", "description": "Filter by district ID"},
                "year": {"type": "integer", "description": "Filter by year (2023 or 2024)"},
            },
            "required": [],
        },
    },
    {
        "name": "get_waste_recycling",
        "description": "Get waste and recycling data by district: total waste, recycled tons, landfill costs, recycling revenue, EV battery recycling, jobs created, CO2 avoided.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "district_id": {"type": "string", "description": "Filter by district ID"},
                "year": {"type": "integer", "description": "Filter by year (2023 or 2024)"},
            },
            "required": [],
        },
    },
    {
        "name": "get_subsidies",
        "description": "Get subsidy data: program name, amount, year, charger IDs, payback period, funding source.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "district_id": {"type": "string", "description": "Filter by district ID"},
            },
            "required": [],
        },
    },
    {
        "name": "compute_roi_dashboard",
        "description": "Compute full ROI dashboard for all districts. Returns per-district breakdown of investment, revenue, costs, property uplift, tourism, health savings, waste savings, recycling revenue, total benefit, ROI %, and payback years.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Analysis year (default 2024)", "default": 2024},
            },
            "required": [],
        },
    },
    {
        "name": "compute_total_roi_summary",
        "description": "Compute aggregate ROI summary across all districts. Returns totals for investment, subsidies, revenue, costs, all benefit categories, overall ROI %, and payback years.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Analysis year (default 2024)", "default": 2024},
            },
            "required": [],
        },
    },
    {
        "name": "run_scenario",
        "description": "Model a what-if scenario: add N DC Fast and/or AC Level 2 chargers to a district. Returns projected revenue, property uplift, health savings, waste savings, tourism uplift, total benefit, ROI %, payback years.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "district_id": {"type": "string", "description": "Target district ID"},
                "additional_dc_fast": {"type": "integer", "description": "Number of DC Fast chargers to add", "default": 0},
                "additional_ac_level2": {"type": "integer", "description": "Number of AC Level 2 chargers to add", "default": 0},
                "scenario_name": {"type": "string", "description": "Name for this scenario", "default": "Custom Scenario"},
            },
            "required": ["district_id"],
        },
    },
    {
        "name": "run_expansion_scenarios",
        "description": "Run 5 pre-defined expansion scenarios for a district (Conservative, Moderate, Aggressive, DC Fast Focus, AC Network). Compare projected outcomes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "district_id": {"type": "string", "description": "Target district ID"},
            },
            "required": ["district_id"],
        },
    },
    {
        "name": "compare_district_scenarios",
        "description": "Compare the same expansion plan across multiple districts to find the best location for investment.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "district_ids": {"type": "array", "items": {"type": "string"}, "description": "List of district IDs to compare"},
                "additional_dc_fast": {"type": "integer", "description": "DC Fast chargers per district", "default": 5},
                "additional_ac_level2": {"type": "integer", "description": "AC Level 2 chargers per district", "default": 5},
            },
            "required": ["district_ids"],
        },
    },
    {
        "name": "optimize_subsidy_allocation",
        "description": "Optimize subsidy allocation across districts for maximum ROI. Considers EV demand, charger coverage gaps, air quality, tourism potential, and current ROI performance.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "budget_eur": {"type": "number", "description": "Total subsidy budget in EUR", "default": 500000},
                "year": {"type": "integer", "description": "Analysis year", "default": 2024},
            },
            "required": [],
        },
    },
    {
        "name": "get_top_subsidy_recommendations",
        "description": "Get top N subsidy recommendations ranked by priority score with rationale.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "n": {"type": "integer", "description": "Number of recommendations", "default": 5},
                "budget_eur": {"type": "number", "description": "Total subsidy budget in EUR", "default": 500000},
            },
            "required": [],
        },
    },
]


def handle_tool_call(name: str, arguments: dict) -> str:
    if name == "get_districts":
        data = [asdict(d) for d in load_districts()]
    elif name == "get_chargers":
        chargers = load_chargers()
        did = arguments.get("district_id")
        if did:
            chargers = [c for c in chargers if c.district_id == did]
        data = [asdict(c) for c in chargers]
    elif name == "get_monthly_usage":
        usage = load_monthly_usage()
        cid = arguments.get("charger_id")
        if cid:
            usage = [u for u in usage if u.charger_id == cid]
        data = [asdict(u) for u in usage]
    elif name == "get_health_impact":
        health = load_health_impact()
        did = arguments.get("district_id")
        yr = arguments.get("year")
        if did:
            health = [h for h in health if h.district_id == did]
        if yr:
            health = [h for h in health if h.year == yr]
        data = [asdict(h) for h in health]
    elif name == "get_property_impact":
        props = load_property_impact()
        did = arguments.get("district_id")
        yr = arguments.get("year")
        if did:
            props = [p for p in props if p.district_id == did]
        if yr:
            props = [p for p in props if p.year == yr]
        data = [asdict(p) for p in props]
    elif name == "get_waste_recycling":
        waste = load_waste_recycling()
        did = arguments.get("district_id")
        yr = arguments.get("year")
        if did:
            waste = [w for w in waste if w.district_id == did]
        if yr:
            waste = [w for w in waste if w.year == yr]
        data = [asdict(w) for w in waste]
    elif name == "get_subsidies":
        subs = load_subsidies()
        did = arguments.get("district_id")
        if did:
            subs = [s for s in subs if s.district_id == did]
        data = [asdict(s) for s in subs]
    elif name == "compute_roi_dashboard":
        yr = arguments.get("year", 2024)
        data = [asdict(r) for r in compute_roi_by_district(yr)]
    elif name == "compute_total_roi_summary":
        yr = arguments.get("year", 2024)
        data = compute_total_roi(yr)
    elif name == "run_scenario":
        data = asdict(
            model_scenario(
                district_id=arguments["district_id"],
                additional_dc_fast=arguments.get("additional_dc_fast", 0),
                additional_ac_level2=arguments.get("additional_ac_level2", 0),
                scenario_name=arguments.get("scenario_name", "Custom Scenario"),
            )
        )
    elif name == "run_expansion_scenarios":
        data = [asdict(s) for s in model_expansion_scenarios(arguments["district_id"])]
    elif name == "compare_district_scenarios":
        data = [
            asdict(s)
            for s in compare_districts(
                arguments["district_ids"],
                arguments.get("additional_dc_fast", 5),
                arguments.get("additional_ac_level2", 5),
            )
        ]
    elif name == "optimize_subsidy_allocation":
        data = [
            asdict(r)
            for r in optimize_subsidies(
                arguments.get("budget_eur", 500000),
                arguments.get("year", 2024),
            )
        ]
    elif name == "get_top_subsidy_recommendations":
        data = [
            asdict(r)
            for r in get_top_subsidy_recommendations(
                arguments.get("n", 5),
                arguments.get("budget_eur", 500000),
            )
        ]
    else:
        return json.dumps({"error": f"Unknown tool: {name}"})

    return json.dumps(data, default=str)


def handle_message(message: dict) -> dict | None:
    method = message.get("method")
    msg_id = message.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {
                    "name": "ev-charger-roi",
                    "version": "1.0.0",
                },
            },
        }

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS},
        }

    if method == "tools/call":
        params = message.get("params", {})
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        result_text = handle_tool_call(tool_name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [{"type": "text", "text": result_text}],
                "isError": False,
            },
        }

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue

        response = handle_message(message)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
