from django.db.models import Count, F
from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from drugcombinator.exceptions import Http400
from drugcombinator.models import Drug, Category, Interaction
from drugcombinator.forms import CombinatorForm, SearchForm
from drugcombinator.utils import normalize, count_queries


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

    drug = Drug.objects.get_from_name_or_404(name)

    if name != drug.slug:
        return redirect(drug, permanent=True)
    
    interactions = (Interaction.objects
            .filter(from_drug=drug)
            .order_by('-risk')
    )
    
    return render(request, 'drugcombinator/drug.html', locals())


# @count_queries
def combine_chart(request):
    
    drugs = (Drug.objects
        .filter(common=True)
        .order_by(F('category__name').asc(nulls_last=True), 'name')
    )
    categories = (Category.objects
        .filter(drugs__in=drugs)
        .distinct()
        .prefetch_related('drugs')
        .annotate(num_drugs=Count('drugs', drugs__in=drugs))
        .order_by('name')
    )
    interactions = (Interaction.objects
        .filter(from_drug__in=drugs, to_drug__in=drugs)
        .prefetch_related('from_drug', 'to_drug')
    )

    chart_data = {drug: {} for drug in drugs}
    for inter in interactions:
        chart_data[inter.from_drug][inter.to_drug] = inter

    header_data = []
    for categ in categories:
        header_data.append(categ)
        header_data += [None] * (categ.num_drugs - 1)
    header_data.append("Autres")
    
    return render(request, 'drugcombinator/combine_chart.html', locals())


def docs(request):

    drugs_count = Drug.objects.all().count()
    interactions_count = Interaction.objects.all().count() // 2

    return render(request, 'drugcombinator/docs.html', locals())


def autocomplete(request):

    drugs = Drug.objects.all()
    entries = [drug.name for drug in drugs]

    for drug in drugs:
        for alias in drug.aliases:
            if not any([normalize(alias) in normalize(entry) for entry in entries]):
                entries.append(alias)
    
    return render(request, 'drugcombinator/autocomplete.js', locals())