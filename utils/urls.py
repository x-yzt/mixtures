from django.views.generic import TemplateView


def template(name, *args, **kwargs):
    return TemplateView.as_view(template_name=name, *args, **kwargs)
