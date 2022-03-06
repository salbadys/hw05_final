from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.models import Post, Group
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username="Alex")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Корректность работы создания поста"""
        tasks_count = Post.objects.count()
        form_data = {
            "text": "Тестовый заголовок 2",
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse("posts:profile", kwargs={"username": "Alex"})
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text="Тестовый заголовок 2",
            ).exists()
        )

    def test_create_post_image(self):
        """Корректность работы создания поста с картинкой"""
        tasks_count = Post.objects.count()
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
        form_data = {
            "text": "Тестовый заголовок 2",
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse("posts:profile", kwargs={"username": "Alex"})
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text="Тестовый заголовок 2",
            ).exists()
        )

    def test_edit_post(self):
        """Корректность работы редактирования поста"""
        Group.objects.create(
            title="Группа для теста",
            slug="group1",
            description="Тестовое описание",
            pk=1,
        )
        Post.objects.create(
            text="Тестовый заголовок",
            author=User.objects.get(username="Alex"),
            group=Group.objects.get(title="Группа для теста"),
        )

        tasks_count = Post.objects.count()
        form_data = {"text": "Тестовый заголовок 2", "group": 1}
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": "1"}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse("posts:post_detail", kwargs={"post_id": "1"})
        )
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertTrue(
            Post.objects.filter(
                text="Тестовый заголовок 2",
            ).exists()
        )
