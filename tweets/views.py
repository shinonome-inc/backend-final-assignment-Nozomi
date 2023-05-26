from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, TemplateView
from django.views.generic.base import View

from .forms import TweetForm
from .models import Like, Tweet


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "tweets/home.html"
    model = Tweet

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tweet_list"] = Tweet.objects.select_related("user").order_by("-created_at")
        liked_list = (
            Like.objects.prefetch_related("tweet").filter(user=self.request.user).values_list("tweet_id", flat=True)
        )
        context["liked_list"] = liked_list
        return context


class TweetDetailView(LoginRequiredMixin, DetailView):
    model = Tweet
    template_name = "tweets/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        liked_list = (
            Like.objects.prefetch_related("tweet").filter(user=self.request.user).values_list("tweet_id", flat=True)
        )
        context["liked_list"] = liked_list
        return context


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    template_name = "tweets/create.html"
    form_class = TweetForm
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tweet
    template_name = "tweets/delete.html"
    success_url = reverse_lazy("tweets:home")

    def test_func(self, **kwargs):
        pk = self.kwargs["pk"]
        tweet = Tweet.objects.get(pk=pk)
        return tweet.user == self.request.user


class LikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tweet_id = self.kwargs["pk"]
        tweet = get_object_or_404(Tweet, id=tweet_id)
        Like.objects.get_or_create(tweet=tweet, user=self.request.user)
        unlike_url = reverse("tweets:unlike", kwargs={"pk": tweet_id})
        tweet = Tweet.objects.prefetch_related("liked_tweet").get(id=tweet_id)
        like_count = tweet.liked_tweet.count()
        is_liked = True
        context = {
            "like_count": like_count,
            "tweet_id": tweet_id,
            "is_liked": is_liked,
            "unlike_url": unlike_url,
        }
        return JsonResponse(context)


class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tweet_id = self.kwargs["pk"]
        tweet = get_object_or_404(Tweet, pk=tweet_id)
        if like := Like.objects.filter(user=self.request.user, tweet=tweet):
            like.delete()
        is_liked = False
        like_url = reverse("tweets:like", kwargs={"pk": tweet_id})
        tweet = Tweet.objects.prefetch_related("liked_tweet").get(id=tweet_id)
        like_count = tweet.liked_tweet.count()
        context = {
            "like_count": like_count,
            "tweet_id": tweet_id,
            "is_liked": is_liked,
            "like_url": like_url,
        }
        return JsonResponse(context)
