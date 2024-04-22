from django.urls import path
from .views import upload_files, homepage, search_scenarios, check_duplicate

app_name = 'registerapp'

urlpatterns = [
    path('register/', upload_files, name='register'),
    path('check-duplicate/', check_duplicate, name='check_duplicate'),
    path('search/', search_scenarios, name='search'),
    path('home/', homepage, name='homepage'),
]