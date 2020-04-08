from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from drugcombinator.exceptions import Http400
from drugcombinator.models import Drug, Category, Interaction
from drugcombinator.forms import CombinatorForm, SearchForm
from drugcombinator.utils import normalize

def main(request):

    drugs = Drug.objects.all()
    common_drugs = drugs.filter(common=True)
    uncategorized_drugs = drugs.filter(category=None)
    categories = Category.objects.all()

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
            
            return redirect('drug', name=name.lower(), permanent=True)

    else:
        search_form = SearchForm()
    
    return render(request, 'drugcombinator/drug_search.html', locals())


def combine(request, slugs):

    if len(slugs) < 2:
        raise Http400(
                "Au moins deux substances sont nécéssaires."
        )

    drugs = Drug.objects.filter(slug__in=slugs)
    interactions = (
            Interaction.objects
            .filter(from_drug__in=drugs, to_drug__in=drugs)
            .order_by('-risk', 'sym_id')
            [::2]
    )
    
    combination_name = ' + '.join([str(d) for d in drugs])

    expected_interactions = len(drugs) * (len(drugs)-1) // 2
    unknown_interactions = expected_interactions - len(interactions)

    return render(request, 'drugcombinator/combine.html', locals())


def drug(request, name):

    try:
        drug = Drug.objects.get(slug=name)
    
    except Drug.DoesNotExist:
        reg = rf'(^|\r|\n){name}(\r|\n|$)'
        drugs = Drug.objects.filter(_aliases__iregex=reg)
        
        try:
            return redirect(drugs[0], permanent=True)
        
        except IndexError:
            raise Http404(
                    f"La substance {name} n'est pas dans la base de données."
            )
    
    interactions = (Interaction.objects
            .filter(from_drug=drug)
            .order_by('-risk')
    )
    
    return render(request, 'drugcombinator/drug.html', locals())


def autocomplete(request):

    drugs = Drug.objects.all()
    entries = [drug.name for drug in drugs]

    for drug in drugs:
        for alias in drug.aliases:
            if not any([normalize(alias) in normalize(entry) for entry in entries]):
                entries.append(alias)
    
    return render(request, 'drugcombinator/autocomplete.js', locals())