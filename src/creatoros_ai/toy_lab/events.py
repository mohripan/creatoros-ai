from dataclasses import dataclass
from datetime import date, datetime
from socketserver import DatagramRequestHandler
from uuid import uuid4


class InvalidEvent(ValueError):
    pass


class IdempotencyConflict(ValueError):
    pass


@dataclass(frozen=True)
class Event:
    id: str
    workspace_id: str
    title: str
    starts_at: datetime
    status: str = "draft"
    
    
class EventStore:
    def __init__(self):
        self.events: dict[str, Event] = {}
        
        # Maps a logical request to its original result.
        self.requests: dict[
            tuple[str, str],
            tuple[tuple[str, datetime], str]
        ] = {}
        
    def create_event(
        self,
        *,
        workspace_id: str,
        title: str,
        starts_at: datetime,
        idempotency_key: str,
    ) -> Event:
        
        workspace_id = workspace_id.strip()
        title = title.strip()
        idempotency_key = idempotency_key.strip()
        
        # Validate before changing application state.
        if not workspace_id or not title or not idempotency_key:
            raise InvalidEvent("Required field is empty")
        
        if (
            not isinstance(starts_at, datetime)
            or starts_at.utcoffset() is None
        ):
            raise InvalidEvent("A timezone-aware datetime is required")
        
        request_key = (workspace_id, idempotency_key)
        payload = (title, starts_at)
        
        # Has this logical request already been executed?
        if request_key in self.requests:
            original_payload, event_id = self.requests[request_key]
            
            if original_payload != payload:
                raise IdempotencyConflict(
                    "The same key was used for a different request"
                )
                
            return self.events[event_id]
        
        event = Event(
            id=str(uuid4()),
            workspace_id=workspace_id,
            title=title,
            starts_at=starts_at,
        )
        
        self.events[event.id] = event
        self.requests[request_key] = (payload, event.id)
        
        return event
    
    def get_event(self, workspace_id: str, event_id: str):
        event = self.events.get(event_id)
        
        if event is None or event.workspace_id != workspace_id:
            return None
        
        return event
    
    def list_events(self, workspace_id: str):
        return [
            event
            for event in self.events.values()
            if event.workspace_id == workspace_id
        ]