from django.db import models
from django.conf import settings

class Channel(models.Model):
    name = models.CharField(max_length=80, unique=True)
    is_private = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="channels_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.name}"

class ChannelMember(models.Model):
    channel = models.ForeignKey(
        "Channel", on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("channel", "user")

class Message(models.Model):
    channel = models.ForeignKey(
        "Channel", on_delete=models.CASCADE, related_name="messages",
        null=True, blank=True
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="messages_sent"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.CASCADE, related_name="dms_received"
    )  # DM si channel es None
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

