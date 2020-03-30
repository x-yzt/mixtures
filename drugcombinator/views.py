from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from drugcombinator.models import Drug, Category


def main(request):

    drugs = Drug.objects.all()
    uncategorized_drugs = drugs.filter(category=None)
    categories = Category.objects.all()
    return render(request, 'drugcombinator/main.html', locals())
