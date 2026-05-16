# Autonomous Insight-to-Action AI Agent

> **Agentic Decision System** — A fully autonomous, multi-step AI agent that ingests data, extracts insights, detects contradictions, makes constrained decisions, simulates execution, and logs every reasoning step.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

The UI opens at `http://localhost:8501`. Click **"Load Sample Data"** then **"Run Full Agent Pipeline"**.

---

## 🧠 Agentic Flow

```
INPUT → INSIGHT → CONFLICT → DECISION → ACTION → SIMULATION → OUTCOME
```

| Stage | Module | What it does |
|-------|--------|-------------|
| **Ingestion** | `app.py` | Loads multi-source data (sales, complaints, suppliers, warehouses, news, financials) |
| **Analysis** | `engine/analyzer.py` | Extracts insights, detects trends, finds contradictions, computes confidence |
| **Planning** | `engine/planner.py` | Generates a 5-step action chain under budget / urgency / time constraints |
| **Simulation** | `engine/simulator.py` | Executes each action with stochastic outcomes, injects failures, applies recovery |
| **Logging** | `engine/logger.py` | Records Antigravity-style traces: observation → reasoning → decision → action → result |
| **Output** | `app.py` | Renders before/after comparison, full reasoning trace, and persists results |

---

## 📂 Project Structure

```
agentic_ai_system/
├── app.py                  # Streamlit UI
├── requirements.txt        # Dependencies
├── README.md               # This file
├── data/
│   └── inputs.json         # Sample scenario data
├── engine/
│   ├── __init__.py
│   ├── analyzer.py         # Insight extraction & contradiction detection
│   ├── planner.py          # Constraint-aware action planning
│   ├── simulator.py        # Action execution simulation
│   └── logger.py           # Antigravity-style reasoning logger
└── outputs/
    ├── logs.json            # Full reasoning trace (generated after run)
    └── results.json         # Analysis + plan + simulation results (generated after run)
```

---

## 🎯 Sample Scenario

**Q2 2026 Supply Chain Crisis — Southeast Region**

- 📉 Fulfillment rate dropped from 94.1% → 72.9%
- 📞 847 customer complaints in 30 days
- 🚢 Primary supplier (China) delayed 18 days due to port congestion
- 📦 Warehouse inventory discrepancies (330-unit gap in Atlanta)
- 📰 Shanghai port congestion worsening, US tariffs increasing June 1
- 💰 $500K emergency budget, $1.85M revenue at risk

---

## 🆚 How This Differs from Simple Automation

| Simple Automation | This Agentic System |
|---|---|
| Follows fixed rules | Reasons about conflicting data |
| Single-step execution | Multi-step chained actions |
| No failure handling | Stochastic failures with recovery |
| No reasoning trace | Full Antigravity-style logs |
| Predetermined output | Adaptive decisions under constraints |
| No state awareness | Before/after state comparison |

---

## 📊 Key Features

- **Multi-source ingestion** — sales, complaints, suppliers, warehouse, news, financials
- **Contradiction detection** — cross-references sources to find conflicts
- **Constraint-aware planning** — respects budget, urgency, and time limits
- **Stochastic simulation** — at least one failure guaranteed, with fallback logic
- **Antigravity traces** — every cognitive step is logged and explorable
- **Mobile-first UI** — responsive dark-themed Streamlit dashboard
- **Zero external APIs** — everything runs locally, no API keys needed

---

## 📜 License

Built for hackathon demonstration purposes.
