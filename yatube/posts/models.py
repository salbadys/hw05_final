from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel
from django.db.models import UniqueConstraint

User = get_user_model()
PER_W = 15


class Group(models.Model):
    title = models.CharField("group_name", max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(CreatedModel):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts")
    group = models.ForeignKey(
        Group, models.SET_NULL, blank=True, null=True, related_name="posts"
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:PER_W]


class Comment(CreatedModel):
    text = models.TextField()
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )
    UniqueConstraint(fields=['user', 'author'], name='unique_follow')
