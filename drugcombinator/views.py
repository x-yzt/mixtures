from itertools import chain
from django.db.models import Count, F
from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from drugcombinator.exceptions import Http400
from drugcombinator.models import Drug, Category, Interaction
from drugcombinator.forms import CombinatorForm, SearchForm
from drugcombinator.utils import normalize, count_queries
from drugportals.models import Portal


def main(request):

    drugs = Drug.objects.all()
    common_drugs = drugs.filter(common=True)
    uncategorized_drugs = drugs.filter(category=None)
    categories = Category.objects.all()
    portals = Portal.objects.all()

    if request.method == 'POST':
        combinator_form = CombinatorForm(request.POST)
        
        if combinator_form.is_valid():
            drugs = combinator_form.cleaned_data['drugs_field']
            slugs = [drug.slug for drug in drugs]
            
            return redirect('combine', slugs=slugs, permanent=True)

    else:
        combinator_form = CombinatorForm()
    
    return render(request, 'drugcombinator/main.html', locals())


def drug_search(request):

    drugs = Drug.objects.all()
    common_drugs = drugs.filter(common=True)

    if request.method == 'POST':
        search_form = SearchForm(request.POST)
        
        if search_form.is_valid():
            name = search_form.cleaned_data['name_field']

            try:
                drug = Drug.objects.get_from_name(name)
                return redirect(drug, permanent=True)
            
            except Drug.DoesNotExist:
                (search_form
                    .fields['name_field']
                    .widget.attrs
                    .update({'class': 'autocomplete invalid'})
                )

    else:
        search_form = SearchForm()
    
    return render(request, 'drugcombinator/drug_search.html', locals())


def combine(request, slugs):

    if len(slugs) < 2:
        raise Http400("Au moins deux substances sont nécessaires.")

    drugs = Drug.objects.filter(slug__in=slugs)
    interactions = (
            Interaction.objects
            .between(drugs, prefetch=True)
            .order_by('is_draft', '-risk')
    )
    
    combination_name = ' + '.join([str(d) for d in drugs])

    expected_interactions = len(drugs) * (len(drugs)-1) // 2
    unknown_interactions = expected_interactions - len(interactions)

    return render(request, 'drugcombinator/combine.html', locals())


def drug(request, name):

    drug = Drug.objects.get_from_name_or_404(name)

    if name != drug.slug:
        return redirect(drug, permanent=True)
    
    interactions = (drug.interactions
        .prefetch_related('from_drug', 'to_drug')
        .order_by('is_draft', '-risk')
    )
    
    return render(request, 'drugcombinator/drug.html', locals())


@xframe_options_exempt
def table(request, slugs=None):

    drugs = Drug.objects
    if slugs:
        drugs = drugs.filter(slug__in=slugs)
    else:
        drugs = drugs.filter(common=True)

    drugs = (drugs
        .prefetch_related('category')
        .order_by(F('category__name').asc(nulls_last=True), 'name')
    )
    interactions = Interaction.objects.between(drugs, prefetch=True)

    dummy_risks = Interaction.get_dummy_risks()
    dummy_synergies = Interaction.get_dummy_synergies()

    chart_data = {drug: {} for drug in drugs}
    for inter in interactions:
        chart_data[inter.from_drug][inter.to_drug] = inter
        chart_data[inter.to_drug][inter.from_drug] = inter

    return render(request, 'drugcombinator/table.html', locals())


def docs(request):

    drugs_count = Drug.objects.all().count()
    interactions_count = Interaction.objects.all().count()

    return render(request, 'drugcombinator/docs.html', locals())


def autocomplete(request):

    drugs = Drug.objects.all()
    entries = [drug.name for drug in drugs]

    for drug in drugs:
        for alias in drug.aliases:
            if not any([normalize(alias) in normalize(entry) for entry in entries]):
                entries.append(alias)
    
    return render(
        request, 'drugcombinator/autocomplete.js', locals(),
        content_type='text/javascript'
    )
