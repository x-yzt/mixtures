from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from django.db import NotSupportedError
from drugcombinator.exceptions import Http400
from drugcombinator.models import Drug, Category, Interaction
from drugcombinator.forms import CombinatorForm


def main(request):

    drugs = Drug.objects.all()
    common_drugs = drugs.filter(common=True)
    uncategorized_drugs = drugs.filter(category=None)
    categories = Category.objects.all()

    combinator_form = CombinatorForm()

    return render(request, 'drugcombinator/main.html', locals())


def combine(request, slugs):

    if len(slugs) < 2:
        raise Http400(
                "Au moins deux substances sont nécéssaires."
        )

    drugs = Drug.objects.filter(slug__in=slugs)
    interactions = (
            Interaction.objects
            .filter(from_drug__in=drugs, to_drug__in=drugs)
            .order_by('sym_id')
    )
    
    try:
        # Trigger DB query using list()
        interactions = list(interactions.distinct('sym_id'))
    
    except NotSupportedError:
        # Fallback if distinct() is not supported by current DB engine
        inters = []
        sym_ids = set()
        for inter in interactions:
            if inter.sym_id not in sym_ids:
                inters.append(inter)
                sym_ids.add(inter.sym_id)
        interactions = inters
    
    combination_name = ' + '.join([str(d) for d in drugs])

    return render(request, 'drugcombinator/combine.html', locals())
