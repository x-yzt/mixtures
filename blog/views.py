from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from blog.models import Article


def index(request, page=None):
    articles = Article.objects.all()

    paginator = Paginator(articles, 10)
    page = paginator.get_page(page)

    return render(request, 'blog/index.html', locals())


def article(request, slug):
    articles = [get_object_or_404(Article, slug=slug)]

    return render(request, 'blog/article.html', locals())
