from django.contrib.auth import get_user_model
from django.db.models import (
    SET_NULL, CharField, DateTimeField, ForeignKey, Model, SlugField,
    TextField)
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from drugcombinator.utils import markdown_allowed


class Article(Model):
    created = DateTimeField(
        auto_now_add=True,
        verbose_name=_("creation")
    )
    last_modified = DateTimeField(
        auto_now=True,
        verbose_name=_("last modification")
    )
    slug = SlugField(
        unique=True,
        verbose_name=_("identifier")
    )
    title = CharField(
        max_length=128,
        verbose_name=_("title")
    )
    author = ForeignKey(
        get_user_model(),
        SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name=_("author")
    )
    content = TextField(
        verbose_name=_("content"),
        help_text=markdown_allowed()
    )

    # History manager will be added throug simple_history's register
    # function in translation.py, after the translated fields are
    # added by modeltranslation

    def __str__(self):
        return self.title

    def get_absolute_uri(self):
        return reverse('article', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = _("article")
        ordering = ('-created',)
