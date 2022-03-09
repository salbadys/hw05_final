from django.core.cache import cache
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from .models import Post, Group, Follow, User
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required

PER_PAGE: int = 10


@cache_page(20 * 1)
def index(request):
    post_list = Post.objects.all()
    post_count = post_list.count()
    paginator = Paginator(post_list, PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "post_count": post_count
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj, "group": group}
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author).exists()
    else:
        following = None
    post_list = author.posts.all()
    paginator = Paginator(post_list, PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    count_post = post_list.count()
    context = {
        "page_obj": page_obj,
        "count_post": count_post,
        "author": author,
        "following": following}
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(
        request.POST or None)
    comments = post.comments.all()
    count = Post.objects.filter(group=post.group).count()
    context = {
        "post": post,
        "count": count,
        "form": form,
        "comments": comments
    }
    return render(request, "posts/post_detail.html", context)


# это моя фишка(вне курса ЯП)
@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("posts/index.html")
    post.delete()
    return redirect('posts:index')


@login_required()
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if not form.is_valid():
        return render(request, "posts/create_post.html", {"form": form})
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect("posts:profile", username=request.user)


@login_required()
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        count = Post.objects.filter(group=post.group).count()
        context = {"post": post, "count": count}
        return render(request, "posts/post_detail.html", context)
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post or None)
    context = {"form": form, "is_edit": is_edit}
    if not form.is_valid():
        return render(request, "posts/create_post.html", context)
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect("posts:post_detail", post_id=post.id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    user = request.user
    post_list = Post.objects.filter(author__following__user=user)
    post_count = post_list.count()
    paginator = Paginator(post_list, PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "post_count": post_count
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        return redirect('posts:index')
    Follow.objects.get_or_create(
        user=request.user,
        author=user
    )
    return redirect('posts:index')


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=user
    ).delete()
    return redirect('posts:index')
