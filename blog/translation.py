from modeltranslation.translator import TranslationOptions, register
from simple_history import register as history_register

from blog.models import Article


@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


# Those are needed for simple_history to discover the new
# language-suffixed fields modeltranslation creates
history_register(Article, inherit=True)
