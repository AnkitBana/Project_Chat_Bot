"""
Guardrails — policy layer that enforces permissions and prevents unsafe actions.
Human-in-the-loop (HITL) — pauses execution for sensitive operations.
"""
import re
from typing import Optional, Callable, List, Dict, Any


# ── Blocked patterns ──────────────────────────────────────────────────────────

BLOCKED_PATTERNS: List[Dict[str, Any]] = [
    # Prompt injection attempts
    {
        "id": "prompt_injection",
        "pattern": r"(ignore (previous|all|above) instructions?|you are now|jailbreak|act as (an? )?(evil|unrestricted|dan))",
        "reason": "Prompt injection attempt detected.",
        "severity": "high",
    },
    # Trying to exfiltrate system files
    {
        "id": "system_file_access",
        "pattern": r"(read|open|cat|show).{0,30}(\/etc\/passwd|\/etc\/shadow|\.ssh\/|id_rsa|\.env)",
        "reason": "Access to sensitive system files is not permitted.",
        "severity": "high",
    },
    # Dangerous shell commands
    {
        "id": "shell_injection",
        "pattern": r"(rm -rf|del \/f|format c:|shutdown|mkfs|dd if=|wget.+\|.+sh|curl.+\|.+sh)",
        "reason": "Potentially destructive shell command detected.",
        "severity": "high",
    },
]

# ── Sensitive patterns that require human approval ────────────────────────────

SENSITIVE_PATTERNS: List[Dict[str, Any]] = [
    {
        "id": "financial_transaction",
        "pattern": r"(transfer|send|pay|wire|debit|charge|refund).{0,30}(\$[\d,]+|[\d,]+ (dollar|usd|gbp|eur))",
        "reason": "Financial transaction detected — requires approval.",
    },
    {
        "id": "delete_files",
        "pattern": r"(delete|remove|erase|wipe).{0,20}(file|folder|directory|database|all)",
        "reason": "Destructive file operation — requires approval.",
    },
    {
        "id": "bulk_api",
        "pattern": r"(send|post|submit|broadcast).{0,30}(to all|everyone|bulk|mass|batch)",
        "reason": "Bulk API operation — requires approval.",
    },
]


class GuardrailViolation(Exception):
    """Raised when a blocked pattern is matched."""
    def __init__(self, rule_id: str, reason: str, severity: str = "medium"):
        self.rule_id  = rule_id
        self.reason   = reason
        self.severity = severity
        super().__init__(reason)


class HITLRequest:
    """Represents a pending human-in-the-loop approval request."""
    def __init__(self, rule_id: str, reason: str, original_input: str):
        self.rule_id        = rule_id
        self.reason         = reason
        self.original_input = original_input
        self.approved: Optional[bool] = None  # None = pending


class Guardrails:
    """
    Policy engine that:
    1. BLOCKS requests matching dangerous patterns
    2. PAUSES requests matching sensitive patterns for human approval
    3. Logs all decisions to the tracer
    """

    def __init__(self):
        self._hitl_queue: List[HITLRequest] = []
        self._hitl_callback: Optional[Callable[[HITLRequest], bool]] = None

    def set_hitl_callback(self, fn: Callable[[HITLRequest], bool]):
        """Register a function that handles human approval (returns True/False)."""
        self._hitl_callback = fn

    def check(self, user_input: str) -> Optional[HITLRequest]:
        """
        Check input against all policies.
        - Raises GuardrailViolation if blocked.
        - Returns HITLRequest if human approval needed.
        - Returns None if safe to proceed.
        """
        text = user_input.lower()

        # 1. Check blocked patterns (hard deny)
        for rule in BLOCKED_PATTERNS:
            if re.search(rule["pattern"], text, re.IGNORECASE):
                raise GuardrailViolation(rule["id"], rule["reason"], rule.get("severity", "high"))

        # 2. Check sensitive patterns (soft deny — needs human approval)
        for rule in SENSITIVE_PATTERNS:
            if re.search(rule["pattern"], text, re.IGNORECASE):
                req = HITLRequest(rule["id"], rule["reason"], user_input)
                self._hitl_queue.append(req)
                return req

        return None  # safe

    def resolve_hitl(self, rule_id: str, approved: bool) -> bool:
        """Mark a pending HITL request as approved or rejected."""
        for req in self._hitl_queue:
            if req.rule_id == rule_id and req.approved is None:
                req.approved = approved
                return True
        return False

    def get_pending_hitl(self) -> List[Dict]:
        return [
            {"rule_id": r.rule_id, "reason": r.reason, "input": r.original_input[:100]}
            for r in self._hitl_queue if r.approved is None
        ]

    def get_all_rules(self) -> Dict[str, Any]:
        return {
            "blocked":   [{"id": r["id"], "reason": r["reason"], "severity": r.get("severity")} for r in BLOCKED_PATTERNS],
            "sensitive":  [{"id": r["id"], "reason": r["reason"]} for r in SENSITIVE_PATTERNS],
        }


# ── Module singleton ──────────────────────────────────────────────────────────
_guardrails = Guardrails()

def get_guardrails() -> Guardrails:
    return _guardrails
