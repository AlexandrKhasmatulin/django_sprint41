from django.db.models import Count
from django.core.paginator import Paginator
from django.utils import timezone

PAGINATION = 10


def get_filtered_posts(post_manager):
    return post_manager.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def get_annotate_comments(posts):
    return posts.select_related(
        'author', 'location', 'category'
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')


def get_paginate(data, request, per_page=PAGINATION):
    paginator = Paginator(data, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
