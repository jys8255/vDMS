# Create your models here.
from django.contrib.auth.models import User
from django.db import models
class DtcCode(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
class ErrCompId(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Scenario(models.Model):
    user             = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='scenarios')
    file_name        = models.CharField(max_length=100, unique=True)
    eADP             = models.CharField(max_length=100)
    project_code     = models.CharField(max_length=100)
    location         = models.CharField(max_length=100)
    simulation_type  = models.CharField(max_length=100)
    test_Scenario_ID = models.CharField(max_length=100)
    sw_version       = models.CharField(max_length=10)
    weather          = models.CharField(max_length=50)
    road_type        = models.CharField(max_length=50)
    sun_status       = models.CharField(max_length=50)
    temperature      = models.IntegerField()
    dtc_code         = models.ManyToManyField(DtcCode)
    err_comp_id      = models.ManyToManyField(ErrCompId)


