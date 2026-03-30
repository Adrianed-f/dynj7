from django.db import models

class Submission(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"Submission #{self.pk} ({self.created_at:%Y-%m-%d %H:%M})"
