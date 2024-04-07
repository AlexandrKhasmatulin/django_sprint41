from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.shortcuts import redirect

from .models import Post
from .forms import PostForm


class AuthorCheckMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user


class PostMixin(LoginRequiredMixin, AuthorCheckMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        return redirect('blog:post_detail',
                        post_id=self.kwargs[self.pk_url_kwarg])

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'get_form'):
            context['form'] = self.get_form()
        return context
