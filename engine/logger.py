"""
Antigravity-Style Reasoning Logger

Captures every cognitive step of the agent — observation, reasoning, decision,
action, result, failure, and recovery — in a structured trace format.
"""

import json
import os
import copy
from datetime import datetime, timezone


class AgentLogger:
    """Generates and persists Antigravity-style reasoning traces."""

    def __init__(self, log_path: str = "outputs/logs.json"):
        self.log_path = log_path
        self.traces: list[dict] = []
        self._current_run_id: str = ""
        self._step_counter: int = 0

    # ------------------------------------------------------------------
    # Run lifecycle
    # ------------------------------------------------------------------
    def start_run(self) -> str:
        """Begin a new agent run and return its ID."""
        self._current_run_id = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")
        self._step_counter = 0
        return self._current_run_id

    # ------------------------------------------------------------------
    # Core trace entry
    # ------------------------------------------------------------------
    def log(
        self,
        phase: str,
        observation: str,
        reasoning: str,
        decision: str,
        action: str,
        result: str,
        failure: str | None = None,
        recovery: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """
        Record a single reasoning step.

        Parameters
        ----------
        phase : str
            Pipeline phase (ingestion | analysis | planning | simulation | output).
        observation : str
            What the agent observed.
        reasoning : str
            Chain-of-thought reasoning about the observation.
        decision : str
            The decision the agent reached.
        action : str
            The concrete action taken.
        result : str
            Outcome of the action.
        failure : str | None
            Description of failure, if any.
        recovery : str | None
            Recovery action taken after failure.
        metadata : dict | None
            Arbitrary extra data to attach.
        """
        self._step_counter += 1
        entry = {
            "run_id": self._current_run_id,
            "step": self._step_counter,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": phase,
            "observation": observation,
            "reasoning": reasoning,
            "decision": decision,
            "action": action,
            "result": result,
            "failure": failure,
            "recovery": recovery,
            "metadata": metadata or {},
        }
        self.traces.append(entry)
        return copy.deepcopy(entry)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self) -> str:
        """Write all traces to disk and return the file path."""
        os.makedirs(os.path.dirname(self.log_path) or ".", exist_ok=True)
        with open(self.log_path, "w", encoding="utf-8") as fh:
            json.dump(self.traces, fh, indent=2, ensure_ascii=False)
        return self.log_path

    def get_traces(self) -> list[dict]:
        """Return a deep copy of all recorded traces."""
        return copy.deepcopy(self.traces)
