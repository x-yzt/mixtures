from django.http import JsonResponse


BASE_SCHEMAS_DOCS_URL = 'https://x-yzt.github.io/mixtures/'


def get_absolute_api_url(request, pattern):
    """Get a nicely formatted absolute URI from an API endpoint URL
    pattern."""
    pattern = (
        pattern
        .replace('%(', ':')
        .replace(')s', '')
    )
    return request.build_absolute_uri('/api/' + pattern)


def schemas(*args):
    """Simple decorator to set a view `schemas` property.

    This will be used later on for displaying response JSON schemas in
    API documentation.
    """
    def decorator(func):
        func.schemas = args
        func.get_schemas_docs_urls = lambda: {
            schema: f'{BASE_SCHEMAS_DOCS_URL}{schema}.schema'
            for schema in func.schemas
        }
        return func

    return decorator


class JsonErrorResponse(JsonResponse):
    def __init__(self, msg, *args, **kwargs):
        kwargs.setdefault('status', 400)
        super().__init__({'error': msg}, *args, **kwargs)
