from django.conf import settings
from django.db import models

from components.fields.encrypted_text_field import EncryptedTextField

import uuid

# Create your models here.


class Baby(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    name = models.CharField()


# TODO: change name to an encrypted field before releasing to production


class GuardianMapping(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, editable=True, default=uuid.uuid4
    )
    baby = models.ForeignKey(
        Baby, on_delete=models.CASCADE, related_name="assigned_baby"
    )
    guardian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_guardian",
    )


class BabyEvent(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    baby = models.ForeignKey(to=Baby, on_delete=models.CASCADE)
    type = models.CharField()
    data = models.JSONField(
        default=None,
        blank=True,
    )
    created_at = models.CharField()
    notes = models.TextField(max_length=1000, default=None)
