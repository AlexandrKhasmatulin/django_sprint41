from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from .models import Comment, Post

User = get_user_model()


class AuthorChangeForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', 'is_published',)
