from django.db import models
from django.contrib.postgres.fields import JSONField


class ApiCall(models.Model):
    called_at = models.DateTimeField(auto_now=True)
    data = JSONField()
