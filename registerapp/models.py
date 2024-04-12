# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.db.models import JSONField


class Scenario(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='scenarios')
    file_name = models.CharField(max_length=100, unique=True)

    test_case_ids = JSONField()  # JSON 필드 사용
    usernames = JSONField()

    eADP = models.CharField(max_length=100)
    project_code = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    sw_version = models.CharField(max_length=100)
    weather = models.CharField(max_length=100)
    road_type = models.CharField(max_length=50)
    road_status = models.CharField(max_length=50)
    sun_status = models.CharField(max_length=50)
    test_mode = models.CharField(max_length=50)
    temperature = models.CharField(max_length=50)
    description = models.TextField(max_length=500)

    def __str__(self):
        return f"{self.file_name} - {self.project_code}"
