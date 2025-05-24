from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    """
    Homepage view for the Movie Recommendation System
    """
    return HttpResponse("<h1>Welcome to Movie Recommendation System!</h1><p>Homepage is working!</p>")
