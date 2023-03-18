import unicodedata

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import translate_url
from django.utils.http import _urlparse, is_same_domain
from django.utils.translation import check_for_language
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def set_language_view(request):
    """Rewrite of `django.views.i18n.set_language` view, checking `next`
    parameter against `ALLOWED_HOSTS` setting.

    This is needed because the `drugportals` app serves portals on
    subdomains, and this view might be served from the root domain -or,
    at least, from a different subdomain.

    # Docstring from `django.views.i18n.set_language`:

        Redirect to a given URL while setting the chosen language in the
        session (if enabled) and in a cookie. The URL and the language
        code need to be specified in the request parameters.

        Since this view changes how the user will see the rest of the
        site, it must only be accessed as a POST request.
    """
    if request.method != "POST":
        return HttpResponse(status=400)

    lang_code = request.POST.get('language')
    next_url = request.POST.get('next')

    if not (lang_code and check_for_language(lang_code)):
        return HttpResponse(status=400)

    if next_url:
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts=settings.ALLOWED_HOSTS,
            require_https=request.is_secure(),
        ):
            next_url = "/"

        response = HttpResponseRedirect(
            translate_url(next_url, lang_code)
        )

    else:
        response = HttpResponse(status=204)

    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        lang_code,
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )
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


def url_has_allowed_host_and_scheme(url, allowed_hosts, require_https=False):
    """Rewrite of `django.utils.http.url_has_allowed_host_and_scheme`
    supporting wilcard domains for the host parameter.

    See original function for docs and comments.
    """
    url = url.strip()
    if not url:
        return False

    return _url_has_allowed_host_and_scheme(
        url, allowed_hosts, require_https=require_https
    ) and _url_has_allowed_host_and_scheme(
        url.replace("\\", "/"), allowed_hosts, require_https=require_https
    )


def _url_has_allowed_host_and_scheme(url, allowed_hosts, require_https=False):
    """Rewrite of `django.utils.http._url_has_allowed_host_and_scheme`
    supporting wilcard domains for the host parameter.

    See original function for docs and comments.
    """
    if url.startswith("///"):
        return False
    try:
        url_info = _urlparse(url)
    except ValueError:
        return False

    if not url_info.netloc and url_info.scheme:
        return False

    if unicodedata.category(url[0])[0] == "C":
        return False

    scheme = url_info.scheme
    if not url_info.scheme and url_info.netloc:
        scheme = "http"

    valid_schemes = ["https"] if require_https else ["http", "https"]

    return (
        not url_info.netloc or any(
            is_same_domain(url_info.netloc, host)
            for host in allowed_hosts
        ) and (
            not scheme or scheme in valid_schemes
        )
    )
