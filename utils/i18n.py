from contextlib import contextmanager

from django.conf import settings
from django.http.request import validate_host
from django.utils.http import _urlparse, url_has_allowed_host_and_scheme
from django.views.i18n import set_language


@contextmanager
def patch_allowed_urls(func):
    """Context manager replacing `url_has_allowed_host_and_scheme` by
    custom variation in the namespace of a given function.
    """
    # func will call the alternate validation function in place of
    # http.url_has_allowed_host_and_scheme
    func.__globals__['url_has_allowed_host_and_scheme'] = _is_allowed

    try:
        yield
    finally:
        # Revert the namespace to its original state
        func.__globals__['url_has_allowed_host_and_scheme'] = (
            url_has_allowed_host_and_scheme)


def _is_allowed(url, require_https=False, *args, **kwargs):
    """Variation of the `django.http.url_has_allowed_host_and_scheme`
    function, checking the given URL host against the `ALLOWED_HOSTS`
    setting (including wildcards.)

    Note: `args` and `kwargs` are there to mock unused arguments from
    original function calls.
    """
    url = _urlparse(url)

    allowed_schemes = {'https'} if require_https else {'http', 'https'}
    allowed_hosts = settings.ALLOWED_HOSTS
    # Fallback to localhost-like patterns when debugging with an empty
    # ALLOWED_HOSTS settings
    if settings.DEBUG and not allowed_hosts:
        allowed_hosts = {'.localhost', '127.0.0.1', '[::1]'}

    return (
        validate_host(url.netloc, allowed_hosts)
        and (url.scheme in allowed_schemes)
    )


def set_language_view(request):
    """Thin wrapper around the `django.views.i18n.set_language` view,
    using a slightly different validation logic for the `next` parameter
    and `Referer` header, allowing redirection to any URI which host
    matches the `ALLOWED_HOST` settings.

    This is needed because the `drugportals` app serves portals on
    subdomains, and this view might be served from the root domain -or,
    at least, from a different subdomain.
    """
    with patch_allowed_urls(set_language):
        # Call the default set_language from Django i18n
        response = set_language(request)

    return response


def get_translated_fields(field):
    """Given a field name, return all translated fields names."""
    langs = (lang[0].replace('-', '_') for lang in settings.LANGUAGES)
    return [f"{field}_{lang}" for lang in langs]


def get_translated_values(obj, field):
    """
    Given a model instance and a field name, return all avalaible
    translated values of the field.
    """
    return list(filter(None, (
        getattr(obj, translated_field, None)
        for translated_field in get_translated_fields(field)
    )))
