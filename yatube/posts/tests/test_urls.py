from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from posts.models import Post, Group
from django.urls import reverse

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_post = 1
        cls.user = User.objects.create(username="Alex")
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Название группы",
            slug="group1",
            description="Для теста описание",
        )
        Post.objects.create(
            text="Текст поста",
            author=User.objects.get(username=cls.user),
            group=Group.objects.get(title=cls.group),
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.get(username=self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        url_page_names = {
            "posts/index.html": "/",
            "posts/group_list.html": reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}
            ),
            "posts/profile.html": reverse(
                "posts:profile", kwargs={"username": self.user}
            ),
            "posts/post_detail.html": f"/posts/{self.test_post}/",
        }
        for template, reverse_name in url_page_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, 200)

    def test_task_added_url_unexisting(self):
        """Неизвестная страница возвращает 404"""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, 404)

    def test_create_user(self):
        """Create поста доступно только авторизованному"""
        response = self.authorized_client.get("/create/")
        self.assertTemplateUsed(response, "posts/create_post.html")
        self.assertEqual(response.status_code, 200)

    def test_edit_user(self):
        """edit поста доступно только автору"""
        response = self.authorized_client.get(f"/posts/{self.test_post}/edit/")
        self.assertTemplateUsed(response, "posts/create_post.html")
        self.assertEqual(response.status_code, 200)

    def test_create_post_guest_client(self):
        response = self.guest_client.get("/create/")
        self.assertRedirects(response, "/auth/login/?next=/create/")
        self.assertEqual(response.status_code, 302)

    def test_edit_post_guest_client(self):
        response = self.guest_client.get("/create/")
        self.assertRedirects(response, "/auth/login/?next=/create/")
        self.assertEqual(response.status_code, 302)

    def test_add_comment_guest_client(self):
        response = self.guest_client.get(
            reverse("posts:add_comment", kwargs={"post_id": self.test_post}),
        )
        self.assertRedirects(response, f"/auth/login/?next=/posts/{self.test_post}/comment/")
        self.assertEqual(response.status_code, 302)
