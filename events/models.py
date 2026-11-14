import uuid

from django.db import models


class OutboxEvent(models.Model):
    event_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    event_type = models.CharField(max_length=100)
    event_version = models.PositiveSmallIntegerField(default=1)
    source = models.CharField(max_length=100, default="discuzz")

    user_id = models.IntegerField(null=True, blank=True)
    payload = models.JSONField()

    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    published_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["published_at", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.event_id}"