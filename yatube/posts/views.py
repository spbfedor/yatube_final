from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(
    request
):
    post_list = Post.objects.select_related(
        'group'
    ).all()
    paginator = Paginator(
        post_list,
        settings.NAMBER_OF_POSTS
    )
    page_number = request.GET.get(
        "page"
    )
    page_obj = paginator.get_page(
        page_number
    )
    template = "posts/index.html"
    context = {
        "page_obj": page_obj,
    }
    return render(
        request,
        template,
        context
    )


def group_posts(
    request,
    slug
):
    template = "posts/group_list.html"
    group = get_object_or_404(
        Group,
        slug=slug
    )
    post_list = group.posts.order_by(
        "-pub_date"
    )
    paginator = Paginator(
        post_list,
        settings.NAMBER_OF_POSTS
    )
    page_number = request.GET.get(
        "page"
    )
    page_obj = paginator.get_page(
        page_number
    )
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(
        request,
        template,
        context
    )


def profile(
    request,
    username
):
    author = get_object_or_404(
        User,
        username=username
    )
    post_list = Post.objects.filter(
        author=author.id
    ).order_by(
        "-pub_date"
    )
    paginator = Paginator(
        post_list,
        settings.NAMBER_OF_POSTS
    )
    page_number = request.GET.get(
        "page"
    )
    page_obj = paginator.get_page(
        page_number
    )
    template = "posts/profile.html"
    count = post_list.count()

    following = False
    if request.user.is_authenticated:
        following = author.following.filter(
            user=request.user
        )
    context = {
        "post_list": post_list,
        "author": author,
        "page_obj": page_obj,
        "count": count,
        "following": following,
    }
    return render(
        request,
        template,
        context
    )


def post_detail(
    request,
    post_id
):
    one_post = get_object_or_404(
        Post,
        pk=post_id
    )
    post_list = Post.objects.all()
    count = one_post.author.posts.count()
    form = CommentForm(
        request.POST or None
    )
    comments = one_post.comments.all()
    template = "posts/post_detail.html"
    context = {
        'one_post': one_post,
        'post_list': post_list,
        'count': count,
        'form': form,
        'comments': comments,
    }
    return render(
        request,
        template,
        context
    )


@login_required
def post_create(
    request
):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        post = form.save(
            commit=False
        )
        post.author = request.user
        post.save()
        return redirect(
            "app_posts:profile",
            username=post.author
        )
    return render(
        request,
        "posts/create_post.html",
        {
            "form": form
        }
    )


@login_required
def post_edit(
    request,
    post_id
):
    post = get_object_or_404(
        Post,
        pk=post_id
    )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post.author == request.user:
        if form.is_valid():
            form.save()
            return redirect(
                "app_posts:post_detail",
                post_id
            )
        context = {
            'form': form,
            'is_edit': True,
            'post': post
        }
        return render(
            request,
            "posts/create_post.html",
            context
        )
    return redirect(
        "app_posts:post_detail",
        post_id
    )


@login_required
def add_comment(
    request,
    post_id
):
    post = get_object_or_404(
        Post,
        pk=post_id,
    )
    form = CommentForm(
        request.POST or None
    )
    if form.is_valid():
        comment = form.save(
            commit=False
        )
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(
        'app_posts:post_detail',
        post_id=post_id
    )


@login_required
def follow_index(
    request
):
    post_list = Post.objects.filter(
        author__following__user=request.user
    ).select_related(
        'group',
        'author'
    )
    paginator = Paginator(
        post_list,
        settings.NAMBER_OF_POSTS
    )
    page_number = request.GET.get(
        "page"
    )
    page_obj = paginator.get_page(
        page_number
    )
    context = {
        "page_obj": page_obj,
    }
    return render(
        request,
        'posts/follow.html',
        context
    )


@login_required
def profile_follow(
    request,
    username
):
    author = get_object_or_404(
        User,
        username=username
    )
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect(
        'app_posts:profile',
        username
    )


@login_required
def profile_unfollow(
    request,
    username
):
    author = get_object_or_404(
        User,
        username=username
    )
    follow_obj = Follow.objects.filter(
        user=request.user,
        author=author
    )
    follow_obj.delete()
    return redirect(
        'app_posts:profile',
        username
    )
