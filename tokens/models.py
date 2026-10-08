from django.db import models

import uuid


# Create your models here.
class Token(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    token = models.CharField()
    scope = models.JSONField(blank=True, default=None)
    issued_at = models.DateTimeField()
    expires_at = models.DateTimeField()
