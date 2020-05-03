from django.db import connection, reset_queries
import unicodedata as ud
import functools
from time import time


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
