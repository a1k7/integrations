from src.models import SentinelInput, DetectionResult, DetectionType, RiskLevel
from src.detectors.base import BaseDetector

class DelegationEscalationDetector(BaseDetector):
    """
    Detects when an agent suddenly gains broader delegation authority.
    """

    def name(self) -> str:
        return "delegation_escalation"

    def detect(self, input_data: SentinelInput) -> DetectionResult:
        # Baseline: normal delegation chain depth = 1-2
        # Escalation: depth > 3 or new high-privilege delegates
        depth = len(input_data.delegation_chain)
        risk_score = 0.0
        reason = "Delegation chain within normal range"

        if depth > 3:
            risk_score = min(0.8 + (depth - 3) * 0.05, 1.0)
            reason = f"Delegation chain depth {depth} exceeds normal threshold"
        elif "root" in input_data.delegation_chain and "admin" in input_data.delegation_chain:
            risk_score = 0.7
            reason = "Agent has both root and admin delegation"

        return DetectionResult(
            detection_type=DetectionType.DELEGATION_ESCALATION,
            risk_score=risk_score,
            risk_level=self._risk_level(risk_score),
            reason=reason,
            evidence={
                "delegation_chain": input_data.delegation_chain,
                "depth": depth,
                "threshold": 3
            }
        )

    def _risk_level(self, score: float) -> RiskLevel:
        if score < 0.3: return RiskLevel.LOW
        if score < 0.6: return RiskLevel.MEDIUM
        if score < 0.8: return RiskLevel.HIGH
        return RiskLevel.CRITICAL