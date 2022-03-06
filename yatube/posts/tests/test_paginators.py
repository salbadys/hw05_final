from django.core.cache import cache
from django.test import Client, TestCase
from posts.models import Post, Group
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()
P_L = 10
NUM_P = 13


class TestPaginator(TestCase):
    @classmethod
    def setUpClass(cls):
        cache.clear()
        User.objects.create(username="Alex3")
        super().setUpClass()
        Group.objects.create(
            title="Название группы",
            slug="group1",
            description="Для теста описание",
        )
        cls.user = User.objects.get(username="Alex3")
        cls.group = Group.objects.get(title="Название группы")

        objs = (
            Post(
                text="Текст поста",
                author=cls.user,
                group=cls.group,
            )
            for _ in range(NUM_P)
        )
        Post.objects.bulk_create(objs)

    def setUp(self):
        self.user = User.objects.get(username="Alex3")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_index_context(self):
        """Шаблон страниц сформирован с правильным контекстом."""
        templates_page_names = (
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": "group1"}),
            reverse("posts:profile", kwargs={"username": "Alex3"}),
        )
        for page in templates_page_names:
            response = self.authorized_client.get(page)
            self.assertTrue(len(response.context["page_obj"]) == P_L)
