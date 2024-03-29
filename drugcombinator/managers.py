from django.db.models import F, Manager, QuerySet
from django.db.models.functions import Coalesce
from django.http import Http404
from django.urls import reverse
from modeltranslation.settings import AVAILABLE_LANGUAGES
from modeltranslation.utils import (
    build_localized_fieldname,
    get_language,
    resolution_order,
)

from drugcombinator.utils import normalize


class TranslatedQuerySet(QuerySet):
    """Utility `QuerySet` subclass extending `modeltranslation`'s
    `MultilingualQuerySet` functionnalities."""

    def coalesce_translations(self, field):
        """Coalesce all translations of a given field according to the
        current language and fallback resolution order, and annotate
        the current QuerySet with it through a `field_translations` key.
        """
        # Languages the translation has to be searched in, in relevant
        # order
        langs = resolution_order(
            get_language(), {'defaut': AVAILABLE_LANGUAGES}
        )
        # Build the list of translated fields names in relevant order
        fields = [
            build_localized_fieldname(field, lang) for lang in langs
        ]

        # If there is only one relevant field, no coalescing is needed
        if len(fields) == 1:
            annotation = F(fields[0])

        else:
            # Get the underlying model field type
            field_type = self.model._meta.get_field(field).__class__
            # Annotate needs to know which type of field it has to output,
            # because translated fields type differs from usual Django
            # fields (e.g. TranslatedCharField differs from CharField)
            annotation = Coalesce(*fields, output_field=field_type())

        return self.annotate(
            **{field + '_translations': annotation}
        )

    def order_by_translated(self, field):
        """As `modeltranslation` does not provide fallback values when
        using the `order_by` method of its manager, this method
        implements it.

        It provides ordering with fallbacks, for a single translated
        field only.
        """
        return (
            self
            .coalesce_translations(field.lstrip('-'))
            .order_by(field + '_translations')
        )


class DrugManager(Manager):
    def get_from_name(self, name):
        """Return a drug based on its name.

        Search criterias priorities:
            - equal to slug (case insensitive, accentuation insensitive)
            - equal to name (case insentitive)
            - included in aliases (case insentitive)

        Throw DoesNotExist if no drug is found.
        """
        reg = rf'(^|\r|\n){name}(\r|\n|$)'

        for lookup in (
            lambda: self.get(slug=normalize(name)),
            lambda: self.filter(name__iexact=name)[0],
            lambda: self.filter(aliases__iregex=reg)[0],
        ):
            try:
                return lookup()
            except (self.model.DoesNotExist, IndexError):
                continue

        raise self.model.DoesNotExist

    def get_from_name_or_404(self, name):
        """Similar to `get_from_name` but raises `Http404` if no drug is
        found."""
        try:
            return self.get_from_name(name)
        except self.model.DoesNotExist as e:
            raise Http404(f"Unable to find drug {name}.") from e


class DrugQuerySet(TranslatedQuerySet):
    def get_absolute_url(self):
        """Return the canonical URL of the combination of this set of
        drugs."""
        slugs = self.values_list('slug', flat=True).order_by('slug')
        return reverse('combine', kwargs={'slugs': slugs})

    @property
    def expected_interaction_count(self):
        """How many interactions are expected between those
        substances."""
        return len(self) * (len(self)-1) // 2


class InteractionQuerySet(TranslatedQuerySet):
    def between(self, drugs, prefetch=False):
        """Return all interactions linking a set of drugs.

        If `prefetch` is set to `True`, related `Drug` instances will be
        prefetched.
        """
        qs = self.filter(from_drug__in=drugs, to_drug__in=drugs)
        if prefetch:
            return qs.prefetch_related('from_drug', 'to_drug')
        return qs

    def order_by_slug(self):
        """Order the queryset by its related drugs slugs in
        lexicographic order."""
        return self.order_by('from_drug__slug', 'to_drug__slug')


DrugManager = DrugManager.from_queryset(DrugQuerySet)
InteractionManager = InteractionQuerySet.as_manager
