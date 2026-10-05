from django.conf import settings
from django.db import models

from components.fields.encrypted_text_field import EncryptedTextField

import uuid

# Create your models here.

class Baby(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    name = EncryptedTextField()


class GuardianMapping(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=True, default=uuid.uuid4)
    baby = models.ForeignKey(Baby, on_delete=models.PROTECT, related_name="assigned_baby")
    guardian = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="assigned_guardian")    


