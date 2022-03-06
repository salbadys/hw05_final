from django import forms
from .models import Post, Comment
from django.utils.translation import gettext_lazy as _


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group", "image"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": "10",
                    "cols": "40",
                    "name": "text",
                    "required id": "id_text",
                }
            )
        }
        labels = {
            "text": _("Группа поста"),
            "group": _("Группа поста")
        }
        help_texts = {
            'text': _('Здесь заполняется новости к посту'),
            'group': _('Также у постов могут быть группы')
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text", )
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": "10",
                    "cols": "40",
                    "name": "text",
                    "required id": "id_text",
                }
            )
        }
