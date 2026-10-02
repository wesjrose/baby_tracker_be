from django.conf import settings
from django.db import models

# Create your models here.

class Baby(models.Model):
    name = models.CharField()


class GuardianMapping(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=True)
    baby = models.ForeignKey(Baby, on_delete=models.PROTECT, related_name="assigned_baby")
    guardian = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="assigned_guardian")    


