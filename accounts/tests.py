from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from tweets.models import Tweet

User = get_user_model()


class TestSignupView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        invalid_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)
        self.assertIn("このフィールドは必須です。", form.errors["username"])
        self.assertIn("このフィールドは必須です。", form.errors["email"])
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])

    def test_failure_post_with_empty_username(self):
        invalid_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])

    def test_failure_post_with_empty_email(self):
        data_with_empty_email = {
            "email": "",
            "username": "testuser",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, data_with_empty_email)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn(form.errors["email"][0], "このフィールドは必須です。")

    def test_failure_post_with_empty_password(self):
        data_with_empty_password = {
            "email": "test@test.com",
            "username": "testuser",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, data_with_empty_password)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn(form.errors["password1"][0], "このフィールドは必須です。")
        self.assertIn(form.errors["password2"][0], "このフィールドは必須です。")

    def test_failure_post_with_duplicated_user(self):
        data_with_duplicated_user = {
            "email": "test@test.com",
            "username": "testuser",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        User.objects.create_user(username="testuser", password="testpassword")
        response = self.client.post(self.url, data_with_duplicated_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("同じユーザー名が既に登録済みです。", form.errors["username"])

    def test_failure_post_with_invalid_email(self):
        data_invalid_email = {
            "email": "test@test",
            "username": "testuser",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, data_invalid_email)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("有効なメールアドレスを入力してください。", form.errors["email"])

    def test_failure_post_with_too_short_password(self):
        data_too_short_password = {
            "email": "test@test.com",
            "username": "testuser",
            "password1": "test",
            "password2": "test",
        }
        response = self.client.post(self.url, data_too_short_password)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは短すぎます。最低 8 文字以上必要です。", form.errors["password2"])

    def test_failure_post_with_password_similar_to_username(self):
        data_similar_to_username = {
            "email": "test@test.com",
            "username": "testtest",
            "password1": "testtesta",
            "password2": "testtesta",
        }

        response = self.client.post(self.url, data_similar_to_username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは ユーザー名 と似すぎています。", form.errors["password2"])

    def test_failure_post_with_only_numbers_password(self):
        data_number_password = {
            "email": "test@test.com",
            "username": "testuser",
            "password1": "11111111",
            "password2": "11111111",
        }
        response = self.client.post(self.url, data_number_password)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"], ["このパスワードは一般的すぎます。", "このパスワードは数字しか使われていません。"])

    def test_failure_post_with_mismatch_password(self):
        data_mismatch_password = {
            "email": "test@test.com",
            "username": "testuser",
            "password1": "testpassword",
            "password2": "testpasswood",
        }
        response = self.client.post(self.url, data_mismatch_password)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("確認用パスワードが一致しません。", form.errors["password2"])


class TestLoginView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )
        self.url = reverse("accounts:login")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "testpassword",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        invalid_data = {
            "username": "tastser",
            "password": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertIn("正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。", form.errors["__all__"])
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "password": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["password"])
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        self.url = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")

    def test_success_post(self):
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(
            response,
            reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )
        self.url = reverse("accounts:login")

    def test_success_get(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertQuerysetEqual(context['tweet'], Tweet.objects.filter(user=self.user))


# class TestUserProfileEditView(TestCase):
#     def test_success_get(self):

#     def test_success_post(self):

#     def test_failure_post_with_not_exists_user(self):

#     def test_failure_post_with_incorrect_user(self):


# class TestFollowView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_user(self):

#     def test_failure_post_with_self(self):


# class TestUnfollowView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_incorrect_user(self):


# class TestFollowingListView(TestCase):
#     def test_success_get(self):


# class TestFollowerListView(TestCase):
#      def test_success_get(self):
