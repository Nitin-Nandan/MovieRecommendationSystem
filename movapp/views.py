from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    """
    Homepage view for the Movie Recommendation System
    """
    if request.method == 'POST':
        # We'll handle form submission in Step 5
        return HttpResponse("Form submitted! (We'll process this in Step 5)")
    
    return render(request, 'movapp/home.html')
