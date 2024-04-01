
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy



class CustomLoginView(LoginView):
    template_name = 'accountapp/login.html'
    success_url = reverse_lazy('registerapp:homepage')