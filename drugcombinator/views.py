from abc import ABCMeta, abstractmethod
from types import SimpleNamespace

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import F
from django.http import Http404, JsonResponse
from django.http.response import (
    HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import get_resolver
from django.utils.decorators import method_decorator
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.base import TemplateResponseMixin
from django_hosts.resolvers import reverse_host

from drugcombinator import api
from drugcombinator.api.utils import get_absolute_api_url
from drugcombinator.exceptions import Http400
from drugcombinator.forms import CombinatorForm, ContribForm, SearchForm
from drugcombinator.models import Category, Contributor, Drug, Interaction
from drugcombinator.utils import normalize
from drugportals.models import Portal


def main(request):
    drugs = Drug.objects.order_by_translated('name')
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
    drugs = Drug.objects.order_by_translated('name')
    common_drugs = drugs.filter(common=True)

    if request.GET:
        search_form = SearchForm(request.GET)

        if search_form.is_valid():
            name = search_form.cleaned_data['q']

            try:
                drug = Drug.objects.get_from_name(name)
                return redirect(drug, permanent=True)

            except Drug.DoesNotExist:
                (
                    search_form
                    .fields['q']
                    .widget
                    .attrs
                    .update({'class': 'autocomplete invalid'})
                )

    else:
        search_form = SearchForm()

    return render(request, 'drugcombinator/drug_search.html', locals())


def combine(request, slugs):
    if len(slugs) < 2:
        raise Http400("At least two substances are requiered")

    drugs = Drug.objects.filter(slug__in=slugs)

    not_found_drugs = len(slugs) - len(drugs)
    if not_found_drugs:
        raise Http404(f"Unable to find {not_found_drugs} substance(s)")

    interactions = (
            Interaction.objects
            .between(drugs, prefetch=True)
            .order_by('is_draft', '-risk')
    )

    combination_name = ' + '.join([str(d) for d in drugs])
    toc = {inter.slug: str(inter) for inter in interactions}

    unknown_interactions = (
        drugs.expected_interaction_count - len(interactions)
    )

    contrib_form = ContribForm()

    return render(request, 'drugcombinator/combine.html', locals())


class AbstractDrugView(View, TemplateResponseMixin, metaclass=ABCMeta):
    def get(self, request, **kwargs):
        ctx = self.get_context(request, **kwargs)
        return self.render_to_response(vars(ctx))

    @abstractmethod
    def get_context(self, request, slug):
        ctx = SimpleNamespace()

        ctx.drug = get_object_or_404(Drug, slug=slug)
        ctx.interactions = (
            ctx.drug.interactions
            .prefetch_related('from_drug', 'to_drug')
            .order_by('is_draft', '-risk')
        )
        ctx.toc = {
            inter.slug: str(inter.other_interactant(ctx.drug))
            for inter in ctx.interactions
        }

        return ctx


class DrugView(AbstractDrugView):
    template_name = 'drugcombinator/drug.html'

    def get_context(self, request, slug):
        ctx = super().get_context(request, slug)
        ctx.default_host = reverse_host(settings.DEFAULT_HOST)
        ctx.contrib_form = ContribForm()

        return ctx


@method_decorator(xframe_options_exempt, name='dispatch')
class RecapView(DrugView):
    template_name = 'drugcombinator/iframes/recap.html'

    def get_context(self, request, slug):
        ctx = super().get_context(request, slug)
        ctx.interactions = ctx.interactions.filter(is_draft=False)
        ctx.dummy_risks = Interaction.get_dummy_risks()
        ctx.dummy_synergies = Interaction.get_dummy_synergies()

        for inter in ctx.interactions:
            inter.drug = inter.other_interactant(ctx.drug)

        return ctx


@xframe_options_exempt
def table(request, slugs=None):
    show_categs = bool(int(request.GET.get('show_categs', 1)))
    only_common = bool(int(request.GET.get('only_common', 1)))

    drugs = Drug.objects
    if slugs:
        drugs = drugs.filter(slug__in=slugs)
    elif only_common:
        drugs = drugs.filter(common=True)

    drugs = (
        drugs
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

    return render(request, 'drugcombinator/iframes/table.html', locals())


def docs(request):
    drugs_count = Drug.objects.all().count()
    interactions_count = Interaction.objects.all().count()

    resolver = get_resolver(api.urls)

    endpoints = []
    # Reverse dict items order must be reversed so the docs follow the
    # URLConf patterns insertion order
    for view, patterns in reversed(list(resolver.reverse_dict.items())):
        # Reverse dict also contains pattern names, discard them
        if not callable(view):
            continue

        patterns, _, _, params = patterns
        pattern = patterns[0][0]

        endpoints.append({
            'url': get_absolute_api_url(request, pattern),
            'params': {
                name: type(converter).__name__
                for name, converter in params.items()
            },
            'schemas': view.get_schemas_docs_urls(),
            'doc': view.__doc__
        })

    return render(request, 'drugcombinator/docs.html', locals())


def about(request):
    contributors = (
        Contributor.objects
        .filter(display=True)
        .order_by('user__username')
    )

    return render(request, 'drugcombinator/about.html', locals())


def autocomplete(request):
    drugs = Drug.objects.all()
    entries = [drug.name for drug in drugs]

    for drug in drugs:
        for alias in drug.aliases:
            if not any(
                [normalize(alias) in normalize(e) for e in entries]
            ):
                entries.append(alias)

    return JsonResponse({entry: None for entry in entries})


def send_contrib(request):
    if request.method == 'POST':
        contrib_form = ContribForm(request.POST)

        if contrib_form.is_valid():
            interaction = contrib_form.cleaned_data['interaction_field']
            name = contrib_form.cleaned_data['combination_name_field']
            expeditor = contrib_form.cleaned_data['email_field']
            message = contrib_form.cleaned_data['message_field']

            send_mail(
                format_lazy(
                    _("New contribution: {interaction}"),
                    interaction=interaction or name,
                ),
                message,
                from_email=expeditor,
                recipient_list=['contact@mixtures.info'],
                fail_silently=False,
            )
            return HttpResponse(status=204)

        return HttpResponseBadRequest("Invalid form data")

    return HttpResponseNotAllowed(['POST'], "Unallowed method")
