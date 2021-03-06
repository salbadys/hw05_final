from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.index, name="index"),
    path("group/<slug:slug>/", views.group_posts, name="group_list"),
    path("profile/<username>/", views.profile, name="profile"),
    # Просмотр записи
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    # Создание записи
    path("create/", views.post_create, name="post_create"),
    path("posts/<post_id>/edit/", views.post_edit, name="post_edit"),
    # это моя фишка(вне ЯП)
    path("posts/<int:post_id>/delete/", views.post_delete, name="post_delete"),
    # это моя фишка(вне ЯП)
    path("posts/comment/<int:comment_id>/delete/", views.comment_delete,
         name="comment_delete"),
    path('posts/<post_id>/comment/', views.add_comment, name='add_comment'),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]
