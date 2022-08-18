from itertools import chain

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse

from drugcombinator.models import Drug, Interaction
# from drugcombinator.utils import count_queries
from utils.i18n import get_translated_values
from utils.serializers import StructureSerializer


def aliases(request):
    drugs = Drug.objects.all()
    aliases = {}

    for drug in drugs:
        uri = request.build_absolute_uri(
            reverse('drug', kwargs={'slug': drug.slug})
        )

        for name in chain(
            get_translated_values(drug, 'name'),
            drug.aliases
        ):
            aliases[name] = uri

    return JsonResponse(aliases)


def drugs(request):
    pass


def drug(request, slug):
    drug = get_object_or_404(Drug, slug=slug)

    serializer = StructureSerializer()
    data = serializer.serialize(
        drug,
        structure={
            'name': None,
            'slug': None,
            'aliases': None,
            'category': None,
            'common': None,
            'description': None,
            'risks': None,
            'effects': None,
            'interactions': ('slug', {
                'interactants': None,
                'is_draft': None,
                'risk': None,
                'synergy': None,
                'risk_reliability': None,
                'effects_reliability': None,
                'risk_description': None,
                'effect_description': None,
            }),
        },
        select_related={
            'interactions': ('from_drug', 'to_drug')
        }
    )

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
