import django
from django.conf import settings
from django.urls import reverse as dj_reverse


class DynamicSubdomainMiddleware:
    """
        Allow subdomains to be used in URL patterns.

        Subdomains are separated from the main url pattern by `::`. Any
        capturing group, named or not, or other features of common
        URL patterns are allowed.

        This middleware will not affect subdomains that are included in
        the `BASE_SUBDOMAINS` setting.

        For this middleware to work, the `ALLOWED_HOSTS` setting must be
        set explicitely (even if `DEBUG = True`). Wilcard domain `*` is
        not supported. Hosts that start by a dot are considered root
        domains.

        Exemple, assuming the URLconf contains the following pattern:
        `path('subdomain::thing/other/', view)`
        The middleware will bind the `subdomain.domain/thing/other/` URL
        to `view` for all root domains in the `ALLOWED_HOSTS` setting.
    """
    def __init__(self, get_response):

        self.get_response = get_response
        self.root_domains = [
            h for h in settings.ALLOWED_HOSTS if h.startswith('.')
        ]

    
    def get_subdomain(self, request):
        """
            Return the subdomain of the current request.
            Return None if the current host:
              - Cannot have a subdomain (e.g. it is an IP address),
              - Is a root domain from ALLOWED_HOSTS,
              - Is not allowed by the ALLOWED_HOSTS setting.
        """
        domain = request.get_host().split(':', 1)[0] # Strips port

        subdomain = None
        for root_domain in self.root_domains:
            if domain.endswith(root_domain):
                subdomain = domain.replace(root_domain, '')
                break
        
        return subdomain


    def __call__(self, request):

        subdomain = self.get_subdomain(request)

        if subdomain not in (None, *settings.BASE_SUBDOMAINS):
            # path_info must start with a '/' to be matched correctly by
            # URLconfs patterns. However, this leading slash will not be
            # needed when writing the patterns in the URLconf.
            request.path_info = f'/{subdomain}::{request.path_info}'
        
        return self.get_response(request)


def reverse(*args, domain=None, **kwargs):
    """
        Tweak of Django's default `reverse` function. It should be
        transparent when dealing with common URLs, and can be
        monkeypatched where it is needed.

        The `DEFAULT_DOMAIN` setting allows for specifying a default
        domain name to reverse subdomain URLs when this function is
        called without explicit `domain` argment.
    """
    url = dj_reverse(*args, **kwargs)

    if '::' in url:
        domain = domain or settings.DEFAULT_DOMAIN
        subdomain, url = url[1:].split('::', 1)
        url = f'//{subdomain}.{domain}{url}'
    
    elif domain is not None:
        url = f'//{domain}{url}'

    return url

django.urls.reverse = reverse
