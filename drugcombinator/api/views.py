from itertools import chain

from django.http import JsonResponse

from drugcombinator.api.utils import JsonErrorResponse, schemas
from drugcombinator.models import Drug, Interaction
from utils.i18n import get_translated_values
from utils.serializers import StructureSerializer


def _site_url(request):
    def get_url(obj):
        return (
            'site_url',
            request.build_absolute_uri(obj.get_absolute_url())
        )
    return get_url


def _api_url(request):
    def get_url(obj):
        return (
            'url',
            request.build_absolute_uri(
                obj.get_absolute_url(namespace='api')
            )
        )
    return get_url


@schemas('aliases')
def aliases(request):
    """A list of all avalaible aliases, mapping them to substance slugs
    and URLs.

    This is useful for caching or if you want to implement your own
    search logic locally.
    """
    drugs = Drug.objects.all()
    aliases = {}

    for drug in drugs:
        data = {'slug': drug.slug} | dict([_api_url(request)(drug)])

        for name in chain(
            get_translated_values(drug, 'name'),
            drug.aliases
        ):
            aliases[name] = data

    return JsonResponse(aliases)


@schemas('search', 'error')
def search(request, name):
    """Get a substance by name and return its slug and URL.

    Database slugs, names and aliases will be matched against the query.
    """
    try:
        drug = Drug.objects.get_from_name(name)

    except Drug.DoesNotExist:
        return JsonErrorResponse(
            f"Unable to find substance {name}", status=404
        )

    data = {'slug': drug.slug} | dict([_api_url(request)(drug)])
    return JsonResponse(data)


@schemas('substances')
def drugs(request):
    """List all substances in the database, and get a basic summary of
    them."""
    drugs = Drug.objects.all()

    serializer = StructureSerializer((
        'name',
        _api_url(request),
        _site_url(request),
        'category',
        'common',
    ))

    data = serializer.serialize_many(drugs, 'slug')
    return JsonResponse(data)


@schemas('substance', 'error')
def drug(request, slug):
    """Get some detailled information about a substance and a basic
    summary of its interactions.

    The `slug` parameter has to be exact, use the `search` endpoint to
    get a substance slug from its name or aliases.
    """
    try:
        drug = Drug.objects.get(slug=slug)

    except Drug.DoesNotExist:
        return JsonErrorResponse(
            f"Unable to find substance {slug}", status=404
        )

    serializer = StructureSerializer(
        structure=(
            'name',
            'slug',
            'aliases',
            _site_url(request),
            'category',
            'common',
            'description',
            'risks',
            'effects',
            ('interactions', 'slug', (
                'interactants',
                'is_draft',
                _api_url(request),
                _site_url(request),
                'risk',
                'synergy',
                'risk_reliability',
                'effects_reliability',
                'risk_description',
                'effect_description',
            )),
        ),
        select_related={
            'interactions': ('from_drug', 'to_drug')
        }
    )

    data = serializer.serialize(drug)
    return JsonResponse(data)


@schemas('combo', 'error')
def combine(request, slugs):
    """Get detailled information about a substance combination.

    The `slugs` parameter must be a list of valid slugs sepatared by
    plus characters (eg. `.../combo/drug-a+drug-b/`). A maximum of 5
    substances is allowed in each query.
    """
    if len(slugs) < 2:
        return JsonErrorResponse(
            f"At least 2 substances are required (got {len(slugs)})"
        )
    if len(slugs) > 5:
        return JsonErrorResponse(
            f"At most 5 substances are allowed (got {len(slugs)})"
        )

    duplicated_slugs = len(slugs) - len(set(slugs))
    if duplicated_slugs:
        return JsonErrorResponse(
            f"{duplicated_slugs} substance(s) are duplicates"
        )

    drugs = Drug.objects.filter(slug__in=slugs)

    not_found_drugs = len(slugs) - len(drugs)
    if not_found_drugs:
        return JsonErrorResponse(
            f"{not_found_drugs} substance(s) were not found",
            status=404
        )

    interactions = Interaction.objects.between(drugs, prefetch=True)
    unknown_interactions = (
        drugs.expected_interaction_count - len(interactions)
    )

    serializer = StructureSerializer(
        structure=(
            'names',
            'is_draft',
            _site_url(request),
            'risk',
            'synergy',
            'risk_reliability',
            'effects_reliability',
            'risk_description',
            'effect_description',
            ('interactants', 'slug', (
                'name',
                'slug',
                _api_url(request),
                _site_url(request),
                'risks',
                'effects',
            )),
        )
    )

    data = {
        'unknown_interactions': unknown_interactions,
        'interactions': serializer.serialize_many(interactions, 'slug'),
    }
    return JsonResponse(data)
