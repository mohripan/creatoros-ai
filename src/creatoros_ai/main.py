from datetime import datetime

from creatoros_ai.toy_lab.events import EventStore
from creatoros_ai.toy_lab.evaluation import evaluate_event_creation


def main():
    store = EventStore()

    requested_time = datetime.fromisoformat(
        "2026-12-04T19:00:00+07:00"
    )

    event = store.create_event(
        workspace_id="creator-123",
        title="Python Workshop",
        starts_at=requested_time,
        idempotency_key="operation-456",
    )

    result = evaluate_event_creation(
        store,
        workspace_id="creator-123",
        event_id=event.id,
        expected_title="Python Workshop",
        expected_starts_at=requested_time,
    )

    print(result)


if __name__ == "__main__":
    main()