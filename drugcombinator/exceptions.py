from django.core.exceptions import SuspiciousOperation


class Http400(SuspiciousOperation):
    pass
