import unicodedata as ud


def normalize(string):
    """
        Returns a lowercase, without accents copy of a given string.
        "Café" -> "cafe"
    """
    return ud.normalize('NFKD', string.lower()).encode('ASCII', 'ignore')
