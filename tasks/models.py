from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Task(models.Model):
    STATUS_CHOICES = [
        ("open", "Abierta"),
        ("doing", "En progreso"),
        ("done", "Hecha"),
    ]
    title       = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks_created")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks_assigned")
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    due_date    = models.DateField(null=True, blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        who = self.assigned_to.username if self.assigned_to else "sin asignar"
        return f"{self.title} · {who} · {self.get_status_display()}"

