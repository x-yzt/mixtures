from django.db import connection, reset_queries
from django.template import RequestContext
from django.shortcuts import render
import unicodedata as ud
import functools


def normalize(string):
    """
        Returns a lowercase, without accents copy of a given string.
        "Café" -> "cafe"
    """
    return (ud.normalize('NFKD', string.lower())
        .encode('ASCII', 'ignore')
        .decode('utf-8')
    )


def markdown_allowed(verbose=True):
    """
        Returns a simple "Markdown is allowed" string.
    """
    help_link = 'https://commonmark.org/help/'
    return (
        f"La syntaxe <a href=\"{help_link}\">markdown</a> est autorisée."
        + verbose * " Les paragraphes sont séparés par deux retours à la ligne."
    )


def count_queries(func):
    """
        Simple debug decorator printing how many DB queries a function
        performs each time it is called.
    """

    @functools.wraps(func)
    def inner_func(*args, **kwargs):

        reset_queries()        
        queries = len(connection.queries)
        result = func(*args, **kwargs)
        queries = len(connection.queries) - queries

        print(f"Function {func.__name__} made {queries} DB queries.")
        return result

    return inner_func


def render_rc(request, context=None, *args, **kwargs):
    """
        Equivalent of the django.shortcut.render shortcut function, but
        using RequestContext.
    """
    context = RequestContext(request, context)
    return render(request, context, *args, **kwargs)
