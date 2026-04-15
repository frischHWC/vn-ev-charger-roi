# EV Charger ROI Analysis - Vietnam Municipalities

MCP-enabled ROI analysis tool for EV charger deployment across Vietnamese districts. Designed to work with Mistral's Nuage agent via MCP connector.

## Architecture

```
User (Le Chat / Vibe CLI)
    |
    v
Nuage Agent (sandbox)
    |
    v
MCP Connector --> ev-charger-roi MCP Server
    |
    v
Data Layer (CSV) + Analysis Engine (Python)
```

## Data Model

```
data/
  districts.csv          15 districts across Hanoi, HCMC, Da Nang, Hai Phong, Can Tho
  chargers.csv           25 chargers (DC Fast 150/350kW + AC Level 2 22kW)
  monthly_usage.csv      6 months of usage data (Jan-Jun 2024) for 11 chargers
  health_impact.csv      PM2.5/NOx reduction, respiratory cases, healthcare savings
  property_impact.csv    Property value uplift, tourism revenue impact
  waste_recycling.csv    Landfill savings, recycling revenue, EV battery recycling
  subsidies.csv          15 subsidy programs with payback tracking
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `get_districts` | List all districts with demographics and EV data |
| `get_chargers` | List chargers, optionally filtered by district |
| `get_monthly_usage` | Monthly sessions, kWh, revenue per charger |
| `get_health_impact` | Air quality improvements and healthcare savings |
| `get_property_impact` | Property value uplift and tourism revenue |
| `get_waste_recycling` | Waste reduction, recycling revenue, jobs |
| `get_subsidies` | Subsidy programs and payback periods |
| `compute_roi_dashboard` | Full ROI breakdown per district |
| `compute_total_roi_summary` | Aggregate ROI across all districts |
| `run_scenario` | What-if: add N chargers to a district |
| `run_expansion_scenarios` | 5 pre-defined expansion plans for a district |
| `compare_district_scenarios` | Compare same plan across districts |
| `optimize_subsidy_allocation` | Allocate budget for maximum ROI |
| `get_top_subsidy_recommendations` | Top N districts for subsidy investment |

## ROI Components

### Direct Revenue
- Charging fees (EUR/kWh) collected from EV users
- Net profit after energy costs and maintenance

### Indirect Benefits
- **Property value uplift**: +2-5% for properties within 500m of chargers
- **Tourism boost**: Increased EV visitor spending in charger-equipped areas
- **Healthcare savings**: Reduced respiratory cases from lower PM2.5/NOx
- **Waste reduction**: Landfill cost avoidance, EV battery recycling revenue
- **Job creation**: New positions in recycling and charging operations

### Scenario Modeling
Model expansion plans with projected outcomes:
- "Add 10 DC Fast chargers to District 1 -> EUR 50,000/year charging revenue + EUR 200,000 property uplift + EUR 150,000 health savings"

### Subsidy Optimization
Multi-factor scoring: EV demand, coverage gaps, air quality urgency, tourism potential, current ROI performance. Recommends where to allocate subsidies for fastest payback.

## Usage with Nuage

### Via MCP Connector
1. Register this repo as an MCP connector in the Mistral integrations API
2. The connector auto-discovers and exposes all 14 tools to the Nuage agent
3. Ask questions like:
   - "Show me the ROI dashboard for all districts"
   - "What happens if we add 10 chargers to District 4?"
   - "Where should we allocate EUR 500,000 in subsidies?"
   - "Compare Da Nang vs HCMC for EV charger investment"

### Direct MCP (stdio)
```bash
python -m src.mcp_server
```

Reads JSON-RPC messages from stdin, writes responses to stdout. Compatible with any MCP client.

## Running Locally

```bash
# Test the analysis
python -c "
from src.analysis.roi_calculator import compute_total_roi
import json
print(json.dumps(compute_total_roi(), indent=2))
"

# Test MCP server
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python -m src.mcp_server
```

## Business Model

- **Government contracts**: Sell ROI tool to municipalities for data-driven EV infrastructure planning
- **Consulting services**: Help cities build business cases for green infrastructure grants
- **Impact reporting**: Automated ROI reports for subsidy compliance and transparency
