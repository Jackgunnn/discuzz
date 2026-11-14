import uuid

from django.utils import timezone

from .models import OutboxEvent


def create_event(
    event_type,
    user_id,
    payload,
    source="discuzz",
    event_version=1
):
    event = OutboxEvent.objects.create(
        event_id=uuid.uuid4(),
        event_type=event_type,
        event_version=event_version,
        source=source,
        user_id=user_id,
        payload=payload,
        occurred_at=timezone.now()
    )

    return event