from operator import attrgetter
from django.shortcuts import get_object_or_404, render
from django.http import Http404

from drugcombinator.models import Drug, Interaction
from drugportals.models import Portal


def _get_drug(request, drug):

    request.drug = get_object_or_404(Drug, slug=drug)


def portal(request):

    portal = get_object_or_404(Portal, drug=request.drug)

    interactions = (
        portal.drug.interactions
        .filter(is_draft=False)
        .prefetch_related('from_drug', 'to_drug')
    )
    for inter in interactions:
        inter.drug = inter.other_interactant(portal.drug)
    interactions = sorted(interactions, key=attrgetter('drug.name'))

    dummy_risks = Interaction.get_dummy_risks()
    
    return render(request, 'drugportals/portal.html', locals())
