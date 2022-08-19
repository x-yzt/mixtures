from itertools import chain

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from drugcombinator.models import Drug, Interaction
# from drugcombinator.utils import count_queries
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


def aliases(request):
    drugs = Drug.objects.all()
    aliases = {}

    for drug in drugs:
        data = {
            'slug': drug.slug,
            'url': _api_url(request)(drug)
        }

        for name in chain(
            get_translated_values(drug, 'name'),
            drug.aliases
        ):
            aliases[name] = data

    return JsonResponse(aliases)


def drugs(request):
    pass


def drug(request, slug):
    drug = get_object_or_404(Drug, slug=slug)

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
        },
    )

    data = serializer.serialize(drug)
    return JsonResponse(data)


def combine(request, slugs):
    drugs = Drug.objects.filter(slug__in=slugs)
    interactions = Interaction.objects.between(drugs, prefetch=True)

    serializer = StructureSerializer()
    data = {
        inter.slug: serializer.serialize(inter, {
            'interactants': None,
            'is_draft': None,
            'risk': None,
            'synergy': None,
            'risk_reliability': None,
            'effects_reliability': None,
            'risk_description': None,
            'effect_description': None,
        })
        for inter in interactions
    }

    return JsonResponse(data)
