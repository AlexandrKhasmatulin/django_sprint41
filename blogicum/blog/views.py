from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView

from .utils import get_annotate_comments, get_filtered_posts, get_paginate
from .forms import AuthorChangeForm, CommentForm, PostForm
from .models import Category, Comment, Post
from .mixins import PostMixin


def index(request):
    page_obj = get_paginate(get_annotate_comments(
        get_filtered_posts(Post.objects)), request)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        post = get_object_or_404(get_filtered_posts(Post.objects), id=post_id)

    context = {
        'post': post,
        'comments': post.comments.all(),
        'form': CommentForm(),
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True)
    page_obj = get_paginate(get_annotate_comments(
        get_filtered_posts(category.posts)), request)
    return render(request, 'blog/category.html',
                  {'category': category, 'page_obj': page_obj})


def user_profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = get_annotate_comments(author.posts.all())
    if request.user != author:
        posts = get_filtered_posts(posts)
    page_obj = get_paginate(posts, request)

    return render(request, 'blog/profile.html',
                  {'profile': author, 'page_obj': page_obj})


@login_required
def edit_profile(request):
    author = get_object_or_404(User, username=request.user)
    if request.user != author:
        return redirect('blog:profile', username=author)
    form = AuthorChangeForm(request.POST or None, instance=author)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=author)

    return render(request, 'blog/user.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html',
                  {'form': form, 'comment': comment})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class PostUpdateView(PostMixin, UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs[self.pk_url_kwarg]})
