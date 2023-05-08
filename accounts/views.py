from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, View

from tweets.models import Tweet

from .admin import FriendShip, User
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
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs["username"])
        context = super().get_context_data(**kwargs)
        context["tweet_list"] = Tweet.objects.select_related("user").filter(user=user)
        context["tweet_user"] = user
        context["following_count"] = FriendShip.objects.filter(follower=user).count()
        context["follower_count"] = FriendShip.objects.filter(following=user).count()
        context["is_following"] = (
            FriendShip.objects.select_related("user").filter(following=user, follower=self.request.user).exists()
        )
        return context


class FollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        following = get_object_or_404(User, username=self.kwargs["username"])

        if request.user == following:
            return HttpResponseBadRequest("自分自身を対象にできません")

        if FriendShip.objects.filter(follower=request.user, following=following).exists():
            messages.warning(request, "あなたはすでにフォローしています")
            return redirect("tweets:home")

        else:
            FriendShip.objects.create(follower=request.user, following=following)
            messages.success(request, "フォローしました")
            return redirect("tweets:home")


class UnFollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        following = get_object_or_404(User, username=self.kwargs["username"])

        if request.user == following:
            return HttpResponseBadRequest("自分自身を対象にできません")

            friends = FriendShip.objects.filter(follower=request.user, following=following)
            friends.delete()
            messages.success(request, "フォローを外しました")
            return redirect("tweets:home")


class FollowerListView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = "accounts/follower_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs["username"])
        context["follower_list"] = FriendShip.objects.select_related("follower").filter(following=user)
        return context


class FollowingListView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = "accounts/following_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs["username"])
        context["following_list"] = FriendShip.objects.select_related("following").filter(follower=user)
        return context
