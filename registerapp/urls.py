from django.urls import path
from .views import upload_files, homepage, search_scenarios

app_name = 'registerapp'

urlpatterns = [
    path('register/', upload_files, name='register'),
    path('search/', search_scenarios, name='search'),
    path('home/', homepage, name='homepage'),
]