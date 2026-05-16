"""
Data Analyzer — Insight Extraction & Contradiction Detection

Ingests the multi-source input payload and produces:
  • Key insights with confidence scores
  • Detected trends
  • Contradictions / conflicts between data sources
"""

from __future__ import annotations

import statistics
from engine.logger import AgentLogger


# ── helpers ───────────────────────────────────────────────────────────
def _pct_change(old: float, new: float) -> float:
    if old == 0:
        return 0.0
    return round((new - old) / old * 100, 2)


# ── main analysis class ──────────────────────────────────────────────
class Analyzer:
    """Stateless analyzer — takes raw data, returns structured insights."""

    def __init__(self, logger: AgentLogger):
        self.logger = logger

    # ------------------------------------------------------------------
    def run(self, data: dict) -> dict:
        """
        Execute the full analysis pipeline.

        Returns
        -------
        dict with keys: insights, trends, contradictions, confidence
        """
        sources = data.get("data_sources", {})

        self.logger.log(
            phase="analysis",
            observation=f"Received {len(sources)} data sources for scenario: {data.get('scenario', 'N/A')}",
            reasoning="Need to process each source independently, then cross-reference for contradictions.",
            decision="Begin multi-source analysis pipeline",
            action="Invoke insight extraction, trend detection, and contradiction scan",
            result="Analysis pipeline initiated",
        )

        insights = self._extract_insights(sources)
        trends = self._detect_trends(sources)
        contradictions = self._detect_contradictions(sources)
        confidence = self._compute_confidence(insights, contradictions)

        self.logger.log(
            phase="analysis",
            observation=f"Extracted {len(insights)} insights, {len(trends)} trends, {len(contradictions)} contradictions",
            reasoning="Cross-referencing complete. Confidence is reduced by contradictions and boosted by corroborated signals.",
            decision="Package analysis results for planner",
            action="Return structured analysis payload",
            result=f"Overall confidence score: {confidence:.0%}",
            metadata={"insight_count": len(insights), "contradiction_count": len(contradictions)},
        )

        return {
            "insights": insights,
            "trends": trends,
            "contradictions": contradictions,
            "confidence": confidence,
        }

    # ------------------------------------------------------------------
    # Insight extraction
    # ------------------------------------------------------------------
    def _extract_insights(self, sources: dict) -> list[dict]:
        insights: list[dict] = []

        # --- Sales ---
        sales = sources.get("sales_data", {}).get("metrics", {})
        if sales:
            fulfillment = sales.get("fulfillment_rate_pct", 0)
            prev_fulfillment = sales.get("prev_quarter_fulfillment_rate_pct", 0)
            drop = round(prev_fulfillment - fulfillment, 1)
            insights.append({
                "id": "INS-001",
                "source": "sales_data",
                "type": "performance_degradation",
                "title": "Fulfillment Rate Collapse",
                "detail": (
                    f"Order fulfillment dropped from {prev_fulfillment}% to {fulfillment}% "
                    f"(−{drop} pp). {sales.get('pending_orders', 0)} orders pending, "
                    f"${sales.get('revenue_at_risk_usd', 0):,.0f} revenue at risk."
                ),
                "severity": "critical",
                "confidence": 0.95,
            })

        # --- Complaints ---
        complaints = sources.get("customer_complaints", {})
        if complaints:
            top_cat = max(
                complaints.get("categories", {}).items(),
                key=lambda x: x[1]["count"],
                default=("unknown", {"count": 0}),
            )
            insights.append({
                "id": "INS-002",
                "source": "customer_complaints",
                "type": "customer_risk",
                "title": "Customer Satisfaction Crisis",
                "detail": (
                    f"{complaints.get('total_tickets', 0)} tickets in 30 days. "
                    f"Top category: '{top_cat[0]}' ({top_cat[1]['count']} tickets). "
                    f"Sentiment score: {complaints.get('sentiment_score', 0):.2f}. "
                    f"Escalation rate: {complaints.get('escalation_rate_pct', 0)}%."
                ),
                "severity": "critical",
                "confidence": 0.92,
            })

        # --- Suppliers ---
        suppliers = sources.get("supplier_status", {}).get("suppliers", [])
        delayed = [s for s in suppliers if s.get("status") in ("delayed", "partial")]
        if delayed:
            names = ", ".join(s["name"] for s in delayed)
            avg_delay = statistics.mean(s.get("delay_days", 0) for s in delayed)
            insights.append({
                "id": "INS-003",
                "source": "supplier_status",
                "type": "supply_chain_risk",
                "title": "Supplier Reliability Failure",
                "detail": (
                    f"{len(delayed)}/{len(suppliers)} suppliers underperforming: {names}. "
                    f"Average delay: {avg_delay:.0f} days. "
                    f"Lowest reliability score: {min(s.get('reliability_score', 1) for s in delayed):.2f}."
                ),
                "severity": "high",
                "confidence": 0.90,
            })

        # --- Warehouse ---
        warehouses = sources.get("warehouse_data", {}).get("warehouses", [])
        discrepancies = [w for w in warehouses if "No discrepancy" not in w.get("discrepancy", "No discrepancy")]
        if discrepancies:
            details = "; ".join(
                f"{w['id']} ({w['location']}): {w['discrepancy']}" for w in discrepancies
            )
            insights.append({
                "id": "INS-004",
                "source": "warehouse_data",
                "type": "data_integrity",
                "title": "Warehouse Inventory Discrepancies",
                "detail": details,
                "severity": "high",
                "confidence": 0.85,
            })

        # --- News ---
        news = sources.get("news_signals", {}).get("signals", [])
        high_impact = [n for n in news if n.get("impact") == "high"]
        if high_impact:
            insights.append({
                "id": "INS-005",
                "source": "news_signals",
                "type": "external_risk",
                "title": "High-Impact External Events",
                "detail": " | ".join(
                    f"{n['headline']} ({n['date']})" for n in high_impact
                ),
                "severity": "high",
                "confidence": 0.80,
            })

        # --- Financial exposure ---
        fin = sources.get("financial_constraints", {})
        if fin:
            risk = sources.get("sales_data", {}).get("metrics", {}).get("revenue_at_risk_usd", 0)
            budget = fin.get("emergency_budget_usd", 0)
            gap = risk - budget
            if gap > 0:
                insights.append({
                    "id": "INS-006",
                    "source": "financial_constraints",
                    "type": "financial_risk",
                    "title": "Budget-to-Risk Gap",
                    "detail": (
                        f"Revenue at risk (${risk:,.0f}) exceeds emergency budget "
                        f"(${budget:,.0f}) by ${gap:,.0f}. Max acceptable loss: "
                        f"${fin.get('max_acceptable_loss_usd', 0):,.0f}."
                    ),
                    "severity": "critical",
                    "confidence": 0.93,
                })

        return insights

    # ------------------------------------------------------------------
    # Trend detection
    # ------------------------------------------------------------------
    def _detect_trends(self, sources: dict) -> list[dict]:
        trends: list[dict] = []

        sales = sources.get("sales_data", {}).get("metrics", {})
        if sales:
            trends.append({
                "id": "TRD-001",
                "title": "Fulfillment Declining Quarter-over-Quarter",
                "direction": "down",
                "magnitude": _pct_change(
                    sales.get("prev_quarter_fulfillment_rate_pct", 100),
                    sales.get("fulfillment_rate_pct", 100),
                ),
                "unit": "percentage_points",
            })

        complaints = sources.get("customer_complaints", {})
        if complaints.get("escalation_rate_pct", 0) > 15:
            trends.append({
                "id": "TRD-002",
                "title": "Escalation Rate Trending Above Threshold",
                "direction": "up",
                "magnitude": complaints["escalation_rate_pct"],
                "unit": "percent",
            })

        news = sources.get("news_signals", {}).get("signals", [])
        tariff_signals = [n for n in news if "tariff" in n.get("headline", "").lower()]
        if tariff_signals:
            trends.append({
                "id": "TRD-003",
                "title": "Regulatory Cost Pressure Increasing",
                "direction": "up",
                "magnitude": 10,
                "unit": "percent_cost_increase",
            })

        return trends

    # ------------------------------------------------------------------
    # Contradiction detection
    # ------------------------------------------------------------------
    def _detect_contradictions(self, sources: dict) -> list[dict]:
        contradictions: list[dict] = []

        # Warehouse data vs itself
        warehouses = sources.get("warehouse_data", {}).get("warehouses", [])
        for wh in warehouses:
            disc = wh.get("discrepancy", "")
            if "No discrepancy" not in disc and disc:
                contradictions.append({
                    "id": f"CON-WH-{wh['id']}",
                    "type": "data_mismatch",
                    "sources": ["warehouse_data.system", "warehouse_data.physical_audit"],
                    "title": f"Inventory Mismatch at {wh['id']}",
                    "detail": disc,
                    "severity": "high",
                })

        # Supplier says delayed but sales data doesn't flag it
        suppliers = sources.get("supplier_status", {}).get("suppliers", [])
        active_but_delayed = [
            s for s in suppliers
            if s.get("status") == "delayed" and s.get("reliability_score", 1) < 0.5
        ]
        sales_affected = sources.get("sales_data", {}).get("top_products_affected", [])
        affected_skus = {p["sku"] for p in sales_affected}
        for s in active_but_delayed:
            overlap = set(s.get("affected_skus", [])) & affected_skus
            if overlap:
                contradictions.append({
                    "id": f"CON-SUP-{s['id']}",
                    "type": "cross_source_conflict",
                    "sources": ["supplier_status", "sales_data"],
                    "title": f"Supplier {s['name']} Critical — SKUs Overlap with Top Shortages",
                    "detail": (
                        f"Supplier reliability {s['reliability_score']:.2f} with "
                        f"{s['delay_days']}-day delay. Overlapping SKUs: {', '.join(overlap)}. "
                        f"The system should have flagged this supplier for immediate action."
                    ),
                    "severity": "critical",
                })

        # Sentiment vs complaint volume
        complaints = sources.get("customer_complaints", {})
        if complaints:
            quality = complaints.get("categories", {}).get("quality_issue", {})
            if quality.get("severity") == "critical" and quality.get("count", 0) < 100:
                contradictions.append({
                    "id": "CON-QA-001",
                    "type": "severity_volume_mismatch",
                    "sources": ["customer_complaints.quality_issue"],
                    "title": "Quality Issues: Low Volume but Critical Severity",
                    "detail": (
                        f"Only {quality['count']} quality tickets, but severity is 'critical'. "
                        f"Average resolution time ({quality.get('avg_resolution_hours', 0)}h) "
                        f"suggests deep root-cause issues that could escalate."
                    ),
                    "severity": "medium",
                })

        return contradictions

    # ------------------------------------------------------------------
    # Confidence scoring
    # ------------------------------------------------------------------
    def _compute_confidence(self, insights: list[dict], contradictions: list[dict]) -> float:
        if not insights:
            return 0.0
        base = statistics.mean(i.get("confidence", 0.5) for i in insights)
        penalty = min(len(contradictions) * 0.04, 0.20)
        return round(max(base - penalty, 0.0), 4)
