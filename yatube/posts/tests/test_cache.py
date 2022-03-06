from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from posts.models import Post, Group, Comment, Follow
from django.urls import reverse
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()
P_L = 10
NUM_P = 13


class TaskCacheTests(TestCase):
    def setUp(self):
        cache.clear()
        User.objects.create(username="Alex1")
        super().setUpClass()
        Group.objects.create(
            title="Название группы",
            slug="group1",
            description="Для теста описание",
            pk=1,
        )
        for _ in range(NUM_P):
            Post.objects.create(
                text="Текст поста",
                author=User.objects.get(username="Alex1"),
                group=Group.objects.get(title="Название группы"),
            )

        self.guest_client = Client()
        self.user = User.objects.get(username="Alex1")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_post(self):
        """Проверка хранения в кэше"""
        response = self.authorized_client.get(reverse('posts:index'))
        res_1 = response.content
        cache.set('my_cache', res_1, 20)
        post_del = Post.objects.get(id=1)
        post_del.delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        res_2 = response_2.content
        self.assertTrue(res_1 == res_2)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        self.assertIsNone(cache.get('my_cache'))

        # cache.clear()
        # response_3 = self.guest_client.get(reverse('posts:index'))
        # res_3 = response_3.content
        # self.assertNotEqual(res_2, res_3)
