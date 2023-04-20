from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from tweets.models import Tweet

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


class LogoutView(auth_views.LogoutView):
    pass


class UserProfileView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = "accounts/profile.html"

    def get_queryset(self):
        return User.objects.filter(username=self.kwargs.get("username"))

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs["username"])
        context = super().get_context_data(**kwargs)
        context["tweet_list"] = Tweet.objects.select_related("user").filter(user=user)
        context["username"] = user.username
        return context
