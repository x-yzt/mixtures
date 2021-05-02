import functools
import unicodedata
from time import time
from django.db import connection, reset_queries
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _


def normalize(string):
    """
        Returns a lowercase, without accents copy of a given string.
        "Café" -> "cafe"
    """
    return (unicodedata.normalize('NFKD', string.lower())
        .encode('ASCII', 'ignore')
        .decode('utf-8')
    )


def markdown_allowed(verbose=True):
    """
        Returns a simple "Markdown is allowed" string.
    """
    help_link = "https://commonmark.org/help/"
    markdown = format_lazy(
        _("The {markdown} syntax is allowed."),
        markdown=f"<a href=\"{help_link}\">markdown</a>"
    )
    syntax = _("Paragraphs are separated by two carriage returns.")
    return format_lazy("{} {}", markdown, syntax)


def count_queries(func):
    """
        Simple debug decorator printing how many DB queries a function
        performs and wich time it took each time it is called.
    """

    @functools.wraps(func)
    def inner_func(*args, **kwargs):

        reset_queries()        
        queries = len(connection.queries)
        t = time()
        result = func(*args, **kwargs)
        queries = len(connection.queries) - queries
        t = 1000 * (time() - t)

        print(
            f"Function {func.__name__} made {queries} DB queries and "
            f"took {t}ms."
        )
        return result

    return inner_func
