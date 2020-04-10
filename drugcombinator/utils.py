import unicodedata as ud


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
    