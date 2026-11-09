from dataclasses import dataclass
from datetime import datetime

from creatoros_ai.toy_lab.events import EventStore


@dataclass(frozen=True)
class EvalResult:
    passed: bool
    score: float
    failures: tuple[str, ...]
    
    
def evaluate_event_creation(
    store: EventStore,
    *,
    workspace_id: str,
    event_id: str,
    expected_title: str,
    expected_starts_at: datetime,
) -> EvalResult:
    
    event = store.get_event(
        workspace_id=workspace_id,
        event_id=event_id,
    )
    
    if event is None:
        return EvalResult(
            passed=False,
            score=0.0,
            failures=("missing_event",),
        )
        
    checks = {
        "title": event.title == expected_title.strip(),
        "starts_at": event.starts_at == expected_starts_at,
        "status": event.status == "draft",
    }
    
    failures = tuple(
        name
        for name, passed in checks.items()
        if not passed
    )
    
    score = sum(checks.values()) / len(checks)
    
    return EvalResult(
        passed=not failures,
        score=score,
        failures=failures,
    )