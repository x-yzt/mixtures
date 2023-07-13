from django.core.exceptions import ObjectDoesNotExist


def exists_or_none(callable):
    try:
        return callable()
    except ObjectDoesNotExist:
        return None
