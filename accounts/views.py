from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from .admin import User
from .forms import LoginForm, SignupForm


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"


class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    template_name = "accounts/login.html"


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "profile.html"
    slug_field = "username"
    slug_url_kwarg = "username"
