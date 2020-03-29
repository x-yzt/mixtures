from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from drugcombinator.models import Drug


def main(request):

    drugs = Drug.objects.all()
    return render(request, 'drugcombinator/main.html', locals())
