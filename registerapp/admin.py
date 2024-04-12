from django.contrib import admin
from .models import Scenario

# Register your models here.

@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'file_name', 'test_case_ids', 'usernames', 'eADP', 'project_code',
        'location', 'sw_version', 'weather', 'road_type', 'road_status',
        'sun_status', 'test_mode', 'temperature', 'description'
    )
