from modeltranslation.translator import TranslationOptions, register

from drugportals.models import Portal


@register(Portal)
class PortalTranslationOptions(TranslationOptions):
    fields = ('name',)
