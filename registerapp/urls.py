from django.urls import path
from .views import upload_json, search_scenarios, homepage

app_name = 'registerapp'

urlpatterns = [
    path('register/', upload_json, name='register'),
    path('search/', search_scenarios, name='search'),
    path('homepage/', homepage, name='homepage'),

]
