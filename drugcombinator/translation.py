from modeltranslation.translator import TranslationOptions, register
from simple_history import register as history_register

from drugcombinator.models import Category, Drug, Interaction


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Drug)
class DrugTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'risks', 'effects', '_aliases')


@register(Interaction)
class InteractionTranslationOptions(TranslationOptions):
    fields = ('names', 'risk_description', 'effect_description')


# Those are needed for simple_history to discover the new
# language-suffixed fields modeltranslation creates
history_register(Drug, inherit=True)
history_register(Interaction, inherit=True)
