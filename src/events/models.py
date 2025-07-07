from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    organizer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="organized_events", blank=True, null=True
    )
    participants = models.ManyToManyField(User, through="EventRegistration", related_name="events_participated")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} @ {self.date}"


class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "event")

    def __str__(self):
        return f"{self.user} registered for {self.event}"
