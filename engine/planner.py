"""
Action Planner — Constraint-Aware Multi-Step Decision Engine
"""
from __future__ import annotations
from engine.logger import AgentLogger

_SEVERITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1}


class Planner:
    def __init__(self, logger: AgentLogger):
        self.logger = logger

    def run(self, analysis: dict, constraints: dict) -> dict:
        self.logger.log(
            phase="planning",
            observation=f"{len(analysis.get('insights',[]))} insights, {len(analysis.get('contradictions',[]))} contradictions",
            reasoning="Prioritize actions by severity, then feasibility within budget.",
            decision="Generate constrained 5-step action chain",
            action="Evaluate insights against constraints and build ordered plan",
            result="Planning started",
        )
        budget = constraints.get("emergency_budget_usd", 0)
        max_loss = constraints.get("max_acceptable_loss_usd", 0)
        actions = self._generate_actions(analysis, constraints)
        plan, spent = self._apply_constraints(actions, budget)
        rationale = f"Selected {len(plan)} actions. Estimated spend: ${spent:,.0f} of ${budget:,.0f} emergency budget."
        self.logger.log(
            phase="planning",
            observation=f"Generated {len(plan)} actions within budget",
            reasoning=rationale,
            decision="Finalize action plan and pass to simulator",
            action="Package plan with metadata",
            result=f"Plan ready — {len(plan)} steps, ${spent:,.0f} allocated",
        )
        return {
            "plan": plan,
            "constraints_applied": {"emergency_budget_usd": budget, "allocated_usd": spent, "remaining_usd": budget - spent, "max_acceptable_loss_usd": max_loss},
            "rationale": rationale,
        }

    def _generate_actions(self, analysis: dict, constraints: dict) -> list[dict]:
        actions = []
        insights = sorted(analysis.get("insights", []), key=lambda i: _SEVERITY_RANK.get(i.get("severity", "low"), 0), reverse=True)
        contradictions = analysis.get("contradictions", [])
        if contradictions:
            actions.append({"step": 1, "title": "Resolve Data Integrity Issues", "description": "Conduct emergency physical audits at warehouses with mismatches. Reconcile system records.", "type": "data_validation", "urgency": "immediate", "estimated_cost_usd": 15000, "estimated_time_hours": 8, "success_probability": 0.90, "insight_refs": [c["id"] for c in contradictions]})
        critical = [i for i in insights if i.get("severity") == "critical"]
        if critical:
            actions.append({"step": 2, "title": "Notify Key Stakeholders & Activate Crisis Protocol", "description": "Alert VP Supply Chain, Regional Director, and Customer Success lead. Share severity dashboard.", "type": "communication", "urgency": "immediate", "estimated_cost_usd": 0, "estimated_time_hours": 2, "success_probability": 0.98, "insight_refs": [i["id"] for i in critical]})
        sup = next((i for i in insights if i.get("type") == "supply_chain_risk"), None)
        if sup:
            unit_cost = constraints.get("expedited_shipping_cost_per_unit_usd", 45)
            units = 400
            actions.append({"step": 3, "title": "Activate Backup Supplier & Expedited Orders", "description": f"Shift critical SKUs to MidWest Components LLC (SUP-002). Place expedited order for ~{units} units at ${unit_cost}/unit.", "type": "procurement", "urgency": "high", "estimated_cost_usd": unit_cost * units, "estimated_time_hours": 24, "success_probability": 0.82, "insight_refs": [sup["id"]]})
        cust = next((i for i in insights if i.get("type") == "customer_risk"), None)
        if cust:
            actions.append({"step": 4, "title": "Launch Proactive Customer Retention Campaign", "description": "Contact top 50 affected accounts. Offer updated timelines, 12% discount, and priority fulfillment guarantee.", "type": "customer_retention", "urgency": "high", "estimated_cost_usd": 95000, "estimated_time_hours": 48, "success_probability": 0.75, "insight_refs": [cust["id"]]})
        actions.append({"step": 5, "title": "Deploy Continuous Monitoring & Adaptive Response Loop", "description": "Set up real-time dashboards for shipment tracking, warehouse reconciliation, and ticket velocity.", "type": "monitoring", "urgency": "medium", "estimated_cost_usd": 25000, "estimated_time_hours": 72, "success_probability": 0.95, "insight_refs": ["INS-005"]})
        for idx, a in enumerate(actions, 1):
            a["step"] = idx
        return actions

    def _apply_constraints(self, actions: list[dict], budget: float) -> tuple[list[dict], float]:
        selected, spent = [], 0.0
        for a in actions:
            cost = a.get("estimated_cost_usd", 0)
            if spent + cost <= budget:
                a["status"] = "approved"
                spent += cost
            else:
                a["status"] = "deferred_over_budget"
            selected.append(a)
        return selected, spent
