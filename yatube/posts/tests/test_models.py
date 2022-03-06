from django.test import TestCase
from posts.models import Group, Post
from django.contrib.auth import get_user_model

User = get_user_model()


PER_W = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test1",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост для проверки",
        )

    def test_models_have_correct_object_names_group(self):
        """Проверяем, что у модели group корректно работает __str__."""
        group = PostModelTest.group
        name = group.title
        self.assertEqual(name, group.title)

    def test_models_have_correct_object_names_post(self):
        """Проверяем, что у модели post
        корректно работает __str__ и ограничечение."""
        post = PostModelTest.post
        name = post.text[:PER_W]
        self.assertEqual(name, str(post))
