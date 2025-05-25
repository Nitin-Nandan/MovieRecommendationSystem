from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .data_loader import movie_data_loader

def home(request):
    """Homepage view for the Movie Recommendation System"""
    if request.method == 'POST':
        try:
            # Get selected movies from form
            selected_movies = request.POST.getlist('selected_movies')
            
            if len(selected_movies) < 3:
                return render(request, 'movapp/home.html', {
                    'error': 'Please select at least 3 movies to get recommendations.'
                })
            
            # Generate enhanced recommendations (20 total, show 10 initially)
            all_recommendations = movie_data_loader.get_enhanced_recommendations(selected_movies, 20)
            
            # Split into initial and additional recommendations
            initial_recommendations = all_recommendations[:10]
            additional_recommendations = all_recommendations[10:20]
            
            return render(request, 'movapp/results.html', {
                'selected_movies': selected_movies,
                'recommendations': initial_recommendations,
                'additional_recommendations': additional_recommendations,
                'has_more': len(additional_recommendations) > 0
            })
            
        except Exception as e:
            return render(request, 'movapp/home.html', {
                'error': f'An error occurred: {str(e)}'
            })
    
    return render(request, 'movapp/home.html')

def search_movies(request):
    """AJAX endpoint for movie search"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'movies': []})
    
    matches = movie_data_loader.search_movies(query, limit=10)
    
    return JsonResponse({'movies': matches})
