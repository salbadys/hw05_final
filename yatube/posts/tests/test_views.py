from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from posts.models import Post, Group, Comment, Follow
from django.urls import reverse
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()
P_L = 10
NUM_P = 10


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create(username="Alex1")
        super().setUpClass()
        Group.objects.create(
            title="Название группы",
            slug="group1",
            description="Для теста описание",
            pk=1,
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        for _ in range(NUM_P):
            Post.objects.create(
                text="Текст поста",
                author=User.objects.get(username="Alex1"),
                group=Group.objects.get(title="Название группы"),
                image=uploaded
            )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.get(username="Alex1")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Проверка что URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": (
                reverse("posts:group_list", kwargs={"slug": "group1"})
            ),
            "posts/profile.html": (
                reverse("posts:profile", kwargs={"username": "Alex1"})
            ),
            "posts/post_detail.html": (
                reverse("posts:post_detail", kwargs={"post_id": "1"})
            ),
            "posts/create_post.html": (
                reverse("posts:post_edit", kwargs={"post_id": "1"})
            ),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, 200)

    def test_page_create_post(self):
        """Проверка создания поста только для авторизованного."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        self.assertTemplateUsed(response, "posts/create_post.html")
        self.assertEqual(response.status_code, 200)

    def test_page_index_context(self):
        """Шаблон страниц сформирован с правильным контекстом."""
        templates_page_names = (
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": "group1"}),
            reverse("posts:profile", kwargs={"username": "Alex1"}),
        )
        for page in templates_page_names:
            response = self.authorized_client.get(page)
            first_object = response.context["page_obj"][0]
            task_text_0 = first_object.text
            task_author_0 = first_object.author.username
            task_group_0 = first_object.group.title
            task_image_0 = first_object.image
            self.assertEqual(task_text_0, "Текст поста")
            self.assertEqual(task_author_0, "Alex1")
            self.assertEqual(task_group_0, "Название группы")
            self.assertTrue(task_image_0)

    def test_task_list_page_group_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": "1"})
        )
        first_object = response.context["post"]
        task_text_0 = first_object.text
        task_author_0 = first_object.author.username
        task_group_0 = first_object.group.title
        self.assertEqual(task_text_0, "Текст поста")
        self.assertEqual(task_author_0, "Alex1")
        self.assertEqual(task_group_0, "Название группы")

    def test_post_edit_context(self):
        """Корректность шаблона редактирования и создания поста"""
        page_names = (
            reverse("posts:post_edit", kwargs={"post_id": "1"}),
            reverse("posts:post_create"),
        )
        for form in page_names:
            response = self.authorized_client.get(form)
            form_fields = {
                "text": forms.fields.CharField,
                "group": forms.ModelChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context["form"].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_create_post_index(self):
        """Проверка появления постов на страницах"""
        Group.objects.create(
            title="Група 2",
            slug="group2",
            description="Для теста описание",
        )
        Post.objects.create(
            text="Текст от группы 2",
            author=User.objects.get(username="Alex1"),
            group=Group.objects.get(title="Група 2"),
        )
        templates_page_names = (
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": "group2"}),
            reverse("posts:profile", kwargs={"username": "Alex1"}),
        )
        for page in templates_page_names:
            response = self.authorized_client.get(page)
            self.assertIn(
                Post.objects.get(
                    text="Текст от группы 2"), response.context["page_obj"]
            )

    def test_control_edit_post(self):
        """Проверка добавление поста при редактировании на главную"""
        form_data = {"text": "Check", "group": 1}
        self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": 10}),
            data=form_data,
            follow=True,
        )
        response = self.authorized_client.get(reverse("posts:index"))
        self.assertIn(Post.objects.get(
            text="Check"), response.context["page_obj"]
        )

    def test_control_add_comment(self):
        """Проверка добавление комментария на странице поста"""
        form_data = {"text": "Check comment"}
        response = self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": 10}),
            data=form_data,
            follow=True,
        )
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": 10}),
        )
        self.assertIn(Comment.objects.get(
            text="Check comment"), response.context["comments"]
        )

    def test_check_requst_user_work_follow(self):
        User.objects.create(username="Mike")
        mike = User.objects.get(username="Mike")
        Post.objects.create(
            text="Пост Майка",
            author=User.objects.get(username="Mike"),
            group=Group.objects.get(title="Название группы"),
        )

        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={"username": "Mike"})
        )
        self.assertTrue(
            Follow.objects.filter(user=self.user).
            filter(author=mike)
        )
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={"username": "Mike"})
        )
        self.assertFalse(
            Follow.objects.filter(user=self.user).
            filter(author=mike)
        )

    def test_check_requst_view_follow(self):
        """Появленее записей у подписанных и неподп."""
        User.objects.create(username="Mike")
        User.objects.create(username="Vova")
        Post.objects.create(
            text="Пост Майка",
            author=User.objects.get(username="Mike"),
            group=Group.objects.get(title="Название группы"),
        )
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={"username": "Mike"})
        )
        response = self.authorized_client.get(reverse(
            "posts:follow_index")
        )
        self.assertIn(Post.objects.get(
            text="Пост Майка"), response.context["page_obj"]
        )
        self.user = User.objects.get(username="Vova")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(reverse(
            "posts:follow_index")
        )
        self.assertIsNot(Post.objects.get(
            text="Пост Майка"), response.context["page_obj"]
        )
