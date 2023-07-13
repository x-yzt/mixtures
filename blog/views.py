from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from blog.models import Article
from utils import exists_or_none


def index(request, page=None):
    articles = Article.objects.all()

    paginator = Paginator(articles, 10)
    page = paginator.get_page(page)

    return render(request, 'blog/index.html', locals())


def article(request, slug):
    article = get_object_or_404(Article, slug=slug)

    previous_article = exists_or_none(article.get_previous_by_created)
    next_article = exists_or_none(article.get_next_by_created)

    return render(request, 'blog/article.html', locals())
