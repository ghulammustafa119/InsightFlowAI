"""
Action Simulator — Executes plan steps with stochastic outcomes.

Simulates each action: updates system state, injects at least one random failure,
and applies retry / fallback logic. Produces before-vs-after snapshots.
"""
from __future__ import annotations
import copy, random
from engine.logger import AgentLogger

random.seed(42)  # reproducible demo; remove for real runs


class Simulator:
    def __init__(self, logger: AgentLogger):
        self.logger = logger

    def run(self, plan: list[dict], initial_state: dict) -> dict:
        before = self._build_state(initial_state)
        state = copy.deepcopy(before)
        results = []
        forced_fail = random.randint(0, max(len(plan) - 1, 0))

        for idx, action in enumerate(plan):
            if action.get("status") == "deferred_over_budget":
                entry = self._skip_action(action)
                results.append(entry)
                continue
            force = idx == forced_fail
            entry = self._execute(action, state, force_failure=force)
            results.append(entry)

        after = copy.deepcopy(state)
        self.logger.log(
            phase="simulation",
            observation=f"Executed {len(results)} actions",
            reasoning="Comparing pre- and post-simulation state to quantify impact.",
            decision="Package before/after with per-action results",
            action="Compile simulation output",
            result="Simulation complete",
        )
        return {"before": before, "after": after, "action_results": results}

    # ── state builder ────────────────────────────────────────────────
    def _build_state(self, data: dict) -> dict:
        src = data.get("data_sources", {})
        sales = src.get("sales_data", {}).get("metrics", {})
        compl = src.get("customer_complaints", {})
        wh = src.get("warehouse_data", {}).get("warehouses", [])
        return {
            "fulfillment_rate_pct": sales.get("fulfillment_rate_pct", 0),
            "pending_orders": sales.get("pending_orders", 0),
            "revenue_at_risk_usd": sales.get("revenue_at_risk_usd", 0),
            "customer_sentiment": compl.get("sentiment_score", 0),
            "escalation_rate_pct": compl.get("escalation_rate_pct", 0),
            "open_tickets": compl.get("total_tickets", 0),
            "inventory_discrepancies": sum(1 for w in wh if "No discrepancy" not in w.get("discrepancy", "No")),
            "supplier_delays_active": sum(1 for s in src.get("supplier_status", {}).get("suppliers", []) if s.get("status") in ("delayed", "partial")),
            "budget_remaining_usd": src.get("financial_constraints", {}).get("emergency_budget_usd", 0),
            "crisis_protocol_active": False,
            "monitoring_active": False,
        }

    # ── execute single action ────────────────────────────────────────
    def _execute(self, action: dict, state: dict, force_failure: bool = False) -> dict:
        title = action["title"]
        step = action["step"]

        fail = force_failure or random.random() > action.get("success_probability", 0.8)

        if fail:
            failure_msg = f"Step {step} '{title}' encountered a failure during execution."
            recovery_msg = self._recover(action, state)
            self.logger.log(
                phase="simulation",
                observation=f"Executing step {step}: {title}",
                reasoning=f"Success probability {action.get('success_probability',0):.0%}. Failure triggered.",
                decision="Attempt recovery / fallback",
                action=title,
                result="Failed — recovery applied",
                failure=failure_msg,
                recovery=recovery_msg,
            )
            self._apply_partial(action, state)
            return {"step": step, "title": title, "status": "recovered", "failure": failure_msg, "recovery": recovery_msg}

        self._apply_full(action, state)
        self.logger.log(
            phase="simulation",
            observation=f"Executing step {step}: {title}",
            reasoning=f"Success probability {action.get('success_probability',0):.0%}. Passed.",
            decision="Apply full state update",
            action=title,
            result="Success",
        )
        return {"step": step, "title": title, "status": "success", "failure": None, "recovery": None}

    def _skip_action(self, action: dict) -> dict:
        self.logger.log(
            phase="simulation",
            observation=f"Step {action['step']}: {action['title']} — deferred (over budget)",
            reasoning="Budget exhausted; deferring non-critical action.",
            decision="Skip execution",
            action=action["title"],
            result="Deferred",
        )
        return {"step": action["step"], "title": action["title"], "status": "deferred", "failure": None, "recovery": None}

    # ── state mutations ──────────────────────────────────────────────
    def _apply_full(self, action: dict, state: dict):
        t = action.get("type", "")
        cost = action.get("estimated_cost_usd", 0)
        state["budget_remaining_usd"] = max(state["budget_remaining_usd"] - cost, 0)
        if t == "data_validation":
            state["inventory_discrepancies"] = 0
        elif t == "communication":
            state["crisis_protocol_active"] = True
        elif t == "procurement":
            state["supplier_delays_active"] = max(state["supplier_delays_active"] - 1, 0)
            state["fulfillment_rate_pct"] = min(state["fulfillment_rate_pct"] + 12, 100)
            state["pending_orders"] = max(state["pending_orders"] - 800, 0)
            state["revenue_at_risk_usd"] = max(state["revenue_at_risk_usd"] - 650000, 0)
        elif t == "customer_retention":
            state["customer_sentiment"] = min(state["customer_sentiment"] + 0.45, 0.0)
            state["escalation_rate_pct"] = max(state["escalation_rate_pct"] - 10, 0)
            state["open_tickets"] = max(state["open_tickets"] - 300, 0)
        elif t == "monitoring":
            state["monitoring_active"] = True

    def _apply_partial(self, action: dict, state: dict):
        t = action.get("type", "")
        cost = action.get("estimated_cost_usd", 0)
        state["budget_remaining_usd"] = max(state["budget_remaining_usd"] - cost * 0.5, 0)
        if t == "data_validation":
            state["inventory_discrepancies"] = max(state["inventory_discrepancies"] - 1, 0)
        elif t == "communication":
            state["crisis_protocol_active"] = True
        elif t == "procurement":
            state["fulfillment_rate_pct"] = min(state["fulfillment_rate_pct"] + 5, 100)
            state["pending_orders"] = max(state["pending_orders"] - 300, 0)
            state["revenue_at_risk_usd"] = max(state["revenue_at_risk_usd"] - 250000, 0)
        elif t == "customer_retention":
            state["customer_sentiment"] = min(state["customer_sentiment"] + 0.2, 0.0)
            state["escalation_rate_pct"] = max(state["escalation_rate_pct"] - 4, 0)
            state["open_tickets"] = max(state["open_tickets"] - 100, 0)
        elif t == "monitoring":
            state["monitoring_active"] = True

    def _recover(self, action: dict, state: dict) -> str:
        t = action.get("type", "")
        if t == "procurement":
            return "Fallback: Split order across SUP-002 and SUP-003 with partial expedite. Reduced quantity to 250 units."
        if t == "data_validation":
            return "Fallback: Automated reconciliation script applied. Manual audit scheduled for remaining gaps."
        if t == "customer_retention":
            return "Fallback: Escalated to VP Customer Success. Extended discount to 15% for top 20 accounts."
        if t == "monitoring":
            return "Fallback: Manual monitoring sheet deployed while dashboard infra is rebuilt."
        return "Fallback: Notified team lead for manual intervention."
