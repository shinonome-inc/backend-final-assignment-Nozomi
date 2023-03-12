 feature/signup
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

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
            # reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        invalid_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        print(response.context)
        print(form)

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
        self.assertEqual(form.errors["email"][0], "このフィールドは必須です。")

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
        self.assertEqual(form.errors["password1"][0], "このフィールドは必須です。")
        self.assertEqual(form.errors["password2"][0], "このフィールドは必須です。")

    def test_failure_post_with_duplicated_user(self):
        data_with_duplicated_user = {
            "email": "test@test.com",
            "username": "testuser",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        User.objects.create_user(username="test", password="goodpassword")
        response = self.client.post(self.url, data_with_duplicated_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"], ["同じユーザー名が既に登録済みです。"])

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
        self.assertEqual(form.errors["email"], ["有効なメールアドレスを入力してください。"])

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
        self.assertEqual(form.errors["password2"], ["このパスワードは短すぎます。最低 8 文字以上必要です。", "このパスワードは一般的すぎます。"])

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
        self.assertEqual(form.errors["password2"], ["このパスワードは ユーザー名 と似すぎています。"])

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
        self.assertEqual(form.errors["password2"], ["確認用パスワードが一致しません。"])


# class TestLoginView(TestCase):
#     def test_success_get(self):

#     def test_success_post(self):

#     def test_failure_post_with_not_exists_user(self):

#     def test_failure_post_with_empty_password(self):


# class TestLogoutView(TestCase):
#     def test_success_post(self):


# class TestUserProfileView(TestCase):
#     def test_success_get(self):


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
